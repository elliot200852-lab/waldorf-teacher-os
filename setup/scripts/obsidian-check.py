#!/usr/bin/env python3
"""
TeacherOS Obsidian Label Checker
掃描 Repo 中缺少中文標籤的 .md / .yaml 檔案，以及未收錄 HOME.md 的檔案。
只做偵測與報告，不修改任何檔案。

用法：
    python3 obsidian-check.py                # 完整掃描（所有 git 追蹤檔案）
    python3 obsidian-check.py --staged-only  # 只掃描 git 暫存區新增檔案
    python3 obsidian-check.py --count-only   # 只輸出數字（供提醒用）
    python3 obsidian-check.py --self-test    # 內建自測（驗證 file_in_home 比對邏輯）

不依賴外部套件，只使用 Python 標準函式庫。
"""

import os
import re
import subprocess
import sys

# ── 路徑設定 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # setup/scripts/ → 上兩層

# ── 排除規則 ──────────────────────────────────────────────
EXCLUDED_FILES = {".DS_Store", ".gitkeep", "token.json", ".env"}
EXCLUDED_DIRS = {".obsidian", ".claude/worktrees", "__pycache__", "node_modules", "venv"}

# 這些目錄的 .md 檔使用 name: 而非 aliases:，跳過 aliases 檢查
SKIP_ALIAS_DIRS = {"ai-core/skills"}

# 被 .gitignore 排除但仍需 Obsidian 標籤檢查的路徑模式
# 這些目錄含教師本機使用的檔案（如學生紀錄），不上傳 git 但需要 Obsidian 能搜到
GITIGNORED_BUT_OBSIDIAN_RELEVANT = ["**/student-notes/"]

# HOME.md 自身不需要被收錄檢查
SKIP_HOME_CHECK = {"Good-notes/HOME.md", "HOME.md"}


def is_excluded(filepath):
    """檢查檔案是否在排除清單中"""
    basename = os.path.basename(filepath)
    if basename in EXCLUDED_FILES:
        return True
    for excluded_dir in EXCLUDED_DIRS:
        if filepath.startswith(excluded_dir + "/") or ("/" + excluded_dir + "/") in filepath:
            return True
    return False


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


def get_gitignored_obsidian_files():
    """掃描被 .gitignore 排除但仍需 Obsidian 標籤檢查的檔案。
    依 GITIGNORED_BUT_OBSIDIAN_RELEVANT 中的 glob 模式，
    用 os.walk 在 Repo 中尋找符合的目錄，回傳其中的 .md / .yaml 檔案。"""
    import fnmatch
    files = []
    for pattern in GITIGNORED_BUT_OBSIDIAN_RELEVANT:
        # 從 pattern 取出目錄名（例如 **/student-notes/ → student-notes）
        dir_name = pattern.replace("**/", "").rstrip("/")
        for root, dirs, filenames in os.walk(REPO_ROOT):
            # 排除 .git 等目錄
            rel_root = os.path.relpath(root, REPO_ROOT)
            if any(excl in rel_root.split(os.sep) for excl in [".git", ".obsidian", "node_modules", "__pycache__"]):
                continue
            if os.path.basename(root) == dir_name:
                for fname in filenames:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in (".md", ".yaml", ".yml"):
                        rel_path = os.path.relpath(os.path.join(root, fname), REPO_ROOT)
                        files.append(rel_path)
    return files


def get_untracked_files():
    """取得 git 未追蹤的新檔案（尚未 git add 的檔案）。
    這些檔案最需要被加入 HOME.md，因為它們通常是剛建立的。"""
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
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
    """檢查檔案是否被 HOME.md 引用（精確比對，避免子字串誤判）。

    匹配策略分兩層：
    - 有路徑結構的檔案（含 /）→ 必須用完整路徑或至少「父目錄/檔名」匹配
    - 根目錄散檔（無 /）→ 可用 basename 匹配
    這樣 A001/content.md 和 A005/content.md 不會互相混淆。
    """
    if filepath in SKIP_HOME_CHECK:
        return True

    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]
    ext = os.path.splitext(basename)[1]  # e.g. '.md', '.sh', ''
    has_path = "/" in filepath

    # 1. 完整路徑比對（最精確，優先）
    #    嘗試完整路徑和去掉副檔名的版本
    filepath_no_ext = os.path.splitext(filepath)[0]
    if filepath in home_content or filepath_no_ext in home_content:
        return True

    escaped_name = re.escape(name_no_ext)
    escaped_ext = re.escape(ext) if ext else ''
    ext_pattern = rf'(?:{escaped_ext})?' if escaped_ext else ''

    if has_path:
        # 2a. 含路徑的 wikilink 匹配：要求 wikilink 中出現「父目錄/檔名」
        #     [[.../A005/content|...]] 匹配 A005/content.md，不匹配 A001/content.md
        parent = os.path.basename(os.path.dirname(filepath))
        escaped_parent = re.escape(parent)
        path_wikilink = rf'\[\[[^\]]*{escaped_parent}/{escaped_name}{ext_pattern}(?:\\?\|[^\]]*)?]]'
        if re.search(path_wikilink, home_content):
            return True

        # 2b. 短名 wikilink 匹配：只匹配 wikilink 內「不含 /」的短名
        #     [[lesson]] 可匹配 ai-core/skills/lesson.md
        #     [[A001/content]] 不是短名（含 /），不會匹配 A005/content.md
        short_wikilink = rf'\[\[{escaped_name}{ext_pattern}(?:\\?\|[^\]]*)?]]'
        if re.search(short_wikilink, home_content):
            return True
    else:
        # 根目錄散檔：用 basename 匹配任何 wikilink
        wikilink_pattern = rf'\[\[(?:[^\]]*\/)?{escaped_name}{ext_pattern}(?:\\?\|[^\]]*)?]]'
        if re.search(wikilink_pattern, home_content):
            return True

    # 3. 完整檔名比對（含副檔名，限無路徑結構的檔案）
    if not has_path and basename in home_content:
        return True

    return False


# ── 清理偵測（第二代功能）──────────────────────────────────

# 非文字檔副檔名（不該出現在 HOME.md 中，除非是 git 追蹤的文件）
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp",  # 圖片
    ".mp3", ".m4a", ".wav", ".ogg", ".flac",                    # 音訊
    ".mp4", ".mov", ".avi", ".mkv",                              # 影片
    ".zip", ".tar", ".gz", ".7z",                                # 壓縮
    ".pdf",                                                       # PDF（保留：可能需收錄）
}
# PDF 特殊處理：git 追蹤的 PDF 可以留在 HOME.md，但 private/ 下的不行


def extract_wikilink_paths(home_content):
    """從 HOME.md 提取所有 wikilink 的路徑部分。
    處理 [[path]] 和 [[path\\|alias]] 兩種格式。
    回傳 [(raw_path, line_number), ...]"""
    results = []
    for i, line in enumerate(home_content.split("\n"), 1):
        # 匹配 [[...]] 中的內容
        for match in re.finditer(r'\[\[([^\]]+?)(?:\\?\|[^\]]*)?]]', line):
            raw_path = match.group(1)
            # 移除可能的 .md 副檔名（Obsidian wikilink 常省略 .md）
            results.append((raw_path, i))
    return results


def scan_home_dead_links(home_content, tracked_set):
    """掃描 HOME.md 中的 wikilink，回報指向不存在檔案的死連結。
    tracked_set: git 追蹤的檔案集合（相對路徑）。

    Obsidian wikilink 有兩種：
    1. 完整路徑：[[workspaces/.../file.md|alias]] — 直接比對
    2. 短名：[[9C-week5-1-v1-教師教案]] — 需要在整個 Repo 中搜尋匹配的 basename
    """
    dead_links = []
    wikilinks = extract_wikilink_paths(home_content)

    # 建立 basename → tracked_path 的索引（用於短名解析）
    basename_index = {}  # basename_no_ext → set of full paths
    for tracked in tracked_set:
        bn = os.path.splitext(os.path.basename(tracked))[0]
        basename_index.setdefault(bn, set()).add(tracked)

    # 也索引本機存在但未追蹤的檔案（gitignored 但本機有的）
    # 透過 os.walk 建索引太慢，僅在短名查不到時 fallback 到路徑檢查

    for raw_path, line_num in wikilinks:
        has_slash = "/" in raw_path

        if has_slash:
            # 完整路徑 wikilink → 直接比對
            candidates = [raw_path]
            if not os.path.splitext(raw_path)[1]:
                candidates.extend([raw_path + ".md", raw_path + ".yaml",
                                   raw_path + ".yml"])

            found = False
            for candidate in candidates:
                if candidate in tracked_set:
                    found = True
                    break
                full_path = os.path.join(REPO_ROOT, candidate)
                if os.path.exists(full_path):
                    found = True
                    break

            # 若仍未找到且無副檔名，嘗試在父目錄中找 prefix 匹配的檔案
            # （處理 .docx / .mp3 / .m4a / .pdf 等 HOME.md 省略副檔名的情況）
            if not found and not os.path.splitext(raw_path)[1]:
                parent = os.path.join(REPO_ROOT, os.path.dirname(raw_path))
                target_name = os.path.basename(raw_path)
                if os.path.isdir(parent):
                    try:
                        for entry in os.listdir(parent):
                            entry_name = os.path.splitext(entry)[0]
                            if entry_name == target_name:
                                found = True
                                break
                    except OSError:
                        pass
        else:
            # 短名 wikilink → 在 basename 索引中搜尋
            name_no_ext = os.path.splitext(raw_path)[0]
            found = name_no_ext in basename_index

            if not found:
                # fallback：也許檔名含副檔名
                found = any(
                    os.path.basename(t) == raw_path
                    for t in tracked_set
                )

        if not found:
            dead_links.append((raw_path, line_num))

    return dead_links


def scan_empty_files(files):
    """回報大小為 0 bytes 的檔案"""
    empty = []
    for filepath in files:
        full_path = os.path.join(REPO_ROOT, filepath)
        try:
            if os.path.exists(full_path) and os.path.getsize(full_path) == 0:
                # .gitkeep 是故意的空檔，跳過
                if os.path.basename(filepath) != ".gitkeep":
                    empty.append(filepath)
        except OSError:
            pass
    return empty


def scan_private_in_home(home_content, tracked_set):
    """回報 HOME.md 中不該收錄的檔案：
    1. 路徑含 /private/（本機私有，不進 git）
    2. 非文字格式且不在 git 追蹤中（圖片/音訊/影片已搬走但連結殘留）"""
    problematic = []
    wikilinks = extract_wikilink_paths(home_content)

    for raw_path, line_num in wikilinks:
        # 規則 1：路徑含 /private/
        if "/private/" in raw_path or raw_path.startswith("private/"):
            problematic.append((raw_path, line_num, "private_path"))
            continue

        # 規則 2：非文字格式的非追蹤檔案
        ext = os.path.splitext(raw_path)[1].lower()
        if ext in BINARY_EXTENSIONS and ext != ".pdf":
            # 檢查是否在 git 追蹤中
            if raw_path not in tracked_set:
                problematic.append((raw_path, line_num, "binary_not_tracked"))
                continue

        # 即使是 .pdf，若在 private/ 也要標記（已被規則 1 捕捉）

    return problematic


def suggest_home_section(filepath):
    """根據路徑模式，回傳建議的 HOME.md 區段名。
    回傳 (h2_section, h3_subsection) 元組。"""
    parts = filepath.split("/")

    # ── 教師 workspace ──
    if filepath.startswith("workspaces/Working_Member/"):
        # 找出教師名
        if len(parts) >= 3:
            teacher_dir = parts[2]  # e.g. "Codeowner_David" or "Teacher_陳佩珊"
            if teacher_dir.startswith("Codeowner_"):
                name = teacher_dir.replace("Codeowner_", "")
                h2 = f"{name} 的工作空間"
            elif teacher_dir.startswith("Teacher_"):
                name = teacher_dir.replace("Teacher_", "")
                h2 = f"{name}老師的工作空間"
            else:
                return ("根目錄散檔", None)

            # 個人設定（嚴格限定）
            basename = os.path.basename(filepath)
            if basename in ("teacheros-personal.yaml", "workspace.yaml", "env-preset.env", "README.md"):
                return (h2, "個人設定")

            # 個人技能
            if "/skills/" in filepath:
                return (h2, "個人技能")

            # 班級判斷
            for i, p in enumerate(parts):
                if p.startswith("class-"):
                    class_code = p  # e.g. "class-12a"
                    # 科目/專案判斷
                    remaining = parts[i+1:]
                    if remaining:
                        subject_or_project = remaining[0]
                        if subject_or_project == "content":
                            return (h2, f"{class_code} 班級")
                        elif subject_or_project in ("senior-project", "marketing"):
                            if "content" in remaining:
                                return (h2, f"{class_code} 班級（{subject_or_project}）教學內容")
                            else:
                                return (h2, f"{class_code} 班級（{subject_or_project}）")
                        elif subject_or_project == "xinbaobao":
                            return (h2, "心抱抱 Podcast 筆記")
                        elif subject_or_project == "records":
                            return (h2, f"{class_code} 學生紀錄")
                        else:
                            return (h2, f"{class_code} {subject_or_project}")
                    return (h2, f"{class_code} 班級")

            # 獨立專案（projects/ 下非 class-* 的）
            if "/projects/" in filepath:
                for i, p in enumerate(parts):
                    if p == "projects" and i + 1 < len(parts):
                        project_name = parts[i + 1]
                        if not project_name.startswith("class-"):
                            return (h2, project_name)

            # 其他教師層級檔案
            return (h2, "個人設定")

    # ── 系統層級 ──
    if filepath.startswith("ai-core/skills/"):
        return ("技能系統（Skills）", "系統技能正本")
    if filepath.startswith("ai-core/reference/"):
        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".yaml", ".yml"):
            return ("系統核心（ai-core/）", "Reference 知識模組（YAML）")
        return ("系統核心（ai-core/）", "Reference 操作文件")
    if filepath.startswith("ai-core/reviews/"):
        return ("系統核心（ai-core/）", "系統回顧紀錄")
    if filepath.startswith("ai-core/"):
        return ("系統核心（ai-core/）", None)
    if filepath.startswith("projects/_di-framework/"):
        return ("差異化教學框架（_di-framework/）", None)
    if filepath.startswith("Good-notes/"):
        return ("Good-notes 建造日誌", None)
    if filepath.startswith("setup/"):
        return ("環境設定與腳本（setup/）", None)
    if filepath.startswith("publish/"):
        return ("輸出與發佈（publish/）", None)
    if filepath.startswith(".claude/"):
        return ("Claude Code 設定（.claude/）", None)

    return ("根目錄散檔", None)


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

    print(f"[self-test] file_in_home (basic): {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)

    # ── 同名不同路徑測試（核心 bug 修復驗證）──
    mock_home_stories = """
| [[path/to/A001/content\\|content]] | 故事正文 |
| [[path/to/A001/narration\\|narration]] | 說書稿 |
| [[path/to/A002/content\\|content]] | 故事正文 |
"""
    story_tests = [
        ("path/to/A001/content.md", True, "A001/content 已收錄"),
        ("path/to/A005/content.md", False, "A005/content 不應被 A001/content 誤判"),
        ("path/to/A005/narration.md", False, "A005/narration 不應被 A001/narration 誤判"),
        ("path/to/A002/content.md", True, "A002/content 已收錄"),
    ]
    st_passed = 0
    st_failed = 0
    for filepath, expected, desc in story_tests:
        result = file_in_home(filepath, mock_home_stories)
        if result == expected:
            st_passed += 1
        else:
            st_failed += 1
            print(f"  FAIL: {filepath} → got {result}, expected {expected} ({desc})")

    print(f"[self-test] file_in_home (same-name): {st_passed} passed, {st_failed} failed")
    if st_failed > 0:
        sys.exit(1)

    # ── suggest_home_section 測試 ──
    suggest_tests = [
        ("workspaces/Working_Member/Teacher_陳佩珊/teacheros-personal.yaml",
         ("陳佩珊老師的工作空間", "個人設定")),
        ("workspaces/Working_Member/Teacher_陳佩珊/env-preset.env",
         ("陳佩珊老師的工作空間", "個人設定")),
        ("workspaces/Working_Member/Teacher_陳佩珊/projects/class-12a/senior-project/content/life-anchor-v2.md",
         ("陳佩珊老師的工作空間", "class-12a 班級（senior-project）教學內容")),
        ("workspaces/Working_Member/Teacher_陳佩珊/projects/teaching-creativity-ppt/index.html",
         ("陳佩珊老師的工作空間", "teaching-creativity-ppt")),
        ("workspaces/Working_Member/Teacher_陳佩珊/projects/class-12a/xinbaobao/EP91.md",
         ("陳佩珊老師的工作空間", "心抱抱 Podcast 筆記")),
        ("workspaces/Working_Member/Teacher_陳佩珊/skills/EXAMPLE.md",
         ("陳佩珊老師的工作空間", "個人技能")),
        ("workspaces/Working_Member/Codeowner_David/projects/class-9c/english/content/lesson.md",
         ("David 的工作空間", "class-9c english")),
        ("ai-core/skills/lesson.md",
         ("技能系統（Skills）", "系統技能正本")),
        ("Good-notes/some-note.md",
         ("Good-notes 建造日誌", None)),
    ]
    s_passed = 0
    s_failed = 0
    for filepath, expected in suggest_tests:
        result = suggest_home_section(filepath)
        if result == expected:
            s_passed += 1
        else:
            s_failed += 1
            print(f"  FAIL suggest: {filepath} → got {result}, expected {expected}")

    print(f"[self-test] suggest_home_section: {s_passed} passed, {s_failed} failed")
    if s_failed > 0:
        sys.exit(1)
    else:
        print("[self-test] suggest_home_section: All edge cases verified.")

    total_failed = failed + s_failed
    if total_failed == 0:
        print("[self-test] ALL TESTS PASSED.")


def main():
    if "--self-test" in sys.argv:
        run_self_test()
        return

    staged_only = "--staged-only" in sys.argv
    count_only = "--count-only" in sys.argv

    # 取得檔案清單
    if staged_only:
        files = get_staged_new_files()
    else:
        files = get_tracked_files()
        existing = set(files)
        # 加入 untracked 新檔案（剛建立、尚未 git add 的檔案）
        for f in get_untracked_files():
            if f not in existing:
                files.append(f)
                existing.add(f)
        # 加入被 gitignore 但仍需 Obsidian 檢查的檔案（如 student-notes/）
        for f in get_gitignored_obsidian_files():
            if f not in existing:
                files.append(f)

    # 讀取 HOME.md（優先從根目錄讀取，兼容舊路徑 Good-notes/）
    home_path = os.path.join(REPO_ROOT, "HOME.md")
    if not os.path.exists(home_path):
        home_path = os.path.join(REPO_ROOT, "Good-notes", "HOME.md")
    home_content = ""
    try:
        with open(home_path, "r", encoding="utf-8") as f:
            home_content = f.read()
    except FileNotFoundError:
        pass

    # ── 既有分類檢查 ──
    tracked_set = set(get_tracked_files())
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
            if not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

        elif ext == ".yaml" or ext == ".yml":
            if yaml_needs_label(filepath):
                unlabeled_yaml.append(filepath)
            if not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

        else:
            # 其他類型檔案只檢查 HOME.md 收錄
            if not file_in_home(filepath, home_content):
                not_in_home.append(filepath)

    # ── 清理偵測（第二代）──
    dead_links = scan_home_dead_links(home_content, tracked_set) if home_content else []
    empty_files = scan_empty_files(files)
    private_in_home = scan_private_in_home(home_content, tracked_set) if home_content else []

    # ── 輸出 ──
    total = (len(unlabeled_md) + len(unlabeled_yaml) + len(not_in_home)
             + len(dead_links) + len(empty_files) + len(private_in_home))

    if count_only:
        if total == 0:
            print("[obsidian-check] OK")
        else:
            parts = []
            if unlabeled_md:
                parts.append(f"{len(unlabeled_md)} 個 .md 未標籤")
            if unlabeled_yaml:
                parts.append(f"{len(unlabeled_yaml)} 個 .yaml 未標籤")
            if not_in_home:
                parts.append(f"{len(not_in_home)} 個未收錄 HOME.md")
            if dead_links:
                parts.append(f"{len(dead_links)} 個 HOME.md 死連結")
            if empty_files:
                parts.append(f"{len(empty_files)} 個空檔")
            if private_in_home:
                parts.append(f"{len(private_in_home)} 個 private/非文字檔殘留 HOME.md")
            print(f"[obsidian-check] {', '.join(parts)}")
        return

    # 完整輸出
    print("[obsidian-check] SCAN_COMPLETE")
    print(f"UNLABELED_MD:{len(unlabeled_md)}")
    print(f"UNLABELED_YAML:{len(unlabeled_yaml)}")
    print(f"NOT_IN_HOME:{len(not_in_home)}")
    print(f"DEAD_LINK:{len(dead_links)}")
    print(f"EMPTY_FILE:{len(empty_files)}")
    print(f"PRIVATE_IN_HOME:{len(private_in_home)}")

    for f in unlabeled_md:
        print(f"FILE:NEW_MD:{f}")
    for f in unlabeled_yaml:
        print(f"FILE:NEW_YAML:{f}")
    for f in not_in_home:
        h2, h3 = suggest_home_section(f)
        suggestion = h3 if h3 else h2
        print(f"FILE:NOT_IN_HOME:{f}:SUGGEST:{suggestion}")
    for path, line_num in dead_links:
        print(f"FILE:DEAD_LINK:{path}:LINE:{line_num}")
    for f in empty_files:
        print(f"FILE:EMPTY:{f}")
    for path, line_num, reason in private_in_home:
        print(f"FILE:PRIVATE_IN_HOME:{path}:LINE:{line_num}:REASON:{reason}")


if __name__ == "__main__":
    main()
