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
version: 2.0.0
created: 2026-03-21
updated: 2026-03-22
---

# skill: story-daily — 臺灣的故事・每日全流程管線

一鍵觸發完整的故事產製流程，從選題到上傳 Google Drive 全部自動化。
本技能是編排器（orchestrator），依序呼叫 5 個子技能 + 1 個 Node.js 腳本。

---

## 授權模型（AUTHORIZATION MODEL）

**本技能啟動後，以下操作已獲得完整預授權，AI 不得在執行中逐一詢問使用者確認：**

- 瀏覽器操作（開啟 Gemini、輸入 prompt、下載圖片）
- osascript 橋接（Mac 檔案重命名、Node.js 腳本執行、GWS CLI 上傳）
- Google Drive 上傳（目標資料夾：「台灣的故事」）
- Repo 內所有檔案的讀取與寫入

**唯一需要使用者確認的節點：Step 1（選題）互動模式下的主題確認。**

AI 在執行過程中若因工具層面的權限對話框而中斷，應自行重試，不得停下來詢問教師。

---

## 強制完成規則（MANDATORY COMPLETION RULES）

**此技能觸發後，AI 必須完成所有 8 個步驟，不得中途停止。**

每個步驟完成後，AI 必須檢查該步驟的「完成條件」。若條件未滿足，回報 FAIL 並說明原因——但不得跳過後續步驟嘗試。

**pipeline 完成定義：** Step 7 的完成報告中，所有步驟狀態為 PASS，HTML + PDF 已上傳 Google Drive。

若 AI 在任何步驟因 context window 耗盡而需要開新 session，必須：
1. 將當前進度寫入 `pipeline-status.yaml`
2. 明確告知教師「pipeline 未完成，需在新 session 中繼續」
3. 新 session 啟動後，讀取 `pipeline-status.yaml`，從中斷處繼續

---

## 資料流總覽（DATA FLOW MAP）

```
Step 0-1: plan
  輸入：index.yaml, theme-skeleton.yaml
  輸出：current-task.yaml
  存放：projects/stories-of-taiwan/

Step 2: research
  輸入：current-task.yaml
  輸出：raw-materials.md
  存放：stories/[block]/[ID]/

Step 3: write
  輸入：raw-materials.md
  輸出：content.md, narration.md, images.md, chalkboard-prompt.md
  存放：stories/[block]/[ID]/

Step 4: verify
  輸入：content.md, narration.md, images.md, raw-materials.md
  輸出：reviews/[ID]-quality.md
  存放：projects/stories-of-taiwan/reviews/

Step 5: gemini（瀏覽器操作）
  輸入：chalkboard-prompt.md 中的 English Prompt
  操作：開啟 Gemini → 貼入 prompt → 等待生成 → 下載圖片 → 重命名
  輸出：AssemblyStory-[ID]-chalkboard.png
  存放：~/Downloads/（不進 Repo）

Step 6: assemble
  輸入（5 項）：
    1. stories/[block]/[ID]/content.md
    2. stories/[block]/[ID]/narration.md
    3. stories/[block]/[ID]/images.md
    4. stories/[block]/[ID]/chalkboard-prompt.md（含下載檔名指向 ~/Downloads/）
    5. ~/Downloads/AssemblyStory-[ID]-chalkboard.png
  額外輸入：stories/[block]/[ID]/raw-materials.md（URL 超連結來源）
  設計規範：ai-core/reference/stitch-design-brief.md + publish/templates/waldorf-base.html
  執行指令（強制帶旗標）：
    node publish/scripts/assemble-story.js stories/[block]/[ID] --pdf --upload
  輸出：
    1. temp/beautify-[ID]-完整版.html
    2. temp/[ID]-完整版.pdf
    3. Google Drive「台灣的故事」資料夾（HTML + PDF）

Step 7: archive
  輸入：content.md（提取 metadata）
  輸出：更新 index.yaml, project.yaml
  清理：刪除 current-task.yaml
```

**關鍵規則：**
- 黑板畫圖檔只存 ~/Downloads/，不複製到 Repo
- assemble-story.js 必須帶 `--pdf --upload` 旗標，不可省略
- 事實出處表必須有可點擊的超連結（來自 raw-materials.md 的 URL）
- 投影圖像清單必須完整呈現（標題、描述、來源、URL、授權、展示時機）
- chalkboard-prompt.md 中的「下載檔名」欄位必須在 Step 5 完成後立即填入

---

## 步驟間 Checkpoint 矩陣（MANDATORY CHECKPOINT MATRIX）

**每個步驟啟動前，AI 必須驗證前一步驟的產出。驗證未通過 → 立即回報 FAIL 並停止 pipeline（除非標記 WARN）。**

| 轉換點 | 驗證項目 | 失敗等級 |
|--------|---------|---------|
| Step 0→1 | `index.yaml` 存在且可解析；`theme-skeleton.yaml` 存在 | FAIL → 停止 |
| Step 1→2 | `current-task.yaml` 存在 + `story_id`、`title`、`sub_theme`、`search_keywords` 欄位非空 | FAIL → 停止 |
| Step 2→3 | `raw-materials.md` 存在 + 字數 > 500 + 「資料來源」段落至少 3 筆含 URL 的來源 | FAIL → 停止 |
| Step 3→4 | `content.md` 存在且字數 > 300；`narration.md` 存在；`images.md` 存在且至少 1 張主圖；`chalkboard-prompt.md` 存在且含 `## English Prompt` 段落 | FAIL → 停止 |
| Step 4→5 | `reviews/[ID]-quality.md` 存在 + 總評狀態為 PASSED 或 NEEDS_REVISION（FAILED → 停止） | FAIL → 停止 |
| Step 5→6 | `~/Downloads/AssemblyStory-[ID]-chalkboard.png` 存在 + 檔案大小 > 50KB；`chalkboard-prompt.md` 下載檔名欄位已填入 | WARN → 跳過圖片繼續組裝，標記「待補圖」 |
| Step 6→7 | `temp/beautify-[ID]-完整版.html` 存在；`temp/[ID]-完整版.pdf` 存在；HTML 中 source URLs > 0；HTML 中 Images > 0；Drive 上傳成功回傳 file ID | FAIL → 停止 |
| Step 7→8 | `index.yaml` 中已存在該 story_id 的條目；`current-task.yaml` 已刪除 | WARN → 繼續但在報告中標記 |

**Checkpoint 執行方式：**
- AI 在進入每個新步驟前，逐項檢查上表對應的驗證項目
- 檢查結果以 `[CHECKPOINT Step X→Y] PASS / FAIL / WARN: 原因` 格式輸出
- FAIL 等級：立即停止 pipeline，寫入 `pipeline-status.yaml`，回報教師
- WARN 等級：記錄問題，繼續執行，在 Step 8 完成報告中標記

---

## 排程模式 fallback（SCHEDULED MODE FALLBACK）

排程任務（Cowork Scheduled Task）在無人值守的環境下執行，可能遇到以下工具不可用的情況：

| 情境 | fallback 行為 |
|------|-------------|
| Claude in Chrome 不可用（Step 5） | 跳過 Step 5，將 `pipeline-status.yaml` 標記 `chalkboard: pending`；Step 6 組裝時使用純文字替代方案（無黑板畫嵌入），HTML/PDF 照常產出並上傳 |
| osascript 橋接不可用 | 跳過所有需要 osascript 的操作（圖片讀取、Mac 端檔案操作）；改用 VM 內可用的 Node.js 直接執行組裝 |
| GWS CLI 不可用 | 跳過 Drive 上傳，HTML/PDF 存入 `temp/`，在 `pipeline-status.yaml` 標記 `drive_upload: pending` |
| 任何步驟 FAIL | 寫入 `pipeline-status.yaml`（含 FAIL 步驟、原因、已完成步驟列表），下次手動 session 啟動時提示教師 |

**`pipeline-status.yaml` 格式：**
```yaml
story_id: A004
pipeline_version: 2.0.0
started_at: 2026-03-22T10:30:00
mode: scheduled
steps:
  step_0_1: { status: PASS }
  step_2:   { status: PASS }
  step_3:   { status: PASS }
  step_4:   { status: PASS }
  step_5:   { status: SKIP, reason: "Claude in Chrome unavailable" }
  step_6:   { status: PASS, note: "No chalkboard image embedded" }
  step_7:   { status: PASS }
pending_actions:
  - "chalkboard: 需手動執行 Step 5 並重新組裝"
  - "drive_upload: 需確認 HTML/PDF 已上傳"
```

---

## 適用對象

David（管理員）。其他教師 clone Repo 後亦可使用。

## 適用平台

| 平台 | 排程方式 | 備註 |
|------|---------|------|
| Cowork | Scheduled Task（`stories-of-taiwan-daily`，Mon-Fri 10:30） | 全自動 |
| Claude Code | 手動觸發（說「臺灣的故事」或 `/story-daily`） | Mac/Windows |
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

### Step 5 — 黑板畫生成（Gemini 瀏覽器操作）

**此步驟已預授權，AI 直接操作，不詢問教師。**

操作流程：
1. 讀取 `chalkboard-prompt.md` 中的 English Prompt
2. 開啟 Gemini 瀏覽器分頁（或使用已開啟的分頁）
3. 點擊輸入框 → 貼入 English Prompt → 送出
4. 等待圖片生成（通常 10-20 秒）
5. 點擊圖片放大 → 點擊下載按鈕
6. 透過 osascript 在 ~/Downloads/ 中找到最新的 Gemini 圖檔，重命名為 `AssemblyStory-[ID]-chalkboard.png`
7. 更新 `chalkboard-prompt.md` 的「下載檔名」欄位

**完成條件：** ~/Downloads/ 中存在 `AssemblyStory-[ID]-chalkboard.png`，且 `chalkboard-prompt.md` 的下載檔名欄位已填入。

**圖檔存放規則：** 只存在 ~/Downloads/，不複製到 Repo。assemble-story.js 直接從 ~/Downloads/ 讀取。

### Step 6 — 組裝 HTML/PDF 並上傳 Google Drive

執行 `assemble-story.js`，將 5 份 .md 檔 + 黑板畫圖片組裝成美化 HTML + PDF。

**渲染規範：** 遵循 `ai-core/skills/beautify.md` 的設計規範（四季視覺系統、字級間距、季節裝飾）。組裝腳本直接套用 `publish/templates/waldorf-base.html` 模板。

**指令（旗標為強制，不可省略）：**

```bash
# macOS / Linux（從 Repo 根目錄執行）
node publish/scripts/assemble-story.js stories/[區塊]/[ID] --pdf --upload

# Cowork VM（透過 osascript 橋接 Mac 執行）
osascript: cd [repo-path] && node publish/scripts/assemble-story.js [story-dir] --pdf --upload
```

**腳本的 6 項強制檢查清單：**
1. `content.md` — 故事正文 + 事實出處表（表中來源須有可點擊的 URL 超連結）
2. `narration.md` — 教師說書稿（含節奏表、段落指引）
3. `images.md` — 投影圖像清單（每張圖須有標題、描述、來源、URL、授權、展示時機）
4. `chalkboard-prompt.md` — Gemini 中英文 prompt + 下載檔名
5. `~/Downloads/AssemblyStory-[ID]-chalkboard.png` — 黑板畫圖檔（Step 5 已下載）
6. `raw-materials.md` — 提供 URL 超連結來源（選用但強烈建議）

**完成條件（全部必須滿足，否則回報 FAIL）：**
- HTML 輸出：`temp/beautify-[ID]-完整版.html` 存在
- PDF 輸出：`temp/[ID]-完整版.pdf` 存在
- 黑板畫：HTML 中 Drawing 狀態為 `embedded`
- 事實出處：HTML 中 source URLs 數量 > 0
- 投影圖像：HTML 中 Images 數量 > 0
- Google Drive：HTML + PDF 已上傳至「台灣的故事」資料夾

**上傳策略（upsert）：** 上傳前先搜尋 Drive 資料夾中同 storyId 的所有舊檔並刪除，再上傳新版。確保資料夾內每篇故事永遠只有最新的 HTML + PDF 各一份。此邏輯已內建於 assemble-story.js v2.0.0 的 `--upload` 流程中。

**上傳目標：** Google Drive 資料夾「台灣的故事」（ID: `1TBD6Xs-wVgqqlX3_13boy4xbBnjQ9LdY`）。

**GWS CLI 呼叫方式依平台而異（詳見 `ai-core/skills/gws-bridge.md`）：**
- Cowork：透過 osascript 橋接 Mac 執行
- Claude Code / 其他：直接在終端機執行 `gws drive +upload`

### Step 7 — 歸檔索引（story-archive）

讀取並執行 `ai-core/skills/story-archive.md`。

注意：`index.yaml` 中的 `files` 路徑需使用子資料夾格式：
```yaml
files:
  content: stories/A-origins/A001/content.md
  narration: stories/A-origins/A001/narration.md
  images: stories/A-origins/A001/images.md
```

### Step 8 — 完成報告

產出完成摘要（必須包含每一步的 PASS/FAIL 狀態）：

```
=== 臺灣的故事・每日管線完成 ===
故事編號：[ID]
標題：[title]
區塊：[block] — [block_title]

Pipeline 狀態：
  Step 0-1 選題：    [PASS/FAIL]
  Step 2   素材搜尋：[PASS/FAIL]
  Step 3   撰寫：    [PASS/FAIL]
  Step 4   品質檢查：[PASS/FAIL]
  Step 5   黑板畫：  [PASS/FAIL] — ~/Downloads/AssemblyStory-[ID]-chalkboard.png
  Step 6   組裝：    [PASS/FAIL]
    HTML：     [temp/beautify-[ID]-完整版.html]
    PDF：      [temp/[ID]-完整版.pdf]
    黑板畫嵌入：[embedded / not found]
    事實超連結：[N 個 URL]
    投影圖像：  [N 張]
    Google Drive：[已上傳 / 未上傳（原因）]
  Step 7   歸檔：    [PASS/FAIL]

檔案清單：
  - stories/[block]/[ID]/content.md
  - stories/[block]/[ID]/narration.md
  - stories/[block]/[ID]/images.md
  - stories/[block]/[ID]/chalkboard-prompt.md
  - stories/[block]/[ID]/raw-materials.md
  - temp/beautify-[ID]-完整版.html
  - temp/[ID]-完整版.pdf
  - ~/Downloads/AssemblyStory-[ID]-chalkboard.png

區塊進度：[M] / [N] 篇
全專案進度：[total] / [annual_target] 篇
===
```

**若任何步驟為 FAIL，AI 必須在報告中明確標示失敗原因，不得隱藏。**

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
