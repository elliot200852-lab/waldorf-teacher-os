#!/usr/bin/env python3
"""
TeacherOS Google Drive 備份腳本（跨平台版）

將整個 Repo 備份至 Google Drive，Markdown 檔自動轉為原生 Google Doc。
目錄結構以繁體中文命名，方便 Gemini 讀取與日後瀏覽。

用法：
    python3 publish/backup-to-drive.py              # 增量備份（預設）
    python3 publish/backup-to-drive.py --dry-run     # 預覽模式，不實際上傳
    python3 publish/backup-to-drive.py --force        # 強制全部重新上傳

增量邏輯：
    1. 比對本地檔案的 mtime / size 與 manifest 紀錄
    2. 若不同 → 進一步比對 MD5
    3. MD5 相同 → 跳過；MD5 不同 → 更新
    4. manifest 中不存在 → 新增上傳
    5. 本地已刪除但 manifest 中仍存在 → 列出，不自動刪除

帳號與路徑從 setup/environment.env 讀取。
"""

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


# ── 常數 ──────────────────────────────────────────────────────

DRIVE_ROOT_FOLDER_BASE = "TeacherOS-Creator-Hub 備份"

MANIFEST_PATH_REL = Path("publish") / "drive-backup-manifest.json"

# 排除的目錄名稱（出現在路徑中的任何層級都排除）
EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    ".claude",
    ".obsidian",
    "__pycache__",
}

# 排除的檔案名稱
EXCLUDE_FILES = {
    ".DS_Store",
    "Thumbs.db",
}

# 排除的特定相對路徑（相對於 Repo 根目錄）
EXCLUDE_PATHS = {
    "setup/credentials.json",
    "setup/token.json",
}

# 排除的副檔名
EXCLUDE_EXTS = {
    ".gdoc",
    ".gsheet",
    ".gslides",
}

# environment.env 中需要遮蔽的關鍵字（出現在 KEY 中則遮蔽 VALUE）
REDACT_KEYWORDS = {"TOKEN", "SECRET", "KEY", "PASSWORD"}

# ── 目錄中文對照表 ────────────────────────────────────────────

FOLDER_CN_MAP = {
    "ai-core": "AI 核心",
    "ai-core/skills": "AI 核心/技能",
    "ai-core/reference": "AI 核心/參考文件",
    "ai-core/reviews": "AI 核心/回顧",
    "projects": "專案",
    "projects/_di-framework": "專案/差異化框架",
    "projects/_di-framework/content": "專案/差異化框架/教學內容",
    "projects/g9": "專案/九年級",
    "projects/g9/content": "專案/九年級/教學內容",
    "workspaces": "工作空間",
    "workspaces/Working_Member": "工作空間/工作夥伴",
    "workspaces/_template": "工作空間/範本",
    "workspaces/工作範例參考": "工作空間/工作範例參考",
    "publish": "輸出工具",
    "publish/templates": "輸出工具/範本",
    "publish/scripts": "輸出工具/腳本",
    "publish/images": "輸出工具/圖片",
    "setup": "環境設定",
    "setup/assets": "環境設定/資源",
    "setup/hooks": "環境設定/鉤子",
    "setup/scripts": "環境設定/腳本",
    "stories": "臺灣的故事",
    "stories/A-origins": "臺灣的故事/A-起源篇",
    "Good-notes": "學習筆記",
    "Git History": "開發紀錄",
    "Engineer_Reference": "工程參考",
    "Tool Download": "工具下載",
    "Tool Download/英文寫作訂正系統": "工具下載/英文寫作訂正系統",
    "Tool Download/音檔轉逐字稿-macOS": "工具下載/音檔轉逐字稿-macOS",
    "David-personal-asset-base": "個人素材庫",
    "temp": "暫存產出",
    "temp/apps-script-viewer": "暫存產出/apps-script-viewer",
    "video": "影片",
    "video/src": "影片/原始碼",
    "video/public": "影片/公開資源",
    "video/public/photos": "影片/公開資源/照片",
    "site": "網站",
    "site/.firebase": "網站/.firebase",
    "manifests": "清單",
    "projects/_di-framework/reference": "專案/差異化框架/參考文件",
    "stories/A-origins/A007": "臺灣的故事/A-起源篇/A007",
    "workspaces/_template/private": "工作空間/範本/private",
    "workspaces/_template/projects": "工作空間/範本/projects",
    "workspaces/_template/skills": "工作空間/範本/skills",
    "workspaces/工作範例參考/projects": "工作空間/工作範例參考/projects",
    "網站展示": "網站展示",
    "網站展示/.firebase": "網站展示/.firebase",
    "網站展示/public": "網站展示/public",
    ".github": "GitHub 設定",
}

# ── 通用片段翻譯表 ──────────────────────────────────────────────
# 當完整路徑不在 FOLDER_CN_MAP 時，逐個片段翻譯（適用於所有層級）。
# 班級代碼與教師前綴另有動態處理邏輯，不需寫在此表中。

SEGMENT_CN_MAP = {
    # 結構性目錄
    "projects": "專案",
    "skills": "技能",
    "private": "個人",
    "content": "教學內容",
    "reference": "參考資料",
    "working": "工作區",
    "records": "紀錄",
    "student-logs": "學生紀錄",
    "notes": "筆記",
    "scripts": "腳本",
    "reviews": "回顧",
    "themes": "主題",
    "stories": "故事",
    "comms": "溝通紀錄",
    "activities": "活動",
    "media": "媒體",
    "photos": "照片",
    "public": "公開資源",
    # 科目
    "english": "英文",
    "homeroom": "導師",
    "main-lesson": "主課程",
    "farm-internship": "農場實習",
    "walking-reading-taiwan": "走讀臺灣",
    "ml-taiwan-literature": "主課程-臺灣文學",
    "ml-undecided": "主課程-待定",
    "taiwanese": "臺語",
    "information_technology": "資訊科技",
    "marketing": "行銷",
    "senior-project": "畢業專題",
    "xinbaobao": "新寶寶",
    "service-learning-trip": "服務學習旅行",
    # 故事相關
    "stories-of-taiwan": "臺灣的故事",
    "A-origins": "A-起源篇",
    # David 個人
    "poetry_output": "詩歌產出",
    "voice-samples": "聲音樣本",
    "Codeowner_David": "David-系統管理",
    "Working_Member": "工作夥伴",
    "_template": "範本",
    "_class-template": "班級範本",
    # 結構性（補充）
    "images": "圖片",
    "templates": "範本",
    "assets": "資源",
    "hooks": "鉤子",
    "src": "原始碼",
    "student-notes": "學生觀察",
    # 其他
    "taiwanese-history": "臺灣歷史",
    "teaching-creativity-ppt": "創意教學簡報",
    "apps-script-viewer": "Apps Script 檢視器",
    # David 詩歌主題
    "light-and-darkness": "光與暗",
    "the-road": "路",
    # 特殊目錄識別碼（DI 框架、年級代碼等）
    "_di-framework": "差異化框架",
    "g9": "九年級",
    # Word 解壓縮暫存結構（林詩閔 reference 內）
    "temp1": "暫存1",
    "temp2": "暫存2",
    "_rels": "_rels",
    "docProps": "文件屬性",
    "word": "word",
    "theme": "佈景主題",
}

# ── 班級代碼動態翻譯 ────────────────────────────────────────────

CLASS_SEGMENT_MAP = {
    "class-9c": "九年級C班",
    "class-9d": "九年級D班",
    "class-9a": "九年級A班",
    "class-9b": "九年級B班",
    "class-8a": "八年級A班",
    "class-7a": "七年級A班",
    "class-4c": "四年級C班",
    "class-12a": "十二年級A班",
    "class-claude": "Claude示範班",
}


# ── 工具函式 ────────────────────────────────────────────────────

def die(msg: str) -> None:
    """印出錯誤訊息並以 exit code 1 終止。"""
    print(msg, file=sys.stderr)
    sys.exit(1)


def load_env(env_path: Path) -> dict:
    """讀取 KEY=VALUE 格式的環境設定檔，忽略註解與空行。"""
    env = {}
    if not env_path.is_file():
        return env
    with env_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


def md5_file(filepath: Path) -> str:
    """計算檔案的 MD5 雜湊值（十六進位）。"""
    h = hashlib.md5()
    with filepath.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def strip_front_matter(text: str) -> str:
    """移除 Markdown 檔案頂部的 YAML Front Matter（--- 區塊）。

    僅匹配行首的 --- 作為開閉標記，避免誤判值中包含 --- 的情況。
    """
    # Front matter 必須以 --- 開頭（可含尾隨空白）
    if not text.startswith("---"):
        return text
    # 使用正則找第二個獨立行的 ---（行首 + 三個減號 + 行尾或空白）
    match = re.search(r"\n---[ \t]*(\n|$)", text, re.MULTILINE)
    if not match:
        return text
    rest_start = match.end()
    return text[rest_start:]


def _translate_segment(segment: str) -> str:
    """翻譯單一目錄片段名稱。

    查詢順序：SEGMENT_CN_MAP → CLASS_SEGMENT_MAP → Teacher_ 前綴處理 → 原名。
    """
    # 1. 通用片段對照表
    if segment in SEGMENT_CN_MAP:
        return SEGMENT_CN_MAP[segment]

    # 2. 班級代碼
    if segment in CLASS_SEGMENT_MAP:
        return CLASS_SEGMENT_MAP[segment]

    # 3. Teacher_ 前綴：保留教師中文名（Teacher_陳佩珊 → 陳佩珊老師）
    if segment.startswith("Teacher_"):
        teacher_name = segment[len("Teacher_"):]
        return f"{teacher_name}老師"

    # 4. 故事編號（A001, A002-v2 等）：保留原名
    if re.match(r"^A\d{3}(-v\d+)?$", segment):
        return segment

    # 5. 原名（已經是中文或無法翻譯）
    return segment


def translate_dir_path(rel_dir: str) -> str:
    """將 Repo 相對目錄路徑翻譯為中文。

    優先查對照表；若查無，對 temp/museum_* 目錄做特殊處理；
    否則逐層翻譯（已翻譯的父目錄 + 未翻譯的子目錄原名）。
    """
    # 正規化路徑分隔符
    rel_dir = rel_dir.replace("\\", "/").strip("/")
    if not rel_dir:
        return ""

    # 直接查表
    if rel_dir in FOLDER_CN_MAP:
        return FOLDER_CN_MAP[rel_dir]

    # temp/museum_* 特殊處理
    parts = rel_dir.split("/")
    if len(parts) >= 2 and parts[0] == "temp" and parts[1].startswith("museum_"):
        # 剝除 museum_ 前綴和日期後綴（如 _20260320）
        raw = parts[1][len("museum_"):]
        # 移除末尾的 _YYYYMMDD 日期
        raw = re.sub(r"_\d{8}$", "", raw)
        cn_name = f"暫存產出/博物館素材-{raw}"
        if len(parts) > 2:
            # 子目錄保持原名
            cn_name += "/" + "/".join(parts[2:])
        return cn_name

    # 逐層翻譯：盡可能長地匹配已知路徑
    best_match_len = 0
    best_match_cn = ""
    for i in range(len(parts), 0, -1):
        candidate = "/".join(parts[:i])
        if candidate in FOLDER_CN_MAP:
            best_match_len = i
            best_match_cn = FOLDER_CN_MAP[candidate]
            break

    if best_match_len > 0 and best_match_len < len(parts):
        # 父目錄有翻譯，子目錄逐片段翻譯
        remainder_parts = parts[best_match_len:]
        translated_remainder = "/".join(
            _translate_segment(seg) for seg in remainder_parts
        )
        return f"{best_match_cn}/{translated_remainder}"

    if best_match_len == len(parts):
        return best_match_cn

    # 完全沒有匹配：逐片段翻譯
    return "/".join(_translate_segment(seg) for seg in parts)


def get_leaf_name(cn_path: str) -> str:
    """從中文路徑取得最後一層的名稱。"""
    parts = cn_path.rsplit("/", 1)
    return parts[-1] if parts else cn_path


def redact_env_content(content: str) -> str:
    """遮蔽 environment.env 中含敏感關鍵字的值。"""
    lines = content.splitlines(keepends=True)
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, sep, value = stripped.partition("=")
            key_upper = key.strip().upper()
            if any(kw in key_upper for kw in REDACT_KEYWORDS):
                result.append(f"{key.strip()}=[REDACTED-備份時自動遮蔽]\n")
                continue
        result.append(line)
    return "".join(result)


# ── GWS CLI 操作 ───────────────────────────────────────────────

def run_gws_cmd(args: list, timeout: int = 60, cwd: Path | None = None) -> tuple:
    """執行 gws CLI 指令，回傳 (success, parsed_json_or_None, stderr)。"""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        data = None
        if result.stdout.strip():
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        return result.returncode == 0, data, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, None, "指令逾時"
    except FileNotFoundError:
        return False, None, "找不到 gws 指令"


def run_gws_with_retry(args: list, max_retries: int = 3, timeout: int = 120, cwd: Path | None = None) -> tuple:
    """執行 gws 指令，遇到 429 錯誤時自動重試。"""
    for attempt in range(max_retries):
        ok, data, stderr = run_gws_cmd(args, timeout=timeout, cwd=cwd)
        if ok:
            return ok, data, stderr
        if "429" in stderr or "rate" in stderr.lower():
            wait = 5 * (attempt + 1)
            print(f"  [備份] 遇到速率限制，等待 {wait} 秒後重試...")
            time.sleep(wait)
            continue
        # 非 429 錯誤，不重試
        return ok, data, stderr
    return False, None, f"重試 {max_retries} 次後仍失敗"


def check_gws_installed() -> bool:
    """檢查 gws CLI 是否已安裝。"""
    return shutil.which("gws") is not None


def check_gws_authenticated() -> bool:
    """檢查 gws CLI 是否已通過認證。"""
    try:
        result = subprocess.run(
            ["gws", "gmail", "users", "getProfile", "--params", '{"userId":"me"}'],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def gws_create_folder(name: str, parent_id: str) -> str | None:
    """在 Drive 中建立資料夾，回傳 folder ID 或 None。"""
    args = [
        "gws", "drive", "files", "create",
        "--json", json.dumps({
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }),
    ]
    ok, data, stderr = run_gws_with_retry(args)
    if ok and isinstance(data, dict):
        return data.get("id")
    return None


def gws_find_folder(name: str, parent_id: str) -> str | None:
    """在 Drive 中搜尋指定名稱的資料夾，回傳 folder ID 或 None。"""
    query = (
        f"name='{name}' and '{parent_id}' in parents "
        f"and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    args = [
        "gws", "drive", "files", "list",
        "--params", json.dumps({"q": query, "pageSize": 1}),
    ]
    ok, data, stderr = run_gws_cmd(args)
    if ok and isinstance(data, dict) and data.get("files"):
        return data["files"][0].get("id")
    return None


def gws_upload_file(local_path: Path, name: str, parent_id: str,
                    mime_type: str | None = None) -> str | None:
    """上傳檔案至 Drive，回傳 file ID 或 None。

    若指定 mime_type 為 Google Doc 類型，Drive 會自動轉換格式。
    注意：gws CLI 的 --upload 會拒絕 cwd 以外的絕對路徑，
    因此使用 cwd 切換到檔案所在目錄，並傳入檔名。
    """
    metadata = {"name": name, "parents": [parent_id]}
    if mime_type:
        metadata["mimeType"] = mime_type

    # gws --upload 只接受 cwd 內的路徑，故切換到檔案所在目錄
    local_path = Path(local_path).resolve()
    args = [
        "gws", "drive", "files", "create",
        "--upload", local_path.name,
        "--json", json.dumps(metadata),
    ]
    ok, data, stderr = run_gws_with_retry(args, timeout=300, cwd=local_path.parent)
    if ok and isinstance(data, dict):
        return data.get("id")
    return None


def gws_update_file(file_id: str, local_path: Path) -> bool:
    """更新 Drive 上已存在的檔案內容。"""
    local_path = Path(local_path).resolve()
    args = [
        "gws", "drive", "files", "update",
        "--params", json.dumps({"fileId": file_id}),
        "--upload", local_path.name,
    ]
    ok, data, stderr = run_gws_with_retry(args, timeout=300, cwd=local_path.parent)
    return ok


def gws_delete_and_reupload(file_id: str, local_path: Path, name: str,
                             parent_id: str, mime_type: str | None = None) -> str | None:
    """刪除舊檔再重新上傳（用於需要 mimeType 轉換的 Google Doc 更新）。"""
    # 刪除舊檔
    del_args = [
        "gws", "drive", "files", "delete",
        "--params", json.dumps({"fileId": file_id}),
    ]
    run_gws_cmd(del_args)
    # 重新上傳
    return gws_upload_file(local_path, name, parent_id, mime_type)


# ── 檔案掃描 ───────────────────────────────────────────────────

def should_exclude(rel_path: Path) -> bool:
    """判斷檔案是否應排除備份。"""
    rel_str = str(rel_path).replace("\\", "/")

    # 排除特定路徑
    if rel_str in EXCLUDE_PATHS:
        return True

    # 排除特定檔名
    if rel_path.name in EXCLUDE_FILES:
        return True

    # 排除特定副檔名
    if rel_path.suffix.lower() in EXCLUDE_EXTS:
        return True

    # 排除特定目錄中的檔案
    for part in rel_path.parts:
        if part in EXCLUDE_DIRS:
            return True

    return False


def scan_files(repo_root: Path) -> tuple:
    """掃描 Repo 中所有應備份的檔案。

    Returns:
        (included: list[Path], excluded_count: int)
        included 為相對路徑列表。
    """
    included = []
    excluded_count = 0

    for dirpath, dirnames, filenames in os.walk(repo_root, followlinks=False):
        # 修改 dirnames 以避免進入排除的目錄
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDE_DIRS
        ]

        for filename in filenames:
            full_path = Path(dirpath) / filename
            rel_path = full_path.relative_to(repo_root)
            if should_exclude(rel_path):
                excluded_count += 1
            else:
                included.append(rel_path)

    included.sort()
    return included, excluded_count


# ── Manifest 管理 ──────────────────────────────────────────────

def load_manifest(manifest_path: Path) -> dict:
    """讀取 manifest 檔案。若不存在則回傳空結構。"""
    if manifest_path.is_file():
        try:
            with manifest_path.open(encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "last_backup": None,
        "root_folder_id": None,
        "files": {},
        "folders": {},
    }


def save_manifest(manifest_path: Path, manifest: dict) -> None:
    """寫入 manifest 檔案。"""
    manifest["last_backup"] = datetime.now(timezone.utc).isoformat()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


# ── 增量比對 ───────────────────────────────────────────────────

def classify_files(
    repo_root: Path,
    files: list,
    manifest: dict,
    force: bool,
) -> tuple:
    """將檔案分類為新增、更新、跳過。

    Returns:
        (new_files, updated_files, skipped_files, deleted_files)
        deleted_files = manifest 中有但本地已不存在的檔案路徑列表
    """
    new_files = []
    updated_files = []
    skipped_files = []

    manifest_files = manifest.get("files", {})

    for rel_path in files:
        rel_str = str(rel_path).replace("\\", "/")
        full_path = repo_root / rel_path

        if force:
            if rel_str in manifest_files:
                updated_files.append(rel_path)
            else:
                new_files.append(rel_path)
            continue

        if rel_str not in manifest_files:
            new_files.append(rel_path)
            continue

        entry = manifest_files[rel_str]
        stat = full_path.stat()
        local_mtime = stat.st_mtime
        local_size = stat.st_size

        if local_mtime == entry.get("mtime") and local_size == entry.get("size"):
            skipped_files.append(rel_path)
            continue

        # mtime 或 size 不同 → 比對 MD5
        local_md5 = md5_file(full_path)
        if local_md5 == entry.get("md5"):
            # 內容相同，更新 manifest 中的 mtime/size 即可
            entry["mtime"] = local_mtime
            entry["size"] = local_size
            skipped_files.append(rel_path)
        else:
            updated_files.append(rel_path)

    # 偵測已刪除的檔案
    current_set = {str(p).replace("\\", "/") for p in files}
    deleted_files = [
        p for p in manifest_files
        if p not in current_set
    ]

    return new_files, updated_files, skipped_files, deleted_files


# ── 資料夾建立 ─────────────────────────────────────────────────

def ensure_folder_chain(
    rel_dir: str,
    root_folder_id: str,
    manifest: dict,
    dry_run: bool = False,
    untranslated: set | None = None,
) -> str | None:
    """確保 Drive 上的資料夾鏈存在，回傳最末層資料夾 ID。

    逐層建立，每層都先查 manifest → 查 Drive → 建立。
    """
    if not rel_dir:
        return root_folder_id

    rel_dir = rel_dir.replace("\\", "/").strip("/")
    folders = manifest.setdefault("folders", {})

    # 已在 manifest 中
    if rel_dir in folders:
        return folders[rel_dir]

    # 逐層處理
    parts = rel_dir.split("/")
    parent_id = root_folder_id

    for i in range(1, len(parts) + 1):
        partial = "/".join(parts[:i])
        if partial in folders:
            parent_id = folders[partial]
            continue

        # 需要建立此層
        cn_path = translate_dir_path(partial)
        leaf_name = get_leaf_name(cn_path)

        # 檢查是否有未翻譯的片段
        if untranslated is not None:
            seg = parts[i - 1]  # 當前層的目錄名
            # 已在任何對照表中、或是中文/數字/museum 特殊處理 → 不算未翻譯
            is_known = (
                seg in SEGMENT_CN_MAP
                or seg in CLASS_SEGMENT_MAP
                or seg in FOLDER_CN_MAP
                or seg.startswith("Teacher_")
                or seg.startswith("museum_")
                or re.match(r"^A\d{3}(-v\d+)?$", seg)
                or re.search(r"[\u4e00-\u9fff]", seg)  # 含中文字
                or seg.startswith(".")  # 隱藏目錄
            )
            if not is_known:
                untranslated.add(partial)

        if dry_run:
            # dry-run 模式下用假 ID
            fake_id = f"dry-run-{partial}"
            folders[partial] = fake_id
            print(f"[備份] 建立資料夾: {cn_path}")
            parent_id = fake_id
            continue

        # 先查 Drive 上是否已存在
        existing_id = gws_find_folder(leaf_name, parent_id)
        if existing_id:
            folders[partial] = existing_id
            parent_id = existing_id
            continue

        # 建立資料夾
        new_id = gws_create_folder(leaf_name, parent_id)
        if new_id:
            folders[partial] = new_id
            parent_id = new_id
            print(f"[備份] 建立資料夾: {cn_path}")
        else:
            print(f"[錯誤] 無法建立資料夾: {cn_path}", file=sys.stderr)
            return None

    return parent_id


# ── 單檔上傳 ───────────────────────────────────────────────────

def process_file(
    repo_root: Path,
    rel_path: Path,
    root_folder_id: str,
    manifest: dict,
    is_update: bool,
    pandoc_bin: str | None,
    dry_run: bool = False,
    untranslated: set | None = None,
) -> bool:
    """處理單一檔案的上傳或更新。回傳是否成功。"""
    rel_str = str(rel_path).replace("\\", "/")
    full_path = repo_root / rel_path

    # 取得目標資料夾
    rel_dir = str(rel_path.parent).replace("\\", "/")
    if rel_dir == ".":
        rel_dir = ""

    cn_dir = translate_dir_path(rel_dir) if rel_dir else ""

    # 確保資料夾存在
    parent_id = ensure_folder_chain(
        rel_dir, root_folder_id, manifest,
        dry_run=dry_run, untranslated=untranslated,
    )
    if parent_id is None and not dry_run:
        return False

    # 決定上傳名稱與方式
    filename = rel_path.name
    is_md = rel_path.suffix.lower() == ".md"
    is_env = rel_str == "setup/environment.env"

    # 暫存檔案路徑（若需要前處理）
    temp_file = None
    upload_path = full_path
    upload_name = filename
    mime_type = None

    try:
        # environment.env 遮蔽處理
        if is_env:
            content = full_path.read_text(encoding="utf-8")
            redacted = redact_env_content(content)
            temp_file = Path(tempfile.NamedTemporaryFile(
                suffix=".env", delete=False).name)
            temp_file.write_text(redacted, encoding="utf-8")
            upload_path = temp_file

        # Markdown → Google Doc 轉換
        elif is_md and pandoc_bin:
            # 讀取並剝除 Front Matter
            content = full_path.read_text(encoding="utf-8")
            stripped = strip_front_matter(content)

            # 寫入暫存 .md（無 Front Matter）
            temp_md = Path(tempfile.NamedTemporaryFile(
                suffix=".md", delete=False).name)
            temp_md.write_text(stripped, encoding="utf-8")

            # Pandoc 轉 docx
            temp_docx = Path(tempfile.NamedTemporaryFile(
                suffix=".docx", delete=False).name)
            ref_doc = repo_root / "publish" / "templates" / "backup-reference.docx"

            pandoc_args = [
                pandoc_bin,
                "--from", "markdown",
                "--to", "docx",
            ]
            if ref_doc.is_file():
                pandoc_args.extend(["--reference-doc", str(ref_doc)])
            pandoc_args.extend(["-o", str(temp_docx), str(temp_md)])

            try:
                subprocess.run(pandoc_args, check=True, capture_output=True, timeout=30)
                upload_path = temp_docx
                # 上傳名稱去掉 .md，Drive 會顯示為 Google Doc
                upload_name = rel_path.stem
                mime_type = "application/vnd.google-apps.document"
                temp_file = temp_docx
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                # Pandoc 失敗，改為直接上傳 .md
                upload_path = full_path
                upload_name = filename
                mime_type = None
            finally:
                # 清理暫存 .md
                if temp_md.is_file():
                    temp_md.unlink()

        # 顯示與格式
        display_type = " (Google Doc)" if mime_type else ""
        display_dir = cn_dir if cn_dir else DRIVE_ROOT_FOLDER_BASE
        action = "更新" if is_update else "上傳"

        if dry_run:
            print(f"[備份] {action}: {rel_str} -> {display_dir}/{upload_name}{display_type}")
            return True

        # 實際上傳
        print(f"[備份] {action}: {rel_str} -> {display_dir}/{upload_name}{display_type}")

        if is_update:
            old_entry = manifest.get("files", {}).get(rel_str, {})
            old_drive_id = old_entry.get("drive_id")

            if old_drive_id and mime_type:
                # Google Doc 更新需要刪除再重建（因為 mimeType 轉換）
                new_id = gws_delete_and_reupload(
                    old_drive_id, upload_path, upload_name,
                    parent_id, mime_type,
                )
                if not new_id:
                    return False
                drive_id = new_id
            elif old_drive_id:
                # 一般檔案直接更新
                if not gws_update_file(old_drive_id, upload_path):
                    return False
                drive_id = old_drive_id
            else:
                # 沒有舊 ID，當新檔上傳
                drive_id = gws_upload_file(upload_path, upload_name, parent_id, mime_type)
                if not drive_id:
                    return False
        else:
            drive_id = gws_upload_file(upload_path, upload_name, parent_id, mime_type)
            if not drive_id:
                return False

        # 更新 manifest
        stat = full_path.stat()
        manifest.setdefault("files", {})[rel_str] = {
            "drive_id": drive_id,
            "mtime": stat.st_mtime,
            "size": stat.st_size,
            "md5": md5_file(full_path),
        }
        return True

    finally:
        # 清理暫存檔
        if temp_file and temp_file.is_file():
            try:
                temp_file.unlink()
            except OSError:
                pass


# ── 主流程 ─────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TeacherOS Google Drive 備份：將 Repo 備份至 Drive，Markdown 自動轉為 Google Doc",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="預覽模式：列出會處理的檔案，不實際上傳",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="強制模式：忽略 manifest，重新上傳所有檔案",
    )
    args = parser.parse_args()

    start_time = time.time()

    # ── Repo 根目錄 ──
    repo_root = Path(__file__).resolve().parent.parent
    env_file = repo_root / "setup" / "environment.env"
    manifest_path = repo_root / MANIFEST_PATH_REL

    # ── 載入環境設定 ──
    if not env_file.is_file():
        die(
            "錯誤：找不到環境設定檔 setup/environment.env\n"
            "請依照 setup/environment.env.example 建立你的個人設定檔。\n"
            "執行：cp setup/environment.env.example setup/environment.env"
        )

    env = load_env(env_file)
    pandoc_path = env.get("PANDOC_PATH", "pandoc")

    # ── 工具檢查 ──
    if not check_gws_installed():
        die(
            "錯誤：找不到 gws CLI。\n"
            "\n"
            "請安裝 Google Workspace CLI：\n"
            "  npm install -g @googleworkspace/cli\n"
            "\n"
            "安裝後登入：\n"
            "  gws auth login"
        )

    if not args.dry_run and not check_gws_authenticated():
        die(
            "錯誤：gws CLI 尚未通過認證。\n"
            "\n"
            "請執行：\n"
            "  gws auth login\n"
            "\n"
            "若需指定帳號：\n"
            "  gws auth login --account YOUR_EMAIL@gmail.com"
        )

    # ── Pandoc 檢查 ──
    pandoc_bin = pandoc_path or "pandoc"
    if shutil.which(pandoc_bin) is None:
        print(
            "[警告] 找不到 Pandoc，Markdown 檔將以純文字上傳（不轉為 Google Doc）。",
            file=sys.stderr,
        )
        install_hint = {
            "Darwin": "brew install pandoc",
            "Windows": "choco install pandoc  或  winget install pandoc",
            "Linux": "sudo apt install pandoc  或  sudo dnf install pandoc",
        }.get(platform.system(), "請安裝 Pandoc")
        print(f"  安裝方式：{install_hint}\n", file=sys.stderr)
        pandoc_bin = None

    # ── 載入 Manifest ──
    manifest = load_manifest(manifest_path)

    if args.force:
        # 強制模式：保留 manifest 完整（包括 drive_id），不清除 files
        # classify_files 在 force=True 時會將已有 manifest 紀錄的檔案標為 updated
        # 這樣有 drive_id 的檔案會被原地更新，而非重複上傳新檔
        pass

    # ── 掃描檔案 ──
    print(f"[備份] 掃描檔案...")
    files, excluded_count = scan_files(repo_root)
    print(f"[備份] 掃描檔案... 找到 {len(files)} 個檔案（排除 {excluded_count} 個）")

    # ── 增量比對 ──
    new_files, updated_files, skipped_files, deleted_files = classify_files(
        repo_root, files, manifest, force=args.force,
    )
    print(
        f"[備份] 增量比對... "
        f"新增 {len(new_files)} / 更新 {len(updated_files)} / "
        f"跳過 {len(skipped_files)} / 已刪除 {len(deleted_files)}"
    )

    # ── 已刪除檔案報告 ──
    if deleted_files:
        print(f"\n[備份] 以下 {len(deleted_files)} 個檔案已從本地刪除，但仍保留在 Drive 上：")
        for dp in deleted_files:
            print(f"  - {dp}")
        print("  （如需清理，請手動從 Drive 刪除）\n")

    # ── 無需處理 ──
    to_process = new_files + updated_files
    if not to_process:
        print("[備份] 所有檔案皆為最新，無需處理。")
        # 仍然儲存 manifest（可能更新了 mtime/size）
        if not args.dry_run:
            save_manifest(manifest_path, manifest)
        return

    # ── 確保根目錄存在 ──
    today_str = time.strftime("%Y-%m-%d")
    drive_root_name = f"{DRIVE_ROOT_FOLDER_BASE}-{today_str}"
    root_folder_id = manifest.get("root_folder_id")
    manifest_root_name = manifest.get("root_folder_name", "")

    if not root_folder_id and not args.dry_run:
        # 搜尋是否已存在同基底名稱的根目錄（不限日期）
        existing_id = None
        existing_name = None
        search_ok, search_data, search_err = run_gws_cmd([
            "gws", "drive", "files", "list",
            "--params", json.dumps({
                "q": f"name contains '{DRIVE_ROOT_FOLDER_BASE}' and mimeType = 'application/vnd.google-apps.folder' and 'root' in parents and trashed = false",
                "pageSize": 5,
            })
        ])
        if search_ok and isinstance(search_data, dict) and search_data.get("files"):
            for f in search_data["files"]:
                if f["name"].startswith(DRIVE_ROOT_FOLDER_BASE):
                    existing_id = f["id"]
                    existing_name = f["name"]
                    break

        if existing_id:
            root_folder_id = existing_id
            manifest["root_folder_id"] = root_folder_id
            # 若日期不同，更新資料夾名稱為今天的日期
            if existing_name != drive_root_name:
                print(f"[備份] 更新根目錄日期: {existing_name} → {drive_root_name}")
                run_gws_cmd([
                    "gws", "drive", "files", "update",
                    "--params", json.dumps({"fileId": existing_id}),
                    "--json", json.dumps({"name": drive_root_name})
                ])
            else:
                print(f"[備份] 找到現有根目錄: {drive_root_name}")
            manifest["root_folder_name"] = drive_root_name
        else:
            root_folder_id = gws_create_folder(drive_root_name, "root")
            if root_folder_id:
                manifest["root_folder_id"] = root_folder_id
                manifest["root_folder_name"] = drive_root_name
                print(f"[備份] 建立根目錄: {drive_root_name}")
            else:
                die("錯誤：無法在 Drive 中建立根目錄。")

    if args.dry_run and not root_folder_id:
        root_folder_id = "dry-run-root"
        manifest["root_folder_id"] = root_folder_id
        print(f"[備份] 根目錄: {drive_root_name}")

    # ── 處理檔案 ──
    untranslated = set()
    success_count = 0
    fail_count = 0
    failures = []

    updated_set = set(str(p) for p in updated_files)  # O(1) lookup

    for idx, rel_path in enumerate(to_process, 1):
        is_update = str(rel_path) in updated_set
        try:
            ok = process_file(
                repo_root, rel_path, root_folder_id, manifest,
                is_update=is_update,
                pandoc_bin=pandoc_bin,
                dry_run=args.dry_run,
                untranslated=untranslated,
            )
            if ok:
                success_count += 1
            else:
                fail_count += 1
                failures.append(str(rel_path))
        except Exception as e:
            fail_count += 1
            failures.append(f"{rel_path}（{e}）")
            print(f"[錯誤] 處理失敗: {rel_path} - {e}", file=sys.stderr)

        # 每 50 個檔案自動儲存 manifest，避免中斷後全部重來
        if not args.dry_run and idx % 50 == 0:
            save_manifest(manifest_path, manifest)

    # ── 儲存 Manifest ──
    if not args.dry_run:
        save_manifest(manifest_path, manifest)

    # ── 未翻譯目錄報告 ──
    if untranslated and args.dry_run:
        print(f"\n[備份] 以下目錄未有中文翻譯（使用英文原名）：")
        for ud in sorted(untranslated):
            print(f"  未翻譯目錄: {ud}")

    # ── 完成報告 ──
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    time_str = f"{minutes} 分 {seconds} 秒" if minutes > 0 else f"{seconds} 秒"

    print(f"\n[備份] 完成！共處理 {success_count} 個檔案，耗時 {time_str}")

    if failures:
        print(f"\n[備份] {fail_count} 個檔案處理失敗：")
        for f in failures:
            print(f"  - {f}")

    if args.dry_run:
        print("\n（--dry-run 模式，未實際上傳任何檔案）")


if __name__ == "__main__":
    main()
