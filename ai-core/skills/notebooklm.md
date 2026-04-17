---
name: notebooklm
description: 使用 NotebookLM MCP 產出教學素材（簡報、影片、語音、資訊圖表、測驗等九種產出）。需先完成 setup/reference/notebooklm-setup.md 的安裝。
triggers:
  - NotebookLM
  - NotebookLM 做簡報
  - NotebookLM 做影片
  - NotebookLM 做語音
  - NotebookLM 做資訊圖表
  - NotebookLM 做測驗
  - NotebookLM 做報告
  - NotebookLM 做心智圖
  - NotebookLM 做學習卡
  - NotebookLM 做資料表
  - NotebookLM 做 Podcast
requires_args: false
cross_platform: true
prerequisite: notebooklm-mcp（透過 nlm CLI 安裝，見 setup/reference/notebooklm-setup.md）
---

# skill: notebooklm — NotebookLM 教學素材產出

透過 NotebookLM MCP 工具，將教師提供的資料來源轉化為九種教學素材。

## 觸發條件

教師說出包含「NotebookLM」且帶有以下產出類型的語句：

| 教師說法 | 產出類型 | MCP artifact_type | 說明 |
|----------|---------|-------------------|------|
| NotebookLM 做語音 / 做 Podcast | 語音摘要 | audio | 兩人對談式音訊概覽 |
| NotebookLM 做簡報 | 簡報 | slide_deck | 可匯出 .pptx |
| NotebookLM 做影片 | 影片摘要 | video | Cinematic / Explainer / Brief |
| NotebookLM 做心智圖 | 心智圖 | mind_map | JSON 格式心智圖 |
| NotebookLM 做報告 | 報告 | report | Briefing Doc / Study Guide / Blog Post |
| NotebookLM 做學習卡 | 學習卡 | flashcards | 含難度分級 |
| NotebookLM 做測驗 | 測驗 | quiz | 多選題，可設題數與難度 |
| NotebookLM 做資訊圖表 | 資訊圖表 | infographic | 多種視覺風格 |
| NotebookLM 做資料表 | 資料表 | data_table | 結構化表格，可匯出 Sheets |

若教師只說「NotebookLM」未指定產出類型，AI 應詢問要做哪一種。

## 前置條件檢查

執行前先確認 NotebookLM MCP 已連接：

1. 嘗試呼叫 `notebook_list`
2. 若成功 → 繼續
3. 若失敗 → 讀取並執行 `ai-core/skills/notebooklm-setup.md`（安裝引導技能），引導教師完成安裝後再繼續。若教師說「我之前有安裝過，只是重新登入」，直接執行 `nlm login` 即可。

## 執行流程

### Step 1 — 確認資料來源

詢問教師要用什麼素材：

| 來源類型 | MCP source_type | 說明 |
|----------|----------------|------|
| 網頁 / YouTube | url | 直接貼 URL |
| 本機檔案（PDF、文字、音訊） | file | 提供檔案路徑 |
| 貼上文字 | text | 直接貼內容 |
| Google Drive 文件 | drive | 提供文件 ID |

若教師已在指令中提供（如「用這份 PDF 做簡報」），直接使用，不重複詢問。

### Step 2 — 建立或選擇 Notebook

**新建 Notebook：**
- 預設名稱格式：`{班級}-{科目}-{主題}`（如「9C-英文-Mango Street」）
- 使用 `notebook_create` 建立
- 使用 `source_add` 加入資料來源，設定 `wait=true` 等待處理完成

**使用既有 Notebook：**
- 若教師指定了 notebook 名稱，用 `notebook_list` 搜尋
- 找到 → 直接使用
- 找不到 → 詢問是否新建

### Step 3 — 產出素材

使用 `studio_create` 產出指定類型的素材：

```
studio_create(
  notebook_id=...,
  artifact_type=...,
  confirm=true,
  language="zh-TW"
)
```

**各類型的常用選項：**

| 類型 | 選項 | 預設值 |
|------|------|--------|
| audio | audio_format: deep_dive / brief / critique / debate | deep_dive |
| audio | audio_length: short / default / long | default |
| video | video_format: explainer / brief / cinematic | explainer |
| video | visual_style: auto_select / classic / whiteboard 等 | auto_select |
| infographic | orientation: landscape / portrait / square | landscape |
| infographic | infographic_style: auto_select / sketch_note / professional 等 | auto_select |
| slide_deck | slide_format: detailed_deck / presenter_slides | detailed_deck |
| report | report_format: Briefing Doc / Study Guide / Blog Post | Briefing Doc |
| quiz | question_count: 數字 | 5 |
| quiz | difficulty: easy / medium / hard | medium |
| flashcards | difficulty: easy / medium / hard | medium |

若教師未指定選項，使用預設值，不逐一追問。

### Step 4 — 等待產出完成

產出需要時間（音訊 / 影片可能數分鐘）。

1. 呼叫 `studio_status` 輪詢狀態
2. 每 30 秒檢查一次
3. 完成後進入 Step 5

等待期間告知教師：「正在產出 [類型]，通常需要 [估計時間]。完成後會自動下載。」

| 類型 | 預估時間 |
|------|---------|
| 簡報 / 資訊圖表 / 心智圖 / 報告 | 30 秒 ~ 1 分鐘 |
| 學習卡 / 測驗 / 資料表 | 30 秒 ~ 1 分鐘 |
| 語音摘要 | 2 ~ 5 分鐘 |
| 影片摘要 | 3 ~ 8 分鐘 |

### Step 5 — 下載到本機

使用 `download_artifact` 下載到對應資料夾：

**本機輸出路徑慣例：**

| 類型 | 路徑 |
|------|------|
| 語音摘要 | `~/Documents/NotebookLM/audio/` |
| 簡報 | `~/Documents/NotebookLM/slides/` |
| 影片摘要 | `~/Documents/NotebookLM/video/` |
| 心智圖 | `~/Documents/NotebookLM/mindmaps/` |
| 報告 | `~/Documents/NotebookLM/docs/` |
| 學習卡 | `~/Documents/NotebookLM/quizzes/` |
| 測驗 | `~/Documents/NotebookLM/quizzes/` |
| 資訊圖表 | `~/Documents/NotebookLM/infographics/` |
| 資料表 | `~/Documents/NotebookLM/sheets/` |

**檔名格式：** `{主題}-{類型}-{日期}.{副檔名}`
（如 `mango-street-簡報-20260405.pptx`）

**特殊匯出：**
- 報告、資料表可用 `export_artifact` 直接匯出為 Google Docs / Sheets
- 簡報可用 `download_artifact` 的 `slide_deck_format=pptx` 匯出為 .pptx

### Step 6 — 報告結果

下載完成後告知教師：

> [類型] 已完成，檔案存放於：
> `[完整路徑]`
>
> 要上傳到 Google Drive 嗎？

若教師說「要」→ 使用 gws CLI 上傳到 Drive（遵循現有 drive 技能的上傳慣例）。
若教師說「不用」→ 結束。

## 注意事項

- 所有產出的二進位檔案（音訊、影片、圖片、PDF）**不進 git repo**
- NotebookLM 的語言設定預設 `zh-TW`（繁體中文），教師可指定其他語言
- 同一個 notebook 可反覆產出不同類型的素材
- 教師可說「用上次那個 notebook」延續既有的 notebook 工作
- 跨平台：路徑使用 `~/Documents/`，macOS 和 Windows 均適用
- 若資料夾不存在，AI 應自動建立
