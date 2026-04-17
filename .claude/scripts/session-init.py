#!/usr/bin/env python3
"""
TeacherOS Session Init Hook
觸發時機：每次使用者送出訊息（UserPromptSubmit）
輸出：
  1. AI_HANDOFF.md 入口提示（確保任何 AI 都知道入口文件位置）
  2. 當前使用者 workspace 內所有班級的工作狀態
不依賴外部套件，只使用 Python 標準函式庫

身份解析鏈（4 階段 fallback）：
  1. 讀 setup/environment.env → WORKSPACE_ID
  2. 讀 .git/config → email → 掃描 env-preset.env 精確比對
  3. noreply email → 提取 GitHub username → 比對 GITHUB_USERNAME
  4. 全部失敗 → 輸出診斷資訊
"""

import configparser
import re
import os
import shutil

# ── 路徑設定 ──────────────────────────────────────────────
# 從腳本位置推算 Repo 根目錄（.claude/scripts/ → 上兩層）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
ENV_PATH = os.path.join(REPO_ROOT, "setup", "environment.env")
GIT_CONFIG_PATH = os.path.join(REPO_ROOT, ".git", "config")
PRESET_DIR = os.path.join(REPO_ROOT, "workspaces", "Working_Member")
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


# ── 輔助函式 ─────────────────────────────────────────────


def read_env(path):
    """讀取 .env 檔案，回傳 dict"""
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


def read_git_config_email():
    """從 .git/config 讀取 [user] email（純文字解析，不需終端機）"""
    try:
        cp = configparser.ConfigParser()
        cp.read(GIT_CONFIG_PATH, encoding="utf-8")
        return cp.get("user", "email", fallback=None)
    except Exception:
        return None


def extract_github_username(email):
    """從 GitHub noreply email 提取 username
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


def scan_presets():
    """掃描所有 env-preset.env，回傳 [{path, env_dict}, ...]"""
    results = []
    if not os.path.isdir(PRESET_DIR):
        return results
    for entry in os.listdir(PRESET_DIR):
        preset_path = os.path.join(PRESET_DIR, entry, "env-preset.env")
        if os.path.isfile(preset_path):
            env = read_env(preset_path)
            if env:
                results.append({"path": preset_path, "env": env})
    return results


def match_email_to_preset(email, presets):
    """精確比對 email → env-preset.env 的 USER_EMAIL"""
    for p in presets:
        if p["env"].get("USER_EMAIL", "").lower() == email.lower():
            return p
    return None


def match_github_username_to_preset(username, presets):
    """比對 GitHub username → env-preset.env 的 GITHUB_USERNAME"""
    for p in presets:
        if p["env"].get("GITHUB_USERNAME", "").lower() == username.lower():
            return p
    return None


def auto_create_env(preset):
    """將匹配的 env-preset.env 複製為 setup/environment.env"""
    try:
        os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
        shutil.copy2(preset["path"], ENV_PATH)
        return True
    except Exception:
        return False


def resolve_identity():
    """4 階段 fallback 身份解析
    回傳 (workspace_id, user_name, method) 或 (None, None, diag_info)
    """

    # Attempt 1: environment.env（快速通道）
    env = read_env(ENV_PATH)
    ws_id = env.get("WORKSPACE_ID", "")
    if ws_id:
        return ws_id, env.get("USER_NAME", ""), "environment.env"

    # 準備 preset 資料（Attempt 2-3 共用）
    presets = scan_presets()
    git_email = read_git_config_email()

    # Attempt 2: git config email → env-preset.env 精確比對
    if git_email:
        matched = match_email_to_preset(git_email, presets)
        if matched:
            auto_create_env(matched)
            return (
                matched["env"].get("WORKSPACE_ID", ""),
                matched["env"].get("USER_NAME", ""),
                f"git email 精確匹配 ({git_email})",
            )

    # Attempt 3: noreply → GitHub username 比對
    if git_email:
        gh_user = extract_github_username(git_email)
        if gh_user:
            matched = match_github_username_to_preset(gh_user, presets)
            if matched:
                auto_create_env(matched)
                return (
                    matched["env"].get("WORKSPACE_ID", ""),
                    matched["env"].get("USER_NAME", ""),
                    f"noreply → {gh_user} 匹配",
                )

    # Attempt 4: 全部失敗 → 回傳診斷資訊
    diag = f"git email: {git_email or '(未設定)'}, 掃描了 {len(presets)} 個 preset"
    return None, None, diag


def extract_field(text, key):
    """從 YAML 文字中提取單一欄位值，處理 null、空值與行內註解，以及 > | block scalar"""
    pattern = rf"^\s*{re.escape(key)}:\s*(.*)$"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    raw = match.group(1).strip()
    val = re.sub(r"\s*#.*$", "", raw).strip()

    # 處理 YAML block scalar（> 或 |）
    if val in (">", "|", ">-", "|-", ">+", "|+"):
        pos = match.end()
        remaining = text[pos:]
        val = None
        for line in remaining.split("\n"):
            if not line:
                continue
            if not line[0].isspace():
                break
            stripped = line.strip()
            if stripped:
                val = stripped[:80] + ("..." if len(stripped) > 80 else "")
                break
        if not val:
            return None
        return val

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

    # 已結案 → 跳過（不顯示於開機摘要）
    phase = extract_field(text, "phase")
    if phase and "已結案" in phase:
        return None

    block = extract_field(text, "block")
    step = extract_field(text, "step")
    desc = extract_field(text, "description")

    if block:
        result = f"區塊{block}"
        if step:
            result += f" Step {step}"
        if desc:
            result += f" → {desc}"
        return result

    # 無 block 欄位：用 phase + status 組合摘要
    status = extract_field(text, "status")
    if phase or status:
        parts = []
        if phase:
            parts.append(phase)
        if status:
            s = status[:60] + ("..." if len(status) > 60 else "")
            parts.append(s)
        return " → ".join(parts)

    return "尚未開始"


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
workspace_id, user_name, method = resolve_identity()

lines = [f"[TeacherOS] 入口：{HANDOFF_REL}"]

if workspace_id:
    workspace_path = os.path.join(REPO_ROOT, "workspaces", "Working_Member", workspace_id)
    statuses = scan_workspace(workspace_path)
    if statuses:
        for s in statuses:
            lines.append(s)
    else:
        lines.append("（workspace 內無進行中的工作線）")
else:
    lines.append(f"[身份解析失敗] {method}")
    lines.append("請執行：bash setup/start.sh（Mac）或 .\\setup\\start.ps1（Windows）")

print("\n".join(lines))
