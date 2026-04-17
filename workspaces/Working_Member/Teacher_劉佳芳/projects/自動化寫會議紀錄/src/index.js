require('dotenv').config();
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { GoogleAIFileManager } = require('@google/generative-ai/server');
const fs = require('fs');
const path = require('path');

const apiKey = process.env.GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(apiKey);
const fileManager = new GoogleAIFileManager(apiKey);

const inputDir = path.join(__dirname, '../data/raw_notes');
const outputDir = path.join(__dirname, '../data/output');

async function uploadToGemini(filePath, mimeType) {
  const uploadResult = await fileManager.uploadFile(filePath, {
    mimeType,
    displayName: path.basename(filePath),
  });
  const file = uploadResult.file;
  console.log(`✅ 已上傳檔案: ${file.displayName} 為: ${file.name}`);
  
  // 檢查檔案處理狀態
  let fileData = await fileManager.getFile(file.name);
  while (fileData.state === 'PROCESSING') {
    process.stdout.write('.');
    await new Promise((resolve) => setTimeout(resolve, 2000));
    fileData = await fileManager.getFile(file.name);
  }
  process.stdout.write('\n');
  
  if (fileData.state !== 'ACTIVE') {
    throw new Error(`上傳的檔案處理失敗: ${file.name}`);
  }
  
  return file;
}

// 加入重試機制
async function generateWithRetry(modelName, contentParts, retries = 3) {
  const model = genAI.getGenerativeModel({ model: modelName });
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      console.log(`正在使用模式 ${modelName} 生成內容 (第 ${attempt} 次嘗試)...`);
      const result = await model.generateContent(contentParts);
      return result.response.text();
    } catch (err) {
      console.error(`Attempt ${attempt} failed with ${modelName}:`, err.message);
      if (attempt === retries) throw err;
      console.log('等待 10 秒後重試...');
      await new Promise(r => setTimeout(r, 10000));
    }
  }
}

async function processMeetingNotes() {
  console.log('開始處理錄音檔或文字檔轉換會議紀錄...');

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const supportedExtensions = ['.txt', '.md', '.mp3', '.wav', '.m4a', '.ogg'];
  const files = fs.readdirSync(inputDir).filter(f => supportedExtensions.includes(path.extname(f).toLowerCase()) && !f.includes('.bak'));

  if (files.length === 0) {
    console.log(`在 ${inputDir} 目錄中找不到任何檔案`);
    return;
  }

  for (const file of files) {
    console.log(`\n------------\n處理檔案: ${file}`);
    const filePath = path.join(inputDir, file);
    const ext = path.extname(file).toLowerCase();
    
    let contentParts = [];

    const prompt = `
請將這份會議內容整理成專業、結構化的會議紀錄。
如果內容是語音辨識的逐字稿或錄音檔，請仔細聆聽/閱讀，過濾掉冗言贅字。
請使用 Markdown 格式輸出。

必須包含以下區塊：
1. **會議主題** (根據內容推測)
2. **會議時間**
3. **會議摘要**
4. **重點紀錄** (分點條列)
5. **後續行動事項 (Action Items)** (條列負責人與任務)
`;
    contentParts.push(prompt);

    if (ext === '.txt' || ext === '.md') {
      const rawContent = fs.readFileSync(filePath, 'utf8');
      contentParts.push(rawContent);
    } else {
      let mimeType = 'audio/mp3';
      if (ext === '.wav') mimeType = 'audio/wav';
      else if (ext === '.m4a' || ext === '.mp4') mimeType = 'audio/m4a';
      else if (ext === '.ogg') mimeType = 'audio/ogg';

      try {
        console.log(`正在將音訊檔 ${file} 上傳至 Gemini API...`);
        const geminiFile = await uploadToGemini(filePath, mimeType);
        contentParts.push({
          fileData: {
            mimeType: geminiFile.mimeType,
            fileUri: geminiFile.uri
          }
        });
      } catch (err) {
        console.error(`音訊檔上傳或處理失敗: ${err.message}`);
        continue;
      }
    }

    try {
      // 若 2.5-flash 高負載失敗，就 fallback 試試 1.5-flash 和 1.5-pro
      let text;
      try {
        text = await generateWithRetry('gemini-2.5-flash', contentParts, 1); // 嘗試 1 次
      } catch (e) {
        console.log('gemini-2.5-flash 失敗，自動切換至 gemini-1.5-flash 模型...');
        try {
          text = await generateWithRetry('gemini-1.5-flash', contentParts, 2);
        } catch (e2) {
          console.log('gemini-1.5-flash 失敗，自動切換至 gemini-1.5-pro 模型...');
          text = await generateWithRetry('gemini-1.5-pro', contentParts, 2);
        }
      }

      const outputFileName = file.replace(new RegExp(`\\${ext}$`, 'i'), '_processed.md');
      const outputPath = path.join(outputDir, outputFileName);

      fs.writeFileSync(outputPath, text, 'utf8');
      console.log(`✅ 已成功產出: ${outputPath}`);
    } catch (err) {
      console.error(`最終生成內容失敗: ${err.message}`);
    }
  }

  console.log('\n所有處理完成。');
}

processMeetingNotes().catch(console.error);
