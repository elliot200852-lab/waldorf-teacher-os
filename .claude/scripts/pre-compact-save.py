#!/usr/bin/env python3
"""
TeacherOS PreCompact Hook — Context 壓縮前自動備份關鍵脈絡
觸發時機：Claude Code context 壓縮（compact）發生前
功能：
  1. 從 teacheros-personal.yaml 提取 voice_anchor 段落
  2. 從所有進行中的 session.yaml 提取 current_position + next_action
  3. 寫入 .claude/.pre-compact-state.md 供壓縮後 AI 重讀
輸出：簡短提醒 AI 壓縮後重讀該檔案
不依賴外部套件，只使用 Python 標準函式庫
"""

import os
import re
import datetime

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
ENV_PATH = os.path.join(REPO_ROOT, "setup", "environment.env")
OUTPUT_PATH = os.path.join(REPO_ROOT, ".claude", ".pre-compact-state.md")

# 科目顯示名稱
SUBJECT_LABELS = {
    "english": "英文",
    "homeroom": "導師",
    "main-lesson": "主課程",
    "ml-taiwan-literature": "主課程（台灣文學）",
    "walking-reading-taiwan": "走讀臺灣",
    "farm-internship": "農場實習",
}
SKIP_DIRS = {"content", "reference", "working"}


def read_env(path):
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


def extract_yaml_block(text, block_key):
    """提取 YAML 中某個 key 的整個子區塊（到下一個同層 key 結束）"""
    pattern = rf"^({re.escape(block_key)}:.*?)(?=^\S|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_field(text, key):
    """從 YAML 文字中提取單一欄位值"""
    pattern = rf"^\s*{re.escape(key)}:\s*(.*)$"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    raw = match.group(1).strip()
    val = re.sub(r"\s*#.*$", "", raw).strip()
    if val in ("null", "~", "''", '""', ""):
        return None
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
        val = val[1:-1]
    return val


def extract_multiline_field(text, key):
    """提取 YAML 中 key: > 格式的多行文字"""
    pattern = rf"^\s*{re.escape(key)}:\s*>\s*\n((?:\s+.+\n?)+)"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        lines = match.group(1).strip().split("\n")
        return " ".join(line.strip() for line in lines)
    # 嘗試單行
    return extract_field(text, key)


def extract_yaml_scalar(text, key):
    """提取 YAML key: > 多行值，到下一個同層 key 為止"""
    # 找到 key: > 或 key: "value"
    pattern = rf"^\s+{re.escape(key)}:\s*>\s*\n((?:\s{{4,}}.+\n?)+)"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        lines = match.group(1).strip().split("\n")
        return " ".join(line.strip() for line in lines)
    # 嘗試單行
    pattern2 = rf"^\s+{re.escape(key)}:\s*(.+)$"
    match2 = re.search(pattern2, text, re.MULTILINE)
    if match2:
        val = match2.group(1).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        return val
    return None


def get_voice_anchor(workspace_path):
    """從 teacheros-personal.yaml 提取 voice_anchor 段落"""
    personal_path = os.path.join(workspace_path, "teacheros-personal.yaml")
    try:
        with open(personal_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None

    # 找到 voice_anchor: 區塊的範圍
    va_match = re.search(r"^voice_anchor:\s*$", text, re.MULTILINE)
    if not va_match:
        return None
    va_start = va_match.end()
    # 找到下一個頂層 key（非縮排的 key:）
    next_key = re.search(r"^\S+:", text[va_start:], re.MULTILINE)
    va_end = va_start + next_key.start() if next_key else len(text)
    va_block = text[va_start:va_end]

    parts = []
    for sub_key in ["who_i_am", "my_tone", "my_students", "design_check"]:
        val = extract_yaml_scalar(va_block, sub_key)
        if val:
            parts.append(f"- **{sub_key}**: {val}")
    return "\n".join(parts) if parts else None


def scan_sessions(workspace_path):
    """掃描所有進行中的 session.yaml，提取位置與下一步"""
    results = []
    projects_path = os.path.join(workspace_path, "projects")
    if not os.path.isdir(projects_path):
        return results

    for project_dir in sorted(os.listdir(projects_path)):
        if project_dir.startswith("_") or project_dir.startswith("."):
            continue
        project_path = os.path.join(projects_path, project_dir)
        if not os.path.isdir(project_path):
            continue

        if project_dir.startswith("class-"):
            # 班級目錄：掃描子資料夾
            label = project_dir.replace("class-", "").upper()
            for sub_dir in sorted(os.listdir(project_path)):
                if sub_dir.startswith(".") or sub_dir in SKIP_DIRS:
                    continue
                sub_path = os.path.join(project_path, sub_dir)
                if not os.path.isdir(sub_path):
                    continue
                session_path = os.path.join(sub_path, "session.yaml")
                entry = format_session(session_path, label, sub_dir)
                if entry:
                    results.append(entry)
        else:
            # 獨立專案
            session_path = os.path.join(project_path, "session.yaml")
            entry = format_session(session_path, project_dir, None)
            if entry:
                results.append(entry)

    return results


def extract_next_action_desc(text):
    """從 session.yaml 提取 next_action.description 的第一行（精簡摘要）"""
    # 找到 next_action: 區塊
    na_match = re.search(r"^\s*next_action:\s*$", text, re.MULTILINE)
    if not na_match:
        return None
    na_start = na_match.end()
    # 在 next_action 區塊中找 description
    remaining = text[na_start:]
    # 匹配 description: "..." 或 description: > 多行
    desc_match = re.search(r'^\s+description:\s*[">]?\s*(.+)', remaining, re.MULTILINE)
    if not desc_match:
        return None
    first_line = desc_match.group(1).strip().strip('"').strip("'")
    # 截取前 80 字
    if len(first_line) > 80:
        first_line = first_line[:80] + "..."
    return first_line


def format_session(path, label, subject_dir):
    """格式化單一 session.yaml 為摘要行"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None

    # 跳過已結案
    status = extract_field(text, "status")
    phase = extract_field(text, "phase")
    if (status and "已結案" in status) or (phase and "已結案" in phase):
        return None

    block = extract_field(text, "block")
    step = extract_field(text, "step")

    if not block:
        return None

    desc = extract_next_action_desc(text)

    subject_label = SUBJECT_LABELS.get(subject_dir, subject_dir) if subject_dir else label
    prefix = f"{label} {subject_label}" if subject_dir else label

    position = f"Block {block} Step {step}" if step else f"Block {block}"
    next_text = f" → {desc}" if desc else ""

    return f"- **{prefix}**: {position}{next_text}"


# ── Main ─────────────────────────────────────────────────
env = read_env(ENV_PATH)
workspace_id = env.get("WORKSPACE_ID", "")

if not workspace_id:
    print("[pre-compact] 無 WORKSPACE_ID，跳過備份")
    exit(0)

workspace_path = os.path.join(
    REPO_ROOT, "workspaces", "Working_Member", workspace_id
)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
sections = [f"# PreCompact 狀態備份\n\n> 自動產生於 {now}，context 壓縮前備份。\n> AI 壓縮後應重讀此檔案以恢復關鍵脈絡。\n"]

# 1. Voice Anchor
anchor = get_voice_anchor(workspace_path)
if anchor:
    sections.append(f"## 語氣錨點（Voice Anchor）\n\n{anchor}\n")

# 2. CLAUDE.md 核心提醒
sections.append(
    "## 核心規則提醒\n\n"
    "- 語言：繁體中文\n"
    "- 課程設計從「對學生的發展意義」出發\n"
    "- 每份產出自問：頭（思考）、心（情感）、手（行動）有觸及嗎？\n"
    "- 差異化不是標籤學生，是看見每個人的發展位置\n"
    "- 不使用表情符號\n"
)

# 3. 進度錨點
sessions = scan_sessions(workspace_path)
if sessions:
    sections.append("## 工作線進度\n\n" + "\n".join(sessions) + "\n")

# 寫入
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(sections))

print(f"[pre-compact] 已備份語氣錨點與進度至 .claude/.pre-compact-state.md")
print("壓縮後請重讀此檔案：Read(.claude/.pre-compact-state.md)")
