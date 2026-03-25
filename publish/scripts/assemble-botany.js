#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — 五年級植物學 組裝腳本
// 路徑：publish/scripts/assemble-botany.js
// 用途：將植物學子資料夾的 .md 組裝成完整 HTML + PDF
// 依賴：無外部套件（純 Node.js fs/path）
// 跨平台：macOS + Linux（Cowork VM 透過 osascript 橋接 Mac 執行 PDF）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 用法：
//   node publish/scripts/assemble-botany.js <lesson-dir> [options]
//
// 參數：
//   lesson-dir        植物學子資料夾（如 Botany_Chapters/B001）
//
// 選項：
//   --season=spring|summer|autumn|winter   手動指定季節（預設：依日期自動偵測）
//   --downloads=PATH   黑板畫圖檔搜尋目錄（預設：~/Downloads）
//   --output=DIR       輸出目錄（預設：temp/）
//   --pdf              同時生成 PDF（呼叫 html-to-pdf.js --auto）
//   --dry-run          不寫入檔案，只輸出 JSON 檢查清單
//   --upload           上傳 HTML + PDF 到 Google Drive（需要 gws CLI）
//   --drive-folder=ID  Drive 目標資料夾 ID（預設：五年級植物學）
//
// 範例：
//   node publish/scripts/assemble-botany.js Botany_Chapters/B001
//   node publish/scripts/assemble-botany.js Botany_Chapters/B001 --pdf
//   node publish/scripts/assemble-botany.js Botany_Chapters/B001 --pdf --upload
//   node publish/scripts/assemble-botany.js Botany_Chapters/B001 --season=autumn --pdf
//   node publish/scripts/assemble-botany.js Botany_Chapters/B001 --dry-run
//
// 組裝清單：
//   [1] content.md           — 課程正文 + 事實出處表
//   [2] kovacs-teaching.md   — Kovacs 教學精要
//   [3] images.md            — 圖像清單 + 黑板畫步驟
//   [4] chalkboard-prompt.md — Gemini 中英文 prompt + 迭代紀錄
//   [5] references.md        — 參考來源
//   [6] ~/Downloads/{filename} — 黑板畫圖檔（base64 內嵌）
//
// 額外：
//   raw-materials.md     — 解析 URL 注入事實出處表超連結
//
// 版本：1.0.0 (2026-03-24) — fork from assemble-story.js v2.2.0，植物學專用
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const fs = require('fs');
const path = require('path');
const os = require('os');

const SCRIPT_VERSION = '1.0.0';
const SCRIPT_PATH = 'publish/scripts/assemble-botany.js';

// Google Drive 上傳設定
const DRIVE_FOLDER_ID = '1jjtNmAtzcpbzVmHY8Dz8Dqz4w2fMJbU4'; // Google Drive「植物學五年級」

// GWS CLI 解析：找到可用的 gws 指令，優先驗證能實際連線
const GWS_BIN = (() => {
  const { execSync } = require('child_process');

  // 健康檢查：實際呼叫 API 確認 credential 有效
  // stdio: ['pipe','pipe','pipe'] 跨平台取代 2>/dev/null
  // JSON params 用跳脫雙引號，相容 Windows cmd 與 macOS sh
  function gwsHealthCheck(bin) {
    try {
      const params = process.platform === 'win32'
        ? '--params "{\\"fields\\":\\"user\\"}"'
        : '--params \'{"fields":"user"}\'';
      execSync(`${bin} drive about get ${params}`, {
        encoding: 'utf-8', timeout: 10000, stdio: ['pipe', 'pipe', 'pipe']
      });
      return true;
    } catch { return false; }
  }

  // 1. Try which/where 找到的 gws，但必須通過健康檢查
  try {
    const cmd = process.platform === 'win32' ? 'where gws' : 'which gws';
    const found = execSync(cmd, { encoding: 'utf-8', timeout: 5000 }).trim().split('\n')[0];
    if (found && gwsHealthCheck(found)) {
      console.log(`[gws] Using: ${found} (health check passed)`);
      return found;
    }
    if (found) console.warn(`[gws] Found ${found} but health check failed (401), trying npx fallback...`);
  } catch {}

  // 2. Scan nvm versions (macOS) — 只檢查檔案存在，不觸發 npx 下載
  const nvmBase = path.join(os.homedir(), '.nvm/versions/node');
  try {
    if (fs.existsSync(nvmBase)) {
      const versions = fs.readdirSync(nvmBase).sort().reverse();
      for (const v of versions) {
        const gwsPath = path.join(nvmBase, v, 'bin/gws');
        if (fs.existsSync(gwsPath) && gwsHealthCheck(gwsPath)) return gwsPath;
      }
    }
  } catch {}

  // 3. npx fallback — 僅在 npx 已有快取時嘗試（避免觸發長時間下載）
  try {
    const { execSync: es } = require('child_process');
    // npx --no-install: 只用本地快取，不觸發下載
    es('npx --no-install @googleworkspace/cli --version', {
      encoding: 'utf-8', timeout: 5000, stdio: ['pipe', 'pipe', 'pipe']
    });
    const npxBin = 'npx @googleworkspace/cli';
    if (gwsHealthCheck(npxBin)) {
      console.log(`[gws] Using: ${npxBin} (health check passed)`);
      return npxBin;
    }
  } catch {}

  // 4. 未找到可用的 gws — 返回 null，上傳步驟會跳過
  console.warn('[gws] No healthy gws found. Upload will be skipped.');
  return null;
})();

// ── 季節偵測 ─────────────────────────────────────────
function detectSeason(date = new Date()) {
  const month = date.getMonth() + 1; // 1-12
  if (month >= 3 && month <= 5) return 'spring';
  if (month >= 6 && month <= 8) return 'summer';
  if (month >= 9 && month <= 11) return 'autumn';
  return 'winter';
}

const SEASON_ICONS = {
  spring: 'eco',
  summer: 'sunny',
  autumn: 'park',
  winter: 'ac_unit',
};

const SEASON_LABELS = {
  spring: '春季',
  summer: '夏季',
  autumn: '秋季',
  winter: '冬季',
};

const SEASON_DIVIDER_ICONS = {
  spring: 'local_florist',
  summer: 'wb_sunny',
  autumn: 'park',
  winter: 'ac_unit',
};

// ── Markdown 解析輔助 ────────────────────────────────

// 剝除 YAML frontmatter（--- ... --- 區塊）
function stripFrontmatter(md) {
  const match = md.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/);
  return match ? md.slice(match[0].length) : md;
}

function splitByHr(md) {
  // 以 --- 分割段落（至少三個 -，獨佔一行）
  return md.split(/\n---+\n/).map(s => s.trim()).filter(Boolean);
}

function extractFrontmatter(md) {
  // 提取 > 開頭的 metadata 行
  const meta = {};
  const lines = md.split('\n');
  for (const line of lines) {
    const m = line.match(/^>\s*(.+?)：\s*(.+)/);
    if (m) meta[m[1].trim()] = m[2].trim();
  }
  return meta;
}

function extractTitle(md) {
  // 優先讀 YAML frontmatter 的 title 欄位（如 title: 真菌）
  const yamlMatch = md.match(/^---\n([\s\S]*?)\n---/);
  if (yamlMatch) {
    const titleLine = yamlMatch[1].match(/^title:\s*"?([^"\n]+)"?\s*$/m);
    if (titleLine) return titleLine[1].trim();
  }
  // fallback：讀 H1，去掉 lesson ID 前綴（如 "B001 "）
  const m = md.match(/^#\s+(.+)/m);
  if (!m) return '五年級植物學';
  return m[1].trim().replace(/^B\d{3}\s+/, '');
}

// ── 動態提取核心意象（pullQuote）────────────────────
function extractPullQuote(contentMd, contentSections) {
  // 策略 1：找 ## 核心意象 段落
  const coreMatch = contentMd.match(/##\s*核心意象\s*\n+(.+)/);
  if (coreMatch) return coreMatch[1].trim();

  // 策略 2：從正文（第一個 section）取最後一個有力句子
  const storySection = contentSections.length > 0 ? contentSections[0] : '';
  if (storySection) {
    const lines = storySection.split('\n').map(l => l.trim()).filter(l =>
      l && !l.startsWith('#') && !l.startsWith('>') && !l.startsWith('|') && !l.startsWith('-') && !l.startsWith('*')
    );
    if (lines.length > 0) {
      const lastLine = lines[lines.length - 1];
      const sentences = lastLine.split(/(?<=[。！？])/);
      const candidate = sentences[sentences.length - 1].trim() || lastLine;
      if (candidate.length > 5) return candidate;
      if (lines.length > 1) return lines[lines.length - 2];
    }
  }

  // fallback
  return '植物是大地的語言——每一片葉子都藏著生命的智慧。';
}

// ── 動態提取下篇預告 ─────────────────────────────
function extractNextPreview(contentMd, nextLessonTitle) {
  // 策略 1：從 content.md 的 **後一篇** 標記提取
  const nextMatch = contentMd.match(/\*\*後一篇[^*]*\*\*[：:]\s*(.+)/);
  if (nextMatch) {
    let preview = nextMatch[1].trim();
    preview = preview.replace(/^B\d{3}\s+[^—]+——\s*/, '');
    if (!preview.endsWith('……')) preview += '……';
    return `下一課預告：${preview}`;
  }

  // 策略 2：使用 theme-skeleton.yaml 傳入的下一課標題
  if (nextLessonTitle) {
    return `下一課預告：${nextLessonTitle}`;
  }

  return ''; // 空值 = 最後一課，由 assembleHtml 決定 fallback
}

// ── 從 theme-skeleton.yaml 讀取下一課標題 ────────────
function getNextLessonTitle(storyId) {
  // 從 B0XX 提取課號
  const lessonNum = parseInt(storyId.replace('B', ''), 10);
  if (isNaN(lessonNum) || lessonNum >= 30) return ''; // 最後一課

  const nextId = 'B' + String(lessonNum + 1).padStart(3, '0');

  // 嘗試讀取 theme-skeleton.yaml（向上搜尋）
  const skeletonPaths = [
    path.resolve('workspaces/Working_Member/Codeowner_David/projects/botany-grade5/theme-skeleton.yaml'),
    // 也支援從故事子資料夾往上找
    path.resolve(path.dirname(path.dirname(process.argv[2] || '')), 'theme-skeleton.yaml'),
  ];

  for (const skPath of skeletonPaths) {
    try {
      if (!fs.existsSync(skPath)) continue;
      const content = fs.readFileSync(skPath, 'utf-8');
      // 簡易 YAML 解析：找 nextId: 後面的 title:
      const idRegex = new RegExp(`^\\s+${nextId}:`, 'm');
      const idMatch = idRegex.exec(content);
      if (idMatch) {
        const afterId = content.slice(idMatch.index);
        const titleMatch = afterId.match(/title:\s*"?([^"\n]+)"?/);
        if (titleMatch) return titleMatch[1].trim();
      }
    } catch (e) { /* continue */ }
  }

  return '';
}

function mdParagraphsToHtml(text, cssClass = 'text-[18px] leading-[1.6]') {
  // 將純文字段落轉為 <p> 標籤
  const paragraphs = text.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
  return paragraphs.map((p, i) => {
    // 跳過標題行和 metadata 行
    if (p.startsWith('#') || p.startsWith('>')) return '';
    // 處理粗體
    p = p.replace(/\*\*(.+?)\*\*/g, '<span class="font-medium text-[var(--primary)]">$1</span>');
    // 處理行內斜體
    p = p.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    // 保留換行（詩句風格）
    p = p.replace(/\n/g, '<br/>');
    return `<p class="${cssClass}">${p}</p>`;
  }).filter(Boolean).join('\n      ');
}

// ── 解析 raw-materials.md 的來源 URL ────────────────
function parseSourceUrls(rawMaterialsMd) {
  // 建立 {來源名稱: URL} 的對照表
  // 支援兩種格式：
  //   格式 A（舊）：1. **名稱**\n- URL: https://...
  //   格式 B（現行）：1. 名稱 — https://url — 可信度：高
  const urls = {};
  const lines = rawMaterialsMd.split('\n');
  let currentName = '';
  for (const line of lines) {
    // 格式 B：「1. 名稱「描述」 — URL — 可信度」或「1. 名稱 — URL — 可信度」
    const formatB = line.match(/^\d+\.\s+(.+?)\s+—\s+(https?:\/\/\S+)/);
    if (formatB) {
      // 從名稱中提取簡短關鍵字（去掉「」內容和「官網」等後綴）
      const rawName = formatB[1].trim();
      const url = formatB[2].trim();
      // 保留完整名稱作為 key
      urls[rawName] = url;
      // 同時建立簡稱 key（例如「太魯閣國家公園管理處官網「太魯閣峽谷的前世今生」」→「太魯閣」）
      const shortNames = extractShortNames(rawName);
      for (const sn of shortNames) {
        if (!urls[sn]) urls[sn] = url;
      }
      continue;
    }
    // 格式 A（舊）：「1. **名稱**」或「- **名稱**」
    const nameMatch = line.match(/(?:\d+\.\s+|\-\s+)\*\*(.+?)\*\*/);
    if (nameMatch) {
      currentName = nameMatch[1].trim();
    }
    // 格式 A（舊）：「- URL: https://...」或「URL: https://...」
    const urlMatch = line.match(/URL[：:]\s*(https?:\/\/\S+)/);
    if (urlMatch && currentName) {
      urls[currentName] = urlMatch[1].trim();
    }
  }
  return urls;
}

// 從來源全名提取可能的簡稱（用於模糊匹配事實表）
function extractShortNames(fullName) {
  const shorts = [];
  // 去掉「」引號內容，取機構名
  const orgName = fullName.replace(/[「」《》（）()].+?[」》）)]/g, '').trim();
  shorts.push(orgName);
  // 提取關鍵地名/機構名（如「太魯閣」「大屯」「維基百科」）
  const keywords = orgName.match(/[\u4e00-\u9fff]{2,}/g) || [];
  for (const kw of keywords) {
    if (kw.length >= 2 && !['官網', '管理處', '國家', '公園', '管理', '資料'].includes(kw)) {
      shorts.push(kw);
    }
  }
  return shorts;
}

// ── 解析 content.md 的事實出處表 ─────────────────────
function parseFactTable(contentMd, sourceUrls) {
  const lines = contentMd.split('\n');
  const facts = [];
  let inTable = false;
  let headerPassed = false;

  for (const line of lines) {
    if (line.includes('事實') && line.includes('來源') && line.includes('|')) {
      inTable = true;
      continue;
    }
    if (inTable && line.match(/^\|[\s\-|]+\|$/)) {
      headerPassed = true;
      continue;
    }
    if (inTable && headerPassed && line.startsWith('|')) {
      const cells = line.split('|').map(c => c.trim()).filter(Boolean);
      if (cells.length >= 2) {
        const fact = cells[0];
        const sourcesRaw = cells[1];
        // 嘗試為每個來源名稱匹配 URL（通用模糊匹配）
        const linkedSources = sourcesRaw.split(/[；;]/).map(s => {
          const name = s.trim();
          let url = '';
          // 1. 精確匹配
          if (sourceUrls[name]) {
            url = sourceUrls[name];
          } else {
            // 2. 雙向子字串匹配
            for (const [key, value] of Object.entries(sourceUrls)) {
              if (key.includes(name) || name.includes(key)) {
                url = value;
                break;
              }
            }
            // 3. 若仍無匹配，提取中文詞彙做 token 交叉比對
            if (!url) {
              const nameTokens = (name.match(/[\u4e00-\u9fff]{2,}/g) || []).filter(t =>
                !['管理處', '國家', '公園', '官網', '資料', '出處'].includes(t)
              );
              for (const [key, value] of Object.entries(sourceUrls)) {
                const keyTokens = (key.match(/[\u4e00-\u9fff]{2,}/g) || []);
                const overlap = nameTokens.filter(t => keyTokens.some(kt => kt.includes(t) || t.includes(kt)));
                if (overlap.length > 0) {
                  url = value;
                  break;
                }
              }
            }
          }
          return { name, url };
        });
        facts.push({ fact, sources: linkedSources });
      }
    }
    if (inTable && headerPassed && !line.startsWith('|') && line.trim() !== '') {
      inTable = false;
    }
  }
  return facts;
}

// ── 解析 chalkboard-prompt.md ────────────────────────
function parseChalkboardPrompt(promptMd) {
  const result = {
    englishPrompt: '',
    chinesePrompt: '',
    downloadFilename: '',
    iterations: [],
  };

  // 提取下載檔名（支援「下載檔名：」和「下載檔案名：」兩種寫法）
  const fnMatch = promptMd.match(/下載檔[案]?名[：:]\s*(.+)/);
  if (fnMatch) result.downloadFilename = fnMatch[1].trim();

  // 將 md 按 ## 標題分割成區塊
  const sections = {};
  const sectionRegex = /^## (.+)$/gm;
  let match;
  const sectionStarts = [];
  while ((match = sectionRegex.exec(promptMd)) !== null) {
    sectionStarts.push({ title: match[1].trim(), index: match.index + match[0].length });
  }
  for (let i = 0; i < sectionStarts.length; i++) {
    const start = sectionStarts[i].index;
    const end = i + 1 < sectionStarts.length ? sectionStarts[i + 1].index - sectionStarts[i + 1].title.length - 3 : promptMd.length;
    sections[sectionStarts[i].title] = promptMd.slice(start, end).trim();
  }

  // 提取英文 prompt（匹配含「English」或「英文」的標題）
  for (const [title, content] of Object.entries(sections)) {
    if (/english|英文.*prompt|gemini.*製圖/i.test(title)) {
      result.englishPrompt = content.replace(/^\n+/, '').trim();
      break;
    }
  }

  // 提取中文 prompt（匹配含「中文」或「翻譯」的標題）
  for (const [title, content] of Object.entries(sections)) {
    if (/中文|翻譯/.test(title)) {
      result.chinesePrompt = content.replace(/^\n+/, '').trim();
      break;
    }
  }

  // 提取迭代表格（匹配含「迭代」或「紀錄」的標題）
  for (const [title, content] of Object.entries(sections)) {
    if (/迭代|iteration/i.test(title)) {
      const rows = content.split('\n').filter(l => l.startsWith('|') && !l.match(/^\|[\s\-|]+\|$/));
      for (const row of rows) {
        const cells = row.split('|').map(c => c.trim()).filter(Boolean);
        if (cells.length >= 3 && cells[0] !== '版本') {
          result.iterations.push({ version: cells[0], issue: cells[1], fix: cells[2] });
        }
      }
      break;
    }
  }

  return result;
}

// ── 解析 images.md ───────────────────────────────────
function parseImages(imagesMd) {
  const sections = [];
  // 支援 ### N. 格式（B001 風格）與 ## 圖 N： 格式（AI 自動生成風格）
  // 使用 lookahead 保留 ## 前綴，讓 title 提取的 /^#+\s*/ 統一處理
  const blocks = imagesMd.split(/\n(?=#{2,} )/);

  for (const block of blocks) {
    if (!block.trim()) continue;
    const lines = block.split('\n');
    const title = lines[0].replace(/^#+\s*/, '').replace(/^\d+\.\s*/, '').trim();
    const content = lines.slice(1).join('\n').trim();

    // 提取 URL — 支援多種格式：
    //   格式 A（舊）：**URL**：https://...  或  URL: https://...
    //   格式 B（現行）：- 來源：名稱（https://url）  或  - 來源：名稱 https://url
    //   格式 C（植物學）：- 連結：https://url（獨立行）
    let url = '';
    // 格式 C：獨立的「連結」欄位（植物學格式）
    const linkMatch = content.match(/連結[：:]\s*(https?:\/\/\S+)/);
    if (linkMatch) {
      url = linkMatch[1].trim();
    }
    // 格式 A：**URL**：或 URL:
    if (!url) {
      const urlFormatA = content.match(/\*{0,2}URL\*{0,2}[：:]\s*(https?:\/\/\S+)/);
      if (urlFormatA) url = urlFormatA[1].trim();
    }
    // 格式 B：從「來源」行提取括號或裸 URL
    if (!url) {
      const sourceLineMatch = content.match(/來源[：:]\s*(.+)/);
      if (sourceLineMatch) {
        const sourceLine = sourceLineMatch[1];
        const parenUrl = sourceLine.match(/[（(](https?:\/\/[^\s）)]+)[）)]/);
        if (parenUrl) {
          url = parenUrl[1].trim();
        } else {
          const bareUrl = sourceLine.match(/(https?:\/\/\S+)/);
          if (bareUrl) url = bareUrl[1].trim();
        }
      }
    }

    // 提取用途 — 支援多種欄位名：
    //   格式 A（舊）：**用途**：...  或  用途：...
    //   格式 B（現行）：- 在故事中的角色：...
    let usage = '';
    const useFormatA = content.match(/\*{0,2}用途\*{0,2}[：:]\s*(.+)/);
    if (useFormatA) {
      usage = useFormatA[1].trim();
    } else {
      const roleMatch = content.match(/在故事中的角色[：:]\s*(.+)/);
      if (roleMatch) usage = roleMatch[1].trim();
    }

    // 提取授權
    let license = '';
    const licMatch = content.match(/\*{0,2}授權\*{0,2}[：:]\s*(.+)/);
    if (licMatch) license = licMatch[1].trim();

    // 提取描述（現行格式特有）
    let description = '';
    const descMatch = content.match(/描述[：:]\s*(.+)/);
    if (descMatch) description = descMatch[1].trim();

    // 提取展示時機（現行格式特有）
    let timing = '';
    const timingMatch = content.match(/展示時機[：:]\s*(.+)/);
    if (timingMatch) timing = timingMatch[1].trim();

    // 提取來源名稱（不含 URL，截斷到 — 或行尾）
    let sourceName = '';
    const sourceNameMatch = content.match(/來源[：:]\s*(.+)/);
    if (sourceNameMatch) {
      // 去掉 URL 和後續內容，只保留來源名稱
      sourceName = sourceNameMatch[1].replace(/\s*(?:—|--)\s*(?:File:|https?:).*/i, '').trim();
    }

    if (title && (url || usage || description)) {
      sections.push({ title, url, usage, license, description, timing, sourceName });
    }
  }

  return sections;
}

// ── 解析 kovacs-teaching.md ─────────────────────────
function parseKovacsTeaching(kovacsTeachingMd) {
  const result = {
    teachingInsight: '',
    taiwanFunFact: '',
    scienceDialogue: '',
  };

  // 按 ## 標題分割
  const sections = {};
  const sectionRegex = /^## (.+)$/gm;
  let match;
  const sectionStarts = [];
  while ((match = sectionRegex.exec(kovacsTeachingMd)) !== null) {
    sectionStarts.push({ title: match[1].trim(), index: match.index + match[0].length });
  }
  for (let i = 0; i < sectionStarts.length; i++) {
    const start = sectionStarts[i].index;
    const end = i + 1 < sectionStarts.length ? sectionStarts[i + 1].index - sectionStarts[i + 1].title.length - 3 : kovacsTeachingMd.length;
    sections[sectionStarts[i].title] = kovacsTeachingMd.slice(start, end).trim();
  }

  // 教學精要（匹配含「教學」或「精要」或 Kovacs 的標題）
  for (const [title, content] of Object.entries(sections)) {
    if (/教學|精要|Kovacs|巧妙/i.test(title)) {
      result.teachingInsight = content;
      break;
    }
  }
  // fallback: 如果沒有匹配的標題，取第一個 section 的內容
  if (!result.teachingInsight && sectionStarts.length > 0) {
    result.teachingInsight = Object.values(sections)[0] || '';
  }
  // 如果連 section 都沒有，取去掉 frontmatter 後的全文
  if (!result.teachingInsight) {
    result.teachingInsight = stripFrontmatter(kovacsTeachingMd).trim();
  }

  // 台灣植物趣事（匹配含「台灣」或「趣事」或「俗諺」的標題）
  for (const [title, content] of Object.entries(sections)) {
    if (/台灣|趣事|俗諺|諺語|fun/i.test(title)) {
      result.taiwanFunFact = content;
      break;
    }
  }

  // 當代科學對話（匹配含「科學」或「對話」或「差異」的標題）
  for (const [title, content] of Object.entries(sections)) {
    if (/科學|對話|差異|當代|contemporary/i.test(title)) {
      result.scienceDialogue = content;
      break;
    }
  }

  return result;
}

// ── 解析 references.md ──────────────────────────────
function parseReferences(referencesMd) {
  const refs = [];
  const lines = referencesMd.split('\n');
  for (const line of lines) {
    // 格式 A：1. 名稱 —/-- URL —/-- 類型（支援 em dash 和 double dash）
    const match = line.match(/^\d+\.\s+(.+?)\s+(?:—|--)\s+(https?:\/\/\S+)(?:\s+(?:—|--)\s+(.+))?/);
    if (match) {
      refs.push({
        name: match[1].trim(),
        url: match[2].trim(),
        type: match[3] ? match[3].trim() : '網站',
      });
      continue;
    }
    // 格式 B：- 名稱（URL）
    const matchB = line.match(/^[-*]\s+(.+?)[（(](https?:\/\/[^\s）)]+)[）)]/);
    if (matchB) {
      refs.push({
        name: matchB[1].trim(),
        url: matchB[2].trim(),
        type: '網站',
      });
      continue;
    }
    // 格式 C：行中含「URL: https://」或「URL：https://」（AI 學術引用格式）
    // 例：- **臺灣生命大百科**（n.d.）。條目。機構。URL: https://...
    const matchC = line.match(/URL[：:]\s*(https?:\/\/[^\s）)]+)/);
    if (matchC) {
      const nameRaw = line
        .replace(/\*{1,2}([^*]+)\*{1,2}/g, '$1')    // 展開 **bold**
        .replace(/URL[：:]\s*https?:\/\/\S*/g, '')    // 移除 URL 及其後
        .replace(/（[^）]*）。?/g, '')                 // 移除 （年份）
        .replace(/^[-*\d.]\s+/, '')                   // 移除列表前綴
        .replace(/[。\.]\s*$/, '')                    // 去尾部句號
        .trim();
      refs.push({
        name: nameRaw || '參考來源',
        url: matchC[1].replace(/[.)）]+$/, '').trim(),
        type: '網站',
      });
    }
  }
  return refs;
}

// ── 組裝 HTML ────────────────────────────────────────
function assembleHtml({
  storyId, season, title, subtitle,
  contentSections, factTable,
  kovacsTeaching, references, images, chalkboardPrompt,
  chalkboardImageBase64, chalkboardImageMime,
  templatePath, date, contentMd, nextLessonTitle,
}) {
  const icon = SEASON_ICONS[season];
  const dividerIcon = SEASON_DIVIDER_ICONS[season];
  const seasonLabel = SEASON_LABELS[season];

  const blockMap = {
    1: 'BLOCK-1', 2: 'BLOCK-1', 3: 'BLOCK-1', 4: 'BLOCK-1', 5: 'BLOCK-1', 6: 'BLOCK-1',
    7: 'BLOCK-2', 8: 'BLOCK-2', 9: 'BLOCK-2', 10: 'BLOCK-2', 11: 'BLOCK-2', 12: 'BLOCK-2', 13: 'BLOCK-2', 14: 'BLOCK-2',
    15: 'BLOCK-3', 16: 'BLOCK-3', 17: 'BLOCK-3', 18: 'BLOCK-3', 19: 'BLOCK-3', 20: 'BLOCK-3', 21: 'BLOCK-3', 22: 'BLOCK-3',
    23: 'BLOCK-4', 24: 'BLOCK-4', 25: 'BLOCK-4', 26: 'BLOCK-4', 27: 'BLOCK-4', 28: 'BLOCK-4', 29: 'BLOCK-4', 30: 'BLOCK-4',
  };
  const lessonNum = parseInt(storyId.replace('B', ''), 10);
  const blockLabel = blockMap[lessonNum] || '';

  // 讀取模板取得 <head> 中的 style 與 script
  const template = fs.readFileSync(templatePath, 'utf-8');

  // 提取 <head>...</head> 內容
  const headMatch = template.match(/<head>([\s\S]+?)<\/head>/);
  const headContent = headMatch ? headMatch[1] : '';

  // 故事正文段落
  const storyParagraphs = contentSections.map((section, i) => {
    const paras = section.split(/\n{2,}/).map(p => p.trim()).filter(p => p && !p.startsWith('#') && !p.startsWith('>') && !p.startsWith('|'));
    const html = paras.map((p, j) => {
      p = p.replace(/\*\*(.+?)\*\*/g, '<span class="font-medium">$1</span>');

      // 特殊處理：「風來了。雨來了。」— 詩句用 italic + 換行
      if (p.includes('風來了') && p.includes('雨來了')) {
        const lines = p.split(/。/).filter(Boolean).map(l => l.trim() + '。');
        return `<p class="text-[18px] leading-[1.6] font-headline italic text-[var(--primary)]">${lines.join('<br/>')}</p>`;
      }
      // 最後一句「現在，它醒了。」
      if (p.includes('現在，它醒了')) {
        return `<p class="text-[18px] leading-[1.6] font-headline italic text-[var(--primary)]">${p}</p>`;
      }
      // 首段 drop-cap
      if (i === 0 && j === 0) {
        return `<p class="drop-cap text-[18px] leading-[1.6]">${p}</p>`;
      }
      return `<p class="text-[18px] leading-[1.6]">${p}</p>`;
    }).join('\n          ');

    return html;
  });

  // 事實出處表（含超連結）
  const factTableHtml = factTable.map(f => {
    const sourceLinks = f.sources.map(s => {
      if (s.url) return `<a href="${s.url}" target="_blank" class="text-[var(--secondary)] underline decoration-dotted hover:text-[var(--primary)]">${s.name}</a>`;
      return s.name;
    }).join('；');
    return `<tr class="border-b border-[var(--outline-variant)]/20"><td class="py-1.5 pr-4">${f.fact}</td><td class="py-1.5">${sourceLinks}</td></tr>`;
  }).join('\n            ');

  // Kovacs 教學精要 HTML
  const kovacsTeachingHtml = mdParagraphsToHtml(kovacsTeaching.teachingInsight);
  const taiwanFunFactHtml = kovacsTeaching.taiwanFunFact ? mdParagraphsToHtml(kovacsTeaching.taiwanFunFact) : '';
  const scienceDialogueHtml = kovacsTeaching.scienceDialogue ? mdParagraphsToHtml(kovacsTeaching.scienceDialogue) : '';

  // 參考來源 HTML
  const referencesHtml = references.map(ref => `
      <div class="flex gap-3 items-start">
        <span class="material-symbols-outlined text-[var(--secondary)] mt-0.5 text-[18px]">link</span>
        <div>
          <p class="text-[17px] leading-[1.55]">
            <a href="${ref.url}" target="_blank" class="text-[var(--secondary)] underline decoration-dotted hover:text-[var(--primary)]">${ref.name}</a>
            <span class="text-sm text-[var(--on-surface-variant)] ml-2">[${ref.type}]</span>
          </p>
        </div>
      </div>`).join('\n');

  // 圖像清單
  const imageListHtml = images.map(img => `
      <div class="flex gap-3 items-start">
        <span class="material-symbols-outlined text-[var(--secondary)] mt-0.5 text-[18px]">image</span>
        <div>
          <p class="text-[17px] leading-[1.55]">
            <span class="font-medium text-[var(--primary)]">${img.title}</span>
            ${img.description ? `<br/><span class="text-[15px] text-[var(--on-surface-variant)]">${img.description}</span>` : ''}
            ${img.usage ? `<br/><span class="text-[15px]">${img.usage}</span>` : ''}
            ${img.timing ? `<br/><span class="text-[14px] text-[var(--on-surface-variant)] italic">展示時機：${img.timing}</span>` : ''}
            ${img.sourceName ? `<br/><span class="text-sm text-[var(--on-surface-variant)]">來源：${img.sourceName}</span>` : ''}
            ${img.url ? `<br/><a href="${img.url}" target="_blank" class="text-[var(--secondary)] underline decoration-dotted text-sm">${img.url}</a>` : ''}
            ${img.license ? `<span class="text-sm text-[var(--on-surface-variant)] ml-2">[${img.license}]</span>` : ''}
          </p>
        </div>
      </div>`).join('\n');

  // 黑板畫圖檔
  const chalkboardImgTag = chalkboardImageBase64
    ? `<img src="data:${chalkboardImageMime};base64,${chalkboardImageBase64}" alt="${storyId} 黑板畫參考" class="w-full rounded-lg shadow-md my-4" style="max-height: 400px; object-fit: contain;"/>`
    : '<p class="text-sm text-[var(--on-surface-variant)] italic">（黑板畫圖檔未找到）</p>';

  // Gemini Prompt 區塊
  const promptHtml = chalkboardPrompt.englishPrompt
    ? `<div class="bg-[var(--bg-wash-3)]/50 rounded-lg p-4 my-3 text-sm leading-relaxed font-mono">
        <p class="font-label text-xs text-[var(--secondary)] mb-2 uppercase tracking-widest">Gemini Pro Prompt (English)</p>
        <p class="text-[14px] leading-[1.5]">${chalkboardPrompt.englishPrompt.replace(/\n/g, '<br/>')}</p>
      </div>
      <div class="bg-[var(--bg-wash-2)]/50 rounded-lg p-4 my-3 text-sm leading-relaxed">
        <p class="font-label text-xs text-[var(--secondary)] mb-2 uppercase tracking-widest">Gemini Pro Prompt (中文)</p>
        <p class="text-[14px] leading-[1.5]">${chalkboardPrompt.chinesePrompt.replace(/\n/g, '<br/>')}</p>
      </div>`
    : '';

  // 迭代紀錄
  const iterHtml = chalkboardPrompt.iterations.length > 0
    ? `<div class="overflow-x-auto my-3">
        <table class="w-full text-[15px] leading-[1.5]">
          <thead><tr class="border-b border-[var(--outline-variant)]/40">
            <th class="text-left py-1.5 pr-3 font-medium text-[var(--primary)]">版本</th>
            <th class="text-left py-1.5 pr-3 font-medium text-[var(--primary)]">問題</th>
            <th class="text-left py-1.5 font-medium text-[var(--primary)]">修正</th>
          </tr></thead>
          <tbody class="text-[var(--on-surface-variant)]">
            ${chalkboardPrompt.iterations.map(it => `<tr class="border-b border-[var(--outline-variant)]/20"><td class="py-1 pr-3">${it.version}</td><td class="py-1 pr-3">${it.issue}</td><td class="py-1">${it.fix}</td></tr>`).join('\n')}
          </tbody>
        </table>
      </div>`
    : '';

  // 故事段落間分隔符
  const storyBreak = `
    <div class="flex justify-center gap-2 py-3 opacity-30">
      <span class="material-symbols-outlined text-[var(--primary)] text-sm">waves</span>
      <span class="material-symbols-outlined text-[var(--primary)] text-sm">waves</span>
      <span class="material-symbols-outlined text-[var(--primary)] text-sm">waves</span>
    </div>`;

  const sectionDivider = `
    <div class="flex justify-center gap-3 py-3 opacity-40">
      <span class="material-symbols-outlined text-[var(--secondary)] text-sm">${dividerIcon}</span>
      <span class="material-symbols-outlined text-[var(--secondary)] text-sm">${dividerIcon}</span>
      <span class="material-symbols-outlined text-[var(--secondary)] text-sm">${dividerIcon}</span>
    </div>`;

  // 核心意象引用（動態提取）
  const pullQuote = extractPullQuote(contentMd || '', contentSections);

  // 組裝完整 HTML
  const html = `<!DOCTYPE html>
<html class="${season}" lang="zh-TW">
<!--
  五年級植物學 ${storyId} — ${title}
  TeacherOS 華德福美化文件
  季節：${season}
  生成日期：${date}
  組裝腳本：${SCRIPT_PATH} v${SCRIPT_VERSION}
-->
<head>
${headContent}
<style>
/* botany-daily PDF 分頁修正 — 確保內容從第一頁開始流動 */
@media print {
  body { min-height: auto !important; }
  main { overflow: visible !important; }
  section { break-inside: auto !important; }
  .botanical-overlay { display: none !important; }
}
</style>
</head>

<body class="font-body text-[var(--on-surface)] selection:bg-[var(--secondary)]/20">

<!-- 植物浮水印 -->
<div class="botanical-overlay"></div>

<!-- 頁首導航 -->
<header class="sticky top-0 z-40 bg-[var(--bg-wash-1)]/80 backdrop-blur-xl print:hidden">
  <div class="flex justify-between items-center w-full px-8 py-6 max-w-screen-xl mx-auto">
    <div class="flex items-center gap-3">
      <span class="material-symbols-outlined text-[var(--primary)]" style="font-size: 2rem;">${icon}</span>
      <h1 class="font-headline text-3xl tracking-wide leading-relaxed text-[var(--primary)]">五年級植物學</h1>
    </div>
    <div class="font-label text-sm text-[var(--on-surface-variant)] tracking-widest">${blockLabel} / ${storyId}</div>
  </div>
  <div class="bg-gradient-to-b from-[var(--outline-variant)] to-transparent h-4 opacity-20"></div>
</header>

<!-- 主內容區 -->
<main class="max-w-[900px] mx-auto px-8 py-6 relative">

  <!-- 季節裝飾角落 -->
  <div class="absolute -top-10 -right-10 opacity-[0.07] rotate-12">
    <span class="material-symbols-outlined text-[12rem] text-[var(--primary)]">${icon}</span>
  </div>

  <!-- ===== HERO 區塊 ===== -->
  <section class="mb-6 text-center">
    <div class="watercolor-wash-header p-5 mb-3 inline-block w-full">
      <h2 class="font-headline text-4xl md:text-5xl text-on-primary leading-tight font-bold italic mb-2">${title.replace(/^.+?\s/, '')}</h2>
      <p class="text-on-primary/90 font-label tracking-[0.2em] uppercase text-sm">${subtitle}</p>
    </div>
    <div class="flex justify-center gap-4 mt-3 text-sm text-[var(--on-surface-variant)]">
      <span class="font-label">五年級</span>
      <span class="opacity-30">|</span>
      <span class="font-label">${blockLabel}</span>
      <span class="opacity-30">|</span>
      <span class="font-label">${date}</span>
    </div>
  </section>

  ${sectionDivider}

  <!-- ===== 課程正文 ===== -->
  ${storyParagraphs.map((html, i) => `
  <section class="mb-6">
    <div class="space-y-3">
      ${html}
    </div>
  </section>
  ${i < storyParagraphs.length - 1 ? storyBreak : ''}`).join('\n')}

  <!-- ===== 核心意象 ===== -->
  <section class="my-6">
    <div class="bg-[var(--bg-wash-3)] p-5 border-l-[6px] border-[var(--secondary)]/60 rounded-r-xl relative">
      <span class="absolute -top-4 -left-4 material-symbols-outlined text-[var(--secondary)]/30 text-5xl">format_quote</span>
      <blockquote class="font-headline italic text-xl text-[var(--primary)] leading-relaxed">
        ${pullQuote}
      </blockquote>
    </div>
  </section>

  ${sectionDivider}

  <!-- ===== Kovacs 教學精要 ===== -->
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">Kovacs 教學精要</h3>
    <div class="space-y-3">
      ${kovacsTeachingHtml}
    </div>
    ${taiwanFunFactHtml ? `
    <div class="hand-drawn-border bg-[var(--bg-wash-2)]/50 px-5 py-3 my-4">
      <h4 class="font-headline text-[18px] text-[var(--accent)] mb-1.5 italic">台灣植物趣事</h4>
      <div class="text-[18px] leading-[1.6]">${taiwanFunFactHtml}</div>
    </div>` : ''}
  </section>

  ${scienceDialogueHtml ? `
  <!-- ===== 當代科學對話 ===== -->
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">當代科學對話</h3>
    <div class="space-y-3">
      ${scienceDialogueHtml}
    </div>
  </section>` : ''}

  ${sectionDivider}

  <!-- ===== 黑板畫 ===== -->
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">黑板畫</h3>

    <!-- 參考圖 -->
    <div class="my-4">
      ${chalkboardImgTag}
    </div>

    <!-- Gemini Prompt -->
    ${promptHtml}

    <!-- 迭代紀錄 -->
    ${iterHtml}
  </section>

  ${sectionDivider}

  <!-- ===== 圖像資源 ===== -->
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">圖像資源</h3>
    <div class="space-y-3">
      ${imageListHtml}
    </div>
    <p class="text-[15px] leading-[1.5] mt-3 text-[var(--on-surface-variant)] italic">使用原則：課程講述時不出示圖像 → 結束後再展示 → 黑板畫優先於投影</p>
  </section>

  ${sectionDivider}

  <!-- ===== 事實出處 ===== -->
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">事實出處</h3>
    <div class="overflow-x-auto">
      <table class="w-full text-[17px] leading-[1.55]">
        <thead>
          <tr class="border-b border-[var(--outline-variant)]/40">
            <th class="text-left py-2 pr-4 font-medium text-[var(--primary)]">事實</th>
            <th class="text-left py-2 font-medium text-[var(--primary)]">來源</th>
          </tr>
        </thead>
        <tbody class="text-[var(--on-surface-variant)]">
            ${factTableHtml}
        </tbody>
      </table>
    </div>
  </section>

  ${sectionDivider}

  <!-- ===== 參考來源 ===== -->
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">參考來源</h3>
    <div class="space-y-2">
      ${referencesHtml}
    </div>
  </section>

  <!-- ===== 下篇預告 ===== -->
  <section class="mb-4 text-center py-3">
    <p class="font-headline text-lg text-[var(--primary)] italic mb-3">${(() => {
      const preview = extractNextPreview(contentMd || '', nextLessonTitle || '');
      return preview || '五年級植物學 — 全課程完結';
    })()}</p>
    <div class="inline-flex flex-col items-center">
      <div class="w-16 h-[2px] bg-[var(--primary)]/30 mb-4"></div>
      <span class="font-label text-base text-[var(--on-surface)]">五年級植物學</span>
    </div>
  </section>

</main>

<!-- 頁尾 -->
<footer class="bg-[var(--bg-wash-1)] w-full border-t-0 mt-4 pb-6">
  <div class="max-w-4xl mx-auto flex flex-col items-center gap-3 px-6 text-center">
    <div class="w-full opacity-15 flex justify-center items-center gap-2 py-2">
      <span class="material-symbols-outlined text-[var(--secondary)]">${icon}</span>
      <span class="material-symbols-outlined text-[var(--secondary)]">${icon}</span>
      <span class="material-symbols-outlined text-[var(--secondary)]">${icon}</span>
    </div>
    <div class="space-y-2">
      <p class="text-[var(--primary)] font-headline italic text-lg">五年級植物學 — 華德福主課程</p>
    </div>
    <div class="text-[var(--secondary)] font-body text-xs tracking-widest uppercase opacity-60">
      TeacherOS &middot; ${date} ${seasonLabel} &middot; ${blockLabel} / ${storyId}
    </div>
    <div class="text-[var(--on-surface-variant)] font-body text-[10px] tracking-wider opacity-40 mt-1">
      Generated by <a href="https://github.com" class="underline decoration-dotted">${SCRIPT_PATH}</a> v${SCRIPT_VERSION}
    </div>
  </div>
</footer>

</body>
</html>`;

  return html;
}

// ── 主函式 ───────────────────────────────────────────
function main() {
  const args = process.argv.slice(2);

  // 解析選項
  const seasonArg = args.find(a => a.startsWith('--season='));
  const downloadsArg = args.find(a => a.startsWith('--downloads='));
  const outputArg = args.find(a => a.startsWith('--output='));
  const driveFolderArg = args.find(a => a.startsWith('--drive-folder='));
  const versionArg = args.find(a => a.startsWith('--version='));
  const storyVersion = versionArg ? versionArg.split('=')[1] : null; // e.g. "v2"
  const doPdf = args.includes('--pdf');
  const doUpload = args.includes('--upload');
  const dryRun = args.includes('--dry-run');

  const fileArgs = args.filter(a => !a.startsWith('--'));
  const storyDir = fileArgs[0];

  if (!storyDir) {
    console.error('Usage: node assemble-botany.js <lesson-dir> [options]');
    console.error('');
    console.error('Options:');
    console.error('  --season=spring|summer|autumn|winter');
    console.error('  --downloads=PATH   (default: ~/Downloads)');
    console.error('  --output=DIR       (default: temp/)');
    console.error('  --pdf              Also generate PDF');
    console.error('  --upload           Upload HTML+PDF to Google Drive');
    console.error('  --drive-folder=ID  Drive folder ID (default: 五年級植物學)');
    console.error('  --dry-run          Check files only, no output');
    console.error('  --version=v2       Version label (skips Drive cleanup, adds suffix to filenames)');
    process.exit(1);
  }

  const resolvedDir = path.resolve(storyDir);
  if (!fs.existsSync(resolvedDir)) {
    console.error(`Error: Lesson directory not found: ${resolvedDir}`);
    process.exit(1);
  }

  const season = seasonArg ? seasonArg.split('=')[1] : detectSeason();
  const downloadsDir = downloadsArg ? downloadsArg.split('=')[1] : path.join(os.homedir(), 'Downloads');
  const outputDir = outputArg ? outputArg.split('=')[1] : 'temp';
  const date = new Date().toISOString().split('T')[0];

  // 提取 lesson ID（資料夾名稱）
  const storyId = path.basename(resolvedDir);

  console.log(`[assemble] Lesson: ${storyId}`);
  console.log(`[assemble] Season: ${season}`);
  console.log(`[assemble] Downloads: ${downloadsDir}`);
  console.log(`[assemble] Output: ${outputDir}`);

  // ── 檢查清單 ─────────────────────────────────────
  const checklist = {
    'content.md': false,
    'kovacs-teaching.md': false,
    'images.md': false,
    'chalkboard-prompt.md': false,
    'references.md': false,
    'chalkboard-image': false,
    'raw-materials.md': false,
  };

  const requiredFiles = ['content.md', 'kovacs-teaching.md', 'images.md', 'chalkboard-prompt.md', 'references.md'];
  const optionalFiles = ['raw-materials.md'];

  // 檢查必要檔案
  for (const f of [...requiredFiles, ...optionalFiles]) {
    const fp = path.join(resolvedDir, f);
    if (fs.existsSync(fp)) {
      checklist[f] = true;
      console.log(`[assemble] [OK] ${f}`);
    } else {
      const level = requiredFiles.includes(f) ? 'MISSING' : 'OPTIONAL';
      console.log(`[assemble] [${level}] ${f}`);
    }
  }

  // 讀取 chalkboard-prompt.md 取得下載檔名
  let chalkboardPrompt = { englishPrompt: '', chinesePrompt: '', downloadFilename: '', iterations: [] };
  if (checklist['chalkboard-prompt.md']) {
    const promptMd = fs.readFileSync(path.join(resolvedDir, 'chalkboard-prompt.md'), 'utf-8');
    chalkboardPrompt = parseChalkboardPrompt(promptMd);
  }

  // 搜尋黑板畫圖檔
  let chalkboardImagePath = '';
  let chalkboardImageBase64 = '';
  let chalkboardImageMime = 'image/png';

  // 策略 1：精確匹配 chalkboard-prompt.md 中的下載檔名
  if (chalkboardPrompt.downloadFilename) {
    const candidatePath = path.join(downloadsDir, chalkboardPrompt.downloadFilename);
    if (fs.existsSync(candidatePath)) {
      chalkboardImagePath = candidatePath;
      checklist['chalkboard-image'] = true;
      console.log(`[assemble] [OK] chalkboard-image: ${chalkboardPrompt.downloadFilename}`);
    } else {
      console.log(`[assemble] [MISSING] chalkboard-image (exact): ${candidatePath}`);
    }
  }

  // 策略 2：storyId + chalkboard 模糊匹配
  if (!chalkboardImagePath) {
    const pattern = new RegExp('Botany-' + storyId + '.*chalkboard', 'i');
    try {
      const files = fs.readdirSync(downloadsDir);
      const match = files.find(f => pattern.test(f) && /\.(png|jpg|jpeg|webp)$/i.test(f));
      if (match) {
        chalkboardImagePath = path.join(downloadsDir, match);
        checklist['chalkboard-image'] = true;
        console.log(`[assemble] [OK] chalkboard-image (fuzzy): ${match}`);
      }
    } catch (e) {
      console.log(`[assemble] [WARN] Cannot read downloads dir: ${downloadsDir}`);
    }
  }

  // 策略 3：Gemini 預設檔名（取 30 分鐘內最新的）
  if (!chalkboardImagePath) {
    try {
      const files = fs.readdirSync(downloadsDir)
        .filter(f => /^Gemini_Generated_Image/i.test(f) && /\.(png|jpg|jpeg|webp)$/i.test(f))
        .map(f => ({ name: f, mtime: fs.statSync(path.join(downloadsDir, f)).mtime }))
        .sort((a, b) => b.mtime - a.mtime);
      const thirtyMinAgo = Date.now() - 30 * 60 * 1000;
      const recent = files.find(f => f.mtime.getTime() > thirtyMinAgo);
      if (recent) {
        chalkboardImagePath = path.join(downloadsDir, recent.name);
        checklist['chalkboard-image'] = true;
        console.log(`[assemble] [OK] chalkboard-image (gemini-recent): ${recent.name}`);
      }
    } catch (e) { /* ignore */ }
  }

  // 策略 4：任何含 storyId 的圖檔
  if (!chalkboardImagePath) {
    try {
      const files = fs.readdirSync(downloadsDir)
        .filter(f => f.toLowerCase().includes(storyId.toLowerCase()) && /\.(png|jpg|jpeg|webp)$/i.test(f));
      if (files.length > 0) {
        chalkboardImagePath = path.join(downloadsDir, files[0]);
        checklist['chalkboard-image'] = true;
        console.log(`[assemble] [OK] chalkboard-image (id-match): ${files[0]}`);
      }
    } catch (e) { /* ignore */ }
  }

  if (!chalkboardImagePath) {
    console.error(`[assemble] [FAIL] chalkboard-image: 4 strategies exhausted, no image found in ${downloadsDir}`);
  }

  // 讀取圖檔並驗證大小
  if (chalkboardImagePath) {
    const ext = path.extname(chalkboardImagePath).toLowerCase();
    chalkboardImageMime = ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg'
      : ext === '.webp' ? 'image/webp' : 'image/png';
    chalkboardImageBase64 = fs.readFileSync(chalkboardImagePath).toString('base64');
    const sizeKB = chalkboardImageBase64.length * 0.75 / 1024;
    console.log(`[assemble] Image size: ${(sizeKB / 1024).toFixed(1)} MB`);
    if (sizeKB < 50) {
      console.error(`[assemble] [FAIL] Chalkboard image too small: ${sizeKB.toFixed(0)} KB (min 50KB)`);
      chalkboardImageBase64 = '';
      chalkboardImagePath = '';
      checklist['chalkboard-image'] = false;
    }
  }

  // ── 檢查結果 ─────────────────────────────────────
  const missingRequired = requiredFiles.filter(f => !checklist[f]);
  if (missingRequired.length > 0 && !dryRun) {
    console.error(`\n[assemble] ABORT: Missing required files: ${missingRequired.join(', ')}`);
    process.exit(1);
  }

  if (dryRun) {
    console.log('\n[assemble] Dry-run checklist:');
    console.log(JSON.stringify(checklist, null, 2));
    process.exit(0);
  }

  // ── 讀取所有檔案（剝除 YAML frontmatter）──────────
  const contentMd = stripFrontmatter(fs.readFileSync(path.join(resolvedDir, 'content.md'), 'utf-8'));
  const kovacsTeachingMd = stripFrontmatter(fs.readFileSync(path.join(resolvedDir, 'kovacs-teaching.md'), 'utf-8'));
  const imagesMd = stripFrontmatter(fs.readFileSync(path.join(resolvedDir, 'images.md'), 'utf-8'));
  const referencesMd = fs.readFileSync(path.join(resolvedDir, 'references.md'), 'utf-8');
  const rawMaterialsMd = checklist['raw-materials.md']
    ? fs.readFileSync(path.join(resolvedDir, 'raw-materials.md'), 'utf-8')
    : '';

  // 解析
  const title = extractTitle(contentMd);
  const meta = extractFrontmatter(contentMd);
  const subtitle = meta['子主題'] || meta['區塊'] || '';

  // 課程正文段落：從 content.md 中精確提取「## 故事本文」段落
  // 策略：按 ## 標題切段，只取「故事本文」區塊的內容
  const contentSections = (() => {
    // 按 ## 標題切分（保留標題行作為段落開頭）
    const h2Parts = contentMd.split(/(?=^## )/m).map(s => s.trim()).filter(Boolean);
    // 找「## 故事本文」段落
    const storyPart = h2Parts.find(p => /^## 故事本文/.test(p));
    if (storyPart) {
      // 移除標題行本身，保留正文
      const body = storyPart.replace(/^## 故事本文\s*\n+/, '').trim();
      return body ? [body] : [];
    }
    // fallback 1：沒有「## 故事本文」時，收集所有非保留 ## 段落合併為故事正文
    // 保留段落：事實出處、地理標記、延伸線索、注意事項、資料來源、下一課預告
    const RESERVED = /^## ?(事實|地理標記|延伸線索|注意事項|資料來源|參考來源|下一課)/;
    const storyParts = h2Parts
      .filter(p => !RESERVED.test(p) && !/^# /.test(p))
      .map(p => p.replace(/^##+ [^\n]+\n/, '').trim())
      .filter(p => p.length > 0);
    if (storyParts.length > 0) {
      return [storyParts.join('\n\n')];
    }
    // fallback 2：最終保底，splitByHr 舊邏輯（去掉 !s.startsWith('#') 以避免過濾正文）
    const allSections = splitByHr(contentMd);
    return allSections.filter(s =>
      !s.startsWith('>') &&
      !s.startsWith('## 事實出處') && !s.includes('| 事實 |') &&
      !s.startsWith('## 地理標記') &&
      !s.startsWith('## 延伸線索')
    );
  })();

  const sourceUrls = rawMaterialsMd ? parseSourceUrls(rawMaterialsMd) : {};
  const factTable = parseFactTable(contentMd, sourceUrls);
  const kovacsTeaching = parseKovacsTeaching(kovacsTeachingMd);
  const references = parseReferences(referencesMd);
  const images = parseImages(imagesMd);

  // 模板路徑
  const templatePath = path.resolve('publish/templates/waldorf-base.html');
  if (!fs.existsSync(templatePath)) {
    console.error(`Error: Template not found: ${templatePath}`);
    process.exit(1);
  }

  // ── 取得下一課標題（從 theme-skeleton.yaml）──────────
  const nextLessonTitle = getNextLessonTitle(storyId);
  if (nextLessonTitle) {
    console.log(`[assemble] Next lesson: ${nextLessonTitle}`);
  }

  // ── 組裝 HTML ─────────────────────────────────────
  const html = assembleHtml({
    storyId, season, title, subtitle,
    contentSections, factTable,
    kovacsTeaching, references, images, chalkboardPrompt,
    chalkboardImageBase64, chalkboardImageMime,
    templatePath, date, contentMd, nextLessonTitle,
  });

  // ── 嚴格輸出驗證（全部通過才寫入）──────────────────
  const validationErrors = [];

  if (contentSections.length === 0) {
    validationErrors.push('content.md produced 0 story paragraphs');
  }
  if (factTable.length === 0) {
    validationErrors.push('Fact table has 0 entries');
  } else {
    const factsWithUrls = factTable.filter(f => f.sources && f.sources.some(s => s.url));
    if (factsWithUrls.length === 0) {
      validationErrors.push('Fact table has entries but 0 clickable source URLs');
    }
  }
  if (images.length === 0) {
    validationErrors.push('images.md produced 0 image references');
  }
  if (!chalkboardImageBase64) {
    validationErrors.push('Chalkboard image not embedded (missing or too small)');
  }
  if (!kovacsTeaching.teachingInsight) {
    validationErrors.push('kovacs-teaching.md has no teaching insight');
  }
  if (references.length === 0) {
    validationErrors.push('references.md has 0 entries');
  }

  if (validationErrors.length > 0) {
    console.error('\n[assemble] VALIDATION FAILED — refusing to output:');
    for (const err of validationErrors) {
      console.error(`  - ${err}`);
    }
    process.exit(2); // exit code 2 = validation failure
  }
  console.log('[assemble] [OK] Output validation passed (all checks)');

  // 確保輸出目錄存在
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const versionSuffix = storyVersion ? `-${storyVersion}` : '';
  const htmlFilename = `${storyId}${versionSuffix}-植物學完整版.html`;
  const htmlPath = path.join(outputDir, htmlFilename);
  fs.writeFileSync(htmlPath, html, 'utf-8');
  console.log(`\n[assemble] HTML written: ${htmlPath}`);

  // ── 生成 PDF（選用）──────────────────────────────
  if (doPdf) {
    const pdfFilename = `${storyId}${versionSuffix}-植物學完整版.pdf`;
    const pdfPath = path.join(outputDir, pdfFilename);
    const pdfScript = path.resolve('publish/scripts/html-to-pdf.js');
    console.log(`[assemble] Generating PDF: ${pdfPath}`);
    const { execSync } = require('child_process');
    try {
      execSync(`node "${pdfScript}" "${htmlPath}" "${pdfPath}" --auto`, {
        stdio: 'inherit',
        cwd: process.cwd(),
      });
      console.log(`[assemble] PDF written: ${pdfPath}`);
    } catch (e) {
      console.error(`[assemble] PDF generation failed: ${e.message}`);
      console.error(`[assemble] HTML is still available at: ${htmlPath}`);
    }
  }

  // ── 上傳到 Google Drive（選用）──────────────────
  // 策略：無版本號時先刪除舊檔再上傳（upsert）；有版本號時保留舊版直接上傳
  const uploadResults = {};
  if (doUpload && !GWS_BIN) {
    console.warn('[upload] Skipped — no GWS CLI available. HTML/PDF saved locally.');
    console.warn('[upload] Install gws (npm install -g @googleworkspace/cli) and run gws auth login to enable upload.');
  }
  if (doUpload && GWS_BIN) {
    const { execSync } = require('child_process');
    const folderId = driveFolderArg ? driveFolderArg.split('=')[1] : DRIVE_FOLDER_ID;

    // Step 1: 搜尋並刪除同 storyId 的舊檔（僅在無版本號時執行）
    if (storyVersion) {
      console.log(`[upload] Version mode (${storyVersion}): skipping cleanup, preserving old files.`);
    } else {
      console.log(`[upload] Cleaning old files for ${storyId}...`);
    try {
      const searchParams = JSON.stringify({
        q: `'${folderId}' in parents and trashed = false and name contains '${storyId}'`,
        fields: 'files(id,name)',
      });
      const quotedSearch = process.platform === 'win32'
        ? `--params "${searchParams.replace(/"/g, '\\"')}"`
        : `--params '${searchParams}'`;
      const searchResult = execSync(
        `${GWS_BIN} drive files list ${quotedSearch} --format json`,
        { encoding: 'utf-8', timeout: 30000 }
      );
      const searchParsed = JSON.parse(searchResult.trim());
      const oldFiles = (searchParsed.files || []);
      if (oldFiles.length > 0) {
        console.log(`[upload] Found ${oldFiles.length} old file(s) to remove:`);
        for (const old of oldFiles) {
          console.log(`[upload]   Deleting: ${old.name} (${old.id})`);
          try {
            const delParams = process.platform === 'win32'
              ? `--params "{\\"fileId\\": \\"${old.id}\\"}"`
              : `--params '{"fileId": "${old.id}"}'`;
            execSync(
              `${GWS_BIN} drive files delete ${delParams}`,
              { encoding: 'utf-8', timeout: 30000 }
            );
          } catch (delErr) {
            console.error(`[upload]   Delete failed: ${old.name} — ${delErr.message}`);
          }
        }
        console.log(`[upload] Cleanup done.`);
      } else {
        console.log(`[upload] No old files found. Clean upload.`);
      }
    } catch (searchErr) {
      console.error(`[upload] Search/cleanup failed (non-fatal): ${searchErr.message}`);
    }
    } // end of !storyVersion cleanup block

    // Step 2: 上傳新版
    const versionLabel = storyVersion ? `-${storyVersion}` : '';
    const driveBaseName = `${storyId}${versionLabel}-${title.replace(/\s+/g, '')}`;

    const filesToUpload = [
      { local: htmlPath, driveName: `${driveBaseName}.html` },
    ];
    if (doPdf) {
      const pdfPath = path.join(outputDir, `${storyId}${versionSuffix}-植物學完整版.pdf`);
      if (fs.existsSync(pdfPath)) {
        filesToUpload.push({ local: pdfPath, driveName: `${driveBaseName}.pdf` });
      }
    }

    for (const file of filesToUpload) {
      console.log(`[upload] Uploading ${file.driveName}...`);
      try {
        const result = execSync(
          `${GWS_BIN} drive +upload "${path.resolve(file.local)}" --parent ${folderId} --name "${file.driveName}"`,
          { encoding: 'utf-8', timeout: 120000 }
        );
        const parsed = JSON.parse(result.trim());
        uploadResults[file.driveName] = parsed.id;
        console.log(`[upload] OK: ${file.driveName} → ${parsed.id}`);
      } catch (e) {
        console.error(`[upload] FAILED: ${file.driveName} — ${e.message}`);
        uploadResults[file.driveName] = 'FAILED';
      }
    }
  }

  // ── 輸出摘要 ─────────────────────────────────────
  console.log('\n[assemble] ── Summary ──');
  console.log(`  Lesson:   ${storyId} — ${title}`);
  console.log(`  Season:   ${season}`);
  console.log(`  Sections: ${contentSections.length} content paragraphs`);
  console.log(`  Facts:    ${factTable.length} entries with ${Object.keys(sourceUrls).length} source URLs`);
  console.log(`  Kovacs:   ${kovacsTeaching.teachingInsight ? 'present' : 'missing'}`);
  console.log(`  Refs:     ${references.length} entries`);
  console.log(`  Images:   ${images.length} references`);
  console.log(`  Prompt:   ${chalkboardPrompt.englishPrompt ? 'EN+ZH' : 'none'}`);
  console.log(`  Drawing:  ${chalkboardImageBase64 ? 'embedded' : 'not found'}`);
  console.log(`  HTML:     ${htmlPath}`);
  if (doPdf) console.log(`  PDF:      ${path.join(outputDir, storyId + versionSuffix + '-植物學完整版.pdf')}`);
  if (doUpload && Object.keys(uploadResults).length > 0) {
    console.log(`  Drive:`);
    for (const [name, id] of Object.entries(uploadResults)) {
      console.log(`    ${name} → ${id}`);
    }
  }
  console.log(`  Script:   ${SCRIPT_PATH} v${SCRIPT_VERSION}`);
}

main();
