#!/usr/bin/env python3
"""
TeacherOS HOME.md 自動同步 — Stop Hook
觸發時機：每次 AI 回應完成時（Stop event）
功能：偵測未收錄 HOME.md 的 .md / .yaml 檔案，自動插入對應區段
輸出規則：無新增 → 無輸出；有新增 → 簡短報告
不依賴外部套件，只使用 Python 標準函式庫
"""

import os
import re
import subprocess
import sys
import datetime

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
HOME_MD = os.path.join(REPO_ROOT, "HOME.md")
OBSIDIAN_SCRIPT = os.path.join(REPO_ROOT, "setup", "scripts", "obsidian-check.py")

# ── 區段錨點映射（路徑模式 → HOME.md 中的錨點文字）────────
# 順序重要：先比對具體路徑，後比對通用路徑
SECTION_ANCHORS = [
    # David 9C 各科
    ("class-9c/english/content/",       "9C 英文內容產出"),
    ("class-9c/english/reference/",     "9C 英文參考資料"),
    ("class-9c/english/",               "**9C 英文**"),
    ("class-9c/homeroom/content/",      "9C 導師內容產出"),
    ("class-9c/homeroom/reference/",    "9C 導師參考資料"),
    ("class-9c/homeroom/",              "**9C 導師**"),
    ("class-9c/walking-reading-taiwan/content/", "9C 走讀臺灣內容產出"),
    ("class-9c/walking-reading-taiwan/", "**9C 走讀臺灣**"),
    ("class-9c/student-notes/",         "**9C 學生觀察紀錄**"),
    ("class-9c/",                       "### 9C 班級"),
    # David 9D
    ("class-9d/",                       "### 9D 班級"),
    # 其他教師
    ("Teacher_郭耀新/",                  "## 郭耀新老師的工作空間"),
    ("Teacher_陳佩珊/",                  "## 陳佩珊老師的工作空間"),
    ("Teacher_劉佳芳/",                  "## 劉佳芳老師的工作空間"),
    # 系統
    ("ai-core/skills/",                 "### 系統技能正本"),
    ("ai-core/reference/",             "### Reference 知識模組"),
    ("ai-core/reviews/",               "### 系統回顧紀錄"),
    ("ai-core/",                       "## 系統核心"),
    ("_di-framework/",                 "## 差異化教學框架"),
    (".claude/skills/",                "### Claude Code Skills"),
    (".claude/commands/",              "### Claude Code Commands"),
    (".claude/",                       "## Claude Code 設定"),
    ("setup/scripts/",                 "### 工具腳本"),
    ("setup/hooks/",                   "### 工具腳本"),
    ("setup/",                         "## 環境設定與腳本"),
    ("publish/",                       "## 輸出與發佈"),
    ("Good-notes/",                    "### Good-notes 建造日誌"),
    ("poetry_output/",                 "### 詩歌研究素材產出"),
]

# 不需加入 HOME.md 的檔案模式
SKIP_PATTERNS = [
    "HOME.md",
    "CLAUDE.md",
    ".claude/settings",
    "node_modules/",
    "__pycache__/",
    ".git/",
    ".obsidian/",
    "temp/",
    ".DS_Store",
]


def should_skip(filepath):
    """判斷是否應跳過此檔案"""
    for pattern in SKIP_PATTERNS:
        if pattern in filepath:
            return True
    return False


def get_not_in_home():
    """執行 obsidian-check.py，取得 NOT_IN_HOME 清單"""
    if not os.path.exists(OBSIDIAN_SCRIPT):
        return []

    try:
        result = subprocess.run(
            ["python3", OBSIDIAN_SCRIPT],
            capture_output=True, text=True, timeout=10,
            cwd=REPO_ROOT
        )
    except Exception:
        return []

    missing = []
    for line in result.stdout.strip().split("\n"):
        if line.startswith("FILE:NOT_IN_HOME:"):
            filepath = line.replace("FILE:NOT_IN_HOME:", "").strip()
            if not should_skip(filepath):
                missing.append(filepath)
    return missing


def find_section_anchor(filepath):
    """根據檔案路徑，決定要插入 HOME.md 的哪個區段"""
    for pattern, anchor in SECTION_ANCHORS:
        if pattern in filepath:
            return anchor
    # fallback：根目錄散檔
    return "## 根目錄散檔"


def generate_alias(filepath):
    """從檔案的 frontmatter aliases 或檔名生成顯示名稱"""
    full_path = os.path.join(REPO_ROOT, filepath)
    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]

    # 嘗試從 frontmatter 讀取 aliases
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(2000)
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                frontmatter = content[3:end]
                # 取得第一個 alias
                alias_match = re.search(r'aliases:\s*\n\s*-\s*["\']?(.+?)["\']?\s*$',
                                       frontmatter, re.MULTILINE)
                if alias_match:
                    return alias_match.group(1).strip().strip('"').strip("'")
    except (FileNotFoundError, UnicodeDecodeError):
        pass

    # fallback：從檔名生成（保留中文，將 - 換成空格）
    return name_no_ext.replace("-", " ").replace("_", " ")


def generate_description(filepath):
    """根據檔案路徑和類型，生成簡短說明"""
    basename = os.path.basename(filepath)
    ext = os.path.splitext(basename)[1].lower()

    # 嘗試從 frontmatter 的 type 欄位推測
    full_path = os.path.join(REPO_ROOT, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(1500)
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                frontmatter = content[3:end]
                type_match = re.search(r'^type:\s*(.+)$', frontmatter, re.MULTILINE)
                if type_match:
                    type_val = type_match.group(1).strip()
                    type_map = {
                        "agenda": "會議議程",
                        "sign-in": "簽到表",
                        "notice": "通知",
                        "lesson-plan": "教案",
                        "worksheet": "學習單",
                        "assessment": "評量",
                        "script": "主持稿",
                        "letter": "家長信",
                    }
                    if type_val in type_map:
                        return type_map[type_val]
    except (FileNotFoundError, UnicodeDecodeError):
        pass

    # 根據副檔名
    if ext == ".yaml" or ext == ".yml":
        return "設定檔"
    elif ext == ".sh":
        return "腳本"
    elif ext == ".py":
        return "Python 腳本"

    return "（自動收錄）"


def generate_wikilink(filepath):
    """生成 Obsidian wikilink 表格行"""
    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]
    alias = generate_alias(filepath)
    desc = generate_description(filepath)

    # 判斷是否需要完整路徑（多層目錄深處的檔案用完整路徑，避免同名衝突）
    # 簡短檔名：用 [[name]] 格式
    # 長路徑：用 [[path|alias]] 格式
    depth = filepath.count("/")
    if depth <= 3:
        # 淺層：用檔名 wikilink
        return f"| [[{name_no_ext}]] | {desc} |"
    else:
        # 深層：用完整路徑 + alias
        # 去掉副檔名的完整路徑
        path_no_ext = os.path.splitext(filepath)[0]
        return f"| [[{path_no_ext}\\|{alias}]] | {desc} |"


def insert_into_home(missing_files):
    """將遺漏檔案插入 HOME.md 對應區段"""
    if not os.path.exists(HOME_MD):
        return 0

    with open(HOME_MD, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 按區段分組
    by_section = {}
    for filepath in missing_files:
        anchor = find_section_anchor(filepath)
        if anchor not in by_section:
            by_section[anchor] = []
        by_section[anchor].append(filepath)

    inserted = 0

    for anchor, files in by_section.items():
        # 找到錨點在 HOME.md 中的位置
        anchor_idx = None
        for i, line in enumerate(lines):
            if anchor in line.strip():
                anchor_idx = i
                break

        if anchor_idx is None:
            # 找不到錨點，附加到檔案末尾
            lines.append(f"\n{anchor}\n\n| 檔案 | 說明 |\n|------|------|\n")
            anchor_idx = len(lines) - 1

        # 找到該區段的最後一個表格行（| 開頭的行）
        insert_pos = anchor_idx + 1
        last_table_row = None
        in_table = False

        for i in range(anchor_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("| ") and not stripped.startswith("| -") and not stripped.startswith("| 檔案"):
                last_table_row = i
                in_table = True
            elif stripped.startswith("|---"):
                in_table = True
                continue
            elif stripped.startswith("| 檔案"):
                in_table = True
                continue
            elif in_table and not stripped.startswith("|"):
                # 表格結束
                break
            elif not in_table and stripped and not stripped.startswith("|"):
                # 不在表格中，遇到非空行
                break

        if last_table_row is not None:
            insert_pos = last_table_row + 1
        else:
            # 沒有找到表格行，在錨點後面尋找表格頭
            for i in range(anchor_idx + 1, min(anchor_idx + 6, len(lines))):
                if lines[i].strip().startswith("|------"):
                    insert_pos = i + 1
                    break

        # 插入新行
        new_lines = []
        for filepath in files:
            wikilink = generate_wikilink(filepath)
            new_lines.append(wikilink + "\n")
            inserted += 1

        for j, new_line in enumerate(new_lines):
            lines.insert(insert_pos + j, new_line)

    # 寫回
    if inserted > 0:
        with open(HOME_MD, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return inserted


# ── Main ─────────────────────────────────────────────────
missing = get_not_in_home()

if not missing:
    # 靜默退出
    sys.exit(0)

count = insert_into_home(missing)

if count > 0:
    print(f"[home-sync] {count} 個檔案已自動加入 HOME.md")
    for f in missing:
        print(f"  + {os.path.basename(f)}")
