#!/bin/bash
# 音檔轉逐字稿（含說話者辨識）- 啟動腳本
# 用法: ./transcribe.sh <音檔> [音檔2] ...
# 或直接將音檔拖進 App 圖示

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "  [錯誤] 找不到虛擬環境，請先執行 setup.sh 安裝。"
    exit 1
fi

source "$VENV_DIR/bin/activate"
python3 "$SCRIPT_DIR/transcribe.py" "$@"
