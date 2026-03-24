#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — Pre-commit 身份驗證 + 路徑攔截（Python 版）
# 路徑：setup/scripts/pre-commit-check.py
# 由 setup/hooks/pre-commit 薄層 shell 呼叫
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 作用：在 git commit 的瞬間，確認：
#   1. 當前使用者有登記在 ai-core/acl.yaml 中
#   2. 準備提交的檔案都在該使用者的 allowed_paths 範圍內
#   3. 任何 protected_always 的核心路徑修改都會被攔截
#
# 緊急繞過（不建議）：git commit --no-verify
#   注意：此操作不會繞過 GitHub CODEOWNERS 審核，David 仍會在 PR 中看到所有變更。
#
# exit code: 0 = 通過, 1 = 攔截

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

# ── ANSI 顏色 ─────────────────────────────────────────

_NO_COLOR = os.environ.get("NO_COLOR") or (sys.platform == "win32" and not os.environ.get("WT_SESSION"))
RED = "" if _NO_COLOR else "\033[0;31m"
YELLOW = "" if _NO_COLOR else "\033[1;33m"
GREEN = "" if _NO_COLOR else "\033[0;32m"
NC = "" if _NO_COLOR else "\033[0m"


# ── 工具函式 ──────────────────────────────────────────

def git(*args: str) -> str:
    """執行 git 指令，回傳 stdout（去尾換行）。"""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def matches(file_path: str, pattern: str) -> bool:
    """判斷檔案路徑是否符合 ACL pattern。"""
    if pattern == "*":
        return True
    # 目錄 prefix（pattern 以 / 結尾）
    if pattern.endswith("/"):
        return file_path.startswith(pattern)
    # 含萬用字元
    if "*" in pattern:
        return fnmatch.fnmatch(file_path, pattern)
    # 完全相符，或作為目錄前綴
    return file_path == pattern or file_path.startswith(pattern.rstrip("/") + "/")


# ── ACL 解析 ─────────────────────────────────────────

def parse_acl(acl_path: Path):
    """
    解析 acl.yaml，回傳 (teachers, protected_always, shared_writable)。
    teachers: { email: { is_admin, allowed_paths, name } }
    使用純 regex，不依賴 PyYAML。
    """
    content = acl_path.read_text(encoding="utf-8")
    teachers: dict = {}

    def register(email, gh_username, entry):
        teachers[email] = entry
        if gh_username:
            noreply = f"{gh_username}@users.noreply.github.com"
            teachers[noreply] = entry

    # ── 解析 admin 區塊 ──
    admin_m = re.search(r"admin:\s*\n(.*?)(?=\n\S|\Z)", content, re.DOTALL)
    if admin_m:
        admin_block = admin_m.group(0)
        emails = re.findall(r"email:\s*([^\s#\n]+)", admin_block)
        gh_users = re.findall(r"github_username:\s*([^\s#\n]+)", admin_block)
        for i, email in enumerate(emails):
            gh = gh_users[i].strip() if i < len(gh_users) else None
            entry = {"is_admin": True, "allowed_paths": ["*"], "name": "Admin"}
            register(email.strip(), gh, entry)

    # ── 解析 teachers 清單 ──
    for m in re.finditer(
        r"-\s+name:\s+(.+?)\n(?:.*?\n)*?\s+email:\s+([^\s#\n]+)"
        r"(?:.*?\n)*?\s+allowed_paths:\s*\n((?:\s+-[^\n]+\n)*)",
        content,
        re.DOTALL,
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

    # ── 解析 protected_always ──
    protected: list[str] = []
    pa_m = re.search(r"protected_always:\s*\n((?:\s+-[^\n]+\n)*)", content)
    if pa_m:
        protected = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", pa_m.group(1))
        ]

    # ── 解析 shared_writable ──
    shared: list[str] = []
    sw_m = re.search(r"shared_writable:\s*\n((?:\s+-[^\n]+\n)*)", content)
    if sw_m:
        shared = [
            p.strip().strip("\"'")
            for p in re.findall(r"-\s+([^\n#]+)", sw_m.group(1))
        ]

    return teachers, protected, shared


# ── 主流程 ────────────────────────────────────────────

# ── 二進位檔案副檔名（大型檔案不適合 git）────────────

BINARY_EXTENSIONS = {
    # 文件
    ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    # 音訊
    ".mp3", ".m4a", ".wav", ".ogg", ".flac",
    # 影片
    ".mp4", ".mov", ".avi", ".mkv",
    # 壓縮
    ".zip", ".rar", ".7z", ".gz", ".tar",
    # 圖片（大型）
    ".tiff", ".tif", ".bmp", ".emf", ".psd",
    # 執行檔
    ".exe", ".dll",
}

BINARY_THRESHOLD = 10  # 超過此數量才顯示警告


def check_workspace_binaries(workspace_path: str) -> int:
    """
    統計 workspace 中已被 git 追蹤的二進位檔案數量。
    回傳二進位檔案數。
    """
    tracked = git("ls-files", "--", workspace_path)
    if not tracked:
        return 0
    count = 0
    for f in tracked.splitlines():
        # git ls-files 對含非 ASCII 的路徑會加引號，去除後再比對
        f = f.strip('"')
        ext = os.path.splitext(f)[1].lower()
        if ext in BINARY_EXTENSIONS:
            count += 1
    return count


def warn_workspace_binaries(user_name: str, workspace_path: str, count: int):
    """顯示二進位檔案過多的警告（不擋 commit）。"""
    print()
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"{YELLOW}  [提醒] Workspace 中有 {count} 個二進位大檔{NC}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print()
    print("  Git Repo 適合存純文字檔（.md、.yaml），")
    print("  大型檔案（Word、音檔、影片等）建議：")
    print(f"    1. 移到 {workspace_path}private/ 資料夾（只留在本機）")
    print("    2. 上傳到 Google Drive（方便共享）")
    print("    3. PDF、Word 檔可以請 AI 直接幫你轉成 .md 檔儲存，不必煩惱怎麼操作")
    print()
    print("  詳情請聯絡 David。")
    print()


def main() -> int:
    repo_root = Path(git("rev-parse", "--show-toplevel"))
    env_file = repo_root / "setup" / "environment.env"
    acl_file = repo_root / "ai-core" / "acl.yaml"

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  TeacherOS Pre-commit 身份與權限檢查")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # ── Step 1：雙重讀取身份 ──────────────────────────

    env_email = ""
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^USER_EMAIL=(.+)$", line.strip())
            if m:
                env_email = m.group(1).strip()
                break

    git_email = git("config", "user.email")

    # 以 environment.env 為主，git config 為備
    current_email = env_email or git_email

    if not current_email:
        print(f"{RED}[錯誤] 無法識別使用者身份。{NC}")
        print("請確認 setup/environment.env 中的 USER_EMAIL 欄位已填入。")
        print()
        return 1

    # 若兩者都有值但不一致，顯示警告
    if env_email and git_email and env_email != git_email:
        print(f"{YELLOW}[警告] 身份資訊不一致，以 environment.env 為準：{NC}")
        print(f"  environment.env  USER_EMAIL : {env_email}")
        print(f"  git config user.email       : {git_email}")
        print()

    print(f"  識別身份：{current_email}")

    # ── Step 2：確認 ACL 與暫存檔案 ──────────────────

    if not acl_file.is_file():
        print(f"{YELLOW}[警告] 找不到 ai-core/acl.yaml，跳過權限檢查。{NC}")
        print("請聯絡 David 確認系統設定。")
        print()
        return 0

    staged_output = git("diff", "--cached", "--name-only")
    if not staged_output:
        print("  暫存區為空，無需檢查。")
        print()
        return 0

    staged_files = [f for f in staged_output.splitlines() if f.strip()]

    # ── Step 3：解析 ACL 並比對路徑 ──────────────────

    try:
        teachers, protected, shared = parse_acl(acl_file)
    except Exception as e:
        print(f"{YELLOW}[警告] ACL 檢查時發生錯誤，跳過路徑比對：{NC} {e}")
        print("請聯絡 David 確認 ai-core/acl.yaml 格式正確。")
        print()
        return 0

    # 未知使用者
    if current_email not in teachers:
        print(f"{RED}[拒絕] 此帳號未登記於 acl.yaml：{NC} {current_email}")
        print("請聯絡 David，請他將你加入 ai-core/acl.yaml 後再操作。")
        print()
        return 1

    user = teachers[current_email]

    # 管理員通過
    if user["is_admin"]:
        print(f"  {GREEN}管理員身份確認，全域授權通過。{NC}")
        print()
        return 0

    # ── Step 4：逐檔比對權限 ─────────────────────────

    blocked: list[tuple[str, str]] = []  # (type, filepath)
    for f in staged_files:
        is_protected = any(matches(f, p) for p in protected)
        is_allowed = (
            any(matches(f, p) for p in user["allowed_paths"])
            or any(matches(f, p) for p in shared)
        )
        if is_protected:
            blocked.append(("PROTECTED", f))
        elif not is_allowed:
            blocked.append(("BLOCKED", f))

    # 全部通過
    if not blocked:
        name = user["name"]
        print(f"  {GREEN}身份確認：{name}，所有修改在授權範圍內，通過。{NC}")

        # ── Step 5：二進位檔案數量警告（僅提醒，不擋）──
        workspace_path = ""
        for p in user["allowed_paths"]:
            if p.startswith("workspaces/"):
                workspace_path = p
                break
        if workspace_path:
            bin_count = check_workspace_binaries(workspace_path)
            if bin_count > BINARY_THRESHOLD:
                warn_workspace_binaries(name, workspace_path, bin_count)

        print()
        return 0

    # ── 有攔截 ───────────────────────────────────────

    print()
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"{RED}  [拒絕提交] 發現超出授權的檔案修改{NC}")
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print()

    for block_type, filepath in blocked:
        if block_type == "BLOCKED":
            print(f"  {RED}✗ 無操作權限：{NC} {filepath}")
        elif block_type == "PROTECTED":
            print(f"  {RED}✗ 受保護的核心路徑：{NC} {filepath}")

    print()
    print("你的授權範圍請查閱：ai-core/acl.yaml")
    print("如需擴充權限，請聯絡 David 更新 acl.yaml（需要 GitHub PR 審核）。")
    print()
    print("如確認為緊急必要操作，可使用：")
    print("  git commit --no-verify")
    print("此操作仍會觸發 GitHub PR 的 CODEOWNERS 審核，David 將看到所有變更。")
    print()
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "TeacherOS Pre-commit 身份驗證與路徑權限檢查。\n"
            "由 setup/hooks/pre-commit 薄層 shell 呼叫，\n"
            "檢查 git 暫存區中的檔案是否在使用者的 ACL 授權範圍內。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "流程：\n"
            "  Step 1  從 environment.env + git config 讀取使用者身份\n"
            "  Step 2  確認 ai-core/acl.yaml 存在，取得暫存檔案清單\n"
            "  Step 3  解析 ACL（admin / teachers / protected_always / shared_writable）\n"
            "  Step 4  逐檔比對權限，輸出結果\n"
            "\n"
            "Exit codes:\n"
            "  0  通過（允許提交）\n"
            "  1  攔截（拒絕提交）\n"
            "\n"
            "緊急繞過：git commit --no-verify\n"
            "  注意：GitHub CODEOWNERS 審核仍然生效。"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
    sys.exit(main())
