#!/usr/bin/env python3
"""
map-generate-initial.py — 從 HOME.md 反推生成 repo-structure-map.yaml 初版

解析 HOME.md 中每個區段下的 wikilink，建立：
1. sections — HOME.md 的完整區段樹
2. rules — 路徑模式 → HOME.md 區段的路由規則（first-match-wins）
3. tracked_directories — 所有 git-tracked 目錄（自動生成）

用法：
    python3 map-generate-initial.py                # 生成初版到 stdout
    python3 map-generate-initial.py --output FILE  # 寫入指定檔案
    python3 map-generate-initial.py --dry-run      # 只顯示解析結果統計

不依賴外部套件（只用 Python 標準函式庫 + PyYAML）。
"""

import os
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import PurePosixPath

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # setup/scripts/ → 上兩層


# ── YAML ordered dict 輸出 ────────────────────────────────
class _OrderedDumper(yaml.SafeDumper):
    pass

def _dict_representer(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())

_OrderedDumper.add_representer(OrderedDict, _dict_representer)
_OrderedDumper.add_representer(dict, _dict_representer)


# ── 解析 HOME.md ─────────────────────────────────────────

def parse_home_md(home_path):
    """解析 HOME.md，回傳 (sections_tree, section_links)。

    sections_tree: OrderedDict 區段樹
      例 {"David 的工作空間": {"heading": "## David 的工作空間", "children": {"個人設定": ...}}}

    section_links: list of (section_path, file_path)
      例 [("David 的工作空間 > 個人設定", "workspaces/.../teacheros-personal.yaml"), ...]
    """
    with open(home_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sections_tree = OrderedDict()
    section_links = []

    # 追蹤當前區段層級
    current_h2 = None
    current_h3 = None

    # wikilink 正規表達式：[[path|alias]] 或 [[path]]
    wikilink_re = re.compile(r'\[\[([^\]|\\]+(?:\\.[^\]|\\]*)*)(?:\|[^\]]*)?]]')
    # 更寬鬆的版本，處理 \| 跳脫
    wikilink_re2 = re.compile(r'\[\[([^\]]*?)(?:\\?\|[^\]]*)?]]')

    for line in lines:
        stripped = line.strip()

        # 解析標題
        if stripped.startswith("## ") and not stripped.startswith("### "):
            current_h2 = stripped[3:].strip()
            current_h3 = None
            if current_h2 not in sections_tree:
                sections_tree[current_h2] = OrderedDict()
        elif stripped.startswith("### "):
            current_h3 = stripped[4:].strip()
            if current_h2 and current_h3 not in sections_tree.get(current_h2, {}):
                sections_tree.setdefault(current_h2, OrderedDict())[current_h3] = []

        # 解析 wikilink
        matches = wikilink_re2.findall(line)
        for match in matches:
            # 清理路徑
            file_path = match.strip()
            if not file_path:
                continue

            # 決定區段路徑
            if current_h2 and current_h3:
                section_path = f"{current_h2} > {current_h3}"
            elif current_h2:
                section_path = current_h2
            else:
                section_path = "(root)"

            section_links.append((section_path, file_path))

            # 把連結加到區段的子項目清單
            if current_h2 and current_h3:
                sections_tree.setdefault(current_h2, OrderedDict()).setdefault(current_h3, []).append(file_path)
            elif current_h2:
                sections_tree.setdefault(current_h2, OrderedDict()).setdefault("_files", []).append(file_path)

    return sections_tree, section_links


def get_tracked_directories():
    """取得所有 git-tracked 檔案所在的目錄"""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0:
        return []

    dirs = set()
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        # 解碼 git 的 octal 跳脫路徑
        path = line.strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
            if "\\" in path:
                try:
                    path = path.encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
        parent = os.path.dirname(path)
        while parent:
            dirs.add(parent)
            parent = os.path.dirname(parent)

    return sorted(dirs)


def infer_rules(section_links):
    """從 wikilink 列表推斷路由規則。

    策略：
    1. 將同一區段下的檔案路徑群組化
    2. 找出每組的共同路徑前綴
    3. 用 glob 模式表示
    """
    # 按區段分組
    section_files = OrderedDict()
    for section_path, file_path in section_links:
        section_files.setdefault(section_path, []).append(file_path)

    rules = []
    seen_patterns = set()

    for section_path, files in section_files.items():
        # 找共同前綴
        if len(files) == 1:
            # 單一檔案：精確匹配
            fp = files[0]
            pattern = fp
            if pattern not in seen_patterns:
                rules.append({
                    "pattern": pattern,
                    "section": section_path,
                    "note": "精確匹配",
                })
                seen_patterns.add(pattern)
        else:
            # 多檔案：找共同目錄前綴
            dirs = [os.path.dirname(f) for f in files]
            # 找最長共同前綴
            if dirs:
                common = os.path.commonpath(dirs) if all(dirs) else ""
            else:
                common = ""

            if common:
                # 檢查是否所有檔案都在同一目錄（不含子目錄）
                all_same_dir = all(os.path.dirname(f) == common for f in files)
                if all_same_dir:
                    # 取得副檔名模式
                    exts = set(os.path.splitext(f)[1] for f in files)
                    if len(exts) == 1:
                        ext = exts.pop()
                        pattern = f"{common}/*{ext}"
                    else:
                        pattern = f"{common}/*"
                else:
                    pattern = f"{common}/**"

                if pattern not in seen_patterns:
                    rules.append({
                        "pattern": pattern,
                        "section": section_path,
                        "note": f"從 {len(files)} 個檔案推斷",
                    })
                    seen_patterns.add(pattern)
            else:
                # 無共同前綴，逐一列出
                for fp in files:
                    if fp not in seen_patterns:
                        rules.append({
                            "pattern": fp,
                            "section": section_path,
                            "note": "精確匹配（無共同前綴）",
                        })
                        seen_patterns.add(fp)

    return rules


def consolidate_rules(rules):
    """合併可簡化的規則。

    例如 workspaces/.../Codeowner_David/skills/X.md 有多條精確匹配，
    可合併為 workspaces/.../Codeowner_David/skills/*.md
    """
    # 按 section 分組
    by_section = OrderedDict()
    for r in rules:
        by_section.setdefault(r["section"], []).append(r)

    consolidated = []
    for section, group in by_section.items():
        if len(group) == 1:
            consolidated.append(group[0])
            continue

        # 嘗試找共同目錄前綴
        patterns = [r["pattern"] for r in group]
        # 只合併精確匹配的（不含 * 的）
        exact = [p for p in patterns if "*" not in p]
        globs = [p for p in patterns if "*" in p]

        if exact:
            dirs = [os.path.dirname(p) for p in exact if os.path.dirname(p)]
            if dirs:
                from collections import Counter
                dir_counts = Counter(dirs)
                for d, count in dir_counts.most_common():
                    if count >= 2:
                        exts = set(os.path.splitext(p)[1] for p in exact if os.path.dirname(p) == d)
                        if len(exts) == 1:
                            glob_pattern = f"{d}/*{exts.pop()}"
                        else:
                            glob_pattern = f"{d}/*"
                        consolidated.append({
                            "pattern": glob_pattern,
                            "section": section,
                            "note": f"合併 {count} 條精確匹配",
                        })
                        exact = [p for p in exact if os.path.dirname(p) != d]

            # 剩餘的精確匹配
            for p in exact:
                consolidated.append({
                    "pattern": p,
                    "section": section,
                    "note": "精確匹配",
                })

        # 保留已有的 glob 規則
        for p in globs:
            matching = [r for r in group if r["pattern"] == p]
            if matching:
                consolidated.append(matching[0])

    return consolidated


def build_sections_list(sections_tree):
    """把區段樹轉為扁平的 section 路徑列表"""
    sections = []
    for h2, children in sections_tree.items():
        sections.append(h2)
        if isinstance(children, dict):
            for h3 in children:
                if h3 != "_files":
                    sections.append(f"{h2} > {h3}")
    return sections


def generate_map(home_path, include_tracked_dirs=True):
    """生成完整的 repo-structure-map.yaml 內容"""
    sections_tree, section_links = parse_home_md(home_path)

    # 推斷路由規則
    raw_rules = infer_rules(section_links)
    rules = consolidate_rules(raw_rules)

    # 建立區段列表
    sections = build_sections_list(sections_tree)

    # 取得 tracked 目錄
    tracked_dirs = get_tracked_directories() if include_tracked_dirs else []

    # 組裝 YAML 結構
    map_data = OrderedDict()
    map_data["_meta"] = OrderedDict([
        ("version", "0.1.0"),
        ("generated_by", "map-generate-initial.py"),
        ("description", "Repo 架構地圖：路徑 → HOME.md 區段的路由規則"),
        ("match_strategy", "first-match-wins"),
    ])

    # rules 區段
    map_data["rules"] = []
    for r in rules:
        rule = OrderedDict()
        rule["pattern"] = r["pattern"]
        rule["section"] = r["section"]
        if r.get("note"):
            rule["note"] = r["note"]
        map_data["rules"].append(rule)

    # sections 區段
    map_data["sections"] = sections

    # tracked_directories 區段
    if tracked_dirs:
        map_data["tracked_directories"] = tracked_dirs

    return map_data, {
        "total_links": len(section_links),
        "total_rules": len(rules),
        "total_sections": len(sections),
        "total_tracked_dirs": len(tracked_dirs),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="從 HOME.md 反推生成 repo-structure-map.yaml 初版")
    parser.add_argument("--output", "-o", help="輸出檔案路徑（預設 stdout）")
    parser.add_argument("--dry-run", action="store_true", help="只顯示統計，不輸出 YAML")
    parser.add_argument("--no-tracked-dirs", action="store_true", help="不包含 tracked_directories")
    args = parser.parse_args()

    # 找 HOME.md
    home_path = os.path.join(REPO_ROOT, "HOME.md")
    if not os.path.exists(home_path):
        home_path = os.path.join(REPO_ROOT, "Good-notes", "HOME.md")
    if not os.path.exists(home_path):
        print("ERROR: HOME.md not found", file=sys.stderr)
        sys.exit(1)

    map_data, stats = generate_map(home_path, include_tracked_dirs=not args.no_tracked_dirs)

    if args.dry_run:
        print(f"[map-generate] 解析完成")
        print(f"  wikilinks 總數: {stats['total_links']}")
        print(f"  推斷規則數: {stats['total_rules']}")
        print(f"  區段數: {stats['total_sections']}")
        print(f"  tracked 目錄數: {stats['total_tracked_dirs']}")
        print(f"\n區段列表:")
        for s in map_data["sections"]:
            indent = "    " if " > " in s else "  "
            print(f"{indent}{s}")
        return

    yaml_output = yaml.dump(
        map_data,
        Dumper=_OrderedDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(yaml_output)
        print(f"[map-generate] 已寫入 {args.output}")
        print(f"  規則數: {stats['total_rules']}  區段數: {stats['total_sections']}  目錄數: {stats['total_tracked_dirs']}")
    else:
        print(yaml_output)


if __name__ == "__main__":
    main()
