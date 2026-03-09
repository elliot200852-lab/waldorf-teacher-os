#!/usr/bin/env python3
"""
TeacherOS Obsidian Label Checker
掃描 Repo 中缺少中文標籤的 .md / .yaml 檔案，以及未收錄 HOME.md 的檔案。
只做偵測與報告，不修改任何檔案。

用法：
    python3 obsidian-check.py                # 完整掃描（所有 git 追蹤檔案）
    python3 obsidian-check.py --staged-only  # 只掃描 git 暫存區新增檔案
    python3 obsidian-check.py --count-only   # 只輸出數字（供提醒用）

不依賴外部套件，只使用 Python 標準函式庫。
"""

import os
import re
import subprocess
import sys

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # setup/scripts/ → 上兩層

# ── 排除規則 ──────────────────────────────────────────────
EXCLUDED_FILES = {".DS_Store", ".gitkeep", "token.json", ".env"}
EXCLUDED_DIRS = {".obsidian", ".claude/worktrees", "__pycache__", "node_modules", "venv"}

# 這些目錄的 .md 檔使用 name: 而非 aliases:，跳過 aliases 檢查
SKIP_ALIAS_DIRS = {"ai-core/skills"}

# HOME.md 自身不需要被收錄檢查
SKIP_HOME_CHECK = {"HOME.md"}


def is_excluded(filepath):
    """檢查檔案是否在排除清單中"""
    basename = os.path.basename(filepath)
    if basename in EXCLUDED_FILES:
        return True
    for excluded_dir in EXCLUDED_DIRS:
        if filepath.startswith(excluded_dir + "/") or ("/" + excluded_dir + "/") in filepath:
            return True
    return False


def decode_git_path(path):
    """解碼 git 的 octal 跳脫路徑（中文檔名會被 git 編碼為 \\xxx 格式）"""
    path = path.strip()
    # git 用雙引號包裹含特殊字元的路徑
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
    # 解碼 octal 跳脫序列（如 \346\225\231 → 教）
    if "\\" in path:
        try:
            path = path.encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    return path


def get_tracked_files():
    """取得所有 git 追蹤的檔案"""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0:
        return []
    return [decode_git_path(f) for f in result.stdout.strip().split("\n") if f.strip()]


def get_staged_new_files():
    """取得 git 暫存區中新增的檔案"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0:
        return []
    return [decode_git_path(f) for f in result.stdout.strip().split("\n") if f.strip()]


def has_chinese(text):
    """檢查文字中是否包含中文字元"""
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def md_needs_alias(filepath):
    """檢查 .md 檔是否缺少 aliases: frontmatter"""
    # 跳過使用 name: 的目錄
    for skip_dir in SKIP_ALIAS_DIRS:
        if filepath.startswith(skip_dir + "/"):
            return False
    # .claude/commands/ 和 .claude/skills/ 使用 name: 而非 aliases:
    if filepath.startswith(".claude/commands/") or filepath.startswith(".claude/skills/"):
        return False

    full_path = os.path.join(REPO_ROOT, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(2000)  # 只讀前 2000 字元
    except (FileNotFoundError, UnicodeDecodeError):
        return False

    if not content.startswith("---"):
        return True

    end = content.find("---", 3)
    if end < 0:
        return True

    frontmatter = content[3:end]
    return "aliases:" not in frontmatter


def yaml_needs_label(filepath):
    """檢查 .yaml 檔前 5 行是否有中文字元"""
    full_path = os.path.join(REPO_ROOT, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= 5:
                    break
                lines.append(line)
    except (FileNotFoundError, UnicodeDecodeError):
        return False

    text = "".join(lines)
    return not has_chinese(text)


def file_in_home(filepath, home_content):
    """檢查檔案是否被 HOME.md 引用"""
    if filepath in SKIP_HOME_CHECK:
        return True

    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]

    # 比對完整路徑或不含副檔名的檔名
    return (filepath in home_content) or (name_no_ext in home_content)


def main():
    staged_only = "--staged-only" in sys.argv
    count_only = "--count-only" in sys.argv

    # 取得檔案清單
    if staged_only:
        files = get_staged_new_files()
    else:
        files = get_tracked_files()

    # 讀取 HOME.md
    home_path = os.path.join(REPO_ROOT, "HOME.md")
    home_content = ""
    try:
        with open(home_path, "r", encoding="utf-8") as f:
            home_content = f.read()
    except FileNotFoundError:
        pass

    # 分類檢查
    unlabeled_md = []
    unlabeled_yaml = []
    not_in_home = []

    for filepath in files:
        if is_excluded(filepath):
            continue

        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".md":
            if md_needs_alias(filepath):
                unlabeled_md.append(filepath)
            if not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

        elif ext == ".yaml" or ext == ".yml":
            if yaml_needs_label(filepath):
                unlabeled_yaml.append(filepath)
            if not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

        else:
            # 其他類型檔案只檢查 HOME.md 收錄
            if not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

    # 輸出
    total = len(unlabeled_md) + len(unlabeled_yaml) + len(not_in_home)

    if count_only:
        if total == 0:
            print("[obsidian-check] OK")
        else:
            parts = []
            if unlabeled_md:
                parts.append(f"{len(unlabeled_md)} 個 .md 未標籤")
            if unlabeled_yaml:
                parts.append(f"{len(unlabeled_yaml)} 個 .yaml 未標籤")
            if not_in_home:
                parts.append(f"{len(not_in_home)} 個未收錄 HOME.md")
            print(f"[obsidian-check] {', '.join(parts)}")
        return

    # 完整輸出
    print("[obsidian-check] SCAN_COMPLETE")
    print(f"UNLABELED_MD:{len(unlabeled_md)}")
    print(f"UNLABELED_YAML:{len(unlabeled_yaml)}")
    print(f"NOT_IN_HOME:{len(not_in_home)}")

    for f in unlabeled_md:
        print(f"FILE:NEW_MD:{f}")
    for f in unlabeled_yaml:
        print(f"FILE:NEW_YAML:{f}")
    for f in not_in_home:
        print(f"FILE:NOT_IN_HOME:{f}")


if __name__ == "__main__":
    main()
