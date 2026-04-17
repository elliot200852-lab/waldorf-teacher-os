#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — 圖片壓縮工具
// 路徑：publish/scripts/compress-image.js
// 用途：黑板畫圖片在 base64 內嵌前先壓縮，減少 HTML/PDF 體積
// 跨平台：macOS (sips 內建) → ImageMagick magick/convert → 跳過
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 模組用法（assemble-base.js 內部呼叫）：
//   const { compressImage } = require('./compress-image');
//   const compressed = compressImage('/path/to/image.png');
//   // 回傳壓縮後路徑（string），或 null（失敗時改用原始路徑）
//
// CLI 用法（獨立執行測試）：
//   node compress-image.js <input-path>
//   node compress-image.js <input-path> --output=temp/compressed
//   node compress-image.js <input-path> --quality=82 --max-px=1600
//   node compress-image.js --detect    （只偵測可用的壓縮器，不壓縮）
//
// 壓縮策略：
//   1. sips（macOS 系統內建，無需安裝）
//   2. magick（ImageMagick v7+，Windows/macOS/Linux）
//   3. convert（ImageMagick v6，Linux/macOS）
//   4. 以上皆無 → 跳過壓縮，輸出警告，組裝流程繼續
//
// 輸出：
//   - 壓縮後 JPEG，放入 temp/compressed/（預設）
//   - 檔名：<原始basename>-compressed.jpg
//   - 日誌：原始大小、壓縮後大小、縮減比例、使用的壓縮器
//
// 版本：1.0.0 (2026-03-30)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const DEFAULT_QUALITY = 80;
const DEFAULT_MAX_PX = 1400;
const DEFAULT_OUTPUT_SUBDIR = 'temp/compressed';

// ── 壓縮器偵測 ────────────────────────────────────────
// 回傳：'sips+cwebp' | 'sips' | 'magick' | 'convert' | null
function detectCompressor() {
  const isWin = process.platform === 'win32';
  const whichCmd = isWin ? 'where' : 'which';

  // 1. sips + cwebp（macOS 最佳組合：sips 負責 resize，cwebp 負責 WebP 壓縮）
  if (process.platform === 'darwin') {
    const sipsOk = spawnSync(whichCmd, ['sips'], { encoding: 'utf-8', timeout: 3000 });
    const cwebpOk = spawnSync(whichCmd, ['cwebp'], { encoding: 'utf-8', timeout: 3000 });
    if (sipsOk.status === 0 && cwebpOk.status === 0) return 'sips+cwebp';
    // sips alone (JPEG fallback, 沒有 cwebp 時)
    if (sipsOk.status === 0) return 'sips';
  }

  // 2. ImageMagick v7（magick 指令）
  {
    const r = spawnSync(whichCmd, ['magick'], { encoding: 'utf-8', timeout: 3000 });
    if (r.status === 0 && r.stdout.trim()) return 'magick';
  }

  // 3. ImageMagick v6（convert 指令）
  {
    const r = spawnSync(whichCmd, ['convert'], { encoding: 'utf-8', timeout: 3000 });
    if (r.status === 0 && r.stdout.trim()) return 'convert';
  }

  return null;
}

// ── 主要壓縮函式（同步）─────────────────────────────────
/**
 * 將圖片壓縮為 JPEG 並儲存到輸出目錄。
 *
 * @param {string} inputPath  - 原始圖片的絕對或相對路徑
 * @param {string|null} outputDir - 壓縮檔輸出目錄（null = temp/compressed/）
 * @param {number} quality    - JPEG 品質 0–100（預設 82）
 * @param {number} maxPx      - 長邊最大像素，超過才縮放（預設 1600）
 * @returns {string|null}     - 壓縮後檔案路徑，或 null（失敗 → 呼叫端改用原始路徑）
 */
function compressImage(inputPath, outputDir = null, quality = DEFAULT_QUALITY, maxPx = DEFAULT_MAX_PX) {
  // ── 前置驗證 ──
  if (!inputPath) {
    console.warn('[compress] No input path provided. Skipping.');
    return null;
  }
  const resolvedInput = path.resolve(inputPath);
  if (!fs.existsSync(resolvedInput)) {
    console.warn(`[compress] Input not found: ${resolvedInput}`);
    return null;
  }

  const compressor = detectCompressor();
  if (!compressor) {
    console.warn('[compress] No compressor available (sips / ImageMagick). Skipping compression.');
    console.warn('[compress] Install ImageMagick to enable: brew install imagemagick (macOS) or choco install imagemagick (Windows)');
    return null;
  }

  // ── 準備輸出路徑 ──
  const resolvedOutputDir = outputDir
    ? path.resolve(outputDir)
    : path.resolve(process.cwd(), DEFAULT_OUTPUT_SUBDIR);

  if (!fs.existsSync(resolvedOutputDir)) {
    fs.mkdirSync(resolvedOutputDir, { recursive: true });
  }

  const basename = path.basename(resolvedInput, path.extname(resolvedInput));
  // 格式優先順序（依環境自動選擇）：
  //   sips（macOS）：avif > jpeg   ← sips 不能寫 webp，但 avif 更小
  //   ImageMagick  ：webp > jpeg   ← IM 寫 webp 需要 libwebp
  const outputPathAvif = path.join(resolvedOutputDir, `${basename}-compressed.avif`);
  const outputPathWebp = path.join(resolvedOutputDir, `${basename}-compressed.webp`);
  const outputPathJpeg = path.join(resolvedOutputDir, `${basename}-compressed.jpg`);

  const originalSizeKB = fs.statSync(resolvedInput).size / 1024;
  console.log(`[compress] Input:  ${path.basename(resolvedInput)} (${originalSizeKB.toFixed(0)} KB)`);

  // ── 執行壓縮（格式優先選最佳，失敗退 JPEG）──
  let success = false;
  let stderr = '';
  let outputPath = outputPathJpeg; // default, overridden below

  if (compressor === 'sips+cwebp') {
    // macOS 最佳路徑：sips resize PNG → cwebp 壓 WebP
    // sips 負責 resize（不轉格式），cwebp 負責 WebP 編碼
    console.log(`[compress] Config: quality=${quality}, max=${maxPx}px, engine=sips+cwebp, format=webp`);
    const tempPng = path.join(resolvedOutputDir, `${basename}-resized.png`);
    // Step 1: sips resize（輸出 PNG 保持無損）
    const r1 = spawnSync('sips', [
      '-s', 'format', 'png',
      '-Z', String(maxPx),
      resolvedInput,
      '--out', tempPng,
    ], { encoding: 'utf-8', timeout: 30000 });
    if (r1.status !== 0) {
      console.warn('[compress] sips resize failed: ' + (r1.stderr || ''));
    } else {
      // Step 2: cwebp 壓縮
      const r2 = spawnSync('cwebp', [
        '-q', String(quality),
        tempPng,
        '-o', outputPathWebp,
      ], { encoding: 'utf-8', timeout: 30000 });
      success = r2.status === 0 && fs.existsSync(outputPathWebp);
      outputPath = outputPathWebp;
      stderr = r2.stderr || '';
    }
    // 清除中間 PNG
    try { fs.unlinkSync(tempPng); } catch {}

    if (!success) {
      // fallback: sips → JPEG
      console.warn('[compress] sips+cwebp failed, falling back to JPEG...');
      const r3 = spawnSync('sips', [
        '-s', 'format', 'jpeg',
        '-s', 'formatOptions', String(quality),
        '-Z', String(maxPx),
        resolvedInput,
        '--out', outputPathJpeg,
      ], { encoding: 'utf-8', timeout: 30000 });
      success = r3.status === 0 && fs.existsSync(outputPathJpeg);
      outputPath = outputPathJpeg;
      if (success) console.log('[compress] [fallback→jpeg] OK');
    }

  } else if (compressor === 'sips') {
    // sips alone（沒有 cwebp 時）→ JPEG
    console.log(`[compress] Config: quality=${quality}, max=${maxPx}px, engine=sips, format=jpeg`);
    const r = spawnSync('sips', [
      '-s', 'format', 'jpeg',
      '-s', 'formatOptions', String(quality),
      '-Z', String(maxPx),
      resolvedInput,
      '--out', outputPathJpeg,
    ], { encoding: 'utf-8', timeout: 30000 });
    success = r.status === 0 && fs.existsSync(outputPathJpeg);
    outputPath = outputPathJpeg;
    stderr = r.stderr || '';

  } else if (compressor === 'magick') {
    // ImageMagick v7 主格式：WebP（需 libwebp）
    console.log(`[compress] Config: quality=${quality}, max=${maxPx}px, engine=magick, format=webp`);
    const r = spawnSync('magick', [
      resolvedInput,
      '-resize', `${maxPx}x${maxPx}>`,
      '-quality', String(quality),
      outputPathWebp,
    ], { encoding: 'utf-8', timeout: 30000 });
    success = r.status === 0 && fs.existsSync(outputPathWebp);
    outputPath = outputPathWebp;
    stderr = r.stderr || '';

    if (!success) {
      console.warn('[compress] magick WebP failed (libwebp missing?), falling back to JPEG...');
      const r2 = spawnSync('magick', [
        resolvedInput,
        '-resize', `${maxPx}x${maxPx}>`,
        '-quality', String(quality),
        outputPathJpeg,
      ], { encoding: 'utf-8', timeout: 30000 });
      success = r2.status === 0 && fs.existsSync(outputPathJpeg);
      outputPath = outputPathJpeg;
      if (success) console.log('[compress] [fallback→jpeg] OK');
    }

  } else if (compressor === 'convert') {
    // ImageMagick v6 主格式：WebP（需 libwebp）
    console.log(`[compress] Config: quality=${quality}, max=${maxPx}px, engine=convert, format=webp`);
    const r = spawnSync('convert', [
      resolvedInput,
      '-resize', `${maxPx}x${maxPx}>`,
      '-quality', String(quality),
      outputPathWebp,
    ], { encoding: 'utf-8', timeout: 30000 });
    success = r.status === 0 && fs.existsSync(outputPathWebp);
    outputPath = outputPathWebp;
    stderr = r.stderr || '';

    if (!success) {
      console.warn('[compress] convert WebP failed, falling back to JPEG...');
      const r2 = spawnSync('convert', [
        resolvedInput,
        '-resize', `${maxPx}x${maxPx}>`,
        '-quality', String(quality),
        outputPathJpeg,
      ], { encoding: 'utf-8', timeout: 30000 });
      success = r2.status === 0 && fs.existsSync(outputPathJpeg);
      outputPath = outputPathJpeg;
      if (success) console.log('[compress] [fallback→jpeg] OK');
    }
  }

  // ── 回報結果 ──
  if (success) {
    const compressedSizeKB = fs.statSync(outputPath).size / 1024;
    // 若壓縮後反而增大（例如已是最佳化的小圖），就改用原始檔
    if (compressedSizeKB >= originalSizeKB) {
      console.warn(`[compress] Compressed (${compressedSizeKB.toFixed(0)} KB) >= original (${originalSizeKB.toFixed(0)} KB). Using original.`);
      try { fs.unlinkSync(outputPath); } catch {}
      return null;
    }
    const reduction = ((1 - compressedSizeKB / originalSizeKB) * 100).toFixed(0);
    console.log(`[compress] [OK]   ${path.basename(outputPath)} (${compressedSizeKB.toFixed(0)} KB, ${reduction}% smaller)`);
    return outputPath;
  } else {
    if (stderr.trim()) console.warn(`[compress] ${compressor} stderr: ${stderr.trim()}`);
    console.warn('[compress] Compression failed. Falling back to original image.');
    return null;
  }
}

// ── 匯出（模組用法）──────────────────────────────────────
module.exports = { compressImage, detectCompressor };

// ── CLI 入口 ──────────────────────────────────────────────
if (require.main === module) {
  const args = process.argv.slice(2);

  // --detect：只偵測壓縮器
  if (args.includes('--detect')) {
    const c = detectCompressor();
    if (c) {
      console.log(`[compress] Compressor detected: ${c}`);
      process.exit(0);
    } else {
      console.warn('[compress] No compressor found.');
      process.exit(1);
    }
  }

  const inputPath = args.find(a => !a.startsWith('--'));
  if (!inputPath) {
    console.error('Usage:');
    console.error('  node compress-image.js <input-path> [--output=<dir>] [--quality=82] [--max-px=1600]');
    console.error('  node compress-image.js --detect');
    process.exit(1);
  }

  const outputArg  = args.find(a => a.startsWith('--output='));
  const qualityArg = args.find(a => a.startsWith('--quality='));
  const maxPxArg   = args.find(a => a.startsWith('--max-px='));

  const outputDir = outputArg  ? outputArg.split('=')[1]           : null;
  const quality   = qualityArg ? parseInt(qualityArg.split('=')[1], 10) : DEFAULT_QUALITY;
  const maxPx     = maxPxArg   ? parseInt(maxPxArg.split('=')[1],   10) : DEFAULT_MAX_PX;

  const result = compressImage(inputPath, outputDir, quality, maxPx);
  if (result) {
    console.log(`[compress] Output: ${result}`);
    process.exit(0);
  } else {
    console.warn('[compress] No compressed file produced (see warnings above).');
    process.exit(1);
  }
}
