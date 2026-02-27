#!/usr/bin/env python3
"""
TeacherOS Session Init Hook
觸發時機：每次使用者送出訊息（UserPromptSubmit）
輸出：注入三個班的當前英文課位置狀態，作為 Claude 的環境背景
不依賴外部套件，只使用 Python 標準函式庫
"""

import re
import os

REPO_ROOT = "/Users/Dave/Desktop/WaldorfTeacherOS-Repo"
CLASSES = ["class-9c", "class-8a", "class-7a"]

def extract_field(text, key):
    """從 YAML 文字中提取單一欄位值，處理 null、空值與行內註解"""
    pattern = rf"^\s*{re.escape(key)}:\s*(.*)$"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    raw = match.group(1).strip()
    # 移除行內 YAML 註解（# 之後的內容）
    val = re.sub(r"\s*#.*$", "", raw).strip()
    if val in ("null", "~", "''", '""', ""):
        return None
    return val

def format_position(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return "（檔案不存在）"
    except Exception:
        return "（讀取失敗）"

    block = extract_field(text, "block")
    step = extract_field(text, "step")
    desc = extract_field(text, "description")

    if not block:
        return "尚未開始"

    result = f"區塊{block}"
    if step:
        result += f" Step {step}"
    if desc:
        result += f" → {desc}"
    return result

lines = ["[TeacherOS 狀態]"]
for cls in CLASSES:
    label = cls.replace("class-", "").upper()
    session_path = os.path.join(REPO_ROOT, "projects", cls, "working", "english-session.yaml")
    position = format_position(session_path)
    lines.append(f"{label} 英文：{position}")

print("\n".join(lines))
