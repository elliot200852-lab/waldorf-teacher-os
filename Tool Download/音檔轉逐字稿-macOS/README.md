# 音檔轉逐字稿（macOS 版）

將音檔自動轉錄為 Markdown 逐字稿，支援**說話者辨識**（自動區分不同說話者）。

專為 **Apple Silicon Mac**（M1/M2/M3/M4）優化，使用本地模型處理，資料不會上傳到雲端。

## 功能

- 語音轉文字（中文為主，支援多語言）
- 說話者辨識（自動標記說話者 A、B、C...）
- 同一說話者的連續語句自動合併為段落
- 輸出為 Markdown 格式（含時間軸 + 說話者標記 + 全文）
- 支援拖放操作（macOS App）

## 支援的音檔格式

m4a, mp3, wav, flac, ogg, wma, aac

## 系統需求

- macOS（Apple Silicon：M1 / M2 / M3 / M4）
- Python 3.9 以上
- 約 3GB 硬碟空間（安裝模型與套件）
- 建議 16GB 以上記憶體（8GB 可運行但較慢）

## 安裝步驟

### 1. 下載本資料夾

將整個 `音檔轉逐字稿-macOS` 資料夾下載到你想放的位置（例如桌面）。

### 2. 執行安裝腳本

打開「終端機」（Terminal），輸入以下指令：

```bash
cd ~/Desktop/音檔轉逐字稿-macOS
chmod +x setup.sh
./setup.sh
```

安裝過程中腳本會引導你完成所有設定，包含 HuggingFace Token。

### 3. 取得 HuggingFace Token（說話者辨識需要）

1. 前往 [HuggingFace](https://huggingface.co) 註冊帳號
2. 前往 [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)，點「Agree and access repository」同意使用條款
3. 前往 [Access Tokens](https://huggingface.co/settings/tokens)，建立一個 **Read** 類型的 Token
4. 安裝腳本會提示你貼上 Token，或事後手動編輯 `.env` 檔

> 如果不設定 Token，工具仍可正常運作，只是不會標記說話者。

## 使用方式

### 方法一：拖放（推薦）

將音檔直接拖到「**音檔轉逐字稿.app**」圖示上。

### 方法二：終端機

```bash
cd ~/Desktop/音檔轉逐字稿-macOS
./transcribe.sh 你的音檔.m4a
```

支援一次處理多個檔案：

```bash
./transcribe.sh 檔案1.m4a 檔案2.mp3 檔案3.wav
```

## 輸出格式

轉錄結果會存為與音檔同名的 `.md` 檔，放在音檔旁邊。

啟用說話者辨識時的輸出範例：

```markdown
### 說話者 A [00:00]
大家好，今天我們來討論一下課程設計的方向。

### 說話者 B [00:15]
好的，我覺得我們可以從上學期的經驗出發。
```

## 檔案說明

| 檔案 | 用途 |
|------|------|
| `setup.sh` | 一鍵安裝腳本 |
| `transcribe.py` | 主程式（語音轉文字 + 說話者辨識） |
| `transcribe.sh` | 啟動腳本（啟動虛擬環境並執行） |
| `build_app.applescript` | 建立 macOS 拖放 App 的腳本 |
| `.env.example` | 環境變數範本 |
| `.env` | 你的實際設定（安裝後自動建立，不要分享） |

## 注意事項

- 首次執行時會自動下載 AI 模型（約 1-2GB），需要網路連線
- 之後的使用完全離線，不需要網路
- `.env` 檔包含你的私人 Token，請勿分享或上傳到 GitHub
- 處理時間依音檔長度而定，一小時的錄音大約需要 3-5 分鐘

## 技術細節

- 語音轉文字：[mlx-whisper](https://github.com/ml-explore/mlx-examples)（Apple Silicon 優化版 Whisper）
- 說話者辨識：[pyannote-audio](https://github.com/pyannote/pyannote-audio) speaker-diarization-3.1
- 模型：mlx-community/whisper-large-v3-turbo
