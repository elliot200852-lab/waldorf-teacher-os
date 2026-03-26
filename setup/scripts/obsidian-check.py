#!/usr/bin/env python3
"""
TeacherOS Obsidian Label Checker
掃描 Repo 中缺少中文標籤的 .md / .yaml 檔案，以及未收錄 HOME.md 的檔案。
只做偵測與報告，不修改任何檔案。

用法：
    python3 obsidian-check.py                    # 完整掃描（所有 git 追蹤檔案）
    python3 obsidian-check.py --staged-only      # 只掃描 git 暫存區新增檔案
    python3 obsidian-check.py --count-only       # 只輸出數字（供提醒用）
    python3 obsidian-check.py --skip-home-check  # 跳過 HOME.md 收錄檢查（wrap-up 專用）
    python3 obsidian-check.py --map-filter       # 地圖驅動過濾：無路由的檔案報告為 UNROUTED
    python3 obsidian-check.py --self-test        # 內建自測（驗證 file_in_home 比對邏輯）

不依賴外部套件，只使用 Python 標準函式庫。
"""

import os
import re
import subprocess
import sys
from pathlib import PurePosixPath

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # setup/scripts/ → 上兩層

# ── 排除規則 ──────────────────────────────────────────────
EXCLUDED_FILES = {".DS_Store", ".gitkeep", "token.json", ".env", ".rels"}
EXCLUDED_DIRS = {
    ".obsidian", ".claude/worktrees", "__pycache__", "node_modules", "venv",
    # docx 解壓殘留（word/、docProps/、_rels/、[Content_Types].xml）
    "/word/", "/docProps/", "/_rels/",
}

# 只有這些副檔名的檔案會被檢查 HOME.md 收錄
# 其他類型（.js, .py, .json, .txt, .docx, .pdf 等）不納入 NOT_IN_HOME 檢查
INDEXABLE_EXTENSIONS = {".md", ".yaml", ".yml"}

# 這些副檔名的檔案完全跳過，不做任何檢查
SKIP_EXTENSIONS = {
    ".js", ".py", ".json", ".txt", ".csv", ".tsv",
    ".docx", ".doc", ".xlsx", ".pdf", ".html", ".css",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".emf",
    ".mp3", ".m4a", ".wav", ".mp4",
    ".xml", ".sh", ".ps1", ".bat",
    ".env", ".gitignore",
}

# 這些目錄的 .md 檔使用 name: 而非 aliases:，跳過 aliases 檢查
SKIP_ALIAS_DIRS = {"ai-core/skills"}

# 這些路徑模式下的檔案不該被索引到 HOME.md（工具腳本、暫存輸出等）
SKIP_HOME_INDEX_PATTERNS = [
    "自動化結案報告測試/",
    "資料處理資料夾/",
    "/temp1/", "/temp2/",
    "歌曲-20240823T005746Z",
    "/射日傳說/",
    # 常見 AI 工作殘留
    "/private/",         # 每位教師的機密區（.gitignore 保護，但以防萬一）
]

# 檔名級排除（basename matching）— AI 工作過程中產生的暫存檔
SKIP_HOME_INDEX_BASENAMES = {
    "output.txt", "auth.txt", "help.txt",
}

# 檔名 glob 模式排除 — 比對 basename
SKIP_HOME_INDEX_BASENAME_PATTERNS = [
    "auth*.txt", "login*.txt", "*_url.txt",
    "client_secret*.json",
    "drive_files.*", "all_files.*", "all_folders.*",
    "out.json", "out_utf8.json",
    "structure.json", "children_list.json",
]

# HOME.md 自身不需要被收錄檢查
SKIP_HOME_CHECK = {"Good-notes/HOME.md", "HOME.md"}

# ── 架構地圖（若存在則用於 suggest_section） ──────────────
MAP_PATH = os.path.join(REPO_ROOT, "ai-core", "reference", "repo-structure-map.yaml")
_map_rules = None  # lazy-loaded


def _load_map_rules():
    """嘗試載入地圖路由規則，失敗則回傳空 list（graceful 退化）。
    PyYAML 為選用依賴：缺失時本腳本仍正常運作，只是 NOT_IN_HOME 不帶建議區段。"""
    global _map_rules
    if _map_rules is not None:
        return _map_rules
    _map_rules = []
    if not os.path.exists(MAP_PATH):
        return _map_rules
    try:
        import yaml
        with open(MAP_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _map_rules = data.get("rules", [])
    except Exception:
        _map_rules = []
    return _map_rules


def suggest_section(filepath):
    """用架構地圖的 first-match-wins 規則建議 HOME.md 區段。
    回傳 (section, pattern) 或 (None, None)。"""
    rules = _load_map_rules()
    for rule in rules:
        pattern = rule.get("pattern", "")
        try:
            if PurePosixPath(filepath).match(pattern):
                return rule.get("section", "?"), pattern
        except (ValueError, TypeError):
            continue
    return None, None


def is_excluded(filepath):
    """檢查檔案是否在排除清單中"""
    basename = os.path.basename(filepath)
    if basename in EXCLUDED_FILES:
        return True
    ext = os.path.splitext(basename)[1].lower()
    if ext in SKIP_EXTENSIONS:
        return True
    for excluded_dir in EXCLUDED_DIRS:
        if filepath.startswith(excluded_dir + "/") or ("/" + excluded_dir + "/") in filepath:
            return True
    return False


def should_index_in_home(filepath):
    """判斷檔案是否應該被索引到 HOME.md（只有 .md/.yaml/.yml 且不在排除路徑中）"""
    import fnmatch as _fnmatch

    ext = os.path.splitext(filepath)[1].lower()
    if ext not in INDEXABLE_EXTENSIONS:
        return False
    # 路徑層級排除
    for pattern in SKIP_HOME_INDEX_PATTERNS:
        if pattern in filepath:
            return False
    # 檔名精確排除
    basename = os.path.basename(filepath)
    if basename in SKIP_HOME_INDEX_BASENAMES:
        return False
    # 檔名 glob 排除
    for pat in SKIP_HOME_INDEX_BASENAME_PATTERNS:
        if _fnmatch.fnmatch(basename, pat):
            return False
    return True


def decode_git_path(path):
    """解碼 git 的 octal 跳脫路徑（中文檔名會被 git 編碼為 \\xxx 格式）"""
    path = path.strip()
    # git 用雙引號包裹含特殊字元的路徑
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
    # 解碼 octal 跳脫序列（如 \346\225\231 → 教）
    if "\\" in path:
        try:
            path = path.encode("utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    return path


def get_tracked_files():
    """取得所有 git 追蹤的檔案"""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0:
        return []
    return [decode_git_path(f) for f in result.stdout.strip().split("\n") if f.strip()]


def get_staged_new_files():
    """取得 git 暫存區中新增的檔案"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0:
        return []
    return [decode_git_path(f) for f in result.stdout.strip().split("\n") if f.strip()]


def has_chinese(text):
    """檢查文字中是否包含中文字元"""
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def md_needs_alias(filepath):
    """檢查 .md 檔是否缺少 aliases: frontmatter"""
    # 跳過使用 name: 的目錄
    for skip_dir in SKIP_ALIAS_DIRS:
        if filepath.startswith(skip_dir + "/"):
            return False
    # .claude/commands/ 和 .claude/skills/ 使用 name: 而非 aliases:
    if filepath.startswith(".claude/commands/") or filepath.startswith(".claude/skills/"):
        return False

    full_path = os.path.join(REPO_ROOT, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(2000)  # 只讀前 2000 字元
    except (FileNotFoundError, UnicodeDecodeError):
        return False

    if not content.startswith("---"):
        return True

    end = content.find("---", 3)
    if end < 0:
        return True

    frontmatter = content[3:end]
    return "aliases:" not in frontmatter


def yaml_needs_label(filepath):
    """檢查 .yaml 檔前 5 行是否有中文字元"""
    full_path = os.path.join(REPO_ROOT, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= 5:
                    break
                lines.append(line)
    except (FileNotFoundError, UnicodeDecodeError):
        return False

    text = "".join(lines)
    return not has_chinese(text)


def file_in_home(filepath, home_content):
    """檢查檔案是否被 HOME.md 引用（精確比對，避免子字串誤判）"""
    if filepath in SKIP_HOME_CHECK:
        return True

    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]
    ext = os.path.splitext(basename)[1]  # e.g. '.md', '.sh', ''

    # 1. wikilink 精確匹配：[[name]] [[name.ext]] [[path/name]] [[path/name.ext|alias]]
    #    只匹配檔案自身的副檔名，不接受其他副檔名（避免 add-teacher 匹配 add-teacher.sh）
    escaped_name = re.escape(name_no_ext)
    escaped_ext = re.escape(ext) if ext else ''
    ext_pattern = rf'(?:{escaped_ext})?' if escaped_ext else ''
    wikilink_pattern = rf'\[\[(?:[^\]]*\/)?{escaped_name}{ext_pattern}(?:\\?\|[^\]]*)?]]'
    if re.search(wikilink_pattern, home_content):
        return True

    # 2. 完整路徑比對（含副檔名，不會子字串誤判）
    if filepath in home_content:
        return True

    # 3. 完整檔名比對（含副檔名，例如 add-teacher.md 不會匹配 add-teacher.sh）
    if basename in home_content:
        return True

    return False


def run_self_test():
    """內建自測：驗證 file_in_home() 不會子字串誤判"""
    mock_home = """
| [[setup/add-teacher.sh|add-teacher.sh]] | 新增教師腳本 |
| [[lesson]] | 進入備課 |
| [[subject-lesson-45]] | 45 分鐘課設計 |
| [[setup/quick-start.sh|quick-start.sh]] | 快速安裝 |
| [[obsidian-sync]] | Obsidian 同步 |
| [[setup/scripts/obsidian-check.py|obsidian-check.py]] | 偵測腳本 |
| [[english-45]] | 英文覆蓋層 |
| [[publish/build.sh|build.sh]] | 發佈腳本 |
| [[setup/teacher-guide.md|teacher-guide.md]] | 教師指南 |
| [[setup/teacher-guide-v2.1.html|teacher-guide-v2.1.html]] | 指南 HTML |
| [[wrap-up]] | 收工 |
| [[Good-notes/9C 班工作全貌\\|9C 班工作全貌]] | 導師筆記 |
| [[workspaces/Working_Member/Teacher_郭耀新/manual\\|郭耀新操作手冊]] | 操作手冊 |
"""
    tests = [
        # (filepath, expected, 說明)
        # --- 應回傳 True（已收錄）---
        ("setup/add-teacher.sh",    True,  "完整路徑在 HOME 中"),
        ("ai-core/skills/lesson.md", True, "[[lesson]] wikilink 存在"),
        ("ai-core/skills/subject-lesson-45.md", True, "[[subject-lesson-45]] wikilink 存在"),
        ("setup/quick-start.sh",    True,  "完整路徑在 HOME 中"),
        ("ai-core/skills/obsidian-sync.md", True, "[[obsidian-sync]] wikilink 存在"),
        ("setup/scripts/obsidian-check.py", True, "完整路徑在 HOME 中"),
        ("ai-core/skills/english-45.md", True, "[[english-45]] wikilink 存在"),
        ("publish/build.sh",        True,  "完整路徑在 HOME 中"),
        ("setup/teacher-guide-v2.1.html", True, "含版本號的完整檔名在 HOME 中"),
        ("ai-core/skills/wrap-up.md", True, "[[wrap-up]] wikilink 存在"),
        # --- 應回傳 False（未收錄，不該被子字串誤判）---
        ("ai-core/skills/add-teacher.md",    False, "不應被 add-teacher.sh 誤判"),
        (".claude/commands/add-teacher.md",  False, "不應被 add-teacher.sh 誤判"),
        ("ai-core/skills/quick-start.md",    False, "不應被 quick-start.sh 誤判"),
        ("ai-core/skills/build.md",          False, "不應被 build.sh 誤判"),
        ("ai-core/skills/obsidian.md",       False, "不應被 obsidian-sync 或 obsidian-check 誤判"),
        ("ai-core/skills/english.md",        False, "不應被 english-45 誤判"),
        ("setup/teacher-guide-v3.html",      False, "新版本不應被舊版本誤判"),
        ("ai-core/skills/new-future-skill.md", False, "全新檔案不應被任何既有條目誤判"),
        # --- 表格內 \| 跳脫 pipe 的 wikilink ---
        ("Good-notes/9C 班工作全貌.md", True, "wikilink 含 \\| 跳脫 pipe 應正確匹配"),
        ("workspaces/Working_Member/Teacher_郭耀新/manual.md", True, "路徑型 wikilink 含 \\| 應正確匹配"),
    ]

    passed = 0
    failed = 0
    for filepath, expected, desc in tests:
        result = file_in_home(filepath, mock_home)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            failed += 1
            print(f"  {status}: {filepath} → got {result}, expected {expected} ({desc})")
        else:
            passed += 1

    print(f"[self-test] {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
    else:
        print("[self-test] All edge cases verified.")


def main():
    if "--self-test" in sys.argv:
        run_self_test()
        return

    staged_only = "--staged-only" in sys.argv
    count_only = "--count-only" in sys.argv
    skip_home_check = "--skip-home-check" in sys.argv
    map_filter = "--map-filter" in sys.argv

    # 取得檔案清單
    if staged_only:
        files = get_staged_new_files()
    else:
        files = get_tracked_files()

    # 讀取 HOME.md（優先從根目錄讀取，兼容舊路徑 Good-notes/）
    # --skip-home-check 時完全跳過 HOME.md 檢查（wrap-up 使用此模式，避免 AI 自動收錄）
    home_content = ""
    if not skip_home_check:
        home_path = os.path.join(REPO_ROOT, "HOME.md")
        if not os.path.exists(home_path):
            home_path = os.path.join(REPO_ROOT, "Good-notes", "HOME.md")
        try:
            with open(home_path, "r", encoding="utf-8") as f:
                home_content = f.read()
        except FileNotFoundError:
            pass

    # 分類檢查
    unlabeled_md = []
    unlabeled_yaml = []
    not_in_home = []

    for filepath in files:
        if is_excluded(filepath):
            continue

        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".md":
            if md_needs_alias(filepath):
                unlabeled_md.append(filepath)
            if not skip_home_check and should_index_in_home(filepath) and not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

        elif ext == ".yaml" or ext == ".yml":
            if yaml_needs_label(filepath):
                unlabeled_yaml.append(filepath)
            if not skip_home_check and should_index_in_home(filepath) and not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

        # 其他類型檔案不再檢查 HOME.md 收錄（已在 is_excluded 或 INDEXABLE_EXTENSIONS 過濾）

    # ── 地圖過濾：分流 ROUTED / UNROUTED ─────────────
    routed = []       # 有地圖路由的（AI 可自動歸類）
    unrouted = []     # 無路由的（需人工決定）

    if map_filter and not_in_home:
        for f in not_in_home:
            section, _ = suggest_section(f)
            if section:
                routed.append((f, section))
            else:
                unrouted.append(f)
    elif not_in_home:
        # 無 --map-filter 時，全部走舊路徑
        for f in not_in_home:
            section, _ = suggest_section(f)
            routed.append((f, section))  # section 可能為 None

    # 輸出
    total = len(unlabeled_md) + len(unlabeled_yaml) + len(not_in_home)

    if count_only:
        if total == 0:
            print("[obsidian-check] OK")
        else:
            parts = []
            if unlabeled_md:
                parts.append(f"{len(unlabeled_md)} 個 .md 未標籤")
            if unlabeled_yaml:
                parts.append(f"{len(unlabeled_yaml)} 個 .yaml 未標籤")
            if routed:
                parts.append(f"{len(routed)} 個未收錄 HOME.md（有路由）")
            if unrouted:
                parts.append(f"{len(unrouted)} 個未收錄 HOME.md（無路由，需人工）")
            if not map_filter and not_in_home:
                parts.append(f"{len(not_in_home)} 個未收錄 HOME.md")
            print(f"[obsidian-check] {', '.join(parts)}")
        return

    # 完整輸出
    print("[obsidian-check] SCAN_COMPLETE")
    print(f"UNLABELED_MD:{len(unlabeled_md)}")
    print(f"UNLABELED_YAML:{len(unlabeled_yaml)}")
    print(f"NOT_IN_HOME:{len(not_in_home)}")
    if map_filter:
        print(f"ROUTED:{len(routed)}")
        print(f"UNROUTED:{len(unrouted)}")

    for f in unlabeled_md:
        print(f"FILE:NEW_MD:{f}")
    for f in unlabeled_yaml:
        print(f"FILE:NEW_YAML:{f}")

    for f, section in routed:
        if section:
            print(f"FILE:NOT_IN_HOME:{f}|{section}")
        else:
            print(f"FILE:NOT_IN_HOME:{f}")

    for f in unrouted:
        print(f"FILE:NOT_IN_HOME_UNROUTED:{f}")


if __name__ == "__main__":
    main()
