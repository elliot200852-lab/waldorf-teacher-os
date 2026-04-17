#!/usr/bin/env python3
"""
map-validate.py — Repo 架構地圖驗證與維護工具

功能：
    --validate          驗證地圖完整性（forward + backward）
    --rebuild-dirs      從 git ls-files 重建 tracked_directories
    --rebuild-sections  從 HOME.md 標題重建 sections
    --pre-commit        精簡輸出供 hook 用（exit code 0=OK, 1=warning）
    --suggest PATH      給定路徑，回傳建議的 HOME.md 區段
    --auto-fix          自動修復（目前：重建 tracked_directories）
    --audit-home        審核 HOME.md 內容完整性（死連結 + 遺漏檔案）

驗證項目（--validate）：
    1. Forward: 每條 rule 的 section 值是否在 sections 清單中
    2. Backward: 每個 tracked 目錄是否至少有一條 rule 覆蓋
    3. Rule 語法：pattern 是否為合法 glob
    4. Section 完整：HOME.md 中的區段是否都在 sections 清單中

審核項目（--audit-home）：
    5. 死連結：HOME.md 有 wikilink 但實際檔案不存在
    6. 遺漏：有路由覆蓋的 .md/.yaml 檔案存在但 HOME.md 未收錄

不依賴外部套件（只用 Python 標準函式庫 + PyYAML）。
"""

import os
import re
import subprocess
import sys
from pathlib import PurePosixPath

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
MAP_PATH = os.path.join(REPO_ROOT, "ai-core", "reference", "repo-structure-map.yaml")
HOME_PATH = os.path.join(REPO_ROOT, "HOME.md")

# 這些目錄不需要路由規則覆蓋（工具目錄、隱藏目錄等）
SKIP_DIRS_FOR_BACKWARD = {
    ".obsidian", ".claude/worktrees", "__pycache__", "node_modules", "venv",
    ".git", ".claude/plans", ".claude/settings",
}

# 這些目錄模式完全跳過 backward 檢查
SKIP_DIR_PATTERNS = [
    "word/", "docProps/", "_rels/",  # docx 解壓殘留
    "temp1/", "temp2/",
]


def load_map():
    """載入 repo-structure-map.yaml"""
    if not os.path.exists(MAP_PATH):
        print(f"ERROR: 地圖檔不存在: {MAP_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(MAP_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _replace_yaml_section(content, marker, new_lines):
    """安全替換 YAML 檔案中某個 top-level key 區段（到下一個 top-level key 或 EOF）。

    護欄：
    1. marker 必須出現在行首（排除 comments 和 nested values 中的誤匹配）
    2. 替換範圍只到下一個 top-level key（非 - 或空白開頭的行）或 EOF
    3. 替換前驗證 marker 確實是 top-level key
    """
    # 找行首的 marker（排除 comments 和 indented 出現）
    pattern = re.compile(r'^' + re.escape(marker), re.MULTILINE)
    matches = list(pattern.finditer(content))
    if not matches:
        print(f"ERROR: 找不到 top-level key '{marker}'", file=sys.stderr)
        return None

    # 用最後一個匹配（tracked_directories 通常在最後）
    match = matches[-1]
    start = match.start()

    # 找這個區段的結尾：下一個 top-level key（行首非空白、非 - 、非 # 的行）
    # 或 EOF
    end = len(content)
    lines_after = content[match.end():].split("\n")
    pos = match.end()
    for i, line in enumerate(lines_after):
        if i == 0:
            # 第一行是 marker 的剩餘部分（如 " []" 或 ""），跳過
            pos += len(line) + 1
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            pos += len(line) + 1
            continue
        # 碰到非空白、非 comment、非 list item 的行 → 這是下一個 top-level key
        end = pos
        break

    return content[:start] + "\n".join(new_lines) + "\n" + content[end:]


def save_map_section(marker, new_lines):
    """安全替換地圖檔中的指定區段。"""
    with open(MAP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = _replace_yaml_section(content, marker, new_lines)
    if new_content is None:
        return False

    with open(MAP_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


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


def get_home_sections():
    """從 HOME.md 解析區段標題"""
    if not os.path.exists(HOME_PATH):
        return []

    with open(HOME_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_h2 = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            current_h2 = stripped[3:].strip()
            sections.append(current_h2)
        elif stripped.startswith("### "):
            h3 = stripped[4:].strip()
            if current_h2:
                sections.append(f"{current_h2} > {h3}")

    return sections


def is_skip_dir(d):
    """是否跳過此目錄的 backward 檢查"""
    for skip in SKIP_DIRS_FOR_BACKWARD:
        if d == skip or d.startswith(skip + "/"):
            return True
    for pattern in SKIP_DIR_PATTERNS:
        if pattern in d:
            return True
    return False


def suggest_section(filepath, rules):
    """給定檔案路徑，回傳 first-match 的區段。
    與 obsidian-check.py 的 suggest_section() 邏輯一致。"""
    for rule in rules:
        pattern = rule.get("pattern", "")
        try:
            if PurePosixPath(filepath).match(pattern):
                return rule.get("section", "?"), pattern
        except (ValueError, TypeError):
            continue
    return None, None


def validate(map_data, verbose=True):
    """執行完整驗證，回傳 (warnings, errors)"""
    rules = map_data.get("rules", [])
    sections = set(map_data.get("sections", []))
    tracked_dirs = map_data.get("tracked_directories", [])

    warnings = []
    errors = []

    # 1. Forward: rule.section 是否在 sections 中
    for i, rule in enumerate(rules):
        section = rule.get("section", "")
        pattern = rule.get("pattern", "")

        # 跳過動態佔位 section
        if section.startswith("("):
            continue

        if section not in sections:
            errors.append(f"Rule #{i+1} pattern='{pattern}': section '{section}' 不在 sections 清單中")

    # 2. Rule 語法：測試每個 pattern 是否能被 PurePosixPath.match() 接受
    for i, rule in enumerate(rules):
        pattern = rule.get("pattern", "")
        try:
            PurePosixPath("test/file.md").match(pattern)
        except (ValueError, TypeError) as e:
            errors.append(f"Rule #{i+1} pattern='{pattern}': 語法錯誤 — {e}")

    # 3. Backward: tracked 目錄是否都有覆蓋
    uncovered = []
    for d in tracked_dirs:
        if is_skip_dir(d):
            continue
        # 用一個假檔案測試此目錄是否有規則覆蓋
        test_paths = [f"{d}/test.md", f"{d}/test.yaml"]
        covered = False
        for tp in test_paths:
            section, _ = suggest_section(tp, rules)
            if section:
                covered = True
                break
        if not covered:
            uncovered.append(d)

    if uncovered:
        for d in uncovered:
            warnings.append(f"目錄未被任何 rule 覆蓋: {d}")

    # 4. Section 完整：HOME.md 的區段是否都在 sections 清單中
    home_sections = get_home_sections()
    for hs in home_sections:
        if hs not in sections:
            warnings.append(f"HOME.md 區段 '{hs}' 不在地圖的 sections 清單中")

    if verbose:
        print(f"[map-validate] 驗證完成")
        print(f"  規則數: {len(rules)}")
        print(f"  區段數: {len(sections)}")
        print(f"  tracked 目錄數: {len(tracked_dirs)}")
        print(f"  錯誤: {len(errors)}")
        print(f"  警告: {len(warnings)}")

        if errors:
            print("\n--- 錯誤 ---")
            for e in errors:
                print(f"  ERROR: {e}")
        if warnings:
            print("\n--- 警告 ---")
            for w in warnings:
                print(f"  WARN: {w}")

        if not errors and not warnings:
            print("\n  全部通過！")

    return warnings, errors


def cmd_rebuild_dirs(map_data, silent=False):
    """重建 tracked_directories"""
    dirs = get_tracked_directories()
    lines = ["tracked_directories:"]
    if dirs:
        for d in dirs:
            lines.append(f'  - "{d}"')
    else:
        lines = ["tracked_directories: []"]

    if save_map_section("tracked_directories:", lines):
        if not silent:
            print(f"[map-validate] 已重建 tracked_directories: {len(dirs)} 個目錄")
    else:
        print("ERROR: 寫入失敗", file=sys.stderr)
        sys.exit(1)
    # 更新 in-memory data
    map_data["tracked_directories"] = dirs


def cmd_rebuild_sections(map_data, silent=False):
    """從 HOME.md 重建 sections（自動寫入地圖檔）"""
    sections = get_home_sections()
    lines = ["sections:"]
    for s in sections:
        lines.append(f'  - "{s}"')

    if save_map_section("sections:", lines):
        if not silent:
            print(f"[map-validate] 已重建 sections: {len(sections)} 個區段")
    else:
        print("ERROR: 寫入失敗", file=sys.stderr)
        sys.exit(1)
    # 更新 in-memory data
    map_data["sections"] = sections


def cmd_suggest(filepath, map_data):
    """給定路徑，回傳建議區段"""
    rules = map_data.get("rules", [])
    section, pattern = suggest_section(filepath, rules)
    if section:
        print(f"FILE:NOT_IN_HOME:{filepath}|{section}")
        print(f"  匹配規則: {pattern}")
    else:
        print(f"FILE:NOT_IN_HOME:{filepath}|?")
        print(f"  （無匹配規則，建議向教師確認）")


def cmd_pre_commit(map_data):
    """精簡輸出供 hook 用"""
    warnings, errors = validate(map_data, verbose=False)
    if errors:
        print(f"[map-validate] {len(errors)} 個錯誤")
        for e in errors[:3]:
            print(f"  {e}")
        if len(errors) > 3:
            print(f"  ...還有 {len(errors)-3} 個")
        sys.exit(1)
    elif warnings:
        # 警告不阻擋 commit，只提示
        print(f"[map-validate] {len(warnings)} 個警告（不阻擋 commit）")
        for w in warnings[:3]:
            print(f"  {w}")


def cmd_audit_home():
    """審核 HOME.md 內容完整性：
    1. 死連結：HOME.md 有 wikilink 但檔案不存在
    2. 遺漏：目錄中有 .md/.yaml 但 HOME.md 沒有對應連結
    只審核有路由規則覆蓋的目錄（避免雜訊）。"""

    if not os.path.exists(HOME_PATH):
        print("ERROR: HOME.md 不存在", file=sys.stderr)
        return

    with open(HOME_PATH, "r", encoding="utf-8") as f:
        home_content = f.read()

    # ── 1. 解析 HOME.md 中所有 wikilink 路徑 ──
    # 匹配 [[path|alias]] 和 [[path]] 兩種格式
    wikilink_pattern = re.compile(r'\[\[([^\]|\\]+?)(?:\\?\|[^\]]*)?]]')
    home_links = set()
    for m in wikilink_pattern.finditer(home_content):
        link = m.group(1).strip()
        # 跳過純名稱連結（無路徑分隔符的短連結，如 [[lesson]]）
        if "/" not in link:
            continue
        home_links.add(link)

    # ── 2. 取得 git tracked 檔案 ──
    tracked = set()
    result = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode == 0:
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            path = line.strip()
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]
                if "\\" in path:
                    try:
                        path = path.encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        pass
            tracked.add(path)

    # ── 3. 死連結：HOME 有但檔案不存在 ──
    dead_links = []
    for link in sorted(home_links):
        # wikilink 可能省略副檔名，嘗試多種可能
        candidates = [link, link + ".md", link + ".yaml", link + ".yml"]
        found = False
        for c in candidates:
            if c in tracked or os.path.exists(os.path.join(REPO_ROOT, c)):
                found = True
                break
        if not found:
            dead_links.append(link)

    # ── 4. 遺漏：檔案存在但 HOME 沒有連結 ──
    # 只檢查 .md 和 .yaml（與 obsidian-check INDEXABLE_EXTENSIONS 一致）
    indexable_ext = {".md", ".yaml", ".yml"}
    skip_patterns = [
        ".obsidian/", ".claude/", ".git/", "__pycache__/", "node_modules/",
        "temp1/", "temp2/", "word/", "docProps/", "_rels/",
        "自動化結案報告測試/", "資料處理資料夾/", "/private/",
    ]
    skip_basenames = {"HOME.md", ".DS_Store", ".gitkeep", "token.json", ".env"}

    # 載入地圖規則來限制審核範圍
    map_data = load_map()
    rules = map_data.get("rules", [])

    missing = []
    for f in sorted(tracked):
        ext = os.path.splitext(f)[1].lower()
        if ext not in indexable_ext:
            continue
        basename = os.path.basename(f)
        if basename in skip_basenames:
            continue
        if any(p in f for p in skip_patterns):
            continue
        # 只審核有路由規則覆蓋的檔案
        section, _ = suggest_section(f, rules)
        if not section:
            continue

        # 檢查 HOME.md 是否有此檔案的連結
        name_no_ext = os.path.splitext(basename)[0]
        f_no_ext = os.path.splitext(f)[0] if ext else f
        found_in_home = (
            f in home_content or
            f_no_ext in home_content or
            name_no_ext in home_content
        )
        if not found_in_home:
            missing.append((f, section))

    # ── 輸出 ──
    print(f"[audit-home] HOME.md 內容審核")
    print(f"  HOME wikilinks: {len(home_links)}")
    print(f"  死連結: {len(dead_links)}")
    print(f"  遺漏: {len(missing)}")

    if dead_links:
        print("\n--- 死連結（HOME 有但檔案不存在）---")
        for link in dead_links[:30]:
            print(f"  DEAD: [[{link}]]")
        if len(dead_links) > 30:
            print(f"  ...還有 {len(dead_links) - 30} 個")

    if missing:
        print("\n--- 遺漏（檔案存在但 HOME 未收錄）---")
        for f, section in missing[:30]:
            print(f"  MISSING: {f}  →  建議區段: {section}")
        if len(missing) > 30:
            print(f"  ...還有 {len(missing) - 30} 個")

    if not dead_links and not missing:
        print("\n  全部通過！")

    return dead_links, missing


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Repo 架構地圖驗證與維護")
    parser.add_argument("--validate", action="store_true", help="驗證地圖完整性")
    parser.add_argument("--rebuild-dirs", action="store_true", help="重建 tracked_directories")
    parser.add_argument("--rebuild-sections", action="store_true", help="從 HOME.md 重建 sections 清單")
    parser.add_argument("--pre-commit", action="store_true", help="精簡輸出供 hook 用")
    parser.add_argument("--suggest", metavar="PATH", help="給定路徑，回傳建議區段")
    parser.add_argument("--auto-fix", action="store_true", help="自動修復（重建 dirs）")
    parser.add_argument("--audit-home", action="store_true", help="審核 HOME.md 內容完整性（死連結 + 遺漏）")
    args = parser.parse_args()

    map_data = load_map()

    if args.rebuild_dirs or args.auto_fix:
        cmd_rebuild_dirs(map_data)
        # 重新載入
        map_data = load_map()

    if args.rebuild_sections:
        cmd_rebuild_sections(map_data)

    if args.suggest:
        cmd_suggest(args.suggest, map_data)

    if args.pre_commit:
        cmd_pre_commit(map_data)

    if args.audit_home:
        cmd_audit_home()

    if args.validate or (not any([args.rebuild_dirs, args.rebuild_sections, args.pre_commit, args.suggest, args.auto_fix, args.audit_home])):
        validate(map_data)


if __name__ == "__main__":
    main()
