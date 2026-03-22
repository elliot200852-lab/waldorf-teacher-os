#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — 臺灣的故事 組裝腳本
// 路徑：publish/scripts/assemble-story.js
// 用途：將故事子資料夾的 5 份 .md 組裝成完整 HTML + PDF
// 依賴：無外部套件（純 Node.js fs/path）
// 跨平台：macOS + Linux（Cowork VM 透過 osascript 橋接 Mac 執行 PDF）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 用法：
//   node publish/scripts/assemble-story.js <story-dir> [options]
//
// 參數：
//   story-dir         故事子資料夾（如 stories/A-origins/A001）
//
// 選項：
//   --season=spring|summer|autumn|winter   手動指定季節（預設：依日期自動偵測）
//   --downloads=PATH   黑板畫圖檔搜尋目錄（預設：~/Downloads）
//   --output=DIR       輸出目錄（預設：temp/）
//   --pdf              同時生成 PDF（呼叫 html-to-pdf.js --auto）
//   --dry-run          不寫入檔案，只輸出 JSON 檢查清單
//   --upload           上傳 HTML + PDF 到 Google Drive（需要 gws CLI）
//   --drive-folder=ID  Drive 目標資料夾 ID（預設：台灣的故事）
//
// 範例：
//   node publish/scripts/assemble-story.js stories/A-origins/A001
//   node publish/scripts/assemble-story.js stories/A-origins/A001 --pdf
//   node publish/scripts/assemble-story.js stories/A-origins/A001 --pdf --upload
//   node publish/scripts/assemble-story.js stories/A-origins/A001 --season=autumn --pdf
//   node publish/scripts/assemble-story.js stories/A-origins/A001 --dry-run
//
// 組裝清單（5 項全數到位才輸出）：
//   [1] content.md        — 故事正文 + 事實出處表
//   [2] narration.md      — 說書指引
//   [3] images.md         — 圖像清單 + 黑板畫步驟
//   [4] chalkboard-prompt.md — Gemini 中英文 prompt + 迭代紀錄
//   [5] ~/Downloads/{filename} — 黑板畫圖檔（base64 內嵌）
//
// 額外：
//   raw-materials.md     — 解析 URL 注入事實出處表超連結
//
// 版本：2.1.0 (2026-03-22) — 加嚴格輸出驗證 + 擴充圖檔搜尋 + 動態 GWS 路徑
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const fs = require('fs');
const path = require('path');
const os = require('os');

const SCRIPT_VERSION = '2.1.0';
const SCRIPT_PATH = 'publish/scripts/assemble-story.js';

// Google Drive 上傳設定
const DRIVE_FOLDER_ID = '1TBD6Xs-wVgqqlX3_13boy4xbBnjQ9LdY'; // 「台灣的故事」資料夾
const GWS_BIN = (() => {
  const { execSync } = require('child_process');
  // 1. Try which (macOS/Linux) or where (Windows)
  try {
    const cmd = process.platform === 'win32' ? 'where gws' : 'which gws';
    const found = execSync(cmd, { encoding: 'utf-8', timeout: 5000 }).trim().split('\n')[0];
    if (found) return found;
  } catch {}
  // 2. Scan nvm versions (macOS)
  const nvmBase = path.join(os.homedir(), '.nvm/versions/node');
  try {
    if (fs.existsSync(nvmBase)) {
      const versions = fs.readdirSync(nvmBase).sort().reverse();
      for (const v of versions) {
        const gwsPath = path.join(nvmBase, v, 'bin/gws');
        if (fs.existsSync(gwsPath)) return gwsPath;
      }
    }
  } catch {}
  // 3. Fallback: assume in PATH
  return 'gws';
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
  const m = md.match(/^#\s+(.+)/m);
  if (!m) return '臺灣的故事';
  // 去掉 story ID 前綴（如 "A001 "）
  return m[1].trim().replace(/^[A-G]\d{3}\s+/, '');
}

// ── 動態提取核心意象（pullQuote）────────────────────
function extractPullQuote(contentMd, contentSections) {
  // 策略 1：找 ## 核心意象 段落
  const coreMatch = contentMd.match(/##\s*核心意象\s*\n+(.+)/);
  if (coreMatch) return coreMatch[1].trim();

  // 策略 2：從故事本文（第一個 section，包含 ## 故事本文）取最後一個有力句子
  // contentSections[0] 通常是故事正文，contentSections[1+] 是地理標記、延伸線索等
  const storySection = contentSections.length > 0 ? contentSections[0] : '';
  if (storySection) {
    const lines = storySection.split('\n').map(l => l.trim()).filter(l =>
      l && !l.startsWith('#') && !l.startsWith('>') && !l.startsWith('|') && !l.startsWith('-') && !l.startsWith('*')
    );
    if (lines.length > 0) {
      // 取倒數第一或第二個段落（最後一段通常是收尾的有力句子）
      const lastLine = lines[lines.length - 1];
      // 取最後一個句號或句尾
      const sentences = lastLine.split(/(?<=[。！？])/);
      const candidate = sentences[sentences.length - 1].trim() || lastLine;
      if (candidate.length > 5) return candidate;
      // 如果太短（可能是殘句），往上找
      if (lines.length > 1) return lines[lines.length - 2];
    }
  }

  // fallback
  return '臺灣的故事——每一頁都藏著一座島嶼的記憶。';
}

// ── 動態提取下篇預告 ─────────────────────────────
function extractNextPreview(contentMd) {
  // 從 ## 延伸線索 中找 **後一篇** 或 **後續連結**
  const nextMatch = contentMd.match(/\*\*後一篇[^*]*\*\*[：:]\s*(.+)/);
  if (nextMatch) {
    let preview = nextMatch[1].trim();
    // 去掉可能的前後篇標題（如「A003 火的禮物」→ 只留描述）
    preview = preview.replace(/^[A-G]\d{3}\s+[^—]+——\s*/, '');
    if (!preview.endsWith('……')) preview += '……';
    return `下一篇預告：${preview}`;
  }

  // 從 narration.md 的 nextStoryLink 欄位（已在 parseNarration 中解析）
  // 這個 fallback 在 assembleHtml 中處理

  return ''; // 空值表示無預告，由 assembleHtml 決定 fallback
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
  const blocks = imagesMd.split(/\n### /);

  for (const block of blocks) {
    if (!block.trim()) continue;
    const lines = block.split('\n');
    const title = lines[0].replace(/^#+\s*/, '').replace(/^\d+\.\s*/, '').trim();
    const content = lines.slice(1).join('\n').trim();

    // 提取 URL — 支援多種格式：
    //   格式 A（舊）：**URL**：https://...  或  URL: https://...
    //   格式 B（現行）：- 來源：名稱（https://url）  或  - 來源：名稱 https://url
    let url = '';
    const urlFormatA = content.match(/\*{0,2}URL\*{0,2}[：:]\s*(https?:\/\/\S+)/);
    if (urlFormatA) {
      url = urlFormatA[1].trim();
    } else {
      // 格式 B：從「來源」行提取括號或裸 URL
      const sourceLineMatch = content.match(/來源[：:]\s*(.+)/);
      if (sourceLineMatch) {
        const sourceLine = sourceLineMatch[1];
        // 嘗試匹配全形括號 （URL） 或半形括號 (URL)
        const parenUrl = sourceLine.match(/[（(](https?:\/\/[^\s）)]+)[）)]/);
        if (parenUrl) {
          url = parenUrl[1].trim();
        } else {
          // 嘗試匹配裸 URL
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

    // 提取來源名稱（不含 URL）
    let sourceName = '';
    const sourceNameMatch = content.match(/來源[：:]\s*([^（(]+)/);
    if (sourceNameMatch) sourceName = sourceNameMatch[1].trim();

    if (title && (url || usage || description)) {
      sections.push({ title, url, usage, license, description, timing, sourceName });
    }
  }

  return sections;
}

// ── 解析 narration.md 段落指引 ───────────────────────
function parseNarration(narrationMd) {
  const result = {
    overallRhythm: [],
    sectionGuides: [],
    activities: [],
    nextStoryLink: '',
  };

  // 節奏表
  const rhythmMatch = narrationMd.match(/\| 段落[\s\S]+?\n\n/);
  if (rhythmMatch) {
    const rows = rhythmMatch[0].split('\n').filter(l => l.startsWith('|') && !l.match(/^\|[\s\-|]+\|$/) && !l.includes('段落'));
    for (const row of rows) {
      const cells = row.split('|').map(c => c.trim()).filter(Boolean);
      if (cells.length >= 4) {
        result.overallRhythm.push({
          section: cells[0],
          theme: cells[1],
          mood: cells[2],
          rhythm: cells[3],
        });
      }
    }
  }

  // 段落指引（### 段落一、段落二...）
  const guideSections = narrationMd.split(/\n### 段落/);
  for (let i = 1; i < guideSections.length; i++) {
    const text = guideSections[i];
    const titleMatch = text.match(/^(.+?)：(.+)/);
    const title = titleMatch ? titleMatch[1].trim() : `段落 ${i}`;
    const subtitle = titleMatch ? titleMatch[2].trim() : '';

    // 關鍵意象
    const imageMatch = text.match(/關鍵意象[*]*[：:]\s*(.+)/);
    const keyImage = imageMatch ? imageMatch[1].trim() : '';

    // 指引內容（扣除標題和關鍵意象行）
    const contentLines = text.split('\n').filter(l =>
      !l.match(/^[一二三四五六七八九十]/) &&
      !l.includes('關鍵意象') &&
      l.trim() !== '' &&
      !l.startsWith('**')
    );

    result.sectionGuides.push({ title, subtitle, keyImage, content: contentLines.join(' ').trim() });
  }

  // 延伸活動
  const actMatch = narrationMd.match(/### 活動[\s\S]+?(?=\n---|\n## |$)/g);
  if (actMatch) {
    for (const act of actMatch) {
      const titleLine = act.match(/### (.+)/);
      const body = act.split('\n').slice(1).join(' ').trim();
      if (titleLine) {
        result.activities.push({ title: titleLine[1].trim(), body });
      }
    }
  }

  // 下一篇銜接
  const nextMatch = narrationMd.match(/## 與下一篇的銜接\n\n([\s\S]+?)$/);
  if (nextMatch) result.nextStoryLink = nextMatch[1].trim();

  return result;
}

// ── 組裝 HTML ────────────────────────────────────────
function assembleHtml({
  storyId, season, title, subtitle,
  contentSections, factTable,
  narration, images, chalkboardPrompt,
  chalkboardImageBase64, chalkboardImageMime,
  templatePath, date, contentMd,
}) {
  const icon = SEASON_ICONS[season];
  const dividerIcon = SEASON_DIVIDER_ICONS[season];
  const seasonLabel = SEASON_LABELS[season];
  const blockMatch = storyId.match(/^([A-G])/);
  const blockId = blockMatch ? blockMatch[1] : '';
  const blockMap = {
    A: 'A-ORIGINS', B: 'B-INDIGENOUS', C: 'C-FORMOSA',
    D: 'D-QING', E: 'E-JAPANESE', F: 'F-ROC', G: 'G-MODERN',
  };
  const blockLabel = blockMap[blockId] || '';

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

  // 說書指引 — 節奏圖示
  const rhythmIcons = ['water', 'volcano', 'terrain', 'favorite', 'self_improvement'];
  const rhythmHtml = narration.overallRhythm.map((r, i) => `
      <div class="flex gap-3 items-start">
        <span class="material-symbols-outlined text-[var(--secondary)] mt-0.5 text-[18px]">${rhythmIcons[i] || 'circle'}</span>
        <div>
          <p class="text-[17px] leading-[1.55]"><span class="font-medium text-[var(--primary)]">${r.theme}</span> — ${r.rhythm}</p>
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

  // 黑板畫指引（從 images.md 提取）
  // 直接用 images.md 中的教師自製建議 section

  // 黑板畫圖檔
  const chalkboardImgTag = chalkboardImageBase64
    ? `<img src="data:${chalkboardImageMime};base64,${chalkboardImageBase64}" alt="A001 黑板畫參考" class="w-full rounded-lg shadow-md my-4" style="max-height: 400px; object-fit: contain;"/>`
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

  // 延伸活動
  const activitiesHtml = narration.activities.map(a => {
    const titleMatch = a.title.match(/(.+?)（(.+?)）/);
    const name = titleMatch ? titleMatch[1] : a.title;
    const duration = titleMatch ? titleMatch[2] : '';
    return `<p><span class="text-[var(--primary)] font-medium">${name}</span>${duration ? `（${duration}）` : ''} — ${a.body}</p>`;
  }).join('\n        ');

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
  臺灣的故事 ${storyId} — ${title}
  TeacherOS 華德福美化文件
  季節：${season}
  生成日期：${date}
  組裝腳本：${SCRIPT_PATH} v${SCRIPT_VERSION}
-->
<head>
${headContent}
</head>

<body class="font-body text-[var(--on-surface)] selection:bg-[var(--secondary)]/20">

<!-- 植物浮水印 -->
<div class="botanical-overlay"></div>

<!-- 頁首導航 -->
<header class="sticky top-0 z-40 bg-[var(--bg-wash-1)]/80 backdrop-blur-xl print:hidden">
  <div class="flex justify-between items-center w-full px-8 py-6 max-w-screen-xl mx-auto">
    <div class="flex items-center gap-3">
      <span class="material-symbols-outlined text-[var(--primary)]" style="font-size: 2rem;">${icon}</span>
      <h1 class="font-headline text-3xl tracking-wide leading-relaxed text-[var(--primary)]">臺灣的故事</h1>
    </div>
    <div class="font-label text-sm text-[var(--on-surface-variant)] tracking-widest">${blockLabel} / ${storyId}</div>
  </div>
  <div class="bg-gradient-to-b from-[var(--outline-variant)] to-transparent h-4 opacity-20"></div>
</header>

<!-- 主內容區 -->
<main class="max-w-[900px] mx-auto px-8 py-6 relative overflow-hidden">

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

  <!-- ===== 故事正文 ===== -->
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

  <!-- ===== 說書指引 ===== -->
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">說書指引</h3>
    <p class="text-[17px] leading-[1.55] mb-3 text-[var(--on-surface-variant)]">建議朗讀時間約 8-10 分鐘。</p>
    <div class="space-y-3">
      ${rhythmHtml}
    </div>
  </section>

  <!-- ===== 延伸活動 ===== -->
  <div class="hand-drawn-border bg-[var(--bg-wash-2)]/50 px-5 py-3 my-4 relative">
    <h4 class="font-headline text-[18px] text-[var(--accent)] mb-1.5 italic">延伸活動</h4>
    <div class="space-y-2 text-[18px] leading-[1.5]">
      ${activitiesHtml}
    </div>
  </div>

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
    <p class="text-[15px] leading-[1.5] mt-3 text-[var(--on-surface-variant)] italic">使用原則：故事朗讀時不出示圖像 → 結束後再展示 → 黑板畫優先於投影</p>
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

  <!-- ===== 下篇預告 ===== -->
  <section class="mb-4 text-center py-3">
    <p class="font-headline text-lg text-[var(--primary)] italic mb-3">${(() => {
      const preview = extractNextPreview(contentMd || '');
      return preview || '臺灣的故事 — 敬請期待';
    })()}</p>
    <div class="inline-flex flex-col items-center">
      <div class="w-16 h-[2px] bg-[var(--primary)]/30 mb-4"></div>
      <span class="font-label text-base text-[var(--on-surface)]">臺灣的故事</span>
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
      <p class="text-[var(--primary)] font-headline italic text-lg">臺灣的故事 — 華德福五年級鄉土課程</p>
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
  const doPdf = args.includes('--pdf');
  const doUpload = args.includes('--upload');
  const dryRun = args.includes('--dry-run');

  const fileArgs = args.filter(a => !a.startsWith('--'));
  const storyDir = fileArgs[0];

  if (!storyDir) {
    console.error('Usage: node assemble-story.js <story-dir> [options]');
    console.error('');
    console.error('Options:');
    console.error('  --season=spring|summer|autumn|winter');
    console.error('  --downloads=PATH   (default: ~/Downloads)');
    console.error('  --output=DIR       (default: temp/)');
    console.error('  --pdf              Also generate PDF');
    console.error('  --upload           Upload HTML+PDF to Google Drive');
    console.error('  --drive-folder=ID  Drive folder ID (default: 台灣的故事)');
    console.error('  --dry-run          Check files only, no output');
    process.exit(1);
  }

  const resolvedDir = path.resolve(storyDir);
  if (!fs.existsSync(resolvedDir)) {
    console.error(`Error: Story directory not found: ${resolvedDir}`);
    process.exit(1);
  }

  const season = seasonArg ? seasonArg.split('=')[1] : detectSeason();
  const downloadsDir = downloadsArg ? downloadsArg.split('=')[1] : path.join(os.homedir(), 'Downloads');
  const outputDir = outputArg ? outputArg.split('=')[1] : 'temp';
  const date = new Date().toISOString().split('T')[0];

  // 提取 story ID（資料夾名稱）
  const storyId = path.basename(resolvedDir);

  console.log(`[assemble] Story: ${storyId}`);
  console.log(`[assemble] Season: ${season}`);
  console.log(`[assemble] Downloads: ${downloadsDir}`);
  console.log(`[assemble] Output: ${outputDir}`);

  // ── 檢查清單 ─────────────────────────────────────
  const checklist = {
    'content.md': false,
    'narration.md': false,
    'images.md': false,
    'chalkboard-prompt.md': false,
    'chalkboard-image': false,
    'raw-materials.md': false,
  };

  const requiredFiles = ['content.md', 'narration.md', 'images.md', 'chalkboard-prompt.md'];
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
    const pattern = new RegExp(storyId.toLowerCase() + '.*chalkboard', 'i');
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

  // ── 讀取所有檔案 ─────────────────────────────────
  const contentMd = fs.readFileSync(path.join(resolvedDir, 'content.md'), 'utf-8');
  const narrationMd = fs.readFileSync(path.join(resolvedDir, 'narration.md'), 'utf-8');
  const imagesMd = fs.readFileSync(path.join(resolvedDir, 'images.md'), 'utf-8');
  const rawMaterialsMd = checklist['raw-materials.md']
    ? fs.readFileSync(path.join(resolvedDir, 'raw-materials.md'), 'utf-8')
    : '';

  // 解析
  const title = extractTitle(contentMd);
  const meta = extractFrontmatter(contentMd);
  const subtitle = meta['子主題'] || meta['區塊'] || '';

  // 故事正文段落（以 --- 分割，排除最後的事實表）
  const allSections = splitByHr(contentMd);
  // 過濾掉 frontmatter（> 開頭）和事實表（## 事實出處）
  const contentSections = allSections.filter(s =>
    !s.startsWith('>') && !s.startsWith('## 事實出處') && !s.includes('| 事實 |')
  );

  const sourceUrls = rawMaterialsMd ? parseSourceUrls(rawMaterialsMd) : {};
  const factTable = parseFactTable(contentMd, sourceUrls);
  const narration = parseNarration(narrationMd);
  const images = parseImages(imagesMd);

  // 模板路徑
  const templatePath = path.resolve('publish/templates/waldorf-base.html');
  if (!fs.existsSync(templatePath)) {
    console.error(`Error: Template not found: ${templatePath}`);
    process.exit(1);
  }

  // ── 組裝 HTML ─────────────────────────────────────
  const html = assembleHtml({
    storyId, season, title, subtitle,
    contentSections, factTable,
    narration, images, chalkboardPrompt,
    chalkboardImageBase64, chalkboardImageMime,
    templatePath, date, contentMd,
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
  if (narration.overallRhythm.length === 0) {
    validationErrors.push('narration.md produced 0 rhythm table entries');
  }

  if (validationErrors.length > 0) {
    console.error('\n[assemble] VALIDATION FAILED — refusing to output:');
    for (const err of validationErrors) {
      console.error(`  - ${err}`);
    }
    process.exit(2); // exit code 2 = validation failure
  }
  console.log('[assemble] [OK] Output validation passed (all 5 checks)');

  // 確保輸出目錄存在
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const htmlFilename = `beautify-${storyId}-完整版.html`;
  const htmlPath = path.join(outputDir, htmlFilename);
  fs.writeFileSync(htmlPath, html, 'utf-8');
  console.log(`\n[assemble] HTML written: ${htmlPath}`);

  // ── 生成 PDF（選用）──────────────────────────────
  if (doPdf) {
    const pdfFilename = `${storyId}-完整版.pdf`;
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
  // 策略：先刪除同 storyId 的舊檔，再上傳新版（upsert）
  const uploadResults = {};
  if (doUpload) {
    const { execSync } = require('child_process');
    const folderId = driveFolderArg ? driveFolderArg.split('=')[1] : DRIVE_FOLDER_ID;

    // Step 1: 搜尋並刪除同 storyId 的舊檔
    console.log(`[upload] Cleaning old files for ${storyId}...`);
    try {
      const searchParams = JSON.stringify({
        q: `'${folderId}' in parents and trashed = false and name contains '${storyId}'`,
        fields: 'files(id,name)',
      });
      const searchResult = execSync(
        `cd /tmp && "${GWS_BIN}" drive files list --params '${searchParams}' --format json`,
        { encoding: 'utf-8', timeout: 30000 }
      );
      const searchParsed = JSON.parse(searchResult.trim());
      const oldFiles = (searchParsed.files || []);
      if (oldFiles.length > 0) {
        console.log(`[upload] Found ${oldFiles.length} old file(s) to remove:`);
        for (const old of oldFiles) {
          console.log(`[upload]   Deleting: ${old.name} (${old.id})`);
          try {
            execSync(
              `cd /tmp && "${GWS_BIN}" drive files delete --params '{"fileId": "${old.id}"}'`,
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

    // Step 2: 上傳新版
    const driveBaseName = `${storyId}-${title.replace(/\s+/g, '')}`;

    const filesToUpload = [
      { local: htmlPath, driveName: `${driveBaseName}.html` },
    ];
    if (doPdf) {
      const pdfPath = path.join(outputDir, `${storyId}-完整版.pdf`);
      if (fs.existsSync(pdfPath)) {
        filesToUpload.push({ local: pdfPath, driveName: `${driveBaseName}.pdf` });
      }
    }

    for (const file of filesToUpload) {
      console.log(`[upload] Uploading ${file.driveName}...`);
      try {
        const result = execSync(
          `"${GWS_BIN}" drive +upload "${path.resolve(file.local)}" --parent ${folderId} --name "${file.driveName}"`,
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
  console.log(`  Story:    ${storyId} — ${title}`);
  console.log(`  Season:   ${season}`);
  console.log(`  Sections: ${contentSections.length} story paragraphs`);
  console.log(`  Facts:    ${factTable.length} entries with ${Object.keys(sourceUrls).length} source URLs`);
  console.log(`  Images:   ${images.length} references`);
  console.log(`  Prompt:   ${chalkboardPrompt.englishPrompt ? 'EN+ZH' : 'none'}`);
  console.log(`  Drawing:  ${chalkboardImageBase64 ? 'embedded' : 'not found'}`);
  console.log(`  HTML:     ${htmlPath}`);
  if (doPdf) console.log(`  PDF:      ${path.join(outputDir, storyId + '-完整版.pdf')}`);
  if (doUpload && Object.keys(uploadResults).length > 0) {
    console.log(`  Drive:`);
    for (const [name, id] of Object.entries(uploadResults)) {
      console.log(`    ${name} → ${id}`);
    }
  }
  console.log(`  Script:   ${SCRIPT_PATH} v${SCRIPT_VERSION}`);
}

main();
