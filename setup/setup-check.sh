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

echo ""
echo "════════════════════════════════════════════════"
echo "  TeacherOS 環境檢查"
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
  echo "  1. 先安裝 Homebrew（如尚未安裝）："
  echo "     /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
  echo "  2. 安裝 Pandoc："
  echo "     brew install pandoc"
fi

# ── 3. Google Drive for Desktop ───────────────────────────────

section "3. Google Drive for Desktop"

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

# ── 4. Google Drive TeacherOS 資料夾 ──────────────────────────

section "4. Google Drive TeacherOS 資料夾"

if [ -n "$GOOGLE_DRIVE_EMAIL" ] && [ -n "$GOOGLE_DRIVE_FOLDER" ]; then
  GDRIVE_PATH="$HOME/Library/CloudStorage/GoogleDrive-${GOOGLE_DRIVE_EMAIL}/我的雲端硬碟/${GOOGLE_DRIVE_FOLDER}"
  if [ -d "$GDRIVE_PATH" ]; then
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
  fi
fi

# ── 5. Git ────────────────────────────────────────────────────

section "5. Git（版本控制）"

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
  echo "  請安裝 Git：brew install git"
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
