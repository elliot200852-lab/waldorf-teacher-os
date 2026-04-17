#!/bin/bash
# TeacherOS 環境檢查腳本
# 用途：新老師第一次使用時，確認所有必要環境是否就緒
# 執行：bash setup/setup-check.sh

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/setup/environment.env"

PASS=0
FAIL=0

check_pass() { echo "  [OK]  $1"; PASS=$((PASS+1)); }
check_fail() { echo "  [!!]  $1"; FAIL=$((FAIL+1)); }
section()    { echo ""; echo "── $1 ──────────────────────────────────────────"; }

# ── OS 偵測 ───────────────────────────────────────────────────

IS_WSL=false
case "$(uname -s)" in
  Darwin*)               OS_TYPE="macos" ;;
  Linux*)
    OS_TYPE="linux"
    if grep -qi microsoft /proc/version 2>/dev/null; then
      IS_WSL=true
    fi
    ;;
  MINGW*|MSYS*|CYGWIN*)  OS_TYPE="windows" ;;
  *)                     OS_TYPE="unknown" ;;
esac

echo ""
echo "════════════════════════════════════════════════"
if [ "$IS_WSL" = true ]; then
  echo "  TeacherOS 環境檢查（linux / WSL2）"
else
  echo "  TeacherOS 環境檢查（$OS_TYPE）"
fi
echo "════════════════════════════════════════════════"

# ── 1. 個人設定檔 ─────────────────────────────────────────────

section "1. 個人設定檔"

if [ -f "$ENV_FILE" ]; then
  check_pass "setup/environment.env 存在"
  source "$ENV_FILE"

  if [ -n "$USER_NAME" ] && [ "$USER_NAME" != "你的姓名" ]; then
    check_pass "USER_NAME 已設定：$USER_NAME"
  else
    check_fail "USER_NAME 尚未設定（請修改 setup/environment.env）"
  fi

  if [ -n "$GOOGLE_DRIVE_EMAIL" ] && [ "$GOOGLE_DRIVE_EMAIL" != "你的帳號@gmail.com" ]; then
    check_pass "GOOGLE_DRIVE_EMAIL 已設定：$GOOGLE_DRIVE_EMAIL"
  else
    check_fail "GOOGLE_DRIVE_EMAIL 尚未設定"
  fi
else
  check_fail "找不到 setup/environment.env"
  echo ""
  echo "  請執行以下指令建立個人設定檔："
  echo "  cp setup/environment.env.example setup/environment.env"
  echo "  然後用文字編輯器打開，填入你的個人資訊。"
fi

# ── 2. Pandoc ─────────────────────────────────────────────────

section "2. Pandoc（Markdown → Word 轉換工具）"

PANDOC_BIN="${PANDOC_PATH:-pandoc}"
if command -v "$PANDOC_BIN" &>/dev/null; then
  VERSION=$("$PANDOC_BIN" --version | head -1)
  check_pass "Pandoc 已安裝：$VERSION"
else
  check_fail "找不到 Pandoc"
  echo ""
  echo "  請安裝 Pandoc："
  if [ "$OS_TYPE" = "macos" ]; then
    echo "  1. 先安裝 Homebrew（如尚未安裝）："
    echo "     /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  2. 安裝 Pandoc："
    echo "     brew install pandoc"
  elif [ "$OS_TYPE" = "linux" ]; then
    echo "    sudo apt install pandoc"
  elif [ "$OS_TYPE" = "windows" ]; then
    echo "    winget install JohnMacFarlane.Pandoc"
    echo ""
    echo "  安裝後重新開啟終端機，若仍找不到，請在 environment.env 設定完整路徑："
    echo "    PANDOC_PATH=/c/Users/<帳號>/AppData/Local/Microsoft/WinGet/Packages/..."
  else
    echo "  請至 https://pandoc.org/installing.html 下載安裝"
  fi
fi

# ── 3. Google Drive for Desktop ───────────────────────────────

section "3. Google Drive for Desktop"

if [ "$OS_TYPE" = "macos" ]; then
  if [ -d "$HOME/Library/CloudStorage" ]; then
    GDRIVE_ACCOUNTS=$(ls "$HOME/Library/CloudStorage/" | grep "GoogleDrive-" | sed 's/GoogleDrive-//')
    if [ -n "$GDRIVE_ACCOUNTS" ]; then
      check_pass "Google Drive for Desktop 已安裝並登入"
      echo ""
      echo "  已連線帳號："
      while IFS= read -r acct; do
        echo "    • $acct"
      done <<< "$GDRIVE_ACCOUNTS"
    else
      check_fail "Google Drive for Desktop 已安裝但未登入任何 Google 帳號"
    fi
  else
    check_fail "找不到 Google Drive for Desktop"
    echo ""
    echo "  請安裝 Google Drive for Desktop："
    echo "  https://www.google.com/drive/download/"
    echo "  安裝後登入你的 Google 帳號，並開啟「我的雲端硬碟」同步。"
  fi

elif [ "$OS_TYPE" = "windows" ]; then
  GDRIVE_FOUND=false

  # 優先使用 environment.env 中手動設定的 GOOGLE_DRIVE_ROOT
  if [ -n "$GOOGLE_DRIVE_ROOT" ] && [ -d "$GOOGLE_DRIVE_ROOT" ]; then
    check_pass "Google Drive 已掛載：$GOOGLE_DRIVE_ROOT"
    GDRIVE_FOUND=true
  else
    # 自動偵測：掃描常見磁碟機代號下的「我的雲端硬碟」
    for DRIVE in /d /e /f /g /h /i /j /k; do
      if [ -d "${DRIVE}/我的雲端硬碟" ]; then
        check_pass "Google Drive 已掛載：${DRIVE}/我的雲端硬碟"
        GOOGLE_DRIVE_ROOT="${DRIVE}/我的雲端硬碟"
        GDRIVE_FOUND=true
        break
      fi
    done
  fi

  if [ "$GDRIVE_FOUND" = false ]; then
    check_fail "找不到 Google Drive 掛載點"
    echo ""
    echo "  請確認 Google Drive for Desktop 已安裝並登入："
    echo "  https://www.google.com/drive/download/"
    echo "  安裝後，在 environment.env 加入掛載根目錄（例如）："
    echo "    GOOGLE_DRIVE_ROOT=/h/我的雲端硬碟"
  fi

elif [ "$OS_TYPE" = "linux" ]; then
  if [ "$IS_WSL" = true ]; then
    echo "  （WSL2 環境：Google Drive for Desktop 不適用）"
    echo "  可透過 /mnt/c/... 存取 Windows 端已同步的 Google Drive 資料夾"
    echo "  或使用瀏覽器版 Google Drive：https://drive.google.com"
  else
    echo "  （Linux 環境：Google Drive for Desktop 不適用，請使用瀏覽器版）"
    echo "  https://drive.google.com"
  fi

else
  echo "  （不支援的 OS，跳過此項檢查）"
fi

# ── 4. Google Drive TeacherOS 資料夾 ──────────────────────────

section "4. Google Drive TeacherOS 資料夾"

if [ -n "$GOOGLE_DRIVE_EMAIL" ] && [ -n "$GOOGLE_DRIVE_FOLDER" ]; then
  # 將 Windows 反斜線統一轉為正斜線
  GDRIVE_FOLDER_UNIX=$(echo "$GOOGLE_DRIVE_FOLDER" | tr '\\' '/')

  if [ "$OS_TYPE" = "macos" ]; then
    GDRIVE_PATH="$HOME/Library/CloudStorage/GoogleDrive-${GOOGLE_DRIVE_EMAIL}/我的雲端硬碟/${GDRIVE_FOLDER_UNIX}"
  elif [ "$OS_TYPE" = "windows" ]; then
    if [ -n "$GOOGLE_DRIVE_ROOT" ]; then
      GDRIVE_PATH="${GOOGLE_DRIVE_ROOT}/${GDRIVE_FOLDER_UNIX}"
    else
      # GOOGLE_DRIVE_ROOT 未偵測到，以腳本所在位置推算
      GDRIVE_PATH="$REPO_ROOT"
    fi
  elif [ "$OS_TYPE" = "linux" ]; then
    if [ "$IS_WSL" = true ] && [ -n "$GOOGLE_DRIVE_ROOT" ] && [ -d "$GOOGLE_DRIVE_ROOT" ]; then
      GDRIVE_PATH="${GOOGLE_DRIVE_ROOT}/${GDRIVE_FOLDER_UNIX}"
    else
      GDRIVE_PATH=""
    fi
  else
    GDRIVE_PATH=""
  fi

  if [ "$OS_TYPE" = "linux" ] && [ -z "$GDRIVE_PATH" ]; then
    echo "  （Linux 環境無法自動偵測 Google Drive 資料夾，略過此項）"
    if [ "$IS_WSL" = true ]; then
      echo "  WSL2 使用者可在 environment.env 設定 GOOGLE_DRIVE_ROOT 來啟用此檢查"
    fi
  elif [ -n "$GDRIVE_PATH" ] && [ -d "$GDRIVE_PATH" ]; then
    check_pass "TeacherOS 資料夾存在：${GOOGLE_DRIVE_FOLDER}"
    # 確認子資料夾
    for CLASS in class-9c class-8a class-7a; do
      if [ -d "$GDRIVE_PATH/projects/$CLASS/english" ]; then
        check_pass "  projects/$CLASS/english/ 存在"
      else
        check_fail "  projects/$CLASS/english/ 不存在（請向管理員取得資料夾結構）"
      fi
    done
  else
    check_fail "找不到 TeacherOS 資料夾：${GOOGLE_DRIVE_FOLDER}"
    echo ""
    echo "  請確認："
    echo "  1. 你的 Google Drive 內有「${GOOGLE_DRIVE_FOLDER}」資料夾"
    echo "  2. 若無，請向系統管理員申請共用或複製"
    if [ "$OS_TYPE" = "windows" ]; then
      echo "  3. 請在 environment.env 設定 GOOGLE_DRIVE_ROOT，例如："
      echo "     GOOGLE_DRIVE_ROOT=/h/我的雲端硬碟"
    fi
  fi
fi

# ── 5. Google Workspace CLI（gws）─────────────────────────────

section "5. Google Workspace CLI（選用，強烈建議）"

GWS_BIN=""
if command -v gws &>/dev/null; then
  GWS_BIN="gws"
elif [ -x "$HOME/.nvm/versions/node/v24.13.0/bin/gws" ]; then
  GWS_BIN="$HOME/.nvm/versions/node/v24.13.0/bin/gws"
fi

if [ -n "$GWS_BIN" ]; then
  GWS_VERSION=$("$GWS_BIN" --version 2>/dev/null || echo "unknown")
  check_pass "gws CLI 已安裝：$GWS_VERSION"

  # 檢查是否有加密憑證（表示已完成認證）
  GWS_CONFIG_DIR="$HOME/.config/gws"
  if [ -d "$GWS_CONFIG_DIR" ] && ls "$GWS_CONFIG_DIR"/credentials.*.enc &>/dev/null 2>&1; then
    GWS_ACCOUNTS=$(ls "$GWS_CONFIG_DIR"/credentials.*.enc 2>/dev/null | sed 's/.*credentials\.\(.*\)\.enc/\1/')
    check_pass "gws 已認證"
    echo ""
    echo "  已認證帳號："
    while IFS= read -r acct; do
      echo "    • $acct"
    done <<< "$GWS_ACCOUNTS"
    echo ""
    echo "  支援服務：Gmail、Drive、Calendar、Sheets、Docs"
    echo "  參考文件：ai-core/reference/gws-cli-guide.md"
  else
    check_fail "gws 已安裝但尚未認證"
    echo ""
    echo "  請執行以下指令完成認證："
    echo "    gws auth login"
    echo "  認證後即可透過 AI 直接操作 Google Workspace 五大服務。"
  fi
else
  check_fail "找不到 gws CLI（Google Workspace 操作將受限）"
  echo ""
  echo "  gws CLI 讓 AI 直接操作 Gmail、Drive、Calendar、Sheets、Docs。"
  echo "  安裝方式："
  echo "    npm install -g @anthropic-ai/googleworkspace-tools"
  echo "  安裝後執行認證："
  echo "    gws auth login"
  echo "  完整指引：ai-core/reference/gws-cli-guide.md"
fi

# ── 6. Git ────────────────────────────────────────────────────

section "6. Git（版本控制）"

if command -v git &>/dev/null; then
  GIT_VERSION=$(git --version)
  check_pass "$GIT_VERSION"
  GIT_USER=$(git config --global user.name 2>/dev/null)
  GIT_EMAIL=$(git config --global user.email 2>/dev/null)
  if [ -n "$GIT_USER" ]; then
    check_pass "Git 使用者：$GIT_USER <$GIT_EMAIL>"
  else
    check_fail "Git 尚未設定使用者資訊"
    echo "  請執行："
    echo "  git config --global user.name \"你的姓名\""
    echo "  git config --global user.email \"你的Email\""
  fi
else
  check_fail "找不到 Git"
  if [ "$OS_TYPE" = "macos" ]; then
    echo "  請安裝 Git：brew install git"
  elif [ "$OS_TYPE" = "linux" ]; then
    echo "  請安裝 Git：sudo apt install git"
  elif [ "$OS_TYPE" = "windows" ]; then
    echo "  請安裝 Git for Windows：https://git-scm.com/download/win"
  else
    echo "  請至 https://git-scm.com 下載安裝 Git"
  fi
fi

# ── 結果摘要 ──────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════════════"
echo "  檢查完成：通過 $PASS 項，需要處理 $FAIL 項"
echo "════════════════════════════════════════════════"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "  環境設定完成，可以開始使用 TeacherOS。"
else
  echo "  請依照上方提示完成設定後，重新執行此腳本確認。"
fi
echo ""
