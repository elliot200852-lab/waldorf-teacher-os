#!/usr/bin/env python3
"""
TeacherOS — 批次轉換所有 .md 為 .docx，放入 Google Drive DocReviewBackup
同時產出 CSV 檔案清單（含 GitHub 連結）
檔名格式：中文名稱_原始檔名.docx（已有中文名的直接保留）
"""

import os
import shutil
import subprocess
import csv
import sys
import re
from pathlib import Path
from urllib.parse import quote

# ── 設定 ──────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
PANDOC = shutil.which("pandoc") or "/opt/homebrew/bin/pandoc"

# 從 environment.env 讀取 email，未設定時用預設值
_env_file = REPO_ROOT / "setup" / "environment.env"
GDRIVE_EMAIL = "elliot200852@gmail.com"
GDRIVE_FOLDER = "00-01-TeacherOS-專案三層記憶"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line.startswith("GOOGLE_DRIVE_EMAIL="):
            _val = _line.split("=", 1)[1].strip().strip("'\"")
            if _val and _val != "你的帳號@gmail.com":
                GDRIVE_EMAIL = _val
        elif _line.startswith("GOOGLE_DRIVE_FOLDER="):
            _val = _line.split("=", 1)[1].strip().strip("'\"")
            if _val:
                GDRIVE_FOLDER = _val
GITHUB_BASE = "https://github.com/elliot200852-lab/waldorf-teacher-os/blob/main"

import platform as _platform
import tempfile as _tempfile
if _platform.system() == "Windows":
    GDRIVE_ROOT = Path.home() / "G:" / "我的雲端硬碟" / GDRIVE_FOLDER  # Windows default
else:
    GDRIVE_ROOT = Path.home() / "Library/CloudStorage" / f"GoogleDrive-{GDRIVE_EMAIL}" / "我的雲端硬碟" / GDRIVE_FOLDER
BACKUP_DIR = GDRIVE_ROOT / "DocReviewBackup"

EXCLUDE_DIRS = {".git", "node_modules", ".claude", "publish"}

# ── 中文檔名對照表 ────────────────────────────────────────
# 規則：原始檔名 → 中文前綴
# 已含中文的檔名不需要加前綴，設為 None
CN_NAME_MAP = {
    # ai-core 根目錄
    "AI_HANDOFF.md": "AI入口",
    "skills-manifest.md": "技能索引",

    # ai-core/skills
    "block-end.md": "區塊結束",
    "di-check.md": "DI檢查",
    "homeroom.md": "導師業務",
    "lesson.md": "課程設計",
    "load.md": "脈絡載入",
    "parent-letter.md": "家長信",
    "pull-request.md": "合併申請",
    "ref.md": "參考載入",
    "rhythm.md": "課堂節奏",
    "save.md": "存檔",
    "session-end.md": "對話收尾",
    "status.md": "狀態查詢",
    "student-note.md": "學生觀察",
    "syllabus.md": "教學大綱",

    # ai-core/reviews
    "context-review-20260228.md": "脈絡回顧",
    "session-log.md": "工作紀錄",

    # projects/_di-framework/content
    "108-curriculum-language-reference.md": "108課綱語文參考",
    "di-classification-guide.md": "DI分類指引",
    "english-di-block1.md": "英文DI區塊一",
    "english-di-block2.md": "英文DI區塊二",
    "english-di-block3.md": "英文DI區塊三",
    "english-di-block4.md": "英文DI區塊四",
    "english-di-template.md": "英文DI總模板",
    "homeroom-template.md": "導師業務模板",
    "strategy-output-quality-standard.md": "策略產出品質標準",
    "student-knowledge-protocol.md": "學生知識庫協議",
    "system-logic-map.md": "系統邏輯關聯圖",

    # projects/_di-framework/reference
    "block1-output-example-draft.md": "區塊一產出範例",
    "strategy-analysis-quality-example.md": "策略分析品質範例",

    # setup
    "teacher-guide.md": "教師使用手冊",

    # workspaces
    "CHANGELOG_v7_20260303.md": "版本更新紀錄V7",

    # 英文教學產出（需結合路徑判斷，在函式中處理）
    "english-syllabus-v1-20260228.md": "英文教學大綱V1",
    "english-syllabus-v2-20260301.md": "英文教學大綱V2",
    "english-syllabus-v1-20260303.md": "英文教學大綱V1",
    "english-unit-1-v1-20260303.md": "英文第一單元V1",
    "english-units-2-4-v1-20260303.md": "英文第二至四單元V1",
    "student-assessments-20260510.md": "學生評量",
    "teacher-term-report-20260510.md": "教師學期報告",
    "sample-logs.md": "學生觀察紀錄範例",
    "teacher-reflections.md": "教師反思紀錄",
    "unit-logs.md": "單元教學紀錄",
    "index.md": "索引",
    "calendar.md": "行事曆",

    # 導師通知
    "homeroom-notice-v1-20260301.md": "班親會通知V1",
    "homeroom-notice-v2-20260301.md": "班親會通知V2",
}

# README 特殊處理：依所在資料夾給中文名
README_CN = {
    "ai-core/skills": "技能總說明",
    "workspaces": "工作區說明",
    "workspaces/_template": "模板說明",
    "workspaces/Working_Member/Codeowner_David/projects/class-9c/english/content": "9C英文內容說明",
}


def has_chinese(text: str) -> bool:
    """檢查字串是否已含中文字元"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def get_cn_docx_name(rel_path: str) -> str:
    """產出中文在前的 .docx 檔名"""
    filename = Path(rel_path).name
    stem = Path(filename).stem
    parent_dir = str(Path(rel_path).parent)

    # README 特殊處理
    if filename == "README.md":
        cn = README_CN.get(parent_dir, "說明")
        return f"{cn}_README.docx"

    # 已含中文的檔名：直接換副檔名
    if has_chinese(stem):
        return f"{stem}.docx"

    # 查對照表
    cn_prefix = CN_NAME_MAP.get(filename)
    if cn_prefix:
        # 加上路徑中的班級前綴（避免重複檔名）
        class_prefix = ""
        if "class-9c" in rel_path:
            class_prefix = "9C"
        elif "class-claude" in rel_path:
            class_prefix = "範例"

        # 加上 homeroom 前綴
        if "homeroom" in rel_path and not cn_prefix.startswith("導師"):
            class_prefix += "導師"

        if class_prefix and not cn_prefix.startswith(class_prefix):
            cn_prefix = f"{class_prefix}{cn_prefix}"

        return f"{cn_prefix}_{stem}.docx"

    # 都沒有匹配：保留原始檔名
    return f"{stem}.docx"


# ── 分類規則 ──────────────────────────────────────────────
def classify_file(rel_path: str) -> tuple[str, str]:
    """回傳 (分類, 類型)"""
    parts = rel_path.split("/")

    if parts[0] == "ai-core":
        if "skills" in parts and parts[-1] != "skills-manifest.md":
            return "系統技能", "技能"
        if "reviews" in parts:
            return "回顧紀錄", "回顧"
        if "reference" in parts:
            return "參考模組", "參考"
        if "AI_HANDOFF" in rel_path:
            return "系統核心", "入口文件"
        if "skills-manifest" in rel_path:
            return "系統核心", "技能索引"
        return "系統核心", "核心文件"

    if parts[0] == "projects":
        if "_di-framework" in parts:
            if "reference" in parts:
                return "DI框架參考", "參考範例"
            if "content" in parts:
                return "DI框架模板", "模板"
            return "DI框架", "框架"
        return "專案", "專案文件"

    if parts[0] == "workspaces":
        if "工作範例參考" in rel_path:
            if "records" in rel_path:
                return "範例參考/紀錄", "範例"
            return "範例參考", "範例"
        if "Codeowner_David" in rel_path:
            if "reference" in parts:
                return "David/教學參考", "參考"
            if "homeroom" in parts:
                return "David/導師業務", "導師"
            if "content" in parts:
                return "David/教學產出", "教學產出"
            return "David/工作區", "工作區"
        if "_template" in rel_path:
            return "工作區模板", "模板"
        return "工作區", "工作區"

    if parts[0] == "Engineer_Reference":
        return "工程參考", "版本紀錄"

    if parts[0] == "setup":
        return "安裝指引", "指引"

    return "根目錄", "其他"


def main():
    # ── 掃描所有 .md ──────────────────────────────────────
    md_files = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(".md"):
                full_path = Path(root) / f
                rel_path = str(full_path.relative_to(REPO_ROOT))
                md_files.append((rel_path, full_path))

    md_files.sort(key=lambda x: x[0])
    print(f"找到 {len(md_files)} 個 .md 檔案")

    if not os.path.exists(PANDOC):
        print(f"錯誤：找不到 Pandoc: {PANDOC}")
        sys.exit(1)

    # ── 清除舊的 DocReviewBackup 內容 ─────────────────────
    import shutil
    if BACKUP_DIR.exists():
        for item in BACKUP_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            elif item.suffix in ('.docx', '.csv'):
                item.unlink()
        print("已清除舊的 DocReviewBackup 內容")

    # ── 批次轉換 ──────────────────────────────────────────
    success = 0
    failed = []
    csv_rows = []

    for rel_path, full_path in md_files:
        # 中文檔名
        cn_docx_name = get_cn_docx_name(rel_path)

        # 保留目錄結構
        docx_subdir = BACKUP_DIR / Path(rel_path).parent
        docx_path = docx_subdir / cn_docx_name

        docx_subdir.mkdir(parents=True, exist_ok=True)

        # Pandoc 轉換
        tmp_path = Path(_tempfile.gettempdir()) / f"teacheros-batch-{cn_docx_name}"
        try:
            subprocess.run(
                [PANDOC, str(full_path), "--from", "markdown", "--to", "docx", "-o", str(tmp_path)],
                check=True, capture_output=True, text=True
            )
            if docx_path.exists():
                docx_path.unlink()
            subprocess.run(["cp", str(tmp_path), str(docx_path)], check=True)
            tmp_path.unlink(missing_ok=True)
            success += 1
            status = "完成"
            print(f"  [OK] {cn_docx_name}")
        except subprocess.CalledProcessError as e:
            failed.append(rel_path)
            status = "失敗"
            print(f"  [失敗] {rel_path}: {e.stderr[:100]}")

        # 分類
        category, file_type = classify_file(rel_path)

        # GitHub 連結
        github_url = f"{GITHUB_BASE}/{quote(rel_path)}"

        # DocReviewBackup 中的相對路徑
        docx_rel = str(Path(rel_path).parent / cn_docx_name)

        csv_rows.append({
            "中文檔名": cn_docx_name.replace(".docx", ""),
            "原始檔名": Path(rel_path).stem,
            "分類": category,
            "類型": file_type,
            "GitHub 連結": github_url,
            "Repo 路徑": rel_path,
            "DocReview 路徑": docx_rel,
            "轉換狀態": status,
            "審閱狀態": "",
            "備註": ""
        })

    print(f"\n轉換完成：{success} 成功，{len(failed)} 失敗")
    if failed:
        print("失敗檔案：")
        for f in failed:
            print(f"  - {f}")

    # ── 產出 CSV ──────────────────────────────────────────
    csv_path = BACKUP_DIR / "DocReview-檔案清單.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "中文檔名", "原始檔名", "分類", "類型",
            "GitHub 連結", "Repo 路徑", "DocReview 路徑",
            "轉換狀態", "審閱狀態", "備註"
        ])
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"\nCSV 已輸出：{csv_path}")
    print(f"共 {len(csv_rows)} 筆記錄")


if __name__ == "__main__":
    main()
