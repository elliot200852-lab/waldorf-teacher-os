#!/usr/bin/env bash
# publish-drafts.sh — 將 drafts/ 中的草稿複製到 published/[pillar]/ 並以語意命名
#
# 用法：bash setup/scripts/publish-drafts.sh [ASSET_BASE_PATH]
#   ASSET_BASE_PATH 預設為 ../Personal-Asset-base（相對於 TeacherOS Repo 根目錄）
#
# 前提：每篇草稿的 YAML frontmatter 必須包含三個欄位：
#   publish_date: "2026-03-10"
#   pillar: C-teacheros-log
#   slug: why-build-an-os
#
# 腳本行為：
#   1. 掃描 vault/drafts/ 下所有 .md 檔
#   2. 從 frontmatter 讀取 publish_date, pillar, slug
#   3. 複製到 vault/published/[pillar]/[publish_date]-[slug]-draft.md
#   4. 如果目標檔已存在 → 跳過（不覆蓋）
#   5. 如果 frontmatter 缺欄位 → 跳過並警告

set -euo pipefail

# ---------- 路徑解析 ----------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ -n "${1:-}" ]]; then
    ASSET_BASE="$1"
else
    ASSET_BASE="$(cd "$REPO_ROOT/../Personal-Asset-base" 2>/dev/null && pwd)" || {
        echo "ERROR: 找不到 Personal-Asset-base。請用參數指定路徑。"
        echo "用法: bash $0 /path/to/Personal-Asset-base"
        exit 1
    }
fi

DRAFTS_DIR="$ASSET_BASE/vault/drafts"
PUBLISHED_DIR="$ASSET_BASE/vault/published"

if [[ ! -d "$DRAFTS_DIR" ]]; then
    echo "ERROR: drafts 資料夾不存在: $DRAFTS_DIR"
    exit 1
fi

# ---------- 從 frontmatter 讀值 ----------
read_frontmatter() {
    local file="$1"
    local key="$2"
    # 只讀第一個 --- 到第二個 --- 之間的內容
    sed -n '/^---$/,/^---$/p' "$file" | grep "^${key}:" | head -1 | sed "s/^${key}:[[:space:]]*//" | tr -d '"' | tr -d "'"
}

# ---------- 主邏輯 ----------
count_copied=0
count_skipped=0
count_error=0

for draft in "$DRAFTS_DIR"/*.md; do
    [[ -f "$draft" ]] || continue

    filename="$(basename "$draft")"
    publish_date="$(read_frontmatter "$draft" "publish_date")"
    pillar="$(read_frontmatter "$draft" "pillar")"
    slug="$(read_frontmatter "$draft" "slug")"

    # 檢查必要欄位
    if [[ -z "$publish_date" || -z "$pillar" || -z "$slug" ]]; then
        echo "SKIP (缺欄位): $filename  [date=$publish_date, pillar=$pillar, slug=$slug]"
        count_error=$((count_error + 1))
        continue
    fi

    # 確保 pillar 子資料夾存在
    target_dir="$PUBLISHED_DIR/$pillar"
    mkdir -p "$target_dir"

    target_file="$target_dir/${publish_date}-${slug}-draft.md"

    if [[ -f "$target_file" ]]; then
        echo "SKIP (已存在): $(basename "$target_file")"
        count_skipped=$((count_skipped + 1))
    else
        cp "$draft" "$target_file"
        echo "COPY: $filename → $(basename "$target_file")"
        count_copied=$((count_copied + 1))
    fi
done

echo ""
echo "完成: 複製 $count_copied 篇 / 跳過 $count_skipped 篇 / 錯誤 $count_error 篇"
