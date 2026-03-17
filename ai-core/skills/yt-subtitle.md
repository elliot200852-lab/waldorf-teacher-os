---
name: yt-subtitle
description: 從 YouTube 影片擷取字幕，清理格式後轉換為 Markdown 教學素材。首次使用自動安裝 yt-dlp。適用於所有教師。
triggers:
  - 下載字幕
  - 抓字幕
  - YouTube 字幕
  - 提取字幕
  - 字幕擷取
  - download subtitles
  - get captions
  - yt subtitles
  - extract subtitles
requires_args: true
args_format: "<YouTube URL> [--lang <語言代碼>] [--timestamps]"
---

# skill: yt-subtitle — YouTube 字幕擷取與教學素材轉換

從 YouTube 影片擷取字幕（手動或自動字幕），清理格式後輸出為 Markdown 教學素材。
首次使用時自動偵測並安裝 yt-dlp，無需另行設定。

## 觸發條件

教師說出接近以下意思的話，並附帶 YouTube 連結：
「下載字幕」「抓字幕」「YouTube 字幕」「提取字幕」「字幕擷取」
「download subtitles」「get captions」「extract subtitles」

**語音模式注意：** 教師以語音輸入為主，任何表達「我要這個影片的字幕」意圖的口語都應觸發。

## 參數

| 參數 | 必要 | 說明 |
|------|------|------|
| YouTube URL | 是 | 影片網址（youtube.com 或 youtu.be 格式皆可） |
| --lang | 否 | 字幕語言代碼（預設依 fallback chain：zh-TW → zh-Hant → zh → en） |
| --timestamps | 否 | 保留時間戳記於輸出中（預設：不保留，輸出純文字段落） |

若教師未提供 URL，AI 應追問一次。
若教師說「抓這個影片的字幕 https://...」，AI 自動解析 URL，不追問。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 跨平台工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機（Claude Code、Cowork） | 自動執行所有步驟 |
| 無終端機（Gemini 語音、ChatGPT） | 逐步輸出指令，請教師在終端機手動執行並回報結果 |

## 執行步驟

### Step 0 — 解析參數

從教師的輸入中提取：

1. **YouTube URL**（必要）— 驗證格式為 `youtube.com/watch?v=`、`youtu.be/`、或 `youtube.com/shorts/`
2. **目標語言**（選用）— 若教師指定語言則使用，否則使用預設 fallback chain
3. **時間戳選項**（選用）— 教師說「要時間戳」「保留時間」則啟用
4. **目標班級/科目**（自動）— 若當前已載入 session 則自動使用，不追問

### Step 1 — 確認 yt-dlp 可用（首次自動安裝）

```bash
command -v yt-dlp && yt-dlp --version
```

**已安裝：** 顯示版本，繼續下一步。

**未安裝：** 依平台自動安裝：

| 平台 | 安裝指令 |
|------|---------|
| macOS（有 Homebrew） | `brew install yt-dlp` |
| macOS（無 Homebrew） | `pip3 install yt-dlp` |
| Linux | `pip3 install yt-dlp` |
| Windows（有 winget） | `winget install yt-dlp` |
| Windows（無 winget） | `pip install yt-dlp` |

偵測邏輯：
1. macOS：先試 `command -v brew`，有則 `brew install`，無則 `pip3 install`
2. Linux：`pip3 install yt-dlp`
3. Windows：先試 `winget install yt-dlp`，失敗則 `pip install yt-dlp`

安裝後再次確認版本，確保可用。

### Step 2 — 查詢可用字幕清單

```bash
yt-dlp --list-subs --skip-download "<URL>"
```

解析輸出，分為兩類：
- **手動字幕（Manual subtitles）** — 人工上傳，品質較高
- **自動字幕（Automatic captions）** — YouTube 機器產生，品質參差

向教師簡要報告可用語言清單。若教師指定的語言不在列表中，建議最接近的替代方案。

### Step 3 — 擷取字幕與影片元資料

**字幕擷取**（手動優先，自動退回）：

```bash
# 嘗試手動字幕
yt-dlp --write-sub --sub-lang "<lang>" --sub-format vtt --skip-download \
  -o "/tmp/yt-sub-%(id)s" "<URL>"

# 若無手動字幕，退回自動字幕
yt-dlp --write-auto-sub --sub-lang "<lang>" --sub-format vtt --skip-download \
  -o "/tmp/yt-sub-%(id)s" "<URL>"
```

**語言 fallback chain**（依序嘗試）：
`zh-TW` → `zh-Hant` → `zh` → `en`

若教師指定了特定語言，則直接使用該語言，不走 fallback。

**影片元資料**：

```bash
yt-dlp --dump-json --skip-download "<URL>"
```

從 JSON 中提取：`title`、`channel`、`upload_date`、`duration`、`description`。

### Step 4 — 轉換為 Markdown

讀取擷取的 `.vtt` 檔案，依序執行以下清理：

1. 移除 VTT header（`WEBVTT`、`Kind:`、`Language:` 等開頭行）
2. 移除時間戳記行（格式：`00:00:00.000 --> 00:00:00.000`）
3. 移除位置標記（`align:start position:0%` 等）
4. 移除 HTML 標籤（`<c>`、`</c>`、`<font>` 等）
5. 移除自動字幕常見的逐字重複行（連續相同文字只保留一次）
6. 合併連續行為段落（以空行作為分段依據）
7. 若教師要求 `--timestamps`，在每段前保留對應的時間戳記（格式：`[MM:SS]`）

組合為 Markdown 輸出：

```markdown
---
title: "{影片標題}"
source_url: "{YouTube URL}"
channel: "{頻道名}"
language: "{字幕語言代碼}"
subtitle_type: "{manual 或 auto-generated}"
duration: "{片長，格式 MM:SS}"
extracted_date: "{今天日期 YYYY-MM-DD}"
tags:
  - subtitle
  - youtube
  - {科目 tag，若當前有載入 session}
aliases:
  - "{影片標題簡稱}"
---

# {影片標題}

> 來源：[{頻道名}]({YouTube URL})
> 語言：{字幕語言} | 類型：{手動/自動產生} | 片長：{duration}

---

{清理後的字幕全文，以段落呈現}
```

### Step 5 — 儲存檔案

決定儲存路徑：

| 情境 | 路徑 |
|------|------|
| 已載入班級/科目 session | `{workspace}/projects/class-{code}/content/{subject}/subtitles/{filename}.md` |
| 未載入任何 session | `{workspace}/content/subtitles/{filename}.md` |

**檔名格式：** `{YYYYMMDD}-{sanitized-title}-{lang}.md`

sanitized 規則：移除特殊字元，空格轉連字號，限 60 字元。

若目標資料夾不存在，自動建立（`mkdir -p`）。

### Step 6 — 清理暫存檔

```bash
rm -f /tmp/yt-sub-*
```

> **Windows：** 改為清理 `%TEMP%\yt-sub-*`

### Step 7 — 回報結果

向教師報告：

```
字幕擷取完成。

影片：{title}
頻道：{channel}
語言：{語言}（{手動/自動}字幕）
字數：約 {字數} 字 / {段落數} 段
儲存：{完整檔案路徑}

需要我根據這份字幕設計教學活動嗎？說「設計一堂課」即可。
```

## 驗證清單

- [ ] yt-dlp 已安裝且可用
- [ ] 字幕檔案已成功擷取
- [ ] Markdown 格式正確（frontmatter 完整、段落清晰）
- [ ] 暫存檔已清理
- [ ] 檔案存放路徑正確且可在 Obsidian 中開啟

## 注意事項

- 全程使用繁體中文回報進度
- 部分影片無字幕（無手動也無自動），此時告知教師並建議：使用其他有字幕的版本，或考慮使用語音轉文字工具
- 自動字幕品質參差不齊（尤其中文），AI 應在回報時提醒教師檢查內容正確性
- 字幕內容為影片作者的智慧財產，僅供教學素材參考使用
- 此技能**不下載影片本身**，僅擷取字幕文字
- 若同一影片需要多語言字幕，可多次執行並指定不同 `--lang`
- Windows 的暫存路徑使用 `%TEMP%` 替代 `/tmp/`
