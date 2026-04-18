#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — Pre-push 身份驗證 + 路徑權限檢查
# 路徑：setup/scripts/pre-push-check.py
# 由 setup/hooks/pre-push 薄層 shell 呼叫
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 作用：在 git push 前，檢查所有待推送 commit：
#   1. author email 是否登記於 ai-core/acl.yaml
#   2. commit 修改的檔案是否在該 email 的 allowed_paths 範圍內
#
# 與 pre-commit-check.py 的差異：
#   pre-commit 檢查「暫存區的檔案」（commit 前）
#   pre-push 檢查「已 commit 但未 push 的完整歷史」（push 前）
#   pre-push 是最後一道 client-side 防線
#
# exit code: 0 = 通過, 1 = 攔截

import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

# ── ANSI 顏色 ─────────────────────────────────────────

RED = "\033[0;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[0;32m"
NC = "\033[0m"


# ── 工具函式 ──────────────────────────────────────────

def git(*args: str) -> str:
    """執行 git 指令，回傳 stdout（去尾換行）。

    統一加 -c core.quotepath=false，避免中文路徑被 git 預設轉義
    成 \\xxx\\xxx，導致與 acl.yaml 的 UTF-8 路徑比對失敗。
    """
    try:
        result = subprocess.run(
            ["git", "-c", "core.quotepath=false"] + list(args),
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:
        return ""


def matches(file_path: str, pattern: str) -> bool:
    if pattern == "*":
        return True
    if pattern.endswith("/"):
        return file_path.startswith(pattern)
    if "*" in pattern:
        return fnmatch.fnmatch(file_path, pattern)
    return file_path == pattern or file_path.startswith(pattern.rstrip("/") + "/")


# ── ACL 解析（與 pre-commit-check.py 相同邏輯）─────────

def parse_acl(acl_path: Path):
    content = acl_path.read_text(encoding="utf-8")
    teachers: dict = {}

    def register(email, gh_username, entry):
        teachers[email] = entry
        if gh_username:
            noreply = f"{gh_username}@users.noreply.github.com"
            teachers[noreply] = entry

    # Admin
    admin_m = re.search(r"admin:\s*\n(.*?)(?=\n\S|\Z)", content, re.DOTALL)
    if admin_m:
        admin_block = admin_m.group(0)
        emails = re.findall(r"email:\s*([^\s#\n]+)", admin_block)
        gh_users = re.findall(r"github_username:\s*([^\s#\n]+)", admin_block)
        for i, email in enumerate(emails):
            gh = gh_users[i].strip() if i < len(gh_users) else None
            entry = {"is_admin": True, "allowed_paths": ["*"], "name": "Admin"}
            register(email.strip(), gh, entry)

    # Teachers
    for m in re.finditer(
        r"-\s+name:\s+(.+?)\n(?:.*?\n)*?\s+email:\s+([^\s#\n]+)"
        r"(?:.*?\n)*?\s+allowed_paths:\s*\n((?:\s+-[^\n]+\n)*)",
        content, re.DOTALL,
    ):
        name = m.group(1).strip()
        email = m.group(2).strip()
        paths_raw = m.group(3)
        paths = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", paths_raw)
        ]
        block_text = m.group(0)
        gh_m = re.search(r"github_username:\s*([^\s#\n]+)", block_text)
        gh = gh_m.group(1).strip() if gh_m else None
        if email not in teachers:
            entry = {"is_admin": False, "allowed_paths": paths, "name": name}
            register(email, gh, entry)

    # protected_always
    protected: list[str] = []
    pa_m = re.search(r"protected_always:\s*\n((?:\s+-[^\n]+\n)*)", content)
    if pa_m:
        protected = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", pa_m.group(1))
        ]

    # shared_writable
    shared: list[str] = []
    sw_m = re.search(r"shared_writable:\s*\n((?:\s+-[^\n]+\n)*)", content)
    if sw_m:
        shared = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", sw_m.group(1))
        ]

    return teachers, protected, shared


# ── 主流程 ────────────────────────────────────────────

def main() -> int:
    repo_root = Path(git("rev-parse", "--show-toplevel"))
    acl_file = repo_root / "ai-core" / "acl.yaml"

    if not acl_file.is_file():
        # 沒有 ACL 檔 → 跳過檢查
        return 0

    # ── Hook 健康檢查 ────────────────────────────────
    # 若 pre-commit hook 不存在，提醒教師重新安裝
    pre_commit_hook = repo_root / "setup" / "hooks" / "pre-commit"
    git_hook = repo_root / ".git" / "hooks" / "pre-commit"
    hooks_path = git("config", "core.hooksPath")
    if hooks_path:
        effective_hook = repo_root / hooks_path / "pre-commit"
    else:
        effective_hook = git_hook
    if not effective_hook.is_file():
        print(f"  {YELLOW}[警告] 偵測到 pre-commit hook 未安裝。{NC}")
        print(f"  {YELLOW}請執行以下指令安裝安全檢查機制：{NC}")
        print(f"    macOS / Linux：bash setup/start.sh")
        print(f"    Windows：.\\setup\\start.ps1")
        print()

    try:
        teachers, protected, shared = parse_acl(acl_file)
    except Exception as e:
        print(f"{YELLOW}[pre-push] ACL 解析錯誤，跳過檢查：{e}{NC}")
        return 0

    # ── 分支偵測：v2.0 分支模型 ──────────────────────
    # admin：可以推送任何分支（包含 main）；非 main 時提示
    # teacher：只能推送自己的 workspace/Teacher_{姓名} 分支
    #         推 main 或別人的分支 → 攔截
    current_branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if current_branch:
        # 先判斷 pusher 身份
        env_file_br = repo_root / "setup" / "environment.env"
        pusher_br = ""
        if env_file_br.is_file():
            for _line in env_file_br.read_text(encoding="utf-8").splitlines():
                _m = re.match(r"^USER_EMAIL=(.+)$", _line.strip())
                if _m:
                    pusher_br = _m.group(1).strip()
                    break
        if not pusher_br:
            pusher_br = git("config", "user.email")

        user_br = teachers.get(pusher_br)
        if user_br and not user_br.get("is_admin"):
            expected_branch = f"workspace/Teacher_{user_br['name']}"
            if current_branch != expected_branch:
                print()
                print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
                if current_branch == "main":
                    print(f"{RED}  [攔截] 你正在推送 main，但 v2.0 分支模型要求教師推送自己的分支。{NC}")
                else:
                    print(f"{RED}  [攔截] 你正在推送分支「{current_branch}」，不是你的個人分支。{NC}")
                print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
                print()
                print(f"  你的個人分支：{expected_branch}")
                print()
                print(f"  請切回自己的分支後再 push：")
                print(f"    git checkout {expected_branch}")
                print(f"    git push origin {expected_branch}")
                print()
                print(f"  若此分支尚未建立，請聯絡 David。")
                print()
                return 1

    # ── Pusher 身份檢查：Admin 直接放行 ─────────────
    # 管理員 cherry-pick 教師 commit 時，author email 是教師的，
    # 但 pusher（當前使用者）是管理員——此時應放行。
    env_file = repo_root / "setup" / "environment.env"
    pusher_email = ""
    if env_file.is_file():
        for _line in env_file.read_text(encoding="utf-8").splitlines():
            _m = re.match(r"^USER_EMAIL=(.+)$", _line.strip())
            if _m:
                pusher_email = _m.group(1).strip()
                break
    if not pusher_email:
        pusher_email = git("config", "user.email")
    if pusher_email in teachers and teachers[pusher_email].get("is_admin"):
        print(f"  {GREEN}管理員 push，跳過逐 commit 路徑檢查。{NC}")
        return 0

    # ── 從 stdin 讀取 push 範圍 ──────────────────────
    # Git pre-push hook stdin 格式：
    #   <local ref> <local sha> <remote ref> <remote sha>
    # 可能有多行（push 多個 ref）

    violations_email: list[tuple[str, str, str]] = []  # (sha, email, subject)
    violations_path: list[tuple[str, str, str, str]] = []  # (sha, email, file, reason)

    zero_sha = "0" * 40

    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) < 4:
            continue

        local_sha = parts[1]
        remote_sha = parts[3]

        # 刪除分支
        if local_sha == zero_sha:
            continue

        # 新分支：檢查所有 commit（相對於 remote 的所有分支）
        if remote_sha == zero_sha:
            commit_range = local_sha
            range_arg = f"--not --remotes=origin"
            commits_raw = git(
                "log", "--format=%H|%ae|%s",
                local_sha, "--not", "--remotes=origin",
            )
        else:
            commits_raw = git(
                "log", "--format=%H|%ae|%s",
                f"{remote_sha}..{local_sha}",
            )

        if not commits_raw:
            continue

        for commit_line in commits_raw.splitlines():
            if "|" not in commit_line:
                continue
            parts2 = commit_line.split("|", 2)
            sha = parts2[0]
            email = parts2[1]
            subject = parts2[2] if len(parts2) > 2 else ""

            # ── 檢查 1：Email 是否在 ACL 中 ─────────
            if email not in teachers:
                violations_email.append((sha[:8], email, subject))
                continue  # email 未知，無法做路徑檢查

            user = teachers[email]

            # Admin 跳過路徑檢查
            if user["is_admin"]:
                continue

            # ── 檢查 2：路徑是否在 allowed_paths 中 ──
            # 使用 -z 避免 git 對非 ASCII 檔名加引號（quoted octal escape）
            changed_files_raw = git(
                "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", sha,
            )
            if not changed_files_raw:
                continue

            for f in changed_files_raw.split("\0"):
                f = f.strip()
                if not f:
                    continue
                is_protected = any(matches(f, p) for p in protected)
                is_allowed = (
                    any(matches(f, p) for p in user["allowed_paths"])
                    or any(matches(f, p) for p in shared)
                )
                if is_protected:
                    violations_path.append((sha[:8], email, f, "受保護路徑"))
                elif not is_allowed:
                    violations_path.append((sha[:8], email, f, "超出授權範圍"))

    # ── 結果 ─────────────────────────────────────────

    if not violations_email and not violations_path:
        return 0

    print()
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"{RED}  [攔截 Push] 偵測到身份或權限問題{NC}")
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print()

    if violations_email:
        print(f"  {RED}未登記的 Author Email：{NC}")
        for sha, email, subject in violations_email:
            print(f"    {sha} | {email} | {subject}")
        print()
        print(f"  {YELLOW}此 Email 未登記於 ai-core/acl.yaml。{NC}")
        print(f"  {YELLOW}請執行以下指令修正你的 Git 身份：{NC}")
        print()
        print(f"    macOS / Linux：bash setup/start.sh")
        print(f"    Windows：.\\setup\\start.ps1")
        print()
        print(f"  修正後，用以下指令更新 commit 的 author：")
        print(f"    git commit --amend --reset-author")
        print()

    if violations_path:
        print(f"  {RED}超出授權範圍的檔案修改：{NC}")
        for sha, email, filepath, reason in violations_path:
            print(f"    {sha} | {email} | {reason}：{filepath}")
        print()
        print(f"  {YELLOW}你只能修改自己 Workspace 內的檔案。{NC}")
        print(f"  如需擴充權限，請聯絡 David。")
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
