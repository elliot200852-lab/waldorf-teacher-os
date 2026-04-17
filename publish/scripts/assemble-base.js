#!/usr/bin/env node
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// TeacherOS — 組裝腳本共用引擎
// 路徑：publish/scripts/assemble-base.js
// 用途：提供所有 assemble-*.js 共用的解析、渲染、上傳邏輯
// 依賴：無外部套件（純 Node.js fs/path）
// 跨平台：macOS + Windows + Linux
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//
// 版本：1.1.0 (2026-03-30) — 新增圖片壓縮步驟（compress-image.js）
// 版本：1.0.0 (2026-03-29) — 從三支 assemble 腳本抽取共用邏輯
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const fs = require('fs');
const path = require('path');
const os = require('os');
const { compressImage } = require('./compress-image');

// ── GWS CLI 解析 ─────────────────────────────────────
// 找到可用的 gws 指令，優先驗證能實際連線
const GWS_BIN = (() => {
  const { execSync } = require('child_process');

  // 0. Patch PATH first so #!/usr/bin/env node resolves correctly in non-interactive shells.
  //    Inject all common node/bin locations; idempotent if already present.
  if (process.platform !== 'win32') {
    const extraDirs = [
      '/opt/homebrew/bin', '/usr/local/bin',
      path.join(os.homedir(), '.npm-global/bin'),
    ];
    const currentPath = process.env.PATH || '';
    const toAdd = extraDirs.filter(d => !currentPath.split(':').includes(d)).join(':');
    if (toAdd) process.env.PATH = `${toAdd}:${currentPath}`;
  }

  // Helper: health check WITH the now-patched env (used throughout this block)
  function gwsHealthCheckWithEnv(bin) {
    try {
      const params = process.platform === 'win32'
        ? '--params "{\\"fields\\":\\"user\\"}"'
        : '--params \'{"fields":"user"}\'';
      execSync(`${bin} drive about get ${params}`, {
        encoding: 'utf-8', timeout: 10000, stdio: ['pipe', 'pipe', 'pipe'],
      });
      return true;
    } catch { return false; }
  }

  // Build candidate list dynamically:
  //   a) npm prefix -g  (works for Homebrew npm, nvm, volta, fnm, etc.)
  //   b) static fallbacks
  const candidates = [];
  try {
    // Try each known node binary to find the active npm
    const nodeBins = [
      process.execPath,
      '/opt/homebrew/bin/node', '/usr/local/bin/node',
    ];
    for (const nb of nodeBins) {
      if (!fs.existsSync(nb)) continue;
      try {
        const npmBin = path.join(path.dirname(nb), 'npm');
        if (!fs.existsSync(npmBin)) continue;
        const prefix = execSync(`${npmBin} prefix -g`, {
          encoding: 'utf-8', timeout: 5000, stdio: ['pipe', 'pipe', 'pipe'],
        }).trim();
        const gwsCandidate = path.join(prefix, 'bin', 'gws');
        if (!candidates.includes(gwsCandidate)) candidates.push(gwsCandidate);
        break;
      } catch {}
    }
  } catch {}
  // Static fallbacks (Windows + common macOS/Linux)
  if (process.platform === 'win32') {
    candidates.push(
      path.join(os.homedir(), 'AppData/Roaming/npm/gws.cmd'),
      'C:/Program Files/nodejs/gws.cmd',
    );
  } else {
    candidates.push(
      '/opt/homebrew/bin/gws',
      '/usr/local/bin/gws',
      path.join(os.homedir(), '.npm-global/bin/gws'),
    );
  }

  for (const p of candidates) {
    if (fs.existsSync(p) && gwsHealthCheckWithEnv(p)) {
      console.log(`[gws] Using: ${p} (health check passed)`);
      return p;
    }
  }

  // 1. Try which/where
  try {
    const cmd = process.platform === 'win32' ? 'where gws' : 'which gws';
    const found = execSync(cmd, { encoding: 'utf-8', timeout: 5000 }).trim().split('\n')[0];
    if (found && gwsHealthCheckWithEnv(found)) {
      console.log(`[gws] Using: ${found} (health check passed)`);
      return found;
    }
    if (found) console.warn(`[gws] Found ${found} but health check failed (401), trying npx fallback...`);
  } catch {}

  // 2. Scan nvm versions (macOS)
  const nvmBase = path.join(os.homedir(), '.nvm/versions/node');
  try {
    if (fs.existsSync(nvmBase)) {
      const versions = fs.readdirSync(nvmBase).sort().reverse();
      for (const v of versions) {
        const gwsPath = path.join(nvmBase, v, 'bin/gws');
        if (fs.existsSync(gwsPath) && gwsHealthCheckWithEnv(gwsPath)) return gwsPath;
      }
    }
  } catch {}

  // 3. npx fallback (local cache only)
  try {
    const { execSync: es } = require('child_process');
    es('npx --no-install @googleworkspace/cli --version', {
      encoding: 'utf-8', timeout: 5000, stdio: ['pipe', 'pipe', 'pipe']
    });
    const npxBin = 'npx @googleworkspace/cli';
    if (gwsHealthCheckWithEnv(npxBin)) {
      console.log(`[gws] Using: ${npxBin} (health check passed)`);
      return npxBin;
    }
  } catch {}

  console.warn('[gws] No healthy gws found. Upload will be skipped.');
  return null;
})();

// ── 季節偵測 ─────────────────────────────────────────
function detectSeason(date = new Date()) {
  const month = date.getMonth() + 1;
  if (month >= 3 && month <= 5) return 'spring';
  if (month >= 6 && month <= 8) return 'summer';
  if (month >= 9 && month <= 11) return 'autumn';
  return 'winter';
}

const SEASON_ICONS = {
  spring: 'eco', summer: 'sunny', autumn: 'park', winter: 'ac_unit',
};
const SEASON_LABELS = {
  spring: '春季', summer: '夏季', autumn: '秋季', winter: '冬季',
};
const SEASON_DIVIDER_ICONS = {
  spring: 'local_florist', summer: 'wb_sunny', autumn: 'park', winter: 'ac_unit',
};

// ── 圖片格式偵測（magic bytes）────────────────────────
// 副檔名不可靠（Gemini 下載的 .png 可能實際是 JPEG），用檔頭判斷真實格式
function detectImageMime(buf) {
  if (buf[0] === 0xFF && buf[1] === 0xD8 && buf[2] === 0xFF) return 'image/jpeg';
  if (buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4E && buf[3] === 0x47) return 'image/png';
  if (buf[0] === 0x52 && buf[1] === 0x49 && buf[2] === 0x46 && buf[3] === 0x46 &&
      buf[8] === 0x57 && buf[9] === 0x45 && buf[10] === 0x42 && buf[11] === 0x50) return 'image/webp';
  // AVIF: starts with ftyp box containing 'avif'
  if (buf.length > 12 && buf.slice(4, 8).toString() === 'ftyp') return 'image/avif';
  return 'image/png'; // fallback
}

// ── Markdown 解析輔助 ────────────────────────────────

function stripFrontmatter(md) {
  const match = md.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/);
  return match ? md.slice(match[0].length) : md;
}

function splitByHr(md) {
  return md.split(/\n---+\n/).map(s => s.trim()).filter(Boolean);
}

function extractFrontmatter(md) {
  const meta = {};
  const lines = md.split('\n');
  for (const line of lines) {
    const m = line.match(/^>\s*(.+?)：\s*(.+)/);
    if (m) meta[m[1].trim()] = m[2].trim();
  }
  return meta;
}

// ── 動態提取核心意象 ─────────────────────────────────
function extractPullQuote(contentMd, contentSections, fallbackQuote) {
  const coreMatch = contentMd.match(/##\s*核心意象\s*\n+(.+)/);
  if (coreMatch) return coreMatch[1].trim();

  const storySection = contentSections.length > 0 ? contentSections[0] : '';
  if (storySection) {
    const lines = storySection.split('\n').map(l => l.trim()).filter(l =>
      l && !l.startsWith('#') && !l.startsWith('>') && !l.startsWith('|') && !l.startsWith('-') && !l.startsWith('*')
    );
    if (lines.length > 0) {
      const lastLine = lines[lines.length - 1];
      const sentences = lastLine.split(/(?<=[。！？])/);
      const candidate = sentences[sentences.length - 1].trim() || lastLine;
      if (candidate.length > 5) return candidate;
      if (lines.length > 1) return lines[lines.length - 2];
    }
  }

  return fallbackQuote || '';
}

function mdParagraphsToHtml(text, cssClass = 'text-[18px] leading-[1.6]') {
  const paragraphs = text.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
  return paragraphs.map((p, i) => {
    if (p.startsWith('#') || p.startsWith('>')) return '';
    p = p.replace(/\*\*(.+?)\*\*/g, '<span class="font-medium text-[var(--primary)]">$1</span>');
    p = p.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    p = p.replace(/\n/g, '<br/>');
    return `<p class="${cssClass}">${p}</p>`;
  }).filter(Boolean).join('\n      ');
}

// ── 解析 raw-materials.md 的來源 URL ────────────────
function parseSourceUrls(rawMaterialsMd) {
  const urls = {};
  const lines = rawMaterialsMd.split('\n');
  let currentName = '';
  for (const line of lines) {
    const formatB = line.match(/^\d+\.\s+(.+?)\s+—\s+(https?:\/\/\S+)/);
    if (formatB) {
      const rawName = formatB[1].trim().replace(/\*\*/g, '');
      const url = formatB[2].trim();
      urls[rawName] = url;
      const shortNames = extractShortNames(rawName);
      for (const sn of shortNames) {
        if (!urls[sn]) urls[sn] = url;
      }
      continue;
    }
    const nameMatch = line.match(/(?:\d+\.\s+|\-\s+)\*\*(.+?)\*\*/);
    if (nameMatch) {
      currentName = nameMatch[1].trim();
    }
    const urlMatch = line.match(/URL[：:]\s*(https?:\/\/\S+)/);
    if (urlMatch && currentName) {
      urls[currentName] = urlMatch[1].trim();
    }
  }
  return urls;
}

function extractShortNames(fullName) {
  const shorts = [];
  const orgName = fullName.replace(/[「」《》（）()].+?[」》）)]/g, '').trim();
  shorts.push(orgName);
  const keywords = orgName.match(/[\u4e00-\u9fff]{2,}/g) || [];
  for (const kw of keywords) {
    if (kw.length >= 2 && !['官網', '管理處', '國家', '公園', '管理', '資料'].includes(kw)) {
      shorts.push(kw);
    }
  }
  return shorts;
}

// ── 解析 content.md 的事實出處表 ─────────────────────
function parseFactTable(contentMd, sourceUrls) {
  const lines = contentMd.split('\n');
  const facts = [];
  let inTable = false;
  let headerPassed = false;

  for (const line of lines) {
    if (line.includes('事實') && line.includes('來源') && line.includes('|')) {
      inTable = true;
      continue;
    }
    if (inTable && line.match(/^\|[\s\-|]+\|$/)) {
      headerPassed = true;
      continue;
    }
    if (inTable && headerPassed && line.startsWith('|')) {
      const cells = line.split('|').map(c => c.trim()).filter(Boolean);
      if (cells.length >= 2) {
        const fact = cells[0];
        const sourcesRaw = cells[1];
        const linkedSources = sourcesRaw.split(/[；;]/).map(s => {
          // First: try to extract inline markdown link [text](url) or [text]（url）
          const inlineLink = s.match(/\[([^\]]+)\]\(([^)]+)\)/) || s.match(/\[([^\]]+)\]（([^）]+)）/);
          if (inlineLink) {
            return { name: inlineLink[1].trim(), url: inlineLink[2].trim() };
          }
          const name = s.trim();
          let url = '';
          if (sourceUrls[name]) {
            url = sourceUrls[name];
          } else {
            for (const [key, value] of Object.entries(sourceUrls)) {
              if (key.includes(name) || name.includes(key)) {
                url = value;
                break;
              }
            }
            if (!url) {
              const nameTokens = (name.match(/[\u4e00-\u9fff]{2,}/g) || []).filter(t =>
                !['管理處', '國家', '公園', '官網', '資料', '出處'].includes(t)
              );
              for (const [key, value] of Object.entries(sourceUrls)) {
                const keyTokens = (key.match(/[\u4e00-\u9fff]{2,}/g) || []);
                const overlap = nameTokens.filter(t => keyTokens.some(kt => kt.includes(t) || t.includes(kt)));
                if (overlap.length > 0) {
                  url = value;
                  break;
                }
              }
            }
          }
          return { name, url };
        });
        facts.push({ fact, sources: linkedSources });
      }
    }
    if (inTable && headerPassed && !line.startsWith('|') && line.trim() !== '') {
      inTable = false;
    }
  }
  return facts;
}

// ── 解析 chalkboard-prompt.md ────────────────────────
function parseChalkboardPrompt(promptMd) {
  const result = {
    englishPrompt: '',
    chinesePrompt: '',
    downloadFilename: '',
    iterations: [],
  };

  const fnMatch = promptMd.match(/下載檔[案]?名[：:]\s*(.+)/);
  if (fnMatch) result.downloadFilename = fnMatch[1].trim();

  const sections = {};
  const sectionRegex = /^## (.+)$/gm;
  let match;
  const sectionStarts = [];
  while ((match = sectionRegex.exec(promptMd)) !== null) {
    sectionStarts.push({ title: match[1].trim(), index: match.index + match[0].length });
  }
  for (let i = 0; i < sectionStarts.length; i++) {
    const start = sectionStarts[i].index;
    const end = i + 1 < sectionStarts.length ? sectionStarts[i + 1].index - sectionStarts[i + 1].title.length - 3 : promptMd.length;
    sections[sectionStarts[i].title] = promptMd.slice(start, end).trim();
  }

  for (const [title, content] of Object.entries(sections)) {
    if (/english|英文.*prompt|gemini.*製圖/i.test(title)) {
      result.englishPrompt = content.replace(/^\n+/, '').trim();
      break;
    }
  }
  for (const [title, content] of Object.entries(sections)) {
    if (/中文|翻譯/.test(title)) {
      result.chinesePrompt = content.replace(/^\n+/, '').trim();
      break;
    }
  }
  for (const [title, content] of Object.entries(sections)) {
    if (/迭代|iteration/i.test(title)) {
      const rows = content.split('\n').filter(l => l.startsWith('|') && !l.match(/^\|[\s\-|]+\|$/));
      for (const row of rows) {
        const cells = row.split('|').map(c => c.trim()).filter(Boolean);
        if (cells.length >= 3 && cells[0] !== '版本') {
          result.iterations.push({ version: cells[0], issue: cells[1], fix: cells[2] });
        }
      }
      break;
    }
  }

  return result;
}

// ── 解析 images.md ───────────────────────────────────
// 使用最完整版本：支援 Format A/B/C + lookahead split + 說明欄位
function parseImages(imagesMd) {
  const sections = [];
  const blocks = imagesMd.split(/\n(?=#{2,} )/);

  for (const block of blocks) {
    if (!block.trim()) continue;
    const lines = block.split('\n');
    const title = lines[0].replace(/^#+\s*/, '').replace(/^\d+\.\s*/, '').trim();
    const content = lines.slice(1).join('\n').trim();

    // Format C：連結欄位
    let url = '';
    const linkMatch = content.match(/連結[：:]\s*(https?:\/\/\S+)/);
    if (linkMatch) url = linkMatch[1].trim();
    // Format A：**URL**：
    if (!url) {
      const urlFormatA = content.match(/\*{0,2}URL\*{0,2}[：:]\s*(https?:\/\/\S+)/);
      if (urlFormatA) url = urlFormatA[1].trim();
    }
    // Format B：來源行
    if (!url) {
      const sourceLineMatch = content.match(/來源[：:]\s*(.+)/);
      if (sourceLineMatch) {
        const sourceLine = sourceLineMatch[1];
        const parenUrl = sourceLine.match(/[（(](https?:\/\/[^\s）)]+)[）)]/);
        if (parenUrl) {
          url = parenUrl[1].trim();
        } else {
          const bareUrl = sourceLine.match(/(https?:\/\/\S+)/);
          if (bareUrl) url = bareUrl[1].trim();
        }
      }
    }

    // 用途（支援多種欄位名）
    let usage = '';
    const useFormatA = content.match(/\*{0,2}用途\*{0,2}[：:]\s*(.+)/);
    if (useFormatA) {
      usage = useFormatA[1].trim();
    } else {
      const roleMatch = content.match(/在故事中的角色[：:]\s*(.+)/);
      if (roleMatch) usage = roleMatch[1].trim();
    }
    if (!usage) {
      const noteMatch = content.match(/說明[：:]\s*(.+)/);
      if (noteMatch) usage = noteMatch[1].trim();
    }

    let license = '';
    const licMatch = content.match(/\*{0,2}授權\*{0,2}[：:]\s*(.+)/);
    if (licMatch) license = licMatch[1].trim();

    let description = '';
    const descMatch = content.match(/圖片描述[：:]\s*(.+)/) || content.match(/(?<!圖片)描述[：:]\s*(.+)/);
    if (descMatch) description = descMatch[1].trim();

    let timing = '';
    const timingMatch = content.match(/展示時機[：:]\s*(.+)/) || content.match(/建議使用時機[：:]\s*(.+)/);
    if (timingMatch) timing = timingMatch[1].trim();

    let sourceName = '';
    const sourceNameMatch = content.match(/來源[：:]\s*(.+)/);
    if (sourceNameMatch) {
      sourceName = sourceNameMatch[1].replace(/\s*(?:—|--)\s*(?:File:|https?:).*/i, '').trim();
    }

    if (title && (url || usage || description)) {
      sections.push({ title, url, usage, license, description, timing, sourceName });
    }
  }

  return sections;
}

// ── 解析 references.md ──────────────────────────────
function parseReferences(referencesMd) {
  const refs = [];
  const lines = referencesMd.split('\n');
  for (const line of lines) {
    // Format A: 1. 名稱 —/-- URL —/-- 類型
    const match = line.match(/^\d+\.\s+(.+?)\s+(?:—|--)\s+(https?:\/\/\S+)(?:\s+(?:—|--)\s+(.+))?/);
    if (match) {
      refs.push({ name: match[1].trim(), url: match[2].trim(), type: match[3] ? match[3].trim() : '網站' });
      continue;
    }
    // Format B: - 名稱（URL）
    const matchB = line.match(/^[-*]\s+(.+?)[（(](https?:\/\/[^\s）)]+)[）)]/);
    if (matchB) {
      refs.push({ name: matchB[1].trim(), url: matchB[2].trim(), type: '網站' });
      continue;
    }
    // Format C: URL: https://（學術引用）
    const matchC = line.match(/URL[：:]\s*(https?:\/\/[^\s）)]+)/);
    if (matchC) {
      const nameRaw = line
        .replace(/\*{1,2}([^*]+)\*{1,2}/g, '$1')
        .replace(/URL[：:]\s*https?:\/\/\S*/g, '')
        .replace(/（[^）]*）。?/g, '')
        .replace(/^[-*\d.]\s+/, '')
        .replace(/[。\.]\s*$/, '')
        .trim();
      refs.push({
        name: nameRaw || '參考來源',
        url: matchC[1].replace(/[.)）]+$/, '').trim(),
        type: '網站',
      });
    }
  }
  return refs;
}

// ── 搜尋黑板畫圖檔 ──────────────────────────────────
// searchPrefix: '' for story, 'Botany-' for botany, 'AncientMyths-' for myths
function findChalkboardImage(storyId, downloadsDir, chalkboardPrompt, searchPrefix = '') {
  let imagePath = '';
  let imageBase64 = '';
  let imageMime = 'image/png';

  // Strategy 1: exact filename from chalkboard-prompt.md
  if (chalkboardPrompt.downloadFilename) {
    const candidatePath = path.join(downloadsDir, chalkboardPrompt.downloadFilename);
    if (fs.existsSync(candidatePath)) {
      imagePath = candidatePath;
      console.log(`[assemble] [OK] chalkboard-image: ${chalkboardPrompt.downloadFilename}`);
    } else {
      console.log(`[assemble] [MISSING] chalkboard-image (exact): ${candidatePath}`);
    }
  }

  // Strategy 2: fuzzy match with prefix
  if (!imagePath) {
    const prefix = searchPrefix || '';
    const pattern = new RegExp(prefix + storyId + '.*chalkboard', 'i');
    try {
      const files = fs.readdirSync(downloadsDir);
      const match = files.find(f => pattern.test(f) && /\.(png|jpg|jpeg|webp)$/i.test(f));
      if (match) {
        imagePath = path.join(downloadsDir, match);
        console.log(`[assemble] [OK] chalkboard-image (fuzzy): ${match}`);
      }
    } catch (e) {
      console.log(`[assemble] [WARN] Cannot read downloads dir: ${downloadsDir}`);
    }
  }

  // Strategy 3: recent Gemini default filename (30 min)
  if (!imagePath) {
    try {
      const files = fs.readdirSync(downloadsDir)
        .filter(f => /^Gemini_Generated_Image/i.test(f) && /\.(png|jpg|jpeg|webp)$/i.test(f))
        .map(f => ({ name: f, mtime: fs.statSync(path.join(downloadsDir, f)).mtime }))
        .sort((a, b) => b.mtime - a.mtime);
      const thirtyMinAgo = Date.now() - 30 * 60 * 1000;
      const recent = files.find(f => f.mtime.getTime() > thirtyMinAgo);
      if (recent) {
        imagePath = path.join(downloadsDir, recent.name);
        console.log(`[assemble] [OK] chalkboard-image (gemini-recent): ${recent.name}`);
      }
    } catch (e) { /* ignore */ }
  }

  // Strategy 4: any image containing storyId
  if (!imagePath) {
    try {
      const files = fs.readdirSync(downloadsDir)
        .filter(f => f.toLowerCase().includes(storyId.toLowerCase()) && /\.(png|jpg|jpeg|webp)$/i.test(f));
      if (files.length > 0) {
        imagePath = path.join(downloadsDir, files[0]);
        console.log(`[assemble] [OK] chalkboard-image (id-match): ${files[0]}`);
      }
    } catch (e) { /* ignore */ }
  }

  if (!imagePath) {
    console.error(`[assemble] [FAIL] chalkboard-image: 4 strategies exhausted, no image found in ${downloadsDir}`);
  }

  // Compress → base64 encode
  if (imagePath) {
    // 壓縮優先：Gemini 圖片通常是大 PNG（2–5 MB），壓縮後可減少 HTML 體積 60–80%
    const compressedPath = compressImage(imagePath);
    const pathToEncode = compressedPath || imagePath;

    // 用 magic bytes 偵測真實格式（不靠副檔名）
    // Gemini 下載的 .png 可能實際上是 JPEG，MIME 不符會導致 PDF 圖片錯誤
    const buf = fs.readFileSync(pathToEncode);
    imageMime = detectImageMime(buf);
    const ext = path.extname(pathToEncode).toLowerCase();
    const extMime = ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg'
      : ext === '.webp' ? 'image/webp'
      : ext === '.avif' ? 'image/avif'
      : 'image/png';
    if (imageMime !== extMime) {
      console.warn(`[assemble] [WARN] MIME mismatch: extension says ${extMime} but file is actually ${imageMime}`);
    }
    imageBase64 = buf.toString('base64');
    const embeddedSizeKB = imageBase64.length * 0.75 / 1024;
    console.log(`[assemble] Embedded: ${(embeddedSizeKB / 1024).toFixed(2)} MB (${pathToEncode === imagePath ? 'original, compression skipped' : 'compressed'})`);
  }

  return { imagePath, imageBase64, imageMime };
}

// ── CLI 參數解析 ─────────────────────────────────────
function parseCLIArgs(scriptName) {
  const args = process.argv.slice(2);
  const seasonArg = args.find(a => a.startsWith('--season='));
  const downloadsArg = args.find(a => a.startsWith('--downloads='));
  const outputArg = args.find(a => a.startsWith('--output='));
  const driveFolderArg = args.find(a => a.startsWith('--drive-folder='));
  const versionArg = args.find(a => a.startsWith('--version='));

  const fileArgs = args.filter(a => !a.startsWith('--'));
  const storyDir = fileArgs[0];

  if (!storyDir) {
    console.error(`Usage: node ${scriptName} <dir> [options]`);
    console.error('');
    console.error('Options:');
    console.error('  --season=spring|summer|autumn|winter');
    console.error('  --downloads=PATH   (default: ~/Downloads)');
    console.error('  --output=DIR       (default: temp/)');
    console.error('  --pdf              Also generate PDF');
    console.error('  --upload           Upload HTML+PDF to Google Drive');
    console.error('  --drive-folder=ID  Drive folder ID');
    console.error('  --dry-run          Check files only, no output');
    console.error('  --version=v2       Version label (skips Drive cleanup)');
    process.exit(1);
  }

  return {
    storyDir,
    season: seasonArg ? seasonArg.split('=')[1] : detectSeason(),
    downloadsDir: downloadsArg ? downloadsArg.split('=')[1] : path.join(os.homedir(), 'Downloads'),
    outputDir: outputArg ? outputArg.split('=')[1] : 'temp',
    driveFolderOverride: driveFolderArg ? driveFolderArg.split('=')[1] : null,
    storyVersion: versionArg ? versionArg.split('=')[1] : null,
    doPdf: args.includes('--pdf'),
    doUpload: args.includes('--upload'),
    dryRun: args.includes('--dry-run'),
    date: new Date().toISOString().split('T')[0],
  };
}

// ── 檔案檢查 ────────────────────────────────────────
function checkFiles(resolvedDir, requiredFiles, optionalFiles = []) {
  const checklist = {};
  for (const f of [...requiredFiles, ...optionalFiles]) {
    checklist[f] = false;
  }
  checklist['chalkboard-image'] = false;

  for (const f of [...requiredFiles, ...optionalFiles]) {
    const fp = path.join(resolvedDir, f);
    if (fs.existsSync(fp)) {
      checklist[f] = true;
      console.log(`[assemble] [OK] ${f}`);
    } else {
      const level = requiredFiles.includes(f) ? 'MISSING' : 'OPTIONAL';
      console.log(`[assemble] [${level}] ${f}`);
    }
  }

  return checklist;
}

// ── 內容段落提取 ─────────────────────────────────────
// 通用策略：## 故事本文 → pre-H2 fallback → non-reserved H2 → splitByHr
function extractContentSections(contentMd) {
  const h2Parts = contentMd.split(/(?=^## )/m).map(s => s.trim()).filter(Boolean);

  // 策略 1：找 ## 故事本文
  const storyPart = h2Parts.find(p => /^## 故事本文/.test(p));
  if (storyPart) {
    const body = storyPart.replace(/^## 故事本文\s*\n+/, '').trim();
    return body ? [body] : [];
  }

  // Fallback 1：# 標題後、第一個 ## 之前的正文
  const firstH2Part = h2Parts[0] || '';
  const preStoryContent = /^# /.test(firstH2Part)
    ? firstH2Part.replace(/^# [^\n]+\n+/, '').trim()
    : '';
  if (preStoryContent.length > 200) {
    return [preStoryContent];
  }

  // Fallback 1b：收集所有非保留 ## 段落
  const RESERVED = /^## ?(事實|地理標記|延伸線索|注意事項|資料來源|參考來源|下一課|教師|核心意象)/;
  const storyParts = h2Parts
    .filter(p => !RESERVED.test(p) && !/^# /.test(p))
    .map(p => p.replace(/^##+ [^\n]+\n/, '').trim())
    .filter(p => p.length > 0);
  if (storyParts.length > 0) {
    return [storyParts.join('\n\n')];
  }

  // Fallback 2：splitByHr
  const allSections = splitByHr(contentMd);
  return allSections.filter(s =>
    !s.startsWith('>') &&
    !s.startsWith('## 事實出處') && !s.includes('| 事實 |') &&
    !s.startsWith('## 地理標記') &&
    !s.startsWith('## 延伸線索')
  );
}

// ── HTML 渲染片段 ────────────────────────────────────

function renderFactTableHtml(factTable) {
  return factTable.map(f => {
    const sourceLinks = f.sources.map(s => {
      if (s.url) return `<a href="${s.url}" target="_blank" class="text-[var(--secondary)] underline decoration-dotted hover:text-[var(--primary)]">${s.name}</a>`;
      return s.name;
    }).join('；');
    return `<tr class="border-b border-[var(--outline-variant)]/20"><td class="py-1.5 pr-4">${f.fact}</td><td class="py-1.5">${sourceLinks}</td></tr>`;
  }).join('\n            ');
}

function renderImagesHtml(images) {
  return images.map(img => `
      <div class="flex gap-3 items-start">
        <span class="material-symbols-outlined text-[var(--secondary)] mt-0.5 text-[18px]">image</span>
        <div>
          <p class="text-[17px] leading-[1.55]">
            <span class="font-medium text-[var(--primary)]">${img.title}</span>
            ${img.description ? `<br/><span class="text-[15px] text-[var(--on-surface-variant)]">${img.description}</span>` : ''}
            ${img.usage ? `<br/><span class="text-[15px]">${img.usage}</span>` : ''}
            ${img.timing ? `<br/><span class="text-[14px] text-[var(--on-surface-variant)] italic">展示時機：${img.timing}</span>` : ''}
            ${img.sourceName ? `<br/><span class="text-sm text-[var(--on-surface-variant)]">來源：${img.sourceName}</span>` : ''}
            ${img.url ? `<br/><a href="${img.url}" target="_blank" class="text-[var(--secondary)] underline decoration-dotted text-sm">${img.url}</a>` : ''}
            ${img.license ? `<span class="text-sm text-[var(--on-surface-variant)] ml-2">[${img.license}]</span>` : ''}
          </p>
        </div>
      </div>`).join('\n');
}

function renderReferencesHtml(references) {
  return references.map(ref => `
      <div class="flex gap-3 items-start">
        <span class="material-symbols-outlined text-[var(--secondary)] mt-0.5 text-[18px]">link</span>
        <div>
          <p class="text-[17px] leading-[1.55]">
            <a href="${ref.url}" target="_blank" class="text-[var(--secondary)] underline decoration-dotted hover:text-[var(--primary)]">${ref.name}</a>
            <span class="text-sm text-[var(--on-surface-variant)] ml-2">[${ref.type}]</span>
          </p>
        </div>
      </div>`).join('\n');
}

function renderChalkboardSection(chalkboardPrompt, chalkboardImageBase64, chalkboardImageMime, storyId) {
  const imgTag = chalkboardImageBase64
    ? `<img src="data:${chalkboardImageMime};base64,${chalkboardImageBase64}" alt="${storyId} 黑板畫參考" class="w-full rounded-lg shadow-md my-4" style="max-height: 400px; object-fit: contain;"/>`
    : '<p class="text-sm text-[var(--on-surface-variant)] italic">（黑板畫圖檔未找到）</p>';

  const promptHtml = chalkboardPrompt.englishPrompt
    ? `<div class="bg-[var(--bg-wash-3)]/50 rounded-lg p-4 my-3 text-sm leading-relaxed font-mono">
        <p class="font-label text-xs text-[var(--secondary)] mb-2 uppercase tracking-widest">Gemini Pro Prompt (English)</p>
        <p class="text-[14px] leading-[1.5]">${chalkboardPrompt.englishPrompt.replace(/\n/g, '<br/>')}</p>
      </div>
      <div class="bg-[var(--bg-wash-2)]/50 rounded-lg p-4 my-3 text-sm leading-relaxed">
        <p class="font-label text-xs text-[var(--secondary)] mb-2 uppercase tracking-widest">Gemini Pro Prompt (中文)</p>
        <p class="text-[14px] leading-[1.5]">${chalkboardPrompt.chinesePrompt.replace(/\n/g, '<br/>')}</p>
      </div>`
    : '';

  const iterHtml = chalkboardPrompt.iterations.length > 0
    ? `<div class="overflow-x-auto my-3">
        <table class="w-full text-[15px] leading-[1.5]">
          <thead><tr class="border-b border-[var(--outline-variant)]/40">
            <th class="text-left py-1.5 pr-3 font-medium text-[var(--primary)]">版本</th>
            <th class="text-left py-1.5 pr-3 font-medium text-[var(--primary)]">問題</th>
            <th class="text-left py-1.5 font-medium text-[var(--primary)]">修正</th>
          </tr></thead>
          <tbody class="text-[var(--on-surface-variant)]">
            ${chalkboardPrompt.iterations.map(it => `<tr class="border-b border-[var(--outline-variant)]/20"><td class="py-1 pr-3">${it.version}</td><td class="py-1 pr-3">${it.issue}</td><td class="py-1">${it.fix}</td></tr>`).join('\n')}
          </tbody>
        </table>
      </div>`
    : '';

  return { imgTag, promptHtml, iterHtml };
}

function renderStoryBreak() {
  return `
    <div class="flex justify-center gap-2 py-3 opacity-30">
      <span class="material-symbols-outlined text-[var(--primary)] text-sm">waves</span>
      <span class="material-symbols-outlined text-[var(--primary)] text-sm">waves</span>
      <span class="material-symbols-outlined text-[var(--primary)] text-sm">waves</span>
    </div>`;
}

function renderSectionDivider(dividerIcon) {
  return `
    <div class="flex justify-center gap-3 py-3 opacity-40">
      <span class="material-symbols-outlined text-[var(--secondary)] text-sm">${dividerIcon}</span>
      <span class="material-symbols-outlined text-[var(--secondary)] text-sm">${dividerIcon}</span>
      <span class="material-symbols-outlined text-[var(--secondary)] text-sm">${dividerIcon}</span>
    </div>`;
}

function renderStoryParagraphs(contentSections) {
  return contentSections.map((section, i) => {
    const paras = section.split(/\n{2,}/).map(p => p.trim()).filter(p => p && !p.startsWith('#') && !p.startsWith('>') && !p.startsWith('|'));
    return paras.map((p, j) => {
      p = p.replace(/\*\*(.+?)\*\*/g, '<span class="font-medium">$1</span>');
      if (p.includes('風來了') && p.includes('雨來了')) {
        const lines = p.split(/。/).filter(Boolean).map(l => l.trim() + '。');
        return `<p class="text-[18px] leading-[1.6] font-headline italic text-[var(--primary)]">${lines.join('<br/>')}</p>`;
      }
      if (p.includes('現在，它醒了')) {
        return `<p class="text-[18px] leading-[1.6] font-headline italic text-[var(--primary)]">${p}</p>`;
      }
      if (i === 0 && j === 0) {
        return `<p class="drop-cap text-[18px] leading-[1.6]">${p}</p>`;
      }
      return `<p class="text-[18px] leading-[1.6]">${p}</p>`;
    }).join('\n          ');
  });
}

// ── PDF 生成 ─────────────────────────────────────────
function generatePdf(htmlPath, pdfPath) {
  const pdfScript = path.resolve('publish/scripts/html-to-pdf.js');
  console.log(`[assemble] Generating PDF: ${pdfPath}`);
  const { execSync } = require('child_process');
  try {
    execSync(`node "${pdfScript}" "${htmlPath}" "${pdfPath}" --auto`, {
      stdio: 'inherit',
      cwd: process.cwd(),
    });
    console.log(`[assemble] PDF written: ${pdfPath}`);
    return true;
  } catch (e) {
    console.error(`[assemble] PDF generation failed: ${e.message}`);
    console.error(`[assemble] HTML is still available at: ${htmlPath}`);
    return false;
  }
}

// ── Google Drive 上傳 ────────────────────────────────
function uploadToDrive(folderId, storyId, filesToUpload, storyVersion) {
  if (!GWS_BIN) {
    console.warn('[upload] Skipped — no GWS CLI available. HTML/PDF saved locally.');
    console.warn('[upload] Install gws (npm install -g @googleworkspace/cli) and run gws auth login to enable upload.');
    return {};
  }

  const { execSync, spawnSync: spawnS } = require('child_process');
  const uploadResults = {};

  // GWS_BIN 可能是 'npx @googleworkspace/cli' 或 '/path/to/gws'
  // 拆成 [cmd, ...baseArgs] 供 spawnSync 陣列傳參（繞過 shell quoting）
  const gwsParts = GWS_BIN.split(' ');
  const gwsCmd = gwsParts[0];
  const gwsBase = gwsParts.slice(1);

  // Step 1: cleanup old files (only when no version suffix)
  if (storyVersion) {
    console.log(`[upload] Version mode (${storyVersion}): skipping cleanup, preserving old files.`);
  } else {
    console.log(`[upload] Cleaning old files for ${storyId}...`);
    try {
      // 用 spawnSync 陣列傳參：params JSON 裡的 single quotes 不會被 shell 解析
      const searchParams = JSON.stringify({
        q: `'${folderId}' in parents and trashed = false and name contains '${storyId}'`,
        fields: 'files(id,name)',
      });
      const searchResult = spawnS(gwsCmd, [
        ...gwsBase, 'drive', 'files', 'list',
        '--params', searchParams,
        '--format', 'json',
      ], { encoding: 'utf-8', timeout: 30000 });

      if (searchResult.status !== 0) {
        throw new Error(searchResult.stderr || `exit ${searchResult.status}`);
      }
      const searchParsed = JSON.parse(searchResult.stdout.trim());
      const oldFiles = (searchParsed.files || []);
      if (oldFiles.length > 0) {
        console.log(`[upload] Found ${oldFiles.length} old file(s) to remove:`);
        for (const old of oldFiles) {
          console.log(`[upload]   Deleting: ${old.name} (${old.id})`);
          const delResult = spawnS(gwsCmd, [
            ...gwsBase, 'drive', 'files', 'delete',
            '--params', JSON.stringify({ fileId: old.id }),
          ], { encoding: 'utf-8', timeout: 30000 });
          if (delResult.status !== 0) {
            console.error(`[upload]   Delete failed: ${old.name} — ${delResult.stderr}`);
          }
        }
        console.log(`[upload] Cleanup done.`);
      } else {
        console.log(`[upload] No old files found. Clean upload.`);
      }
    } catch (searchErr) {
      console.error(`[upload] Search/cleanup failed (non-fatal): ${searchErr.message}`);
    }
  }

  // Step 2: upload files
  for (const file of filesToUpload) {
    console.log(`[upload] Uploading ${file.driveName}...`);
    try {
      const result = execSync(
        `${GWS_BIN} drive +upload "${path.resolve(file.local)}" --parent ${folderId} --name "${file.driveName}"`,
        { encoding: 'utf-8', timeout: 120000 }
      );
      const parsed = JSON.parse(result.trim());
      uploadResults[file.driveName] = parsed.id;
      console.log(`[upload] OK: ${file.driveName} → ${parsed.id}`);
    } catch (e) {
      console.error(`[upload] FAILED: ${file.driveName} — ${e.message}`);
      uploadResults[file.driveName] = 'FAILED';
    }
  }

  return uploadResults;
}

// ── Exports ──────────────────────────────────────────
module.exports = {
  // Constants
  GWS_BIN,
  SEASON_ICONS, SEASON_LABELS, SEASON_DIVIDER_ICONS,

  // Season
  detectSeason,

  // Image utilities
  detectImageMime,

  // Markdown utilities
  stripFrontmatter, splitByHr, extractFrontmatter,
  extractPullQuote, mdParagraphsToHtml,

  // Parsers
  parseSourceUrls, extractShortNames,
  parseFactTable, parseChalkboardPrompt,
  parseImages, parseReferences,

  // Content extraction
  extractContentSections,

  // CLI
  parseCLIArgs,

  // File checks
  checkFiles,

  // Image search
  findChalkboardImage,

  // HTML rendering fragments
  renderFactTableHtml, renderImagesHtml, renderReferencesHtml,
  renderChalkboardSection, renderStoryBreak, renderSectionDivider,
  renderStoryParagraphs,

  // Output
  generatePdf,
  uploadToDrive,
};
