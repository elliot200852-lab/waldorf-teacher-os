/**
 * validate.js — Build quality gate for CreatorHub
 *
 * Runs after generate-site.js, before deploy. Checks:
 *   - At least 1 channel has files (BLOCK)
 *   - index.html exists (BLOCK)
 *   - Each channel page exists (BLOCK)
 *   - Each story HTML exists and > 0 bytes (BLOCK)
 *   - Thumbnail coverage stats (WARN)
 *   - HTML size warnings for files < 1MB (WARN)
 *
 * Exit code 0 = pass, 1 = blocked.
 * Writes data/validation-report.json for CI artifact.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const FILES_PATH = path.join(ROOT, 'data', 'files.json');
const PUBLIC_DIR = path.join(ROOT, 'public');
const THUMB_DIR = path.join(PUBLIC_DIR, 'thumbnails');
const STORIES_DIR = path.join(PUBLIC_DIR, 'stories');
const REPORT_PATH = path.join(ROOT, 'data', 'validation-report.json');

function main() {
  if (!fs.existsSync(FILES_PATH)) {
    console.error('BLOCK: data/files.json not found. Run npm run sync first.');
    process.exit(1);
  }

  const filesData = JSON.parse(fs.readFileSync(FILES_PATH, 'utf8'));
  const channelList = filesData.channelList || [];

  const report = {
    timestamp: new Date().toISOString(),
    status: 'pass',
    blocks: [],
    warnings: [],
    channels: {},
  };

  let hasFiles = false;

  // --- Check index.html ---
  const indexPath = path.join(PUBLIC_DIR, 'index.html');
  if (!fs.existsSync(indexPath)) {
    report.blocks.push('index.html does not exist');
  }

  // --- Per-channel checks ---
  for (const ch of channelList) {
    const channelFiles = filesData.channels[ch.id];
    const files = channelFiles?.files || [];
    const count = files.length;

    const chReport = {
      name: ch.name,
      storyCount: count,
      thumbExtracted: 0,
      thumbFallback: 0,
      smallHtml: [],
      missingStories: [],
      missingThumbs: [],
    };

    if (count > 0) hasFiles = true;

    // Check channel page exists
    const channelPage = path.join(PUBLIC_DIR, 'channel', `${ch.id}.html`);
    if (count > 0 && !fs.existsSync(channelPage)) {
      report.blocks.push(`Channel page missing: channel/${ch.id}.html`);
    }

    for (const file of files) {
      // Check story HTML
      const storyPath = path.join(STORIES_DIR, `${file.storyId}.html`);
      if (!fs.existsSync(storyPath)) {
        chReport.missingStories.push(file.storyId);
      } else {
        const storySize = fs.statSync(storyPath).size;
        if (storySize === 0) {
          report.blocks.push(`Empty story file: stories/${file.storyId}.html`);
        }
        if (storySize < 1024 * 1024) {
          chReport.smallHtml.push({ id: file.storyId, sizeKB: Math.round(storySize / 1024) });
        }
      }

      // Check thumbnail
      const thumbPath = path.join(THUMB_DIR, `${file.storyId}.jpg`);
      if (!fs.existsSync(thumbPath)) {
        chReport.missingThumbs.push(file.storyId);
        chReport.thumbFallback++;
      } else {
        // Check if it's a real extraction or a copy of watercolor/default
        const thumbSize = fs.statSync(thumbPath).size;
        // Watercolor placeholders are ~15-25KB, real extractions are 40-120KB
        if (thumbSize > 35000) {
          chReport.thumbExtracted++;
        } else {
          chReport.thumbFallback++;
        }
      }
    }

    // Generate warnings
    if (chReport.smallHtml.length > 0) {
      report.warnings.push(
        `[${ch.id}] ${chReport.smallHtml.length} HTML files < 1MB (may lack embedded images): ${chReport.smallHtml.map(h => `${h.id}(${h.sizeKB}KB)`).join(', ')}`
      );
    }
    if (chReport.missingStories.length > 0) {
      report.blocks.push(
        `[${ch.id}] Missing story files: ${chReport.missingStories.join(', ')}`
      );
    }

    report.channels[ch.id] = chReport;
  }

  if (!hasFiles) {
    report.blocks.push('No channels have any files');
  }

  // --- Determine final status ---
  if (report.blocks.length > 0) {
    report.status = 'blocked';
  }

  // --- Output ---
  fs.writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2));

  console.log('=== CreatorHub Validation Report ===\n');

  // Channel summary
  for (const ch of channelList) {
    const cr = report.channels[ch.id];
    if (!cr) continue;
    const total = cr.storyCount;
    const thumbRate = total > 0 ? Math.round(cr.thumbExtracted / total * 100) : 0;
    const status = total === 0 ? 'empty' : `${total} stories, ${thumbRate}% thumb extracted`;
    console.log(`  [${ch.id}] ${ch.name}: ${status}`);
  }

  console.log('');

  if (report.warnings.length > 0) {
    console.log('WARNINGS:');
    for (const w of report.warnings) console.log(`  - ${w}`);
    console.log('');
  }

  if (report.blocks.length > 0) {
    console.log('BLOCKED — deployment will not proceed:');
    for (const b of report.blocks) console.log(`  - ${b}`);
    console.log('');
    process.exit(1);
  }

  console.log('PASS — all quality checks passed.\n');
}

main();
