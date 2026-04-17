#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — 五年級植物學 組裝腳本
// 路徑：publish/scripts/assemble-botany.js
// 用途：將植物學子資料夾的 .md 組裝成完整 HTML + PDF
// 依賴：assemble-base.js（共用引擎）
// 跨平台：macOS + Windows + Linux
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 用法：
//   node publish/scripts/assemble-botany.js <lesson-dir> [options]
//
// 選項：
//   --season=spring|summer|autumn|winter   手動指定季節（預設：依日期自動偵測）
//   --downloads=PATH   黑板畫圖檔搜尋目錄（預設：~/Downloads）
//   --output=DIR       輸出目錄（預設：temp/）
//   --pdf              同時生成 PDF（呼叫 html-to-pdf.js --auto）
//   --dry-run          不寫入檔案，只輸出 JSON 檢查清單
//   --upload           上傳 HTML + PDF 到 Google Drive（需要 gws CLI）
//   --drive-folder=ID  Drive 目標資料夾 ID（預設：五年級植物學）
//   --version=v2       版本標記（跳過 Drive 清除，檔名加後綴）
//
// 組裝清單：
//   [1] content.md           — 課程正文 + 事實出處表
//   [2] kovacs-teaching.md   — Kovacs 教學精要
//   [3] images.md            — 圖像清單 + 黑板畫步驟
//   [4] chalkboard-prompt.md — Gemini 中英文 prompt + 迭代紀錄
//   [5] references.md        — 參考來源
//   [6] ~/Downloads/{filename} — 黑板畫圖檔（base64 內嵌）
//
// 版本：2.0.0 (2026-03-29) — 重構：共用邏輯移至 assemble-base.js
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const fs = require('fs');
const path = require('path');

const base = require('./assemble-base');

const SCRIPT_VERSION = '2.0.0';
const SCRIPT_PATH = 'publish/scripts/assemble-botany.js';
const DRIVE_FOLDER_ID = '1jjtNmAtzcpbzVmHY8Dz8Dqz4w2fMJbU4';
// REQUIRED_FILES 需搭配 storyId 前綴，由 getRequiredFiles() 產生
const BASE_REQUIRED = ['content.md', 'kovacs-teaching.md', 'images.md', 'chalkboard-prompt.md', 'references.md'];
function getRequiredFiles(id) { return BASE_REQUIRED.map(f => `${id}-${f}`); }
function getOptionalFiles(id) { return [`${id}-raw-materials.md`]; }

// ── 植物學專用解析器 ─────────────────────────────────

function extractTitle(md) {
  const yamlMatch = md.match(/^---\n([\s\S]*?)\n---/);
  if (yamlMatch) {
    const titleLine = yamlMatch[1].match(/^title:\s*"?([^"\n]+)"?\s*$/m);
    if (titleLine) return titleLine[1].trim();
  }
  const m = md.match(/^#\s+(.+)/m);
  if (!m) return '五年級植物學';
  return m[1].trim().replace(/^B\d{3}\s+/, '');
}

function parseKovacsTeaching(kovacsTeachingMd) {
  const result = { teachingInsight: '', taiwanFunFact: '', scienceDialogue: '' };
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

  for (const [title, content] of Object.entries(sections)) {
    if (/教學|精要|Kovacs|巧妙/i.test(title)) { result.teachingInsight = content; break; }
  }
  if (!result.teachingInsight && sectionStarts.length > 0) {
    result.teachingInsight = Object.values(sections)[0] || '';
  }
  if (!result.teachingInsight) {
    result.teachingInsight = base.stripFrontmatter(kovacsTeachingMd).trim();
  }

  for (const [title, content] of Object.entries(sections)) {
    if (/台灣|趣事|俗諺|諺語|fun/i.test(title)) { result.taiwanFunFact = content; break; }
  }
  for (const [title, content] of Object.entries(sections)) {
    if (/科學|對話|差異|當代|contemporary/i.test(title)) { result.scienceDialogue = content; break; }
  }

  return result;
}

function getNextLessonTitle(storyId) {
  const lessonNum = parseInt(storyId.replace('B', ''), 10);
  if (isNaN(lessonNum) || lessonNum >= 30) return '';
  const nextId = 'B' + String(lessonNum + 1).padStart(3, '0');
  const skeletonPaths = [
    path.resolve('workspaces/Working_Member/Codeowner_David/projects/botany-grade5/theme-skeleton.yaml'),
    path.resolve(path.dirname(path.dirname(process.argv[2] || '')), 'theme-skeleton.yaml'),
  ];
  for (const skPath of skeletonPaths) {
    try {
      if (!fs.existsSync(skPath)) continue;
      const content = fs.readFileSync(skPath, 'utf-8');
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

function extractNextPreview(contentMd, nextLessonTitle) {
  const nextMatch = contentMd.match(/\*\*後一篇[^*]*\*\*[：:]\s*(.+)/);
  if (nextMatch) {
    let preview = nextMatch[1].trim();
    preview = preview.replace(/^B\d{3}\s+[^—]+——\s*/, '');
    if (!preview.endsWith('……')) preview += '……';
    return `下一課預告：${preview}`;
  }
  if (nextLessonTitle) return `下一課預告：${nextLessonTitle}`;
  return '';
}

// ── 組裝 HTML ────────────────────────────────────────
function assembleHtml({
  storyId, season, title, subtitle,
  contentSections, factTable,
  kovacsTeaching, references, images, chalkboardPrompt,
  chalkboardImageBase64, chalkboardImageMime,
  templatePath, date, contentMd, nextLessonTitle,
}) {
  const icon = base.SEASON_ICONS[season];
  const dividerIcon = base.SEASON_DIVIDER_ICONS[season];
  const seasonLabel = base.SEASON_LABELS[season];

  const blockMap = {
    1: 'BLOCK-1', 2: 'BLOCK-1', 3: 'BLOCK-1', 4: 'BLOCK-1', 5: 'BLOCK-1', 6: 'BLOCK-1',
    7: 'BLOCK-2', 8: 'BLOCK-2', 9: 'BLOCK-2', 10: 'BLOCK-2', 11: 'BLOCK-2', 12: 'BLOCK-2', 13: 'BLOCK-2', 14: 'BLOCK-2',
    15: 'BLOCK-3', 16: 'BLOCK-3', 17: 'BLOCK-3', 18: 'BLOCK-3', 19: 'BLOCK-3', 20: 'BLOCK-3', 21: 'BLOCK-3', 22: 'BLOCK-3',
    23: 'BLOCK-4', 24: 'BLOCK-4', 25: 'BLOCK-4', 26: 'BLOCK-4', 27: 'BLOCK-4', 28: 'BLOCK-4', 29: 'BLOCK-4', 30: 'BLOCK-4',
  };
  const lessonNum = parseInt(storyId.replace('B', ''), 10);
  const blockLabel = blockMap[lessonNum] || '';

  const template = fs.readFileSync(templatePath, 'utf-8');
  const headMatch = template.match(/<head>([\s\S]+?)<\/head>/);
  const headContent = (headMatch ? headMatch[1] : '').replace('{{TITLE}}', `${title} — 五年級植物學`);

  // Render shared fragments
  const storyParagraphs = base.renderStoryParagraphs(contentSections);
  const factTableHtml = base.renderFactTableHtml(factTable);
  const kovacsTeachingHtml = base.mdParagraphsToHtml(kovacsTeaching.teachingInsight);
  const taiwanFunFactHtml = kovacsTeaching.taiwanFunFact ? base.mdParagraphsToHtml(kovacsTeaching.taiwanFunFact) : '';
  const scienceDialogueHtml = kovacsTeaching.scienceDialogue ? base.mdParagraphsToHtml(kovacsTeaching.scienceDialogue) : '';
  const referencesHtml = base.renderReferencesHtml(references);
  const imageListHtml = base.renderImagesHtml(images);
  const { imgTag: chalkboardImgTag, promptHtml, iterHtml } = base.renderChalkboardSection(chalkboardPrompt, chalkboardImageBase64, chalkboardImageMime, storyId);
  const storyBreak = base.renderStoryBreak();
  const sectionDivider = base.renderSectionDivider(dividerIcon);
  const pullQuote = base.extractPullQuote(contentMd || '', contentSections, '植物是大地的語言——每一片葉子都藏著生命的智慧。');

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
      <h1 class="font-headline text-3xl tracking-wide leading-relaxed text-[var(--primary)]">五年級植物學</h1>
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
  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">當代科學對話</h3>
    <div class="space-y-3">
      ${scienceDialogueHtml}
    </div>
  </section>` : ''}

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
    <p class="text-[15px] leading-[1.5] mt-3 text-[var(--on-surface-variant)] italic">使用原則：課程講述時不出示圖像 → 結束後再展示 → 黑板畫優先於投影</p>
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

  ${sectionDivider}

  <section class="mb-6">
    <h3 class="font-headline text-xl text-[var(--primary)] mb-3 border-b border-[var(--outline-variant)]/30 pb-1.5">參考來源</h3>
    <div class="space-y-2">
      ${referencesHtml}
    </div>
  </section>

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
  const opts = base.parseCLIArgs('assemble-botany.js');
  const resolvedDir = path.resolve(opts.storyDir);
  if (!fs.existsSync(resolvedDir)) {
    console.error(`Error: Lesson directory not found: ${resolvedDir}`);
    process.exit(1);
  }

  const storyId = path.basename(resolvedDir);
  console.log(`[assemble] Lesson: ${storyId}`);
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

  const { imagePath, imageBase64: chalkboardImageBase64, imageMime: chalkboardImageMime } =
    base.findChalkboardImage(storyId, opts.downloadsDir, chalkboardPrompt, 'Botany-');

  checklist['chalkboard-image'] = !!imagePath;
  if (imagePath) {
    // Validate image size (botany-specific: min 50KB)
    const sizeKB = chalkboardImageBase64.length * 0.75 / 1024;
    if (sizeKB < 50) {
      console.error(`[assemble] [FAIL] Chalkboard image too small: ${sizeKB.toFixed(0)} KB (min 50KB)`);
      checklist['chalkboard-image'] = false;
    }
  }

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
  const kovacsTeachingMd = base.stripFrontmatter(fs.readFileSync(path.join(resolvedDir, `${storyId}-kovacs-teaching.md`), 'utf-8'));
  const imagesMd = base.stripFrontmatter(fs.readFileSync(path.join(resolvedDir, `${storyId}-images.md`), 'utf-8'));
  const referencesMd = fs.readFileSync(path.join(resolvedDir, `${storyId}-references.md`), 'utf-8');
  const rawMaterialsMd = checklist[`${storyId}-raw-materials.md`]
    ? fs.readFileSync(path.join(resolvedDir, `${storyId}-raw-materials.md`), 'utf-8') : '';

  const title = extractTitle(contentMd);
  const meta = base.extractFrontmatter(contentMd);
  const subtitle = meta['子主題'] || meta['區塊'] || '';
  const contentSections = base.extractContentSections(contentMd);
  const sourceUrls = rawMaterialsMd ? base.parseSourceUrls(rawMaterialsMd) : {};
  const factTable = base.parseFactTable(contentMd, sourceUrls);
  const kovacsTeaching = parseKovacsTeaching(kovacsTeachingMd);
  const references = base.parseReferences(referencesMd);
  const images = base.parseImages(imagesMd);
  const nextLessonTitle = getNextLessonTitle(storyId);

  const templatePath = path.resolve('publish/templates/waldorf-base.html');
  if (!fs.existsSync(templatePath)) {
    console.error(`Error: Template not found: ${templatePath}`);
    process.exit(1);
  }

  if (nextLessonTitle) console.log(`[assemble] Next lesson: ${nextLessonTitle}`);

  // Assemble HTML
  const finalBase64 = checklist['chalkboard-image'] ? chalkboardImageBase64 : '';
  const html = assembleHtml({
    storyId, season: opts.season, title, subtitle,
    contentSections, factTable,
    kovacsTeaching, references, images, chalkboardPrompt,
    chalkboardImageBase64: finalBase64, chalkboardImageMime,
    templatePath, date: opts.date, contentMd, nextLessonTitle,
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
  if (!finalBase64) validationErrors.push('Chalkboard image not embedded (missing or too small)');
  if (!kovacsTeaching.teachingInsight) validationErrors.push('kovacs-teaching.md has no teaching insight');
  if (references.length === 0) validationErrors.push('references.md has 0 entries');

  if (validationErrors.length > 0) {
    console.error('\n[assemble] VALIDATION FAILED — refusing to output:');
    for (const err of validationErrors) console.error(`  - ${err}`);
    process.exit(2);
  }
  console.log('[assemble] [OK] Output validation passed (all checks)');

  // Write HTML
  if (!fs.existsSync(opts.outputDir)) fs.mkdirSync(opts.outputDir, { recursive: true });
  const versionSuffix = opts.storyVersion ? `-${opts.storyVersion}` : '';
  const htmlFilename = `${storyId}${versionSuffix}-植物學完整版.html`;
  const htmlPath = path.join(opts.outputDir, htmlFilename);
  fs.writeFileSync(htmlPath, html, 'utf-8');
  console.log(`\n[assemble] HTML written: ${htmlPath}`);

  // PDF
  if (opts.doPdf) {
    const pdfFilename = `${storyId}${versionSuffix}-植物學完整版.pdf`;
    const pdfPath = path.join(opts.outputDir, pdfFilename);
    base.generatePdf(htmlPath, pdfPath);
  }

  // Upload to Google Drive
  if (opts.doUpload) {
    const folderId = opts.driveFolderOverride || DRIVE_FOLDER_ID;
    const driveTitle = title.split(/[｜|]/)[0].trim();
    const driveBaseName = `${storyId}${versionSuffix}-${driveTitle.replace(/\s+/g, '')}`;
    const filesToUpload = [{ local: htmlPath, driveName: `${driveBaseName}.html` }];
    if (opts.doPdf) {
      const pdfPath = path.join(opts.outputDir, `${storyId}${versionSuffix}-植物學完整版.pdf`);
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
  console.log(`  Lesson:   ${storyId} — ${title}`);
  console.log(`  Season:   ${opts.season}`);
  console.log(`  Sections: ${contentSections.length} content paragraphs`);
  console.log(`  Facts:    ${factTable.length} entries with ${Object.keys(sourceUrls).length} source URLs`);
  console.log(`  Kovacs:   ${kovacsTeaching.teachingInsight ? 'present' : 'missing'}`);
  console.log(`  Refs:     ${references.length} entries`);
  console.log(`  Images:   ${images.length} references`);
  console.log(`  Prompt:   ${chalkboardPrompt.englishPrompt ? 'EN+ZH' : 'none'}`);
  console.log(`  Drawing:  ${finalBase64 ? 'embedded' : 'not found'}`);
  console.log(`  HTML:     ${htmlPath}`);
  if (opts.doPdf) console.log(`  PDF:      ${path.join(opts.outputDir, storyId + versionSuffix + '-植物學完整版.pdf')}`);
  console.log(`  Script:   ${SCRIPT_PATH} v${SCRIPT_VERSION}`);
}

main();
