#!/usr/bin/env python3
"""批次為 bases/my-pages-wiki/raw/ 下的 .md 檔案補上 Obsidian frontmatter。

根據目錄結構自動產生 aliases、tags、type、teacher。
已有 frontmatter 的檔案跳過不覆蓋。
"""

import os
import re
import sys
from pathlib import Path

BASE = Path("bases/my-pages-wiki/raw")

# 目錄 → tags 對照表
TAG_MAP = {
    "個人文件": ["wiki/個人文件"],
    "學校行政與活動": ["wiki/學校行政", "wiki/活動"],
    "推薦信與對外文件": ["wiki/推薦信", "wiki/對外文件"],
    "歷史教學": ["wiki/歷史", "wiki/教學"],
    "歷史教學/台灣史": ["wiki/歷史", "wiki/教學", "wiki/台灣史"],
    "歷史教學/學習單與評量": ["wiki/歷史", "wiki/教學", "wiki/學習單", "wiki/評量"],
    "歷史教學/歐美地理歷史": ["wiki/歷史", "wiki/教學", "wiki/歐美地理"],
    "歷史教學/現代史": ["wiki/歷史", "wiki/教學", "wiki/現代史"],
    "班級經營": ["wiki/班級經營"],
    "班級經營/學生輔導": ["wiki/班級經營", "wiki/學生輔導"],
    "班級經營/家長溝通": ["wiki/班級經營", "wiki/家長溝通"],
    "班級經營/戲劇": ["wiki/班級經營", "wiki/戲劇"],
    "班級經營/戶外活動": ["wiki/班級經營", "wiki/戶外活動"],
    "班級經營/班級活動與規範": ["wiki/班級經營", "wiki/班級活動", "wiki/規範"],
    "英文教學": ["wiki/英文", "wiki/教學"],
    "英文教學/口說與聽力": ["wiki/英文", "wiki/教學", "wiki/口說", "wiki/聽力"],
    "英文教學/單字與詞彙": ["wiki/英文", "wiki/教學", "wiki/單字", "wiki/詞彙"],
    "英文教學/寫作": ["wiki/英文", "wiki/教學", "wiki/寫作"],
    "英文教學/文法": ["wiki/英文", "wiki/教學", "wiki/文法"],
    "英文教學/詩歌與歌曲": ["wiki/英文", "wiki/教學", "wiki/詩歌", "wiki/歌曲"],
    "英文教學/課程大綱與評量": ["wiki/英文", "wiki/教學", "wiki/課程大綱", "wiki/評量"],
    "英文教學/閱讀與文學": ["wiki/英文", "wiki/教學", "wiki/閱讀", "wiki/文學"],
    "語文教學-中文台灣文學": ["wiki/語文", "wiki/中文", "wiki/台灣文學"],
    "跨領域與專題": ["wiki/跨領域", "wiki/專題"],
}

# 目錄 → type 對照
TYPE_MAP = {
    "個人文件": "個人文件",
    "學校行政與活動": "行政文件",
    "推薦信與對外文件": "對外文件",
    "歷史教學": "教學素材",
    "班級經營": "班級經營",
    "英文教學": "教學素材",
    "語文教學-中文台灣文學": "教學素材",
    "跨領域與專題": "教學素材",
}

# 目錄 → subject 對照
SUBJECT_MAP = {
    "歷史教學": "歷史",
    "英文教學": "英文",
    "語文教學-中文台灣文學": "語文",
    "跨領域與專題": "跨領域",
}


def has_frontmatter(content: str) -> bool:
    """檢查是否已有 frontmatter。"""
    if not content.startswith("---"):
        return False
    end = content.find("---", 3)
    return end > 3


def clean_alias(filename: str) -> str:
    """從檔名產生可讀的 alias。"""
    name = Path(filename).stem
    # 移除常見前綴標記 [107], [111], [pre2022] 等
    name = re.sub(r"^\[.*?\]\s*", "", name)
    return name.strip()


def get_tags_and_meta(rel_path: Path):
    """根據相對路徑取得 tags、type、subject。"""
    parts = rel_path.parts  # e.g. ('英文教學', '文法', 'xxx.md')

    # 嘗試兩層目錄 match，再 fallback 到一層
    if len(parts) >= 3:
        two_level = f"{parts[0]}/{parts[1]}"
        if two_level in TAG_MAP:
            tags = TAG_MAP[two_level]
            doc_type = TYPE_MAP.get(parts[0], "教學素材")
            subject = SUBJECT_MAP.get(parts[0], "")
            return tags, doc_type, subject

    one_level = parts[0]
    tags = TAG_MAP.get(one_level, ["wiki/未分類"])
    doc_type = TYPE_MAP.get(one_level, "文件")
    subject = SUBJECT_MAP.get(one_level, "")
    return tags, doc_type, subject


def build_frontmatter(alias: str, tags: list, doc_type: str,
                      subject: str, teacher: str = "林信宏") -> str:
    """產生 YAML frontmatter 字串。"""
    lines = ["---"]
    lines.append("aliases:")
    lines.append(f"  - \"{alias}\"")
    lines.append("tags:")
    for t in tags:
        lines.append(f"  - {t}")
    lines.append(f"type: {doc_type}")
    if subject:
        lines.append(f"subject: {subject}")
    lines.append(f"teacher: {teacher}")
    lines.append(f"source: my-pages-wiki")
    lines.append("---")
    return "\n".join(lines) + "\n"


def process_file(filepath: Path, rel_path: Path) -> bool:
    """處理單一檔案，回傳是否有修改。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  SKIP (read error): {rel_path} — {e}")
        return False

    if has_frontmatter(content):
        return False

    alias = clean_alias(filepath.name)
    tags, doc_type, subject = get_tags_and_meta(rel_path)
    fm = build_frontmatter(alias, tags, doc_type, subject)

    # 加在檔案最前面，保留一個空行分隔
    if content and not content.startswith("\n"):
        new_content = fm + "\n" + content
    else:
        new_content = fm + content

    filepath.write_text(new_content, encoding="utf-8")
    return True


def main():
    if not BASE.exists():
        print(f"ERROR: {BASE} not found")
        sys.exit(1)

    md_files = sorted(BASE.rglob("*.md"))
    total = len(md_files)
    modified = 0
    skipped = 0

    print(f"掃描 {total} 個 .md 檔案...")

    for fp in md_files:
        rel = fp.relative_to(BASE)
        if process_file(fp, rel):
            modified += 1
        else:
            skipped += 1

    print(f"\n完成：{modified} 個檔案已補上 frontmatter，{skipped} 個跳過（已有或無法讀取）")


if __name__ == "__main__":
    main()
