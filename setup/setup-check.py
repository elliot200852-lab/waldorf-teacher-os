#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — 環境檢查腳本（Python 版）
# 路徑：setup/setup-check.py
# 用途：新老師第一次使用時，確認所有必要環境是否就緒
# 使用方式：python3 setup/setup-check.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


# ──────────────────────────────────────────────────────────
# 全域計數器
# ──────────────────────────────────────────────────────────

_pass_count = 0
_fail_count = 0


def check_pass(msg: str) -> None:
    global _pass_count
    print(f"  [OK]  {msg}")
    _pass_count += 1


def check_fail(msg: str) -> None:
    global _fail_count
    print(f"  [!!]  {msg}")
    _fail_count += 1


def check_info(msg: str) -> None:
    """選用項目未安裝/未設定時的提示訊息（不計入 PASS / FAIL）。"""
    print(f"  [i ]  {msg}")


def section(title: str) -> None:
    print()
    print(f"── {title} ──────────────────────────────────────────")


def run_cmd(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """執行外部指令，回傳 CompletedProcess。"""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def read_env_file(path: Path) -> dict[str, str]:
    """讀取 .env 檔案，回傳 key=value dict（忽略註解與空行）。"""
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


# ──────────────────────────────────────────────────────────
# OS 偵測
# ──────────────────────────────────────────────────────────

def detect_os() -> tuple[str, bool]:
    """
    回傳 (os_type, is_wsl)。
    os_type: "macos" | "linux" | "windows" | "unknown"
    """
    system = platform.system()
    is_wsl = False

    if system == "Darwin":
        return "macos", False
    elif system == "Linux":
        # 偵測 WSL
        try:
            proc_version = Path("/proc/version").read_text(encoding="utf-8", errors="ignore")
            if "microsoft" in proc_version.lower():
                is_wsl = True
        except OSError:
            pass
        return "linux", is_wsl
    elif system == "Windows":
        return "windows", False
    else:
        return "unknown", False


# ──────────────────────────────────────────────────────────
# 各項檢查
# ──────────────────────────────────────────────────────────

def check_env_file(repo_root: Path, env_data: dict[str, str]) -> None:
    """檢查 1：個人設定檔"""
    section("1. 個人設定檔")

    env_file = repo_root / "setup" / "environment.env"

    if not env_file.is_file():
        check_fail("找不到 setup/environment.env")
        print()
        print("  請執行以下指令建立個人設定檔：")
        print("  cp setup/environment.env.example setup/environment.env")
        print("  然後用文字編輯器打開，填入你的個人資訊。")
        return

    check_pass("setup/environment.env 存在")

    user_name = env_data.get("USER_NAME", "")
    if user_name and user_name != "你的姓名":
        check_pass(f"USER_NAME 已設定：{user_name}")
    else:
        check_fail("USER_NAME 尚未設定（請修改 setup/environment.env）")

    gdrive_email = env_data.get("GOOGLE_DRIVE_EMAIL", "")
    if gdrive_email and gdrive_email != "你的帳號@gmail.com":
        check_pass(f"GOOGLE_DRIVE_EMAIL 已設定：{gdrive_email}")
    else:
        check_fail("GOOGLE_DRIVE_EMAIL 尚未設定")


def check_pandoc(os_type: str, env_data: dict[str, str]) -> None:
    """檢查 2：Pandoc"""
    section("2. Pandoc（Markdown → Word 轉換工具）")

    pandoc_bin = env_data.get("PANDOC_PATH", "") or "pandoc"
    pandoc_path = shutil.which(pandoc_bin)

    if pandoc_path:
        r = run_cmd([pandoc_path, "--version"])
        version = r.stdout.strip().splitlines()[0] if r.stdout else "已安裝"
        check_pass(f"Pandoc 已安裝：{version}")
    else:
        check_fail("找不到 Pandoc")
        print()
        print("  請安裝 Pandoc：")
        if os_type == "macos":
            print("  1. 先安裝 Homebrew（如尚未安裝）：")
            print('     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            print("  2. 安裝 Pandoc：")
            print("     brew install pandoc")
        elif os_type == "linux":
            print("    sudo apt install pandoc")
        elif os_type == "windows":
            print("    winget install JohnMacFarlane.Pandoc")
            print()
            print("  安裝後重新開啟終端機，若仍找不到，請在 environment.env 設定完整路徑：")
            print("    PANDOC_PATH=/c/Users/<帳號>/AppData/Local/Microsoft/WinGet/Packages/...")
        else:
            print("  請至 https://pandoc.org/installing.html 下載安裝")


def check_google_drive(os_type: str, is_wsl: bool, env_data: dict[str, str]) -> None:
    """檢查 3：Google Drive for Desktop"""
    section("3. Google Drive for Desktop")

    if os_type == "macos":
        cloud_storage = Path.home() / "Library" / "CloudStorage"
        if cloud_storage.is_dir():
            gdrive_accounts = [
                d.name.replace("GoogleDrive-", "")
                for d in cloud_storage.iterdir()
                if d.name.startswith("GoogleDrive-")
            ]
            if gdrive_accounts:
                check_pass("Google Drive for Desktop 已安裝並登入")
                print()
                print("  已連線帳號：")
                for acct in gdrive_accounts:
                    print(f"    - {acct}")
            else:
                check_fail("Google Drive for Desktop 已安裝但未登入任何 Google 帳號")
        else:
            check_fail("找不到 Google Drive for Desktop")
            print()
            print("  請安裝 Google Drive for Desktop：")
            print("  https://www.google.com/drive/download/")
            print("  安裝後登入你的 Google 帳號，並開啟「我的雲端硬碟」同步。")

    elif os_type == "windows":
        gdrive_found = False
        gdrive_root = env_data.get("GOOGLE_DRIVE_ROOT", "")

        if gdrive_root and Path(gdrive_root).is_dir():
            check_pass(f"Google Drive 已掛載：{gdrive_root}")
            gdrive_found = True
        else:
            # 自動偵測常見磁碟機代號
            for letter in "defghijk":
                candidate = Path(f"/{letter}/我的雲端硬碟")
                if candidate.is_dir():
                    check_pass(f"Google Drive 已掛載：{candidate}")
                    gdrive_found = True
                    break

        if not gdrive_found:
            check_fail("找不到 Google Drive 掛載點")
            print()
            print("  請確認 Google Drive for Desktop 已安裝並登入：")
            print("  https://www.google.com/drive/download/")
            print("  安裝後，在 environment.env 加入掛載根目錄（例如）：")
            print("    GOOGLE_DRIVE_ROOT=/h/我的雲端硬碟")

    elif os_type == "linux":
        if is_wsl:
            print("  （WSL2 環境：Google Drive for Desktop 不適用）")
            print("  可透過 /mnt/c/... 存取 Windows 端已同步的 Google Drive 資料夾")
            print("  或使用瀏覽器版 Google Drive：https://drive.google.com")
        else:
            print("  （Linux 環境：Google Drive for Desktop 不適用，請使用瀏覽器版）")
            print("  https://drive.google.com")
    else:
        print("  （不支援的 OS，跳過此項檢查）")


def check_gdrive_folder(os_type: str, is_wsl: bool, repo_root: Path, env_data: dict[str, str]) -> None:
    """檢查 4：Google Drive TeacherOS 資料夾"""
    section("4. Google Drive TeacherOS 資料夾")

    gdrive_email = env_data.get("GOOGLE_DRIVE_EMAIL", "")
    gdrive_folder = env_data.get("GOOGLE_DRIVE_FOLDER", "")
    gdrive_root = env_data.get("GOOGLE_DRIVE_ROOT", "")

    if not gdrive_email or not gdrive_folder:
        return

    # 將反斜線統一轉為正斜線
    gdrive_folder_unix = gdrive_folder.replace("\\", "/")
    gdrive_path: Path | None = None

    if os_type == "macos":
        gdrive_path = (
            Path.home() / "Library" / "CloudStorage"
            / f"GoogleDrive-{gdrive_email}" / "我的雲端硬碟" / gdrive_folder_unix
        )
    elif os_type == "windows":
        if gdrive_root:
            gdrive_path = Path(gdrive_root) / gdrive_folder_unix
        else:
            gdrive_path = repo_root
    elif os_type == "linux":
        if is_wsl and gdrive_root and Path(gdrive_root).is_dir():
            gdrive_path = Path(gdrive_root) / gdrive_folder_unix
        else:
            gdrive_path = None

    if os_type == "linux" and gdrive_path is None:
        print("  （Linux 環境無法自動偵測 Google Drive 資料夾，略過此項）")
        if is_wsl:
            print("  WSL2 使用者可在 environment.env 設定 GOOGLE_DRIVE_ROOT 來啟用此檢查")
        return

    if gdrive_path is not None and gdrive_path.is_dir():
        check_pass(f"TeacherOS 資料夾存在：{gdrive_folder}")
        for class_name in ("class-9c", "class-8a", "class-7a"):
            class_dir = gdrive_path / "projects" / class_name / "english"
            if class_dir.is_dir():
                check_pass(f"  projects/{class_name}/english/ 存在")
            else:
                check_fail(f"  projects/{class_name}/english/ 不存在（請向管理員取得資料夾結構）")
    else:
        check_fail(f"找不到 TeacherOS 資料夾：{gdrive_folder}")
        print()
        print("  請確認：")
        print(f"  1. 你的 Google Drive 內有「{gdrive_folder}」資料夾")
        print("  2. 若無，請向系統管理員申請共用或複製")
        if os_type == "windows":
            print("  3. 請在 environment.env 設定 GOOGLE_DRIVE_ROOT，例如：")
            print("     GOOGLE_DRIVE_ROOT=/h/我的雲端硬碟")


def check_gws(os_type: str) -> None:
    """檢查 5：Google Workspace CLI（gws）— 完全選用"""
    section("5. Google Workspace CLI（gws，完全選用）")

    gws_bin: str | None = None

    if shutil.which("gws"):
        gws_bin = "gws"
    else:
        # 備援路徑：nvm 安裝的 gws（掃描所有 node 版本，避免寫死版號）
        nvm_root = Path.home() / ".nvm" / "versions" / "node"
        if nvm_root.is_dir():
            for version_dir in sorted(nvm_root.iterdir(), reverse=True):
                candidate = version_dir / "bin" / "gws"
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    gws_bin = str(candidate)
                    break

    if gws_bin:
        r = run_cmd([gws_bin, "--version"])
        gws_version = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else "unknown"
        check_pass(f"gws CLI 已安裝：{gws_version}")

        # 檢查是否有加密憑證（表示已完成認證）
        gws_config_dir = Path.home() / ".config" / "gws"
        if gws_config_dir.is_dir():
            enc_files = list(gws_config_dir.glob("credentials.*.enc"))
            if enc_files:
                check_pass("gws 已認證")
                print()
                print("  已認證帳號：")
                for f in enc_files:
                    # 從 credentials.xxx.enc 提取帳號名
                    acct = f.stem.replace("credentials.", "")
                    print(f"    - {acct}")
                print()
                print("  支援服務：Gmail、Drive、Calendar、Sheets、Docs")
                print("  參考文件：ai-core/reference/gws-cli-guide.md")
            else:
                check_info("gws 已安裝，尚未完成 OAuth 認證")
                print()
                print("  若要使用 Drive / Gmail / Calendar 等功能，請執行：")
                print("    gws auth login")
                print("  完整指引：ai-core/reference/gws-cli-guide.md")
        else:
            check_info("gws 已安裝，尚未完成 OAuth 認證")
            print()
            print("  若要使用，請執行：gws auth login")
    else:
        check_info("gws CLI 未安裝（選用功能，不影響備課與課程設計）")
        print()
        print("  gws CLI 讓 AI 直接操作你個人的 Gmail / Drive / Calendar / Sheets / Docs。")
        print("  每位老師獨立建立自己的 GCP 專案與 OAuth 憑證——")
        print("  與 David 的帳號完全分離。")
        print()
        print("  安裝步驟（之後想用再做即可）：")
        if os_type == "macos":
            print("    1a. brew install googleworkspace-cli   ← Mac 推薦")
            print("        （或 npm install -g @googleworkspace/cli）")
            print()
            print("    注意：不要 brew install gws（那是另一個同名工具，會衝突）")
        elif os_type == "windows":
            print("    1. npm install -g @googleworkspace/cli")
            print("       （需要先有 Node.js — https://nodejs.org/）")
        else:
            print("    1. npm install -g @googleworkspace/cli")
        print("    2. 依 ai-core/reference/gws-cli-guide.md 建立你自己的 OAuth client")
        print("    3. gws auth login --account 你的@gmail.com")


def check_git(os_type: str) -> None:
    """檢查 6：Git"""
    section("6. Git（版本控制）")

    if shutil.which("git"):
        r = run_cmd(["git", "--version"])
        check_pass(r.stdout.strip())

        r_user = run_cmd(["git", "config", "--global", "user.name"])
        r_email = run_cmd(["git", "config", "--global", "user.email"])
        git_user = r_user.stdout.strip() if r_user.returncode == 0 else ""
        git_email = r_email.stdout.strip() if r_email.returncode == 0 else ""

        if git_user:
            check_pass(f"Git 使用者：{git_user} <{git_email}>")
        else:
            check_fail("Git 尚未設定使用者資訊")
            print('  請執行：')
            print('  git config --global user.name "你的姓名"')
            print('  git config --global user.email "你的Email"')
    else:
        check_fail("找不到 Git")
        if os_type == "macos":
            print("  請安裝 Git：brew install git")
        elif os_type == "linux":
            print("  請安裝 Git：sudo apt install git")
        elif os_type == "windows":
            print("  請安裝 Git for Windows：https://git-scm.com/download/win")
        else:
            print("  請至 https://git-scm.com 下載安裝 Git")


def check_python() -> None:
    """檢查 7：Python 版本"""
    section("7. Python（腳本執行環境）")

    version = platform.python_version()
    major, minor = sys.version_info[:2]

    if major >= 3 and minor >= 8:
        check_pass(f"Python {version}")
    else:
        check_fail(f"Python {version}（需要 3.8 以上）")


def check_node() -> None:
    """檢查 8：Node.js / npm"""
    section("8. Node.js / npm（gws 相依環境）")

    if shutil.which("node"):
        r = run_cmd(["node", "--version"])
        check_pass(f"Node.js {r.stdout.strip()}")
    else:
        check_fail("找不到 Node.js")
        print("  請至 https://nodejs.org 下載安裝")

    if shutil.which("npm"):
        r = run_cmd(["npm", "--version"])
        check_pass(f"npm {r.stdout.strip()}")
    else:
        check_fail("找不到 npm")


def check_hooks_installed(repo_root: Path) -> None:
    """檢查 9：Git hooks 是否已安裝"""
    section("9. Git Hooks 安裝狀態")

    hooks_dir = repo_root / ".git" / "hooks"

    for hook_name in ("pre-commit", "post-merge"):
        hook_file = hooks_dir / hook_name
        if hook_file.is_file():
            check_pass(f"{hook_name} hook 已安裝")
        else:
            check_fail(f"{hook_name} hook 未安裝（請執行 python3 setup/install-hooks.py）")


def check_branch() -> None:
    """檢查 10：workspace 分支狀態"""
    section("10. 工作分支狀態")

    if not shutil.which("git"):
        check_fail("Git 未安裝，無法檢查分支狀態")
        return

    r = run_cmd(["git", "branch", "--show-current"])
    if r.returncode != 0:
        check_fail("無法取得目前分支")
        return

    current = r.stdout.strip()
    if current.startswith("workspace/"):
        check_pass(f"目前在個人工作分支：{current}")
    elif current == "main":
        check_pass(f"目前在 main 分支")
        print("  （若你是協作教師，請切換到你的 workspace/ 分支）")
    else:
        check_pass(f"目前分支：{current}")


# ──────────────────────────────────────────────────────────
# --help
# ──────────────────────────────────────────────────────────

def show_help() -> None:
    print("用法：python3 setup/setup-check.py [選項]")
    print()
    print("TeacherOS 環境檢查工具")
    print("檢查教師的完整環境設定狀態，輸出格式化的中文報告。")
    print()
    print("選項：")
    print("  --help, -h    顯示本說明")
    print()
    print("檢查項目：")
    print("   1. 個人設定檔（environment.env）")
    print("   2. Pandoc 版本")
    print("   3. Google Drive for Desktop")
    print("   4. Google Drive TeacherOS 資料夾")
    print("   5. Google Workspace CLI（gws）")
    print("   6. Git 版本與設定")
    print("   7. Python 版本")
    print("   8. Node.js / npm 版本")
    print("   9. Git hooks 安裝狀態")
    print("  10. 工作分支狀態")


# ──────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────

def main() -> None:
    global _pass_count, _fail_count

    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)

    _pass_count = 0
    _fail_count = 0

    repo_root = Path(__file__).resolve().parent.parent
    os_type, is_wsl = detect_os()

    # 標題
    print()
    print("════════════════════════════════════════════════")
    if is_wsl:
        print("  TeacherOS 環境檢查（linux / WSL2）")
    else:
        print(f"  TeacherOS 環境檢查（{os_type}）")
    print("════════════════════════════════════════════════")

    # 讀取 environment.env
    env_file = repo_root / "setup" / "environment.env"
    env_data = read_env_file(env_file)

    # 依序執行各項檢查
    check_env_file(repo_root, env_data)
    check_pandoc(os_type, env_data)
    check_google_drive(os_type, is_wsl, env_data)
    check_gdrive_folder(os_type, is_wsl, repo_root, env_data)
    check_gws(os_type)
    check_git(os_type)
    check_python()
    check_node()
    check_hooks_installed(repo_root)
    check_branch()

    # 結果摘要
    print()
    print("════════════════════════════════════════════════")
    print(f"  檢查完成：通過 {_pass_count} 項，需要處理 {_fail_count} 項")
    print("════════════════════════════════════════════════")
    print()

    if _fail_count == 0:
        print("  環境設定完成，可以開始使用 TeacherOS。")
    else:
        print("  請依照上方提示完成設定後，重新執行此腳本確認。")
    print()


if __name__ == "__main__":
    main()
