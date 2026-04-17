/**
 * generate-site.js — Generate static HTML pages from data/files.json + channels.json
 *
 * Produces:
 *   public/index.html           — Homepage with channel cards (cover = latest story's thumbnail)
 *   public/channel/{id}.html    — Channel page with story card grid
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const FILES_PATH = path.join(ROOT, 'data', 'files.json');
const CHANNELS_PATH = path.join(ROOT, 'data', 'channels.json');
const PUBLIC_DIR = path.join(ROOT, 'public');

// ─── Season color configs ────────────────────────────────────
const SEASON_CSS = {
  autumn: {
    primary: '#8B6F47', secondary: '#5B7553', accent: '#C47D3B',
    bgWash1: '#FAF6F0', bgWash2: '#F5E6C8', bgWash3: '#F0DDD5',
    onSurface: '#1C1C18', onSurfaceVariant: '#4E453B', outlineVariant: '#D1C4B7',
    gradient: 'linear-gradient(135deg, #8B6F47 0%, #5B7553 100%)',
    bodyGradient: 'radial-gradient(ellipse at top left, #FAF6F0 0%, #F5E6C8 50%, #F0DDD5 100%)',
  },
  summer: {
    primary: '#4A7C6F', secondary: '#C47D3B', accent: '#E06B40',
    bgWash1: '#FFF8F0', bgWash2: '#FFE8C8', bgWash3: '#F0E0D0',
    onSurface: '#1C2A25', onSurfaceVariant: '#3D4A44', outlineVariant: '#C4D4CC',
    gradient: 'linear-gradient(135deg, #4A7C6F 0%, #C47D3B 100%)',
    bodyGradient: 'radial-gradient(ellipse at top left, #FFF8F0 0%, #FFE8C8 50%, #F0E0D0 100%)',
  },
  spring: {
    primary: '#6B7F5E', secondary: '#9B7BB0', accent: '#D4A574',
    bgWash1: '#F0F5EB', bgWash2: '#E8F0D8', bgWash3: '#F2E8F5',
    onSurface: '#2A3325', onSurfaceVariant: '#4A5544', outlineVariant: '#C4D1B8',
    gradient: 'linear-gradient(135deg, #6B7F5E 0%, #9B7BB0 100%)',
    bodyGradient: 'radial-gradient(ellipse at top left, #F0F5EB 0%, #E8F0D8 50%, #F2E8F5 100%)',
  },
  winter: {
    primary: '#5E6B7F', secondary: '#7B6B60', accent: '#8B7B9B',
    bgWash1: '#F0F2F5', bgWash2: '#E0E5EB', bgWash3: '#E8E0F0',
    onSurface: '#1C1E22', onSurfaceVariant: '#44484F', outlineVariant: '#C4C8D0',
    gradient: 'linear-gradient(135deg, #5E6B7F 0%, #7B6B60 100%)',
    bodyGradient: 'radial-gradient(ellipse at top left, #F0F2F5 0%, #E0E5EB 50%, #E8E0F0 100%)',
  },
};

// ─── Shared HTML fragments ───────────────────────────────────
const HTML_HEAD = `<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta name="robots" content="noindex, nofollow"/>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script>
tailwind.config={theme:{extend:{fontFamily:{"headline":["Playfair Display","Noto Serif TC","Georgia","serif"],"body":["Plus Jakarta Sans","Noto Sans TC","PingFang TC","Microsoft JhengHei","sans-serif"],"label":["Plus Jakarta Sans","Noto Sans TC","sans-serif"]}}}}
</script>`;

const SHARED_CSS = `
.watercolor-wash-header{mask-image:url("data:image/svg+xml;utf8,<svg viewBox='0 0 100 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'><path d='M0,0 C20,10 40,-5 60,5 C80,15 100,0 100,0 L100,90 C80,100 60,85 40,95 C20,105 0,90 0,90 Z' fill='black'/></svg>");-webkit-mask-image:url("data:image/svg+xml;utf8,<svg viewBox='0 0 100 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'><path d='M0,0 C20,10 40,-5 60,5 C80,15 100,0 100,0 L100,90 C80,100 60,85 40,95 C20,105 0,90 0,90 Z' fill='black'/></svg>");mask-size:100% 100%;-webkit-mask-size:100% 100%}
.card-hover{transition:transform .25s ease,box-shadow .25s ease}
.card-hover:hover{transform:translateY(-4px);box-shadow:0 12px 28px rgba(0,0,0,.12)}
.thumb-overlay{background:linear-gradient(to top,rgba(0,0,0,.55) 0%,transparent 60%)}
.placeholder-thumb{background:linear-gradient(135deg,#2a2a2a,#1a1a1a);display:flex;align-items:center;justify-content:center}
.placeholder-thumb .material-symbols-outlined{font-size:3rem;color:rgba(255,255,255,.12)}
.material-symbols-outlined{font-variation-settings:"FILL" 0,"wght" 400,"GRAD" 0,"opsz" 24}
.stats-badge{backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}`;

function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function storyUrl(storyId) { return `/stories/${storyId}.html`; }
function thumbExists(storyId) { return fs.existsSync(path.join(PUBLIC_DIR, 'thumbnails', `${storyId}.jpg`)); }
function storyHtmlExists(storyId) { return fs.existsSync(path.join(PUBLIC_DIR, 'stories', `${storyId}.html`)); }
function formatSize(bytes) { return `${Math.round(bytes / 1024 / 1024)} MB`; }

// Watercolor placeholders rotate by index (1-10)
let _placeholderIdx = 0;
function nextWatercolorPlaceholder() {
  _placeholderIdx = (_placeholderIdx % 10) + 1;
  return `watercolor-${_placeholderIdx}.jpg`;
}

// ─── Generate Homepage ───────────────────────────────────────
function generateIndex(site, channels, filesData) {
  const channelCards = channels.map(ch => {
    const count = filesData.channels[ch.id]?.count || 0;
    const s = SEASON_CSS[ch.season];
    const coverFile = `thumbnails/cover-${ch.id}.jpg`;
    const hasCover = fs.existsSync(path.join(PUBLIC_DIR, coverFile));
    const countLabel = ch.dynamic ? 'updating...' : `${count} ${count === 1 ? 'story' : 'stories'}`;
    const prefix = ch.prefix ? ch.prefix.toUpperCase() + '-SERIES' : 'MISC';

    return `
    <a href="channel/${ch.id}.html" class="card-hover block rounded-2xl overflow-hidden bg-white shadow-md hover:shadow-xl">
      <div class="relative aspect-[16/9] overflow-hidden">
        ${hasCover
          ? `<img src="${coverFile}" alt="${esc(ch.name)}" class="absolute inset-0 w-full h-full object-cover" loading="lazy"/>`
          : `<img src="thumbnails/watercolor-${channels.indexOf(ch) + 1}.jpg" alt="${esc(ch.name)}" class="absolute inset-0 w-full h-full object-cover" loading="lazy"/>`}
        <div class="thumb-overlay absolute inset-0"></div>
        <div class="absolute bottom-3 left-3"><span class="stats-badge bg-black/40 text-white text-xs font-label px-2.5 py-1 rounded-full">${countLabel}</span></div>
        <div class="absolute top-3 right-3"><span class="material-symbols-outlined text-white/70" style="font-size:1.5rem">${ch.icon}</span></div>
      </div>
      <div class="p-5" style="background:${s.bgWash1}">
        <div class="flex items-start justify-between mb-2">
          <h3 class="font-headline text-xl font-bold" style="color:${s.primary}">${esc(ch.name)}</h3>
          <span class="text-xs font-label tracking-wider uppercase px-2 py-0.5 rounded-full" style="background:${s.bgWash2};color:${s.primary}">${prefix}</span>
        </div>
        <p class="text-sm leading-relaxed" style="color:${s.primary};opacity:.7">${esc(ch.description)}</p>
      </div>
    </a>`;
  }).join('\n');

  return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
${HTML_HEAD}
<title>${esc(site.title)}</title>
<style>
body{background:radial-gradient(ellipse at top left,#FAF8F5 0%,#F0EDE8 50%,#E8E5E0 100%);min-height:100vh}
${SHARED_CSS}
</style>
</head>
<body class="font-body text-[#1C1C18]">
<header class="relative overflow-hidden">
  <div class="watercolor-wash-header px-6 py-16 md:py-24" style="background:linear-gradient(135deg,#5E6B7F 0%,#8B6F47 40%,#4A7C6F 70%,#6B7F5E 100%)">
    <div class="max-w-5xl mx-auto text-center relative z-10">
      <div class="flex items-center justify-center gap-3 mb-4"><span class="material-symbols-outlined text-white/80" style="font-size:2.5rem">school</span></div>
      <h1 class="font-headline text-4xl md:text-6xl text-white font-bold italic leading-tight mb-4">Waldorf Creator Hub</h1>
      <p class="text-white/80 font-label text-sm md:text-base tracking-[0.25em] uppercase mb-6">Database of Teaching Materials</p>
      <p class="text-white/70 font-body text-base md:text-lg max-w-2xl mx-auto leading-relaxed">${esc(site.description)}</p>
    </div>
  </div>
  <div class="h-8 bg-gradient-to-b from-[#4A7C6F]/10 to-transparent"></div>
</header>
<main class="max-w-6xl mx-auto px-4 md:px-8 py-8 md:py-12">
  <div class="flex items-center gap-3 mb-8">
    <span class="material-symbols-outlined text-[#8B6F47]" style="font-size:1.5rem">subscriptions</span>
    <h2 class="font-headline text-2xl text-[#8B6F47]">Teaching Channels</h2>
    <div class="flex-1 h-px bg-[#D1C4B7]/50"></div>
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
${channelCards}
  </div>
  <div class="flex justify-center gap-3 py-10 opacity-30">
    <span class="material-symbols-outlined text-[#8B6F47] text-sm">eco</span>
    <span class="material-symbols-outlined text-[#4A7C6F] text-sm">sunny</span>
    <span class="material-symbols-outlined text-[#6B7F5E] text-sm">park</span>
    <span class="material-symbols-outlined text-[#5E6B7F] text-sm">ac_unit</span>
  </div>
  <section class="max-w-3xl mx-auto text-center mb-8">
    <h2 class="font-headline text-xl text-[#8B6F47] mb-4 italic">About This Hub</h2>
    <p class="text-[15px] leading-relaxed text-[#4E453B]">WaldorfCreatorHubDatabase \u662f\u83ef\u5fb7\u798f\u6559\u5b78\u7d20\u6750\u7684\u516c\u958b\u5c55\u793a\u5e73\u53f0\u3002\u6240\u6709\u7d20\u6750\u7531 TeacherOS AI \u5354\u4f5c\u7cfb\u7d71\u6bcf\u65e5\u751f\u6210\uff0c\u5305\u542b\u9ed1\u677f\u756b\u3001\u6545\u4e8b\u6587\u672c\u3001\u6559\u5e2b\u8aaa\u66f8\u7a3f\u8207\u6559\u5b78\u6307\u5f15\u3002</p>
  </section>
</main>
<footer class="bg-[#F0EDE8] border-t border-[#D1C4B7]/30 py-8">
  <div class="max-w-4xl mx-auto flex flex-col items-center gap-3 px-6 text-center">
    <p class="font-headline italic text-lg text-[#8B6F47]">\u5b9c\u862d\u6148\u5fc3\u83ef\u5fb7\u798f\u5be6\u9a57\u5b78\u6821</p>
    <p class="text-[#7B6B60] text-xs tracking-widest uppercase">Powered by TeacherOS &middot; Updated Daily</p>
  </div>
</footer>
</body>
</html>`;
}

// ─── Curriculum Position (ancient-myths interlude ordering) ──
// TW island interludes slot between AM blocks in curriculum order.
function getCurriculumPosition(storyId) {
  const TW = { TW01: 8, TW02: 13, TW03: 19, TW04: 25 };
  if (TW[storyId]) return TW[storyId];
  const m = storyId.match(/^AM(\d+)$/);
  if (!m) return 0;
  const n = parseInt(m[1], 10);
  if (n <= 7) return n;        // AM001-007 → 1-7
  if (n <= 11) return n + 1;   // AM008-011 → 9-12
  if (n <= 16) return n + 2;   // AM012-016 → 14-18
  return n + 3;                // AM017-021 → 20-24
}

// ─── Generate Channel Page ───────────────────────────────────
function generateChannelPage(channel, files) {
  const s = SEASON_CSS[channel.season];
  let sorted;
  if (channel.id === 'ancient-myths') {
    sorted = [...files].sort((a, b) => getCurriculumPosition(b.storyId) - getCurriculumPosition(a.storyId));
  } else if (channel.sort === 'storyId') {
    sorted = [...files].sort((a, b) => a.storyId.localeCompare(b.storyId, undefined, { numeric: true }));
  } else {
    sorted = [...files].sort((a, b) => (b.modifiedTime || '').localeCompare(a.modifiedTime || ''));
  }

  // Reset placeholder rotation for each channel
  _placeholderIdx = 0;

  const storyCards = sorted.map(file => {
    const hasThumb = thumbExists(file.storyId);
    const hasHtml = storyHtmlExists(file.storyId);
    const placeholderFile = nextWatercolorPlaceholder();
    // Link to local HTML if deployed, otherwise Drive
    const href = hasHtml ? storyUrl(file.storyId) : `https://drive.google.com/file/d/${file.fileId}/view`;
    const target = hasHtml ? '' : ' target="_blank" rel="noopener"';
    return `
    <a href="${href}"${target} class="card-hover block rounded-xl overflow-hidden bg-white shadow-sm">
      <div class="relative aspect-[16/10] overflow-hidden">
        ${hasThumb
          ? `<img src="../thumbnails/${file.storyId}.jpg" alt="" class="absolute inset-0 w-full h-full object-cover" loading="lazy"/>`
          : `<img src="../thumbnails/${placeholderFile}" alt="" class="absolute inset-0 w-full h-full object-cover" loading="lazy"/>`}
        <div class="thumb-overlay absolute inset-0"></div>
        <div class="absolute top-2.5 left-2.5"><span class="bg-[${s.primary}] text-white text-xs font-label font-semibold px-2 py-0.5 rounded">${esc(file.storyId)}</span></div>
      </div>
      <div class="p-4">
        <h3 class="font-headline text-base font-bold leading-snug mb-1" style="color:${s.onSurface}">${esc(file.title)}</h3>
        <p class="text-xs" style="color:${s.onSurfaceVariant}">${formatSize(file.size)}</p>
      </div>
    </a>`;
  }).join('\n');

  const prefix = channel.prefix ? channel.prefix.toUpperCase() + '-Series' : 'Collection';

  return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
${HTML_HEAD}
<title>${esc(channel.name)} \u2014 WaldorfCreatorHubDatabase</title>
<style>
:root{--primary:${s.primary};--secondary:${s.secondary};--bg-wash-1:${s.bgWash1};--bg-wash-2:${s.bgWash2};--bg-wash-3:${s.bgWash3};--on-surface:${s.onSurface};--on-surface-variant:${s.onSurfaceVariant};--outline-variant:${s.outlineVariant}}
body{background:${s.bodyGradient};min-height:100vh}
${SHARED_CSS}
</style>
</head>
<body class="font-body" style="color:${s.onSurface}">
<header class="relative overflow-hidden">
  <div class="watercolor-wash-header px-6 py-12 md:py-16" style="background:${s.gradient}">
    <div class="max-w-5xl mx-auto relative z-10">
      <a href="../index.html" class="inline-flex items-center gap-1.5 text-white/60 hover:text-white/90 text-sm font-label mb-6 transition-colors">
        <span class="material-symbols-outlined" style="font-size:1.2rem">arrow_back</span>All Channels</a>
      <div class="flex items-center gap-4 mb-3">
        <span class="material-symbols-outlined text-white/80" style="font-size:2.5rem">${channel.icon}</span>
        <div>
          <h1 class="font-headline text-3xl md:text-5xl text-white font-bold italic leading-tight">${esc(channel.name)}</h1>
          <p class="text-white/60 font-label text-sm tracking-[0.15em] uppercase mt-1">${prefix} &middot; ${files.length} Stories</p>
        </div>
      </div>
      <p class="text-white/70 font-body text-base max-w-2xl leading-relaxed mt-4">${esc(channel.description)}</p>
    </div>
  </div>
  <div class="h-6 bg-gradient-to-b from-[${s.secondary}]/10 to-transparent"></div>
</header>
<main class="max-w-6xl mx-auto px-4 md:px-8 py-8">
  <div class="flex items-center justify-between mb-6">
    <p class="text-sm font-label" style="color:${s.onSurfaceVariant}"><span class="font-semibold">${files.length}</span> stories &middot; ${channel.sort === 'storyId' || channel.id === 'ancient-myths' ? 'curriculum order' : 'latest first'}</p>
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
${storyCards}
  </div>
</main>
<footer style="background:${s.bgWash1}" class="border-t py-8 mt-8" style="border-color:${s.outlineVariant}30">
  <div class="max-w-4xl mx-auto flex flex-col items-center gap-3 px-6 text-center">
    <a href="../index.html" class="inline-flex items-center gap-1.5 text-sm font-label transition-colors" style="color:${s.primary}">
      <span class="material-symbols-outlined" style="font-size:1.2rem">arrow_back</span>Back to All Channels</a>
    <p class="font-headline italic text-lg" style="color:${s.primary}">\u5b9c\u862d\u6148\u5fc3\u83ef\u5fb7\u798f\u5be6\u9a57\u5b78\u6821</p>
    <p class="text-xs tracking-widest uppercase" style="color:${s.secondary}">Powered by TeacherOS &middot; Updated Daily</p>
  </div>
</footer>
</body>
</html>`;
}

// ─── Deploy Manifest ─────────────────────────────────────────
function writeManifest(channels, filesData) {
  const summary = {};
  for (const ch of channels) {
    const files = filesData.channels[ch.id]?.files || [];
    const latest = files.length
      ? files.reduce((a, b) => (a.modifiedTime || '') > (b.modifiedTime || '') ? a : b)
      : null;
    summary[ch.id] = {
      name: ch.name,
      count: files.length,
      latest: latest ? latest.storyId : null,
    };
  }

  const manifest = {
    deployedAt: new Date().toISOString(),
    syncedAt: filesData.generatedAt || null,
    channels: summary,
  };

  const manifestPath = path.join(PUBLIC_DIR, 'deploy-manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  console.log('Generated: public/deploy-manifest.json');
  return manifest;
}

// ─── Main ────────────────────────────────────────────────────
function main() {
  const channelsData = JSON.parse(fs.readFileSync(CHANNELS_PATH, 'utf8'));
  const filesData = JSON.parse(fs.readFileSync(FILES_PATH, 'utf8'));
  const { site } = channelsData;

  // Build channel objects from files.json channelList (populated by sync-drive)
  // Sort by prefix order: A → AM → B → I → O
  const PREFIX_ORDER = ['A', 'AM', 'B', 'I', 'O'];
  const channels = (filesData.channelList || []).map(ch => {
    const cfg = channelsData.channels[ch.id] || {};
    return {
      id: ch.id,
      name: ch.name,
      description: ch.description || '',
      prefix: ch.prefix || '',
      season: ch.season || 'winter',
      icon: ch.icon || 'science',
      dynamic: ch.isNew || false,
      sort: cfg.sort || 'modifiedTime',
    };
  }).sort((a, b) => {
    const ia = PREFIX_ORDER.indexOf(a.prefix.toUpperCase());
    const ib = PREFIX_ORDER.indexOf(b.prefix.toUpperCase());
    return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib);
  });

  // Generate index.html
  const indexHtml = generateIndex(site, channels, filesData);
  fs.writeFileSync(path.join(PUBLIC_DIR, 'index.html'), indexHtml);
  console.log('Generated: public/index.html');

  // Generate channel pages
  fs.mkdirSync(path.join(PUBLIC_DIR, 'channel'), { recursive: true });
  for (const channel of channels) {
    const files = filesData.channels[channel.id]?.files || [];
    const html = generateChannelPage(channel, files);
    const outPath = path.join(PUBLIC_DIR, 'channel', `${channel.id}.html`);
    fs.writeFileSync(outPath, html);
    console.log(`Generated: public/channel/${channel.id}.html (${files.length} stories)`);
  }

  // Write deploy manifest (deployed to Firebase as /deploy-manifest.json)
  writeManifest(channels, filesData);

  console.log('\nSite generation complete!');
}

main();
