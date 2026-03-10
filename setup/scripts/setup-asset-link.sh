#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# setup-asset-link.sh
# 在 TeacherOS Repo 內建立指向 Personal-Asset-base 的 symlink
# 讓 Obsidian 可以直接在 TeacherOS vault 裡編輯文章
# 只需執行一次。重複執行安全（會檢查已存在的 link）。
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -euo pipefail

# ── 路徑設定 ──────────────────────────────────────────
# TeacherOS Repo 根目錄（腳本所在位置往上兩層）
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LINK_DIR="${REPO_ROOT}/David-personal-asset-base"

# Personal-Asset-base 位置（預設路徑，可透過參數覆蓋）
ASSET_BASE="${1:-${HOME}/Desktop/Personal-Asset-base}"

# ── 檢查 ──────────────────────────────────────────────
if [ ! -d "${ASSET_BASE}" ]; then
    echo "找不到 Personal-Asset-base 資料夾："
    echo "  預期路徑：${ASSET_BASE}"
    echo ""
    echo "用法：bash setup/scripts/setup-asset-link.sh [Personal-Asset-base 的完整路徑]"
    echo "例如：bash setup/scripts/setup-asset-link.sh ~/Documents/Personal-Asset-base"
    exit 1
fi

if [ ! -d "${ASSET_BASE}/vault" ]; then
    echo "找到 ${ASSET_BASE} 但裡面沒有 vault/ 資料夾。"
    echo "請確認 Personal-Asset-base 的結構正確。"
    exit 1
fi

# ── 建立 symlink ──────────────────────────────────────
mkdir -p "${LINK_DIR}"

create_link() {
    local name="$1"
    local target="${ASSET_BASE}/vault/${name}"
    local link="${LINK_DIR}/${name}"

    if [ -L "${link}" ]; then
        current_target="$(readlink "${link}")"
        if [ "${current_target}" = "${target}" ]; then
            echo "  [OK] ${name} — symlink 已存在且正確"
        else
            echo "  [更新] ${name} — 舊目標：${current_target}"
            rm "${link}"
            ln -s "${target}" "${link}"
            echo "         新目標：${target}"
        fi
    elif [ -d "${link}" ]; then
        echo "  [警告] ${name} — 是實體資料夾，非 symlink。"
        echo "         請手動刪除後重新執行：rm -rf ${link}"
    else
        ln -s "${target}" "${link}"
        echo "  [建立] ${name} → ${target}"
    fi
}

echo ""
echo "TeacherOS Repo: ${REPO_ROOT}"
echo "Asset Base:     ${ASSET_BASE}"
echo ""
echo "建立 symlink..."

create_link "drafts"
create_link "published"

# ── .gitignore 設定 ────────────────────────────────────
GITIGNORE="${LINK_DIR}/.gitignore"
if [ ! -f "${GITIGNORE}" ]; then
    cat > "${GITIGNORE}" << 'EOF'
# symlink 內容不進 TeacherOS 的 git（它有自己的 repo）
drafts/
published/
EOF
    echo ""
    echo "  [建立] .gitignore — symlink 內容不會進 TeacherOS git"
fi

echo ""
echo "設定完成。"
echo ""
echo "驗證方式："
echo "  ls -la ${LINK_DIR}/drafts"
echo "  ls -la ${LINK_DIR}/published"
echo ""
echo "在 Obsidian 裡，David-personal-asset-base/ 現在會顯示你的文章草稿和定稿。"
echo "編輯任一邊（Obsidian / Personal-Asset-base 資料夾）都即時生效。"
