#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — 一鍵技術安裝腳本（Python 版）
# 路徑：setup/quick-start.py
# 用途：新教師快速安裝 TeacherOS 開發環境
# 使用方式：python3 setup/quick-start.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from __future__ import annotations

import os
import sys
import shutil
import subprocess
import platform
import re
import stat
import webbrowser
from pathlib import Path

# ──────────────────────────────────────────────────────────
# 顏色與符號設定
# ──────────────────────────────────────────────────────────

# Windows cmd 預設不支援 ANSI，偵測後決定是否啟用顏色
_USE_COLOR = True
if platform.system() == "Windows":
    # Windows 10+ 的新版 terminal 支援 ANSI；舊版則關閉
    try:
        os.system("")  # 啟用 Windows ANSI 支援
    except Exception:
        _USE_COLOR = False

if _USE_COLOR and os.environ.get("NO_COLOR"):
    _USE_COLOR = False


def _c(code: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{code}{text}\033[0m"


GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"

CHECK = "✓"
WARN = "⚠"
ERROR = "✗"
INFO = "ℹ"


# ──────────────────────────────────────────────────────────
# 輔助函式
# ──────────────────────────────────────────────────────────


def print_banner():
    print()
    print(_c(BLUE, "╔═══════════════════════════════════════════════════════╗"))
    print(_c(BLUE, "║") + "  TeacherOS 技術安裝精靈                             " + _c(BLUE, "║"))
    print(_c(BLUE, "║") + "  一鍵設定你的教學工作環境                           " + _c(BLUE, "║"))
    print(_c(BLUE, "║") + "  ──────────────────────────────────────           " + _c(BLUE, "║"))
    print(_c(BLUE, "║") + "  歡迎使用華德福課程設計系統                         " + _c(BLUE, "║"))
    print(_c(BLUE, "║") + "  The Teacher's Consciousness Operating System       " + _c(BLUE, "║"))
    print(_c(BLUE, "╚═══════════════════════════════════════════════════════╝"))
    print()


def print_section(title: str):
    print()
    print(_c(BLUE, "──────────────────────────────────────────────────────"))
    print(_c(BLUE, title))
    print(_c(BLUE, "──────────────────────────────────────────────────────"))


def print_success(msg: str):
    print(_c(GREEN, f"{CHECK} {msg}"))


def print_warning(msg: str):
    print(_c(YELLOW, f"{WARN} {msg}"))


def print_error(msg: str):
    print(_c(RED, f"{ERROR} {msg}"))


def print_info(msg: str):
    print(_c(BLUE, f"{INFO} {msg}"))


def run_cmd(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """執行外部指令，回傳 CompletedProcess。"""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def _extract_github_username(email: str) -> str | None:
    """從 GitHub noreply email 提取 username。
    現代格式: 12345+username@users.noreply.github.com
    舊格式: username@users.noreply.github.com
    """
    if not email or "noreply.github.com" not in email:
        return None
    m = re.match(r"\d+\+(.+)@users\.noreply\.github\.com$", email)
    if m:
        return m.group(1)
    m = re.match(r"(.+)@users\.noreply\.github\.com$", email)
    if m:
        return m.group(1)
    return None


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


def show_help():
    print("用法：python3 setup/quick-start.py [選項]")
    print()
    print("TeacherOS 一鍵技術安裝精靈")
    print("為新教師快速設定教學工作環境。")
    print()
    print("選項：")
    print("  --help, -h    顯示本說明")
    print()
    print("此腳本將依序檢查並設定：")
    print("  1. Git 安裝狀態")
    print("  2. TeacherOS Repo 完整性")
    print("  3. Homebrew（僅 macOS）")
    print("  4. Pandoc 安裝狀態")
    print("  5. Git Pre-commit Hook")
    print("  6. 個人環境設定檔（environment.env）")
    print("  6.5 Git 身份強制匹配（user.email = USER_EMAIL）")
    print("  7. 詳細環境檢查（setup-check.py）")
    print("  8. 切換到個人工作分支")
    print("  9. Claude Code Hook 設定")


# ──────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)

    os_name = platform.system()  # 'Darwin', 'Linux', 'Windows'

    print_banner()

    # 確認 Repo 根目錄
    repo_root = Path(__file__).resolve().parent.parent
    print_info(f"Repo 根目錄：{repo_root}")

    # ──────────────────────────────────────────────────────
    # 檢查 1：Git 安裝
    # ──────────────────────────────────────────────────────

    print_section("檢查 1：Git 安裝狀態（版本控制的鑰匙）")

    if shutil.which("git"):
        r = run_cmd(["git", "--version"])
        print_success(f"Git 已安裝：{r.stdout.strip()}")
    else:
        print_error("Git 尚未安裝")
        print()
        print(_c(YELLOW, "請按照以下步驟安裝 Git："))
        print()
        print("macOS 使用者：")
        print("  brew install git")
        print()
        print("Ubuntu/Debian 使用者：")
        print("  sudo apt-get update")
        print("  sudo apt-get install git")
        print()
        print("Windows 使用者：")
        print("  前往 https://git-scm.com 下載 Git for Windows")
        print()
        sys.exit(1)

    # ──────────────────────────────────────────────────────
    # 檢查 2：Repo 已複製
    # ──────────────────────────────────────────────────────

    print_section("檢查 2：TeacherOS Repo 狀態（已複製校驗）")

    if (repo_root / "ai-core" / "teacheros.yaml").is_file():
        print_success("TeacherOS Repo 已完整複製")
    else:
        print_error("找不到 ai-core/teacheros.yaml，Repo 可能不完整")
        print()
        print(_c(YELLOW, "請確認您已執行："))
        print("  git clone https://github.com/elliot200852-lab/WaldorfTeacherOS-Repo.git")
        sys.exit(1)

    # ──────────────────────────────────────────────────────
    # 檢查 3：Homebrew（macOS 特定）
    # ──────────────────────────────────────────────────────

    print_section("檢查 3：Homebrew 安裝狀態（macOS 套件管理器）")

    if os_name == "Darwin":
        if shutil.which("brew"):
            r = run_cmd(["brew", "--version"])
            brew_ver = r.stdout.strip().splitlines()[0] if r.stdout else "已安裝"
            print_success(f"Homebrew 已安裝：{brew_ver}")
        else:
            print_warning("Homebrew 尚未安裝（僅 macOS 需要）")
            print()
            print(_c(YELLOW, "若需要自動安裝 Pandoc 等工具，請安裝 Homebrew："))
            print('  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            print()
    else:
        print_info("您不在 macOS 系統上，Homebrew 檢查略過")

    # ──────────────────────────────────────────────────────
    # 檢查 4：Pandoc 安裝
    # ──────────────────────────────────────────────────────

    print_section("檢查 4：Pandoc 安裝狀態（Markdown 轉換工具）")

    if shutil.which("pandoc"):
        r = run_cmd(["pandoc", "--version"])
        pandoc_ver = r.stdout.strip().splitlines()[0] if r.stdout else "已安裝"
        print_success(f"Pandoc 已安裝：{pandoc_ver}")
    else:
        print_warning("Pandoc 尚未安裝")
        print()
        print(_c(YELLOW, "建議安裝 Pandoc（用於 Markdown → Word 轉換）："))
        print()
        if os_name == "Darwin":
            print("macOS 使用者：")
            print("  brew install pandoc")
        elif os_name == "Windows":
            print("Windows 使用者：")
            print("  前往 https://pandoc.org/installing.html 下載安裝")
        else:
            print("Ubuntu/Debian 使用者：")
            print("  sudo apt-get install pandoc")
        print()

    # ──────────────────────────────────────────────────────
    # 檢查 5：安裝 Git Pre-commit Hook（門鎖）
    # ──────────────────────────────────────────────────────

    print_section("檢查 5：安裝 Git Pre-commit Hook（授權檢查的門鎖）")

    # 優先使用 Python 版 install-hooks；若匯入失敗則 fallback 到 shell 版
    install_hooks_ok = False
    install_hooks_py = repo_root / "setup" / "install-hooks.py"

    if install_hooks_py.is_file():
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("install_hooks", str(install_hooks_py))
            mod = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(mod)  # type: ignore
            print_info("開始安裝 Git Hooks...")
            install_hooks_ok = mod.install_hooks(repo_root)
            if install_hooks_ok:
                print_success("Git Hooks 安裝完成")
            else:
                print_error("Git Hooks 安裝失敗")
        except Exception as e:
            print_error(f"install-hooks.py 執行失敗：{e}")
    else:
        # Fallback: 使用 shell 版
        install_hooks_sh = repo_root / "setup" / "install-hooks.sh"
        if install_hooks_sh.is_file():
            print_info("開始安裝 Pre-commit Hook（shell 備援）...")
            r = run_cmd(["bash", str(install_hooks_sh)])
            if r.returncode == 0:
                print_success("Pre-commit Hook 安裝完成")
            else:
                print_error("Pre-commit Hook 安裝失敗")
                print(f"請手動執行：bash {install_hooks_sh}")
        else:
            print_warning("找不到 install-hooks.py 或 install-hooks.sh，跳過 Hook 安裝")

    # ──────────────────────────────────────────────────────
    # 檢查 6：個人環境設定檔（鑰匙）
    # ──────────────────────────────────────────────────────

    print_section("檢查 6：個人環境設定檔（你的工作鑰匙）")

    env_file = repo_root / "setup" / "environment.env"
    env_example = repo_root / "setup" / "environment.env.example"

    if env_file.is_file():
        print_success("environment.env 已存在")
        env_content = env_file.read_text(encoding="utf-8")
        if "USER_NAME=你的姓名" in env_content:
            print_warning("environment.env 仍含有預設佔位符，請編輯檔案並填入真實資訊")
        else:
            print_info("environment.env 已初步配置")
    else:
        # 嘗試自動偵測：從 workspace 的 env-preset.env 比對 git config user.email
        r = run_cmd(["git", "config", "user.email"])
        git_email = r.stdout.strip() if r.returncode == 0 else ""
        preset_found: Path | None = None

        if git_email:
            preset_dir = repo_root / "workspaces" / "Working_Member"
            if preset_dir.is_dir():
                # 第一輪：精確 email 比對
                for preset_path in preset_dir.glob("*/env-preset.env"):
                    preset_env = read_env_file(preset_path)
                    if preset_env.get("USER_EMAIL", "").lower() == git_email.lower():
                        preset_found = preset_path
                        break

                # 第二輪：GitHub noreply → username 比對
                if not preset_found:
                    gh_user = _extract_github_username(git_email)
                    if gh_user:
                        for preset_path in preset_dir.glob("*/env-preset.env"):
                            preset_env = read_env_file(preset_path)
                            if preset_env.get("GITHUB_USERNAME", "").lower() == gh_user.lower():
                                preset_found = preset_path
                                print_info(f"透過 GitHub noreply 匹配到帳號：{gh_user}")
                                break

        if preset_found is not None:
            preset_env = read_env_file(preset_found)
            preset_name = preset_env.get("USER_NAME", "")
            print_info(f"偵測到你的預填設定（{preset_name}），自動建立 environment.env...")
            shutil.copy2(preset_found, env_file)
            print_success("environment.env 已自動建立（必填欄位已預填）")
            print()
            print(_c(GREEN, "以下欄位已自動設定："))
            print("  USER_NAME、USER_EMAIL、WORKSPACE_ID、GITHUB_USERNAME")
            print()
            print(_c(YELLOW, "選填欄位（Google Drive、Pandoc 等）可之後再補充。"))
            print()
        elif env_example.is_file():
            print_info("複製 environment.env.example → environment.env...")
            shutil.copy2(env_example, env_file)
            print_success("environment.env 已建立")
            print()
            print(_c(YELLOW, "請用文字編輯器打開 setup/environment.env，填入你的個人資訊："))
            print("  - USER_NAME：你的姓名")
            print("  - USER_EMAIL：你的 Email（必須與 GitHub 帳號相符）")
            print("  - GOOGLE_DRIVE_EMAIL：你的 Google Drive 帳號")
            print("  - GITHUB_USERNAME：你的 GitHub 帳號")
            print()
        else:
            print_error("找不到 environment.env.example")

    # ──────────────────────────────────────────────────────
    # 檢查 6.5：強制 Git Identity 與 environment.env 一致
    # ──────────────────────────────────────────────────────

    print_section("檢查 6.5：Git 身份與註冊 Email 一致性")

    EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    PLACEHOLDER_NAMES = {"你的姓名", "Your Name", "your name"}

    if env_file.is_file():
        env_data = read_env_file(env_file)
        reg_email = env_data.get("USER_EMAIL", "").strip()
        reg_name = env_data.get("USER_NAME", "").strip()

        if reg_email and EMAIL_RE.match(reg_email):
            r = run_cmd(["git", "config", "user.email"])
            current_git_email = r.stdout.strip() if r.returncode == 0 else ""

            if current_git_email != reg_email:
                run_cmd(["git", "config", "user.email", reg_email])
                print_success(f"git config user.email 已更新為：{reg_email}")
                if current_git_email:
                    print_info(f"（原值：{current_git_email}）")
            else:
                print_success(f"git config user.email 已正確：{reg_email}")
        elif reg_email:
            print_warning(f"environment.env 的 USER_EMAIL 不是有效格式：{reg_email}")
            print_info("請編輯 setup/environment.env，把 USER_EMAIL 填成你真正的 Email，再重新執行此腳本")
        else:
            print_warning("environment.env 缺少 USER_EMAIL，無法同步 Git 身份")

        if reg_name and reg_name not in PLACEHOLDER_NAMES:
            r = run_cmd(["git", "config", "user.name"])
            current_git_name = r.stdout.strip() if r.returncode == 0 else ""

            if current_git_name != reg_name:
                run_cmd(["git", "config", "user.name", reg_name])
                print_success(f"git config user.name 已更新為：{reg_name}")
                if current_git_name:
                    print_info(f"（原值：{current_git_name}）")
            else:
                print_success(f"git config user.name 已正確：{reg_name}")
        elif reg_name in PLACEHOLDER_NAMES:
            print_warning(f"environment.env 的 USER_NAME 仍為預設佔位符：{reg_name}")
            print_info("請編輯 setup/environment.env 填入真實姓名，再重新執行此腳本")
    else:
        print_warning("environment.env 尚未建立，無法同步 Git 身份")
        print_info("請先完成 Step 6，再重新執行本腳本")

    # ──────────────────────────────────────────────────────
    # 檢查 7：執行 setup-check.sh
    # ──────────────────────────────────────────────────────

    print_section("檢查 7：詳細環境檢查")

    setup_check_py = repo_root / "setup" / "setup-check.py"
    setup_check_sh = repo_root / "setup" / "setup-check.sh"

    if setup_check_py.is_file():
        print_info("執行詳細環境檢查...")
        print()
        r = run_cmd([sys.executable, str(setup_check_py)])
        if r.stdout:
            print(r.stdout, end="")
        if r.returncode == 0:
            print_success("所有環境檢查完成")
        else:
            print_warning("部分環境檢查未通過，但不影響基本功能")
    elif setup_check_sh.is_file():
        print_info("執行詳細環境檢查（shell 備援）...")
        print()
        r = run_cmd(["bash", str(setup_check_sh)])
        if r.stdout:
            print(r.stdout, end="")
        if r.returncode == 0:
            print_success("所有環境檢查完成")
        else:
            print_warning("部分環境檢查未通過，但不影響基本功能")
    else:
        print_warning("找不到 setup-check.py 或 setup-check.sh，跳過詳細檢查")

    # ──────────────────────────────────────────────────────
    # 檢查 8：切換到個人 Branch
    # ──────────────────────────────────────────────────────

    print_section("檢查 8：個人工作分支狀態")

    # 先看當前分支：若已在 workspace/* 上，直接成功
    r = run_cmd(["git", "branch", "--show-current"])
    current_branch = r.stdout.strip() if r.returncode == 0 else ""

    if current_branch.startswith("workspace/"):
        print_success(f"已在你的個人分支：{current_branch}")
    else:
        # 不在 workspace 分支上 — 列出可用分支讓老師自行切換
        print_warning(f"目前在 '{current_branch or '未知'}' 分支，不是個人 workspace 分支")
        print()

        run_cmd(["git", "fetch", "--all", "--quiet"])
        r = run_cmd(["git", "branch", "-r"])
        workspace_branches: list[str] = []
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                line = line.strip()
                if "origin/workspace/" in line:
                    branch = line.replace("origin/", "").strip()
                    workspace_branches.append(branch)

        if workspace_branches:
            print_info("可用的 workspace 分支：")
            for b in workspace_branches:
                print(f"  - {b}")
            print()
            print(_c(YELLOW, "請手動切換到你自己的分支（範例，把姓名換成你自己的）："))
            print("  git checkout workspace/Teacher_你的姓名")
        else:
            print_info("尚未找到任何 workspace 分支")
            print_info("請聯繫 David，等他建立後再執行 git pull")

    # ──────────────────────────────────────────────────────
    # 檢查 9：Claude Code Hook 設定（選用）
    # ──────────────────────────────────────────────────────

    print_section("檢查 9：Claude Code Hook 設定（選用）")

    claude_settings = repo_root / ".claude" / "settings.local.json"
    claude_scripts = repo_root / ".claude" / "scripts"

    if claude_settings.is_file():
        settings_content = claude_settings.read_text(encoding="utf-8")
        if "session-init.py" in settings_content:
            print_success("Claude Code Hook 已設定")
        else:
            print_info("settings.local.json 已存在但未包含 Hook，跳過自動寫入")
            print_info("如需手動設定，請參考 setup/teacher-guide.md")
    else:
        session_init = claude_scripts / "session-init.py"
        if session_init.is_file():
            claude_settings.parent.mkdir(parents=True, exist_ok=True)
            hook_json = """\
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/scripts/session-init.py"
          }
        ]
      }
    ]
  }
}
"""
            claude_settings.write_text(hook_json, encoding="utf-8")
            print_success("Claude Code Hook 已自動設定")
            print_info("每次使用 Claude Code 時，會自動顯示你的班級工作狀態")
        else:
            print_warning("找不到 .claude/scripts/session-init.py，跳過 Hook 設定")

    print_info("不使用 Claude Code？此步驟不影響任何其他 AI 工具")

    # ──────────────────────────────────────────────────────
    # 完成提示
    # ──────────────────────────────────────────────────────

    print()
    print(_c(GREEN, "╔═══════════════════════════════════════════════════════╗"))
    print(_c(GREEN, "║") + "  技術安裝完成！                                   " + _c(GREEN, "║"))
    print(_c(GREEN, "╚═══════════════════════════════════════════════════════╝"))
    print()

    # 檢查是否已在 workspace branch 上
    r = run_cmd(["git", "branch", "--show-current"])
    current_branch = r.stdout.strip() if r.returncode == 0 else ""

    if current_branch.startswith("workspace/"):
        print_success(f"你已在個人分支上：{current_branch}")
        print_info("可以開始使用 TeacherOS 了！")
    else:
        print_info("下一步：請聯繫 David（elliot200852@gmail.com）取得你的工作空間。")
        print_info("David 設定完成後，執行 git pull 再重新執行本腳本即可。")
    print()


if __name__ == "__main__":
    main()
