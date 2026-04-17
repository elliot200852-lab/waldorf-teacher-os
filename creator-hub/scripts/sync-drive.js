/**
 * sync-drive.js — Auto-discover channels from Google Drive and build files.json
 *
 * Scans the root folder for subfolders (each = a channel), queries Drive API
 * for HTML files in each, deduplicates by story ID, and writes data/files.json.
 *
 * Channel discovery:
 *   1. List subfolders under rootFolderId
 *   2. Skip folders in ignoreFolders list
 *   3. Match folder name to channels config (by folderName)
 *   4. Unknown folders → auto-create channel with defaults
 *
 * Auth: GOOGLE_SERVICE_ACCOUNT_KEY env var (JSON string) or local key file.
 */

const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const CHANNELS_PATH = path.join(ROOT, 'data', 'channels.json');
const OUTPUT_PATH = path.join(ROOT, 'data', 'files.json');

async function getDriveClient() {
  let credentials;
  if (process.env.GOOGLE_SERVICE_ACCOUNT_KEY) {
    credentials = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_KEY);
  } else {
    const keyPath = path.join(ROOT, 'service-account-key.json');
    if (fs.existsSync(keyPath)) {
      credentials = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
    } else {
      console.error('No service account key found. Set GOOGLE_SERVICE_ACCOUNT_KEY env var or place service-account-key.json in creator-hub/');
      process.exit(1);
    }
  }
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/drive.readonly'],
  });
  return google.drive({ version: 'v3', auth });
}

/**
 * Discover channels by listing subfolders under the root folder.
 * Returns array of { id, folderId, folderName, name, prefix, season, icon, description }.
 */
async function discoverChannels(drive, config) {
  const { rootFolderId, ignoreFolders = [], channels: channelConfigs, defaults } = config;

  // List all subfolders under root
  const res = await drive.files.list({
    q: `'${rootFolderId}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false`,
    fields: 'files(id, name)',
    orderBy: 'name',
    pageSize: 100,
  });

  const folders = (res.data.files || []).filter(f => !ignoreFolders.includes(f.name));

  // Build reverse lookup: folderName → channelId
  const byFolderName = {};
  for (const [channelId, conf] of Object.entries(channelConfigs)) {
    byFolderName[conf.folderName] = { channelId, ...conf };
  }

  const discovered = [];
  let autoIdx = 0;

  for (const folder of folders) {
    const match = byFolderName[folder.name];
    if (match) {
      discovered.push({
        id: match.channelId,
        folderId: folder.id,
        folderName: folder.name,
        name: match.name,
        prefix: match.prefix,
        season: match.season,
        icon: match.icon,
        description: match.description || defaults.description,
      });
    } else {
      // Unknown folder — auto-create channel
      autoIdx++;
      const autoId = folder.name
        .toLowerCase()
        .replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-')
        .replace(/^-|-$/g, '')
        .substring(0, 30) || `channel-${autoIdx}`;
      const autoPrefix = `X${autoIdx}`;

      console.log(`  [NEW] Discovered new channel folder: "${folder.name}" → id="${autoId}", prefix="${autoPrefix}"`);

      discovered.push({
        id: autoId,
        folderId: folder.id,
        folderName: folder.name,
        name: folder.name,
        prefix: autoPrefix,
        season: defaults.season,
        icon: defaults.icon,
        description: defaults.description,
        isNew: true,
      });
    }
  }

  return discovered;
}

/**
 * Parse story ID and title from filename.
 * Examples:
 *   "A013-星星告訴我們何時狩獵.html" → { id: "A013", title: "星星告訴我們何時狩獵" }
 *   "B005-B005：地衣.html" → { id: "B005", title: "地衣" }
 *   "AM006-羅摩與悉多.html" → { id: "AM006", title: "羅摩與悉多" }
 */
function parseFilename(name, prefix) {
  let base = name.replace(/\.html$/i, '');

  const idPattern = prefix
    ? new RegExp(`^(${prefix}\\d+)`)
    : /^([A-Z]+\d+)/;
  let idMatch = base.match(idPattern);

  // If prefix-specific pattern fails, try generic uppercase-letter+digits pattern
  // (e.g. channel prefix is "A" but file is "EN001-..." → still parse "EN001" as the ID)
  if (!idMatch && prefix) {
    idMatch = base.match(/^([A-Z]+\d+)/);
  }

  if (!idMatch) {
    // No recognized ID — generate stable ID from filename
    const safeId = base
      .replace(/[（）()【】\[\]{}]/g, '')
      .replace(/[^a-zA-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .substring(0, 40);
    return { id: safeId || 'untitled', title: base, rawId: null };
  }

  const id = idMatch[1];
  let title = base.substring(idMatch[0].length);

  // Clean up title
  title = title.replace(/^[-_：:—\s]+/, '');
  // Remove duplicate ID in title (e.g. "B005-B005：地衣" → after split: "B005：地衣" → "地衣")
  const dupPattern = new RegExp(`^${id}[：:—\\-\\s]*`);
  title = title.replace(dupPattern, '');
  title = title.replace(/^v\d+[-_：:—\s]*/i, '');
  title = title.replace(/[-_]*(完整版|美化版|full|校準版)[-_]*/g, '');
  title = title.trim().replace(/^[-_：:—\s]+/, '').replace(/[-_：:—\s]+$/, '');

  return { id, title: title || id, rawId: id };
}

async function listHtmlFiles(drive, folderId) {
  const files = [];
  let pageToken = null;
  do {
    const res = await drive.files.list({
      q: `'${folderId}' in parents and mimeType='text/html' and trashed=false`,
      fields: 'nextPageToken, files(id, name, size, modifiedTime)',
      orderBy: 'name',
      pageSize: 100,
      pageToken,
    });
    files.push(...(res.data.files || []));
    pageToken = res.data.nextPageToken;
  } while (pageToken);
  return files;
}

/**
 * Deduplicate: for each story ID, keep the file with largest size.
 * No size filter — validate.js handles quality warnings downstream.
 * For files without a recognized prefix, auto-assign sequential IDs.
 */
function deduplicateFiles(files, prefix) {
  const byId = new Map();

  for (const file of files) {
    const parsed = parseFilename(file.name, prefix);
    const key = parsed.rawId || parsed.id;
    const size = parseInt(file.size || '0', 10);

    const existing = byId.get(key);
    if (!existing || size > existing.size) {
      byId.set(key, {
        fileId: file.id,
        name: file.name,
        storyId: parsed.rawId || parsed.id,
        title: parsed.title,
        size,
        modifiedTime: file.modifiedTime,
      });
    }
  }

  let results = Array.from(byId.values()).sort((a, b) =>
    a.storyId.localeCompare(b.storyId, undefined, { numeric: true })
  );

  // No re-ID: storyId comes directly from the filename (either parsed prefix+number
  // or sanitized filename). This ensures the ID always matches the actual file.

  return results;
}

async function main() {
  const config = JSON.parse(fs.readFileSync(CHANNELS_PATH, 'utf8'));
  const drive = await getDriveClient();

  console.log(`Discovering channels in root folder ${config.rootFolderId}...`);
  const channels = await discoverChannels(drive, config);
  console.log(`Found ${channels.length} channel(s)\n`);

  const result = {
    generatedAt: new Date().toISOString(),
    channelList: channels.map(ch => ({
      id: ch.id,
      name: ch.name,
      prefix: ch.prefix,
      season: ch.season,
      icon: ch.icon,
      description: ch.description,
      isNew: ch.isNew || false,
    })),
    channels: {},
  };

  for (const channel of channels) {
    console.log(`[${channel.id}] Scanning "${channel.folderName}" (${channel.folderId})...`);
    const rawFiles = await listHtmlFiles(drive, channel.folderId);
    console.log(`  Found ${rawFiles.length} HTML files`);

    const deduped = deduplicateFiles(rawFiles, channel.prefix);
    console.log(`  After dedup: ${deduped.length} unique stories`);

    result.channels[channel.id] = {
      files: deduped,
      count: deduped.length,
    };
  }

  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(result, null, 2));
  console.log(`\nWrote ${OUTPUT_PATH}`);
}

main().catch(err => {
  console.error('sync-drive failed:', err.message);
  process.exit(1);
});
