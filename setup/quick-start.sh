#!/usr/bin/env bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — 一鍵技術安裝腳本
# 路徑：setup/quick-start.sh
# 用途：新教師快速安裝 TeacherOS 開發環境
# 使用方式：bash setup/quick-start.sh
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

# ──────────────────────────────────────────────────────────
# 顏色與符號設定
# ──────────────────────────────────────────────────────────

GREEN='\033[0;32m'      # ✓ OK
YELLOW='\033[1;33m'     # ⚠ 警告
RED='\033[0;31m'        # ✗ 錯誤
BLUE='\033[0;34m'       # ℹ 資訊
NC='\033[0m'            # 無色

CHECK="✓"
WARN="⚠"
ERROR="✗"
INFO="ℹ"

# ──────────────────────────────────────────────────────────
# 輔助函式
# ──────────────────────────────────────────────────────────

print_banner() {
  echo ""
  echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC}  TeacherOS 技術安裝精靈                             ${BLUE}║${NC}"
  echo -e "${BLUE}║${NC}  一鍵設定你的教學工作環境                           ${BLUE}║${NC}"
  echo -e "${BLUE}║${NC}  ──────────────────────────────────────           ${BLUE}║${NC}"
  echo -e "${BLUE}║${NC}  歡迎使用華德福課程設計系統                         ${BLUE}║${NC}"
  echo -e "${BLUE}║${NC}  The Teacher's Consciousness Operating System       ${BLUE}║${NC}"
  echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
  echo ""
}

print_section() {
  echo ""
  echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
}

print_success() {
  echo -e "${GREEN}${CHECK} $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}${WARN} $1${NC}"
}

print_error() {
  echo -e "${RED}${ERROR} $1${NC}"
}

print_info() {
  echo -e "${BLUE}${INFO} $1${NC}"
}

# ──────────────────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────────────────

print_banner

# 確認 Repo 根目錄
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
print_info "Repo 根目錄：$REPO_ROOT"

# ──────────────────────────────────────────────────────────
# 檢查 1：Git 安裝
# ──────────────────────────────────────────────────────────

print_section "檢查 1：Git 安裝狀態（版本控制的鑰匙）"

if command -v git &> /dev/null; then
  GIT_VERSION=$(git --version)
  print_success "Git 已安裝：$GIT_VERSION"
else
  print_error "Git 尚未安裝"
  echo ""
  echo -e "${YELLOW}請按照以下步驟安裝 Git：${NC}"
  echo ""
  echo "macOS 使用者："
  echo "  brew install git"
  echo ""
  echo "Ubuntu/Debian 使用者："
  echo "  sudo apt-get update"
  echo "  sudo apt-get install git"
  echo ""
  echo "Windows 使用者："
  echo "  前往 https://git-scm.com 下載 Git for Windows"
  echo ""
  exit 1
fi

# ──────────────────────────────────────────────────────────
# 檢查 2：Repo 已複製
# ──────────────────────────────────────────────────────────

print_section "檢查 2：TeacherOS Repo 狀態（已複製校驗）"

if [ -f "$REPO_ROOT/ai-core/teacheros.yaml" ]; then
  print_success "TeacherOS Repo 已完整複製"
else
  print_error "找不到 ai-core/teacheros.yaml，Repo 可能不完整"
  echo ""
  echo -e "${YELLOW}請確認您已執行：${NC}"
  echo "  git clone https://github.com/elliot200852-lab/WaldorfTeacherOS-Repo.git"
  exit 1
fi

# ──────────────────────────────────────────────────────────
# 檢查 3：Homebrew（macOS 特定）
# ──────────────────────────────────────────────────────────

print_section "檢查 3：Homebrew 安裝狀態（macOS 套件管理器）"

if [[ "$OSTYPE" == "darwin"* ]]; then
  if command -v brew &> /dev/null; then
    BREW_VERSION=$(brew --version | head -1)
    print_success "Homebrew 已安裝：$BREW_VERSION"
  else
    print_warning "Homebrew 尚未安裝（僅 macOS 需要）"
    echo ""
    echo -e "${YELLOW}若需要自動安裝 Pandoc 等工具，請安裝 Homebrew：${NC}"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
  fi
else
  print_info "您不在 macOS 系統上，Homebrew 檢查略過"
fi

# ──────────────────────────────────────────────────────────
# 檢查 4：Pandoc 安裝
# ──────────────────────────────────────────────────────────

print_section "檢查 4：Pandoc 安裝狀態（Markdown 轉換工具）"

if command -v pandoc &> /dev/null; then
  PANDOC_VERSION=$(pandoc --version | head -1)
  print_success "Pandoc 已安裝：$PANDOC_VERSION"
else
  print_warning "Pandoc 尚未安裝"
  echo ""
  echo -e "${YELLOW}建議安裝 Pandoc（用於 Markdown → Word 轉換）：${NC}"
  echo ""
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS 使用者："
    echo "  brew install pandoc"
  else
    echo "Ubuntu/Debian 使用者："
    echo "  sudo apt-get install pandoc"
  fi
  echo ""
fi

# ──────────────────────────────────────────────────────────
# 檢查 4.5：Google Workspace CLI（gws）安裝狀態
# ──────────────────────────────────────────────────────────

print_section "檢查 4.5：Google Workspace CLI（gws）安裝狀態"

# 先檢查 Node.js / npm（gws 的前置條件）
if command -v node &> /dev/null && command -v npm &> /dev/null; then
  NODE_VERSION=$(node --version)
  print_success "Node.js 已安裝：$NODE_VERSION"

  if command -v gws &> /dev/null; then
    GWS_VERSION=$(gws --version 2>/dev/null || echo "已安裝")
    print_success "Google Workspace CLI 已安裝：$GWS_VERSION"

    # 檢查是否已登入
    if gws auth status &>/dev/null; then
      print_success "gws 已登入 Google 帳號"
    else
      print_warning "gws 尚未登入 Google 帳號"
      echo ""
      echo -e "${YELLOW}請執行以下指令登入：${NC}"
      echo "  gws auth login"
      echo ""
    fi
  else
    print_warning "Google Workspace CLI（gws）尚未安裝"
    echo ""
    echo -e "${YELLOW}建議安裝 gws（讓 AI 可直接操作 Google Drive、Calendar 等服務）：${NC}"
    echo "  npm install -g @googleworkspace/cli"
    echo ""
    echo -e "${YELLOW}安裝後，執行以下指令登入你的 Google 帳號：${NC}"
    echo "  gws auth login"
    echo ""
  fi
else
  print_info "Node.js / npm 未安裝，跳過 gws 檢查"
  echo ""
  echo -e "${YELLOW}若需要使用 Google Workspace CLI，請先安裝 Node.js：${NC}"
  echo "  https://nodejs.org"
  echo ""
fi

# ──────────────────────────────────────────────────────────
# 檢查 5：安裝 Git Pre-commit Hook（門鎖）
# ──────────────────────────────────────────────────────────

print_section "檢查 5：安裝 Git Pre-commit Hook（授權檢查的門鎖）"

if [ -f "$REPO_ROOT/setup/install-hooks.sh" ]; then
  print_info "開始安裝 Pre-commit Hook..."

  if bash "$REPO_ROOT/setup/install-hooks.sh"; then
    print_success "Pre-commit Hook 安裝完成"
  else
    print_error "Pre-commit Hook 安裝失敗"
    echo "請手動執行：bash $REPO_ROOT/setup/install-hooks.sh"
  fi
else
  print_warning "找不到 setup/install-hooks.sh，跳過 Hook 安裝"
fi

# ──────────────────────────────────────────────────────────
# 檢查 6：個人環境設定檔（鑰匙）
# ──────────────────────────────────────────────────────────

print_section "檢查 6：個人環境設定檔（你的工作鑰匙）"

ENV_FILE="$REPO_ROOT/setup/environment.env"
ENV_EXAMPLE="$REPO_ROOT/setup/environment.env.example"

if [ -f "$ENV_FILE" ]; then
  print_success "environment.env 已存在"
  # 檢查是否已填入基本信息
  if grep -q "USER_NAME=你的姓名" "$ENV_FILE" 2>/dev/null; then
    print_warning "environment.env 仍含有預設佔位符，請編輯檔案並填入真實資訊"
  else
    print_info "environment.env 已初步配置"
  fi
else
  # 嘗試自動偵測：從 workspace 的 env-preset.env 比對 git config user.email
  GIT_EMAIL_CHECK=$(git config user.email 2>/dev/null || echo "")
  PRESET_FOUND=""

  if [ -n "$GIT_EMAIL_CHECK" ]; then
    for PRESET in "$REPO_ROOT"/workspaces/Working_Member/*/env-preset.env; do
      [ -f "$PRESET" ] || continue
      PRESET_EMAIL=$(grep -E "^USER_EMAIL=" "$PRESET" 2>/dev/null | cut -d'=' -f2 | tr -d '[:space:]')
      if [ "$PRESET_EMAIL" = "$GIT_EMAIL_CHECK" ]; then
        PRESET_FOUND="$PRESET"
        break
      fi
    done
  fi

  if [ -n "$PRESET_FOUND" ]; then
    # 找到管理員預填的環境設定，直接使用
    PRESET_NAME=$(grep -E "^USER_NAME=" "$PRESET_FOUND" 2>/dev/null | cut -d'=' -f2)
    print_info "偵測到你的預填設定（$PRESET_NAME），自動建立 environment.env..."
    cp "$PRESET_FOUND" "$ENV_FILE"
    print_success "environment.env 已自動建立（必填欄位已預填）"
    echo ""
    echo -e "${GREEN}以下欄位已自動設定：${NC}"
    echo "  USER_NAME、USER_EMAIL、WORKSPACE_ID、GITHUB_USERNAME"
    echo ""
    echo -e "${YELLOW}選填欄位（Google Drive、Pandoc 等）可之後再補充。${NC}"
    echo ""
  elif [ -f "$ENV_EXAMPLE" ]; then
    print_info "複製 environment.env.example → environment.env..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    print_success "environment.env 已建立"
    echo ""
    echo -e "${YELLOW}請用文字編輯器打開 setup/environment.env，填入你的個人資訊：${NC}"
    echo "  - USER_NAME：你的姓名"
    echo "  - USER_EMAIL：你的 Email（必須與 GitHub 帳號相符）"
    echo "  - GOOGLE_DRIVE_EMAIL：你的 Google Drive 帳號"
    echo "  - GITHUB_USERNAME：你的 GitHub 帳號"
    echo ""
  else
    print_error "找不到 environment.env.example"
  fi
fi

# ──────────────────────────────────────────────────────────
# 檢查 7：執行 setup-check.sh
# ──────────────────────────────────────────────────────────

print_section "檢查 7：詳細環境檢查"

if [ -f "$REPO_ROOT/setup/setup-check.sh" ]; then
  print_info "執行詳細環境檢查..."
  echo ""

  if bash "$REPO_ROOT/setup/setup-check.sh"; then
    print_success "所有環境檢查完成"
  else
    print_warning "部分環境檢查未通過，但不影響基本功能"
  fi
else
  print_warning "找不到 setup-check.sh，跳過詳細檢查"
fi

# ──────────────────────────────────────────────────────────
# 檢查 8：切換到個人 Branch
# ──────────────────────────────────────────────────────────

print_section "檢查 8：切換到你的個人工作分支"

# 從 environment.env 讀取 email，尋找對應的 branch
TEACHER_EMAIL=""
if [ -f "$ENV_FILE" ]; then
  TEACHER_EMAIL=$(grep -E "^USER_EMAIL=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '[:space:]')
fi

if [ -z "$TEACHER_EMAIL" ]; then
  TEACHER_EMAIL=$(git config user.email 2>/dev/null || echo "")
fi

# 嘗試從遠端 branch 列表中找到 workspace/ 開頭的分支
git fetch --all --quiet 2>/dev/null || true
WORKSPACE_BRANCHES=$(git branch -r 2>/dev/null | grep "origin/workspace/" | sed 's|origin/||' | tr -d ' ')

if [ -n "$WORKSPACE_BRANCHES" ]; then
  BRANCH_COUNT=$(echo "$WORKSPACE_BRANCHES" | wc -l | tr -d ' ')

  if [ "$BRANCH_COUNT" -eq 1 ]; then
    # 只有一個 workspace branch，直接切換
    BRANCH_NAME=$(echo "$WORKSPACE_BRANCHES" | head -1)
    print_info "偵測到你的工作分支：$BRANCH_NAME"
    git checkout "$BRANCH_NAME" 2>/dev/null && \
      print_success "已切換到你的個人分支：$BRANCH_NAME" || \
      print_warning "自動切換失敗，請手動執行：git checkout $BRANCH_NAME"
  else
    # 多個 workspace branch，列出讓教師選
    print_info "偵測到多個工作分支："
    echo "$WORKSPACE_BRANCHES" | while read -r b; do
      echo "  - $b"
    done
    echo ""
    print_warning "請手動切換到你的分支，例如："
    echo "  git checkout workspace/Teacher_你的姓名"
  fi
else
  print_info "尚未找到你的個人分支"
  print_info "這代表 David 還沒有建立你的工作空間"
  print_info "請聯繫 David，等他建立後再執行一次 git pull"
fi

# ──────────────────────────────────────────────────────────
# 檢查 9：Claude Code Hook 設定（選用，不影響其他 AI 工具）
# ──────────────────────────────────────────────────────────

print_section "檢查 9：Claude Code Hook 設定（選用）"

CLAUDE_SETTINGS="$REPO_ROOT/.claude/settings.local.json"
CLAUDE_SCRIPTS="$REPO_ROOT/.claude/scripts"

if [ -f "$CLAUDE_SETTINGS" ]; then
  # 已有設定檔，檢查是否包含 hook
  if grep -q "session-init.py" "$CLAUDE_SETTINGS" 2>/dev/null; then
    print_success "Claude Code Hook 已設定"
  else
    print_info "settings.local.json 已存在但未包含 Hook，跳過自動寫入"
    print_info "如需手動設定，請參考 setup/teacher-guide.md"
  fi
else
  # 沒有設定檔，建立新的（僅含 hook，不含 permissions）
  if [ -f "$CLAUDE_SCRIPTS/session-init.py" ]; then
    mkdir -p "$(dirname "$CLAUDE_SETTINGS")"
    cat > "$CLAUDE_SETTINGS" << 'ENDJSON'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/scripts/session-init.py"
          }
        ]
      }
    ]
  }
}
ENDJSON
    print_success "Claude Code Hook 已自動設定"
    print_info "每次使用 Claude Code 時，會自動顯示你的班級工作狀態"
  else
    print_warning "找不到 .claude/scripts/session-init.py，跳過 Hook 設定"
  fi
fi

print_info "不使用 Claude Code？此步驟不影響任何其他 AI 工具"

# ──────────────────────────────────────────────────────────
# 完成提示
# ──────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  技術安裝完成！                                   ${GREEN}║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# 檢查是否已在 workspace branch 上
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if echo "$CURRENT_BRANCH" | grep -q "^workspace/"; then
  print_success "你已在個人分支上：$CURRENT_BRANCH"
  print_info "可以開始使用 TeacherOS 了！"
else
  print_info "下一步：請聯繫 David（elliot200852@gmail.com）取得你的工作空間。"
  print_info "David 設定完成後，執行 git pull 再重新執行本腳本即可。"
fi
echo ""
