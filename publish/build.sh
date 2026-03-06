#!/bin/bash
# TeacherOS 輸出腳本
# 用途：將 .md 草稿轉換為 .docx，上傳至 Google Drive
# 上傳方式：GWS CLI 優先 → Google Drive Desktop 備案（無縫切換，使用者無感）
# 輸出資料夾與檔名皆使用繁體中文，版本號保留 V1/V2 格式。
#
# 用法（AI 直接呼叫，不需教師手動輸入）：
#   ./publish/build.sh <markdown檔案路徑>
#
# 班級與科目解析優先順序：
#   1. Markdown 檔案頂部 Front Matter（class: / subject: 欄位）
#   2. 備援：從檔案路徑自動推斷
#   3. 兩者皆失敗 → 輸出說明並終止
#
# 帳號與路徑從 setup/environment.env 讀取。

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

# ── 上傳方式偵測（GWS CLI 優先，Google Drive Desktop 備案）────
# 邏輯：先嘗試 GWS CLI，若未安裝或未登入則無縫切換到 Google Drive Desktop。
# 使用者無需知道背後使用哪種方式。

USE_GWS_UPLOAD=false
USE_GDRIVE_DESKTOP=false

if command -v gws &>/dev/null && gws auth status &>/dev/null 2>&1; then
  USE_GWS_UPLOAD=true
elif [ -d "$HOME/Library/CloudStorage/GoogleDrive-${GOOGLE_DRIVE_EMAIL}" ]; then
  USE_GDRIVE_DESKTOP=true
else
  echo "錯誤：找不到可用的 Google Drive 上傳方式。"
  echo ""
  echo "請選擇以下任一方式設定："
  echo ""
  echo "  方式一（推薦）：安裝 Google Workspace CLI"
  echo "    npm install -g @googleworkspace/cli"
  echo "    gws auth login"
  echo ""
  echo "  方式二：安裝 Google Drive for Desktop"
  echo "    https://www.google.com/drive/download/"
  echo "    安裝後以 ${GOOGLE_DRIVE_EMAIL} 登入"
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

# ── 解析班級與科目（Front Matter 優先，路徑為備援）─────────────

# Front Matter 讀取輔助函式
# 讀取 Markdown 檔案開頭 --- 區塊中的指定 key 值
fm_value() {
  local key="$1"
  local file="$2"
  awk 'BEGIN{f=0} /^---/{f++; next} f==1{print} f>=2{exit}' "$file" \
    | grep "^${key}:" | head -1 \
    | sed "s/^${key}:[[:space:]]*//" | tr -d "'\""
}

# Step 1：優先從 Front Matter 讀取
CLASS_FM=$(fm_value "class" "$INPUT")
SUBJECT_FM=$(fm_value "subject" "$INPUT")

# Step 2：若 Front Matter 缺失，從路徑備援推斷
CLASS_PATH=$(echo "$INPUT_REL" | grep -oE 'class-[0-9]+[a-z]+' | head -1)
SUBJECT_PATH=$(echo "$INPUT_REL" | grep -oE 'english|main-lesson|homeroom' | head -1)

CLASS="${CLASS_FM:-$CLASS_PATH}"
SUBJECT="${SUBJECT_FM:-$SUBJECT_PATH}"

# 來源標記（供輸出訊息顯示）
[[ -n "$CLASS_FM" ]]   && CLASS_SRC="Front Matter" || CLASS_SRC="路徑推斷"
[[ -n "$SUBJECT_FM" ]] && SUBJ_SRC="Front Matter"  || SUBJ_SRC="路徑推斷"

# Step 3：失敗保護——兩種方式都無法取得時終止並給出說明
if [ -z "$CLASS" ]; then
  echo "錯誤：無法識別班級。"
  echo ""
  echo "解決方式：在 Markdown 檔案最頂部加入 Front Matter，例如："
  echo "  ---"
  echo "  class: class-9c"
  echo "  subject: english"
  echo "  ---"
  echo ""
  echo "目前支援的班級：class-9c / class-8a / class-7a"
  exit 1
fi

if [ -z "$SUBJECT" ]; then
  echo "錯誤：無法識別科目。"
  echo ""
  echo "解決方式：在 Markdown 檔案最頂部加入 Front Matter，例如："
  echo "  ---"
  echo "  class: class-9c"
  echo "  subject: english"
  echo "  ---"
  echo ""
  echo "目前支援的科目：english / main-lesson / homeroom"
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

DISPLAY_PATH="${GOOGLE_DRIVE_FOLDER}/班級專案/$CLASS_CN/$SUBJECT_CN${DOC_FOLDER:+/$DOC_FOLDER}/"

# 先輸出至本機暫存，避免 Google Drive Desktop 的 Stale file handle 問題
TEMP_DOCX="/tmp/teacheros-$(date +%s)-${CN_FILENAME}"

echo ""
echo "── TeacherOS 輸出 ──────────────────────────────"
echo "使用者  ：${USER_NAME:-未設定}"
echo "來源    ：$INPUT_REL"
echo "班級    ：$CLASS_CN（$CLASS_SRC）　科目：$SUBJECT_CN（$SUBJ_SRC）"
echo "目標    ：Google Drive / $DISPLAY_PATH"
echo "檔名    ：$CN_FILENAME"
echo "────────────────────────────────────────────────"

# Step 1：Pandoc 轉換至暫存路徑
"$PANDOC_BIN" "$INPUT" --from markdown --to docx -o "$TEMP_DOCX"

# Step 2：上傳至 Google Drive
#   首選：GWS CLI 直接上傳
#   備案：Google Drive Desktop 本機同步
#   若 GWS CLI 上傳失敗，自動嘗試 Desktop 備案（如有）

gws_upload() {
  # 確保雲端資料夾存在（以 GOOGLE_DRIVE_FOLDER 為根目錄）
  GWS_FOLDER_PATH="${GOOGLE_DRIVE_FOLDER}/班級專案/${CLASS_CN}/${SUBJECT_CN}"
  if [ -n "$DOC_FOLDER" ]; then
    GWS_FOLDER_PATH="${GWS_FOLDER_PATH}/${DOC_FOLDER}"
  fi

  # 查詢或建立資料夾（逐層）
  PARENT_ID="root"
  IFS='/' read -ra FOLDER_PARTS <<< "$GWS_FOLDER_PATH"
  for PART in "${FOLDER_PARTS[@]}"; do
    FOLDER_RESULT=$(gws drive files list --params "{\"q\": \"name='${PART}' and '${PARENT_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false\", \"pageSize\": 1}" 2>/dev/null)
    FOLDER_ID=$(echo "$FOLDER_RESULT" | grep -o '"id": *"[^"]*"' | head -1 | sed 's/"id": *"//;s/"//')

    if [ -z "$FOLDER_ID" ]; then
      CREATE_RESULT=$(gws drive files create --json "{\"name\": \"${PART}\", \"mimeType\": \"application/vnd.google-apps.folder\", \"parents\": [\"${PARENT_ID}\"]}" 2>/dev/null)
      FOLDER_ID=$(echo "$CREATE_RESULT" | grep -o '"id": *"[^"]*"' | head -1 | sed 's/"id": *"//;s/"//')
    fi

    if [ -n "$FOLDER_ID" ]; then
      PARENT_ID="$FOLDER_ID"
    else
      return 1
    fi
  done

  # 上傳檔案
  UPLOAD_RESULT=$(gws drive files create \
    --params "{\"parents\": [\"${PARENT_ID}\"]}" \
    --json "{\"name\": \"${CN_FILENAME}\"}" \
    --upload "$TEMP_DOCX" 2>/dev/null)

  FILE_ID=$(echo "$UPLOAD_RESULT" | grep -o '"id": *"[^"]*"' | head -1 | sed 's/"id": *"//;s/"//')
  if [ -n "$FILE_ID" ]; then
    echo "完成。已上傳至 Google Drive。"
    echo "雲端路徑：${GWS_FOLDER_PATH}/${CN_FILENAME}"
    echo "檔案連結：https://drive.google.com/file/d/${FILE_ID}"
    return 0
  else
    return 1
  fi
}

gdrive_desktop_copy() {
  if [ -d "$HOME/Library/CloudStorage/GoogleDrive-${GOOGLE_DRIVE_EMAIL}" ]; then
    if [ -n "$DOC_FOLDER" ]; then
      OUTPUT_DIR="$GDRIVE_BASE/$CLASS_CN/$SUBJECT_CN/$DOC_FOLDER"
    else
      OUTPUT_DIR="$GDRIVE_BASE/$CLASS_CN/$SUBJECT_CN"
    fi
    mkdir -p "$OUTPUT_DIR"
    OUTPUT_DOCX="$OUTPUT_DIR/$CN_FILENAME"
    rm -f "$OUTPUT_DOCX" 2>/dev/null || true
    cp "$TEMP_DOCX" "$OUTPUT_DOCX"
    echo "完成。Google Drive Desktop 將自動同步。"
    echo "雲端路徑：${DISPLAY_PATH}${CN_FILENAME}"
    return 0
  else
    return 1
  fi
}

UPLOAD_SUCCESS=false

if [ "$USE_GWS_UPLOAD" = true ]; then
  if gws_upload; then
    UPLOAD_SUCCESS=true
  else
    # GWS CLI 失敗，嘗試 Desktop 備案
    if gdrive_desktop_copy; then
      UPLOAD_SUCCESS=true
    fi
  fi
elif [ "$USE_GDRIVE_DESKTOP" = true ]; then
  if gdrive_desktop_copy; then
    UPLOAD_SUCCESS=true
  fi
fi

rm -f "$TEMP_DOCX"

if [ "$UPLOAD_SUCCESS" = false ]; then
  echo "錯誤：上傳失敗。請確認 Google Drive 連線狀態。"
  exit 1
fi

echo ""
