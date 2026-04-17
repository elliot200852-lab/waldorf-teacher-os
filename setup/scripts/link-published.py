#!/usr/bin/env python3
"""
link-published.py — 回填 CreatorHub 已發布素材的外部連結

讀取 creator-hub/data/files.json，比對 repo 中的素材源檔，
在 frontmatter 補上 published_url + published_channel，
在 body 末尾補上 ## 連結 區段（含外部 URL + 同組 wikilinks）。

用法：
  python3 setup/scripts/link-published.py               # dry-run（預設）
  python3 setup/scripts/link-published.py --apply        # 實際寫入
  python3 setup/scripts/link-published.py --channel A    # 只處理特定 prefix

獨立於 story-daily pipeline，部署完成後單獨執行。
"""

import argparse
import json
import os
import re
import sys
from glob import glob
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
FILES_JSON = REPO_ROOT / "creator-hub" / "data" / "files.json"
BASE_URL = "https://waldorfcreatorhubdatabase.web.app"

# story ID prefix → repo 搜尋路徑（相對 REPO_ROOT）
SOURCE_SEARCH_PATHS = {
    "A":  "workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/",
    "EN": "workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/",
    "B":  "workspaces/Working_Member/Codeowner_David/projects/botany-grade5/stories/",
    "AM": "workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/",
    "TW": "workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/",
    "I":  None,  # Drive 直接上傳，無 repo 源檔
    "SH": "workspaces/Working_Member/Teacher_王琬婷/projects/class-3a/ml-shanhaijing/content/",
}

# 同目錄的組件檔案後綴
COMPONENT_SUFFIXES = ["-narration.md", "-images.md", "-chalkboard-prompt.md"]


def get_prefix(story_id: str) -> str:
    """從 story ID 提取 prefix（連續字母部分）。"""
    m = re.match(r"^([A-Z]+)", story_id)
    return m.group(1) if m else ""


def find_source_file(story_id: str) -> "Optional[Path]":
    """在 repo 中搜尋 {story_id}-content.md。"""
    prefix = get_prefix(story_id)
    search_base = SOURCE_SEARCH_PATHS.get(prefix)
    if search_base is None:
        return None

    base_path = REPO_ROOT / search_base
    if not base_path.exists():
        return None

    # 搜尋 {ID}/{ID}-content.md（可能在子目錄中）
    pattern = str(base_path / "**" / story_id / f"{story_id}-content.md")
    matches = glob(pattern, recursive=True)
    if matches:
        return Path(matches[0])

    # 備案：直接搜尋 {ID}-content.md
    pattern2 = str(base_path / "**" / f"{story_id}-content.md")
    matches2 = glob(pattern2, recursive=True)
    if matches2:
        return Path(matches2[0])

    return None


def parse_frontmatter(text: str) -> tuple:
    """解析 YAML frontmatter，回傳 (欄位dict, 起始行, 結束行)。
    簡化版：只找 published_url 和 published_channel 是否存在。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0, 0

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return None, 0, 0

    fm_text = "\n".join(lines[1:end_idx])
    has_published_url = "published_url:" in fm_text
    has_published_channel = "published_channel:" in fm_text
    has_related = "related:" in fm_text

    return {
        "has_published_url": has_published_url,
        "has_published_channel": has_published_channel,
        "has_related": has_related,
    }, 0, end_idx


def build_published_url(story_id: str) -> str:
    return f"{BASE_URL}/stories/{story_id}.html"


def add_frontmatter_fields(text: str, story_id: str, channel_id: str) -> str:
    """在 frontmatter 結尾 --- 前插入 published_url 和 published_channel。"""
    lines = text.split("\n")
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return text

    url = build_published_url(story_id)
    new_fields = []

    fm_block = "\n".join(lines[1:end_idx])
    if "published_url:" not in fm_block:
        new_fields.append(f'published_url: {url}')
    if "published_channel:" not in fm_block:
        new_fields.append(f"published_channel: {channel_id}")

    if not new_fields:
        return text

    insert_lines = new_fields
    lines = lines[:end_idx] + insert_lines + lines[end_idx:]
    return "\n".join(lines)


def add_links_section(text: str, story_id: str) -> str:
    """在 body 末尾加入 ## 連結 區段（若尚未存在）。"""
    if "## 連結" in text:
        # 已有連結區段，檢查是否包含 CreatorHub 連結
        url = build_published_url(story_id)
        if url in text:
            return text
        # 在現有 ## 連結 區段末尾追加
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == "## 連結":
                # 找到區段，在下一個 ## 之前或檔案末尾追加
                insert_idx = i + 1
                while insert_idx < len(lines) and not lines[insert_idx].startswith("## "):
                    insert_idx += 1
                link_line = f"- 已發布：[CreatorHub — {story_id}]({url})"
                lines.insert(insert_idx, link_line)
                return "\n".join(lines)
        return text

    # 尚無連結區段，在末尾追加
    url = build_published_url(story_id)
    links = [
        "",
        "## 連結",
        "",
        f"- 已發布：[CreatorHub — {story_id}]({url})",
        f"- 說書稿：[[{story_id}-narration]]",
        f"- 圖像清單：[[{story_id}-images]]",
        f"- 黑板畫提示：[[{story_id}-chalkboard-prompt]]",
    ]
    return text.rstrip() + "\n" + "\n".join(links) + "\n"


def process_component_files(content_path: Path, story_id: str, channel_id: str,
                            dry_run: bool) -> list[str]:
    """為同目錄的組件檔案（narration, images, chalkboard-prompt）補 published_url。"""
    results = []
    parent = content_path.parent

    for suffix in COMPONENT_SUFFIXES:
        comp_path = parent / f"{story_id}{suffix}"
        if not comp_path.exists():
            continue

        text = comp_path.read_text(encoding="utf-8")
        fm_info, _, _ = parse_frontmatter(text)

        if fm_info and fm_info.get("has_published_url"):
            continue

        if dry_run:
            results.append(f"  [dry-run] 會補 published_url: {comp_path.name}")
        else:
            new_text = add_frontmatter_fields(text, story_id, channel_id)
            comp_path.write_text(new_text, encoding="utf-8")
            results.append(f"  [updated] {comp_path.name}")

    return results


def main():
    parser = argparse.ArgumentParser(description="回填 CreatorHub 外部連結到 repo 素材源檔")
    parser.add_argument("--apply", action="store_true", help="實際寫入（預設 dry-run）")
    parser.add_argument("--channel", type=str, help="只處理特定 prefix（例：A, B, AM）")
    args = parser.parse_args()

    dry_run = not args.apply

    if not FILES_JSON.exists():
        print(f"[error] 找不到 {FILES_JSON}")
        print("  請先執行 GitHub Actions sync 或手動 npm run sync 產出 files.json")
        sys.exit(1)

    with open(FILES_JSON, encoding="utf-8") as f:
        data = json.load(f)

    stats = {"found": 0, "updated": 0, "skipped": 0, "no_source": 0}
    no_source_list = []

    for channel_id, channel_data in data.get("channels", {}).items():
        files = channel_data.get("files", [])
        for file_info in files:
            story_id = file_info.get("storyId", "")
            if not story_id:
                continue

            prefix = get_prefix(story_id)

            # 過濾 prefix
            if args.channel and prefix != args.channel.upper():
                continue

            # 非標準 ID（中文檔名等）的「其他」頻道，跳過
            if not prefix:
                stats["no_source"] += 1
                no_source_list.append(f"  {story_id} (others, non-standard ID)")
                continue

            source = find_source_file(story_id)
            if source is None:
                stats["no_source"] += 1
                no_source_list.append(f"  {story_id} ({channel_id}, no repo source)")
                continue

            stats["found"] += 1
            text = source.read_text(encoding="utf-8")
            fm_info, _, _ = parse_frontmatter(text)

            # 檢查是否已完成
            if fm_info and fm_info.get("has_published_url"):
                url = build_published_url(story_id)
                if url in text:
                    stats["skipped"] += 1
                    continue

            if dry_run:
                url = build_published_url(story_id)
                rel = source.relative_to(REPO_ROOT)
                print(f"[dry-run] {story_id}")
                print(f"  源檔：{rel}")
                print(f"  URL：{url}")
                if fm_info and not fm_info.get("has_published_url"):
                    print(f"  → 會補 frontmatter published_url + published_channel")
                if "## 連結" not in text:
                    print(f"  → 會補 body ## 連結 區段")
                elif url not in text:
                    print(f"  → 會在現有 ## 連結 區段追加 CreatorHub 連結")
                comp_results = process_component_files(source, story_id, channel_id, True)
                for r in comp_results:
                    print(r)
                print()
                stats["updated"] += 1
            else:
                new_text = add_frontmatter_fields(text, story_id, channel_id)
                new_text = add_links_section(new_text, story_id)
                source.write_text(new_text, encoding="utf-8")
                rel = source.relative_to(REPO_ROOT)
                print(f"[updated] {story_id} → {rel}")
                comp_results = process_component_files(source, story_id, channel_id, False)
                for r in comp_results:
                    print(r)
                stats["updated"] += 1

    # 摘要
    print("=" * 50)
    mode = "DRY-RUN" if dry_run else "APPLIED"
    print(f"[{mode}] 結果摘要")
    print(f"  找到源檔：{stats['found']}")
    print(f"  {'會更新' if dry_run else '已更新'}：{stats['updated']}")
    print(f"  已完成（跳過）：{stats['skipped']}")
    print(f"  無 repo 源檔：{stats['no_source']}")

    if no_source_list:
        print(f"\n  無源檔清單（{len(no_source_list)} 個）：")
        for item in no_source_list[:20]:
            print(f"    {item}")
        if len(no_source_list) > 20:
            print(f"    ...（還有 {len(no_source_list) - 20} 個）")


if __name__ == "__main__":
    main()
