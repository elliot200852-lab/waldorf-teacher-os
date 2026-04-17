/**
 * extract-thumbnails.js — Extract/fetch thumbnails for each story
 *
 * Thumbnail fallback chain:
 *   1. Extract base64 image from HTML (works for story-daily 10+ MB files)
 *   2. Search pic-fetch Drive folder for matching thumbnail by title keywords
 *   3. Use pic-fetch "others" thumbnail
 *   4. Use {channelId}-default.jpg (locally committed)
 *   5. Watercolor placeholder (last resort)
 *
 * Also saves full HTML files to public/stories/ for Firebase hosting.
 */

const { google } = require('googleapis');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const FILES_PATH = path.join(ROOT, 'data', 'files.json');
const CHANNELS_PATH = path.join(ROOT, 'data', 'channels.json');
const THUMB_DIR = path.join(ROOT, 'public', 'thumbnails');
const STORIES_DIR = path.join(ROOT, 'public', 'stories');
const PLACEHOLDER_PATH = path.join(THUMB_DIR, 'placeholder.jpg');

const FORCE = process.argv.includes('--force');
const THUMB_WIDTH = 800;
const JPEG_QUALITY = 80;

// Curriculum position for ancient-myths TW interludes (shared with generate-site.js)
function getCurriculumPosition(storyId) {
  const TW = { TW01: 8, TW02: 13, TW03: 19, TW04: 25 };
  if (TW[storyId]) return TW[storyId];
  const m = storyId.match(/^AM(\d+)$/);
  if (!m) return 0;
  const n = parseInt(m[1], 10);
  if (n <= 7) return n;
  if (n <= 11) return n + 1;
  if (n <= 16) return n + 2;
  return n + 3;
}

// Cache for pic-fetch folder contents
let _picFetchCache = null;

async function getDriveClient() {
  let credentials;
  if (process.env.GOOGLE_SERVICE_ACCOUNT_KEY) {
    credentials = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_KEY);
  } else {
    const keyPath = path.join(ROOT, 'service-account-key.json');
    if (fs.existsSync(keyPath)) {
      credentials = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
    } else {
      console.error('No service account key found.');
      process.exit(1);
    }
  }
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/drive.readonly'],
  });
  return google.drive({ version: 'v3', auth });
}

async function downloadFile(drive, fileId) {
  const res = await drive.files.get(
    { fileId, alt: 'media' },
    { responseType: 'arraybuffer' }
  );
  return Buffer.from(res.data);
}

function extractBase64Image(htmlBuffer) {
  const html = htmlBuffer.toString('utf8');
  const match = html.match(/src="data:image\/(png|jpeg|jpg|webp|avif);base64,([A-Za-z0-9+/=\s]+)"/);
  if (!match) return null;
  const b64 = match[2].replace(/\s/g, '');
  return Buffer.from(b64, 'base64');
}

/**
 * List all image files in the pic-fetch folder (cached).
 */
async function listPicFetchImages(drive, pickFetchFolderId) {
  if (_picFetchCache) return _picFetchCache;
  if (!pickFetchFolderId) { _picFetchCache = []; return []; }

  try {
    const res = await drive.files.list({
      q: `'${pickFetchFolderId}' in parents and (mimeType contains 'image/') and trashed=false`,
      fields: 'files(id, name, size)',
      pageSize: 200,
      orderBy: 'name',
    });
    _picFetchCache = res.data.files || [];
    console.log(`[pic-fetch] Loaded ${_picFetchCache.length} images from pic-fetch folder`);
  } catch (err) {
    console.warn(`[pic-fetch] Could not access pic-fetch folder: ${err.message}`);
    _picFetchCache = [];
  }
  return _picFetchCache;
}

/**
 * Find a matching thumbnail in pic-fetch by story title keywords.
 * Returns Drive file object or null.
 */
function findMatchingPicFetch(picFetchImages, storyTitle, channelName) {
  if (!picFetchImages.length) return null;

  // Try exact substring match first
  const titleLower = storyTitle.toLowerCase();
  const channelLower = (channelName || '').toLowerCase();

  // Build search terms from title (split on common separators)
  const keywords = storyTitle
    .split(/[-—_：:，、。\s]+/)
    .filter(k => k.length >= 2);

  // 1. Try matching story title keywords against image filenames
  for (const img of picFetchImages) {
    const imgName = img.name.toLowerCase();
    for (const kw of keywords) {
      if (imgName.includes(kw.toLowerCase())) {
        return img;
      }
    }
  }

  // 2. Try matching channel name
  if (channelName) {
    for (const img of picFetchImages) {
      const imgName = img.name.toLowerCase();
      if (imgName.includes(channelLower)) {
        return img;
      }
    }
  }

  return null;
}

/**
 * Find the "others" fallback image in pic-fetch.
 */
function findOthersPicFetch(picFetchImages) {
  if (!picFetchImages.length) return null;
  for (const img of picFetchImages) {
    const n = img.name.toLowerCase();
    if (n.includes('other') || n.includes('default') || n.includes('fallback')) {
      return img;
    }
  }
  // If no explicit "others", use the last image as fallback
  return picFetchImages[picFetchImages.length - 1];
}

async function generatePlaceholder() {
  if (fs.existsSync(PLACEHOLDER_PATH) && !FORCE) return;
  const svg = `<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2a2a2a"/><stop offset="100%" style="stop-color:#1a1a1a"/>
    </linearGradient></defs>
    <rect width="800" height="500" fill="url(#g)"/>
    <text x="400" y="260" font-family="serif" font-size="48" fill="rgba(255,255,255,0.08)" text-anchor="middle">&#x1F3A8;</text>
  </svg>`;
  await sharp(Buffer.from(svg)).jpeg({ quality: JPEG_QUALITY }).toFile(PLACEHOLDER_PATH);
  console.log('Generated placeholder.jpg');
}

async function generateWatercolorPlaceholders() {
  const palettes = [
    { name: 'sunrise',  c1: '#E8A87C', c2: '#D4688E', c3: '#F6E58D', bg: '#FFF5E6' },
    { name: 'lavender', c1: '#B5A8D5', c2: '#8B7BB0', c3: '#D4C5F0', bg: '#F2EAF8' },
    { name: 'ocean',    c1: '#7EC8C8', c2: '#4A7C6F', c3: '#A8D8D0', bg: '#E8F4F0' },
    { name: 'autumn',   c1: '#C47D3B', c2: '#8B6F47', c3: '#E8A87C', bg: '#FAF0E6' },
    { name: 'rose',     c1: '#D4688E', c2: '#B85070', c3: '#F0A0B8', bg: '#FFF0F0' },
    { name: 'forest',   c1: '#6B8E5E', c2: '#4A6B3A', c3: '#A0C890', bg: '#EAF5E0' },
    { name: 'golden',   c1: '#D4A050', c2: '#B8863C', c3: '#F0D080', bg: '#FFF8E0' },
    { name: 'twilight', c1: '#5E6B8E', c2: '#3A4A6B', c3: '#8090B0', bg: '#E8ECF5' },
    { name: 'earth',    c1: '#A08060', c2: '#806040', c3: '#C0A080', bg: '#F5F0E8' },
    { name: 'spring',   c1: '#7CB87C', c2: '#5B9B5B', c3: '#B8D8A0', bg: '#EFF8EA' },
  ];
  for (let i = 0; i < palettes.length; i++) {
    const outPath = path.join(THUMB_DIR, `watercolor-${i + 1}.jpg`);
    if (fs.existsSync(outPath) && !FORCE) continue;
    const p = palettes[i];
    const svg = `<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <filter id="blur${i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
        <filter id="grain${i}"><feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feBlend in="SourceGraphic" mode="multiply"/></filter>
      </defs>
      <rect width="800" height="500" fill="${p.bg}"/>
      <ellipse cx="250" cy="200" rx="300" ry="250" fill="${p.c1}" opacity="0.35" filter="url(#blur${i})"/>
      <ellipse cx="550" cy="300" rx="280" ry="220" fill="${p.c2}" opacity="0.3" filter="url(#blur${i})"/>
      <ellipse cx="400" cy="150" rx="250" ry="200" fill="${p.c3}" opacity="0.25" filter="url(#blur${i})"/>
      <ellipse cx="150" cy="400" rx="200" ry="180" fill="${p.c2}" opacity="0.2" filter="url(#blur${i})"/>
      <ellipse cx="650" cy="100" rx="180" ry="150" fill="${p.c1}" opacity="0.15" filter="url(#blur${i})"/>
      <rect width="800" height="500" filter="url(#grain${i})" opacity="0.03"/>
    </svg>`;
    await sharp(Buffer.from(svg)).jpeg({ quality: 85 }).toFile(outPath);
  }
  console.log('Generated 10 watercolor placeholders');
}

async function main() {
  const filesData = JSON.parse(fs.readFileSync(FILES_PATH, 'utf8'));
  const config = JSON.parse(fs.readFileSync(CHANNELS_PATH, 'utf8'));
  const drive = await getDriveClient();

  fs.mkdirSync(THUMB_DIR, { recursive: true });
  fs.mkdirSync(STORIES_DIR, { recursive: true });
  await generatePlaceholder();
  await generateWatercolorPlaceholders();

  // Pre-load pic-fetch images for fallback
  const picFetchImages = await listPicFetchImages(drive, config.pickFetchFolderId);

  // Build channel list from files.json (which now includes channelList from sync)
  const channelList = filesData.channelList || [];

  for (const channelInfo of channelList) {
    const channelFiles = filesData.channels[channelInfo.id];
    if (!channelFiles || channelFiles.count === 0) {
      console.log(`[${channelInfo.id}] No files, skipping`);
      continue;
    }

    // Channel-level default thumbnail
    const channelDefaultPath = path.join(THUMB_DIR, `${channelInfo.id}-default.jpg`);
    const useChannelDefault = fs.existsSync(channelDefaultPath);

    console.log(`\n[${channelInfo.id}] Processing ${channelFiles.count} files...`);
    let watercolorIdx = 0;

    // Determine the most recently modified story for channel cover
    const latestByTime = [...channelFiles.files].sort((a, b) =>
      (b.modifiedTime || '').localeCompare(a.modifiedTime || '')
    )[0];

    const sorted = channelInfo.id === 'ancient-myths'
      ? [...channelFiles.files].sort((a, b) => getCurriculumPosition(b.storyId) - getCurriculumPosition(a.storyId))
      : [...channelFiles.files].sort((a, b) => b.storyId.localeCompare(a.storyId, undefined, { numeric: true }));

    for (const file of sorted) {
      const thumbPath = path.join(THUMB_DIR, `${file.storyId}.jpg`);
      const storyPath = path.join(STORIES_DIR, `${file.storyId}.html`);

      if (fs.existsSync(thumbPath) && fs.existsSync(storyPath) && !FORCE) {
        console.log(`  ${file.storyId}: exists, skipping`);
        continue;
      }

      console.log(`  ${file.storyId}: downloading HTML (${(file.size / 1024 / 1024).toFixed(1)} MB)...`);

      try {
        const htmlBuffer = await downloadFile(drive, file.fileId);
        fs.writeFileSync(storyPath, htmlBuffer);
        console.log(`  ${file.storyId}: HTML saved (${(htmlBuffer.length / 1024 / 1024).toFixed(1)} MB)`);

        // --- Thumbnail fallback chain ---
        // Priority: HTML embedded > pic-fetch match > channel-default > watercolor placeholder

        // 1. Try extracting from HTML (works for large files with embedded images)
        const imgBuffer = extractBase64Image(htmlBuffer);

        if (imgBuffer) {
          await sharp(imgBuffer)
            .resize(THUMB_WIDTH, null, { withoutEnlargement: true })
            .jpeg({ quality: JPEG_QUALITY })
            .toFile(thumbPath);
          const thumbSize = fs.statSync(thumbPath).size;
          console.log(`  ${file.storyId}: thumbnail extracted (${(thumbSize / 1024).toFixed(0)} KB)`);
        } else {
          // 2. Search pic-fetch for matching thumbnail
          const picMatch = findMatchingPicFetch(picFetchImages, file.title, channelInfo.name);
          if (picMatch) {
            console.log(`  ${file.storyId}: fetching from pic-fetch: "${picMatch.name}"...`);
            const imgBuf = await downloadFile(drive, picMatch.id);
            await sharp(imgBuf)
              .resize(THUMB_WIDTH, null, { withoutEnlargement: true })
              .jpeg({ quality: JPEG_QUALITY })
              .toFile(thumbPath);
            console.log(`  ${file.storyId}: pic-fetch thumbnail saved`);
          } else if (useChannelDefault) {
            // 3. Channel-level default (fallback when no pic-fetch match)
            fs.copyFileSync(channelDefaultPath, thumbPath);
            console.log(`  ${file.storyId}: using ${channelInfo.id}-default.jpg`);
          } else {
            // 4. Use pic-fetch "others" fallback
            const othersPic = findOthersPicFetch(picFetchImages);
            if (othersPic) {
              console.log(`  ${file.storyId}: fetching pic-fetch others fallback: "${othersPic.name}"...`);
              const imgBuf = await downloadFile(drive, othersPic.id);
              await sharp(imgBuf)
                .resize(THUMB_WIDTH, null, { withoutEnlargement: true })
                .jpeg({ quality: JPEG_QUALITY })
                .toFile(thumbPath);
              console.log(`  ${file.storyId}: pic-fetch others thumbnail saved`);
            } else {
              // 5. Watercolor placeholder (last resort)
              watercolorIdx = (watercolorIdx % 10) + 1;
              const wcPath = path.join(THUMB_DIR, `watercolor-${watercolorIdx}.jpg`);
              fs.copyFileSync(wcPath, thumbPath);
              console.log(`  ${file.storyId}: no image found, using watercolor-${watercolorIdx}`);
            }
          }
        }
      } catch (err) {
        console.error(`  ${file.storyId}: ERROR — ${err.message}`);
        watercolorIdx = (watercolorIdx % 10) + 1;
        fs.copyFileSync(path.join(THUMB_DIR, `watercolor-${watercolorIdx}.jpg`), thumbPath);
      }

    }

    // Channel cover: use default or most recently modified story's thumbnail
    const coverPath = path.join(THUMB_DIR, `cover-${channelInfo.id}.jpg`);
    if (useChannelDefault) {
      fs.copyFileSync(channelDefaultPath, coverPath);
      console.log(`  Cover: ${channelInfo.id}-default.jpg`);
    } else if (latestByTime) {
      const latestThumbPath = path.join(THUMB_DIR, `${latestByTime.storyId}.jpg`);
      if (fs.existsSync(latestThumbPath)) {
        fs.copyFileSync(latestThumbPath, coverPath);
        console.log(`  Cover: ${latestByTime.storyId}.jpg (latest by modifiedTime: ${latestByTime.modifiedTime})`);
      }
    }
  }

  console.log('\nDone! All thumbnails processed.');
}

main().catch(err => {
  console.error('extract-thumbnails failed:', err.message);
  process.exit(1);
});
