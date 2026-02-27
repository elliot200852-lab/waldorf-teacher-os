#!/bin/bash
# TeacherOS 輸出腳本
# 用途：將 Repo 中的 .md 草稿轉換為 .docx，並自動放入 Google Drive
#
# 用法：
#   ./publish/build.sh <markdown檔案路徑> <班級> <科目>
#
# 範例：
#   ./publish/build.sh projects/class-9c/content/english/english-syllabus-v1-20260227.md class-9c english
#
# 如果不帶參數，腳本會引導你輸入。

set -e

GDRIVE_BASE="$HOME/Library/CloudStorage/GoogleDrive-elliot200852@gmail.com/我的雲端硬碟/00-01-TeacherOS-專案三層記憶/projects"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── 參數處理 ──────────────────────────────────────────────────

if [ -z "$1" ]; then
  echo "請輸入要輸出的 .md 檔案路徑（相對於 Repo 根目錄）："
  read -r INPUT_REL
else
  INPUT_REL="$1"
fi

INPUT="$REPO_ROOT/$INPUT_REL"

if [ ! -f "$INPUT" ]; then
  echo "錯誤：找不到檔案 $INPUT"
  exit 1
fi

if [ -z "$2" ]; then
  echo "請輸入班級代碼（class-9c / class-8a / class-7a）："
  read -r CLASS
else
  CLASS="$2"
fi

if [ -z "$3" ]; then
  echo "請輸入科目（english / main-lesson）："
  read -r SUBJECT
else
  SUBJECT="$3"
fi

# ── 路徑計算 ──────────────────────────────────────────────────

OUTPUT_DIR="$GDRIVE_BASE/$CLASS/$SUBJECT"
mkdir -p "$OUTPUT_DIR"

BASENAME=$(basename "$INPUT" .md)
OUTPUT_DOCX="$OUTPUT_DIR/$BASENAME.docx"

# ── 執行轉換 ──────────────────────────────────────────────────

echo ""
echo "── TeacherOS 輸出 ──────────────────────────────"
echo "來源：$INPUT_REL"
echo "目標：Google Drive / 00-01-TeacherOS-專案三層記憶 / projects / $CLASS / $SUBJECT"
echo "檔名：$BASENAME.docx"
echo "────────────────────────────────────────────────"
echo ""

pandoc "$INPUT" \
  --from markdown \
  --to docx \
  -o "$OUTPUT_DOCX"

echo "轉換完成。"
echo ""
echo "下一步："
echo "  1. 打開 Google Drive（網頁版），前往 00-01-TeacherOS-專案三層記憶/projects/$CLASS/$SUBJECT/"
echo "  2. 找到 $BASENAME.docx，右鍵 → 用 Google 文件開啟"
echo "  3. 即可分享或列印。"
echo ""
