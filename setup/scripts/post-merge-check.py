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
        ["git", "-c", "core.quotepath=false", "diff", "--name-only",
         f"{orig_head}..HEAD", "--", "Good-notes/"],
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


def verify_identity(repo_root: Path, my_emails: set) -> None:
    """Pull 後驗證本機使用者身份是否在 ACL 中登記。"""
    acl_path = repo_root / "ai-core" / "acl.yaml"
    if not acl_path.is_file():
        return

    acl = acl_path.read_text(encoding="utf-8")

    # 收集 ACL 中所有已登記的 email
    registered = set()
    for m in re.finditer(r"email:\s*([^\s#\n]+)", acl):
        registered.add(m.group(1).strip())
    for m in re.finditer(r"github_username:\s*([^\s#\n]+)", acl):
        gh = m.group(1).strip()
        registered.add(f"{gh}@users.noreply.github.com")

    # Bot emails
    registered.add("noreply@github.com")
    registered.add("41898282+github-actions[bot]@users.noreply.github.com")

    # 檢查本機 email 是否有任何一個在 ACL 中
    if my_emails & registered:
        # 至少有一個 email 已登記，顯示確認
        matched = (my_emails & registered).pop()
        print(f"  \033[0;32m身份確認：{matched}\033[0m")
        return

    # 沒有任何 email 在 ACL 中
    email_list = ", ".join(my_emails) if my_emails else "(未設定)"
    print()
    print("\033[1;33m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    print(f"\033[1;33m  [警告] 你的 Email（{email_list}）未登記於 acl.yaml\033[0m")
    print("\033[1;33m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    print()
    print("  你的 commit 將會被 pre-commit hook 攔截。")
    print("  請執行以下指令重新設定身份：")
    print()
    print("    macOS / Linux：bash setup/start.sh")
    print("    Windows：.\\setup\\start.ps1")
    print()


def main() -> None:
    repo_root = get_repo_root()
    my_emails = get_my_emails(repo_root)

    # ── 身份驗證（每次 pull 後執行）──────────────────
    verify_identity(repo_root, my_emails)

    # ── 分支偵測（每次 pull 後提醒）──────────────────
    # v2.0 分支模型：
    #   - main：admin 的工作分支（正常）
    #   - workspace/Teacher_{姓名}：教師的個人工作分支（正常）
    #   - 其他分支：不應該，提示
    result_br = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    current_branch = result_br.stdout.strip() if result_br.returncode == 0 else ""
    if (
        current_branch
        and current_branch != "main"
        and not current_branch.startswith("workspace/Teacher_")
    ):
        print()
        print("\033[1;33m  [提醒] 你目前在分支「%s」，不是 main 也不是個人分支。\033[0m" % current_branch)
        print("  若這是意外，請切回正確的分支：")
        print("    git checkout main                          （管理員）")
        print("    git checkout workspace/Teacher_{你的姓名}  （教師）")
        print()

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
