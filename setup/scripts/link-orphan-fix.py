#!/usr/bin/env python3
"""
link-orphan-fix.py — 批量補齊 LINK_ORPHAN 檔案的 related: 與 ## 連結

用法：
    python3 link-orphan-fix.py              # dry-run（顯示計劃，不寫入）
    python3 link-orphan-fix.py --apply      # 實際寫入所有類型
    python3 link-orphan-fix.py --type story # 只處理 story_content + story_component
    python3 link-orphan-fix.py --type wiki  # 只處理 wiki_entry + concept_page
    python3 link-orphan-fix.py --apply --type story

邏輯：
    story_content   → related: 連到同目錄的 narration/images/chalkboard-prompt
                      若有 published_url → 加 CreatorHub 外部連結
                      ## 連結 section 放在 body 末尾
    story_component → related: 連回 {ID}-content
                      若自身有 published_url → 加 CreatorHub 外部連結
    wiki_entry      → related: 來自 source_plan + 相鄰 wiki 頁 + 概念頁匹配
                      ## 連結 section
    concept_page    → ## 連結 section（從 related: frontmatter 複製）
"""

import os
import re
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # setup/scripts/ → 上兩層


# ── 工具函式 ───────────────────────────────────────────────

def get_link_orphans():
    """執行 obsidian-check.py --link-check，回傳 [(filepath, type, [missing...])]"""
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "obsidian-check.py"), "--link-check"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    orphans = []
    for line in result.stdout.splitlines():
        if line.startswith("FILE:LINK_ORPHAN:"):
            rest = line[len("FILE:LINK_ORPHAN:"):]
            parts = rest.split("|")
            if len(parts) >= 3:
                filepath = parts[0]
                file_type = parts[1]
                missing = parts[2].replace("missing:", "").split("+")
                orphans.append((filepath, file_type, missing))
    return orphans


def read_file(filepath):
    full_path = os.path.join(REPO_ROOT, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return None


def write_file(filepath, content):
    full_path = os.path.join(REPO_ROOT, filepath)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_frontmatter(content):
    """回傳 (frontmatter_text, after_closing_dashes) 或 None"""
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end < 0:
        return None
    return content[3:end], content[end + 4:]  # after_closing = \n\n# body...


def has_related(fm_text):
    """frontmatter 中是否已有 related: 欄位"""
    return bool(re.search(r"^related:", fm_text, re.MULTILINE))


def inject_related(content, related_items):
    """在 frontmatter 末尾加入 related:，若已存在則跳過"""
    parsed = get_frontmatter(content)
    if parsed is None:
        return content
    fm_text, after = parsed
    if has_related(fm_text):
        return content

    related_yaml = "related:\n"
    for item in related_items:
        related_yaml += f'  - "{item}"\n'

    new_fm = fm_text.rstrip() + "\n" + related_yaml
    return "---" + new_fm + "\n---" + after


def has_link_section(content):
    return "## 連結" in content


def append_link_section(content, links):
    """在檔案末尾加入 ## 連結 section，若已存在則跳過"""
    if has_link_section(content):
        return content
    section = "\n## 連結\n\n"
    for link in links:
        section += f"- {link}\n"
    return content.rstrip() + "\n" + section


def get_story_id(filepath):
    """從檔名提取 ID（如 AM001、A010、EN001），去掉後綴"""
    basename = os.path.basename(filepath)
    for suffix in ["-content.md", "-narration.md", "-images.md",
                   "-chalkboard-prompt.md", "-raw-materials.md"]:
        if basename.endswith(suffix):
            return basename[: -len(suffix)]
    return None


def get_published_url(content):
    """從 frontmatter 提取 published_url"""
    parsed = get_frontmatter(content)
    if parsed is None:
        return None
    fm_text, _ = parsed
    m = re.search(r"published_url:\s*(.+)", fm_text)
    if m:
        url = m.group(1).strip().strip('"').strip("'")
        return url if url.startswith("http") else None
    return None


def find_siblings(filepath, story_id):
    """在同目錄查詢現有的 narration/images/chalkboard-prompt 兄弟檔"""
    dir_path = os.path.join(REPO_ROOT, os.path.dirname(filepath))
    found = {}
    for suffix in ["narration", "images", "chalkboard-prompt"]:
        if os.path.exists(os.path.join(dir_path, f"{story_id}-{suffix}.md")):
            found[suffix] = f"[[{story_id}-{suffix}]]"
    return found


def load_concept_aliases():
    """掃描 wiki/concepts/ 下所有概念頁，建立 alias → 檔名 對照表"""
    concept_dir = os.path.join(REPO_ROOT, "wiki", "concepts")
    aliases = {}
    if not os.path.isdir(concept_dir):
        return aliases
    for root, dirs, files in os.walk(concept_dir):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            stem = fname[:-3]
            cpath = os.path.join(root, fname)
            try:
                with open(cpath, "r", encoding="utf-8") as cf:
                    head = cf.read(600)
            except (FileNotFoundError, UnicodeDecodeError):
                continue
            # stem 本身也是一個 alias
            aliases[stem.lower()] = stem
            # 從 aliases: frontmatter 提取
            for a in re.findall(r'-\s+"([^"]+)"', head[:400]):
                aliases[a.lower()] = stem
    return aliases


# ── 修復函式（各類型）──────────────────────────────────────

def fix_story_content(filepath, missing, dry_run, log):
    content = read_file(filepath)
    if content is None:
        return 0

    story_id = get_story_id(filepath)
    if not story_id:
        return 0

    siblings = find_siblings(filepath, story_id)
    published_url = get_published_url(content)

    related_items = []
    for suffix in ["narration", "images", "chalkboard-prompt"]:
        if suffix in siblings:
            related_items.append(siblings[suffix])
    if published_url:
        related_items.append(f"[CreatorHub — {story_id}]({published_url})")

    body_links = []
    label_map = {
        "narration": "說書稿",
        "images": "圖像清單",
        "chalkboard-prompt": "黑板畫提示",
    }
    for suffix in ["narration", "images", "chalkboard-prompt"]:
        if suffix in siblings:
            body_links.append(f"{label_map[suffix]}：{siblings[suffix]}")
    if published_url:
        body_links.append(f"已發布：[CreatorHub — {story_id}]({published_url})")

    if not related_items and not body_links:
        return 0

    changes = []
    new_content = content

    if "related" in missing and related_items:
        new_content = inject_related(new_content, related_items)
        changes.append(f"related({len(related_items)})")

    if "body" in missing and body_links:
        new_content = append_link_section(new_content, body_links)
        changes.append("## 連結")

    if not changes or new_content == content:
        return 0

    log.append(f"  {filepath}  [{', '.join(changes)}]")
    if not dry_run:
        write_file(filepath, new_content)
    return 1


def fix_story_component(filepath, missing, dry_run, log):
    content = read_file(filepath)
    if content is None:
        return 0

    story_id = get_story_id(filepath)
    if not story_id:
        return 0

    published_url = get_published_url(content)

    related_items = [f"[[{story_id}-content]]"]
    if published_url:
        related_items.append(f"[CreatorHub — {story_id}]({published_url})")

    if "related" not in missing:
        return 0

    new_content = inject_related(content, related_items)
    if new_content == content:
        return 0

    log.append(f"  {filepath}  [related({len(related_items)})]")
    if not dry_run:
        write_file(filepath, new_content)
    return 1


def fix_wiki_entry(filepath, missing, dry_run, log, concept_aliases):
    content = read_file(filepath)
    if content is None:
        return 0

    parsed = get_frontmatter(content)
    if parsed is None:
        return 0
    fm_text, _ = parsed

    related_items = []

    # 1. source_plan（已有的教案連結）
    sp_m = re.search(r'source_plan:\s*["\']?(\[\[.+?\]\])["\']?', fm_text)
    if sp_m:
        related_items.append(sp_m.group(1))

    # 2. 相鄰 wiki 頁（同 week 前後 session）
    basename = os.path.basename(filepath).replace(".md", "")
    m = re.match(r"(.+-w\d+-)(\d+)$", basename)
    if m:
        prefix, num = m.group(1), int(m.group(2))
        wiki_dir = os.path.dirname(os.path.join(REPO_ROOT, filepath))
        if num > 1:
            prev_name = f"{prefix}{num - 1}"
            if os.path.exists(os.path.join(wiki_dir, f"{prev_name}.md")):
                related_items.append(f"[[{prev_name}]]")
        next_name = f"{prefix}{num + 1}"
        if os.path.exists(os.path.join(wiki_dir, f"{next_name}.md")):
            related_items.append(f"[[{next_name}]]")

    # 3. 概念頁：從 tags 比對
    tags_m = re.search(r"tags:(.*?)(?=\n\S|\Z)", fm_text, re.DOTALL)
    if tags_m:
        for tag in re.findall(r"-\s+(.+)", tags_m.group(1)):
            tag_clean = tag.strip().strip("'\"")
            if tag_clean.lower() in concept_aliases:
                link = f"[[{concept_aliases[tag_clean.lower()]}]]"
                if link not in related_items:
                    related_items.append(link)

    if not related_items:
        return 0

    changes = []
    new_content = content

    if "related" in missing:
        new_content = inject_related(new_content, related_items)
        changes.append(f"related({len(related_items)})")

    if "body" in missing:
        body_links = [item for item in related_items]
        new_content = append_link_section(new_content, body_links)
        changes.append("## 連結")

    if not changes or new_content == content:
        return 0

    log.append(f"  {filepath}  [{', '.join(changes)}]")
    if not dry_run:
        write_file(filepath, new_content)
    return 1


def fix_concept_page(filepath, missing, dry_run, log):
    """concept_page：補 ## 連結 section（從現有 related: 複製）"""
    if "body" not in missing:
        return 0

    content = read_file(filepath)
    if content is None:
        return 0

    parsed = get_frontmatter(content)
    if parsed is None:
        return 0
    fm_text, _ = parsed

    # 從 related: 提取已有連結
    related_items = re.findall(r'-\s+"?(\[\[.+?\]\]|\[.+?\]\(.+?\))"?', fm_text)

    body_links = related_items if related_items else ["（連結待補）"]
    new_content = append_link_section(content, body_links)

    if new_content == content:
        return 0

    log.append(f"  {filepath}  [## 連結({len(body_links)} links)]")
    if not dry_run:
        write_file(filepath, new_content)
    return 1


# ── 主流程 ─────────────────────────────────────────────────

def main():
    dry_run = "--apply" not in sys.argv
    type_filter = None
    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            type_filter = sys.argv[idx + 1]

    print("[link-orphan-fix] 掃描 LINK_ORPHAN 清單...")
    orphans = get_link_orphans()
    print(f"  找到 {len(orphans)} 個需修復的檔案")

    mode = "DRY-RUN（加 --apply 才寫入）" if dry_run else "APPLY 模式"
    print(f"  模式：{mode}")
    if type_filter:
        print(f"  篩選：--type {type_filter}")
    print()

    concept_aliases = load_concept_aliases()

    log = []
    counts = {
        "story_content": 0,
        "story_component": 0,
        "wiki_entry": 0,
        "concept_page": 0,
        "skipped": 0,
    }

    for filepath, file_type, missing in orphans:
        if type_filter == "story" and file_type not in ("story_content", "story_component"):
            continue
        if type_filter == "wiki" and file_type not in ("wiki_entry", "concept_page"):
            continue

        if file_type == "story_content":
            n = fix_story_content(filepath, missing, dry_run, log)
            if n:
                counts["story_content"] += n
            else:
                counts["skipped"] += 1

        elif file_type == "story_component":
            n = fix_story_component(filepath, missing, dry_run, log)
            if n:
                counts["story_component"] += n
            else:
                counts["skipped"] += 1

        elif file_type == "wiki_entry":
            n = fix_wiki_entry(filepath, missing, dry_run, log, concept_aliases)
            if n:
                counts["wiki_entry"] += n
            else:
                counts["skipped"] += 1

        elif file_type == "concept_page":
            n = fix_concept_page(filepath, missing, dry_run, log)
            if n:
                counts["concept_page"] += n
            else:
                counts["skipped"] += 1

    # ── 報告 ──
    if log:
        for line in log:
            print(line)
        print()

    verb = "計劃修改" if dry_run else "已修改"
    print(f"{'[DRY-RUN]' if dry_run else '[完成]'} 摘要：")
    for k, v in counts.items():
        if k == "skipped":
            if v:
                print(f"  跳過（無可補連結）: {v} 個")
        elif v:
            print(f"  {k}: {v} 個")
    total = sum(v for k, v in counts.items() if k != "skipped")
    print(f"  合計 {verb}: {total} 個")

    if dry_run and total > 0:
        print("\n  → 確認無誤後執行 --apply 正式寫入")


if __name__ == "__main__":
    main()
