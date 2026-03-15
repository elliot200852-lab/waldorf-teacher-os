#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — Post-merge Check（Good-notes 新分享通知）
# 路徑：setup/scripts/post-merge-check.py
# 觸發時機：git pull / git merge 完成後，由 post-merge hook 呼叫
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 功能：檢查剛拉進來的 commit 是否有人在 Good-notes/ 新增或修改筆記，
#       若有，在終端機顯示通知，包含作者姓名與檔案清單。
#       自己的改動不通知。

import os
import re
import sys
import subprocess
from pathlib import Path
from collections import OrderedDict


def get_repo_root() -> Path:
    """取得 Git repo 根目錄。"""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(0)
    return Path(result.stdout.strip())


def get_my_emails(repo_root: Path) -> set:
    """從 environment.env 與 git config 收集本機使用者的 email，用於排除自己的 commit。"""
    emails = set()

    # 從 environment.env 讀取
    env_file = repo_root / "setup" / "environment.env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^USER_EMAIL=(.+)", line)
            if m:
                email = m.group(1).strip()
                if email:
                    emails.add(email)

    # 從 git config 讀取
    result = subprocess.run(
        ["git", "config", "user.email"],
        capture_output=True, text=True
    )
    git_email = result.stdout.strip()
    if git_email:
        emails.add(git_email)

    return emails


def get_orig_head(repo_root: Path) -> str:
    """讀取 ORIG_HEAD，若不存在則回傳空字串。"""
    orig_head_file = repo_root / ".git" / "ORIG_HEAD"
    if not orig_head_file.is_file():
        return ""
    return orig_head_file.read_text(encoding="utf-8").strip()


def has_goodnotes_changes(repo_root: Path, orig_head: str) -> bool:
    """快速檢查 Good-notes/ 是否有變動。"""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{orig_head}..HEAD", "--", "Good-notes/"],
        capture_output=True, text=True, cwd=str(repo_root)
    )
    if result.returncode != 0:
        return False
    return bool(result.stdout.strip())


def build_name_map(repo_root: Path) -> dict:
    """從 acl.yaml 建立 email / github_username → 中文姓名對照表。"""
    name_map = {}
    acl_path = repo_root / "ai-core" / "acl.yaml"
    if not acl_path.is_file():
        return name_map

    acl = acl_path.read_text(encoding="utf-8")
    current_name = ""

    for line in acl.splitlines():
        m_name = re.match(r"\s+-\s+name:\s*(.+)", line)
        if m_name:
            raw = m_name.group(1).strip().strip("\"'")
            # 取括號前的中文名，如「林信宏（David）」→「林信宏」
            current_name = re.sub(r"[（(].+[）)]", "", raw).strip()

        m_email = re.match(r"\s+email:\s*(.+)", line)
        if m_email and current_name:
            email = m_email.group(1).strip().strip("\"'")
            name_map[email] = current_name

        m_gh = re.match(r"\s+github_username:\s*(.+)", line)
        if m_gh and current_name:
            gh = m_gh.group(1).strip().strip("\"'")
            name_map[f"{gh}@users.noreply.github.com"] = current_name

    return name_map


def resolve_name(email: str, git_name: str, name_map: dict) -> str:
    """將 email 對照為中文姓名，找不到則回傳 git author name。"""
    return name_map.get(email, git_name)


def collect_entries(repo_root: Path, orig_head: str, my_emails: set, name_map: dict) -> list:
    """解析 git log，收集其他人在 Good-notes/ 的變動。回傳 [(display_name, symbol, filename)]。"""
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", "log", f"{orig_head}..HEAD",
         "--diff-filter=ACMR", "--name-status", "--format=%H %ae %an",
         "--", "Good-notes/"],
        capture_output=True, text=True, cwd=str(repo_root)
    )
    if result.returncode != 0:
        return []

    entries = []
    current_email = ""
    current_name = ""
    status_symbols = {"A": "+", "C": "+", "M": "~", "R": ">"}

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        # commit 行：HASH email name
        if re.match(r"^[0-9a-f]{40} ", line):
            parts = line.split(" ", 2)
            current_email = parts[1]
            git_author = parts[2] if len(parts) > 2 else ""
            current_name = resolve_name(current_email, git_author, name_map)
            continue

        # 跳過自己
        if current_email in my_emails:
            continue

        # 檔案行：STATUS\tPATH
        cols = line.split("\t")
        if len(cols) < 2:
            continue

        st, fpath = cols[0], cols[1]
        sym = status_symbols.get(st, "?")
        fname = Path(fpath).name
        entries.append((current_name, sym, fname))

    # 去重（保留順序）
    return list(dict.fromkeys(entries))


def print_notification(entries: list) -> None:
    """輸出通知到終端機。"""
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Good-notes 有新分享！")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # 按作者分組
    by_author: OrderedDict = OrderedDict()
    for name, sym, fname in entries:
        by_author.setdefault(name, []).append((sym, fname))

    for author, files in by_author.items():
        print(f"  {author} 分享了 {len(files)} 個筆記：")
        for sym, fname in files:
            print(f"    {sym} {fname}")
        print()

    print("  查看詳情：git log ORIG_HEAD..HEAD -- Good-notes/")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()


def main() -> None:
    repo_root = get_repo_root()
    my_emails = get_my_emails(repo_root)

    orig_head = get_orig_head(repo_root)
    if not orig_head:
        sys.exit(0)

    if not has_goodnotes_changes(repo_root, orig_head):
        sys.exit(0)

    name_map = build_name_map(repo_root)
    entries = collect_entries(repo_root, orig_head, my_emails, name_map)

    if not entries:
        sys.exit(0)

    print_notification(entries)


if __name__ == "__main__":
    main()
