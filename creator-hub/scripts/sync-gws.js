#!/usr/bin/env node
/**
 * sync-gws.js — Local sync using gws CLI (user OAuth) instead of service account.
 * Drop-in replacement for sync-drive.js when running locally without SA key.
 * Produces identical data/files.json output.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const CHANNELS_PATH = path.join(ROOT, 'data', 'channels.json');
const OUTPUT_PATH = path.join(ROOT, 'data', 'files.json');
const GWS = '/opt/homebrew/bin/gws';

function gws(resource, method, params) {
  // Write params to temp file to avoid shell quoting issues
  const tmpFile = path.join(ROOT, '.tmp-gws-params.json');
  fs.writeFileSync(tmpFile, JSON.stringify(params));
  try {
    const cmd = `${GWS} drive ${resource} ${method} --params "$(cat ${tmpFile})"`;
    const out = execSync(cmd, { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
    const jsonStart = out.indexOf('{');
    return JSON.parse(out.substring(jsonStart));
  } finally {
    try { fs.unlinkSync(tmpFile); } catch {}
  }
}

function parseFilename(name, prefix) {
  let base = name.replace(/\.html$/i, '');
  const idPattern = prefix ? new RegExp(`^(${prefix}\\d+)`) : /^([A-Z]+\d+)/;
  let idMatch = base.match(idPattern);
  if (!idMatch && prefix) idMatch = base.match(/^([A-Z]+\d+)/);

  if (!idMatch) {
    const safeId = base.replace(/[（）()【】\[\]{}]/g, '').replace(/[^a-zA-Z0-9\u4e00-\u9fff]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '').substring(0, 40);
    return { id: safeId || 'untitled', title: base, rawId: null };
  }

  const id = idMatch[1];
  let title = base.substring(idMatch[0].length);
  title = title.replace(/^[-_：:—\s]+/, '');
  const dupPattern = new RegExp(`^${id}[：:—\\-\\s]*`);
  title = title.replace(dupPattern, '');
  title = title.replace(/^v\d+[-_：:—\s]*/i, '');
  title = title.replace(/[-_]*(完整版|美化版|full|校準版)[-_]*/g, '');
  title = title.trim().replace(/^[-_：:—\s]+/, '').replace(/[-_：:—\s]+$/, '');
  return { id, title: title || id, rawId: id };
}

function listHtmlFiles(folderId) {
  const allFiles = [];
  let pageToken = null;
  do {
    const params = {
      q: `'${folderId}' in parents and mimeType='text/html' and trashed=false`,
      fields: 'nextPageToken, files(id, name, size, modifiedTime)',
      orderBy: 'name',
      pageSize: 100,
    };
    if (pageToken) params.pageToken = pageToken;
    const res = gws('files', 'list', params);
    allFiles.push(...(res.files || []));
    pageToken = res.nextPageToken || null;
  } while (pageToken);
  return allFiles;
}

function deduplicateFiles(files, prefix) {
  const byId = new Map();
  for (const file of files) {
    const parsed = parseFilename(file.name, prefix);
    const key = parsed.rawId || parsed.id;
    const size = parseInt(file.size || '0', 10);
    const existing = byId.get(key);
    if (!existing || size > existing.size) {
      byId.set(key, { fileId: file.id, name: file.name, storyId: parsed.rawId || parsed.id, title: parsed.title, size, modifiedTime: file.modifiedTime });
    }
  }
  return Array.from(byId.values()).sort((a, b) => a.storyId.localeCompare(b.storyId, undefined, { numeric: true }));
}

function main() {
  const config = JSON.parse(fs.readFileSync(CHANNELS_PATH, 'utf8'));
  const { rootFolderId, ignoreFolders = [], channels: channelConfigs, defaults } = config;

  console.log(`Discovering channels in root folder ${rootFolderId}...`);
  const foldersRes = gws('files', 'list', {
    q: `'${rootFolderId}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false`,
    fields: 'files(id, name)',
    orderBy: 'name',
    pageSize: 100,
  });

  const folders = (foldersRes.files || []).filter(f => !ignoreFolders.includes(f.name));
  const byFolderName = {};
  for (const [channelId, conf] of Object.entries(channelConfigs)) {
    byFolderName[conf.folderName] = { channelId, ...conf };
  }

  const channels = [];
  for (const folder of folders) {
    const match = byFolderName[folder.name];
    if (match) {
      channels.push({ id: match.channelId, folderId: folder.id, folderName: folder.name, name: match.name, prefix: match.prefix, season: match.season, icon: match.icon, description: match.description || defaults.description });
    } else {
      const autoId = folder.name.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-').replace(/^-|-$/g, '').substring(0, 30);
      console.log(`  [NEW] Unknown folder: "${folder.name}" → skipped`);
    }
  }

  console.log(`Found ${channels.length} channel(s)\n`);

  const result = {
    generatedAt: new Date().toISOString(),
    channelList: channels.map(ch => ({ id: ch.id, name: ch.name, prefix: ch.prefix, season: ch.season, icon: ch.icon, description: ch.description, isNew: false })),
    channels: {},
  };

  for (const channel of channels) {
    console.log(`[${channel.id}] Scanning "${channel.folderName}" (${channel.folderId})...`);
    const rawFiles = listHtmlFiles(channel.folderId);
    console.log(`  Found ${rawFiles.length} HTML files`);
    const deduped = deduplicateFiles(rawFiles, channel.prefix);
    console.log(`  After dedup: ${deduped.length} unique stories`);
    result.channels[channel.id] = { files: deduped, count: deduped.length };
  }

  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(result, null, 2));
  console.log(`\nWrote ${OUTPUT_PATH}`);
}

main();
