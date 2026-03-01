#!/bin/bash
# TeacherOS 輸出腳本
# 用途：將 .md 草稿轉換為 .docx，自動放入 Google Drive（本機資料夾同步）
# 輸出資料夾與檔名皆使用繁體中文，版本號保留 V1/V2 格式。
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

GDRIVE_ROOT="$HOME/Library/CloudStorage/GoogleDrive-${GOOGLE_DRIVE_EMAIL}/我的雲端硬碟/${GOOGLE_DRIVE_FOLDER}"
GDRIVE_BASE="$GDRIVE_ROOT/班級專案"

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
SUBJECT=$(echo "$INPUT_REL" | grep -oE 'english|main-lesson|homeroom' | head -1)

if [ -z "$CLASS" ]; then
  echo "錯誤：無法從路徑解析班級（需包含 class-9c / class-8a / class-7a）"
  exit 1
fi

if [ -z "$SUBJECT" ]; then
  echo "錯誤：無法從路徑解析科目（需包含 english / main-lesson / homeroom）"
  exit 1
fi

# ── 班級與科目中文對照 ────────────────────────────────────────

case "$CLASS" in
  class-9c) CLASS_CN="九年級C班" ;;
  class-8a) CLASS_CN="八年級A班" ;;
  class-7a) CLASS_CN="七年級A班" ;;
  *) CLASS_CN="$CLASS" ;;
esac

case "$SUBJECT" in
  english) SUBJECT_CN="英文" ;;
  main-lesson) SUBJECT_CN="主課程" ;;
  homeroom) SUBJECT_CN="導師" ;;
  *) SUBJECT_CN="$SUBJECT" ;;
esac

# ── 中文數字輔助函式 ──────────────────────────────────────────

cn_num() {
  case "$1" in
    1) echo "一" ;; 2) echo "二" ;; 3) echo "三" ;;
    4) echo "四" ;; 5) echo "五" ;; 6) echo "六" ;;
    7) echo "七" ;; 8) echo "八" ;; 9) echo "九" ;;
    10) echo "十" ;; *) echo "$1" ;;
  esac
}

# ── 依檔名判斷文件類型、資料夾與中文檔名 ─────────────────────

BASENAME=$(basename "$INPUT" .md)
VERSION=$(echo "$BASENAME" | grep -oiE 'v[0-9]+' | head -1 | tr '[:lower:]' '[:upper:]')
DATE=$(echo "$BASENAME" | grep -oE '[0-9]{8}' | head -1)
UNIT_NUM=$(echo "$BASENAME" | grep -oE 'unit-[0-9]+' | grep -oE '[0-9]+' | head -1)

if [[ "$BASENAME" == *syllabus* ]]; then
  DOC_FOLDER="教學大綱"
  CN_FILENAME="教學大綱-${VERSION}-${DATE}.docx"

elif [[ "$BASENAME" == *unit* ]]; then
  DOC_FOLDER="單元教學"
  if [ -n "$UNIT_NUM" ]; then
    UNIT_CN=$(cn_num "$UNIT_NUM")
    CN_FILENAME="第${UNIT_CN}單元教學流程-${VERSION}-${DATE}.docx"
  else
    CN_FILENAME="單元教學流程-${VERSION}-${DATE}.docx"
  fi

elif [[ "$BASENAME" == *task* ]]; then
  DOC_FOLDER="差異化任務"
  if [ -n "$UNIT_NUM" ]; then
    UNIT_CN=$(cn_num "$UNIT_NUM")
    CN_FILENAME="第${UNIT_CN}單元差異化任務-${VERSION}-${DATE}.docx"
  else
    CN_FILENAME="差異化任務-${VERSION}-${DATE}.docx"
  fi

elif [[ "$BASENAME" == *assessment* ]]; then
  DOC_FOLDER="學習評量"
  CN_FILENAME="學習評量-${DATE}.docx"

elif [[ "$BASENAME" == *log* ]] || [[ "$BASENAME" == *record* ]] || [[ "$BASENAME" == *reflection* ]]; then
  DOC_FOLDER="教學紀錄"
  CN_FILENAME="${BASENAME}.docx"

elif [[ "$BASENAME" == *notice* ]]; then
  DOC_FOLDER="親師溝通"
  CN_FILENAME="班親會通知-${VERSION}-${DATE}.docx"

elif [[ "$BASENAME" == *season-plan* ]] || [[ "$BASENAME" == *plan* ]]; then
  DOC_FOLDER="班級計畫"
  CN_FILENAME="學季計畫-${VERSION}-${DATE}.docx"

elif [[ "$BASENAME" == *activity* ]]; then
  DOC_FOLDER="班級活動"
  CN_FILENAME="活動紀錄-${VERSION}-${DATE}.docx"

else
  DOC_FOLDER=""
  CN_FILENAME="${BASENAME}.docx"
fi

# ── 路徑計算與執行 ────────────────────────────────────────────

if [ -n "$DOC_FOLDER" ]; then
  OUTPUT_DIR="$GDRIVE_BASE/$CLASS_CN/$SUBJECT_CN/$DOC_FOLDER"
else
  OUTPUT_DIR="$GDRIVE_BASE/$CLASS_CN/$SUBJECT_CN"
fi
mkdir -p "$OUTPUT_DIR"

OUTPUT_DOCX="$OUTPUT_DIR/$CN_FILENAME"
DISPLAY_PATH="${GOOGLE_DRIVE_FOLDER}/班級專案/$CLASS_CN/$SUBJECT_CN${DOC_FOLDER:+/$DOC_FOLDER}/"

# 先輸出至本機暫存，避免 Google Drive Desktop 的 Stale file handle 問題
TEMP_DOCX="/tmp/teacheros-$(date +%s)-${CN_FILENAME}"

echo ""
echo "── TeacherOS 輸出 ──────────────────────────────"
echo "使用者  ：${USER_NAME:-未設定}"
echo "來源    ：$INPUT_REL"
echo "班級    ：$CLASS_CN　科目：$SUBJECT_CN"
echo "目標    ：Google Drive / $DISPLAY_PATH"
echo "檔名    ：$CN_FILENAME"
echo "────────────────────────────────────────────────"

# Step 1：Pandoc 轉換至暫存路徑
"$PANDOC_BIN" "$INPUT" --from markdown --to docx -o "$TEMP_DOCX"

# Step 2：加入識別 Logo（圓形去背、頁首右上角）
LOGO_SCRIPT="$REPO_ROOT/setup/add-logo.py"
if [ -f "$LOGO_SCRIPT" ]; then
  python3 "$LOGO_SCRIPT" "$TEMP_DOCX"
fi

# Step 3：複製至 Google Drive 資料夾
# 先移除舊檔，避免 Google Drive Desktop 的 Stale NFS file handle 問題
mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DOCX" 2>/dev/null || true
cp "$TEMP_DOCX" "$OUTPUT_DOCX"
rm -f "$TEMP_DOCX"

echo "完成。Google Drive Desktop 將自動同步。"
echo "雲端路徑：${DISPLAY_PATH}${CN_FILENAME}"
echo ""
