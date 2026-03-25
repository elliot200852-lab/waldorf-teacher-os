#!/usr/bin/env python3
"""
TeacherOS 輸出腳本（跨平台版）

將 .md 草稿轉換為 .docx，上傳至 Google Drive。
上傳方式：GWS CLI 優先 → Google Drive Desktop 備案（無縫切換，使用者無感）
輸出資料夾與檔名皆使用繁體中文，版本號保留 V1/V2 格式。

用法（AI 直接呼叫，不需教師手動輸入）：
    python3 publish/build.py <markdown檔案路徑>
    python3 publish/build.py --dry-run <markdown檔案路徑>

班級與科目解析優先順序：
    1. Markdown 檔案頂部 Front Matter（class: / subject: 欄位）
    2. 備援：從檔案路徑自動推斷
    3. 兩者皆失敗 → 輸出說明並終止

帳號與路徑從 setup/environment.env 讀取。
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


# ── 常數對照表 ──────────────────────────────────────────────────

CLASS_CN_MAP = {
    "class-9c": "九年級C班",
    "class-9d": "九年級D班",
    "class-8a": "八年級A班",
    "class-7a": "七年級A班",
}

SUBJECT_CN_MAP = {
    "english": "英文",
    "main-lesson": "主課程",
    "homeroom": "導師",
}

CN_NUMBERS = {
    1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
    6: "六", 7: "七", 8: "八", 9: "九", 10: "十",
}


# ── 工具函式 ────────────────────────────────────────────────────

def cn_num(n: int) -> str:
    """阿拉伯數字轉中文數字（1-10）。"""
    return CN_NUMBERS.get(n, str(n))


def die(msg: str) -> None:
    """印出錯誤訊息並以 exit code 1 終止。"""
    print(msg, file=sys.stderr)
    sys.exit(1)


def load_env(env_path: Path) -> dict:
    """讀取 KEY=VALUE 格式的環境設定檔，忽略註解與空行。"""
    env = {}
    with env_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


def fm_value(key: str, filepath: Path) -> str:
    """從 Markdown Front Matter（--- 區塊）讀取指定 key 的值。"""
    in_front_matter = False
    with filepath.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped == "---":
                if not in_front_matter:
                    in_front_matter = True
                    continue
                else:
                    break  # 結束 Front Matter 區塊
            if in_front_matter:
                m = re.match(rf"^{re.escape(key)}:\s*(.+)$", stripped)
                if m:
                    return m.group(1).strip("'\"")
    return ""


def detect_gdrive_cloud_path(email: str) -> Path | None:
    """偵測 Google Drive Desktop 的本機同步路徑（跨平台）。"""
    system = platform.system()

    if system == "Darwin":
        # macOS：~/Library/CloudStorage/GoogleDrive-{email}/我的雲端硬碟/
        p = Path.home() / "Library" / "CloudStorage" / f"GoogleDrive-{email}" / "我的雲端硬碟"
        if p.is_dir():
            return p
        # 英文版 macOS
        p_en = Path.home() / "Library" / "CloudStorage" / f"GoogleDrive-{email}" / "My Drive"
        if p_en.is_dir():
            return p_en

    elif system == "Windows":
        # Windows：常見路徑
        candidates = [
            Path(os.environ.get("USERPROFILE", "")) / "Google Drive" / "My Drive",
            Path(os.environ.get("USERPROFILE", "")) / "Google Drive",
            Path("G:/My Drive"),
            Path("G:/"),
        ]
        for c in candidates:
            if c.is_dir():
                return c

    elif system == "Linux":
        # Linux：與 macOS CloudStorage 類似的路徑結構
        p = Path.home() / "Library" / "CloudStorage" / f"GoogleDrive-{email}" / "My Drive"
        if p.is_dir():
            return p
        # Gnome / Nautilus mount
        p2 = Path.home() / ".local" / "share" / "google-drive" / email
        if p2.is_dir():
            return p2

    return None


def detect_gdrive_cloudstorge_dir(email: str) -> bool:
    """檢查 Google Drive Desktop CloudStorage 目錄是否存在。"""
    system = platform.system()
    if system == "Darwin":
        return (Path.home() / "Library" / "CloudStorage" / f"GoogleDrive-{email}").is_dir()
    elif system == "Windows":
        return detect_gdrive_cloud_path(email) is not None
    elif system == "Linux":
        return detect_gdrive_cloud_path(email) is not None
    return False


def check_gws_available() -> bool:
    """檢查 GWS CLI 是否可用（已安裝且已登入）。"""
    if shutil.which("gws") is None:
        return False
    try:
        result = subprocess.run(
            ["gws", "auth", "status"],
            capture_output=True, timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_json_cmd(args: list[str]) -> dict | list | None:
    """執行指令並嘗試解析 JSON 輸出。"""
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def extract_id(data) -> str | None:
    """從 GWS CLI 回傳的 JSON 中取出 id 欄位。"""
    if isinstance(data, dict):
        return data.get("id")
    return None


# ── GWS CLI 上傳 ───────────────────────────────────────────────

def gws_upload(
    temp_docx: Path,
    folder_path: str,
    cn_filename: str,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """透過 GWS CLI 逐層建立資料夾並上傳檔案。

    Returns:
        (success, message)
    """
    parent_id = "root"
    parts = [p for p in folder_path.split("/") if p]

    for part in parts:
        query = (
            f"name='{part}' and '{parent_id}' in parents "
            f"and mimeType='application/vnd.google-apps.folder' and trashed=false"
        )
        list_args = [
            "gws", "drive", "files", "list",
            "--params", json.dumps({"q": query, "pageSize": 1}),
        ]

        if dry_run:
            print(f"  [dry-run] 查詢資料夾：{part}（parent={parent_id}）")
            parent_id = f"fake-id-{part}"
            continue

        data = run_json_cmd(list_args)
        folder_id = None
        if isinstance(data, dict) and data.get("files"):
            folder_id = data["files"][0].get("id")

        if not folder_id:
            create_args = [
                "gws", "drive", "files", "create",
                "--json", json.dumps({
                    "name": part,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_id],
                }),
            ]
            create_data = run_json_cmd(create_args)
            folder_id = extract_id(create_data)

        if folder_id:
            parent_id = folder_id
        else:
            return False, f"無法建立或找到資料夾：{part}"

    # 上傳檔案
    if dry_run:
        msg = (
            f"  [dry-run] 上傳檔案：{cn_filename}\n"
            f"  [dry-run] 目標資料夾：{folder_path}"
        )
        print(msg)
        return True, f"雲端路徑：{folder_path}/{cn_filename}"

    upload_args = [
        "gws", "drive", "files", "create",
        "--params", json.dumps({"parents": [parent_id]}),
        "--json", json.dumps({"name": cn_filename}),
        "--upload", str(temp_docx),
    ]
    upload_data = run_json_cmd(upload_args)
    file_id = extract_id(upload_data)

    if file_id:
        return True, (
            f"完成。已上傳至 Google Drive。\n"
            f"雲端路徑：{folder_path}/{cn_filename}\n"
            f"檔案連結：https://drive.google.com/file/d/{file_id}"
        )
    return False, "GWS CLI 上傳失敗。"


# ── Google Drive Desktop 複製 ──────────────────────────────────

def gdrive_desktop_copy(
    temp_docx: Path,
    gdrive_base: Path,
    class_cn: str,
    subject_cn: str,
    doc_folder: str,
    cn_filename: str,
    display_path: str,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """透過 Google Drive Desktop 本機同步資料夾複製檔案。"""
    if doc_folder:
        output_dir = gdrive_base / class_cn / subject_cn / doc_folder
    else:
        output_dir = gdrive_base / class_cn / subject_cn

    output_docx = output_dir / cn_filename

    if dry_run:
        print(f"  [dry-run] 建立資料夾：{output_dir}")
        print(f"  [dry-run] 複製檔案至：{output_docx}")
        return True, f"雲端路徑：{display_path}{cn_filename}"

    output_dir.mkdir(parents=True, exist_ok=True)
    # 移除舊檔避免 Stale file handle
    if output_docx.exists():
        output_docx.unlink()
    shutil.copy2(temp_docx, output_docx)

    return True, (
        f"完成。Google Drive Desktop 將自動同步。\n"
        f"雲端路徑：{display_path}{cn_filename}"
    )


# ── 主流程 ─────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TeacherOS 輸出腳本：Markdown → docx → Google Drive",
    )
    parser.add_argument("input", help="Markdown 檔案的相對路徑（相對於 Repo 根目錄）")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行，不實際轉換或上傳")
    args = parser.parse_args()

    # ── Repo 根目錄 ──
    repo_root = Path(__file__).resolve().parent.parent
    env_file = repo_root / "setup" / "environment.env"

    # ── 載入環境設定 ──
    if not env_file.is_file():
        die(
            "錯誤：找不到環境設定檔 setup/environment.env\n"
            "請依照 setup/environment.env.example 建立你的個人設定檔。\n"
            "執行：cp setup/environment.env.example setup/environment.env"
        )

    env = load_env(env_file)

    google_drive_email = env.get("GOOGLE_DRIVE_EMAIL", "")
    google_drive_folder = env.get("GOOGLE_DRIVE_FOLDER", "")
    user_name = env.get("USER_NAME", "未設定")
    pandoc_path = env.get("PANDOC_PATH", "pandoc")

    # ── 驗證必要設定 ──
    if not google_drive_email or google_drive_email == "你的帳號@gmail.com":
        die("錯誤：setup/environment.env 中的 GOOGLE_DRIVE_EMAIL 尚未設定。")

    if not google_drive_folder:
        die("錯誤：setup/environment.env 中的 GOOGLE_DRIVE_FOLDER 尚未設定。")

    # ── Pandoc 檢查 ──
    pandoc_bin = pandoc_path or "pandoc"
    if shutil.which(pandoc_bin) is None:
        install_hint = {
            "Darwin": "brew install pandoc",
            "Windows": "choco install pandoc  或  winget install pandoc",
            "Linux": "sudo apt install pandoc  或  sudo dnf install pandoc",
        }.get(platform.system(), "請安裝 Pandoc")
        die(f"錯誤：找不到 Pandoc。請安裝：{install_hint}")

    # ── Google Drive 路徑 ──
    gdrive_cloud_path = detect_gdrive_cloud_path(google_drive_email)
    gdrive_base: Path | None = None
    if gdrive_cloud_path:
        gdrive_base = gdrive_cloud_path / google_drive_folder / "班級專案"

    # ── 上傳方式偵測 ──
    use_gws = check_gws_available()
    use_desktop = detect_gdrive_cloudstorge_dir(google_drive_email)

    if not use_gws and not use_desktop:
        die(
            "錯誤：找不到可用的 Google Drive 上傳方式。\n"
            "\n"
            "請選擇以下任一方式設定：\n"
            "\n"
            "  方式一（推薦）：安裝 Google Workspace CLI\n"
            "    npm install -g @googleworkspace/cli\n"
            "    gws auth login\n"
            "\n"
            "  方式二：安裝 Google Drive for Desktop\n"
            "    https://www.google.com/drive/download/\n"
            f"    安裝後以 {google_drive_email} 登入"
        )

    # ── 輸入檔案 ──
    input_rel = args.input
    input_path = repo_root / input_rel

    if not input_path.is_file():
        die(f"錯誤：找不到檔案 {input_path}")

    # ── 解析班級與科目（Front Matter 優先，路徑為備援）──
    class_fm = fm_value("class", input_path)
    subject_fm = fm_value("subject", input_path)

    # 路徑備援
    class_path_match = re.search(r"class-[0-9]+[a-z]+", input_rel)
    subject_path_match = re.search(r"(english|main-lesson|homeroom)", input_rel)

    class_id = class_fm or (class_path_match.group(0) if class_path_match else "")
    subject_id = subject_fm or (subject_path_match.group(0) if subject_path_match else "")

    class_src = "Front Matter" if class_fm else "路徑推斷"
    subj_src = "Front Matter" if subject_fm else "路徑推斷"

    if not class_id:
        die(
            "錯誤：無法識別班級。\n"
            "\n"
            "解決方式：在 Markdown 檔案最頂部加入 Front Matter，例如：\n"
            "  ---\n"
            "  class: class-9c\n"
            "  subject: english\n"
            "  ---\n"
            "\n"
            "目前支援的班級：class-9c / class-8a / class-7a"
        )

    if not subject_id:
        die(
            "錯誤：無法識別科目。\n"
            "\n"
            "解決方式：在 Markdown 檔案最頂部加入 Front Matter，例如：\n"
            "  ---\n"
            "  class: class-9c\n"
            "  subject: english\n"
            "  ---\n"
            "\n"
            "目前支援的科目：english / main-lesson / homeroom"
        )

    # ── 中文對照 ──
    class_cn = CLASS_CN_MAP.get(class_id, class_id)
    subject_cn = SUBJECT_CN_MAP.get(subject_id, subject_id)

    # ── 檔名與文件類型判斷 ──
    basename = input_path.stem  # 不含 .md

    version_match = re.search(r"(?i)v[0-9]+", basename)
    version = version_match.group(0).upper() if version_match else ""

    date_match = re.search(r"[0-9]{8}", basename)
    date_str = date_match.group(0) if date_match else ""

    unit_match = re.search(r"unit-([0-9]+)", basename)
    unit_num = int(unit_match.group(1)) if unit_match else None

    doc_folder = ""
    cn_filename = ""
    lower_base = basename.lower()

    if "syllabus" in lower_base:
        doc_folder = "教學大綱"
        cn_filename = f"教學大綱-{version}-{date_str}.docx"

    elif "unit" in lower_base:
        doc_folder = "單元教學"
        if unit_num is not None:
            cn_filename = f"第{cn_num(unit_num)}單元教學流程-{version}-{date_str}.docx"
        else:
            cn_filename = f"單元教學流程-{version}-{date_str}.docx"

    elif "task" in lower_base:
        doc_folder = "差異化任務"
        if unit_num is not None:
            cn_filename = f"第{cn_num(unit_num)}單元差異化任務-{version}-{date_str}.docx"
        else:
            cn_filename = f"差異化任務-{version}-{date_str}.docx"

    elif "assessment" in lower_base:
        doc_folder = "學習評量"
        cn_filename = f"學習評量-{date_str}.docx"

    elif any(kw in lower_base for kw in ("log", "record", "reflection")):
        doc_folder = "教學紀錄"
        cn_filename = f"{basename}.docx"

    elif "notice" in lower_base:
        doc_folder = "親師溝通"
        cn_filename = f"班親會通知-{version}-{date_str}.docx"

    elif "season-plan" in lower_base or "plan" in lower_base:
        doc_folder = "班級計畫"
        cn_filename = f"學季計畫-{version}-{date_str}.docx"

    elif "activity" in lower_base:
        doc_folder = "班級活動"
        cn_filename = f"活動紀錄-{version}-{date_str}.docx"

    else:
        doc_folder = ""
        cn_filename = f"{basename}.docx"

    # ── 路徑計算 ──
    subfolder_part = f"/{doc_folder}" if doc_folder else ""
    display_path = f"{google_drive_folder}/班級專案/{class_cn}/{subject_cn}{subfolder_part}/"

    gws_folder_path = f"{google_drive_folder}/班級專案/{class_cn}/{subject_cn}"
    if doc_folder:
        gws_folder_path += f"/{doc_folder}"

    # ── 輸出摘要 ──
    print()
    print("── TeacherOS 輸出 ──────────────────────────────")
    print(f"使用者  ：{user_name}")
    print(f"來源    ：{input_rel}")
    print(f"班級    ：{class_cn}（{class_src}）　科目：{subject_cn}（{subj_src}）")
    print(f"目標    ：Google Drive / {display_path}")
    print(f"檔名    ：{cn_filename}")
    if args.dry_run:
        print("模式    ：--dry-run（模擬執行）")
    print("────────────────────────────────────────────────")

    # ── Step 1：Pandoc 轉換 ──
    temp_dir = Path(tempfile.gettempdir())
    temp_docx = temp_dir / f"teacheros-{int(time.time())}-{cn_filename}"

    if args.dry_run:
        print(f"\n  [dry-run] Pandoc 轉換：{input_path} → {temp_docx}")
    else:
        try:
            subprocess.run(
                [pandoc_bin, str(input_path), "--from", "markdown", "--to", "docx", "-o", str(temp_docx)],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            die(f"錯誤：Pandoc 轉換失敗（exit code {e.returncode}）")

    # ── Step 2：上傳 ──
    upload_success = False
    upload_msg = ""

    if use_gws:
        ok, msg = gws_upload(temp_docx, gws_folder_path, cn_filename, dry_run=args.dry_run)
        if ok:
            upload_success = True
            upload_msg = msg
        elif use_desktop and gdrive_base:
            # GWS 失敗，嘗試 Desktop 備案
            ok2, msg2 = gdrive_desktop_copy(
                temp_docx, gdrive_base, class_cn, subject_cn,
                doc_folder, cn_filename, display_path, dry_run=args.dry_run,
            )
            if ok2:
                upload_success = True
                upload_msg = msg2
    elif use_desktop and gdrive_base:
        ok, msg = gdrive_desktop_copy(
            temp_docx, gdrive_base, class_cn, subject_cn,
            doc_folder, cn_filename, display_path, dry_run=args.dry_run,
        )
        if ok:
            upload_success = True
            upload_msg = msg

    # 清理暫存
    if temp_docx.is_file() and not args.dry_run:
        temp_docx.unlink()

    if not upload_success:
        die("錯誤：上傳失敗。請確認 Google Drive 連線狀態。")

    print(upload_msg)
    print()


if __name__ == "__main__":
    main()
