#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — HTML 內嵌圖片重壓縮
// 路徑：publish/scripts/recompress-html.js
// 用途：將已上傳 Drive 的舊 HTML 中未壓縮的 base64 圖片就地壓縮
// 依賴：compress-image.js（壓縮引擎）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 用法：
//   node recompress-html.js <input.html> [--output=<path>]
//
// 邏輯：
//   1. 讀取 HTML
//   2. 正則找出所有 data:image/...;base64,... 的 <img> src
//   3. 逐一 decode → 暫存檔 → compressImage() → 新 base64 替換
//   4. 寫出壓縮後 HTML
//
// 版本：1.0.0 (2026-03-30)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

'use strict';

const fs = require('fs');
const path = require('path');
const { compressImage } = require('./compress-image');

const TEMP_DIR = path.resolve(process.cwd(), 'temp', 'recompress-work');

function recompressHtml(inputPath, outputPath) {
  if (!fs.existsSync(inputPath)) {
    console.error(`[recompress] File not found: ${inputPath}`);
    return false;
  }

  const originalSizeKB = fs.statSync(inputPath).size / 1024;
  console.log(`[recompress] Input: ${path.basename(inputPath)} (${originalSizeKB.toFixed(0)} KB)`);

  let html = fs.readFileSync(inputPath, 'utf-8');

  // 修復 {{TITLE}}：從 HTML 內容提取實際標題
  const titleMatch = html.match(/<h2[^>]*>([^<]+)<\/h2>/);
  if (titleMatch && html.includes('{{TITLE}}')) {
    const realTitle = titleMatch[1].trim();
    html = html.replace('{{TITLE}}', realTitle);
    console.log(`[recompress] Fixed <title>: "${realTitle}"`);
  }

  // 找出所有 base64 data URI（含 avif——需從 AVIF 轉回 JPEG）
  // 格式：data:image/png;base64,iVBOR...（可能非常長）
  const dataUriPattern = /data:image\/(png|jpeg|jpg|webp|gif|avif);base64,([A-Za-z0-9+/=]+)/g;

  let match;
  const replacements = [];
  let imgIndex = 0;

  while ((match = dataUriPattern.exec(html)) !== null) {
    const fullMatch = match[0];
    const mimeType = match[1];
    const base64Data = match[2];
    const rawSizeKB = base64Data.length * 0.75 / 1024;

    // 小於 50 KB 的圖片不壓（可能是 icon 或 divider）
    if (rawSizeKB < 50) {
      console.log(`[recompress]   img#${imgIndex}: ${rawSizeKB.toFixed(0)} KB (${mimeType}) — skip (< 50 KB)`);
      imgIndex++;
      continue;
    }

    console.log(`[recompress]   img#${imgIndex}: ${rawSizeKB.toFixed(0)} KB (${mimeType}) — compressing...`);

    // Decode → 暫存
    if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR, { recursive: true });
    const ext = mimeType === 'jpeg' || mimeType === 'jpg' ? '.jpg' : `.${mimeType}`;
    const tempFile = path.join(TEMP_DIR, `img-${imgIndex}${ext}`);
    fs.writeFileSync(tempFile, Buffer.from(base64Data, 'base64'));

    // 壓縮
    const compressedPath = compressImage(tempFile, TEMP_DIR);

    if (compressedPath) {
      const compressedBase64 = fs.readFileSync(compressedPath).toString('base64');
      const compressedExt = path.extname(compressedPath).toLowerCase();
      const newMime = compressedExt === '.avif' ? 'avif'
        : compressedExt === '.webp' ? 'webp'
        : compressedExt === '.jpg' || compressedExt === '.jpeg' ? 'jpeg'
        : mimeType;
      const newDataUri = `data:image/${newMime};base64,${compressedBase64}`;
      const newSizeKB = compressedBase64.length * 0.75 / 1024;
      const reduction = ((1 - newSizeKB / rawSizeKB) * 100).toFixed(0);
      console.log(`[recompress]   img#${imgIndex}: ${rawSizeKB.toFixed(0)} KB → ${newSizeKB.toFixed(0)} KB (${reduction}% smaller)`);
      replacements.push({ original: fullMatch, replacement: newDataUri });
    } else {
      console.warn(`[recompress]   img#${imgIndex}: compression failed, keeping original`);
    }

    // 清除暫存
    try { fs.unlinkSync(tempFile); } catch {}
    if (compressedPath) { try { fs.unlinkSync(compressedPath); } catch {} }

    imgIndex++;
  }

  if (replacements.length === 0) {
    console.log('[recompress] No images needed compression.');
    // 即使沒壓縮，仍拷貝到 output（保持流程一致）
    if (outputPath !== inputPath) fs.copyFileSync(inputPath, outputPath);
    return true;
  }

  // 執行替換
  for (const r of replacements) {
    html = html.replace(r.original, r.replacement);
  }

  // 寫出
  const resolvedOutput = outputPath || inputPath;
  fs.writeFileSync(resolvedOutput, html, 'utf-8');
  const newSizeKB = fs.statSync(resolvedOutput).size / 1024;
  const totalReduction = ((1 - newSizeKB / originalSizeKB) * 100).toFixed(0);
  console.log(`[recompress] [DONE] ${path.basename(resolvedOutput)}: ${originalSizeKB.toFixed(0)} KB → ${newSizeKB.toFixed(0)} KB (${totalReduction}% smaller, ${replacements.length} image(s) recompressed)`);

  return true;
}

module.exports = { recompressHtml };

// ── CLI ──
if (require.main === module) {
  const args = process.argv.slice(2);
  const inputPath = args.find(a => !a.startsWith('--'));
  const outputArg = args.find(a => a.startsWith('--output='));

  if (!inputPath) {
    console.error('Usage: node recompress-html.js <input.html> [--output=<path>]');
    process.exit(1);
  }

  const outputPath = outputArg ? outputArg.split('=')[1] : inputPath;
  const ok = recompressHtml(path.resolve(inputPath), path.resolve(outputPath));
  process.exit(ok ? 0 : 1);
}
