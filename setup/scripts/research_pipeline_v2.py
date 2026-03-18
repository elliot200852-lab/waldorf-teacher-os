#!/usr/bin/env python3
"""
TeacherOS API Research Pipeline v2
===================================
教師備課研究工具：輸入一個主題，自動串接五個免費 API，
產出結構化的備課素材（YAML + Markdown）。

v2 改動（相對原版）：
  - Python 3.8+ 相容（移除 3.10 union type syntax）
  - 年級對應難度過濾（CEFR 詞頻 + 詩歌行數閾值 + 詞彙數量）
  - 輸出路徑防禦（自動偵測 repo 根目錄）
  - 素材不足時的 fallback 提示
  - macOS / Windows 跨平台（純 Python，無 shell 依賴）

用法：
    python3 research_pipeline_v2.py "identity and belonging"
    python3 research_pipeline_v2.py "courage" --grade 9 --subject english
    python3 research_pipeline_v2.py "migration" --grade 7 --subject history

API（全部免費、不需要 Key）：
    1. PoetryDB        — 詩歌搜尋
    2. Datamuse         — 語義關聯、押韻、同義詞（含詞頻過濾）
    3. Free Dictionary  — 詞彙定義、音標、例句
    4. Gutendex         — Project Gutenberg 公版書搜尋
    5. Open Library     — 書目資料與延伸閱讀

作者：TeacherOS / David
"""

from __future__ import annotations

import argparse
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
    "poetrydb": "https://poetrydb.org",
    "datamuse": "https://api.datamuse.com",
    "dictionary": "https://api.dictionaryapi.dev/api/v2/entries/en",
    "gutendex": "https://gutendex.com",
    "openlibrary": "https://openlibrary.org",
}

API_DELAY = 0.3       # 秒，一般 API 間隔
API_DELAY_DICT = 1.0  # 秒，Free Dictionary 較嚴格
MAX_RETRIES = 3       # 429 重試次數

# ── Stopwords：拆關鍵字時排除 ─────────────────
# 這些字不會單獨作為搜尋詞，但完整片語仍保留
STOPWORDS = {
    # Determiners & pronouns
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "it", "its", "this", "that", "these", "those", "my", "your", "his",
    "her", "our", "their", "not", "no", "do", "does", "did", "has", "have",
    "had", "will", "would", "can", "could", "may", "might", "shall", "should",
    "so", "if", "as", "up", "out", "about", "into", "over", "after", "before",
    # Common ultra-generic words that pollute vocab/semantic results
    "one", "two", "three", "some", "any", "all", "each", "every", "other",
    "more", "most", "much", "many", "such", "own", "same", "than", "then",
    "also", "just", "only", "very", "too", "well", "still", "even",
    "way", "thing", "things", "something", "anything", "nothing",
    "line", "part", "set", "get", "got", "make", "made", "take", "took",
}

# ── 年級對應參數 ──────────────────────────────
# 台灣 7-9 年級英文程度約 CEFR A2-B1
# Datamuse frequency score: 越高 = 越常見
#   - 七年級（A2-）: 只取高頻詞，詩短、詞少
#   - 八年級（A2+）: 中高頻詞
#   - 九年級（B1） : 放寬到中頻詞

GRADE_PROFILES: Dict[int, Dict[str, Any]] = {
    7: {
        "label": "七年級 (A2-)",
        "max_poem_lines": 16,       # 短詩為主
        "max_poems": 8,
        "max_vocab_words": 8,       # 較少詞彙
        "max_semantic_words": 12,
        "freq_threshold": 8.0,      # Datamuse freq: 只取高頻（zipf >= 8）
        "max_books": 5,
    },
    8: {
        "label": "八年級 (A2+)",
        "max_poem_lines": 24,
        "max_poems": 10,
        "max_vocab_words": 10,
        "max_semantic_words": 16,
        "freq_threshold": 5.0,      # 中高頻
        "max_books": 6,
    },
    9: {
        "label": "九年級 (B1)",
        "max_poem_lines": 32,       # 可處理中長詩
        "max_poems": 10,
        "max_vocab_words": 12,
        "max_semantic_words": 20,
        "freq_threshold": 3.0,      # 放寬到中頻
        "max_books": 8,
    },
}


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
    # Fallback: script 所在目錄的上一層（假設在 tools/ 下）
    script_dir = Path(__file__).resolve().parent
    if script_dir.name == "tools":
        return script_dir.parent
    return script_dir


# ─────────────────────────────────────────────
# HTTP Helper
# ─────────────────────────────────────────────

def api_get(url: str, label: str = "", delay: float = 0) -> Optional[Union[Dict, List]]:
    """Safe GET with error handling, rate limiting, and 429 retry with backoff.
    Pass delay=API_DELAY_DICT for Free Dictionary calls."""
    wait = delay if delay > 0 else API_DELAY
    time.sleep(wait)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "TeacherOS-ResearchPipeline/2.0 (education tool)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"  + {label or url}")
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                backoff = wait * (2 ** attempt)  # 2s, 4s, 8s...
                print(f"  ~ {label or url} -- 429 rate limit, retry in {backoff:.0f}s ({attempt}/{MAX_RETRIES})")
                time.sleep(backoff)
                continue
            print(f"  x {label or url} -- HTTP {e.code}")
            return None
        except urllib.error.URLError as e:
            print(f"  x {label or url} -- {e.reason}")
            return None
        except Exception as e:
            print(f"  x {label or url} -- {e}")
            return None
    return None


# ─────────────────────────────────────────────
# Stage 1: Poetry Search (PoetryDB)
# ─────────────────────────────────────────────

def _poem_relevance(poem_lines: List[str], content_words: List[str]) -> int:
    """Count how many times any content keyword appears in the poem text.
    Title matches get a bonus of +5. Returns 0 for irrelevant poems."""
    text = " ".join(poem_lines).lower()
    score = 0
    for w in content_words:
        score += text.count(w)
    return score


def search_poems(keywords: List[str], profile: Dict[str, Any],
                 content_words: List[str] = None) -> List[Dict]:
    """Search PoetryDB; filter by line count AND relevance score."""
    max_lines = profile["max_poem_lines"]
    max_poems = profile["max_poems"]
    if content_words is None:
        content_words = keywords  # fallback

    print(f"\n[Stage 1] Searching poems (PoetryDB, max {max_lines} lines, relevance filter)...")
    poems: List[Dict] = []
    seen_titles: set = set()

    for kw in keywords:
        # Search by title
        url = f"{API_ENDPOINTS['poetrydb']}/title/{urllib.parse.quote(kw)}"
        data = api_get(url, f"poems by title: '{kw}'")
        if isinstance(data, list):
            for poem in data:
                if not isinstance(poem, dict):
                    continue
                title = poem.get("title", "")
                if title in seen_titles:
                    continue
                linecount = int(poem.get("linecount", len(poem.get("lines", []))))
                if linecount > max_lines:
                    continue
                lines_list = poem.get("lines", [])
                relevance = _poem_relevance(lines_list, content_words) + 5  # title match bonus
                seen_titles.add(title)
                poems.append({
                    "title": title,
                    "author": poem.get("author", "Unknown"),
                    "lines": lines_list,
                    "linecount": linecount,
                    "match_type": "title",
                    "keyword": kw,
                    "relevance": relevance,
                })

        # Search by lines (content)
        url = f"{API_ENDPOINTS['poetrydb']}/lines/{urllib.parse.quote(kw)}/author,title,lines,linecount"
        data = api_get(url, f"poems by content: '{kw}'")
        if isinstance(data, list):
            for poem in data:
                if not isinstance(poem, dict):
                    continue
                title = poem.get("title", "")
                if title in seen_titles:
                    continue
                linecount = int(poem.get("linecount", 0))
                if linecount > max_lines:
                    continue
                lines_list = poem.get("lines", [])
                relevance = _poem_relevance(lines_list, content_words)
                if relevance < 1:
                    continue  # skip: keyword doesn't actually appear in text
                seen_titles.add(title)
                poems.append({
                    "title": title,
                    "author": poem.get("author", "Unknown"),
                    "lines": lines_list,
                    "linecount": linecount,
                    "match_type": "content",
                    "keyword": kw,
                    "relevance": relevance,
                })

        if len(poems) >= max_poems:
            break

    # Sort: relevance first (high→low), then linecount (short→long)
    poems.sort(key=lambda p: (-p.get("relevance", 0), p.get("linecount", 999)))
    poems = poems[:max_poems]

    if not poems:
        print(f"  ! No poems found within {max_lines} lines. Consider raising grade or broadening topic.")
    else:
        print(f"  -> Found {len(poems)} poems (filtered: <={max_lines} lines, sorted by relevance)")
        for p in poems[:3]:
            print(f"     [{p['relevance']}] {p['title']} by {p['author']} ({p['linecount']}L)")
    return poems


# ─────────────────────────────────────────────
# Stage 2: Semantic Exploration (Datamuse)
#   with CEFR frequency filtering
# ─────────────────────────────────────────────

def explore_semantics(keywords: List[str], profile: Dict[str, Any]) -> Dict:
    """Build semantic field; filter by word frequency for grade level."""
    freq_threshold = profile["freq_threshold"]
    max_words = profile["max_semantic_words"]

    print(f"\n[Stage 2] Building semantic field (Datamuse, freq>={freq_threshold})...")
    result: Dict[str, Any] = {
        "related_words": [],
        "rhymes": [],
        "triggers": [],
        "synonyms": [],
        "adjectives": [],
    }

    primary_kw = keywords[0]

    # Meaning-related words — request with metadata (frequency tag)
    url = (
        f"{API_ENDPOINTS['datamuse']}/words"
        f"?ml={urllib.parse.quote(primary_kw)}"
        f"&md=f"  # request frequency metadata
        f"&max={max_words * 3}"  # request more, then filter
    )
    data = api_get(url, f"semantic field: '{primary_kw}'")
    if data:
        filtered = []
        for w in data:
            # Datamuse freq tag format: "tags": ["f:4.123"]
            freq = _extract_freq(w)
            if freq >= freq_threshold:
                filtered.append({
                    "word": w["word"],
                    "score": w.get("score", 0),
                    "freq": round(freq, 2),
                })
        result["related_words"] = filtered[:max_words]
        print(f"    freq filter: {len(data)} -> {len(filtered)} (kept freq>={freq_threshold})")

    # Rhymes
    url = f"{API_ENDPOINTS['datamuse']}/words?rel_rhy={urllib.parse.quote(primary_kw)}&max=10"
    data = api_get(url, f"rhymes: '{primary_kw}'")
    if data:
        result["rhymes"] = [w["word"] for w in data[:10]]

    # Associations (triggered by)
    url = f"{API_ENDPOINTS['datamuse']}/words?rel_trg={urllib.parse.quote(primary_kw)}&max=10"
    data = api_get(url, f"associations: '{primary_kw}'")
    if data:
        result["triggers"] = [w["word"] for w in data[:10]]

    # Synonyms
    url = f"{API_ENDPOINTS['datamuse']}/words?rel_syn={urllib.parse.quote(primary_kw)}&max=10"
    data = api_get(url, f"synonyms: '{primary_kw}'")
    if data:
        result["synonyms"] = [w["word"] for w in data[:10]]

    # Adjectives
    url = f"{API_ENDPOINTS['datamuse']}/words?rel_jjb={urllib.parse.quote(primary_kw)}&max=10"
    data = api_get(url, f"adjectives for: '{primary_kw}'")
    if data:
        result["adjectives"] = [w["word"] for w in data[:10]]

    total = sum(len(v) for v in result.values() if isinstance(v, list))
    print(f"  -> Collected {total} semantic connections")
    return result


def _extract_freq(word_entry: Dict) -> float:
    """Extract Zipf frequency from Datamuse tags. Returns 0.0 if missing."""
    for tag in word_entry.get("tags", []):
        if isinstance(tag, str) and tag.startswith("f:"):
            try:
                return float(tag[2:])
            except ValueError:
                pass
    return 0.0


# ─────────────────────────────────────────────
# Stage 3: Vocabulary Builder (Free Dictionary)
# ─────────────────────────────────────────────

def build_vocabulary(
    keywords: List[str], semantic_data: Dict, profile: Dict[str, Any],
    content_words: List[str] = None
) -> List[Dict]:
    """Build vocabulary cards; quantity adjusted by grade.
    Uses content_words (not keywords with phrases) to avoid noise."""
    max_vocab = profile["max_vocab_words"]

    print(f"\n[Stage 3] Building vocabulary cards (Free Dictionary, max {max_vocab})...")

    # Start with individual content words only (no phrases)
    base_words = content_words if content_words else keywords
    candidates: List[str] = [w for w in base_words if " " not in w]

    # Add semantic related words, but skip:
    #   - multi-word entries
    #   - very short words (a, an, the leaked through)
    #   - stopwords
    for w in semantic_data.get("related_words", []):
        word = w["word"]
        if (word not in candidates
                and " " not in word
                and len(word) > 2
                and word not in STOPWORDS):
            candidates.append(word)
    candidates = candidates[:max_vocab]

    vocab: List[Dict] = []
    for word in candidates:
        url = f"{API_ENDPOINTS['dictionary']}/{urllib.parse.quote(word)}"
        data = api_get(url, f"define: '{word}'", delay=API_DELAY_DICT)
        if not data or not isinstance(data, list):
            continue

        entry = data[0]
        card: Dict[str, Any] = {
            "word": entry.get("word", word),
            "phonetic": entry.get("phonetic", ""),
            "audio": "",
            "meanings": [],
        }

        # Audio URL
        for p in entry.get("phonetics", []):
            if p.get("audio"):
                card["audio"] = p["audio"]
                break

        # Meanings (max 2)
        for meaning in entry.get("meanings", [])[:2]:
            m: Dict[str, Any] = {
                "part_of_speech": meaning.get("partOfSpeech", ""),
                "definition": "",
                "example": "",
                "synonyms": [],
            }
            if meaning.get("definitions"):
                d = meaning["definitions"][0]
                m["definition"] = d.get("definition", "")
                m["example"] = d.get("example", "")
                m["synonyms"] = d.get("synonyms", [])[:5]
            card["meanings"].append(m)

        vocab.append(card)

    if len(vocab) < 3:
        print(f"  ! Only {len(vocab)} words found. Topic may be too narrow.")
    else:
        print(f"  -> Built {len(vocab)} vocabulary cards")
    return vocab


# ─────────────────────────────────────────────
# Stage 4: Literature Search (Gutendex + Open Library)
# ─────────────────────────────────────────────

def search_literature(keywords: List[str], profile: Dict[str, Any],
                      content_words: List[str] = None) -> Dict:
    """Search for related books. Uses content_words to avoid query duplication."""
    max_books = profile["max_books"]

    print(f"\n[Stage 4] Searching literature (Gutendex + Open Library, max {max_books})...")
    result: Dict[str, List] = {"gutenberg": [], "openlibrary": []}

    # Use content_words (deduplicated) for query, not keywords (which may contain phrases + singles)
    search_words = content_words if content_words else keywords
    query = " ".join(search_words)

    # Gutendex
    url = f"{API_ENDPOINTS['gutendex']}/books?search={urllib.parse.quote(query)}&languages=en"
    data = api_get(url, f"Gutenberg: '{query}'")
    if data and data.get("results"):
        for book in data["results"][:max_books]:
            authors = [a.get("name", "") for a in book.get("authors", [])]
            text_url = ""
            for fmt, link in book.get("formats", {}).items():
                if "text/plain" in fmt or "text/html" in fmt:
                    text_url = link
                    break
            result["gutenberg"].append({
                "id": book.get("id"),
                "title": book.get("title", ""),
                "authors": authors,
                "subjects": book.get("subjects", [])[:5],
                "download_count": book.get("download_count", 0),
                "text_url": text_url,
            })

    # Open Library
    url = (
        f"{API_ENDPOINTS['openlibrary']}/search.json"
        f"?q={urllib.parse.quote(query)}"
        f"&fields=title,author_name,first_publish_year,subject,key,cover_i"
        f"&limit={max_books}"
    )
    data = api_get(url, f"Open Library: '{query}'")
    if data and data.get("docs"):
        for doc in data["docs"][:max_books]:
            cover_url = ""
            if doc.get("cover_i"):
                cover_url = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
            ol_url = ""
            if doc.get("key"):
                ol_url = f"https://openlibrary.org{doc['key']}"
            result["openlibrary"].append({
                "title": doc.get("title", ""),
                "authors": doc.get("author_name", []),
                "year": doc.get("first_publish_year"),
                "subjects": doc.get("subject", [])[:5],
                "url": ol_url,
                "cover_url": cover_url,
            })

    total = len(result["gutenberg"]) + len(result["openlibrary"])
    print(f"  -> Found {total} books total")
    return result


# ─────────────────────────────────────────────
# Output Generators
# ─────────────────────────────────────────────

def generate_research_yaml(
    topic: str, grade: int, subject: str, profile: Dict[str, Any],
    poems: List, semantics: Dict, vocab: List, literature: Dict
) -> Dict:
    """Master research-output.yaml."""
    return {
        "meta": {
            "topic": topic,
            "grade": grade,
            "grade_profile": profile["label"],
            "subject": subject,
            "generated_at": datetime.now().isoformat(),
            "pipeline_version": "2.0",
            "apis_used": list(API_ENDPOINTS.keys()),
            "filters_applied": {
                "poem_max_lines": profile["max_poem_lines"],
                "vocab_freq_threshold": profile["freq_threshold"],
                "vocab_max_count": profile["max_vocab_words"],
            },
        },
        "poems": [
            {
                "title": p["title"],
                "author": p["author"],
                "linecount": p["linecount"],
                "match_keyword": p["keyword"],
                "usability_note": _poem_note(p["linecount"], grade),
            }
            for p in poems
        ],
        "semantic_field": semantics,
        "vocabulary": [
            {
                "word": v["word"],
                "phonetic": v["phonetic"],
                "primary_definition": v["meanings"][0]["definition"] if v["meanings"] else "",
                "part_of_speech": v["meanings"][0]["part_of_speech"] if v["meanings"] else "",
            }
            for v in vocab
        ],
        "literature": literature,
        "teaching_suggestions": {
            "recommended_poem": poems[0]["title"] if poems else "N/A",
            "core_vocabulary_count": len(vocab),
            "semantic_richness": len(semantics.get("related_words", [])),
            "available_public_domain_texts": len(literature.get("gutenberg", [])),
        },
        "quality_warnings": _quality_warnings(poems, vocab, semantics),
    }


def _poem_note(linecount: int, grade: int) -> str:
    if linecount <= 12:
        return "短詩，適合課堂精讀與朗誦"
    elif linecount <= 20:
        return "中等長度，適合引導式閱讀"
    else:
        if grade <= 7:
            return "偏長，建議節選 8-12 行"
        return "中長詩，建議節選重點段落"


def _quality_warnings(poems: List, vocab: List, semantics: Dict) -> List[str]:
    warnings: List[str] = []
    if len(poems) == 0:
        warnings.append("NO_POEMS: 未找到符合條件的詩歌。建議換主題或放寬年級。")
    elif len(poems) < 3:
        warnings.append(f"FEW_POEMS: 只找到 {len(poems)} 首，素材可能不足。")
    if len(vocab) < 3:
        warnings.append(f"FEW_VOCAB: 只建立 {len(vocab)} 張詞彙卡，建議補充。")
    if len(semantics.get("related_words", [])) < 5:
        warnings.append("THIN_SEMANTIC: 語義場偏薄，主題可能太窄。")
    return warnings


def generate_poems_md(poems: List) -> str:
    lines = ["# Poems Collection\n"]
    lines.append(f"> {len(poems)} poems found\n")

    for i, poem in enumerate(poems, 1):
        lines.append(f"## {i}. {poem['title']}")
        lines.append(f"**Author:** {poem['author']}  ")
        lines.append(f"**Lines:** {poem['linecount']}  ")
        lines.append(f"**Match:** {poem['match_type']} -> `{poem['keyword']}`\n")
        lines.append("```")
        lines.extend(poem.get("lines", []))
        lines.append("```\n")
        lines.append("---\n")

    return "\n".join(lines)


def generate_vocab_cards_md(
    vocab: List, semantics: Dict, grade: int
) -> str:
    """Simple vocabulary cards: word + phonetic + short definition + 5 daily-life examples."""
    lines = ["# Vocabulary Cards\n"]
    lines.append(f"> Grade {grade} | Simple definitions + daily-life examples\n")

    for card in vocab:
        word = card["word"]
        phonetic = card.get("phonetic", "")
        audio = card.get("audio", "")

        lines.append(f"## {word}")
        if phonetic:
            lines.append(f"**Say it:** {phonetic}")
        if audio:
            lines.append(f"**Listen:** [audio]({audio})")
        lines.append("")

        # Simple definition (first meaning only, keep it short)
        if card.get("meanings"):
            m = card["meanings"][0]
            pos = m.get("part_of_speech", "")
            defn = m.get("definition", "")
            if pos and defn:
                lines.append(f"**What it means** ({pos}): {defn}")
            elif defn:
                lines.append(f"**What it means:** {defn}")

            # Easier words if available
            syns = m.get("synonyms", [])[:3]
            if syns:
                lines.append(f"**Easier words:** {', '.join(syns)}")
        lines.append("")

        # 5 daily-life example sentences
        # We provide the API example if available, and placeholder prompts for the rest
        lines.append("**Examples in daily life:**")
        api_example = ""
        if card.get("meanings"):
            api_example = card["meanings"][0].get("example", "")
        if api_example:
            lines.append(f"1. *{api_example}*")
            start = 2
        else:
            start = 1
        # Fill remaining slots with guided prompts for the teacher to complete
        prompts = [
            f"Use **{word}** to describe something at school.",
            f"Use **{word}** to describe something at home.",
            f"Use **{word}** to describe a feeling.",
            f"Use **{word}** to talk about a friend.",
            f"Use **{word}** in a question.",
        ]
        for i in range(start, 6):
            idx = i - start
            if idx < len(prompts):
                lines.append(f"{i}. _{prompts[idx]}_")
        lines.append("")
        lines.append("---\n")

    return "\n".join(lines)


def generate_practice_sheet_md(
    topic: str, display_word: str, poems: List, vocab: List, semantics: Dict
) -> str:
    lines = ["# Practice Sheet\n"]
    lines.append(f"**Topic:** {topic}\n")

    # Part 1: Vocab matching
    if vocab:
        lines.append("## Part 1: Vocabulary Matching")
        lines.append("Match each word with its definition.\n")
        lines.append("| # | Word | Definition |")
        lines.append("|---|------|------------|")
        for i, card in enumerate(vocab[:8], 1):
            defn = card["meanings"][0]["definition"] if card.get("meanings") else ""
            lines.append(f"| {i} | {card['word']} | {defn} |")
        lines.append("")

    # Part 2: Rhyme
    rhymes = semantics.get("rhymes", [])
    if rhymes:
        lines.append("## Part 2: Sound & Rhyme")
        lines.append(f"These words rhyme with **{display_word}**: {', '.join(rhymes[:6])}\n")
        lines.append("**Task:** Choose 3 rhyming words and write a short verse (2-4 lines).\n")

    # Part 3: Poetry response
    if poems:
        poem = poems[0]
        lines.append("## Part 3: Poetry Response")
        lines.append(f'Re-read **"{poem["title"]}"** by {poem["author"]}.\n')
        lines.append("Answer ONE of the following:")
        lines.append("1. What image stayed with you after reading? Describe it.")
        lines.append("2. Choose one line that speaks to you. Why?")
        lines.append("3. If this poem were a colour, what would it be? Explain.\n")

    # Part 4: Creative writing
    triggers = semantics.get("triggers", [])
    if triggers:
        lines.append("## Part 4: Word Associations (Creative Writing)")
        lines.append(f"When people hear **{display_word}**, they think of: {', '.join(triggers[:6])}\n")
        lines.append("**Task:** Pick 2-3 words from the list above and write a short paragraph (5-8 sentences) that connects them.\n")

    return "\n".join(lines)


def generate_semantic_map_md(display_word: str, semantics: Dict) -> str:
    lines = ["# Semantic Map\n"]
    lines.append("```mermaid")
    lines.append("mindmap")

    primary = display_word.capitalize()
    lines.append(f"  root(({primary}))")

    syns = semantics.get("synonyms", [])[:5]
    if syns:
        lines.append("    Synonyms")
        for s in syns:
            lines.append(f"      {s}")

    related = semantics.get("related_words", [])[:6]
    if related:
        lines.append("    Related")
        for r in related:
            lines.append(f"      {r['word']}")

    adjs = semantics.get("adjectives", [])[:5]
    if adjs:
        lines.append("    Descriptions")
        for a in adjs:
            lines.append(f"      {a}")

    triggers = semantics.get("triggers", [])[:5]
    if triggers:
        lines.append("    Associations")
        for t in triggers:
            lines.append(f"      {t}")

    rhymes = semantics.get("rhymes", [])[:5]
    if rhymes:
        lines.append("    Rhymes")
        for r in rhymes:
            lines.append(f"      {r}")

    lines.append("```\n")
    lines.append("> Render in any Mermaid-compatible editor (Obsidian, GitHub, etc.)")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────

def run_pipeline(topic: str, grade: int = 9, subject: str = "english", workspace: str = "") -> Dict:
    """Execute the full research pipeline."""
    profile = GRADE_PROFILES.get(grade, GRADE_PROFILES[9])

    print("=" * 60)
    print("  TeacherOS API Research Pipeline v2")
    print(f"  Topic:   {topic}")
    print(f"  Grade:   {grade} ({profile['label']})")
    print(f"  Subject: {subject}")
    print(f"  Time:    {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Filters: poems<={profile['max_poem_lines']}L, freq>={profile['freq_threshold']}")
    print("=" * 60)

    # Parse keywords: filter stopwords, keep full phrase as first entry
    raw_words = [w.strip() for w in topic.lower().split() if w.strip()]
    content_words = [w for w in raw_words if w not in STOPWORDS and len(w) > 1]

    # Strategy: full phrase first (for PoetryDB line search), then individual words
    keywords: List[str] = []
    if len(content_words) >= 2:
        keywords.append(" ".join(content_words))  # e.g. "identity belonging"
    keywords.extend(content_words)
    # Deduplicate while preserving order
    seen: set = set()
    unique_kw: List[str] = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_kw.append(kw)
    keywords = unique_kw

    if not keywords:
        keywords = [topic.lower().strip()]
        content_words = keywords

    # display_word: the main content word(s) for display in outputs
    # e.g. "the sea" → "sea", "identity and belonging" → "identity"
    display_word = content_words[0] if content_words else topic.strip()
    print(f"\nKeywords: {keywords}")
    print(f"Display word: {display_word}")

    # Run stages
    poems = search_poems(keywords, profile, content_words)
    semantics = explore_semantics(keywords, profile)
    vocab = build_vocabulary(keywords, semantics, profile, content_words)
    literature = search_literature(keywords, profile, content_words)

    # Output
    print(f"\n[Stage 5] Generating outputs...")

    # 路徑防禦：嘗試找 repo 根目錄，fallback 到當前目錄
    repo_root = find_repo_root()
    if workspace:
        workspace_path = repo_root / workspace
        output_dir = workspace_path / "poetry_output" / topic.replace(" ", "-").lower()
    else:
        output_dir = repo_root / "output" / topic.replace(" ", "-").lower()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. YAML
    research_data = generate_research_yaml(
        topic, grade, subject, profile, poems, semantics, vocab, literature
    )
    yaml_path = output_dir / "research-output.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(research_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  + {yaml_path}")

    # 2. Poems
    poems_path = output_dir / "poems.md"
    with open(poems_path, "w", encoding="utf-8") as f:
        f.write(generate_poems_md(poems))
    print(f"  + {poems_path}")

    # 3. Vocab cards
    vocab_path = output_dir / "vocab-cards.md"
    with open(vocab_path, "w", encoding="utf-8") as f:
        f.write(generate_vocab_cards_md(vocab, semantics, grade))
    print(f"  + {vocab_path}")

    # 4. Practice sheet
    practice_path = output_dir / "practice-sheet.md"
    with open(practice_path, "w", encoding="utf-8") as f:
        f.write(generate_practice_sheet_md(topic, display_word, poems, vocab, semantics))
    print(f"  + {practice_path}")

    # 5. Semantic map
    map_path = output_dir / "semantic-map.md"
    with open(map_path, "w", encoding="utf-8") as f:
        f.write(generate_semantic_map_md(display_word, semantics))
    print(f"  + {map_path}")

    # Summary
    warnings = research_data.get("quality_warnings", [])
    print("\n" + "=" * 60)
    print("  Pipeline Complete!")
    print(f"  Output:  {output_dir}/")
    print(f"  Poems:   {len(poems)}")
    print(f"  Vocab:   {len(vocab)}")
    print(f"  Semantic: {len(semantics.get('related_words', []))}")
    print(f"  Books:   {len(literature.get('gutenberg', [])) + len(literature.get('openlibrary', []))}")
    if warnings:
        print(f"\n  WARNINGS:")
        for w in warnings:
            print(f"    ! {w}")
    print("=" * 60)

    return research_data


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TeacherOS API Research Pipeline v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 research_pipeline_v2.py "courage"
  python3 research_pipeline_v2.py "identity and belonging" --grade 9
  python3 research_pipeline_v2.py "the sea" --grade 8 --subject english
  python3 research_pipeline_v2.py "migration" --grade 7 --subject history
        """,
    )
    parser.add_argument("topic", help="Research topic (English)")
    parser.add_argument("--grade", type=int, default=9, choices=[7, 8, 9],
                        help="Grade level (7/8/9), default: 9")
    parser.add_argument("--subject", default="english",
                        help="Subject, default: english")
    parser.add_argument("--workspace", default="",
                        help="Teacher workspace path (e.g. workspaces/Working_Member/Codeowner_David/)")

    args = parser.parse_args()
    run_pipeline(args.topic, args.grade, args.subject, args.workspace)
