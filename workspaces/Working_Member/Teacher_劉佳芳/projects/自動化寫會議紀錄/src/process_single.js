require('dotenv').config();
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { GoogleAIFileManager } = require('@google/generative-ai/server');
const fs = require('fs');
const path = require('path');

const apiKey = process.env.GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(apiKey);
const fileManager = new GoogleAIFileManager(apiKey);

// 只處理指定的單一檔案
const targetFile = process.argv[2]; // 從命令列參數取得檔名
if (!targetFile) {
  console.error('請指定要處理的檔名，例如: node src/process_single.js "課品小組開會.m4a"');
  process.exit(1);
}

const inputDir = path.join(__dirname, '../data/raw_notes');
const outputDir = path.join(__dirname, '../data/output');

async function uploadToGemini(filePath, mimeType) {
  const uploadResult = await fileManager.uploadFile(filePath, {
    mimeType,
    displayName: path.basename(filePath),
  });
  const file = uploadResult.file;
  console.log(`✅ 已上傳檔案: ${file.displayName} => ${file.name}`);
  
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

async function generateWithRetry(modelName, contentParts, retries = 3) {
  const model = genAI.getGenerativeModel({ model: modelName });
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      console.log(`正在使用模型 ${modelName} 生成內容 (第 ${attempt} 次嘗試)...`);
      const result = await model.generateContent(contentParts);
      return result.response.text();
    } catch (err) {
      console.error(`Attempt ${attempt} failed:`, err.message);
      if (attempt === retries) throw err;
      console.log('等待 10 秒後重試...');
      await new Promise(r => setTimeout(r, 10000));
    }
  }
}

async function main() {
  const filePath = path.join(inputDir, targetFile);
  if (!fs.existsSync(filePath)) {
    console.error(`找不到檔案: ${filePath}`);
    process.exit(1);
  }

  console.log(`開始處理: ${targetFile}`);

  const ext = path.extname(targetFile).toLowerCase();
  let mimeType = 'audio/mp3';
  if (ext === '.wav') mimeType = 'audio/wav';
  else if (ext === '.m4a' || ext === '.mp4') mimeType = 'audio/m4a';
  else if (ext === '.ogg') mimeType = 'audio/ogg';

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

  console.log(`正在上傳 ${targetFile} 至 Gemini API...`);
  const geminiFile = await uploadToGemini(filePath, mimeType);

  const contentParts = [
    prompt,
    {
      fileData: {
        mimeType: geminiFile.mimeType,
        fileUri: geminiFile.uri
      }
    }
  ];

  let text;
  try {
    text = await generateWithRetry('gemini-2.5-flash', contentParts, 1);
  } catch (e) {
    console.log('gemini-2.5-flash 失敗，切換至 gemini-1.5-flash...');
    try {
      text = await generateWithRetry('gemini-1.5-flash', contentParts, 2);
    } catch (e2) {
      console.log('gemini-1.5-flash 失敗，切換至 gemini-1.5-pro...');
      text = await generateWithRetry('gemini-1.5-pro', contentParts, 2);
    }
  }

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputFileName = targetFile.replace(new RegExp(`\\${ext}$`, 'i'), '_processed.md');
  const outputPath = path.join(outputDir, outputFileName);

  fs.writeFileSync(outputPath, text, 'utf8');
  console.log(`\n✅ 成功產出: ${outputPath}`);
  console.log(`   檔案大小: ${Buffer.byteLength(text, 'utf8')} bytes`);
}

main().catch(err => {
  console.error('執行失敗:', err);
  process.exit(1);
});
