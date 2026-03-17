#!/bin/bash
# TeacherOS 輸出腳本（Shell 薄包裝）
# 實際邏輯已移至 publish/build.py（跨平台 Python 版）
# 本檔保留為向後相容的進入點。
#
# 用法：./publish/build.sh <markdown檔案路徑> [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

exec python3 "$SCRIPT_DIR/build.py" "$@"
