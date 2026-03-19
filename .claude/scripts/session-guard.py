#!/usr/bin/env python3
"""
TeacherOS Session Guard — Stop Hook
觸發時機：每次 AI 回應完成時（Stop event）
功能：檢查是否有未完成的收工步驟，提醒 AI 建議教師執行 wrap-up
輸出規則：全部乾淨 → 無輸出；有問題 → 簡短中文提醒
不依賴外部套件，只使用 Python 標準函式庫
"""

import os
import subprocess
import datetime

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

OBSIDIAN_MARKER = os.path.join(REPO_ROOT, ".claude", ".last-obsidian-check")
HOME_MD = os.path.join(REPO_ROOT, "HOME.md")


def git_uncommitted_count():
    """回傳未 commit 的檔案數量"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_ROOT
        )
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        return len(lines)
    except Exception:
        return 0


def obsidian_checked_this_session():
    """檢查本 session 是否已執行過 obsidian-check"""
    if not os.path.exists(OBSIDIAN_MARKER):
        return False
    # marker 存在且是今天建立的
    mtime = datetime.date.fromtimestamp(os.path.getmtime(OBSIDIAN_MARKER))
    return mtime == datetime.date.today()


def home_md_days_since_commit():
    """HOME.md 距離上次 commit 的天數"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", "HOME.md"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_ROOT
        )
        date_str = result.stdout.strip()
        if not date_str:
            return 999  # 從未 commit 過
        last_commit = datetime.date.fromisoformat(date_str)
        return (datetime.date.today() - last_commit).days
    except Exception:
        return 0  # 無法判斷時不報警


# ── Main ─────────────────────────────────────────────────
issues = []

uncommitted = git_uncommitted_count()
if uncommitted > 0:
    issues.append(f"{uncommitted} 個檔案未 commit")

if not obsidian_checked_this_session():
    issues.append("obsidian-check 本次 session 未執行")

home_days = home_md_days_since_commit()
if home_days >= 3:
    issues.append(f"HOME.md 上次更新：{home_days} 天前")

# 只在有問題時輸出，乾淨時完全靜默
if issues:
    print("[session-guard] 收工提醒：")
    for item in issues:
        print(f"  - {item}")
    print("建議執行收工（wrap-up）再結束。")
