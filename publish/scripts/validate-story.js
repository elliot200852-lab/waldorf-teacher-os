#!/usr/bin/env node
/**
 * validate-story.js
 * TeacherOS — ancient-myths-grade5 故事驗證工具
 *
 * 用法：
 *   node validate-story.js AM006               # 簡寫（自動展開路徑）
 *   node validate-story.js /絕對/路徑/AM006    # 完整路徑
 *   node validate-story.js --all               # 批次驗證所有故事
 *
 * 驗證項目：
 *   1. 7 件套檔案存在
 *   2. content.md frontmatter 必填欄位
 *   3. 故事本文字數 + 事實出處筆數
 *   4. images.md 圖數 + 每張圖有 https:// 連結
 *   5. raw-materials.md 字數 + URL 筆數 + 中文來源數
 *   6. 交叉驗證：content.md 來源 ↔ raw-materials.md key
 *
 * 失敗等級：
 *   [FAIL] 阻擋 Step 4（進入 Gemini 組裝前必須修正）
 *   [WARN] 不阻擋但記錄（廢棄欄位等相容性問題）
 *   [INFO] 純通知
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ══════════════════════════════════════════════
// 常數：故事資料夾基底路徑
// ══════════════════════════════════════════════
const STORIES_BASE = path.join(
  __dirname,
  '../../workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories'
);

const SCHEMA_PATH = path.join(__dirname, '../config/story-schema.yaml');

// ══════════════════════════════════════════════
// 工具：解析 story-schema.yaml 中的數值
// ══════════════════════════════════════════════
function loadSchema() {
  const defaults = {
    minContentWords: 800,
    minFactRows: 5,
    minImages: 3,
    minRawWords: 900,
    minRawSources: 5,
    minChineseSources: 2,
    requiredFiles: [
      'content.md', 'waldorf-teaching.md', 'chalkboard-prompt.md',
      'images.md', 'references.md', 'raw-materials.md', 'quality-report.md'
    ],
    requiredFrontmatter: ['aliases', 'id', 'title', 'block', 'lesson', 'age_group', 'consciousness'],
    deprecatedFrontmatter: ['lesson_id', 'story_ref', 'date'],
    deprecatedImageFields: ['在故事中的角色', '用途', '展示時機', /^URL[：:]/],
    blockAllowedValues: [
      'block-1-india', 'block-2-persia', 'block-3-babylon',
      'block-4-egypt', 'island-interludes'
    ]
  };

  if (!fs.existsSync(SCHEMA_PATH)) return defaults;

  try {
    const raw = fs.readFileSync(SCHEMA_PATH, 'utf-8');

    const numMatch = (key, pattern) => {
      const m = raw.match(pattern);
      return m ? parseInt(m[1], 10) : null;
    };

    // 各 section 分段解析，避免同名 key 互相污染
    const section = (name) => {
      const m = raw.match(new RegExp(`${name}:[\\s\\S]*?(?=\\n\\S|$)`, 'm'));
      return m ? m[0] : '';
    };
    const rawSection      = section('raw_materials_md');
    const contentSection  = section('content_md');
    const imagesSection   = section('images_md');
    const waldorfSection  = section('waldorf_teaching_md');

    const v = {
      minContentWords:   numMatch('', /故事本文最低字數:\s*(\d+)/)                          || defaults.minContentWords,
      minFactRows:       numMatch('', /最低筆數:\s*(\d+)/)                                  || defaults.minFactRows,
      minImages:         numMatch('', /最少圖數:\s*(\d+)/)                                  || defaults.minImages,
      minRawWords:       (rawSection.match(/最低字數:\s*(\d+)/) || [])[1]
                           ? parseInt(rawSection.match(/最低字數:\s*(\d+)/)[1], 10)
                           : defaults.minRawWords,
      minRawSources:     numMatch('', /最少來源筆數:\s*(\d+)/)                              || defaults.minRawSources,
      minChineseSources: numMatch('', /最少中文來源:\s*(\d+)/)                              || defaults.minChineseSources,
    };

    return { ...defaults, ...v };
  } catch (e) {
    return defaults;
  }
}

// ══════════════════════════════════════════════
// 工具：解析路徑
// ══════════════════════════════════════════════
function resolveStoryDir(arg) {
  if (path.isAbsolute(arg)) return arg;
  if (/^(AM\d{3}|TW\d{2})$/.test(arg)) {
    return path.join(STORIES_BASE, arg);
  }
  return path.resolve(process.cwd(), arg);
}

// ══════════════════════════════════════════════
// 工具：計算中文字數（含標點、英文單字）
// ══════════════════════════════════════════════
function countWords(text) {
  // 中文字符各算一字；英文/數字以空白分隔算單字
  const zhCount = (text.match(/[\u4e00-\u9fff\u3400-\u4dbf]/g) || []).length;
  const enCount = (text.match(/[a-zA-Z0-9]+/g) || []).length;
  return zhCount + enCount;
}

// ══════════════════════════════════════════════
// 工具：Levenshtein 距離（用於推薦候選 key）
// ══════════════════════════════════════════════
function levenshtein(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, (_, i) => [i, ...Array(n).fill(0)]);
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = a[i-1] === b[j-1]
        ? dp[i-1][j-1]
        : 1 + Math.min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);
    }
  }
  return dp[m][n];
}

// ══════════════════════════════════════════════
// 工具：stripFrontmatter
// ══════════════════════════════════════════════
function stripFrontmatter(md) {
  if (!md.startsWith('---')) return md;
  const end = md.indexOf('\n---', 3);
  if (end < 0) return md;
  return md.slice(end + 4).trimStart();
}

function extractFrontmatter(md) {
  if (!md.startsWith('---')) return '';
  const end = md.indexOf('\n---', 3);
  if (end < 0) return '';
  return md.slice(0, end + 4);
}

// ══════════════════════════════════════════════
// CHECK 1：7 件套檔案存在
// ══════════════════════════════════════════════
function checkFiles(storyDir, schema) {
  const results = [];
  const missing = [];
  const storyId = path.basename(storyDir);
  for (const f of schema.requiredFiles) {
    if (!fs.existsSync(path.join(storyDir, f)) && !fs.existsSync(path.join(storyDir, `${storyId}-${f}`))) missing.push(f);
  }
  if (missing.length === 0) {
    results.push({ level: 'PASS', msg: `7 件套：全部存在` });
  } else {
    results.push({ level: 'FAIL', msg: `7 件套：缺少 ${missing.join(', ')}` });
  }
  return results;
}

// ══════════════════════════════════════════════
// CHECK 2：content.md frontmatter 必填欄位
// ══════════════════════════════════════════════
function checkFrontmatter(contentMd, schema) {
  const results = [];
  const fm = extractFrontmatter(contentMd);
  if (!fm) {
    results.push({ level: 'FAIL', msg: 'content.md frontmatter：缺少 YAML frontmatter（--- 區塊）' });
    return results;
  }

  const missing = [];
  for (const field of schema.requiredFrontmatter) {
    if (!new RegExp(`^${field}:\\s*`, 'm').test(fm)) {
      missing.push(field);
    }
  }

  const deprecated = [];
  for (const field of schema.deprecatedFrontmatter) {
    if (new RegExp(`^${field}:\\s*`, 'm').test(fm)) {
      deprecated.push(field);
    }
  }

  if (missing.length === 0) {
    results.push({ level: 'PASS', msg: `content.md frontmatter：${schema.requiredFrontmatter.length}/${schema.requiredFrontmatter.length} 必填欄位存在` });
  } else {
    results.push({ level: 'FAIL', msg: `content.md frontmatter：缺少必填欄位 ${missing.join(', ')}` });
  }

  for (const d of deprecated) {
    results.push({ level: 'WARN', msg: `content.md：發現廢棄欄位「${d}」，請改為 ${d === 'lesson_id' ? 'id' : '對應新欄位'}` });
  }

  // 驗證 id 格式
  const idMatch = fm.match(/^id:\s*(.+)/m);
  if (idMatch) {
    const id = idMatch[1].trim().replace(/['"]/g, '');
    if (!/^(AM\d{3}|TW\d{2})$/.test(id)) {
      results.push({ level: 'WARN', msg: `content.md：id 格式不符（「${id}」應為 AM001-AM021 或 TW01-TW04）` });
    }
  }

  // 驗證 block 允許值
  const blockMatch = fm.match(/^block:\s*(.+)/m);
  if (blockMatch) {
    const block = blockMatch[1].trim().replace(/['"]/g, '');
    if (!schema.blockAllowedValues.includes(block)) {
      results.push({ level: 'WARN', msg: `content.md：block 值「${block}」不在允許清單中` });
    }
  }

  return results;
}

// ══════════════════════════════════════════════
// CHECK 3：故事本文字數 + 事實出處筆數
// ══════════════════════════════════════════════
function checkContentBody(contentMd, schema) {
  const results = [];
  const body = stripFrontmatter(contentMd);

  // 故事本文
  const storyMatch = body.match(/##\s*故事本文\s*\n([\s\S]*?)(?=\n##|\s*$)/);
  if (!storyMatch) {
    results.push({ level: 'FAIL', msg: 'content.md：缺少「## 故事本文」章節' });
  } else {
    const wc = countWords(storyMatch[1]);
    if (wc >= schema.minContentWords) {
      results.push({ level: 'PASS', msg: `故事本文：${wc.toLocaleString()} 字（>${schema.minContentWords}）` });
    } else {
      results.push({ level: 'FAIL', msg: `故事本文：${wc.toLocaleString()} 字（需要 >${schema.minContentWords}）` });
    }
  }

  // 事實出處
  const factMatch = body.match(/##\s*事實出處\s*\n([\s\S]*?)(?=\n##|\s*$)/);
  if (!factMatch) {
    results.push({ level: 'FAIL', msg: 'content.md：缺少「## 事實出處」章節' });
  } else {
    // 計算表格資料行（排除 header 和分隔線）
    const tableRows = factMatch[1]
      .split('\n')
      .filter(l => l.startsWith('|') && !l.match(/^[\s|:-]+$/))
      .filter(l => !l.match(/^\|\s*(事實|fact)\s*\|/i)); // 排除表頭
    const rowCount = tableRows.length;
    if (rowCount >= schema.minFactRows) {
      results.push({ level: 'PASS', msg: `事實出處：${rowCount} 筆（≥${schema.minFactRows}）` });
    } else {
      results.push({ level: 'FAIL', msg: `事實出處：${rowCount} 筆（需要 ≥${schema.minFactRows}）` });
    }
  }

  return results;
}

// ══════════════════════════════════════════════
// CHECK 4：images.md 圖數 + 連結欄位
// ══════════════════════════════════════════════
function checkImages(imagesMd, schema) {
  const results = [];

  // 切分圖像區塊（以 ### 開頭）
  const blocks = imagesMd.split(/\n(?=###\s)/);
  const imageBlocks = blocks.filter(b => /^###\s/.test(b.trim()));

  if (imageBlocks.length < schema.minImages) {
    results.push({ level: 'FAIL', msg: `images.md：只有 ${imageBlocks.length} 張圖（需要 ≥${schema.minImages}）` });
  }

  let allHaveLinks = true;
  let totalImages = imageBlocks.length;

  for (let i = 0; i < imageBlocks.length; i++) {
    const block = imageBlocks[i];
    const titleLine = block.match(/^###\s+(.+)/);
    const label = titleLine ? titleLine[1].trim() : `圖 ${i + 1}`;

    // 驗證連結欄位
    const hasLink = /[-*]\s*連結[：:]\s*https?:\/\//.test(block);
    if (!hasLink) {
      allHaveLinks = false;
      // 檢查是否有廢棄的 URL 欄位
      const hasDeprecatedUrl = /[-*]\s*URL[：:]\s*https?:\/\//.test(block);
      if (hasDeprecatedUrl) {
        results.push({ level: 'FAIL', msg: `images.md：「${label}」使用廢棄欄位「URL：」，請改為「連結：」` });
      } else {
        results.push({ level: 'FAIL', msg: `images.md：「${label}」缺少「連結：https://」欄位` });
      }
    }

    // 檢查廢棄欄位（WARN）
    const deprecatedFields = [
      ['在故事中的角色', '說明'],
      ['用途', '說明'],
      ['展示時機', '建議使用時機'],
    ];
    for (const [old, newField] of deprecatedFields) {
      if (new RegExp(`[-*]\\s*${old}[：:]`).test(block)) {
        results.push({ level: 'WARN', msg: `images.md：「${label}」使用廢棄欄位「${old}：」，應改為「${newField}：」` });
      }
    }
  }

  if (imageBlocks.length >= schema.minImages && allHaveLinks) {
    results.push({ level: 'PASS', msg: `images.md：${totalImages} 張圖，全部有 https:// 連結` });
  }

  return results;
}

// ══════════════════════════════════════════════
// CHECK 5：raw-materials.md 字數 + URL 筆數 + 中文來源
// ══════════════════════════════════════════════
function checkRawMaterials(rawMd, schema) {
  const results = [];

  const wc = countWords(rawMd);
  if (wc >= schema.minRawWords) {
    results.push({ level: 'PASS', msg: `raw-materials.md：${wc.toLocaleString()} 字（>${schema.minRawWords}）` });
  } else {
    results.push({ level: 'FAIL', msg: `raw-materials.md：${wc.toLocaleString()} 字（需要 >${schema.minRawWords}）` });
  }

  // 計算 URL: 筆數
  const urlLines = (rawMd.match(/^\s+URL:\s*https?:\/\//gm) || []);
  const urlCount = urlLines.length;
  if (urlCount >= schema.minRawSources) {
    results.push({ level: 'PASS', msg: `raw-materials.md：${urlCount} 筆 URL（≥${schema.minRawSources}）` });
  } else {
    results.push({ level: 'FAIL', msg: `raw-materials.md：${urlCount} 筆 URL（需要 ≥${schema.minRawSources}）` });
  }

  // 計算中文來源（[中] 標記）
  const cnLines = (rawMd.match(/\[中\]/g) || []);
  const cnCount = cnLines.length;
  if (cnCount >= schema.minChineseSources) {
    results.push({ level: 'PASS', msg: `raw-materials.md：${cnCount} 筆中文來源（≥${schema.minChineseSources}）` });
  } else {
    results.push({ level: 'FAIL', msg: `raw-materials.md：${cnCount} 筆中文來源（需要 ≥${schema.minChineseSources}，請加 [中] 標記）` });
  }

  return results;
}

// ══════════════════════════════════════════════
// 解析 raw-materials.md 的 key set
// ══════════════════════════════════════════════
function parseRawMaterialsKeys(rawMd) {
  const keys = [];
  const regex = /^\d+\.\s+\*\*(.+?)\*\*/gm;
  let m;
  while ((m = regex.exec(rawMd)) !== null) {
    keys.push(m[1].trim());
  }
  return keys;
}

// ══════════════════════════════════════════════
// 解析 content.md 事實出處表的「來源」欄
// ══════════════════════════════════════════════
function parseFactTableSources(contentMd) {
  const body = stripFrontmatter(contentMd);
  const factMatch = body.match(/##\s*事實出處\s*\n([\s\S]*?)(?=\n##|\s*$)/);
  if (!factMatch) return [];

  const sources = [];
  const rows = factMatch[1]
    .split('\n')
    .filter(l => l.startsWith('|') && !l.match(/^[\s|:-]+$/) && !l.match(/^\|\s*(事實|fact)\s*\|/i));

  for (const row of rows) {
    const cells = row.split('|').map(c => c.trim()).filter(Boolean);
    if (cells.length >= 2) {
      const sourceCel = cells[1];
      // 以全形或半形分號拆分多來源
      const parts = sourceCel.split(/[；;]/).map(s => s.trim()).filter(Boolean);
      sources.push(...parts);
    }
  }
  return sources;
}

// ══════════════════════════════════════════════
// CHECK 6：交叉驗證
// ══════════════════════════════════════════════
function checkCrossRef(contentMd, rawMd) {
  const results = [];

  const keys = parseRawMaterialsKeys(rawMd);
  if (keys.length === 0) {
    results.push({ level: 'WARN', msg: '交叉驗證：raw-materials.md 無法解析任何 key（格式是否符合規範？）' });
    return results;
  }

  const sources = parseFactTableSources(contentMd);
  if (sources.length === 0) {
    results.push({ level: 'WARN', msg: '交叉驗證：content.md 事實出處表無法解析任何來源欄' });
    return results;
  }

  const failed = [];
  const passed = [];
  const skipped = [];

  for (const src of sources) {
    // 豁免：書本引用（含 *斜體書名* 格式）
    if (/\*.+\*/.test(src)) {
      skipped.push(src);
      continue;
    }

    // A. 精確比對
    if (keys.includes(src)) { passed.push(src); continue; }

    // B. 單向包含（key 包含 src，且 src 足夠長）
    if (src.length >= 6 && keys.some(k => k.includes(src))) { passed.push(src); continue; }

    // C. src 包含 key（key 是 src 的子字串）
    if (keys.some(k => k.length >= 6 && src.includes(k))) { passed.push(src); continue; }

    // D. em dash 兩側分段比對
    if (src.includes('—') || src.includes('--')) {
      const parts = src.split(/—|--/).map(p => p.trim()).filter(p => p.length >= 3);
      const allPartsFound = parts.length > 0 && parts.every(p => keys.some(k => k.includes(p)));
      if (allPartsFound) { passed.push(src); continue; }
    }

    failed.push(src);
  }

  if (failed.length === 0) {
    const total = passed.length + skipped.length;
    const skipNote = skipped.length > 0 ? `（${skipped.length} 筆書本引用豁免）` : '';
    results.push({ level: 'PASS', msg: `交叉驗證：${passed.length}/${total} 來源 key 匹配${skipNote}` });
  } else {
    for (const src of failed) {
      // 推薦候選（Levenshtein 距離 ≤ 15，取最近的 3 個）
      const candidates = keys
        .map(k => ({ k, d: levenshtein(src, k) }))
        .sort((a, b) => a.d - b.d)
        .slice(0, 2)
        .filter(c => c.d <= Math.max(15, src.length * 0.5));

      let msg = `交叉驗證：來源「${src}」在 raw-materials.md 無對應 key`;
      if (candidates.length > 0) {
        msg += `\n         候選推薦：「${candidates.map(c => c.k).join('」或「')}」？`;
      }
      results.push({ level: 'FAIL', msg });
    }
  }

  if (skipped.length > 0) {
    results.push({ level: 'INFO', msg: `交叉驗證：${skipped.length} 筆書本引用跳過（${skipped.map(s => `「${s}」`).join('、')}）` });
  }

  return results;
}

// ══════════════════════════════════════════════
// 主驗證函數：驗證單個故事
// ══════════════════════════════════════════════
function validateStory(storyDir, schema) {
  const storyId = path.basename(storyDir);

  // 讀取檔案（支援 ID- 前綴命名慣例，如 AM011-content.md）
  const read = (f) => {
    const p = path.join(storyDir, f);
    if (fs.existsSync(p)) return fs.readFileSync(p, 'utf-8');
    const prefixed = path.join(storyDir, `${storyId}-${f}`);
    if (fs.existsSync(prefixed)) return fs.readFileSync(prefixed, 'utf-8');
    return null;
  };

  const contentMd    = read('content.md');
  const imagesMd     = read('images.md');
  const rawMd        = read('raw-materials.md');

  // 從 content.md 取得標題
  let title = storyId;
  if (contentMd) {
    const titleMatch = contentMd.match(/^title:\s*"?([^"\n]+)"?/m);
    if (titleMatch) title = `${storyId} ${titleMatch[1].trim()}`;
  }

  const allResults = [];

  // CHECK 1: 檔案存在
  allResults.push(...checkFiles(storyDir, schema));

  // CHECK 2: frontmatter
  if (contentMd) allResults.push(...checkFrontmatter(contentMd, schema));
  else allResults.push({ level: 'FAIL', msg: 'content.md frontmatter：檔案不存在，略過' });

  // CHECK 3: 正文字數 + 事實出處
  if (contentMd) allResults.push(...checkContentBody(contentMd, schema));
  else allResults.push({ level: 'FAIL', msg: '故事本文 / 事實出處：content.md 不存在，略過' });

  // CHECK 4: images.md
  if (imagesMd) allResults.push(...checkImages(imagesMd, schema));
  else allResults.push({ level: 'FAIL', msg: 'images.md：檔案不存在，略過' });

  // CHECK 5: raw-materials.md
  if (rawMd) allResults.push(...checkRawMaterials(rawMd, schema));
  else allResults.push({ level: 'FAIL', msg: 'raw-materials.md：檔案不存在，略過' });

  // CHECK 6: 交叉驗證
  if (contentMd && rawMd) allResults.push(...checkCrossRef(contentMd, rawMd));
  else allResults.push({ level: 'WARN', msg: '交叉驗證：content.md 或 raw-materials.md 不存在，略過' });

  // 統計
  const fails = allResults.filter(r => r.level === 'FAIL').length;
  const warns = allResults.filter(r => r.level === 'WARN').length;
  const passes = allResults.filter(r => r.level === 'PASS').length;
  const total = passes + fails;  // INFO 不算入

  return { storyId, title, results: allResults, fails, warns, passes, total };
}

// ══════════════════════════════════════════════
// 報告輸出
// ══════════════════════════════════════════════
function printReport(validation) {
  const { title, results, fails, warns, passes, total } = validation;
  const sep = '═'.repeat(50);
  const thin = '─'.repeat(50);

  console.log(`\n${sep}`);
  console.log(`validate-story.js — ${title}`);
  console.log(sep);

  for (const r of results) {
    const prefix = { PASS: '✓', FAIL: '✗', WARN: '⚑', INFO: 'ℹ' }[r.level] || '?';
    const color = { PASS: '\x1b[32m', FAIL: '\x1b[31m', WARN: '\x1b[33m', INFO: '\x1b[36m' }[r.level] || '';
    const reset = '\x1b[0m';
    const lines = r.msg.split('\n');
    console.log(`${color}[${r.level}]${reset} ${prefix} ${lines[0]}`);
    for (let i = 1; i < lines.length; i++) {
      console.log(`         ${lines[i]}`);
    }
  }

  console.log(thin);
  const status = fails === 0 ? '\x1b[32mPASS\x1b[0m' : '\x1b[31mFAIL\x1b[0m';
  const warnNote = warns > 0 ? `，${warns} 個 WARN` : '';
  console.log(`結果：${status}（${passes}/${total} 通過${warnNote}）`);
  console.log(`${sep}\n`);
}

// ══════════════════════════════════════════════
// 批次模式：--all
// ══════════════════════════════════════════════
function runAll(schema) {
  if (!fs.existsSync(STORIES_BASE)) {
    console.error(`錯誤：找不到 stories 目錄 ${STORIES_BASE}`);
    process.exit(1);
  }

  const dirs = fs.readdirSync(STORIES_BASE)
    .filter(d => /^(AM\d{3}|TW\d{2})$/.test(d))
    .sort();

  if (dirs.length === 0) {
    console.log('找不到任何故事資料夾（AM001-AM021 或 TW01-TW04）');
    return;
  }

  const summaryRows = [];
  let totalFails = 0;

  for (const d of dirs) {
    const storyDir = path.join(STORIES_BASE, d);
    const v = validateStory(storyDir, schema);
    printReport(v);
    summaryRows.push(v);
    totalFails += v.fails;
  }

  // 總結表
  console.log('\n' + '═'.repeat(60));
  console.log('批次驗證總結');
  console.log('─'.repeat(60));
  for (const v of summaryRows) {
    const status = v.fails === 0 ? '\x1b[32mPASS\x1b[0m' : '\x1b[31mFAIL\x1b[0m';
    const warnNote = v.warns > 0 ? ` (${v.warns}W)` : '';
    console.log(`  ${v.storyId.padEnd(8)} ${status}${warnNote}`);
  }
  console.log('─'.repeat(60));
  if (totalFails === 0) {
    console.log('\x1b[32m所有故事驗證通過\x1b[0m');
  } else {
    console.log(`\x1b[31m${summaryRows.filter(v => v.fails > 0).length} 個故事有 FAIL 需修正\x1b[0m`);
  }
  console.log('═'.repeat(60) + '\n');

  process.exit(totalFails > 0 ? 1 : 0);
}

// ══════════════════════════════════════════════
// 入口
// ══════════════════════════════════════════════
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('用法：');
    console.log('  node validate-story.js AM006        # 驗證單個故事（簡寫）');
    console.log('  node validate-story.js /path/AM006  # 驗證單個故事（完整路徑）');
    console.log('  node validate-story.js --all        # 批次驗證所有故事');
    process.exit(0);
  }

  const schema = loadSchema();

  if (args[0] === '--all') {
    runAll(schema);
    return;
  }

  const storyDir = resolveStoryDir(args[0]);

  if (!fs.existsSync(storyDir)) {
    console.error(`錯誤：找不到故事目錄 ${storyDir}`);
    process.exit(1);
  }

  const v = validateStory(storyDir, schema);
  printReport(v);

  process.exit(v.fails > 0 ? 1 : 0);
}

main();
