---
name: story-daily
description: >
  「臺灣的故事」每日全流程管線。一鍵觸發從選題到上傳的完整 7 步驟：
  自動編號 → 選題（story-planner）→ 素材搜尋（story-research）→ 撰寫三件套 + 黑板畫 prompt（story-writer）→
  品質檢查（story-verify）→ 組裝 HTML/PDF 並上傳 Google Drive（assemble-story.js）→ 歸檔索引（story-archive）。
  當教師提到臺灣的故事、每日臺灣的故事、寫一篇臺灣的故事、Daily Story of Taiwan、daily story、stories of taiwan 時觸發。
triggers:
  - 臺灣的故事
  - 每日臺灣的故事
  - 寫一篇臺灣的故事
  - Daily Story of Taiwan
  - daily story
  - stories of taiwan
platforms: [cowork, claude-code, gemini]
requires_args: false
version: 1.0.0
created: 2026-03-21
---

# skill: story-daily — 臺灣的故事・每日全流程管線

一鍵觸發完整的故事產製流程，從選題到上傳 Google Drive 全部自動化。
本技能是編排器（orchestrator），依序呼叫 5 個子技能 + 1 個 Node.js 腳本。

## 適用對象

David（管理員）。其他教師 clone Repo 後亦可使用。

## 適用平台

| 平台 | 排程方式 | 備註 |
|------|---------|------|
| Cowork | Scheduled Task（`stories-of-taiwan-daily`，Mon-Fri 10:30） | 全自動，需預先授權 osascript |
| Claude Code | 手動觸發（說「臺灣的故事」或 `/story-daily`） | Mac/Windows 均可直接執行 |
| 其他 AI | 手動觸發 + 讀取本檔案 | 需有檔案讀寫與網路搜尋能力 |
| 無 AI 環境 | 手動撰寫 5 份 .md → `node assemble-story.js` | 只需 Node.js |

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 前置條件

- Node.js 已安裝（assemble-story.js 所需）
- GWS CLI 已安裝並認證（上傳 Google Drive 所需；詳見 `ai-core/skills/gws-bridge.md`）
- `requests` Python 套件已安裝（story-research 的 API 搜尋所需）

## 讀取的檔案（啟動時）

1. `projects/stories-of-taiwan/project.yaml` — 專案進度
2. `projects/stories-of-taiwan/themes/theme-skeleton.yaml` — 主題骨架
3. `projects/stories-of-taiwan/index.yaml` — 已完成故事索引

---

## 執行步驟

### Step 0 — 自動編號

讀取 `index.yaml`，找出最新的 story ID，自動遞增：

**編號邏輯：**
- 每個區塊使用字母前綴：A = origins, B = indigenous, C = colonial, D = qing, E = japanese, F = modern, G = contemporary
- 區塊內流水號三位數：A001, A002, ..., A999
- 讀取 index.yaml 中該區塊最大編號，+1
- 若區塊內尚無故事，從 001 開始

**報告格式：**
```
下一篇故事編號：[ID]
區塊：[block_name] — [區塊標題]
區塊進度：已完成 [M] / 目標 [N] 篇
```

### Step 1 — 選題（story-planner）

讀取並執行 `ai-core/skills/story-planner.md`。

產出：`projects/stories-of-taiwan/current-task.yaml`（暫存選題結果）。

**自動模式**（排程觸發）：跳過教師確認，直接進入 Step 2。
**互動模式**（手動觸發）：向教師報告選題結果，等待確認。

### Step 2 — 素材搜尋（story-research）

讀取並執行 `ai-core/skills/story-research.md`。

產出：`stories/[區塊]/[ID]/raw-materials.md`。

注意：故事檔案使用子資料夾結構（`A001/raw-materials.md`，非 `A001-raw-materials.md`）。

### Step 3 — 撰寫三件套 + 黑板畫 prompt（story-writer）

讀取並執行 `ai-core/skills/story-writer.md`。

產出（全部存入 `stories/[區塊]/[ID]/`）：
- `content.md` — 故事正文 + 事實出處表
- `narration.md` — 教師說書稿
- `images.md` — 投影圖像清單 + 黑板畫步驟

**額外產出黑板畫 prompt：**

在三件套完成後，根據故事主題與視覺需求，撰寫 `chalkboard-prompt.md`：

```markdown
# 黑板畫 Prompt：[ID] [標題]

## English Prompt（Gemini 製圖用）

[200 字以內的英文 prompt，使用具象藝術語言描述構圖、色彩、光影、氛圍]

## 中文翻譯

[對應的中文翻譯]

## 迭代紀錄

| 版本 | 調整重點 | 結果 |
|------|---------|------|
| v1 | 初版 | 待評估 |

## 下載檔案名

（Gemini 產圖後手動填入）
```

**核心原則：概念先行，藝術補強。** prompt 描述的是一幅在黑色背景上用粉筆繪製的華德福風格黑板畫，畫面必須能傳達故事的核心意象。

### Step 4 — 品質檢查（story-verify）

讀取並執行 `ai-core/skills/story-verify.md`。

產出：`projects/stories-of-taiwan/reviews/[ID]-quality.md`。

- **PASSED** → 繼續 Step 5
- **NEEDS_REVISION** → 自動修正後重新檢查（最多重試 2 次），仍未通過則暫停等待教師
- **FAILED** → 暫停流程，通知教師

### Step 5 — 組裝 HTML/PDF 並上傳 Google Drive

執行 `assemble-story.js`，將 5 份 .md 檔 + 黑板畫圖片組裝成美化 HTML + PDF。

**指令：**

```bash
# macOS / Linux
node publish/scripts/assemble-story.js stories/[區塊]/[ID] --pdf --upload

# Windows（PowerShell）
node publish\scripts\assemble-story.js stories\[區塊]\[ID] --pdf --upload
```

**腳本的 5 項強制檢查清單：**
1. `content.md` — 故事正文 + 事實出處表
2. `narration.md` — 教師說書稿
3. `images.md` — 投影圖像清單
4. `chalkboard-prompt.md` — Gemini 中英文 prompt
5. `~/Downloads/{filename}` — 黑板畫圖檔（從 chalkboard-prompt.md 讀取檔名）

如果第 5 項（黑板畫圖檔）不存在：
- **自動模式**：產出 HTML/PDF 但不含黑板畫圖片，在報告中標記「待補圖」
- **互動模式**：提示教師先用 Gemini 產圖並下載

**上傳目標：** Google Drive 資料夾「台灣的故事」（ID: `1TBD6Xs-wVgqqlX3_13boy4xbBnjQ9LdY`）。

**GWS CLI 呼叫方式依平台而異（詳見 `ai-core/skills/gws-bridge.md`）：**
- Cowork：透過 osascript 橋接 Mac 執行
- Claude Code / 其他：直接在終端機執行 `gws drive +upload`

### Step 6 — 歸檔索引（story-archive）

讀取並執行 `ai-core/skills/story-archive.md`。

注意：`index.yaml` 中的 `files` 路徑需使用子資料夾格式：
```yaml
files:
  content: stories/A-origins/A001/content.md
  narration: stories/A-origins/A001/narration.md
  images: stories/A-origins/A001/images.md
```

### Step 7 — 完成報告

產出完成摘要：

```
=== 臺灣的故事・每日管線完成 ===
故事編號：[ID]
標題：[title]
區塊：[block] — [block_title]
品質：[PASSED/NEEDS_REVISION]
Google Drive：已上傳 ✓ / 未上傳（原因）
檔案：
  - stories/[block]/[ID]/content.md
  - stories/[block]/[ID]/narration.md
  - stories/[block]/[ID]/images.md
  - stories/[block]/[ID]/chalkboard-prompt.md
  - stories/[block]/[ID]/raw-materials.md
  - temp/[ID]-full.html
  - temp/[ID]-full.pdf
區塊進度：[M] / [N] 篇
全專案進度：[total] / [annual_target] 篇
===
```

---

## 子資料夾結構

每篇故事以獨立子資料夾存放：

```
stories/
  A-origins/
    A001/
      content.md
      narration.md
      images.md
      chalkboard-prompt.md
      raw-materials.md
    A002/
      ...
  B-indigenous/
    B001/
      ...
```

Repo 內只存 `.md` 檔案。黑板畫圖檔保留在本機 `~/Downloads/`，不進 Repo。

---

## 故障處理

| 狀況 | 處理 |
|------|------|
| API 搜尋全部失敗 | 僅用 AI 網路搜尋補充，在報告中標記 |
| story-verify 未通過 | 自動修正最多 2 次，仍失敗則暫停 |
| 黑板畫圖檔不存在 | 略過圖片，HTML/PDF 照產，標記「待補圖」 |
| GWS CLI 未安裝/未認證 | 跳過上傳，HTML/PDF 存本地，提示手動上傳 |
| Node.js 未安裝 | 跳過 Step 5（組裝），提示安裝 |
| index.yaml 不存在 | 從 A001 開始，建立新 index.yaml |

---

## 注意事項

- 本技能是編排器，不包含各子步驟的細節邏輯——細節全在子技能的正本中
- 排程模式下全部步驟自動推進；互動模式下 Step 1（選題）需教師確認
- 所有路徑使用 `path.join()` 或 `pathlib.Path()`，支援 macOS / Windows / Linux
- 不使用表情符號
