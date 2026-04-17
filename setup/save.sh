#!/usr/bin/env bash
# TeacherOS — 一鍵存檔腳本
# 用法：bash setup/save.sh "你做了什麼的說明"
# 範例：bash setup/save.sh "完成 Unit 2 的逐節教案"
# 說明：自動執行 git add → commit → push，一行搞定。

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── 檢查說明文字 ──────────────────────────────────────

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
  echo ""
  echo -e "${YELLOW}請加上說明文字，讓你之後能回憶這次存了什麼。${NC}"
  echo ""
  echo "  用法：bash setup/save.sh \"你做了什麼的說明\""
  echo ""
  echo "  範例："
  echo "    bash setup/save.sh \"完成 Unit 2 的逐節教案\""
  echo "    bash setup/save.sh \"更新了三位學生的 DI 分類\""
  echo ""
  exit 1
fi

# ── 確認在 repo 目錄內 ────────────────────────────────

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo -e "${RED}錯誤：請在 TeacherOS 資料夾內執行此指令。${NC}"
  exit 1
}

cd "$REPO_ROOT"

# ── 檢查是否有更動 ────────────────────────────────────

if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo ""
  echo "目前沒有任何更動，不需要存檔。"
  echo ""
  exit 0
fi

# ── 執行存檔 ──────────────────────────────────────────

echo ""
echo "正在儲存你的工作..."
echo ""

git add .
git commit -m "$MESSAGE"
git push

echo ""
echo -e "${GREEN}✓ 存檔完成！${NC}"
echo ""
echo "  說明：$MESSAGE"
echo "  你的工作已安全上傳到 GitHub。"
echo ""
