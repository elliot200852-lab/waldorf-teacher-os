#!/usr/bin/env python3
"""
wiki-bootstrap.py — 一次性為現有教案/學習單補上 wikilink 連結

掃描 workspaces/**/content/*.md，根據 frontmatter metadata 推斷
related: 連結和 ## 連結 body 區段。

用法：
  python3 setup/scripts/wiki-bootstrap.py               # dry-run（預設）
  python3 setup/scripts/wiki-bootstrap.py --apply        # 實際寫入
  python3 setup/scripts/wiki-bootstrap.py --stats        # 只顯示統計

連結規範見 ai-core/reference/wikilink-protocol.yaml。
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from glob import glob
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_yaml_frontmatter(text):
    """極簡 YAML frontmatter 解析。回傳 dict（key: value 字串）。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, 0

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return {}, 0

    fm = {}
    current_key = None
    current_list = None

    for line in lines[1:end_idx]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # list item
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            fm[current_key] = current_list
            continue

        # key: value
        m = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', stripped)
        if m:
            current_key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            if val:
                fm[current_key] = val
                current_list = None
            else:
                current_list = []
                fm[current_key] = current_list

    return fm, end_idx


def infer_file_type(filename):
    """推斷檔案類型：lesson-plan / worksheet / answer-key / reference / other"""
    name = filename.lower()
    if "教師教案" in name or "教案" in name:
        return "lesson-plan"
    if "學習單-教師版" in name or "學習單_教師版" in name:
        return "answer-key"
    if "學習單" in name:
        return "worksheet"
    if "教學參考" in name:
        return "reference"
    return "other"


def derive_wiki_entry_name(class_code, subject, week, seq=None):
    """推導 wiki 備課日誌的檔名（不含 .md）。"""
    if seq:
        return f"{class_code}-{subject}-w{week}-{seq}"
    return f"{class_code}-{subject}-w{week}-1"


def build_related_links(fm, filepath, all_files_index, all_same_subject):
    """根據 frontmatter 推斷 related: 連結清單。"""
    links = []
    file_type = infer_file_type(filepath.name)
    class_code = fm.get("class", "")
    subject = fm.get("subject", "")
    week = fm.get("week", "")
    session = fm.get("session", "")

    if not class_code or not subject:
        # 無 frontmatter 或缺 class/subject 時，
        # 嘗試用目錄結構推斷同科目檔案互連
        return build_directory_links(filepath)

    # 1. 配對連結（教案 ↔ 學習單，同 week+session）
    key = f"{class_code}:{subject}:{week}:{session}"
    siblings = all_files_index.get(key, [])
    for sib_path, sib_type in siblings:
        if sib_path == filepath:
            continue
        sib_name = sib_path.stem
        if file_type == "lesson-plan" and sib_type == "worksheet":
            links.append(f"[[{sib_name}]]")
        elif file_type == "worksheet" and sib_type == "lesson-plan":
            links.append(f"[[{sib_name}]]")
        elif file_type == "lesson-plan" and sib_type == "answer-key":
            links.append(f"[[{sib_name}]]")

    # 1b. 同 class+subject 的其他檔案（無 week 時用此邏輯）
    if not week:
        subj_key = f"{class_code}:{subject}"
        for sib_path, sib_fm in all_same_subject.get(subj_key, []):
            if sib_path == filepath:
                continue
            sib_name = sib_path.stem
            links.append(f"[[{sib_name}]]")

    # 2. wiki 備課日誌連結（prev / current / next）
    if week:
        try:
            w = int(week)
            current_wiki = derive_wiki_entry_name(class_code, subject, w)
            links.append(f"[[{current_wiki}]]")
            if w > 1:
                prev_wiki = derive_wiki_entry_name(class_code, subject, w - 1)
                links.append(f"[[{prev_wiki}]]")
            next_wiki = derive_wiki_entry_name(class_code, subject, w + 1)
            links.append(f"[[{next_wiki}]]")
        except ValueError:
            pass

    # 3. 文本概念頁
    text = fm.get("text", "")
    if text and text != "null":
        links.append(f"[[{text}]]")

    return links


def build_directory_links(filepath):
    """無 frontmatter 時，用目錄鄰居推斷連結。
    同目錄下的其他 .md 檔視為相關文件。"""
    links = []
    parent = filepath.parent
    siblings = sorted(parent.glob("*.md"))
    for sib in siblings:
        if sib == filepath:
            continue
        if sib.name.startswith(".") or sib.name.startswith("_"):
            continue
        links.append(f"[[{sib.stem}]]")
    return links


def add_related_frontmatter(text, links, fm_end_idx):
    """在 frontmatter 結尾 --- 前插入 related: 清單。"""
    if not links:
        return text

    lines = text.split("\n")
    # 檢查是否已有 related:
    fm_block = "\n".join(lines[1:fm_end_idx])
    if "related:" in fm_block:
        return text

    related_lines = ["related:"]
    for link in links:
        related_lines.append(f'  - "{link}"')

    lines = lines[:fm_end_idx] + related_lines + lines[fm_end_idx:]
    return "\n".join(lines)


def add_body_links_section(text, links, filepath):
    """在 body 末尾加 ## 連結 區段（僅教案類型）。"""
    file_type = infer_file_type(filepath.name)
    # 學習單不加 body 連結（學生會看到），其他類型都加
    if file_type in ("worksheet", "answer-key"):
        return text

    if "## 連結" in text:
        return text

    if not links:
        return text

    section = ["\n## 連結\n"]
    for link in links:
        section.append(f"- {link}")

    return text.rstrip() + "\n" + "\n".join(section) + "\n"


def main():
    parser = argparse.ArgumentParser(description="為現有教案/學習單補上 wikilink 連結")
    parser.add_argument("--apply", action="store_true", help="實際寫入（預設 dry-run）")
    parser.add_argument("--stats", action="store_true", help="只顯示統計")
    args = parser.parse_args()

    dry_run = not args.apply

    # 掃描所有 content/*.md
    pattern = str(REPO_ROOT / "workspaces" / "**" / "content" / "*.md")
    all_files = sorted(glob(pattern, recursive=True))

    # 建立索引：{class:subject:week:session} → [(path, type)]
    files_index = defaultdict(list)
    # 同科目索引（無 week 時用）：{class:subject} → [(path, fm)]
    same_subject_index = defaultdict(list)
    file_data = []

    for fpath_str in all_files:
        fpath = Path(fpath_str)
        text = fpath.read_text(encoding="utf-8", errors="replace")
        fm, fm_end = parse_yaml_frontmatter(text)
        ftype = infer_file_type(fpath.name)

        class_code = fm.get("class", "")
        subject = fm.get("subject", "")
        week = fm.get("week", "")
        session = fm.get("session", "")

        key = f"{class_code}:{subject}:{week}:{session}"
        files_index[key].append((fpath, ftype))
        if class_code and subject:
            subj_key = f"{class_code}:{subject}"
            same_subject_index[subj_key].append((fpath, fm))
        file_data.append((fpath, text, fm, fm_end, ftype))

    # 統計
    total = len(file_data)
    has_related = 0
    for _, text, _, _, _ in file_data:
        if text.startswith("---") and text.count("---") >= 2:
            parts = text.split("---", 2)
            if len(parts) >= 2 and "related:" in parts[1]:
                has_related += 1
    has_links_section = sum(1 for _, text, _, _, _ in file_data if "## 連結" in text)

    type_counts = defaultdict(int)
    for _, _, _, _, ft in file_data:
        type_counts[ft] += 1

    print(f"掃描結果：{total} 個 content .md 檔案")
    print(f"  教案：{type_counts['lesson-plan']}")
    print(f"  學習單：{type_counts['worksheet']}")
    print(f"  教師版：{type_counts['answer-key']}")
    print(f"  教學參考：{type_counts['reference']}")
    print(f"  其他：{type_counts['other']}")
    print(f"  已有 related:：~{has_related}")
    print(f"  已有 ## 連結：{has_links_section}")
    print()

    if args.stats:
        return

    # 處理每個檔案
    updated = 0
    skipped = 0

    for fpath, text, fm, fm_end, ftype in file_data:
        links = build_related_links(fm, fpath, files_index, same_subject_index)

        if not links:
            skipped += 1
            continue

        # 檢查是否已完成
        fm_block = ""
        if text.startswith("---") and text.count("---") >= 2:
            parts = text.split("---", 2)
            if len(parts) >= 2:
                fm_block = parts[1]

        already_has_related = "related:" in fm_block
        already_has_links = "## 連結" in text
        needs_body = ftype in ("lesson-plan", "reference") and not already_has_links

        if already_has_related and not needs_body:
            skipped += 1
            continue

        if dry_run:
            rel = fpath.relative_to(REPO_ROOT)
            print(f"[dry-run] {rel}")
            if not already_has_related:
                print(f"  → 會補 frontmatter related: ({len(links)} 個連結)")
                for link in links[:5]:
                    print(f"    {link}")
                if len(links) > 5:
                    print(f"    ...（共 {len(links)} 個）")
            if needs_body:
                print(f"  → 會補 body ## 連結 區段")
            print()
            updated += 1
        else:
            new_text = text
            if not already_has_related:
                new_text = add_related_frontmatter(new_text, links, fm_end)
            if needs_body:
                new_text = add_body_links_section(new_text, links, fpath)
            if new_text != text:
                fpath.write_text(new_text, encoding="utf-8")
                rel = fpath.relative_to(REPO_ROOT)
                print(f"[updated] {rel}")
                updated += 1
            else:
                skipped += 1

    print("=" * 50)
    mode = "DRY-RUN" if dry_run else "APPLIED"
    print(f"[{mode}] 結果摘要")
    print(f"  {'會更新' if dry_run else '已更新'}：{updated}")
    print(f"  跳過（已完成或無連結）：{skipped}")


if __name__ == "__main__":
    main()
