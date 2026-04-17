#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — 臺灣的故事 組裝腳本
// 路徑：publish/scripts/assemble-story.js
// 用途：將故事子資料夾的 .md 組裝成完整 HTML + PDF
// 依賴：assemble-base.js（共用引擎）
// 跨平台：macOS + Windows + Linux
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 用法：
//   node publish/scripts/assemble-story.js <story-dir> [options]
//
// 選項：
//   --season=spring|summer|autumn|winter   手動指定季節（預設：依日期自動偵測）
//   --downloads=PATH   黑板畫圖檔搜尋目錄（預設：~/Downloads）
//   --output=DIR       輸出目錄（預設：temp/）
//   --pdf              同時生成 PDF（呼叫 html-to-pdf.js --auto）
//   --dry-run          不寫入檔案，只輸出 JSON 檢查清單
//   --upload           上傳 HTML + PDF 到 Google Drive（需要 gws CLI）
//   --drive-folder=ID  Drive 目標資料夾 ID（預設：台灣的故事）
//   --version=v2       版本標記（跳過 Drive 清除，檔名加後綴）
//
// 組裝清單：
//   [1] content.md           — 故事正文 + 事實出處表
//   [2] narration.md         — 說書指引
//   [3] images.md            — 圖像清單 + 黑板畫步驟
//   [4] chalkboard-prompt.md — Gemini 中英文 prompt + 迭代紀錄
//   [5] ~/Downloads/{filename} — 黑板畫圖檔（base64 內嵌）
//
// 版本：3.0.0 (2026-03-29) — 重構：共用邏輯移至 assemble-base.js
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const fs = require('fs');
const path = require('path');

const base = require('./assemble-base');

const SCRIPT_VERSION = '3.0.0';
const SCRIPT_PATH = 'publish/scripts/assemble-story.js';
const DRIVE_FOLDER_ID = '1TBD6Xs-wVgqqlX3_13boy4xbBnjQ9LdY';
// REQUIRED_FILES 需搭配 storyId 前綴，由 getRequiredFiles() 產生
const BASE_REQUIRED = ['content.md', 'narration.md', 'images.md', 'chalkboard-prompt.md'];
function getRequiredFiles(id) { return BASE_REQUIRED.map(f => `${id}-${f}`); }
function getOptionalFiles(id) { return [`${id}-raw-materials.md`]; }

// ── 臺灣的故事專用解析器 ─────────────────────────────

function extractTitle(md) {
  const m = md.match(/^#\s+(.+)/m);
  if (!m) return '臺灣的故事';
  return m[1].trim().replace(/^(?:[A-G]\d{3}|EN\d{3})\s+/, '');
}

function extractNextPreview(contentMd) {
  const nextMatch = contentMd.match(/\*\*後一篇[^*]*\*\*[：:]\s*(.+)/);
  if (nextMatch) {
    let preview = nextMatch[1].trim();
    preview = preview.replace(/^[A-G]\d{3}\s+[^—]+——\s*/, '');
    if (!preview.endsWith('……')) preview += '……';
    return `下一篇預告：${preview}`;
  }
  return '';
}

// ── 解析 narration.md 段落指引（story 獨有）────────────
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

    const imageMatch = text.match(/關鍵意象[*]*[：:]\s*(.+)/);
    const keyImage = imageMatch ? imageMatch[1].trim() : '';

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
  const icon = base.SEASON_ICONS[season];
  const dividerIcon = base.SEASON_DIVIDER_ICONS[season];
  const seasonLabel = base.SEASON_LABELS[season];

  const blockMatch = storyId.match(/^([A-G]|EN)/);
  const blockId = blockMatch ? blockMatch[1] : '';
  const blockMap = {
    A: 'A-ORIGINS', EN: 'B-ENCOUNTER', C: 'C-FORMOSA',
    D: 'D-QING', E: 'E-JAPANESE', F: 'F-ROC', G: 'G-MODERN',
  };
  const blockLabel = blockMap[blockId] || '';

  const template = fs.readFileSync(templatePath, 'utf-8');
  const headMatch = template.match(/<head>([\s\S]+?)<\/head>/);
  const headContent = (headMatch ? headMatch[1] : '').replace('{{TITLE}}', `${title} — 臺灣的故事`);

  // Render shared fragments
  const storyParagraphs = base.renderStoryParagraphs(contentSections);
  const factTableHtml = base.renderFactTableHtml(factTable);
  const imageListHtml = base.renderImagesHtml(images);
  const { imgTag: chalkboardImgTag, promptHtml, iterHtml } = base.renderChalkboardSection(chalkboardPrompt, chalkboardImageBase64, chalkboardImageMime, storyId);
  const storyBreak = base.renderStoryBreak();
  const sectionDivider = base.renderSectionDivider(dividerIcon);
  const pullQuote = base.extractPullQuote(contentMd || '', contentSections, '臺灣的故事——每一頁都藏著一座島嶼的記憶。');

  // Story-specific: narration rhythm table
  const rhythmIcons = ['water', 'volcano', 'terrain', 'favorite', 'self_improvement'];
  const rhythmHtml = narration.overallRhythm.map((r, i) => `
      <div class="flex gap-3 items-start">
        <span class="material-symbols-outlined text-[var(--secondary)] mt-0.5 text-[18px]">${rhythmIcons[i] || 'circle'}</span>
        <div>
          <p class="text-[17px] leading-[1.55]"><span class="font-medium text-[var(--primary)]">${r.theme}</span> — ${r.rhythm}</p>
        </div>
      </div>`).join('\n');

  // Story-specific: activities
  const activitiesHtml = narration.activities.map(a => {
    const titleMatch = a.title.match(/(.+?)（(.+?)）/);
    const name = titleMatch ? titleMatch[1] : a.title;
    const duration = titleMatch ? titleMatch[2] : '';
    return `<p><span class="text-[var(--primary)] font-medium">${name}</span>${duration ? `（${duration}）` : ''} — ${a.body}</p>`;
  }).join('\n        ');

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
<style>
@media print {
  body { min-height: auto !important; }
  main { overflow: visible !important; }
  section { break-inside: auto !important; }
  .botanical-overlay { display: none !important; }
}
</style>
</head>

<body class="font-body text-[var(--on-surface)] selection:bg-[var(--secondary)]/20">

<div class="botanical-overlay"></div>

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

<main class="max-w-[900px] mx-auto px-8 py-6 relative">

  <div class="absolute -top-10 -right-10 opacity-[0.07] rotate-12">
    <span class="material-symbols-outlined text-[12rem] text-[var(--primary)]">${icon}</span>
  </div>

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

  ${storyParagraphs.map((html, i) => `
  <section class="mb-6">
    <div class="space-y-3">
      ${html}
    </div>
  </section>
  ${i < storyParagraphs.length - 1 ? storyBreak : ''}`).join('\n')}

  <section class="my-6">
    <div class="bg-[var(--bg-wash-3)] p-5 border-l-[6px] border-[var(--secondary)]/60 rounded-r-xl relative">
      <span class="absolute -top-4 -left-4 material-symbols-outlined text-[var(--secondary)]/30 text-5xl">format_quote</span>
      <blockquote class="font-headline italic text-xl text-[var(--primary)] leading-relaxed">
        ${pullQuote}
      </blockquote>
    </div>
  </section>

  ${sectionDivider}

  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">說書指引</h3>
    <p class="text-[17px] leading-[1.55] mb-3 text-[var(--on-surface-variant)]">建議朗讀時間約 8-10 分鐘。</p>
    <div class="space-y-3">
      ${rhythmHtml}
    </div>
  </section>

  <div class="hand-drawn-border bg-[var(--bg-wash-2)]/50 px-5 py-3 my-4 relative">
    <h4 class="font-headline text-[18px] text-[var(--accent)] mb-1.5 italic">延伸活動</h4>
    <div class="space-y-2 text-[18px] leading-[1.5]">
      ${activitiesHtml}
    </div>
  </div>

  ${sectionDivider}

  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">黑板畫</h3>
    <div class="my-4">${chalkboardImgTag}</div>
    ${promptHtml}
    ${iterHtml}
  </section>

  ${sectionDivider}

  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">圖像資源</h3>
    <div class="space-y-3">
      ${imageListHtml}
    </div>
    <p class="text-[15px] leading-[1.5] mt-3 text-[var(--on-surface-variant)] italic">使用原則：故事朗讀時不出示圖像 → 結束後再展示 → 黑板畫優先於投影</p>
  </section>

  ${sectionDivider}

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
  const opts = base.parseCLIArgs('assemble-story.js');
  const resolvedDir = path.resolve(opts.storyDir);
  if (!fs.existsSync(resolvedDir)) {
    console.error(`Error: Story directory not found: ${resolvedDir}`);
    process.exit(1);
  }

  const storyId = path.basename(resolvedDir);
  console.log(`[assemble] Story: ${storyId}`);
  console.log(`[assemble] Season: ${opts.season}`);
  console.log(`[assemble] Downloads: ${opts.downloadsDir}`);
  console.log(`[assemble] Output: ${opts.outputDir}`);

  // Check files (with storyId prefix)
  const REQUIRED_FILES = getRequiredFiles(storyId);
  const OPTIONAL_FILES = getOptionalFiles(storyId);
  const checklist = base.checkFiles(resolvedDir, REQUIRED_FILES, OPTIONAL_FILES);

  // Parse chalkboard prompt + find image
  let chalkboardPrompt = { englishPrompt: '', chinesePrompt: '', downloadFilename: '', iterations: [] };
  if (checklist[`${storyId}-chalkboard-prompt.md`]) {
    const promptMd = fs.readFileSync(path.join(resolvedDir, `${storyId}-chalkboard-prompt.md`), 'utf-8');
    chalkboardPrompt = base.parseChalkboardPrompt(promptMd);
  }

  // Story uses no search prefix (just storyId pattern)
  const { imagePath, imageBase64: chalkboardImageBase64, imageMime: chalkboardImageMime } =
    base.findChalkboardImage(storyId, opts.downloadsDir, chalkboardPrompt, '');

  checklist['chalkboard-image'] = !!imagePath;

  // Check required files
  const missingRequired = REQUIRED_FILES.filter(f => !checklist[f]);
  if (missingRequired.length > 0 && !opts.dryRun) {
    console.error(`\n[assemble] ABORT: Missing required files: ${missingRequired.join(', ')}`);
    process.exit(1);
  }

  if (opts.dryRun) {
    console.log('\n[assemble] Dry-run checklist:');
    console.log(JSON.stringify(checklist, null, 2));
    process.exit(0);
  }

  // Read and parse all files (with storyId prefix)
  const contentMd = base.stripFrontmatter(fs.readFileSync(path.join(resolvedDir, `${storyId}-content.md`), 'utf-8'));
  const narrationMd = base.stripFrontmatter(fs.readFileSync(path.join(resolvedDir, `${storyId}-narration.md`), 'utf-8'));
  const imagesMd = base.stripFrontmatter(fs.readFileSync(path.join(resolvedDir, `${storyId}-images.md`), 'utf-8'));
  const rawMaterialsMd = checklist[`${storyId}-raw-materials.md`]
    ? fs.readFileSync(path.join(resolvedDir, `${storyId}-raw-materials.md`), 'utf-8') : '';

  const title = extractTitle(contentMd);
  const meta = base.extractFrontmatter(contentMd);
  const subtitle = meta['子主題'] || meta['區塊'] || '';
  const contentSections = base.extractContentSections(contentMd);
  const sourceUrls = rawMaterialsMd ? base.parseSourceUrls(rawMaterialsMd) : {};
  const factTable = base.parseFactTable(contentMd, sourceUrls);
  const narration = parseNarration(narrationMd);
  const images = base.parseImages(imagesMd);

  const templatePath = path.resolve('publish/templates/waldorf-base.html');
  if (!fs.existsSync(templatePath)) {
    console.error(`Error: Template not found: ${templatePath}`);
    process.exit(1);
  }

  // Assemble HTML
  const html = assembleHtml({
    storyId, season: opts.season, title, subtitle,
    contentSections, factTable,
    narration, images, chalkboardPrompt,
    chalkboardImageBase64: checklist['chalkboard-image'] ? chalkboardImageBase64 : '',
    chalkboardImageMime,
    templatePath, date: opts.date, contentMd,
  });

  // Validate
  const validationErrors = [];
  if (contentSections.length === 0) validationErrors.push('content.md produced 0 story paragraphs');
  if (factTable.length === 0) {
    validationErrors.push('Fact table has 0 entries');
  } else if (factTable.filter(f => f.sources && f.sources.some(s => s.url)).length === 0) {
    validationErrors.push('Fact table has entries but 0 clickable source URLs');
  }
  if (images.length === 0) validationErrors.push('images.md produced 0 image references');
  if (!chalkboardImageBase64) validationErrors.push('Chalkboard image not embedded (missing or too small)');
  if (narration.overallRhythm.length === 0) validationErrors.push('narration.md produced 0 rhythm table entries');

  if (validationErrors.length > 0) {
    console.error('\n[assemble] VALIDATION FAILED — refusing to output:');
    for (const err of validationErrors) console.error(`  - ${err}`);
    process.exit(2);
  }
  console.log('[assemble] [OK] Output validation passed (all checks)');

  // Write HTML
  if (!fs.existsSync(opts.outputDir)) fs.mkdirSync(opts.outputDir, { recursive: true });
  const versionSuffix = opts.storyVersion ? `-${opts.storyVersion}` : '';
  const htmlFilename = `beautify-${storyId}${versionSuffix}-完整版.html`;
  const htmlPath = path.join(opts.outputDir, htmlFilename);
  fs.writeFileSync(htmlPath, html, 'utf-8');
  console.log(`\n[assemble] HTML written: ${htmlPath}`);

  // PDF
  if (opts.doPdf) {
    const pdfFilename = `${storyId}${versionSuffix}-完整版.pdf`;
    const pdfPath = path.join(opts.outputDir, pdfFilename);
    base.generatePdf(htmlPath, pdfPath);
  }

  // Upload to Google Drive
  if (opts.doUpload) {
    const folderId = opts.driveFolderOverride || DRIVE_FOLDER_ID;
    const driveBaseName = `${storyId}${versionSuffix}-${title.replace(/\s+/g, '')}`;
    const filesToUpload = [{ local: htmlPath, driveName: `${driveBaseName}.html` }];
    if (opts.doPdf) {
      const pdfPath = path.join(opts.outputDir, `${storyId}${versionSuffix}-完整版.pdf`);
      if (fs.existsSync(pdfPath)) filesToUpload.push({ local: pdfPath, driveName: `${driveBaseName}.pdf` });
    }
    const uploadResults = base.uploadToDrive(folderId, storyId, filesToUpload, opts.storyVersion);

    if (Object.keys(uploadResults).length > 0) {
      console.log(`  Drive:`);
      for (const [name, id] of Object.entries(uploadResults)) console.log(`    ${name} → ${id}`);
    }
  }

  // Summary
  console.log('\n[assemble] ── Summary ──');
  console.log(`  Story:    ${storyId} — ${title}`);
  console.log(`  Season:   ${opts.season}`);
  console.log(`  Sections: ${contentSections.length} story paragraphs`);
  console.log(`  Facts:    ${factTable.length} entries with ${Object.keys(sourceUrls).length} source URLs`);
  console.log(`  Images:   ${images.length} references`);
  console.log(`  Prompt:   ${chalkboardPrompt.englishPrompt ? 'EN+ZH' : 'none'}`);
  console.log(`  Drawing:  ${chalkboardImageBase64 ? 'embedded' : 'not found'}`);
  console.log(`  HTML:     ${htmlPath}`);
  if (opts.doPdf) console.log(`  PDF:      ${path.join(opts.outputDir, storyId + versionSuffix + '-完整版.pdf')}`);
  console.log(`  Script:   ${SCRIPT_PATH} v${SCRIPT_VERSION}`);
}

main();
