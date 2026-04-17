#!/usr/bin/env node
/**
 * download-stories-gws.js — Download story HTML files from Drive using gws CLI.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const FILES_PATH = path.join(ROOT, 'data', 'files.json');
const STORIES_DIR = path.join(ROOT, 'public', 'stories');
const GWS = '/opt/homebrew/bin/gws';

function main() {
  const filesData = JSON.parse(fs.readFileSync(FILES_PATH, 'utf8'));
  fs.mkdirSync(STORIES_DIR, { recursive: true });

  let total = 0, downloaded = 0, skipped = 0, failed = 0;

  for (const [channelId, channelData] of Object.entries(filesData.channels)) {
    const files = channelData.files || [];
    console.log(`[${channelId}] ${files.length} stories`);

    for (const file of files) {
      total++;
      const outPath = path.join(STORIES_DIR, `${file.storyId}.html`);

      if (fs.existsSync(outPath) && fs.statSync(outPath).size > 0) {
        skipped++;
        continue;
      }

      try {
        const params = JSON.stringify({ fileId: file.fileId, alt: 'media' });
        const tmpParams = path.join(ROOT, '.tmp-dl-params.json');
        fs.writeFileSync(tmpParams, params);
        execSync(`${GWS} drive files get --params "$(cat ${tmpParams})" -o "${outPath}"`, {
          encoding: 'utf8', timeout: 60000, stdio: ['pipe', 'pipe', 'pipe']
        });
        try { fs.unlinkSync(tmpParams); } catch {}

        if (fs.existsSync(outPath) && fs.statSync(outPath).size > 0) {
          downloaded++;
          process.stdout.write(`  + ${file.storyId} (${Math.round(file.size/1024)}KB)\n`);
        } else {
          failed++;
          console.log(`  x ${file.storyId} (empty)`);
        }
      } catch (err) {
        failed++;
        console.log(`  x ${file.storyId} (error)`);
      }
    }
  }

  console.log(`\nDone: ${downloaded} downloaded, ${skipped} skipped, ${failed} failed (${total} total)`);
}

main();
