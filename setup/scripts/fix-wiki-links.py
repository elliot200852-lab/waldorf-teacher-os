#!/usr/bin/env python3
"""批次修復 bases/my-pages-wiki/ 中的 wikilink 路徑。

問題：wiki 頁面間互相引用時缺少目錄前綴。
策略：建立檔名→實際路徑的索引，然後逐檔修復。
"""

import re
from pathlib import Path

BASE = Path("bases/my-pages-wiki")

# 建立檔名索引（stem → 相對於 BASE 的路徑，不含 .md）
def build_index():
    """建立所有 .md 檔案的索引：stem → relative path（不含 .md）"""
    idx = {}
    for fp in BASE.rglob("*.md"):
        if fp.suffix == ".bak":
            continue
        rel = fp.relative_to(BASE)
        stem = fp.stem
        # 不含 .md 的相對路徑
        rel_no_ext = str(rel)[:-3]  # strip .md
        idx[stem] = rel_no_ext
        # 也用小寫版本做 fallback
        idx[stem.lower()] = rel_no_ext
    return idx


def fix_wikilinks(content: str, file_path: Path, index: dict) -> tuple[str, int]:
    """修復內容中的 wikilink，回傳 (修復後內容, 修復數量)。"""

    # 跳過 frontmatter
    fm_end = 0
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            fm_end = end + 3

    prefix = content[:fm_end]
    body = content[fm_end:]

    fixes = 0

    def replace_link(m):
        nonlocal fixes
        full = m.group(0)
        target = m.group(1).strip()
        display = m.group(2)  # may be None

        # 跳過空連結
        if not target:
            return full

        # 跳過已有路徑前綴的連結（raw/, wiki/, 或含 /）
        # 但如果含 / 且目標不存在，還是要修
        if target.endswith(".md"):
            target_check = target
        else:
            target_check = target

        # 檢查目標是否已經存在（相對於檔案所在目錄或 BASE）
        candidates = []
        t_with_md = target if target.endswith(".md") else target + ".md"
        candidates.append(file_path.parent / t_with_md)
        candidates.append(BASE / t_with_md)

        if any(c.exists() for c in candidates):
            return full  # 連結已有效，不改

        # 連結失效，嘗試從索引找到正確路徑
        # 先用原始 target（可能含路徑），提取 stem
        target_stem = Path(target.replace(".md", "")).name

        correct_path = index.get(target_stem) or index.get(target_stem.lower())

        if not correct_path:
            return full  # 找不到對應檔案，保留原樣

        # 計算從檔案所在目錄到目標的相對路徑
        # 由於 Obsidian wikilink 通常用相對於 vault root 的路徑
        # 直接用相對於 BASE 的路徑即可
        fixes += 1

        if display:
            return f"[[{correct_path}|{display.strip()}]]"
        else:
            return f"[[{correct_path}]]"

    # 匹配 [[target]] 或 [[target|display]]
    pattern = re.compile(r'\[\[([^\]|]+?)(?:\|([^\]]*?))?\]\]')
    new_body = pattern.sub(replace_link, body)

    return prefix + new_body, fixes


def main():
    index = build_index()
    print(f"索引建立完成：{len(index)} 個條目")

    total_fixes = 0
    fixed_files = 0

    # 只處理非 raw、非 .bak 的 .md 檔案
    for fp in sorted(BASE.rglob("*.md")):
        if ".bak" in fp.name or "/raw/" in str(fp):
            continue

        try:
            content = fp.read_text(encoding="utf-8")
        except Exception:
            continue

        new_content, fixes = fix_wikilinks(content, fp, index)

        if fixes > 0:
            fp.write_text(new_content, encoding="utf-8")
            print(f"  修復 {fixes:>3} 個連結：{fp.relative_to(BASE)}")
            total_fixes += fixes
            fixed_files += 1

    print(f"\n完成：{fixed_files} 個檔案共修復 {total_fixes} 個連結")


if __name__ == "__main__":
    main()
