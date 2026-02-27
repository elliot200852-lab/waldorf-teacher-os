#!/bin/bash
# TeacherOS 輸出腳本
# 用途：將 .md 草稿轉換為 .docx，自動放入 Google Drive（本機資料夾同步）
#
# 用法（AI 直接呼叫，不需教師手動輸入）：
#   ./publish/build.sh <markdown檔案路徑>
#
# 班級與科目從路徑自動解析，無需額外參數。
# 範例路徑：projects/class-9c/content/english/english-syllabus-v1-20260227.md

set -e

GDRIVE_BASE="$HOME/Library/CloudStorage/GoogleDrive-elliot200852@gmail.com/我的雲端硬碟/00-01-TeacherOS-專案三層記憶/projects"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

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
echo "來源  ：$INPUT_REL"
echo "班級  ：$CLASS　科目：$SUBJECT"
echo "目標  ：Google Drive / projects/$CLASS/$SUBJECT/"
echo "檔名  ：$BASENAME.docx"
echo "────────────────────────────────────────────────"

pandoc "$INPUT" --from markdown --to docx -o "$OUTPUT_DOCX"

echo "完成。Google Drive Desktop 將自動同步。"
echo "雲端路徑：00-01-TeacherOS-專案三層記憶/projects/$CLASS/$SUBJECT/$BASENAME.docx"
echo ""
