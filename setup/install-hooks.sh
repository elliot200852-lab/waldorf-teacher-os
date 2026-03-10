#!/usr/bin/env bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TeacherOS — Hook 一鍵安裝腳本
# 路徑：setup/install-hooks.sh
# 使用方式：bash setup/install-hooks.sh
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ -z "$REPO_ROOT" ]; then
    echo "[錯誤] 請在 TeacherOS 的 Git 資料夾內執行此腳本。"
    exit 1
fi

SRC="$REPO_ROOT/setup/hooks/pre-commit"
DEST="$REPO_ROOT/.git/hooks/pre-commit"

if [ ! -f "$SRC" ]; then
    echo "[錯誤] 找不到 setup/hooks/pre-commit，請確認 Repo 是否完整。"
    exit 1
fi

chmod +x "$SRC"
cp "$SRC" "$DEST"
chmod +x "$DEST"

# ── Post-merge hook（Good-notes 新分享通知）────────────────
SRC_PM="$REPO_ROOT/setup/hooks/post-merge"
DEST_PM="$REPO_ROOT/.git/hooks/post-merge"

if [ -f "$SRC_PM" ]; then
    chmod +x "$SRC_PM"
    cp "$SRC_PM" "$DEST_PM"
    chmod +x "$DEST_PM"
    PM_MSG="  Post-merge hook 已安裝至：.git/hooks/post-merge"
else
    PM_MSG="  [略過] 找不到 setup/hooks/post-merge"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TeacherOS Hook 安裝完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Pre-commit hook 已安裝至：.git/hooks/pre-commit"
echo "$PM_MSG"
echo ""
echo "  往後每次執行 git commit，系統將自動："
echo "    1. 確認你的身份（USER_EMAIL）"
echo "    2. 比對 ai-core/acl.yaml 的授權範圍"
echo "    3. 攔截超出授權的檔案修改"
echo ""
echo "  每次 git pull 時，若 Good-notes/ 有新分享，"
echo "  系統會顯示分享者姓名與檔案清單。"
echo ""
echo "  如有任何問題，請聯絡 David。"
echo ""
