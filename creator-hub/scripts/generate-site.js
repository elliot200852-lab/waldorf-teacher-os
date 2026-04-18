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
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=JetBrains+Mono:wght@400;500&family=Noto+Serif+TC:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet"/>
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

// ─── Almanac Mode (homepage) ─────────────────────────────────
// Editorial archive layout: two-column (daily feed + series index cards)
// Design source: Waldorf Creator Hub design bundle (2026-04-18).

const GLYPH_SVG = {
  leaf: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 38 C 10 20, 24 10, 38 10 C 38 24, 28 38, 10 38 Z"/><path d="M10 38 L 32 16"/></svg>',
  sprout: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M24 40 V 22"/><path d="M24 22 C 24 14, 16 12, 10 14 C 12 20, 18 24, 24 22 Z"/><path d="M24 22 C 24 16, 32 14, 38 16 C 36 22, 30 26, 24 22 Z"/></svg>',
  column: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 10 H 34"/><path d="M12 14 H 36"/><path d="M16 14 V 36"/><path d="M32 14 V 36"/><path d="M24 14 V 36" stroke-dasharray="2 3"/><path d="M12 36 H 36"/><path d="M10 40 H 38"/></svg>',
  diamond: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M24 6 L 42 24 L 24 42 L 6 24 Z"/><path d="M24 14 L 34 24 L 24 34 L 14 24 Z"/></svg>',
  star: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="24" cy="24" r="2" fill="currentColor"/><path d="M24 8 V 14"/><path d="M24 34 V 40"/><path d="M8 24 H 14"/><path d="M34 24 H 40"/><path d="M12 12 L 16 16"/><path d="M32 32 L 36 36"/><path d="M36 12 L 32 16"/><path d="M16 32 L 12 36"/></svg>',
  wheat: '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><path d="M24 42 V 14"/><path d="M24 14 C 20 14, 16 12, 16 8 C 20 8, 24 10, 24 14"/><path d="M24 14 C 28 14, 32 12, 32 8 C 28 8, 24 10, 24 14"/><path d="M24 22 C 20 22, 16 20, 16 16 C 20 16, 24 18, 24 22"/><path d="M24 22 C 28 22, 32 20, 32 16 C 28 16, 24 18, 24 22"/><path d="M24 30 C 20 30, 16 28, 16 24 C 20 24, 24 26, 24 30"/><path d="M24 30 C 28 30, 32 28, 32 24 C 28 24, 24 26, 24 30"/></svg>',
};

// Per-channel metadata for almanac view (grade / glyph). Add entries as new channels appear.
const CHANNEL_META = {
  'taiwan-stories':       { grade: '五年級', glyph: 'leaf' },
  'ancient-myths':        { grade: '五年級', glyph: 'column' },
  'botany':               { grade: '五年級', glyph: 'sprout' },
  'island-myths-3rd':     { grade: '三年級', glyph: 'wheat' },
  'shanhaijing-3rd':      { grade: '三年級', glyph: 'diamond' },
  'taiwan-literature-9d': { grade: '九年級', glyph: 'star' },
};
const CHANNEL_META_DEFAULT = { grade: '', glyph: 'leaf' };

const SEASON_CHINESE = { spring: '春', summer: '夏', autumn: '秋', winter: '冬' };

// Accent colour used for card hover shadow + feed date
const SEASON_ACCENT = {
  spring: '#3a5a3a',
  summer: '#8b3a2e',
  autumn: '#8b6f47',
  winter: '#1e2a3a',
};

function cnNum(n) {
  const d = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
  if (n < 10) return d[n];
  if (n === 10) return '十';
  if (n < 20) return '十' + d[n - 10];
  if (n < 100) {
    const t = Math.floor(n / 10), o = n % 10;
    return d[t] + '十' + (o === 0 ? '' : d[o]);
  }
  return String(n);
}

function getRecentUpdates(filesData, channels, limit = 7) {
  const all = [];
  for (const ch of channels) {
    const files = filesData.channels[ch.id]?.files || [];
    for (const f of files) {
      all.push({
        mtime: f.modifiedTime || '',
        dateLabel: f.modifiedTime
          ? (() => { const d = new Date(f.modifiedTime); return `${d.getMonth() + 1}.${d.getDate()}`; })()
          : '—',
        seriesCode: (ch.prefix || 'MISC').toUpperCase(),
        channelId: ch.id,
        season: ch.season,
        title: f.title || f.storyId,
        storyId: f.storyId,
        type: '單元',
      });
    }
  }
  all.sort((a, b) => (b.mtime || '').localeCompare(a.mtime || ''));
  return all.slice(0, limit);
}

function generateIndex(site, channels, filesData) {
  const updates = getRecentUpdates(filesData, channels, 7);
  const today = new Date();
  const weekdayNames = ['日', '一', '二', '三', '四', '五', '六'];
  const dateStr = `${today.getFullYear()} 年 ${today.getMonth() + 1} 月 ${today.getDate()} 日`;
  const weekStr = `週${weekdayNames[today.getDay()]}`;
  // Simple rolling issue number from the site's epoch (Spring 2024 launch)
  const epoch = new Date('2024-03-20T00:00:00Z');
  const issueNo = Math.max(1, Math.floor((today - epoch) / (7 * 24 * 60 * 60 * 1000)));

  const totalStories = channels.reduce((sum, ch) => sum + (filesData.channels[ch.id]?.files?.length || 0), 0);
  const seriesCount = channels.length;

  const updatesHtml = updates.map((u, i) => `
      <li class="feed-item${i === 0 ? ' feed-item--first' : ''}" style="--accent:${SEASON_ACCENT[u.season] || '#3a5a3a'}">
        <div class="feed-row">
          <div class="feed-date">${esc(u.dateLabel)}</div>
          <div class="feed-body">
            <div class="feed-label">${esc(u.seriesCode)}-Series · ${esc(u.type)}</div>
            <a class="feed-title" href="stories/${esc(u.storyId)}.html">${esc(u.title)}</a>
          </div>
        </div>
      </li>`).join('\n');

  const cardsHtml = channels.map((ch, i) => {
    const meta = CHANNEL_META[ch.id] || CHANNEL_META_DEFAULT;
    const season = ch.season || 'winter';
    const accent = SEASON_ACCENT[season];
    const count = filesData.channels[ch.id]?.files?.length || 0;
    const code = ch.prefix ? `${ch.prefix.toUpperCase()}-SERIES` : 'MISC';
    const seasonCN = SEASON_CHINESE[season] || '';
    const thumbCandidates = [
      `thumbnails/cover-${ch.id}.jpg`,
      `thumbnails/${ch.id}-default.jpg`,
      `thumbnails/others-default.jpg`,
    ];
    const thumbSrc = thumbCandidates.find(p => fs.existsSync(path.join(PUBLIC_DIR, p))) || thumbCandidates[2];
    return `
      <a class="series-card" href="channel/${ch.id}.html" style="--accent:${accent};--delay:${i * 120}ms">
        <div class="card-top">
          <span class="card-code">${esc(code)}</span>
          <span class="card-glyph" aria-hidden="true">${GLYPH_SVG[meta.glyph] || GLYPH_SVG.leaf}</span>
        </div>
        <div class="card-rule"></div>
        <div class="card-body">
          <div class="card-text">
            <h3 class="card-title">${esc(ch.name)}</h3>
            <div class="card-grade">${esc(meta.grade)}${seasonCN ? ' · ' + seasonCN + '之章' : ''}</div>
            <p class="card-subtitle">${esc(ch.description || '')}</p>
          </div>
          <div class="card-thumb-wrap">
            <img class="card-thumb" src="${thumbSrc}" alt="" loading="lazy"/>
          </div>
        </div>
        <div class="card-footer">
          <span>${String(count).padStart(2, '0')} 單元</span>
          <span class="card-arrow">進入 <span class="card-arrow-sym">→</span></span>
        </div>
      </a>`;
  }).join('\n');

  return `<!DOCTYPE html>
<html lang="zh-TW" data-theme="spring" data-density="loose" data-card="outlined" data-motion="strong">
<head>
${HTML_HEAD}
<title>${esc(site.title)} · 華德福教材年鑑</title>
<style>
:root {
  --bg: #f5f0e5; --paper: #faf6ec; --fg: #2d3b2d; --muted: #6b6b5a; --moss: #8a9a7b;
  --shadow-emboss: 0 1px 0 rgba(255,255,255,0.55), 0 1px 2px rgba(45,59,45,0.08);
  --shadow-strong: 0 1px 0 rgba(255,255,255,0.6), 0 2px 3px rgba(45,59,45,0.18), 0 4px 12px rgba(45,59,45,0.08);
}
html[data-theme="autumn"] {
  --bg: #f0e8d8; --paper: #f7f0df; --fg: #3a2820; --muted: #7a5a42; --moss: #c4a57b;
  --shadow-emboss: 0 1px 0 rgba(255,248,232,0.55), 0 1px 2px rgba(58,40,32,0.1);
  --shadow-strong: 0 1px 0 rgba(255,248,232,0.6), 0 2px 3px rgba(58,40,32,0.2), 0 4px 12px rgba(58,40,32,0.1);
}
html[data-theme="dark"] {
  --bg: #1a1e1a; --paper: #232823; --fg: #e8e2d2; --muted: #aaa598; --moss: #c4a57b;
  --shadow-emboss: 0 1px 0 rgba(0,0,0,0.55), 0 1px 2px rgba(0,0,0,0.6);
  --shadow-strong: 0 1px 0 rgba(0,0,0,0.6), 0 2px 3px rgba(0,0,0,0.7), 0 0 12px rgba(232,226,210,0.06);
}
html[data-density="loose"] { --pad-y: 72px; --grid-gap: 32px; --card-pad: 24px; }
html[data-density="tight"] { --pad-y: 40px; --grid-gap: 16px; --card-pad: 18px; }

* , *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg); color: var(--fg);
  font-family: "Noto Serif TC", "EB Garamond", serif;
  font-feature-settings: "palt";
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
::selection { background: var(--fg); color: var(--bg); }
a { color: inherit; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(24px);} to { opacity: 1; transform: translateY(0);} }

.topnav {
  position: sticky; top: 0; z-index: 20;
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 32px;
  background: color-mix(in srgb, var(--bg) 92%, transparent);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  border-bottom: 0.5px solid var(--fg);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 12px; letter-spacing: 0.25em; color: var(--muted); text-transform: uppercase;
  text-shadow: var(--shadow-emboss);
}
.topnav-links { display: flex; gap: 22px; }

.page { padding: var(--pad-y) 48px; max-width: 1240px; margin: 0 auto; }
@media (max-width: 768px) { .page { padding: 48px 16px; } }

.masthead { border-bottom: 1px solid var(--fg); padding-bottom: 32px; margin-bottom: 56px; }
.masthead-meta { display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; flex-wrap: wrap; font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12px; letter-spacing: 0.3em; color: var(--muted); text-transform: uppercase; text-shadow: var(--shadow-emboss); }
.masthead-title {
  font-family: "Cormorant Garamond", "Noto Serif TC", serif;
  font-style: italic; font-weight: 500;
  font-size: clamp(38px, 5vw, 72px);
  line-height: 1.05; margin: 22px 0 14px;
  color: var(--fg); letter-spacing: -0.01em; text-align: center;
  text-shadow: var(--shadow-strong);
}
.masthead-title .masthead-title-zh {
  font-family: "Noto Serif TC", serif; font-style: normal; font-weight: 600;
  margin-left: 0.25em; letter-spacing: 0.02em;
}
.masthead-sub { display: flex; justify-content: center; align-items: center; gap: 16px; font-family: "Cormorant Garamond", serif; font-style: italic; font-size: 22px; color: var(--muted); text-shadow: var(--shadow-emboss); }
.masthead-sub .rule { flex: 1; height: 1px; background: var(--fg); opacity: 0.3; max-width: 120px; }
.masthead-desc { text-align: center; font-family: "Noto Serif TC", serif; font-size: 16px; color: var(--fg); opacity: 0.85; margin: 18px auto 0; max-width: 580px; line-height: 1.85; text-shadow: var(--shadow-emboss); }

.layout { display: grid; grid-template-columns: 300px 1fr; gap: 52px; }
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; gap: 32px; }
  .rail { position: static !important; }
}
.rail { position: sticky; top: 80px; align-self: start; }
.rail-label, .idx-label { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12px; letter-spacing: 0.3em; color: var(--muted); text-transform: uppercase; padding-bottom: 14px; border-bottom: 1px solid var(--fg); margin-bottom: 22px; text-shadow: var(--shadow-emboss); }
.feed { list-style: none; padding: 0; margin: 0; }
.feed-item { margin-bottom: 22px; padding-bottom: 22px; border-bottom: 0.5px dashed var(--fg); opacity: 0.88; }
.feed-item--first { opacity: 1; }
.feed-item:last-child { border-bottom: none; }
.feed-row { display: flex; gap: 14px; align-items: baseline; }
.feed-date { font-family: "Cormorant Garamond", serif; font-style: italic; font-size: 28px; font-weight: 500; color: var(--accent); width: 56px; flex-shrink: 0; text-shadow: var(--shadow-strong); }
.feed-body { flex: 1; min-width: 0; }
.feed-label { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 11px; letter-spacing: 0.18em; color: var(--muted); text-transform: uppercase; margin-bottom: 5px; text-shadow: var(--shadow-emboss); }
.feed-title { font-family: "Noto Serif TC", serif; font-size: 17px; font-weight: 500; line-height: 1.55; color: var(--fg); text-decoration: none; display: inline-block; text-shadow: var(--shadow-emboss); }
.feed-title:hover { text-decoration: underline; text-underline-offset: 3px; }

.idx-bar { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 30px; gap: 16px; flex-wrap: wrap; }
.idx-count { font-family: "Cormorant Garamond", serif; font-style: italic; font-size: 17px; color: var(--muted); text-shadow: var(--shadow-emboss); }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--grid-gap); }
.series-card {
  text-decoration: none; color: inherit;
  background: var(--paper); border: 1px solid var(--fg);
  padding: var(--card-pad); position: relative; display: block;
  transition: transform 400ms cubic-bezier(.2,.7,.2,1), box-shadow 400ms cubic-bezier(.2,.7,.2,1);
  opacity: 0; transform: translateY(16px);
  animation: fadeUp 500ms cubic-bezier(.2,.7,.2,1) forwards;
  animation-delay: var(--delay, 0ms);
  box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.04);
}
html[data-theme="dark"] .series-card { box-shadow: 0 1px 2px rgba(0,0,0,0.3), 0 2px 8px rgba(0,0,0,0.2); }
html[data-motion="off"] .series-card { animation: none; opacity: 1; transform: none; transition: none; }
html[data-motion="subtle"] .series-card { animation-duration: 260ms; }
.series-card:hover { transform: translateY(-4px); box-shadow: 6px 6px 0 0 var(--accent), 0 8px 20px rgba(0,0,0,0.1); }
html[data-motion="off"] .series-card:hover { transform: none; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }

html[data-card="filled"] .series-card { background: var(--accent); color: #f5f0e5; border-color: transparent; }
html[data-card="filled"] .series-card .card-rule { background: #f5f0e5; opacity: 0.4; }
html[data-card="filled"] .card-glyph { color: #f5f0e5; }
html[data-card="minimal"] .series-card { background: transparent; border: none; border-top: 2px solid var(--accent); padding-left: 0; padding-right: 0; box-shadow: none; }
html[data-card="minimal"] .series-card:hover { box-shadow: none; transform: translateY(-2px); }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.card-code { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 11px; letter-spacing: 0.25em; opacity: 0.75; text-shadow: var(--shadow-emboss); }
.card-glyph { display: inline-flex; width: 26px; height: 26px; color: var(--accent); filter: drop-shadow(0 1px 1px rgba(45,59,45,0.12)); }
.card-glyph svg { width: 100%; height: 100%; }
.card-rule { height: 1px; background: currentColor; opacity: 0.2; margin-bottom: 20px; }

/* Layout (b): 2/3 text-left, 1/3 image-right */
.card-body { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; align-items: start; margin-bottom: 18px; }
.card-text { min-width: 0; }
.card-title { font-family: "Noto Serif TC", serif; font-size: 26px; font-weight: 600; margin: 0 0 8px; letter-spacing: 0.02em; line-height: 1.2; text-shadow: var(--shadow-strong); }
.card-grade { font-family: "Cormorant Garamond", serif; font-style: italic; font-size: 16px; opacity: 0.75; margin-bottom: 12px; text-shadow: var(--shadow-emboss); }
.card-subtitle { font-family: "Noto Serif TC", serif; font-size: 15px; line-height: 1.75; margin: 0; opacity: 0.82; text-shadow: var(--shadow-emboss); }
html[data-card="filled"] .card-subtitle { opacity: 0.94; }
.card-thumb-wrap { aspect-ratio: 3 / 4; width: 100%; overflow: hidden; border: 1px solid currentColor; background: var(--bg); box-shadow: 0 2px 6px rgba(0,0,0,0.12); }
html[data-card="minimal"] .card-thumb-wrap { border-color: var(--accent); }
.card-thumb { width: 100%; height: 100%; object-fit: cover; display: block; }

.card-footer { display: flex; justify-content: space-between; align-items: center; font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12px; letter-spacing: 0.18em; opacity: 0.8; text-transform: uppercase; text-shadow: var(--shadow-emboss); padding-top: 14px; border-top: 0.5px solid currentColor; }
.card-footer { border-top-color: color-mix(in srgb, currentColor 20%, transparent); }
.card-arrow { display: inline-flex; align-items: center; gap: 6px; }
.card-arrow-sym { transition: transform 300ms; display: inline-block; }
.series-card:hover .card-arrow-sym { transform: translateX(4px); }

.about { max-width: 640px; margin: 88px auto 0; text-align: center; font-family: "Noto Serif TC", serif; font-size: 16px; line-height: 1.9; color: var(--fg); opacity: 0.85; border-top: 0.5px solid var(--fg); padding-top: 36px; text-shadow: var(--shadow-emboss); }
.about-title { font-family: "Cormorant Garamond", serif; font-style: italic; font-size: 24px; margin: 0 0 14px; opacity: 1; text-shadow: var(--shadow-strong); }

.colophon { margin-top: 96px; border-top: 1px solid var(--fg); padding-top: 28px; display: flex; justify-content: space-between; font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12px; letter-spacing: 0.2em; color: var(--muted); text-transform: uppercase; flex-wrap: wrap; gap: 14px; text-shadow: var(--shadow-emboss); }
.colophon-motto { font-family: "Cormorant Garamond", serif; font-style: italic; text-transform: none; letter-spacing: normal; font-size: 17px; }

/* Tweaks panel */
.tweaks-btn { position: fixed; top: 16px; right: 16px; z-index: 30; width: 40px; height: 40px; border-radius: 50%; background: var(--paper); border: 1px solid var(--fg); color: var(--fg); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 18px; transition: transform 400ms ease; }
.tweaks-btn:hover { transform: rotate(60deg); }
.tweaks-backdrop { position: fixed; inset: 0; z-index: 35; background: rgba(20,24,20,0.3); opacity: 0; pointer-events: none; transition: opacity 300ms; }
.tweaks-backdrop.open { opacity: 1; pointer-events: auto; }
.tweaks-panel { position: fixed; top: 0; right: 0; bottom: 0; z-index: 40; width: min(320px, 88vw); background: var(--paper); color: var(--fg); border-left: 1px solid var(--fg); padding: 32px 28px; overflow-y: auto; transform: translateX(100%); transition: transform 400ms cubic-bezier(.2,.7,.2,1); box-shadow: -12px 0 40px rgba(0,0,0,0.08); }
.tweaks-panel.open { transform: translateX(0); }
.tweaks-title { font-family: "Cormorant Garamond", serif; font-style: italic; font-size: 22px; margin: 0 0 6px; }
.tweaks-subtitle { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 9px; letter-spacing: 0.25em; color: var(--muted); text-transform: uppercase; margin-bottom: 28px; }
.tweaks-group { margin-bottom: 24px; }
.tweaks-label { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 9px; letter-spacing: 0.25em; color: var(--muted); text-transform: uppercase; margin-bottom: 10px; }
.tweaks-options { display: flex; gap: 6px; flex-wrap: wrap; }
.tweaks-opt { font-family: "Noto Serif TC", serif; font-size: 13px; padding: 6px 12px; border: 1px solid var(--fg); background: transparent; color: var(--fg); cursor: pointer; transition: all 200ms; }
.tweaks-opt:hover { background: color-mix(in srgb, var(--fg) 10%, transparent); }
.tweaks-opt.active { background: var(--fg); color: var(--paper); }
.tweaks-close { position: absolute; top: 16px; right: 16px; background: none; border: none; color: var(--muted); cursor: pointer; font-size: 22px; line-height: 1; padding: 4px 8px; }
</style>
</head>
<body>
<nav class="topnav">
  <span>Waldorf Creator Hub · WCH</span>
  <span class="topnav-links"><span>系列</span><span>每日</span><span>關於</span></span>
</nav>

<button class="tweaks-btn" id="tweaks-btn" title="Tweaks" aria-label="開啟設定">⚙</button>
<div class="tweaks-backdrop" id="tweaks-backdrop"></div>
<aside class="tweaks-panel" id="tweaks-panel" aria-hidden="true">
  <button class="tweaks-close" id="tweaks-close" aria-label="關閉">×</button>
  <h3 class="tweaks-title">Tweaks</h3>
  <div class="tweaks-subtitle">Customise your view</div>
  <div class="tweaks-group"><div class="tweaks-label">Theme · 色彩主題</div>
    <div class="tweaks-options" data-tweak="theme">
      <button class="tweaks-opt" data-val="spring">春（紙色）</button>
      <button class="tweaks-opt" data-val="autumn">秋</button>
      <button class="tweaks-opt" data-val="dark">夜</button>
    </div></div>
  <div class="tweaks-group"><div class="tweaks-label">Density · 排版密度</div>
    <div class="tweaks-options" data-tweak="density">
      <button class="tweaks-opt" data-val="loose">寬鬆</button>
      <button class="tweaks-opt" data-val="tight">緊密</button>
    </div></div>
  <div class="tweaks-group"><div class="tweaks-label">Card Style · 卡片樣式</div>
    <div class="tweaks-options" data-tweak="card">
      <button class="tweaks-opt" data-val="outlined">邊框</button>
      <button class="tweaks-opt" data-val="filled">填色</button>
      <button class="tweaks-opt" data-val="minimal">極簡</button>
    </div></div>
  <div class="tweaks-group"><div class="tweaks-label">Motion · 動態</div>
    <div class="tweaks-options" data-tweak="motion">
      <button class="tweaks-opt" data-val="strong">強</button>
      <button class="tweaks-opt" data-val="subtle">弱</button>
      <button class="tweaks-opt" data-val="off">關</button>
    </div></div>
</aside>

<div class="page">
  <header class="masthead">
    <div class="masthead-meta">
      <span>No. ${issueNo} · ${dateStr} · ${weekStr}</span>
      <span>每日更新 · 建於 2024 年春分</span>
    </div>
    <h1 class="masthead-title">CreatorHub <span class="masthead-title-zh">教學資源中心</span></h1>
    <div class="masthead-sub"><span class="rule"></span><span>Almanac of the Seasons &amp; Stories</span><span class="rule"></span></div>
    <p class="masthead-desc">${esc(site.description || '一本為教師而編的活節氣書——收錄黑板畫、故事文本、身體練習與教學筆記。')}</p>
  </header>

  <div class="layout">
    <aside class="rail">
      <div class="rail-label">每日更新 · Daily</div>
      <ul class="feed">${updatesHtml || '<li class="feed-item">尚無更新</li>'}</ul>
    </aside>
    <main>
      <div class="idx-bar">
        <div class="idx-label">課程系列 · Index</div>
        <div class="idx-count">${cnNum(seriesCount)}系列 · 共 ${totalStories} 單元</div>
      </div>
      <div class="card-grid">${cardsHtml}</div>
    </main>
  </div>

  <section class="about">
    <h2 class="about-title">About This Hub</h2>
    <p>WaldorfCreatorHubDatabase 是華德福教學素材的公開展示平台。所有素材由 TeacherOS AI 協作系統每日生成，包含黑板畫、故事文本、教師說書稿與教學指引。</p>
  </section>

  <footer class="colophon">
    <span>Waldorf Creator Hub · Vol. IV</span>
    <span class="colophon-motto">Per aspera ad astra</span>
    <span>MMXXVI · 宜蘭慈心華德福實驗學校</span>
  </footer>
</div>

<script>
(function(){
  const KEY = 'wch-tweaks-v2';
  const defaults = { theme: 'spring', density: 'loose', card: 'outlined', motion: 'strong' };
  let state;
  try { state = Object.assign({}, defaults, JSON.parse(localStorage.getItem(KEY) || 'null') || {}); }
  catch (_) { state = Object.assign({}, defaults); }

  function apply() {
    const h = document.documentElement;
    h.setAttribute('data-theme', state.theme);
    h.setAttribute('data-density', state.density);
    h.setAttribute('data-card', state.card);
    h.setAttribute('data-motion', state.motion);
    document.querySelectorAll('[data-tweak]').forEach(function(group){
      const key = group.dataset.tweak;
      group.querySelectorAll('.tweaks-opt').forEach(function(btn){
        btn.classList.toggle('active', btn.dataset.val === state[key]);
      });
    });
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) {}
  }
  function openPanel(){ document.getElementById('tweaks-panel').classList.add('open'); document.getElementById('tweaks-backdrop').classList.add('open'); document.getElementById('tweaks-panel').setAttribute('aria-hidden','false'); }
  function closePanel(){ document.getElementById('tweaks-panel').classList.remove('open'); document.getElementById('tweaks-backdrop').classList.remove('open'); document.getElementById('tweaks-panel').setAttribute('aria-hidden','true'); }

  document.getElementById('tweaks-btn').addEventListener('click', openPanel);
  document.getElementById('tweaks-close').addEventListener('click', closePanel);
  document.getElementById('tweaks-backdrop').addEventListener('click', closePanel);
  document.querySelectorAll('[data-tweak] .tweaks-opt').forEach(function(btn){
    btn.addEventListener('click', function(){
      const key = btn.closest('[data-tweak]').dataset.tweak;
      state[key] = btn.dataset.val; apply();
    });
  });
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') closePanel(); });
  apply();
})();
</script>
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

// ─── Channel Palette (magazine-feature layout) ───────────────
// Maps a season to the paper-based palette used by the channel page.
// Keeps visual parity with index.html's almanac design while varying
// the accent per season.
const CHANNEL_PALETTE = {
  spring: { bg: '#f5f0e5', paper: '#faf6ec', fg: '#2d3b2d', muted: '#6b6b5a', accent: '#3a5a3a', ink: '#1f2a1f' },
  summer: { bg: '#fff7ea', paper: '#fbf0dc', fg: '#3a2418', muted: '#7a5a4a', accent: '#8b3a2e', ink: '#2a1810' },
  autumn: { bg: '#f0e8d8', paper: '#f7f0df', fg: '#3a2820', muted: '#8a6a52', accent: '#8b6f47', ink: '#2d1f18' },
  winter: { bg: '#eef1f5', paper: '#f7f9fc', fg: '#1c1e22', muted: '#5a6470', accent: '#3a4a5e', ink: '#10141a' },
};

const SEASON_LABEL_CN = { spring: '春之章', summer: '夏之章', autumn: '秋之章', winter: '冬之章' };

// Parse a storyId into its letter prefix + numeric suffix.
// e.g. "AM007" → { prefix: 'AM', num: 7 }; "TW01" → { prefix: 'TW', num: 1 }.
function parseStoryId(storyId) {
  const m = (storyId || '').match(/^([A-Za-z]+)(\d+)?/);
  if (!m) return { prefix: 'OTHER', num: null };
  return { prefix: m[1].toUpperCase(), num: m[2] ? parseInt(m[2], 10) : null };
}

// Check whether a file matches a block's `match` predicate.
// Supported predicates:
//   { prefix: "A" }                      — all stories with prefix A
//   { prefix: "AM", from: 1, to: 7 }     — AM001..AM007
//   { ids: ["TW01", "TW02"] }            — explicit storyId list
function matchesBlock(file, match) {
  if (!match) return false;
  if (Array.isArray(match.ids) && match.ids.includes(file.storyId)) return true;
  if (!match.prefix) return false;
  const { prefix, num } = parseStoryId(file.storyId);
  if (prefix !== match.prefix.toUpperCase()) return false;
  if (match.from != null && (num == null || num < match.from)) return false;
  if (match.to != null && (num == null || num > match.to)) return false;
  return true;
}

// Resolve files into blocks based on `feature.blocks` metadata.
// Each block gets its own `units` array sorted by storyId (numeric-aware).
// Files that don't match any block are collected into a trailing "其他" block.
function resolveBlocks(files, feature, palette) {
  const blocks = (feature && Array.isArray(feature.blocks)) ? feature.blocks : [];
  const matched = new Set();
  const resolved = blocks.map((b) => {
    const units = files.filter((f) => matchesBlock(f, b.match));
    units.forEach((u) => matched.add(u.storyId));
    units.sort((a, b2) => a.storyId.localeCompare(b2.storyId, undefined, { numeric: true }));
    return {
      id: b.id || b.code,
      code: b.code || b.id,
      title: b.title || b.code || b.id,
      subtitle: b.subtitle || '',
      description: b.description || '',
      accent: b.accent || palette.accent,
      units,
    };
  });
  const leftover = files.filter((f) => !matched.has(f.storyId));
  if (leftover.length > 0) {
    leftover.sort((a, b) => a.storyId.localeCompare(b.storyId, undefined, { numeric: true }));
    resolved.push({
      id: 'other', code: '其他', title: '其他單元', subtitle: '', description: '尚未歸入章節的素材。',
      accent: palette.muted, units: leftover,
    });
  }
  return resolved.filter((b) => b.units.length > 0);
}

const STRIPE_BG_DARK = 'repeating-linear-gradient(135deg, #2a2a22 0 8px, #1f1f18 8px 16px)';

// ─── Generate Channel Page — Magazine Feature layout ─────────
// Opt-in via `channel.feature.layout === 'magazine'`.
// Unified with the index almanac design — same fonts, paper palette, borders.
// Layout (see creator-hub/docs/channel-feature-spec.md):
//   topnav → slim hero → intro → pull quote → chapter directory
//   → block section × N (unit grid) → colophon, + sticky scrollspy rail.
function generateChannelPageFeature(channel, files) {
  const palette = CHANNEL_PALETTE[channel.season] || CHANNEL_PALETTE.spring;
  const feature = channel.feature || {};

  let blocks = resolveBlocks(files, feature, palette);

  // ancient-myths: preserve curriculum order within each block (interludes interleaved by position).
  if (channel.id === 'ancient-myths') {
    blocks = blocks.map(b => ({
      ...b,
      units: [...b.units].sort((a, c) => getCurriculumPosition(a.storyId) - getCurriculumPosition(c.storyId)),
    }));
  }

  const totalUnits = blocks.reduce((n, b) => n + b.units.length, 0);
  const prefixCode = (channel.prefix || 'MISC').toUpperCase();
  const titleEn = feature.titleEn || '';
  const tagline = feature.tagline || channel.description || '';
  const grade = feature.grade || '';
  const seasonLabel = feature.seasonLabel || SEASON_LABEL_CN[channel.season] || '';
  const number = feature.number || 'No. 01';
  const metaBits = [
    number,
    `${prefixCode}-SERIES`,
    grade,
    seasonLabel,
    `共 ${totalUnits} 單元`,
    `${blocks.length} 章節`,
  ].filter(Boolean).join(' · ');

  const introLead = (feature.intro && feature.intro.lead) || `《${channel.name}》系列索引。`;
  const introBody = (feature.intro && feature.intro.body) || channel.description || '';

  // ─ Chapter directory (TOC) ─
  const directoryHtml = blocks.map((b, i) => `
      <a class="toc-item" href="#block-${esc(b.id)}" style="--accent:${esc(b.accent)}">
        <div class="toc-num">${String(i + 1).padStart(2, '0')}.</div>
        <div class="toc-body">
          <div class="toc-label">${esc(b.code)}${b.subtitle ? ' · ' + esc(b.subtitle) : ''}</div>
          <div class="toc-title">${esc(b.title)}</div>
          <div class="toc-meta">${b.units.length} 單元</div>
        </div>
      </a>`).join('\n');

  // ─ Unit card renderer ─
  function unitCardHtml(u, accent, idx) {
    const hasThumb = thumbExists(u.storyId);
    const hasHtml = storyHtmlExists(u.storyId);
    const href = hasHtml ? storyUrl(u.storyId) : `https://drive.google.com/file/d/${u.fileId}/view`;
    const target = hasHtml ? '' : ' target="_blank" rel="noopener"';
    const thumbImg = hasThumb
      ? `<img class="unit-thumb" src="../thumbnails/${esc(u.storyId)}.jpg" alt="" loading="lazy"/>`
      : `<div class="unit-thumb unit-thumb--stripe" aria-hidden="true"><span class="unit-thumb__label">${esc(u.storyId)}</span></div>`;
    return `
        <a class="unit-card" href="${href}"${target} style="--accent:${esc(accent)}; --delay:${idx * 50}ms">
          <div class="unit-thumb-wrap">
            ${thumbImg}
            <span class="unit-code">${esc(u.storyId)}</span>
          </div>
          <div class="unit-body">
            <div class="unit-meta">
              <span>${esc(u.type || '單元')}</span>
              <span>${esc(formatSize(u.size || 0))}</span>
            </div>
            <h3 class="unit-title">${esc(u.title || u.storyId)}</h3>
            <div class="unit-footer">
              <span class="unit-arrow">閱讀 <span class="unit-arrow-sym">→</span></span>
            </div>
          </div>
        </a>`;
  }

  // ─ Each block section ─
  const sectionsHtml = blocks.map((b) => `
      <section id="block-${esc(b.id)}" class="sub-section" style="--accent:${esc(b.accent)}">
        <header class="sub-header">
          <div class="sub-info">
            <div class="sub-label">${esc(b.code)}${b.subtitle ? ' · ' + esc(b.subtitle) : ''} · ${b.units.length} 單元</div>
            <h2 class="sub-title">${esc(b.title)}</h2>
            ${b.description ? `<p class="sub-desc">${esc(b.description)}</p>` : ''}
          </div>
          <div class="sub-bigcode">${esc(b.code)}</div>
        </header>
        <div class="unit-grid">
          ${b.units.map((u, i) => unitCardHtml(u, b.accent, i)).join('')}
        </div>
      </section>`).join('\n');

  // ─ Scrollspy rail ─
  const railLinksHtml = [
    `<a class="rail-link" href="#intro" data-spy="intro">序</a>`,
    ...blocks.map((b, i) => `<a class="rail-link" href="#block-${esc(b.id)}" data-spy="block-${esc(b.id)}" style="--accent:${esc(b.accent)}">${String(i + 1).padStart(2, '0')}. ${esc(b.title)}</a>`),
  ].join('\n      ');

  return `<!DOCTYPE html>
<html lang="zh-TW" data-season="${esc(channel.season)}">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<meta name="robots" content="noindex, nofollow"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Noto+Serif+TC:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<title>${esc(channel.name)} · ${esc(prefixCode)}-Series · Waldorf Creator Hub</title>
<style>
:root {
  --bg: ${palette.bg};
  --paper: ${palette.paper};
  --fg: ${palette.fg};
  --muted: ${palette.muted};
  --accent: ${palette.accent};
  --ink: ${palette.ink};
  --shadow-emboss: 0 1px 0 rgba(255,255,255,0.55), 0 1px 2px rgba(0,0,0,0.08);
  --shadow-strong: 0 1px 0 rgba(255,255,255,0.6), 0 2px 3px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.08);
}
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); }
body {
  color: var(--fg);
  font-family: "Noto Serif TC", serif;
  font-feature-settings: "palt";
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  scroll-behavior: smooth;
}
a { color: inherit; }
::selection { background: var(--ink); color: var(--paper); }

@keyframes fadeUp { from { opacity: 0; transform: translateY(14px);} to { opacity: 1; transform: translateY(0);} }

/* Topnav */
.topnav {
  position: sticky; top: 0; z-index: 20;
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 32px;
  background: color-mix(in srgb, var(--bg) 92%, transparent);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  border-bottom: 0.5px solid var(--fg);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 11px; letter-spacing: 0.25em; color: var(--muted); text-transform: uppercase;
}
.topnav a { text-decoration: none; color: var(--muted); transition: color 200ms; }
.topnav a:hover { color: var(--fg); }
.topnav-right { display: flex; gap: 20px; }

/* Hero — warm diagonal wash, visibly distinct from the paper intro below */
.hero {
  position: relative; overflow: hidden;
  border-bottom: 1px solid var(--fg);
  background:
    linear-gradient(135deg,
      color-mix(in srgb, var(--accent) 62%, var(--paper)) 0%,
      color-mix(in srgb, var(--accent) 38%, var(--paper)) 45%,
      color-mix(in srgb, var(--muted) 28%, var(--paper)) 100%);
}
.hero::before {
  content: ''; position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 15% 30%, color-mix(in srgb, var(--paper) 55%, transparent), transparent 55%),
    radial-gradient(ellipse at 88% 85%, color-mix(in srgb, var(--ink) 20%, transparent), transparent 60%);
  pointer-events: none;
}
.hero::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: 0; height: 36px;
  background: linear-gradient(180deg, transparent, color-mix(in srgb, var(--paper) 70%, transparent) 70%, var(--paper));
  pointer-events: none;
}
.hero-inner { position: relative; z-index: 2; max-width: 1280px; margin: 0 auto; padding: 52px 48px 44px; color: var(--ink); }
.hero-meta {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 16px;
}
.hero-grid { display: grid; grid-template-columns: 1fr auto; gap: 48px; align-items: end; }
.hero-tagline {
  font-family: "Cormorant Garamond", "Noto Serif TC", serif;
  font-style: italic; font-size: clamp(17px, 2vw, 22px);
  color: var(--muted); margin-bottom: 6px; letter-spacing: 0.04em;
}
.hero-title {
  font-family: "Cormorant Garamond", "Noto Serif TC", serif;
  font-weight: 500; font-style: italic;
  font-size: clamp(40px, 5vw, 72px);
  line-height: 1.04; margin: 0; letter-spacing: 0.01em;
  background: linear-gradient(180deg, var(--ink) 0%, color-mix(in srgb, var(--ink) 60%, var(--muted)) 100%);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  text-shadow: 0 1px 0 rgba(255,255,255,0.5);
}
.hero-title-en {
  font-family: "Cormorant Garamond", serif; font-style: italic;
  font-size: clamp(15px, 1.6vw, 22px);
  margin-top: 6px; color: var(--muted); letter-spacing: 0.08em;
}
.hero-desc {
  font-family: "Noto Serif TC", serif;
  font-size: 13px; line-height: 1.75; color: var(--fg);
  opacity: 0.82; max-width: 280px; text-align: right; padding-bottom: 4px;
}
@media (max-width: 820px) {
  .hero-inner { padding: 40px 20px 32px; }
  .hero-grid { grid-template-columns: 1fr; gap: 18px; }
  .hero-desc { max-width: none; text-align: left; }
}

/* Body layout */
.page-body { max-width: 1280px; margin: 0 auto; padding: 0 48px; display: grid; grid-template-columns: 1fr 200px; gap: 64px; }
@media (max-width: 1024px) {
  .page-body { grid-template-columns: 1fr; gap: 24px; padding: 0 20px; }
  .rail { position: static !important; order: -1; padding-top: 24px !important; }
}

/* Intro */
.section-label {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 20px;
}
.intro { padding: 56px 0 48px; border-bottom: 1px solid var(--fg); }
.intro-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: start; }
@media (max-width: 820px) { .intro-grid { grid-template-columns: 1fr; gap: 24px; } }
.intro-lead {
  font-family: "Cormorant Garamond", "Noto Serif TC", serif;
  font-style: italic; font-size: clamp(22px, 2.4vw, 32px);
  line-height: 1.38; margin: 0; color: var(--ink); letter-spacing: 0.01em;
}
.intro-body {
  font-family: "Noto Serif TC", serif;
  font-size: 15px; line-height: 2; margin: 0;
  color: var(--fg); opacity: 0.9; text-indent: 2em;
}

/* Directory / TOC */
.toc { padding: 64px 0 32px; }
.toc-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  border-top: 0.5px solid var(--fg);
}
.toc-item {
  padding: 22px 20px;
  border-bottom: 0.5px solid var(--fg);
  border-right: 0.5px solid var(--fg);
  color: var(--fg); text-decoration: none;
  display: flex; gap: 18px; align-items: baseline;
  transition: background 240ms;
}
.toc-item:last-child { border-right: none; }
.toc-item:hover { background: var(--paper); }
.toc-num {
  font-family: "Cormorant Garamond", serif; font-style: italic;
  font-size: 32px; color: var(--accent); width: 54px; flex-shrink: 0;
}
.toc-body { flex: 1; min-width: 0; }
.toc-label {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 9px; letter-spacing: 0.25em;
  color: var(--accent); text-transform: uppercase; margin-bottom: 4px;
}
.toc-title { font-family: "Noto Serif TC", serif; font-size: 19px; color: var(--ink); margin-bottom: 4px; }
.toc-meta { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 10px; letter-spacing: 0.08em; color: var(--muted); }

/* Sub-series section */
.sub-section { padding: 64px 0 32px; }
.sub-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-bottom: 28px; border-bottom: 1px solid var(--fg); padding-bottom: 18px; gap: 20px;
}
.sub-info { flex: 1; min-width: 0; }
.sub-label {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 10px;
}
.sub-title {
  font-family: "Noto Serif TC", serif; font-weight: 500;
  font-size: clamp(28px, 3.6vw, 44px); margin: 0 0 10px;
  color: var(--ink); letter-spacing: 0.01em;
}
.sub-desc {
  font-family: "Cormorant Garamond", "Noto Serif TC", serif;
  font-style: italic; font-size: 16px; line-height: 1.7;
  color: var(--muted); margin: 0; max-width: 640px;
}
.sub-bigcode {
  font-family: "Cormorant Garamond", serif; font-style: italic;
  font-size: 64px; line-height: 0.9;
  color: var(--accent); opacity: 0.85;
  padding-left: 20px; flex-shrink: 0;
}

/* Unit grid */
.unit-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 26px; }
.unit-card {
  background: var(--paper);
  border: 1px solid var(--fg);
  position: relative;
  text-decoration: none; color: inherit; display: block;
  opacity: 0; transform: translateY(12px);
  animation: fadeUp 560ms cubic-bezier(.2,.7,.2,1) forwards;
  animation-delay: var(--delay, 0ms);
  transition: box-shadow 300ms, transform 300ms;
}
.unit-card:hover { box-shadow: 4px 4px 0 0 var(--accent); transform: translateY(-2px); }

.unit-thumb-wrap { height: 180px; overflow: hidden; border-bottom: 1px solid var(--fg); position: relative; }
.unit-thumb { width: 100%; height: 100%; object-fit: cover; display: block; }
.unit-thumb--stripe { display: flex; align-items: center; justify-content: center; background: ${STRIPE_BG_DARK}; color: rgba(255,255,255,0.22); }
.unit-thumb__label { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12px; letter-spacing: 0.25em; color: rgba(255,255,255,0.45); }
.unit-code {
  position: absolute; bottom: 12px; left: 12px;
  background: var(--paper); color: var(--accent);
  border: 1px solid var(--accent);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 10px; letter-spacing: 0.2em;
  padding: 4px 9px;
}

.unit-body { padding: 18px 20px 18px; }
.unit-meta {
  display: flex; justify-content: space-between; align-items: center;
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 10px;
}
.unit-title {
  font-family: "Noto Serif TC", serif; font-size: 18px; font-weight: 500;
  margin: 0 0 14px; line-height: 1.35; color: var(--ink);
}
.unit-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 12px; border-top: 0.5px solid var(--fg);
}
.unit-arrow {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 10px; letter-spacing: 0.2em;
  color: var(--ink); text-transform: uppercase;
  display: inline-flex; align-items: center; gap: 6px;
}
.unit-arrow-sym { transition: transform 260ms; display: inline-block; }
.unit-card:hover .unit-arrow-sym { transform: translateX(4px); }

/* Scrollspy rail */
.rail { position: sticky; top: 80px; align-self: start; padding-top: 72px; height: fit-content; }
.rail-label {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 9px; letter-spacing: 0.3em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 14px;
}
.rail-link {
  display: block; padding: 7px 0 7px 14px;
  border-left: 1px solid color-mix(in srgb, var(--muted) 50%, transparent);
  color: var(--muted);
  font-family: "Noto Serif TC", serif; font-size: 13px; text-decoration: none;
  transition: all 280ms;
}
.rail-link.is-active {
  border-left: 2px solid var(--accent, var(--ink));
  color: var(--ink); font-weight: 500;
}

/* Colophon */
.colophon {
  border-top: 1px solid var(--fg); padding: 32px 0 64px; margin-top: 48px;
  display: flex; justify-content: space-between; align-items: center;
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 10px; letter-spacing: 0.2em; color: var(--muted); text-transform: uppercase;
  flex-wrap: wrap; gap: 14px;
}
.colophon a { text-decoration: none; color: var(--muted); transition: color 200ms; }
.colophon a:hover { color: var(--ink); }
.colophon-motto {
  font-family: "Cormorant Garamond", serif; font-style: italic;
  text-transform: none; letter-spacing: normal; font-size: 14px;
}
</style>
</head>
<body>
<nav class="topnav">
  <a href="../index.html">← Waldorf Creator Hub</a>
  <span>${esc(prefixCode)} · Feature No. 01</span>
  <span class="topnav-right"><span>系列</span><span>每日</span><span>關於</span></span>
</nav>

<header class="hero">
  <div class="hero-inner">
    <div class="hero-meta">${esc(metaBits)}</div>
    <div class="hero-grid">
      <div>
        ${tagline ? `<div class="hero-tagline">${esc(tagline)}</div>` : ''}
        <h1 class="hero-title">${esc(channel.name)}</h1>
        ${titleEn ? `<div class="hero-title-en">${esc(titleEn)}</div>` : ''}
      </div>
      ${channel.description ? `<div class="hero-desc">${esc(channel.description)}</div>` : ''}
    </div>
  </div>
</header>

<div class="page-body">
  <main>
    <section id="intro" class="intro">
      <div class="section-label">序 · Introduction</div>
      <div class="intro-grid">
        <p class="intro-lead">${esc(introLead)}</p>
        ${introBody ? `<p class="intro-body">${esc(introBody)}</p>` : ''}
      </div>
    </section>

    <section class="toc">
      <div class="section-label">分部目錄 · Sub-Series</div>
      <div class="toc-grid">
${directoryHtml}
      </div>
    </section>

${sectionsHtml}

    <footer class="colophon">
      <a href="../index.html">← 返回年鑑</a>
      <span class="colophon-motto">Per aspera ad astra</span>
      <span>MMXXVI · 宜蘭慈心華德福實驗學校</span>
    </footer>
  </main>

  <aside class="rail">
    <div class="rail-label">本輯分部</div>
    <nav>
      ${railLinksHtml}
    </nav>
  </aside>
</div>

<script>
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.rail-link'));
  var targets = links.map(function(a){
    var id = a.getAttribute('data-spy');
    return { id: id, el: document.getElementById(id), link: a };
  }).filter(function(t){ return !!t.el; });

  function onScroll(){
    var y = window.scrollY + 160;
    var current = targets[0];
    for (var i = 0; i < targets.length; i++){
      if (targets[i].el.offsetTop <= y) current = targets[i];
    }
    links.forEach(function(l){ l.classList.remove('is-active'); });
    if (current) current.link.classList.add('is-active');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
</script>
</body>
</html>`;
}

// ─── Generate Channel Page — Legacy (gradient YouTube-card layout) ─
// Used by channels that haven't opted into the Magazine Feature layout.
// Kept verbatim from the previous design (pre-2026-04-18 redesign).
function generateChannelPageLegacy(channel, files) {
  const s = SEASON_CSS[channel.season];
  let sorted;
  if (channel.id === 'ancient-myths') {
    sorted = [...files].sort((a, b) => getCurriculumPosition(b.storyId) - getCurriculumPosition(a.storyId));
  } else if (channel.sort === 'storyId') {
    sorted = [...files].sort((a, b) => a.storyId.localeCompare(b.storyId, undefined, { numeric: true }));
  } else {
    sorted = [...files].sort((a, b) => (b.modifiedTime || '').localeCompare(a.modifiedTime || ''));
  }

  _placeholderIdx = 0;

  const storyCards = sorted.map(file => {
    const hasThumb = thumbExists(file.storyId);
    const hasHtml = storyHtmlExists(file.storyId);
    const placeholderFile = nextWatercolorPlaceholder();
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

// ─── Dispatcher ───────────────────────────────────────────────
// Picks Magazine Feature layout when opted-in via feature.layout, else Legacy.
function generateChannelPage(channel, files) {
  if (channel.feature && channel.feature.layout === 'magazine') {
    return generateChannelPageFeature(channel, files);
  }
  return generateChannelPageLegacy(channel, files);
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

  // Build channel objects from channels.json as authoritative list,
  // merging any runtime info from files.json.channelList (sync-drive populated).
  const PREFIX_ORDER = ['A', 'AM', 'B', 'TL', 'I', 'SH', 'O'];
  const runtime = Object.fromEntries((filesData.channelList || []).map(c => [c.id, c]));
  const ids = new Set([
    ...Object.keys(channelsData.channels || {}),
    ...Object.keys(runtime),
  ]);
  const channels = [...ids].map(id => {
    const cfg = channelsData.channels[id] || {};
    const rt = runtime[id] || {};
    return {
      id,
      name: cfg.name || rt.name || id,
      description: cfg.description || rt.description || '',
      prefix: cfg.prefix || rt.prefix || '',
      season: cfg.season || rt.season || 'winter',
      icon: cfg.icon || rt.icon || 'science',
      dynamic: rt.isNew || false,
      sort: cfg.sort || 'modifiedTime',
      feature: cfg.feature || null,
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
