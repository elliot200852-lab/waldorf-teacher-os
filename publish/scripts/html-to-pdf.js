#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — HTML → PDF 轉換腳本
// 路徑：publish/scripts/html-to-pdf.js
// 用途：將美化版 HTML 轉為 A4 PDF，版面規格固定
// 依賴：puppeteer（npm install puppeteer）
// 跨平台：macOS + Windows（Node.js 環境）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 用法：
//   node publish/scripts/html-to-pdf.js <input.html> [output.pdf] [options]
//
// 選項：
//   --fit-page       自動調整間距，讓內容剛好填滿指定頁數
//   --pages=N        目標頁數（預設 1）；搭配 --fit-page 使用
//   --auto           自動模式：先自然渲染偵測頁數，再調整間距填滿（等同 --fit-page --pages=自然頁數）
//   --dry-run        不輸出 PDF，僅輸出 JSON 量測結果（供 AI 判斷）
//
// 範例：
//   node publish/scripts/html-to-pdf.js temp/beautify-學習單.html temp/學習單.pdf --fit-page
//   node publish/scripts/html-to-pdf.js temp/beautify-學習單.html --fit-page --pages=2
//   node publish/scripts/html-to-pdf.js temp/beautify-學習單.html --auto
//   node publish/scripts/html-to-pdf.js temp/beautify-學習單.html --fit-page --dry-run
//
// 版面規格（David 確認，2026-03-20）：
//   - A4（210mm × 297mm）
//   - 邊界：上下左右 10mm
//   - 背景圖形：保留
//   - 頁碼：右下角，9px 灰色
//   - 不顯示頁首（URL、日期等）
//
// --fit-page 邏輯：
//   1. 兩點校準：scale=1.0 與 scale=0.5 量測高度
//   2. 線性模型求解初始 scale
//   3. 生成測試 PDF，驗證實際頁數
//   4. 若頁數不符目標，二分搜尋微調 scale
//   5. 單頁模式：只調間距，字級不動
//   6. 多頁模式：間距 + 字級同步放大，舒適閱讀
//
// --auto 邏輯：
//   1. 先以原始 CSS 自然渲染，取得 PDF 自然頁數 N
//   2. 以 --fit-page --pages=N 填滿 N 頁
//   3. 自動完成，不需 AI 手動判斷
//
// --dry-run 輸出格式（JSON，供 AI 解析）：
//   {
//     "scale": 0.85,
//     "direction": "COMPRESS",
//     "target_pages": 1,
//     "actual_pages": 1,
//     "fill_percent": 96,
//     "squeeze_level": "comfortable",  // comfortable | tight | very_tight
//     "recommendation": "ok"           // ok | suggest_2_pages
//   }
//
// squeeze_level 判定：
//   scale >= 0.80  → comfortable（舒適）
//   scale >= 0.65  → tight（偏擠，但可接受）
//   scale <  0.65  → very_tight（建議改兩頁）
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

// ── 固定版面規格（Hook 級，不接受外部覆寫）──────────────
const PDF_OPTIONS = {
  format: 'A4',
  margin: {
    top: '10mm',
    bottom: '10mm',
    left: '10mm',
    right: '10mm',
  },
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  footerTemplate: `
    <div style="width: 100%; font-size: 9px; color: #999; padding-right: 15mm; text-align: right; font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;">
      <span class="pageNumber"></span> / <span class="totalPages"></span>
    </div>
  `,
  scale: 1,
  preferCSSPageSize: false,
};

// A4 可用高度（實測校準）
// 測試條件：format A4, margin 10mm all, displayHeaderFooter: true
// 實測分頁點：1040-1050px（div height=1040 → 1 page, 1050 → 2 pages）
// 取 1035px（留 5px 安全緩衝）
const A4_USABLE_HEIGHT_PX = 1035;

// PDF 內容區寬度（與 viewport 一致，確保量測準確）
// A4 寬度 210mm - 左右邊界各 10mm = 190mm = 718px at 96dpi
const PDF_CONTENT_WIDTH_PX = 718;

// 伸縮範圍
const MIN_SCALE = 0.5;   // 壓縮下限（再低書寫空間不夠）
const MAX_SCALE = 2.0;   // 放大上限（再大間距過於誇張）

// 擠壓門檻（供 AI 詢問教師用）
const SQUEEZE_COMFORTABLE = 0.80;  // >= 此值：舒適
const SQUEEZE_TIGHT = 0.65;        // >= 此值：偏擠但可接受；< 此值：建議兩頁

// ── 核心：注入 CSS 控制間距（與字級）─────────────────────
//
// spacingScale：控制間距（padding, margin, answer-line height）
// fontScale：控制字級（僅多頁模式啟用，預設 1.0）
//
function buildFitPageCSS(spacingScale, fontScale = 1.0) {
  const s = spacingScale;
  const f = fontScale;
  return `
    /* ── fit-page spacing=${s.toFixed(3)} font=${f.toFixed(3)} ── */

    /* ── 學習單類型（answer-line, worksheet-header）── */
    .answer-line      { min-height: calc(2.4em * ${s}) !important; }
    .answer-line-tall { min-height: calc(4.2em * ${s}) !important; }

    .worksheet-header {
      padding-top:    calc(12px * ${s}) !important;
      padding-bottom: calc(12px * ${s}) !important;
      margin-bottom:  calc(8px * ${s}) !important;
    }

    .task-card {
      padding-top:    calc(6px * ${s}) !important;
      padding-bottom: calc(6px * ${s}) !important;
      margin-bottom:  calc(5px * ${s}) !important;
    }

    .preview-table td, .preview-table th {
      padding-top:    calc(3px * ${s}) !important;
      padding-bottom: calc(3px * ${s}) !important;
    }

    /* ── 考卷/測驗類型（question, stem, options, explanation）── */
    .question {
      margin-bottom: calc(12px * ${s}) !important;
    }
    .question p.stem {
      margin-bottom: calc(3px * ${s}) !important;
      ${f !== 1.0 ? `font-size: calc(1em * ${f}) !important;` : ''}
    }
    .question .options {
      ${f !== 1.0 ? `font-size: calc(0.94em * ${f}) !important;` : ''}
    }
    .question .explanation {
      margin-top: calc(2px * ${s}) !important;
      ${f !== 1.0 ? `font-size: calc(0.88em * ${f}) !important;` : ''}
    }

    /* ── 通用結構 ── */
    section            { margin-bottom: calc(12px * ${s}) !important; }
    section p          { margin-bottom: calc(8px * ${s}) !important; }

    main {
      padding-top:    calc(16px * ${s}) !important;
      padding-bottom: calc(16px * ${s}) !important;
      ${f !== 1.0 ? `font-size: calc(1em * ${f}) !important;` : ''}
    }

    .section-label {
      margin-bottom: calc(10px * ${s}) !important;
    }

    .watercolor-wash-header {
      padding: calc(16px * ${s}) !important;
      margin-bottom: calc(8px * ${s}) !important;
    }

    .flex.justify-center {
      padding-top:    calc(4px * ${s}) !important;
      padding-bottom: calc(4px * ${s}) !important;
    }

    .hand-drawn-border {
      padding-top:    calc(8px * ${s}) !important;
      padding-bottom: calc(8px * ${s}) !important;
      margin-top:     calc(4px * ${s}) !important;
      margin-bottom:  calc(4px * ${s}) !important;
    }

    footer {
      margin-top:  calc(8px * ${s}) !important;
      padding-top: calc(4px * ${s}) !important;
    }

    .grid {
      gap:           calc(12px * ${s}) !important;
      margin-bottom: calc(12px * ${s}) !important;
    }

    .space-y-2 > * + * {
      margin-top: calc(8px * ${s}) !important;
    }

    ${f !== 1.0 ? `
    /* 多頁模式：字級同步放大 */
    section p, section li, .task-card p, .task-card li {
      font-size: calc(1em * ${f}) !important;
    }
    .answer-line, .answer-line-tall {
      font-size: calc(1em * ${f}) !important;
    }
    ` : ''}
  `;
}

// ── 主函式 ───────────────────────────────────────────
async function htmlToPdf(inputPath, outputPath, options = {}) {
  const { fitPage = false, targetPages = 1, dryRun = false, auto = false } = options;

  const absoluteInput = path.resolve(inputPath);
  const absoluteOutput = path.resolve(outputPath);

  // 前置檢查：輸入檔案存在
  if (!fs.existsSync(absoluteInput)) {
    throw new Error(`Input file not found: ${absoluteInput}`);
  }

  // 前置檢查：輸出目錄存在
  const outputDir = path.dirname(absoluteOutput);
  if (!fs.existsSync(outputDir)) {
    throw new Error(`Output directory not found: ${outputDir}`);
  }

  // 跨平台 file:// URL（正確處理中文檔名與空格）
  const fileUrl = pathToFileURL(absoluteInput).href;

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const page = await browser.newPage();
    // 視窗寬度 = PDF 內容區寬度（扣邊界後），確保量測高度與 PDF 輸出一致
    await page.setViewport({ width: PDF_CONTENT_WIDTH_PX, height: 1123 });

    await page.goto(fileUrl, {
      waitUntil: 'networkidle0',
      timeout: 30000,
    });

    await page.evaluate(() => document.fonts.ready);

    // ── PDF 分頁修正 ──────────────────────────────────
    // 問題：模板的 @media print 有 section { break-inside: avoid }，
    // 對單頁學習單有效，但故事正文 section 跨多頁時會被整個推到下一頁，
    // 導致第一頁只有標題。此處覆蓋為 break-inside: auto。
    await page.evaluate(() => {
      const fix = document.createElement('style');
      fix.id = 'pdf-flow-fix';
      fix.textContent = `
        section { break-inside: auto !important; }
        body { min-height: auto !important; }
        main { overflow: visible !important; }
      `;
      document.head.appendChild(fix);
    });

    // ── 輔助函式 ─────────────────────────────────────
    const applyScale = (spacingScale, fontScale = 1.0) => page.evaluate((css) => {
      const old = document.getElementById('fit-page-css');
      if (old) old.remove();
      const style = document.createElement('style');
      style.id = 'fit-page-css';
      style.textContent = css;
      document.head.appendChild(style);
    }, buildFitPageCSS(spacingScale, fontScale));

    const reflow = () => page.evaluate(() =>
      new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))
    );

    const getHeight = () => page.evaluate(() => {
      const main = document.querySelector('main');
      return main ? main.scrollHeight : document.body.scrollHeight;
    });

    // 計算 PDF 頁數：必須寫入暫存檔再讀取
    // （Puppeteer buffer 模式與 file 模式的 PDF 結構不同，buffer 會漏頁）
    const probePath = absoluteOutput + '.probe.pdf';
    const getPdfPageCount = async () => {
      await page.pdf({ path: probePath, ...PDF_OPTIONS });
      const buf = fs.readFileSync(probePath);
      const pdfStr = buf.toString('binary');
      const matches = pdfStr.matchAll(/\/Count\s+(\d+)/g);
      let maxCount = 1;
      for (const m of matches) {
        const n = parseInt(m[1], 10);
        if (n > maxCount) maxCount = n;
      }
      try { fs.unlinkSync(probePath); } catch (_) {}
      return maxCount;
    };

    // ── --auto：自動偵測自然頁數再填滿 ────────────────
    let effectiveFitPage = fitPage;
    let effectiveTargetPages = targetPages;

    if (auto) {
      // 自然渲染：生成完整 PDF 到暫存檔，用檔案大小與頁數驗證
      const tmpPath = absoluteOutput + '.auto-probe.pdf';
      await page.pdf({ path: tmpPath, ...PDF_OPTIONS });
      const tmpBuf = fs.readFileSync(tmpPath);
      const tmpStr = tmpBuf.toString('binary');
      const countMatches = tmpStr.matchAll(/\/Count\s+(\d+)/g);
      let naturalPages = 1;
      for (const m of countMatches) {
        const n = parseInt(m[1], 10);
        if (n > naturalPages) naturalPages = n;
      }
      fs.unlinkSync(tmpPath);
      console.log(`[auto] Natural render: ${naturalPages} page(s) (probe file: ${tmpBuf.length} bytes)`);
      effectiveFitPage = true;
      effectiveTargetPages = naturalPages;
    }

    // ── --fit-page：自動適配 ─────────────────────────
    if (effectiveFitPage) {
      const targetHeight = A4_USABLE_HEIGHT_PX * effectiveTargetPages;

      // ── 階段一：兩點校準（快速逼近）──────────────
      // 校準點 1：scale = 1.0（原始）
      const H1 = await getHeight();

      // 校準點 2：scale = 0.5
      await applyScale(0.5);
      await reflow();
      const H05 = await getHeight();

      // 線性模型求解
      const H_variable = 2 * (H1 - H05);  // 可伸縮部分的基準高度
      const H_fixed = H1 - H_variable;     // 固定部分（文字、邊框）

      console.log(`[fit-page] H_fixed=${Math.round(H_fixed)}px, H_variable=${Math.round(H_variable)}px`);
      console.log(`[fit-page] H@1.0=${H1}px, H@0.5=${H05}px, Target=${targetHeight}px (${effectiveTargetPages} page(s))`);

      let initialScale;
      if (H_variable > 0) {
        initialScale = (targetHeight - H_fixed) / H_variable;
      } else {
        initialScale = 1.0;
      }

      // 多頁模式：同步放大字級
      let fontScale = 1.0;
      if (effectiveTargetPages >= 2 && initialScale > 1.0) {
        // 字級放大比例 = 間距放大的 30%（避免過度膨脹）
        fontScale = 1.0 + (initialScale - 1.0) * 0.3;
        fontScale = Math.min(fontScale, 1.25);  // 字級最大放大 25%
      }

      // 夾在合理範圍
      const clampedScale = Math.min(Math.max(initialScale, MIN_SCALE), MAX_SCALE);

      const direction = clampedScale > 1.0 ? 'EXPAND' : clampedScale < 1.0 ? 'COMPRESS' : 'NO CHANGE';
      console.log(`[fit-page] Initial estimate: scale=${initialScale.toFixed(3)} → clamped=${clampedScale.toFixed(3)} (${direction})`);
      if (fontScale !== 1.0) {
        console.log(`[fit-page] Multi-page mode: fontScale=${fontScale.toFixed(3)}`);
      }

      // ── 階段二：實際驗證 + 二分搜尋微調 ──────────
      // 兩點校準是近似的（CSS calc 非完美線性），
      // 所以用實際 PDF 頁數做最終校驗。
      await applyScale(clampedScale, fontScale);
      await reflow();

      let actualPages = await getPdfPageCount();
      let finalScale = clampedScale;

      console.log(`[fit-page] After calibration: scale=${finalScale.toFixed(3)}, pages=${actualPages}, target=${effectiveTargetPages}`);

      if (actualPages !== effectiveTargetPages) {
        console.log(`[fit-page] Page count mismatch. Starting binary search...`);

        // 二分搜尋：找到剛好符合目標頁數的 scale
        let lo, hi;
        if (actualPages > effectiveTargetPages) {
          // 頁數太多 → 需要更小的 scale（壓縮）
          lo = MIN_SCALE;
          hi = finalScale;
        } else {
          // 頁數太少 → 需要更大的 scale（放大）
          lo = finalScale;
          hi = MAX_SCALE;
        }

        // 最多搜尋 8 次（精度 < 0.5%）
        for (let i = 0; i < 8; i++) {
          const mid = (lo + hi) / 2;
          let fScale = fontScale;
          if (effectiveTargetPages >= 2 && mid > 1.0) {
            fScale = 1.0 + (mid - 1.0) * 0.3;
            fScale = Math.min(fScale, 1.25);
          }

          await applyScale(mid, fScale);
          await reflow();
          const midPages = await getPdfPageCount();

          console.log(`[fit-page] Binary search #${i + 1}: scale=${mid.toFixed(3)}, pages=${midPages}`);

          if (midPages <= effectiveTargetPages) {
            // 頁數符合或偏少 → 可以試著放大
            lo = mid;
            finalScale = mid;
            fontScale = fScale;
          } else {
            // 頁數太多 → 需要壓縮
            hi = mid;
          }

          // 如果 lo 和 hi 已經很接近，停止搜尋
          if (hi - lo < 0.005) break;
        }

        // 套用最終結果
        await applyScale(finalScale, fontScale);
        await reflow();
        actualPages = await getPdfPageCount();
      }

      // ── 階段三：如果剛好符合目標頁數，嘗試填滿空間 ──
      // 在不超出頁數的前提下，盡量放大 scale 以填滿空間
      if (actualPages === effectiveTargetPages && finalScale < MAX_SCALE) {
        // 從目前的 scale 開始，每次嘗試加一點
        let testScale = finalScale;
        const step = 0.02;  // 每次加 2%

        for (let i = 0; i < 10; i++) {
          const candidate = testScale + step;
          if (candidate > MAX_SCALE) break;

          let fScale = fontScale;
          if (effectiveTargetPages >= 2 && candidate > 1.0) {
            fScale = 1.0 + (candidate - 1.0) * 0.3;
            fScale = Math.min(fScale, 1.25);
          }

          await applyScale(candidate, fScale);
          await reflow();
          const testPages = await getPdfPageCount();

          if (testPages <= effectiveTargetPages) {
            testScale = candidate;
            fontScale = fScale;
            console.log(`[fit-page] Fill-up: scale=${candidate.toFixed(3)} still fits (${testPages} page(s))`);
          } else {
            console.log(`[fit-page] Fill-up: scale=${candidate.toFixed(3)} overflows (${testPages} page(s)), stopping`);
            break;
          }
        }

        finalScale = testScale;
        await applyScale(finalScale, fontScale);
        await reflow();
        actualPages = await getPdfPageCount();
      }

      // ── 最終結果 ─────────────────────────────────
      const finalHeight = await getHeight();
      const pageUsableHeight = A4_USABLE_HEIGHT_PX * effectiveTargetPages;
      const fillPercent = Math.round((finalHeight / pageUsableHeight) * 100);

      // 擠壓等級判定（僅在壓縮模式有意義）
      let squeezeLevel, recommendation;
      if (finalScale >= SQUEEZE_COMFORTABLE) {
        squeezeLevel = 'comfortable';
        recommendation = 'ok';
      } else if (finalScale >= SQUEEZE_TIGHT) {
        squeezeLevel = 'tight';
        recommendation = 'ok';
      } else {
        squeezeLevel = 'very_tight';
        recommendation = 'suggest_2_pages';
      }

      // 如果目標是多頁，squeeze 一定是 comfortable
      if (effectiveTargetPages >= 2 && finalScale >= 1.0) {
        squeezeLevel = 'comfortable';
        recommendation = 'ok';
      }

      console.log(`[fit-page] ── Final Result ──`);
      console.log(`[fit-page] scale=${finalScale.toFixed(3)}, fontScale=${fontScale.toFixed(3)}`);
      console.log(`[fit-page] ${actualPages} page(s), ${fillPercent}% fill`);
      console.log(`[fit-page] squeeze_level=${squeezeLevel}, recommendation=${recommendation}`);

      // --dry-run：只輸出 JSON，不生成 PDF
      if (dryRun) {
        // 用最終 scale 判斷方向（非初始估計）
        const finalDirection = finalScale > 1.0 ? 'EXPAND' : finalScale < 1.0 ? 'COMPRESS' : 'NO CHANGE';
        const result = {
          scale: parseFloat(finalScale.toFixed(3)),
          font_scale: parseFloat(fontScale.toFixed(3)),
          direction: finalDirection,
          target_pages: effectiveTargetPages,
          actual_pages: actualPages,
          fill_percent: fillPercent,
          squeeze_level: squeezeLevel,
          recommendation: recommendation,
        };
        console.log(`\n[fit-page-json] ${JSON.stringify(result)}`);
        return result;
      }

      if (clampedScale < SQUEEZE_TIGHT && effectiveTargetPages === 1) {
        console.log(`[fit-page] WARNING: Content is very tight at scale=${finalScale.toFixed(3)}. Consider --pages=2 for better readability.`);
      }
    }

    // ── 生成 PDF ─────────────────────────────────────
    if (!dryRun) {
      await page.pdf({
        path: absoluteOutput,
        ...PDF_OPTIONS,
      });

      console.log(`PDF generated: ${absoluteOutput}`);
    }
  } finally {
    try { await browser.close(); } catch (_) { /* browser already closed */ }
  }
}

// ── CLI 入口 ─────────────────────────────────────────
const args = process.argv.slice(2);

// 解析選項
const fitPage = args.includes('--fit-page');
const dryRun = args.includes('--dry-run');
const auto = args.includes('--auto');

let targetPages = 1;
const pagesArg = args.find(a => a.startsWith('--pages='));
if (pagesArg) {
  targetPages = parseInt(pagesArg.split('=')[1], 10);
  if (isNaN(targetPages) || targetPages < 1) {
    console.error('Error: --pages must be a positive integer (e.g., --pages=1, --pages=2)');
    process.exit(1);
  }
}

// --dry-run 必須搭配 --fit-page 或 --auto
if (dryRun && !fitPage && !auto) {
  console.error('Error: --dry-run requires --fit-page or --auto');
  process.exit(1);
}

// --auto 與 --fit-page 互斥（auto 已內含 fit-page 邏輯）
if (auto && fitPage) {
  console.error('Error: --auto and --fit-page are mutually exclusive (--auto includes fit-page)');
  process.exit(1);
}

const fileArgs = args.filter(a => !a.startsWith('--'));
const [input, output] = fileArgs;

if (!input) {
  console.error('Usage: node html-to-pdf.js <input.html> [output.pdf] [options]');
  console.error('');
  console.error('Options:');
  console.error('  input.html       Source HTML file path');
  console.error('  output.pdf       Output PDF file path (default: same name with .pdf)');
  console.error('  --fit-page       Auto-adjust spacing to fill target page count');
  console.error('  --pages=N        Target page count (default: 1), used with --fit-page');
  console.error('  --auto           Auto-detect natural page count, then fit content to fill evenly');
  console.error('  --dry-run        Output metrics JSON only, no PDF (used with --fit-page or --auto)');
  console.error('');
  console.error('Examples:');
  console.error('  node html-to-pdf.js input.html output.pdf --fit-page');
  console.error('  node html-to-pdf.js input.html --fit-page --pages=2');
  console.error('  node html-to-pdf.js input.html --fit-page --dry-run');
  process.exit(1);
}

// 安全檢查：確保輸出檔名不會覆蓋輸入檔案
let outputFile = output || input.replace(/\.html?$/i, '.pdf');
if (outputFile === input) {
  // 輸入檔案不是 .html/.htm 副檔名，附加 .pdf 避免覆蓋
  outputFile = input + '.pdf';
}

htmlToPdf(input, outputFile, { fitPage, targetPages, dryRun, auto }).catch(err => {
  console.error('PDF generation failed:', err.message);
  process.exit(1);
});
