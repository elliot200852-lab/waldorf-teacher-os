#!/usr/bin/env python3
"""
TeacherOS Museum Resource Pipeline
====================================
博物館 API 素材管線：從 Met Museum 和 Europeana 搜集藝術作品 metadata，
生成統一 YAML 與課堂投影用 HTML 畫廊。

支援來源：
    1. Metropolitan Museum of Art（主要，免費 CC0，無需 key）
    2. Europeana（備案，需免費 API key）

用法：
    python3 museum_resource_pipeline.py "autumn landscape"
    python3 museum_resource_pipeline.py "van gogh" --source met --count 15 --gallery
    python3 museum_resource_pipeline.py "impressionism" --source both --europeana-key rboarikee --gallery
    python3 museum_resource_pipeline.py "rembrandt" --source europeana --europeana-key rboarikee --count 15

作者：TeacherOS / David
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# PyYAML: 唯一外部依賴
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml --break-system-packages")
    sys.exit(1)


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

API_ENDPOINTS = {
    "met_search": "https://collectionapi.metmuseum.org/public/collection/v1/search",
    "met_object": "https://collectionapi.metmuseum.org/public/collection/v1/objects",
    "europeana": "https://api.europeana.eu/record/v2/search.json",
}

API_DELAY_MET = 0.15       # Met 允許較快的請求
API_DELAY_EUROPEANA = 0.3  # Europeana 稍慢
MAX_RETRIES = 3


# ─────────────────────────────────────────────
# Utility: Detect repo root
# ─────────────────────────────────────────────

def find_repo_root() -> Path:
    """Try git rev-parse; fallback to script directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    # Fallback: script 所在目錄的上兩層（setup/scripts/）
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent.parent


# ─────────────────────────────────────────────
# HTTP Helper
# ─────────────────────────────────────────────

def api_get(url: str, label: str = "", delay: float = 0.3) -> Optional[Union[Dict, List]]:
    """Safe GET with error handling, rate limiting, and 429 retry."""
    time.sleep(delay)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "TeacherOS-MuseumPipeline/1.0 (education tool)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                backoff = delay * (2 ** attempt)
                print(f"  ~ {label} -- 429 rate limit, retry in {backoff:.0f}s ({attempt}/{MAX_RETRIES})")
                time.sleep(backoff)
                continue
            print(f"  x {label} -- HTTP {e.code}")
            return None
        except urllib.error.URLError as e:
            print(f"  x {label} -- {e.reason}")
            return None
        except Exception as e:
            print(f"  x {label} -- {e}")
            return None
    return None


# ─────────────────────────────────────────────
# Europeana: Clean dirty dcCreator fields
# ─────────────────────────────────────────────

def clean_creator(raw: str) -> str:
    """Europeana dcCreator sometimes returns URLs or coded strings.
    Try to extract a human-readable name."""
    if not raw:
        return ""
    # Skip URLs
    if raw.startswith("http://") or raw.startswith("https://"):
        return ""
    # Skip codes like '188_person'
    if "_" in raw and raw.split("_")[0].isdigit():
        return ""
    return raw.strip()


# ─────────────────────────────────────────────
# Safe array extraction for Europeana
# ─────────────────────────────────────────────

def safe_first(value: Any, default: str = "") -> str:
    """Extract first element from list or return string as-is."""
    if isinstance(value, list):
        return str(value[0]) if value else default
    if value is None:
        return default
    return str(value)


def parse_europeana_rights(rights_url: str) -> str:
    """Convert Europeana rights URL to human-readable license."""
    if not rights_url:
        return "Unknown"
    url_lower = rights_url.lower()
    if "publicdomain" in url_lower or "/mark/" in url_lower:
        return "Public Domain"
    if "creativecommons.org/licenses/by-nc-sa" in url_lower:
        return "CC BY-NC-SA"
    if "creativecommons.org/licenses/by-nc-nd" in url_lower:
        return "CC BY-NC-ND"
    if "creativecommons.org/licenses/by-nc" in url_lower:
        return "CC BY-NC"
    if "creativecommons.org/licenses/by-sa" in url_lower:
        return "CC BY-SA"
    if "creativecommons.org/licenses/by-nd" in url_lower:
        return "CC BY-ND"
    if "creativecommons.org/licenses/by" in url_lower:
        return "CC BY"
    if "creativecommons.org" in url_lower:
        return "CC (see link)"
    if "rightsstatements.org" in url_lower:
        # Extract the short code from URL path
        parts = [p for p in rights_url.rstrip("/").split("/") if p]
        if len(parts) >= 2:
            return parts[-2]  # e.g. "InC" for In Copyright
    return "See source"


# ─────────────────────────────────────────────
# Met Museum API
# ─────────────────────────────────────────────

def search_met(query: str, count: int, public_domain_only: bool = False) -> List[Dict]:
    """Search Met Museum API: 2-step (search -> fetch details)."""
    print(f"\n{'='*50}")
    print(f"Met Museum API: \"{query}\" (max {count})")
    print(f"{'='*50}")

    # Step 1: Search
    params = {"q": query, "hasImages": "true"}
    if public_domain_only:
        params["isPublicDomain"] = "true"
    search_url = f"{API_ENDPOINTS['met_search']}?{urllib.parse.urlencode(params)}"
    data = api_get(search_url, "Met search", delay=API_DELAY_MET)

    if not data:
        print("  ! Met search returned no data")
        return []

    total = data.get("total", 0)
    object_ids = data.get("objectIDs") or []
    print(f"  Found {total} results, fetching items with images (target: {count})...")

    # Step 2: Fetch individual objects, SKIP those without images
    # Cap scanning at 5x target to avoid runaway API calls
    max_scan = min(count * 5, len(object_ids))
    items = []
    fetched = 0
    for oid in object_ids[:max_scan]:
        if len(items) >= count:
            break
        obj_url = f"{API_ENDPOINTS['met_object']}/{oid}"
        obj = api_get(obj_url, f"Met #{oid}", delay=API_DELAY_MET)
        fetched += 1
        if not obj:
            continue

        # Skip items without images — no point showing empty placeholders
        image_url = obj.get("primaryImage", "")
        if not image_url:
            sys.stdout.write("-")
            sys.stdout.flush()
            continue

        item = {
            "id": f"met_{oid}",
            "title": obj.get("title", ""),
            "title_zh": "",
            "artist": obj.get("artistDisplayName", ""),
            "date": obj.get("objectDate", ""),
            "period": obj.get("department", ""),
            "medium": obj.get("medium", ""),
            "image_url": image_url,
            "thumb_url": obj.get("primaryImageSmall", ""),
            "source_url": obj.get("objectURL", ""),
            "license": "CC0" if obj.get("isPublicDomain") else "Restricted",
            "api_source": "met",
            "desc_zh": "",
            "teaching_notes": {},
        }
        items.append(item)
        sys.stdout.write("+")
        sys.stdout.flush()

    print(f"\n  Met: {len(items)} items with images (scanned {fetched} objects)")
    return items


# ─────────────────────────────────────────────
# Europeana API
# ─────────────────────────────────────────────

def search_europeana(query: str, count: int, api_key: str) -> List[Dict]:
    """Search Europeana API: 1-step (search returns metadata inline)."""
    print(f"\n{'='*50}")
    print(f"Europeana API: \"{query}\" (max {count})")
    print(f"{'='*50}")

    params = {
        "wskey": api_key,
        "query": query,
        "rows": str(count),
        "qf": "TYPE:IMAGE",
    }
    search_url = f"{API_ENDPOINTS['europeana']}?{urllib.parse.urlencode(params)}"
    data = api_get(search_url, "Europeana search", delay=API_DELAY_EUROPEANA)

    if not data:
        print("  ! Europeana search returned no data")
        return []

    if not data.get("success", False):
        print(f"  ! Europeana error: {data.get('error', 'unknown')}")
        return []

    total = data.get("totalResults", 0)
    raw_items = data.get("items", [])
    print(f"  Found {total} results, processing {len(raw_items)}...")

    items = []
    for raw in raw_items:
        # Extract and clean fields
        title = safe_first(raw.get("title"), "(untitled)")
        creator_raw = safe_first(raw.get("dcCreator"), "")
        creator = clean_creator(creator_raw)
        year = safe_first(raw.get("year"), "")
        preview = safe_first(raw.get("edmPreview"), "")
        shown_by = safe_first(raw.get("edmIsShownBy"), "")
        shown_at = safe_first(raw.get("edmIsShownAt"), "")
        guid = raw.get("guid", "")
        rights_url = safe_first(raw.get("rights"), "")
        provider = safe_first(raw.get("dataProvider"), "")
        euro_id = raw.get("id", "")

        # Use edmIsShownBy for full image, fallback to edmPreview
        image_url = shown_by if shown_by else preview
        source_url = shown_at if shown_at else guid

        # Skip items without any image
        if not image_url:
            sys.stdout.write("-")
            sys.stdout.flush()
            continue

        item = {
            "id": f"euro_{euro_id.replace('/', '_')}",
            "title": title,
            "title_zh": "",
            "artist": creator,
            "date": year,
            "period": provider,  # Use provider as context (Europeana lacks period field)
            "medium": "",
            "image_url": image_url,
            "thumb_url": preview,
            "source_url": source_url,
            "license": parse_europeana_rights(rights_url),
            "api_source": "europeana",
            "desc_zh": "",
            "teaching_notes": {},
        }
        items.append(item)
        sys.stdout.write("+")
        sys.stdout.flush()

    print(f"\n  Europeana: {len(items)} items collected")
    return items


# ─────────────────────────────────────────────
# HTML Gallery Generator
# ─────────────────────────────────────────────

def generate_gallery_html(items: List[Dict], query: str, timestamp: str) -> str:
    """Generate a self-contained HTML gallery with split layout (image left, info right)."""

    # Prepare items JSON for embedding
    items_json = []
    for item in items:
        items_json.append({
            "id": item["id"],
            "title": html_mod.escape(item["title"]),
            "title_zh": html_mod.escape(item.get("title_zh", "")),
            "artist": html_mod.escape(item.get("artist", "") or ""),
            "date": html_mod.escape(item.get("date", "")),
            "period": html_mod.escape(item.get("period", "")),
            "medium": html_mod.escape(item.get("medium", "")),
            "image_url": item.get("image_url", ""),
            "thumb_url": item.get("thumb_url", "") or item.get("image_url", ""),
            "source_url": item.get("source_url", ""),
            "license": html_mod.escape(item.get("license", "")),
            "api_source": item.get("api_source", ""),
            "desc_zh": html_mod.escape(item.get("desc_zh", "")),
        })

    items_js = json.dumps(items_json, ensure_ascii=False, indent=2)
    query_escaped = html_mod.escape(query)
    total = len(items)

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{query_escaped} — TeacherOS Museum Gallery</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: #1a1a2e;
  color: #e0e0e0;
  font-family: "Noto Serif TC", "Georgia", "Times New Roman", serif;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}}

/* ── Main split layout ── */
.main {{
  flex: 1;
  display: flex;
  min-height: 0;
}}

/* Left: image viewer */
.image-panel {{
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: #111;
  overflow: hidden;
}}
.image-panel img {{
  max-width: 92%;
  max-height: 92%;
  object-fit: contain;
  cursor: pointer;
  transition: opacity 0.3s;
}}
.image-panel .placeholder {{
  color: #555;
  text-align: center;
  padding: 40px;
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.image-panel .placeholder a {{ color: #c0a060; }}

/* Nav arrows */
.nav-btn {{
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0,0,0,0.4);
  color: rgba(255,255,255,0.7);
  border: none;
  font-size: 28px;
  padding: 20px 10px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s;
}}
.nav-btn:hover {{ background: rgba(0,0,0,0.7); color: #fff; }}
.nav-btn.prev {{ left: 0; border-radius: 0 4px 4px 0; }}
.nav-btn.next {{ right: 0; border-radius: 4px 0 0 4px; }}

/* Right: info panel */
.info-panel {{
  width: 380px;
  min-width: 340px;
  background: #16213e;
  border-left: 1px solid #2a2a4a;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}}

/* Museum header */
.museum-header {{
  padding: 20px 28px 0;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}}
.museum-name {{
  font-size: 11px;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: #667;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-weight: 400;
}}
.counter {{
  font-size: 13px;
  color: #556;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

/* Query title */
.query-title {{
  padding: 6px 28px 16px;
  font-size: 20px;
  color: #d0d0d0;
  font-weight: 400;
  border-bottom: 1px solid #2a2a4a;
}}

/* Period tag */
.period-section {{
  padding: 20px 28px 0;
}}
.period-tag {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.period-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c0a060;
}}
.period-dot.met {{ background: #e07050; }}
.period-dot.europeana {{ background: #50b080; }}

/* Title section */
.title-section {{
  padding: 16px 28px 0;
}}
.title-zh {{
  font-size: 26px;
  color: #c0a060;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 4px;
}}
.title-en {{
  font-size: 15px;
  color: #999;
  font-style: italic;
  line-height: 1.4;
}}

/* Description */
.desc-section {{
  padding: 16px 28px 0;
  flex: 1;
}}
.desc-text {{
  font-size: 14px;
  color: #aab;
  line-height: 1.7;
}}

/* Notes area */
.notes-section {{
  padding: 12px 28px;
  margin-top: auto;
}}
.notes-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}}
.notes-label {{
  font-size: 11px;
  color: #556;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.export-btn {{
  background: none;
  border: 1px solid #334;
  color: #778;
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 3px;
  cursor: pointer;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  transition: all 0.2s;
}}
.export-btn:hover {{ border-color: #c0a060; color: #c0a060; }}
.notes-area {{
  width: 100%;
  min-height: 60px;
  background: #1a1a35;
  border: 1px solid #2a2a4a;
  border-radius: 6px;
  color: #889;
  font-size: 13px;
  padding: 10px 12px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}}
.notes-area:focus {{ border-color: #c0a060; color: #ccc; }}
.notes-area::placeholder {{ color: #445; }}

/* Source link */
.source-section {{
  padding: 8px 28px 16px;
}}
.source-link {{
  font-size: 13px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.source-link a {{
  color: #7799bb;
  text-decoration: none;
  transition: color 0.2s;
}}
.source-link a:hover {{ color: #99bbdd; }}

/* ── Bottom thumbnail strip ── */
.thumbs {{
  display: flex;
  gap: 3px;
  padding: 6px 12px;
  background: #0d0d1a;
  overflow-x: auto;
  flex-shrink: 0;
  border-top: 1px solid #1a1a30;
}}
.thumbs img {{
  width: 56px;
  height: 56px;
  object-fit: cover;
  border: 2px solid transparent;
  border-radius: 3px;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.2s;
  flex-shrink: 0;
}}
.thumbs img.active {{
  border-color: #c0a060;
  opacity: 1;
}}
.thumbs img:hover {{ opacity: 0.8; }}
</style>
</head>
<body>

<div class="main">
  <!-- Left: Image -->
  <div class="image-panel" id="image-panel">
    <button class="nav-btn prev" onclick="navigate(-1)">&lsaquo;</button>
    <img id="main-img" src="" alt="" onclick="openSource()">
    <div class="placeholder" id="placeholder" style="display:none;">
      Image unavailable<br><a href="#" id="placeholder-link" target="_blank">View on source website</a>
    </div>
    <button class="nav-btn next" onclick="navigate(1)">&rsaquo;</button>
  </div>

  <!-- Right: Info -->
  <div class="info-panel">
    <div class="museum-header">
      <span class="museum-name" id="museum-name"></span>
      <span class="counter"><span id="current-num">1</span> / {total}</span>
    </div>
    <div class="query-title">{query_escaped}</div>

    <div class="period-section">
      <span class="period-tag">
        <span class="period-dot" id="period-dot"></span>
        <span id="period-text"></span>
      </span>
    </div>

    <div class="title-section">
      <div class="title-zh" id="title-zh"></div>
      <div class="title-en" id="title-en"></div>
    </div>

    <div class="desc-section">
      <div class="desc-text" id="desc-text"></div>
    </div>

    <div class="notes-section">
      <div class="notes-header">
        <span class="notes-label">Teaching Notes</span>
        <button class="export-btn" onclick="exportNotes()">Export All</button>
      </div>
      <textarea class="notes-area" id="notes-area" placeholder="Write teaching notes for this artwork..."></textarea>
    </div>

    <div class="source-section">
      <div class="source-link" id="source-link"></div>
    </div>
  </div>
</div>

<div class="thumbs" id="thumbs"></div>

<script>
const ITEMS = {items_js};
let currentIndex = 0;
const notes = {{}};  // Store notes per item index

function showItem(index) {{
  if (index < 0 || index >= ITEMS.length) return;
  // Save current notes before switching
  notes[currentIndex] = document.getElementById('notes-area').value;
  currentIndex = index;
  const item = ITEMS[index];
  const img = document.getElementById('main-img');
  const placeholder = document.getElementById('placeholder');

  // Image
  if (item.image_url) {{
    img.style.display = 'block';
    placeholder.style.display = 'none';
    img.src = item.image_url;
    img.alt = item.title;
    img.onerror = function() {{
      img.style.display = 'none';
      placeholder.style.display = 'block';
      document.getElementById('placeholder-link').href = item.source_url || '#';
    }};
  }} else {{
    img.style.display = 'none';
    placeholder.style.display = 'block';
    document.getElementById('placeholder-link').href = item.source_url || '#';
  }}

  // Museum name
  const museumNames = {{
    'met': 'THE METROPOLITAN MUSEUM OF ART',
    'europeana': 'EUROPEANA'
  }};
  document.getElementById('museum-name').textContent = museumNames[item.api_source] || item.api_source.toUpperCase();
  document.getElementById('current-num').textContent = index + 1;

  // Period dot color
  const dot = document.getElementById('period-dot');
  dot.className = 'period-dot ' + item.api_source;

  // Period / meta info
  let periodParts = [];
  if (item.period) periodParts.push(item.period);
  if (item.date) periodParts.push(item.date);
  document.getElementById('period-text').textContent = periodParts.join(' \\u00b7 ') || '';

  // Titles
  document.getElementById('title-zh').textContent = item.title_zh || item.title;
  const enParts = [item.title];
  if (item.date && !item.title.includes(item.date)) enParts.push(item.date);
  document.getElementById('title-en').textContent =
    item.title_zh ? enParts.join(', ') : (item.artist ? item.artist + (item.date ? ', ' + item.date : '') : '');

  // Description
  let descParts = [];
  if (item.desc_zh) descParts.push(item.desc_zh);
  if (item.medium) descParts.push(item.medium);
  if (item.artist && item.title_zh) descParts.push(item.artist);
  document.getElementById('desc-text').textContent = descParts.join('\\n');

  // Notes (restore saved)
  document.getElementById('notes-area').value = notes[index] || '';

  // Source link
  if (item.source_url) {{
    const licBadge = item.license ? ' (' + item.license + ')' : '';
    document.getElementById('source-link').innerHTML =
      '\\u2192 <a href="' + item.source_url + '" target="_blank">View on source website</a>' + licBadge;
  }} else {{
    document.getElementById('source-link').innerHTML = '';
  }}

  // Thumbnails
  document.querySelectorAll('.thumbs img').forEach((t, i) => {{
    t.classList.toggle('active', i === index);
  }});
  const activeThumb = document.querySelector('.thumbs img.active');
  if (activeThumb) activeThumb.scrollIntoView({{ behavior: 'smooth', inline: 'center' }});
}}

function navigate(dir) {{
  const next = currentIndex + dir;
  if (next >= 0 && next < ITEMS.length) showItem(next);
}}

function openSource() {{
  const item = ITEMS[currentIndex];
  if (item.source_url) window.open(item.source_url, '_blank');
}}

// Export all notes as Markdown download
function exportNotes() {{
  // Save current before export
  notes[currentIndex] = document.getElementById('notes-area').value;
  let md = '# Teaching Notes\\n\\n';
  let hasNotes = false;
  ITEMS.forEach((item, i) => {{
    if (notes[i] && notes[i].trim()) {{
      hasNotes = true;
      const titleLine = item.title_zh ? item.title_zh + '  ' + item.title : item.title;
      md += '## ' + (i+1) + '. ' + titleLine + '\\n';
      if (item.artist) md += '*' + item.artist + (item.date ? ', ' + item.date : '') + '*\\n\\n';
      md += notes[i].trim() + '\\n\\n';
      if (item.source_url) md += '[Source](' + item.source_url + ')\\n\\n';
      md += '---\\n\\n';
    }}
  }});
  if (!hasNotes) {{
    alert('No notes to export.');
    return;
  }}
  const blob = new Blob([md], {{ type: 'text/markdown' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'teaching-notes-{query_escaped}.md';
  a.click();
}}

// Keyboard navigation (only when textarea not focused)
document.addEventListener('keydown', (e) => {{
  if (document.activeElement.tagName === 'TEXTAREA') return;
  if (e.key === 'ArrowLeft') navigate(-1);
  if (e.key === 'ArrowRight') navigate(1);
  if (e.key === 'Home') showItem(0);
  if (e.key === 'End') showItem(ITEMS.length - 1);
}});

// Build thumbnail strip
const thumbsContainer = document.getElementById('thumbs');
ITEMS.forEach((item, i) => {{
  const img = document.createElement('img');
  img.src = item.thumb_url || item.image_url || '';
  img.alt = item.title;
  img.onclick = () => showItem(i);
  img.onerror = function() {{ this.style.background = '#333'; this.alt = '?'; }};
  thumbsContainer.appendChild(img);
}});

// Show first item
if (ITEMS.length > 0) showItem(0);
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# YAML Output
# ─────────────────────────────────────────────

def write_yaml(items: List[Dict], query: str, source: str, grade: int,
               output_dir: Path, timestamp: str) -> Path:
    """Write unified YAML output."""
    output = {
        "query": query,
        "api_source": source,
        "grade": grade,
        "timestamp": timestamp,
        "total_results": len(items),
        "items": items,
    }
    yaml_path = output_dir / "museum-materials.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return yaml_path


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="TeacherOS Museum Resource Pipeline: Search Met Museum & Europeana for art resources."
    )
    parser.add_argument("query", help="Search keyword(s)")
    parser.add_argument("--source", choices=["met", "europeana", "both"], default="met",
                        help="API source (default: met)")
    parser.add_argument("--count", type=int, default=15,
                        help="Max items per source (default: 15)")
    parser.add_argument("--grade", type=int, choices=[7, 8, 9], default=9,
                        help="Target grade (default: 9)")
    parser.add_argument("--workspace", type=str, default="",
                        help="Teacher workspace path (relative to repo root)")
    parser.add_argument("--europeana-key", type=str, default="",
                        help="Europeana API key (fallback: EUROPEANA_API_KEY env var)")
    parser.add_argument("--gallery", action="store_true",
                        help="Generate HTML gallery")
    parser.add_argument("--public-domain", action="store_true",
                        help="Met: only return public domain items")
    parser.add_argument("--from-yaml", type=str, default="",
                        help="Regenerate gallery from an existing enriched YAML file (skip API search)")
    args = parser.parse_args()

    # Resolve Europeana key
    europeana_key = args.europeana_key or os.environ.get("EUROPEANA_API_KEY", "")
    if args.source in ("europeana", "both") and not europeana_key:
        print("ERROR: Europeana API key required.")
        print("  Provide via --europeana-key or set EUROPEANA_API_KEY env var.")
        print("  Get a free key at: https://pro.europeana.eu/pages/get-api")
        sys.exit(1)

    # ── Regenerate mode: skip API, read existing YAML ──
    if args.from_yaml:
        from_yaml_path = Path(args.from_yaml)
        if not from_yaml_path.exists():
            print(f"ERROR: YAML file not found: {from_yaml_path}")
            sys.exit(1)
        with open(from_yaml_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
        all_items = yaml_data.get("items", [])
        query = yaml_data.get("query", args.query)
        output_dir = from_yaml_path.parent
        timestamp = yaml_data.get("timestamp", datetime.now().strftime("%Y%m%d-%H%M%S"))

        print(f"\nTeacherOS Museum Resource Pipeline — Regenerate Mode")
        print(f"{'='*40}")
        print(f"Source YAML: {from_yaml_path}")
        print(f"Items:       {len(all_items)}")

        if not all_items:
            print("\n! No items in YAML.")
            sys.exit(0)

        # Generate gallery
        print(f"\nRegenerating gallery...")
        gallery_html = generate_gallery_html(all_items, query, timestamp)
        gallery_path = output_dir / "gallery.html"
        with open(gallery_path, "w", encoding="utf-8") as f:
            f.write(gallery_html)
        print(f"  Gallery: {gallery_path}")

        print(f"\n{'='*40}")
        print(f"DONE: gallery regenerated with {len(all_items)} items")
        print(f"Gallery: {gallery_path}")
        return str(output_dir)

    # Resolve output directory
    repo_root = find_repo_root()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Sanitize for filesystem (remove chars invalid on Windows)
    import re
    query_slug = re.sub(r'[<>:"/\\|?*]', '', args.query).replace(" ", "_")[:30]

    if args.workspace:
        output_dir = repo_root / args.workspace / "museum_output" / f"{query_slug}_{timestamp[:8]}"
    else:
        output_dir = repo_root / "temp" / f"museum_{query_slug}_{timestamp[:8]}"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nTeacherOS Museum Resource Pipeline")
    print(f"{'='*40}")
    print(f"Query:   {args.query}")
    print(f"Source:  {args.source}")
    print(f"Count:   {args.count}")
    print(f"Grade:   {args.grade}")
    print(f"Output:  {output_dir}")

    # ── Stage 1: Search & Collect ──
    all_items = []  # type: List[Dict]

    if args.source in ("met", "both"):
        met_items = search_met(args.query, args.count, args.public_domain)
        all_items.extend(met_items)

    if args.source in ("europeana", "both"):
        euro_items = search_europeana(args.query, args.count, europeana_key)
        all_items.extend(euro_items)

    if not all_items:
        print("\n! No items found. Try different keywords.")
        sys.exit(0)

    # Write YAML
    yaml_path = write_yaml(all_items, args.query, args.source, args.grade, output_dir, timestamp)
    print(f"\n  YAML: {yaml_path}")

    # ── Stage 2: HTML Gallery ──
    if args.gallery:
        print(f"\nGenerating gallery...")
        gallery_html = generate_gallery_html(all_items, args.query, timestamp)
        gallery_path = output_dir / "gallery.html"
        with open(gallery_path, "w", encoding="utf-8") as f:
            f.write(gallery_html)
        print(f"  Gallery: {gallery_path}")

    # ── Summary ──
    print(f"\n{'='*40}")
    print(f"DONE: {len(all_items)} items collected")
    if args.source == "both":
        met_count = sum(1 for i in all_items if i["api_source"] == "met")
        euro_count = sum(1 for i in all_items if i["api_source"] == "europeana")
        print(f"  Met: {met_count}  |  Europeana: {euro_count}")

    # Summary table
    print(f"\n{'No.':<4} {'Source':<10} {'Img':<4} {'Title':<45} {'Artist':<25}")
    print("-" * 90)
    for i, item in enumerate(all_items, 1):
        has_img = "Y" if item.get("image_url") else "-"
        title = item["title"][:43]
        artist = (item.get("artist") or "?")[:23]
        src = item["api_source"][:8]
        print(f"{i:<4} {src:<10} {has_img:<4} {title:<45} {artist:<25}")

    print(f"\nOutput directory: {output_dir}")
    if args.gallery:
        print(f"Gallery: {output_dir / 'gallery.html'}")

    return str(output_dir)


if __name__ == "__main__":
    main()
