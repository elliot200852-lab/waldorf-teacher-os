#!/usr/bin/env python3
"""
TeacherOS Session Init Hook
觸發時機：每次使用者送出訊息（UserPromptSubmit）
輸出：
  1. AI_HANDOFF.md 入口提示（確保任何 AI 都知道入口文件位置）
  2. 當前使用者 workspace 內所有班級的工作狀態
不依賴外部套件，只使用 Python 標準函式庫
"""

import re
import os

# ── 路徑設定 ──────────────────────────────────────────────
# 從腳本位置推算 Repo 根目錄（.claude/scripts/ → 上兩層）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
ENV_PATH = os.path.join(REPO_ROOT, "setup", "environment.env")
HANDOFF_REL = "ai-core/AI_HANDOFF.md"

# ── 科目名稱對照 ─────────────────────────────────────────
# 資料夾名稱 → 顯示名稱（未列出的資料夾以原名顯示）
SUBJECT_LABELS = {
    "english": "英文",
    "homeroom": "導師",
    "main-lesson": "主課程",
    "ml-taiwan-literature": "主課程（台灣文學）",
    "ml-undecided": "主課程（待定）",
}
# 掃描時忽略的資料夾（不含 session.yaml 的輔助資料夾）
SKIP_DIRS = {"content", "reference", "working"}


def read_env(path):
    """讀取 environment.env，回傳 dict"""
    env = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env


def extract_field(text, key):
    """從 YAML 文字中提取單一欄位值，處理 null、空值與行內註解"""
    pattern = rf"^\s*{re.escape(key)}:\s*(.*)$"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    raw = match.group(1).strip()
    val = re.sub(r"\s*#.*$", "", raw).strip()
    if val in ("null", "~", "''", '""', ""):
        return None
    # 移除包圍引號
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
        val = val[1:-1]
    return val


def format_position(path):
    """讀取 session YAML，回傳人類可讀的位置摘要"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None
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


def scan_workspace(workspace_path):
    """掃描 workspace 內所有班級的 session 檔案，回傳狀態列表
    規則：每個 class-* 下的一層子資料夾中找 session.yaml
    例如 class-9c/english/session.yaml、class-9c/homeroom/session.yaml
    """
    results = []
    projects_path = os.path.join(workspace_path, "projects")
    if not os.path.isdir(projects_path):
        return results

    for class_dir in sorted(os.listdir(projects_path)):
        if not class_dir.startswith("class-"):
            continue
        class_path = os.path.join(projects_path, class_dir)
        if not os.path.isdir(class_path):
            continue

        label = class_dir.replace("class-", "").upper()

        # 掃描 class-* 下所有一層子資料夾的 session.yaml
        for sub_dir in sorted(os.listdir(class_path)):
            if sub_dir.startswith(".") or sub_dir in SKIP_DIRS:
                continue
            sub_path = os.path.join(class_path, sub_dir)
            if not os.path.isdir(sub_path):
                continue
            session_path = os.path.join(sub_path, "session.yaml")
            position = format_position(session_path)
            if position:
                subject_label = SUBJECT_LABELS.get(sub_dir, sub_dir)
                results.append(f"{label} {subject_label}：{position}")

    return results


# ── Main ─────────────────────────────────────────────────
env = read_env(ENV_PATH)
workspace_id = env.get("WORKSPACE_ID", "")

lines = [f"[TeacherOS] 入口：{HANDOFF_REL}"]

if workspace_id:
    workspace_path = os.path.join(
        REPO_ROOT, "workspaces", "Working_Member", workspace_id
    )
    statuses = scan_workspace(workspace_path)
    if statuses:
        for s in statuses:
            lines.append(s)
    else:
        lines.append("（workspace 內無進行中的工作線）")
else:
    lines.append("（未設定 WORKSPACE_ID，請在 setup/environment.env 中填入）")

print("\n".join(lines))
