#!/bin/bash
# ============================================================
#  音檔轉逐字稿 - macOS 一鍵安裝腳本
#  適用於 Apple Silicon Mac（M1/M2/M3/M4）
#
#  此腳本會自動完成：
#    1. 建立 Python 虛擬環境
#    2. 安裝 mlx-whisper（語音轉文字）
#    3. 安裝 pyannote-audio（說話者辨識）
#    4. 建立拖放用的 macOS App
#    5. 設定 HuggingFace Token（說話者辨識需要）
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo ""
echo "  ============================================"
echo "  音檔轉逐字稿 — macOS 安裝程式"
echo "  ============================================"
echo ""

# --- 檢查系統環境 ---
echo "  [1/6] 檢查系統環境..."

# 確認是 macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "  ❌ 此工具僅支援 macOS。"
    exit 1
fi

# 確認是 Apple Silicon
ARCH="$(uname -m)"
if [[ "$ARCH" != "arm64" ]]; then
    echo "  ❌ 此工具需要 Apple Silicon Mac（M1/M2/M3/M4）。"
    echo "     偵測到的架構: $ARCH"
    exit 1
fi

# 確認有 Python 3
if ! command -v python3 &>/dev/null; then
    echo "  ❌ 找不到 Python 3，請先安裝。"
    echo "     建議: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "  ✅ macOS + Apple Silicon"
echo "  ✅ $PYTHON_VERSION"

# --- 建立虛擬環境 ---
echo ""
echo "  [2/6] 建立 Python 虛擬環境..."

if [ -d "$VENV_DIR" ]; then
    echo "  已存在，跳過。"
else
    python3 -m venv "$VENV_DIR"
    echo "  ✅ 虛擬環境建立完成"
fi

source "$VENV_DIR/bin/activate"

# --- 安裝 mlx-whisper ---
echo ""
echo "  [3/6] 安裝語音轉文字引擎（mlx-whisper）..."
echo "  （這可能需要幾分鐘，請耐心等待）"
echo ""

if python3 -c "import mlx_whisper" 2>/dev/null; then
    echo "  已安裝，跳過。"
else
    pip install --upgrade pip -q
    pip install mlx-whisper 2>&1 | tail -3
    echo ""
    if python3 -c "import mlx_whisper" 2>/dev/null; then
        echo "  ✅ mlx-whisper 安裝成功"
    else
        echo "  ❌ mlx-whisper 安裝失敗，請檢查錯誤訊息。"
        exit 1
    fi
fi

# --- 安裝 pyannote-audio ---
echo ""
echo "  [4/6] 安裝說話者辨識引擎（pyannote-audio）..."
echo "  （這可能需要較長時間，請耐心等待）"
echo ""

if python3 -c "import pyannote.audio" 2>/dev/null; then
    echo "  已安裝，跳過。"
else
    pip install pyannote-audio 2>&1 | tail -3
    echo ""
    if python3 -c "import pyannote.audio" 2>/dev/null; then
        echo "  ✅ pyannote-audio 安裝成功"
    else
        echo "  ❌ pyannote-audio 安裝失敗，請檢查錯誤訊息。"
        exit 1
    fi
fi

# --- 設定 HuggingFace Token ---
echo ""
echo "  [5/6] 設定 HuggingFace Token（說話者辨識需要）..."

ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ] && grep -q "^HF_TOKEN=hf_" "$ENV_FILE"; then
    echo "  已設定，跳過。"
else
    echo ""
    echo "  說話者辨識需要 HuggingFace 的存取權杖。"
    echo "  如果你還沒有，請按照以下步驟取得："
    echo ""
    echo "    1. 前往 https://huggingface.co/settings/tokens"
    echo "    2. 點「Create new token」"
    echo "    3. Name 隨意填，Type 選「Read」"
    echo "    4. 複製產生的 Token（以 hf_ 開頭）"
    echo ""
    echo "  另外，你也需要同意 pyannote 模型的使用條款："
    echo "    https://huggingface.co/pyannote/speaker-diarization-3.1"
    echo "    （登入後點「Agree and access repository」）"
    echo ""
    read -p "  請貼上你的 HuggingFace Token（或按 Enter 跳過）: " HF_INPUT

    if [[ "$HF_INPUT" == hf_* ]]; then
        echo "# HuggingFace Access Token（用於 pyannote 說話者辨識模型）" > "$ENV_FILE"
        echo "HF_TOKEN=$HF_INPUT" >> "$ENV_FILE"
        echo "  ✅ Token 已儲存到 .env"
    else
        echo "  ⚠️  未設定 Token，說話者辨識功能暫時無法使用。"
        echo "     之後可手動建立 .env 檔並填入 HF_TOKEN=你的Token"
        # 建立空的 .env
        if [ ! -f "$ENV_FILE" ]; then
            cp "$SCRIPT_DIR/.env.example" "$ENV_FILE" 2>/dev/null || echo "# HF_TOKEN=你的HuggingFace存取權杖" > "$ENV_FILE"
        fi
    fi
fi

# --- 建立 macOS App ---
echo ""
echo "  [6/6] 建立拖放用 App..."

APP_SCRIPT="$SCRIPT_DIR/build_app.applescript"
if [ -f "$APP_SCRIPT" ]; then
    osacompile -o "$SCRIPT_DIR/音檔轉逐字稿.app" "$APP_SCRIPT"
    if [ -d "$SCRIPT_DIR/音檔轉逐字稿.app" ]; then
        echo "  ✅ App 建立完成"
    else
        echo "  ⚠️  App 建立失敗，但你仍可透過命令列使用。"
    fi
else
    echo "  ⚠️  找不到 build_app.applescript，跳過 App 建立。"
fi

# --- 完成 ---
echo ""
echo "  ============================================"
echo "  ✅ 安裝完成！"
echo "  ============================================"
echo ""
echo "  使用方式："
echo "    方法 1: 將音檔拖到「音檔轉逐字稿.app」圖示上"
echo "    方法 2: 終端機執行 ./transcribe.sh 你的音檔.m4a"
echo ""
echo "  輸出："
echo "    轉錄結果會存為同名 .md 檔，放在音檔旁邊。"
echo "    如果有設定 HF_TOKEN，會自動標記說話者。"
echo ""
