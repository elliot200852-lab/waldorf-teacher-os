#!/usr/bin/env python3
"""
TeacherOS Obsidian Label Checker
掃描 Repo 中缺少中文標籤的 .md / .yaml 檔案，以及未收錄 HOME.md 的檔案。
偵測模式只做報告；--auto-fix 模式會自動將有格式建議的條目寫入 HOME.md。

用法：
    python3 obsidian-check.py                    # 完整掃描（所有 git 追蹤檔案）
    python3 obsidian-check.py --staged-only      # 只掃描 git 暫存區新增檔案
    python3 obsidian-check.py --count-only       # 只輸出數字（供提醒用）
    python3 obsidian-check.py --skip-home-check  # 跳過 HOME.md 收錄檢查（wrap-up 專用）
    python3 obsidian-check.py --map-filter       # 地圖驅動過濾：無路由的檔案報告為 UNROUTED
    python3 obsidian-check.py --auto-fix         # 自動將有格式建議的條目寫入 HOME.md
    python3 obsidian-check.py --link-check       # 掃描缺少 related: 或 ## 連結 的 .md 檔
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


def _find_sibling_id(filepath):
    """從路徑中萃取 ID 前綴（例如 A012、AM005）和可替換的 ID 段落。
    回傳 (id_str, parent_dir) 或 (None, None)。
    支援兩種結構：
      1. 目錄型：.../A012/content.md → ID 在目錄名
      2. 檔名型：.../reviews/A012-quality.md → ID 在檔名前綴"""
    parts = filepath.replace("\\", "/").split("/")
    # 嘗試目錄名匹配
    for i, part in enumerate(parts):
        if re.match(r'^(A\d{3}|AM\d{3}|TW\d{2})(-v\d+)?$', part):
            return part, "/".join(parts[:i])
    # 嘗試檔名前綴匹配（如 A012-quality.md）
    basename = os.path.splitext(os.path.basename(filepath))[0]
    m = re.match(r'^(A\d{3}|AM\d{3}|TW\d{2})(-v\d+)?-', basename)
    if m:
        return m.group(1) + (m.group(2) or ""), "/".join(parts[:-1])
    return None, None


def suggest_home_entry(filepath, home_content):
    """從 HOME.md 同區段已有的 sibling 條目複製格式，產出完整的建議條目。
    回傳格式化的 HOME.md 條目字串，或 None（無法找到模板時）。"""
    if not home_content:
        return None

    file_id, parent_dir = _find_sibling_id(filepath)
    if not file_id:
        return None

    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]

    id_pattern = r'(A\d{3}|AM\d{3}|TW\d{2})(-v\d+)?'

    # 判斷是目錄型（A012/content）還是檔名型（A012-quality）
    parts = filepath.replace("\\", "/").split("/")
    is_dirname_id = any(re.match(rf'^{id_pattern}$', p) for p in parts)

    # 計算路徑前綴（去掉 ID 和檔名部分），用於限制只匹配同專案的 sibling
    # 例如 .../stories-of-taiwan/stories/A-origins/A012/content.md → .../stories-of-taiwan/
    # 例如 .../ancient-myths-grade5/stories/AM005/content.md → .../ancient-myths-grade5/
    path_prefix = None
    for i, p in enumerate(parts):
        if re.match(rf'^{id_pattern}$', p):
            # 取 ID 目錄的上兩層作為專案前綴（如 .../ancient-myths-grade5/stories/）
            path_prefix = "/".join(parts[:max(1, i-1)])
            break
    if not path_prefix and not is_dirname_id:
        # 檔名型：取父目錄作為前綴
        path_prefix = "/".join(parts[:-2]) if len(parts) > 2 else ""

    if is_dirname_id:
        escaped_basename = re.escape(name_no_ext)
        line_pattern = rf'^\|.*\[\[.*/{id_pattern}/{escaped_basename}.*\]\].*\|.*\|'
    else:
        suffix_match = re.match(rf'^{id_pattern}(-.+)$', name_no_ext)
        if not suffix_match:
            return None
        suffix = re.escape(suffix_match.group(3))
        line_pattern = rf'^\|.*\[\[.*/{id_pattern}{suffix}.*\]\].*\|.*\|'

    matches = []
    for line in home_content.splitlines():
        m = re.match(line_pattern, line)
        if m:
            # 限制同專案路徑：模板行必須包含相同的路徑前綴
            if path_prefix and path_prefix not in line:
                continue
            matches.append(line)

    if not matches:
        return None

    # 取最後一個匹配（最近的 sibling）
    template_line = matches[-1]

    # 替換 ID：將模板中的 sibling ID 換成新檔案的 ID
    if is_dirname_id:
        id_in_template = re.search(rf'/({id_pattern})/', template_line)
        if not id_in_template:
            return None
        old_id = id_in_template.group(1)
        suggested = template_line.replace(f"/{old_id}/", f"/{file_id}/")
    else:
        # 檔名型替換：A009-quality → A012-quality
        id_in_template = re.search(rf'/({id_pattern})-', template_line)
        if not id_in_template:
            return None
        old_id = id_in_template.group(1)
        suggested = template_line.replace(f"/{old_id}-", f"/{file_id}-")

    return suggested


def _read_story_title(file_id):
    """嘗試從 content.md 讀取故事標題。
    搜尋順序：frontmatter title: → 第一個 # 標題（去掉 ID 前綴）。
    回傳標題字串或 None。"""
    import glob as _glob
    pattern = os.path.join(REPO_ROOT, "**", file_id, "content.md")
    candidates = _glob.glob(pattern, recursive=True)
    for cpath in candidates:
        try:
            with open(cpath, "r", encoding="utf-8") as f:
                text = f.read(2000)
        except (FileNotFoundError, UnicodeDecodeError):
            continue
        # 嘗試 frontmatter title:
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                fm = text[3:end]
                m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
                if m:
                    return m.group(1).strip()
        # fallback：第一個 # 標題
        heading = re.search(r'^#\s+(?:' + re.escape(file_id) + r'\s+)?(.+)$', text, re.MULTILINE)
        if heading:
            return heading.group(1).strip()
    return None


def _find_last_sibling_line(home_lines, file_id):
    """在 HOME.md 的行列表中，找到 file_id 的前一個 sibling block 的最後一行行號。
    回傳 (line_index, sibling_id) 或 (None, None)。
    例如 file_id='A012' → 找 A011、A010、A009... 中最近的一個。"""
    id_match = re.match(r'^(A|AM|TW)(\d+)$', file_id)
    if not id_match:
        return None, None
    prefix = id_match.group(1)
    num = int(id_match.group(2))
    # 從前一個 ID 往回找
    for n in range(num - 1, 0, -1):
        if prefix == "TW":
            sib_id = f"{prefix}{n:02d}"
        else:
            sib_id = f"{prefix}{n:03d}"
        # 找這個 sibling 在 HOME.md 中的最後出現位置
        last_idx = None
        for i, line in enumerate(home_lines):
            if f"/{sib_id}/" in line or f"/{sib_id}-" in line or f"/{sib_id}|" in line or f"/{sib_id}\\" in line:
                last_idx = i
        if last_idx is not None:
            return last_idx, sib_id
    return None, None


def auto_fix_home(routed_files, home_content):
    """自動將有格式建議的 ROUTED 檔案寫入 HOME.md。
    routed_files: [(filepath, section, suggested_entry), ...]
    回傳 (new_home_content, fixed_count, skipped_files)。"""
    # 按 ID 分組
    from collections import OrderedDict
    groups = OrderedDict()  # id → [(filepath, suggested_entry), ...]
    skipped = []

    for filepath, section, suggested in routed_files:
        if not suggested:
            skipped.append(filepath)
            continue
        file_id, _ = _find_sibling_id(filepath)
        if not file_id:
            skipped.append(filepath)
            continue
        groups.setdefault(file_id, []).append((filepath, suggested))

    if not groups:
        return home_content, 0, skipped

    home_lines = home_content.splitlines()
    # 從後往前插入（避免行號偏移）
    insertions = []  # [(line_index, block_text), ...]

    for file_id, entries in groups.items():
        insert_after, sib_id = _find_last_sibling_line(home_lines, file_id)
        if insert_after is None:
            for fp, _ in entries:
                skipped.append(fp)
            continue

        # 讀取標題
        title = _read_story_title(file_id)
        header = f"**{file_id} {title}**" if title else f"**{file_id}**"

        # 組裝 block
        block_lines = [
            "",
            header,
            "",
            "| 檔案 | 說明 |",
            "|------|------|",
        ]
        for _, entry in entries:
            block_lines.append(entry)

        insertions.append((insert_after, block_lines, len(entries)))

    # 從後往前插入
    insertions.sort(key=lambda x: x[0], reverse=True)
    fixed_count = 0
    for insert_after, block_lines, count in insertions:
        for i, line in enumerate(block_lines):
            home_lines.insert(insert_after + 1 + i, line)
        fixed_count += count

    new_content = "\n".join(home_lines)
    # 確保檔案結尾有換行
    if not new_content.endswith("\n"):
        new_content += "\n"
    return new_content, fixed_count, skipped


# ── 連結檢查（--link-check）──────────────────────────────
# 依 wikilink-protocol.yaml placement 規則判斷每個 .md 檔需要哪些連結

import fnmatch as _fnmatch_module

# 檔案類型 → (需要 frontmatter related, 需要 body ## 連結)
LINK_RULES = [
    # (glob_pattern, needs_related, needs_body_section, type_label)
    ("wiki/concepts/**/*.md", True,  True,  "concept_page"),
    ("wiki/*.md",             True,  True,  "wiki_entry"),
    ("*-教師教案.md",          True,  True,  "lesson_plan"),
    ("*-學習單.md",            True,  False, "worksheet"),
    ("*-content.md",          True,  True,  "story_content"),
    ("*-narration.md",        True,  False, "story_component"),
    ("*-images.md",           True,  False, "story_component"),
    ("*-chalkboard-prompt.md", True, False, "story_component"),
]

# 連結檢查豁免（不需要連結的目錄或檔案）
LINK_CHECK_SKIP_DIRS = {
    ".claude/", "ai-core/skills/", "setup/", ".github/",
    "ai-core/reference/", "projects/_di-framework/",
}
LINK_CHECK_SKIP_FILES = {"_wiki-handoff.md", "README.md", "CLAUDE.md", "HOME.md"}


def classify_link_type(filepath):
    """依 wikilink-protocol.yaml 規則判斷檔案類型。
    回傳 (needs_related, needs_body, type_label) 或 None（不需檢查）。"""
    basename = os.path.basename(filepath)

    # 跳過豁免
    if basename in LINK_CHECK_SKIP_FILES:
        return None
    for skip in LINK_CHECK_SKIP_DIRS:
        if filepath.startswith(skip):
            return None

    # 嘗試匹配規則（first-match-wins）
    for pattern, needs_related, needs_body, label in LINK_RULES:
        if PurePosixPath(filepath).match(pattern):
            return (needs_related, needs_body, label)

    return None


def check_links(filepath):
    """檢查檔案是否缺少 related: frontmatter 或 ## 連結 body 區段。
    回傳 (missing_related: bool, missing_body: bool, type_label: str) 或 None。"""
    rule = classify_link_type(filepath)
    if rule is None:
        return None

    needs_related, needs_body, label = rule
    full_path = os.path.join(REPO_ROOT, filepath)

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read(5000)
    except (FileNotFoundError, UnicodeDecodeError):
        return None

    missing_related = False
    missing_body = False

    if needs_related:
        # 檢查 frontmatter 中是否有 related:
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                fm = content[3:end]
                if "related:" not in fm:
                    missing_related = True
            else:
                missing_related = True
        else:
            missing_related = True

    if needs_body:
        # 讀取完整檔案（前 5000 字元可能不夠）
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                full_content = f.read()
        except (FileNotFoundError, UnicodeDecodeError):
            full_content = content
        if "## 連結" not in full_content:
            missing_body = True

    if not missing_related and not missing_body:
        return None

    return (missing_related, missing_body, label)


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
| [[lesson-engine]] | 統一課程設計引擎 |
| [[setup/quick-start.sh|quick-start.sh]] | 快速安裝 |
| [[obsidian-sync]] | Obsidian 同步 |
| [[setup/scripts/obsidian-check.py|obsidian-check.py]] | 偵測腳本 |
| [[english-overlay]] | 英文覆蓋層 |
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
        ("ai-core/skills/lesson-engine.md", True, "[[lesson-engine]] wikilink 存在"),
        ("setup/quick-start.sh",    True,  "完整路徑在 HOME 中"),
        ("ai-core/skills/obsidian-sync.md", True, "[[obsidian-sync]] wikilink 存在"),
        ("setup/scripts/obsidian-check.py", True, "完整路徑在 HOME 中"),
        ("ai-core/skills/english-overlay.md", True, "[[english-overlay]] wikilink 存在"),
        ("publish/build.sh",        True,  "完整路徑在 HOME 中"),
        ("setup/teacher-guide-v2.1.html", True, "含版本號的完整檔名在 HOME 中"),
        ("ai-core/skills/wrap-up.md", True, "[[wrap-up]] wikilink 存在"),
        # --- 應回傳 False（未收錄，不該被子字串誤判）---
        ("ai-core/skills/add-teacher.md",    False, "不應被 add-teacher.sh 誤判"),
        (".claude/commands/add-teacher.md",  False, "不應被 add-teacher.sh 誤判"),
        ("ai-core/skills/quick-start.md",    False, "不應被 quick-start.sh 誤判"),
        ("ai-core/skills/build.md",          False, "不應被 build.sh 誤判"),
        ("ai-core/skills/obsidian.md",       False, "不應被 obsidian-sync 或 obsidian-check 誤判"),
        ("ai-core/skills/english.md",        False, "不應被 english-overlay 誤判"),
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

    print(f"[self-test] file_in_home: {passed} passed, {failed} failed")

    # ── suggest_home_entry 測試 ──────────────────────────
    mock_home_suggest = (
        "**A009 鐵砂與煙霧——十三行人的秘密**\n\n"
        "| 檔案 | 說明 |\n|------|------|\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A009/content\\|content]] | 故事正文 |\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A009/narration\\|narration]] | 教師說書稿 |\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A009/images\\|images]] | 投影圖像清單 |\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A009/chalkboard-prompt\\|chalkboard]] | 黑板畫 prompt |\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A009/raw-materials\\|raw-materials]] | 研究素材包 |\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/reviews/A009-quality\\|品質報告]] | 品質審核紀錄 |\n\n"
        "**AM004 種姓制度與聖牛**\n\n"
        "| 檔案 | 說明 |\n|------|------|\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM004/content\\|content]] | 故事正文 |\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM004/waldorf-teaching\\|waldorf-teaching]] | 華德福教學指引 |\n"
        "| [[workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM004/museum-materials\\|museum-materials]] | 博物館藝術素材 |\n"
    )

    suggest_tests = [
        # (filepath, expected_contains, 說明)
        (
            "workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A012/content.md",
            "/A012/content",
            "A012 content 應從 A009 模板產出"
        ),
        (
            "workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A012/narration.md",
            "/A012/narration",
            "A012 narration 應從 A009 模板產出"
        ),
        (
            "workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM005/museum-materials.yaml",
            "/AM005/museum-materials",
            "AM005 museum-materials 應從 AM004 模板產出"
        ),
        (
            "workspaces/Working_Member/Codeowner_David/projects/stories-of-taiwan/stories/A-origins/A012/some-new-file.md",
            None,
            "HOME 無同名 basename 時應回傳 None"
        ),
    ]

    s_passed = 0
    s_failed = 0
    for filepath, expected, desc in suggest_tests:
        result = suggest_home_entry(filepath, mock_home_suggest)
        if expected is None:
            ok = result is None
        else:
            ok = result is not None and expected in result
        status = "PASS" if ok else "FAIL"
        if not ok:
            s_failed += 1
            print(f"  {status}: suggest_home_entry({filepath}) → {result!r}, expected contains {expected!r} ({desc})")
        else:
            s_passed += 1

    print(f"[self-test] suggest_home_entry: {s_passed} passed, {s_failed} failed")
    total_failed = failed + s_failed
    if total_failed > 0:
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
    auto_fix = "--auto-fix" in sys.argv
    link_check = "--link-check" in sys.argv

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
    link_orphans = []  # (filepath, missing_related, missing_body, type_label)

    for filepath in files:
        if is_excluded(filepath):
            continue

        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".md":
            if md_needs_alias(filepath):
                unlabeled_md.append(filepath)
            if not skip_home_check and should_index_in_home(filepath) and not file_in_home(filepath, home_content):
                not_in_home.append(filepath)
            if link_check:
                result = check_links(filepath)
                if result:
                    mr, mb, label = result
                    link_orphans.append((filepath, mr, mb, label))

        elif ext == ".yaml" or ext == ".yml":
            if yaml_needs_label(filepath):
                unlabeled_yaml.append(filepath)
            if not skip_home_check and should_index_in_home(filepath) and not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

        # 其他類型檔案不再檢查 HOME.md 收錄（已在 is_excluded 或 INDEXABLE_EXTENSIONS 過濾）

    # ── 地圖過濾：分流 ROUTED / UNROUTED ─────────────
    routed = []       # 有地圖路由的（AI 可自動歸類）— (filepath, section, suggested_entry)
    unrouted = []     # 無路由的（需人工決定）

    if map_filter and not_in_home:
        for f in not_in_home:
            section, _ = suggest_section(f)
            if section:
                suggested = suggest_home_entry(f, home_content)
                routed.append((f, section, suggested))
            else:
                unrouted.append(f)
    elif not_in_home:
        # 無 --map-filter 時，全部走舊路徑
        for f in not_in_home:
            section, _ = suggest_section(f)
            suggested = suggest_home_entry(f, home_content)
            routed.append((f, section, suggested))  # section 可能為 None

    # ── auto-fix 模式：自動寫入 HOME.md ─────────────
    if auto_fix and routed:
        home_path = os.path.join(REPO_ROOT, "HOME.md")
        if not os.path.exists(home_path):
            home_path = os.path.join(REPO_ROOT, "Good-notes", "HOME.md")
        new_content, fixed, fix_skipped = auto_fix_home(routed, home_content)
        if fixed > 0:
            with open(home_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[obsidian-check] AUTO-FIX: {fixed} 個條目已寫入 HOME.md")
            # 重新載入 home_content，移除已修復的檔案
            home_content = new_content
            still_missing = []
            for fp, sec, sug in routed:
                if not file_in_home(fp, home_content):
                    still_missing.append((fp, sec, sug))
            routed = still_missing
            not_in_home = [fp for fp, _, _ in routed] + unrouted
        if fix_skipped:
            print(f"[obsidian-check] AUTO-FIX: {len(fix_skipped)} 個無法自動修復（需人工）")
            for fp in fix_skipped:
                print(f"  SKIP: {fp}")

    # 輸出
    total = len(unlabeled_md) + len(unlabeled_yaml) + len(not_in_home) + len(link_orphans)

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
                with_suggest = sum(1 for _, _, s in routed if s)
                if with_suggest:
                    parts.append(f"{len(routed)} 個未收錄 HOME.md（{with_suggest} 個有格式建議）")
                else:
                    parts.append(f"{len(routed)} 個未收錄 HOME.md（有路由）")
            if unrouted:
                parts.append(f"{len(unrouted)} 個未收錄 HOME.md（無路由，需人工）")
            if not map_filter and not_in_home:
                parts.append(f"{len(not_in_home)} 個未收錄 HOME.md")
            if link_orphans:
                parts.append(f"{len(link_orphans)} 個缺連結")
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
    if link_check:
        print(f"LINK_ORPHAN:{len(link_orphans)}")

    for f in unlabeled_md:
        print(f"FILE:NEW_MD:{f}")
    for f in unlabeled_yaml:
        print(f"FILE:NEW_YAML:{f}")

    for f, section, suggested in routed:
        if suggested:
            print(f"FILE:NOT_IN_HOME:{f}|{section}|SUGGEST:{suggested}")
        elif section:
            print(f"FILE:NOT_IN_HOME:{f}|{section}")
        else:
            print(f"FILE:NOT_IN_HOME:{f}")

    for f in unrouted:
        print(f"FILE:NOT_IN_HOME_UNROUTED:{f}")

    for f, mr, mb, label in link_orphans:
        missing = []
        if mr:
            missing.append("related")
        if mb:
            missing.append("body")
        print(f"FILE:LINK_ORPHAN:{f}|{label}|missing:{'+'.join(missing)}")


if __name__ == "__main__":
    main()
