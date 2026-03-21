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
// 版本：1.0.0 (2026-03-21)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const fs = require('fs');
const path = require('path');
const os = require('os');

const SCRIPT_VERSION = '1.1.0';
const SCRIPT_PATH = 'publish/scripts/assemble-story.js';

// Google Drive 上傳設定
const DRIVE_FOLDER_ID = '1TBD6Xs-wVgqqlX3_13boy4xbBnjQ9LdY'; // 「台灣的故事」資料夾
const GWS_BIN = '/Users/Dave/.nvm/versions/node/v24.13.0/bin/gws';

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
  const urls = {};
  const lines = rawMaterialsMd.split('\n');
  let currentName = '';
  for (const line of lines) {
    // 匹配 "1. **名稱**" 或 "- **名稱**"
    const nameMatch = line.match(/(?:\d+\.\s+|\-\s+)\*\*(.+?)\*\*/);
    if (nameMatch) {
      currentName = nameMatch[1].trim();
    }
    // 匹配 "- URL: https://..."
    const urlMatch = line.match(/URL:\s*(https?:\/\/\S+)/);
    if (urlMatch && currentName) {
      urls[currentName] = urlMatch[1].trim();
    }
  }
  return urls;
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
        // 嘗試為每個來源名稱匹配 URL
        const linkedSources = sourcesRaw.split(/[；;]/).map(s => {
          const name = s.trim();
          // 在 sourceUrls 中找匹配（部分匹配即可）
          let url = '';
          for (const [key, value] of Object.entries(sourceUrls)) {
            if (key.includes(name) || name.includes(key) ||
                // 簡稱匹配
                (name.includes('大屯') && key.includes('大屯')) ||
                (name.includes('災害防救') && key.includes('災害防救')) ||
                (name.includes('科學月刊') && key.includes('科學月刊')) ||
                (name.includes('泛科學') && key.includes('泛科學')) ||
                (name.includes('玉山') && key.includes('玉山')) ||
                (name.includes('氣象署') && key.includes('氣象署')) ||
                (name.includes('觀光局') && key.includes('觀光局')) ||
                (name.includes('維基') && key.includes('維基'))) {
              url = value;
              break;
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

  // 提取下載檔名
  const fnMatch = promptMd.match(/下載檔名[：:]\s*(.+)/);
  if (fnMatch) result.downloadFilename = fnMatch[1].trim();

  // 提取英文 prompt（## English Prompt 到下一個 --- 之間）
  const enMatch = promptMd.match(/## English Prompt.*?\n\n([\s\S]+?)(?=\n---)/);
  if (enMatch) result.englishPrompt = enMatch[1].trim();

  // 提取中文 prompt
  const zhMatch = promptMd.match(/## 中文 Prompt.*?\n\n([\s\S]+?)(?=\n---)/);
  if (zhMatch) result.chinesePrompt = zhMatch[1].trim();

  // 提取迭代表格
  const iterMatch = promptMd.match(/## Prompt 迭代紀錄[\s\S]+?\n\n([\s\S]+?)$/);
  if (iterMatch) {
    const rows = iterMatch[1].split('\n').filter(l => l.startsWith('|') && !l.match(/^\|[\s\-|]+\|$/));
    for (const row of rows) {
      const cells = row.split('|').map(c => c.trim()).filter(Boolean);
      if (cells.length >= 3 && cells[0] !== '版本') {
        result.iterations.push({ version: cells[0], issue: cells[1], fix: cells[2] });
      }
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

    // 提取 URL（處理 **URL**: 或 URL: 兩種格式）
    const urlMatch = content.match(/\*{0,2}URL\*{0,2}[：:]\s*(https?:\/\/\S+)/);
    const url = urlMatch ? urlMatch[1].trim() : '';

    // 提取用途（處理 **用途**： 或 用途： 兩種格式）
    const useMatch = content.match(/\*{0,2}用途\*{0,2}[：:]\s*(.+)/);
    const usage = useMatch ? useMatch[1].trim() : '';

    // 提取授權
    const licMatch = content.match(/\*{0,2}授權\*{0,2}[：:]\s*(.+)/);
    const license = licMatch ? licMatch[1].trim() : '';

    if (title && (url || usage)) {
      sections.push({ title, url, usage, license });
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
  templatePath, date,
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
            ${img.usage ? ` — ${img.usage}` : ''}
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

  // 核心意象引用
  const pullQuote = '這座島嶼是活的——就像你們一樣，每年都在長高。';

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
    <p class="font-headline text-lg text-[var(--primary)] italic mb-3">下一篇預告：島嶼站起來之後，等了很久很久，直到第一個腳印出現……</p>
    <div class="inline-flex flex-col items-center">
      <div class="w-16 h-[2px] bg-[var(--primary)]/30 mb-4"></div>
      <span class="font-label text-base text-[var(--on-surface)]">臺灣的故事 — 敬請期待</span>
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

  if (chalkboardPrompt.downloadFilename) {
    const candidatePath = path.join(downloadsDir, chalkboardPrompt.downloadFilename);
    if (fs.existsSync(candidatePath)) {
      chalkboardImagePath = candidatePath;
      checklist['chalkboard-image'] = true;
      console.log(`[assemble] [OK] chalkboard-image: ${chalkboardPrompt.downloadFilename}`);
    } else {
      console.log(`[assemble] [MISSING] chalkboard-image: ${candidatePath}`);
      // 嘗試模糊搜尋
      const pattern = new RegExp(storyId.toLowerCase() + '.*chalkboard', 'i');
      try {
        const files = fs.readdirSync(downloadsDir);
        const match = files.find(f => pattern.test(f) || f === chalkboardPrompt.downloadFilename);
        if (match) {
          chalkboardImagePath = path.join(downloadsDir, match);
          checklist['chalkboard-image'] = true;
          console.log(`[assemble] [OK] chalkboard-image (fuzzy): ${match}`);
        }
      } catch (e) {
        console.log(`[assemble] [WARN] Cannot read downloads dir: ${downloadsDir}`);
      }
    }
  }

  if (chalkboardImagePath) {
    const ext = path.extname(chalkboardImagePath).toLowerCase();
    chalkboardImageMime = ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg'
      : ext === '.webp' ? 'image/webp' : 'image/png';
    chalkboardImageBase64 = fs.readFileSync(chalkboardImagePath).toString('base64');
    console.log(`[assemble] Image size: ${(chalkboardImageBase64.length * 0.75 / 1024 / 1024).toFixed(1)} MB`);
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
    templatePath, date,
  });

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
  const uploadResults = {};
  if (doUpload) {
    const { execSync } = require('child_process');
    const folderId = driveFolderArg ? driveFolderArg.split('=')[1] : DRIVE_FOLDER_ID;

    // 用 content.md 的標題建立 Drive 友善檔名
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
