#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — Hook 一鍵安裝腳本（Python 版）
# 路徑：setup/install-hooks.py
# 使用方式：python3 setup/install-hooks.py
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from __future__ import annotations

import os
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path


# ──────────────────────────────────────────────────────────
# 輔助函式
# ──────────────────────────────────────────────────────────

def _find_repo_root() -> Path:
    """從本檔案位置往上推算 Repo 根目錄。"""
    return Path(__file__).resolve().parent.parent


def _make_executable(path: Path) -> None:
    """在 macOS / Linux 上為檔案加上可執行權限。Windows 跳過。"""
    if platform.system() == "Windows":
        return
    current = path.stat().st_mode
    path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def show_help() -> None:
    print("用法：python3 setup/install-hooks.py [選項]")
    print()
    print("TeacherOS Git Hook 安裝工具")
    print("將 setup/hooks/ 下的 hook 檔案複製到 .git/hooks/ 並設定執行權限。")
    print()
    print("選項：")
    print("  --help, -h    顯示本說明")
    print()
    print("支援的 hooks：")
    print("  - pre-commit   授權檢查（每次 commit 前自動執行）")
    print("  - pre-push     身份 + 路徑驗證（每次 push 前自動執行）")
    print("  - post-merge   新分享通知（每次 pull 後自動執行）")
    print()
    print("此腳本可直接執行，也可被 quick-start.py 匯入使用：")
    print("  from install_hooks import install_hooks")


# ──────────────────────────────────────────────────────────
# 核心安裝邏輯（可供外部 import）
# ──────────────────────────────────────────────────────────

def install_hooks(repo_root: Path | None = None) -> bool:
    """
    安裝 Git hooks。

    Args:
        repo_root: Repo 根目錄。若為 None，自動偵測。

    Returns:
        True 表示所有必要 hooks 安裝成功，False 表示有錯誤。
    """
    if repo_root is None:
        repo_root = _find_repo_root()

    hooks_src_dir = repo_root / "setup" / "hooks"
    hooks_dest_dir = repo_root / ".git" / "hooks"

    # 檢查 .git 目錄是否存在
    if not (repo_root / ".git").is_dir():
        print("[錯誤] 找不到 .git 目錄，請在 TeacherOS 的 Git 資料夾內執行此腳本。")
        return False

    # 確保目標目錄存在
    hooks_dest_dir.mkdir(parents=True, exist_ok=True)

    success = True
    installed: list[str] = []
    skipped: list[str] = []

    # 定義要安裝的 hooks：(名稱, 是否必要)
    hooks_to_install = [
        ("pre-commit", True),
        ("pre-push", True),
        ("post-merge", False),
    ]

    for hook_name, required in hooks_to_install:
        src = hooks_src_dir / hook_name
        dest = hooks_dest_dir / hook_name

        if not src.is_file():
            if required:
                print(f"[錯誤] 找不到 setup/hooks/{hook_name}，請確認 Repo 是否完整。")
                success = False
            else:
                skipped.append(hook_name)
            continue

        # 設定來源檔案可執行權限
        _make_executable(src)

        # 複製到 .git/hooks/
        shutil.copy2(src, dest)

        # 設定目標檔案可執行權限
        _make_executable(dest)

        installed.append(hook_name)

    # ── 設定 core.hooksPath 指向 repo 內的 hooks 目錄 ──────
    # 好處：git pull 時 hook 自動更新，不需重新執行安裝腳本
    # 複製到 .git/hooks/ 仍保留作為 fallback
    try:
        subprocess.run(
            ["git", "config", "core.hooksPath", "setup/hooks"],
            cwd=str(repo_root),
            capture_output=True, text=True, check=True,
        )
        hooks_path_set = True
    except Exception:
        hooks_path_set = False

    # 輸出安裝報告
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  TeacherOS Hook 安裝完成")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    for hook_name in installed:
        print(f"  {hook_name} hook 已安裝至：.git/hooks/{hook_name}")

    for hook_name in skipped:
        print(f"  [略過] 找不到 setup/hooks/{hook_name}")

    if hooks_path_set:
        print()
        print("  core.hooksPath 已設定為 setup/hooks/")
        print("  往後 git pull 時 hook 會自動更新，無需重新安裝。")
    else:
        print()
        print("  [注意] core.hooksPath 設定失敗，hook 仍從 .git/hooks/ 執行。")

    print()
    print("  往後每次執行 git commit，系統將自動：")
    print("    1. 確認你的身份（USER_EMAIL）")
    print("    2. 比對 ai-core/acl.yaml 的授權範圍")
    print("    3. 攔截超出授權的檔案修改")
    print()
    print("  每次 git pull 時，若 Good-notes/ 有新分享，")
    print("  系統會顯示分享者姓名與檔案清單。")
    print()
    print("  如有任何問題，請聯絡 David。")
    print()

    return success


# ──────────────────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────────────────

def main() -> None:
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)

    ok = install_hooks()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
