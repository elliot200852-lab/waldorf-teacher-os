#!/bin/bash
# TeacherOS 輸出腳本
# 用途：將 .md 草稿轉換為 .docx，自動放入 Google Drive（本機資料夾同步）
#
# 用法（AI 直接呼叫，不需教師手動輸入）：
#   ./publish/build.sh <markdown檔案路徑>
#
# 班級與科目從路徑自動解析。帳號與路徑從 setup/environment.env 讀取。

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/setup/environment.env"

# ── 載入個人環境設定 ──────────────────────────────────────────

if [ ! -f "$ENV_FILE" ]; then
  echo "錯誤：找不到環境設定檔 setup/environment.env"
  echo "請依照 setup/environment.env.example 建立你的個人設定檔。"
  echo "執行：cp setup/environment.env.example setup/environment.env"
  exit 1
fi

source "$ENV_FILE"

# ── 驗證必要設定 ──────────────────────────────────────────────

if [ -z "$GOOGLE_DRIVE_EMAIL" ] || [ "$GOOGLE_DRIVE_EMAIL" = "你的帳號@gmail.com" ]; then
  echo "錯誤：setup/environment.env 中的 GOOGLE_DRIVE_EMAIL 尚未設定。"
  exit 1
fi

if [ -z "$GOOGLE_DRIVE_FOLDER" ]; then
  echo "錯誤：setup/environment.env 中的 GOOGLE_DRIVE_FOLDER 尚未設定。"
  exit 1
fi

PANDOC_BIN="${PANDOC_PATH:-pandoc}"
if ! command -v "$PANDOC_BIN" &>/dev/null; then
  echo "錯誤：找不到 Pandoc。請安裝：brew install pandoc"
  exit 1
fi

GDRIVE_BASE="$HOME/Library/CloudStorage/GoogleDrive-${GOOGLE_DRIVE_EMAIL}/我的雲端硬碟/${GOOGLE_DRIVE_FOLDER}/projects"

if [ ! -d "$HOME/Library/CloudStorage/GoogleDrive-${GOOGLE_DRIVE_EMAIL}" ]; then
  echo "錯誤：找不到 Google Drive 本機資料夾。"
  echo "請確認 Google Drive for Desktop 已安裝並以 ${GOOGLE_DRIVE_EMAIL} 登入。"
  exit 1
fi

# ── 參數處理 ──────────────────────────────────────────────────

if [ -z "$1" ]; then
  echo "錯誤：請提供 .md 檔案路徑。"
  echo "用法：./publish/build.sh <markdown檔案路徑>"
  exit 1
fi

INPUT_REL="$1"
INPUT="$REPO_ROOT/$INPUT_REL"

if [ ! -f "$INPUT" ]; then
  echo "錯誤：找不到檔案 $INPUT"
  exit 1
fi

# ── 從路徑自動解析班級與科目 ─────────────────────────────────

CLASS=$(echo "$INPUT_REL" | grep -oE 'class-[0-9]+[a-z]+' | head -1)
SUBJECT=$(echo "$INPUT_REL" | grep -oE 'english|main-lesson' | head -1)

if [ -z "$CLASS" ]; then
  echo "錯誤：無法從路徑解析班級（需包含 class-9c / class-8a / class-7a）"
  exit 1
fi

if [ -z "$SUBJECT" ]; then
  echo "錯誤：無法從路徑解析科目（需包含 english / main-lesson）"
  exit 1
fi

# ── 路徑計算與執行 ────────────────────────────────────────────

OUTPUT_DIR="$GDRIVE_BASE/$CLASS/$SUBJECT"
mkdir -p "$OUTPUT_DIR"

BASENAME=$(basename "$INPUT" .md)
OUTPUT_DOCX="$OUTPUT_DIR/$BASENAME.docx"

echo ""
echo "── TeacherOS 輸出 ──────────────────────────────"
echo "使用者  ：${USER_NAME:-未設定}"
echo "來源    ：$INPUT_REL"
echo "班級    ：$CLASS　科目：$SUBJECT"
echo "目標    ：Google Drive / ${GOOGLE_DRIVE_FOLDER}/projects/$CLASS/$SUBJECT/"
echo "檔名    ：$BASENAME.docx"
echo "────────────────────────────────────────────────"

"$PANDOC_BIN" "$INPUT" --from markdown --to docx -o "$OUTPUT_DOCX"

echo "完成。Google Drive Desktop 將自動同步。"
echo "雲端路徑：${GOOGLE_DRIVE_FOLDER}/projects/$CLASS/$SUBJECT/$BASENAME.docx"
echo ""
