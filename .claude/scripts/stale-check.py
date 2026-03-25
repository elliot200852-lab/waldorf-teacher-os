#!/usr/bin/env python3
"""
TeacherOS Stale Check — UserPromptSubmit Hook #2
觸發時機：每次使用者送出訊息時（排在 session-init.py 之後）
功能：
  - Session 首次：偵測跨 session 堆積的未 commit 檔案 + obsidian 狀態
  - 後續：只在大量未 commit 時簡短提醒
輸出規則：無問題 → 無輸出；有問題 → 簡短中文提醒
不依賴外部套件，只使用 Python 標準函式庫
"""

import os
import subprocess
import time
import datetime

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SESSION_MARKER = os.path.join(REPO_ROOT, ".claude", ".session-marker")
OBSIDIAN_SCRIPT = os.path.join(REPO_ROOT, "setup", "scripts", "obsidian-check.py")


def is_first_prompt():
    """判斷是否為本 session 的首次 prompt
    macOS/Linux：用 parent PID（os.getppid()）判斷
    Windows：os.getppid() 不存在，改用 os.getpid() 作為 fallback
    """
    if hasattr(os, "getppid"):
        current_id = str(os.getppid())
    else:
        # Windows fallback：用 PID（每次 Claude Code session 啟動都不同）
        current_id = str(os.getpid())

    stored_id = None
    try:
        with open(SESSION_MARKER, "r") as f:
            stored_id = f.read().strip()
    except FileNotFoundError:
        pass

    if stored_id == current_id:
        return False

    # 新 session：寫入新 ID
    os.makedirs(os.path.dirname(SESSION_MARKER), exist_ok=True)
    with open(SESSION_MARKER, "w") as f:
        f.write(current_id)
    return True


def git_uncommitted_files():
    """回傳未 commit 的檔案列表"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_ROOT
        )
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        return lines
    except Exception:
        return []


def oldest_modified_days(files):
    """計算未 commit 檔案中最舊的修改距今天數"""
    oldest = time.time()
    for line in files:
        # git status --porcelain 格式：XY filename
        filepath = line[3:].strip().strip('"')
        # 處理 renamed: old -> new
        if " -> " in filepath:
            filepath = filepath.split(" -> ")[-1]
        full_path = os.path.join(REPO_ROOT, filepath)
        try:
            mtime = os.path.getmtime(full_path)
            if mtime < oldest:
                oldest = mtime
        except OSError:
            continue

    if oldest == time.time():
        return 0
    return (datetime.date.today() - datetime.date.fromtimestamp(oldest)).days


def run_obsidian_count():
    """執行 obsidian-check.py --count-only，回傳輸出"""
    if not os.path.exists(OBSIDIAN_SCRIPT):
        return None
    try:
        result = subprocess.run(
            ["python3", OBSIDIAN_SCRIPT, "--count-only"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_ROOT
        )
        output = result.stdout.strip()
        if output:
            return output
    except Exception:
        pass
    return None


# ── Main ─────────────────────────────────────────────────
first_prompt = is_first_prompt()
files = git_uncommitted_files()
count = len(files)

output_lines = []

if first_prompt and count > 0:
    days = oldest_modified_days(files)
    if days > 0:
        output_lines.append(
            f"[stale-check] {count} 個檔案未 commit（最舊：{days} 天前）"
        )
    else:
        output_lines.append(f"[stale-check] {count} 個檔案未 commit")

    # 首次 prompt：執行 obsidian-check
    obsidian_output = run_obsidian_count()
    if obsidian_output:
        # 解析 obsidian-check --count-only 的格式
        # 預期：UNLABELED_MD:N / UNLABELED_YAML:N / NOT_IN_HOME:N
        parts = []
        for line in obsidian_output.split("\n"):
            line = line.strip()
            if line.startswith("UNLABELED_MD:"):
                n = line.split(":")[1]
                if n != "0":
                    parts.append(f"{n} 個 .md 未標籤")
            elif line.startswith("NOT_IN_HOME:"):
                n = line.split(":")[1]
                if n != "0":
                    parts.append(f"{n} 個未收錄 HOME.md")
        if parts:
            output_lines.append(f"[stale-check] obsidian: {', '.join(parts)}")

    if output_lines:
        output_lines.append("建議先 commit 再開始新工作，或執行收工（wrap-up）。")

elif not first_prompt and count > 5:
    # 後續 prompt：只在大量未 commit 時提醒
    output_lines.append(f"[stale-check] {count} 個檔案未 commit")

# 輸出
if output_lines:
    print("\n".join(output_lines))
