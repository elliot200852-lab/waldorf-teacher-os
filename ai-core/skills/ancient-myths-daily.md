---
name: ancient-myths-daily
description: >
  五年級古文明神話每日故事管線。從選題到上傳的完整 8 步驟：
  確認下一課 → 素材研究（theme-skeleton + 神話 WebSearch）→ 撰寫 7 件套 → 品質檢查 →
  Gemini 黑板畫生成 → 組裝 HTML/PDF → 上傳 Google Drive → 歸檔索引。
triggers:
  - 古文明神話故事
  - 每日古文明
  - 寫一篇古文明
  - ancient myths daily
  - ancient myths story
platforms: [cowork, claude-code, gemini]
requires_args: false
version: 1.0.0
created: 2026-03-25
---

# 五年級古文明神話每日故事管線 v1.0.0

## 專案路徑

```
workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/
```

## 預授權操作

以下操作已獲得完整預授權，AI 必須直接執行，不得逐一詢問：

- 瀏覽器操作（開啟 Gemini、點擊工具選單、選擇「建立圖像」、輸入 prompt、下載圖片）
- osascript 橋接（Mac 檔案重命名、Node.js 腳本執行、GWS CLI 上傳）
- Google Drive 上傳（目標資料夾 ID：`1lUTzAcmJ5UuI3njADbJ-a3HSLl3aUhpC`）
- Repo 內所有檔案的讀取與寫入

**唯一需要確認**：無（全自動模式）

---

## Pipeline 步驟總覽

```
Step 0   前置確認（project.yaml + theme-skeleton.yaml）
Step 1   建立任務（current-task.yaml + 子資料夾）
Step 2   素材研究（2 agent 並行：theme-skeleton + 神話文化搜尋）
Step 3   撰寫 7 件套（3 agent 並行）
Step 4   Gemini 黑板畫生成（11 子步驟）
Step 5   組裝 HTML/PDF（assemble-ancient-myths.js）
Step 6   上傳 Google Drive
Step 7   歸檔（index.yaml + project.yaml）
```

---

## Step 0 — 前置確認

讀取 `project.yaml`：
- `story_count.total` = 已完成數
- 下一課號 = total + 1（格式：AM001 ~ AM021）
- 若 total >= 21 → 回報「全部 21 課已完成」，結束 pipeline

讀取 `theme-skeleton.yaml`，取出該課的：
- title, mythology_topic, block, core_image, taiwan_connection, art_response

---

## Step 1 — 建立任務

1. 建立 `stories/AM0XX/` 子資料夾
2. 寫入 `current-task.yaml`：

```yaml
lesson_id: AM0XX
title: "..."
mythology_topic: "..."
block: block-X-...
taiwan_connection: [...]
search_keywords: [...]
started_at: 2026-XX-XXTXX:XX:XX
```

---

## Step 2 — 素材研究（2 agent 並行）

**Agent A（本地 — theme-skeleton 神話摘要）**：
- 讀取 `theme-skeleton.yaml` 的該課 core_image + taiwan_connection
- 讀取 `theme-skeleton.md` 的該 Block 核心主題、意識階段、台灣意識錨點表格
- 從 AI 訓練知識補充該神話的故事素材（注意：無 Kovacs 原文，明確標註為 AI 知識）

**Agent B（線上 — 神話與文化搜尋）**：
- WebSearch 搜尋該文明的神話資料（至少 3 次搜尋）
- 搜尋目標：神話原文英譯/學術解讀/台灣對照文化/Wikimedia Commons 圖片 URL
- 來源優先序：大英百科 → 學術資料庫 → 維基百科 → 博物館網站 → iNaturalist

**合併產出**：`raw-materials.md`
- theme-skeleton 核心意象摘要
- AI 知識補充的神話素材（明確標註來源為 AI 訓練知識）
- 台灣文化對應資料（中文）
- 資料來源（至少 3 筆含 URL）
- 台灣文化趣事（1-2 句）

**Checkpoint**：raw-materials.md > 500 字 + 至少 3 筆 URL → 否則 FAIL

---

## Step 3 — 撰寫 7 件套（3 agent 並行）

**Agent C（撰寫主力）**：
- 產出：`content.md`（800 字說書稿）+ `chalkboard-prompt.md`（黑板畫 Prompt）
- content.md 必須含 `## 故事本文` 和 `## 事實出處` 表格

**Agent D（教學精要）**：
- 產出：`waldorf-teaching.md`（300 字）
- 含三段：華德福教學指引（此課的意識發展重點）/ 施泰納框架對應 / 台灣文化趣事

**Agent E（圖像與來源）**：
- 產出：`images.md`（至少 3 張圖 + URL + 授權）+ `references.md`（所有來源）

**主線程**：三者完成後，品質自檢 → `quality-report.md`

**Checkpoint**：6 檔全部存在 + chalkboard-prompt 含 `## English Prompt` → 否則 FAIL

---

## Step 4 — Gemini 黑板畫生成（11 子步驟）

**此步驟已完全預授權，AI 直接操作，不詢問教師。**

**4.1** 讀取 `chalkboard-prompt.md` 的 English Prompt

**4.2** 組合完整 prompt：第一行 `請你生成一張圖片`，空一行，接英文 prompt 全文

**4.3** 開啟 Gemini（導航至 `gemini.google.com`）→ 截圖確認已載入

**4.4** 確認 Pro 模式已選取 → 截圖確認。若非 Pro，點擊模型選擇器切換

**4.5** 點擊「工具」選單 → 截圖確認選單展開 → 點擊「建立圖像」→ 截圖確認已選取

**4.6** 點擊文字輸入區

**4.7** 貼入完整 prompt（含中文前綴）

**4.8** 按 Enter 送出

**4.9** 等待圖片生成（每 10 秒截圖檢查，最多等 30 秒）

**4.10** 圖片出現後 → 點擊圖片放大 → 點擊右上角下載按鈕（向下箭頭圖示）→ 等 3 秒確認下載完成

**4.11** 在 `~/Downloads/` 找到最新下載的圖檔（搜尋策略：AncientMyths-AM0XX → Gemini_Generated_Image → 任何含 AM0XX 的圖），重命名為 `AncientMyths-AM0XX-chalkboard.png`

**Checkpoint**：`~/Downloads/AncientMyths-AM0XX-chalkboard.png` 存在且 > 50KB → 否則重試（最多 3 次）

**排程模式 fallback**：若 Claude in Chrome 不可用 → SKIP Step 4，標記 `chalkboard: pending`，HTML/PDF 照常產出但不含黑板畫嵌入

---

## Step 5 — 組裝 HTML/PDF

```bash
node publish/scripts/assemble-ancient-myths.js \
  workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM0XX \
  --pdf --upload
```

**組裝清單（5 項必需 + 1 選用）**：
1. `content.md` — 故事正文 + 事實出處表
2. `waldorf-teaching.md` — Waldorf 教學指引
3. `images.md` — 投影圖像清單
4. `chalkboard-prompt.md` — Gemini 中英文 prompt
5. `references.md` — 參考來源
6. `raw-materials.md` — 素材包（選用，供 URL 交叉匹配）

**黑板畫圖檔**：`~/Downloads/AncientMyths-AM0XX-chalkboard.png`（base64 嵌入）

**輸出驗證（exit code 2 = 失敗）**：
- 故事段落數 > 0
- 事實出處表 > 0 且至少 1 筆有 URL
- 圖像清單 > 0
- Waldorf 教學指引存在
- 參考來源 > 0
- 黑板畫已嵌入（或 pending）

若失敗 → 讀取錯誤訊息修正 → 重試（最多 2 次）

---

## Step 6 — 上傳 Google Drive

assemble-ancient-myths.js 的 `--upload` 旗標自動處理：
- 上傳 HTML + PDF 到「古文明神話五年級」資料夾（ID：待建立）
- 舊檔 upsert（同 lesson_id 的舊檔先刪再傳）

**fallback**：GWS CLI 不可用 → 跳過上傳，HTML/PDF 存 `temp/`，標記 `drive_upload: pending`

---

## Step 7 — 歸檔

1. 追加 `index.yaml` 條目（id, title, block, mythology_topic, taiwan_connection, date_created, files, quality_check, drive, tags）
2. 更新 `project.yaml` 的 `story_count`（total + by_block）
3. 更新 `project.yaml` 的 `current_position`
4. 刪除 `current-task.yaml`

---

## Checkpoint 矩陣

| 轉換 | 驗證項 | 失敗等級 |
|------|--------|----------|
| 0→1 | project.yaml + theme-skeleton.yaml 存在 | FAIL |
| 1→2 | current-task.yaml 非空 | FAIL |
| 2→3 | raw-materials.md > 500 字 + 至少 3 筆 URL | FAIL |
| 3→4 | 6 檔全部存在 + chalkboard-prompt 含 `## English Prompt` | FAIL |
| 4→5 | ~/Downloads/AncientMyths-AM0XX-chalkboard.png > 50KB | FAIL（重試 3 次）|
| 5→6 | HTML + PDF 存在 + 黑板畫 base64 嵌入 | FAIL |
| 6→7 | Drive 上傳成功 | WARN |

---

## 排程模式 Fallback

| 情境 | fallback |
|------|----------|
| Claude in Chrome 不可用（Step 4） | SKIP 黑板畫，標記 pending，HTML/PDF 照產 |
| GWS CLI 不可用 | 跳過上傳，存本地 |
| 任何步驟 FAIL | 寫入 pipeline-status.yaml，下次提示教師 |

---

## 完成報告格式

```
Pipeline 完成：AM0XX [標題]

Step 0-1 前置+選題：PASS
Step 2   素材研究：PASS — raw-materials.md [N] 字
Step 3   撰寫：    PASS — 7 件套全部到位
Step 4   黑板畫：  PASS — ~/Downloads/AncientMyths-AM0XX-chalkboard.png
Step 5   組裝：    PASS
  HTML：     temp/beautify-AM0XX-古文明神話完整版.html
  PDF：      temp/AM0XX-古文明神話完整版.pdf
  黑板畫嵌入：embedded
  事實超連結：[N] 個 URL
  投影圖像：  [N] 張
  Waldorf：  present
  參考來源：  [N] 筆
Step 6   Drive：   PASS — HTML + PDF 已上傳
Step 7   歸檔：    PASS — index.yaml + project.yaml 已更新

區塊進度：Block X [M/N]
全專案進度：[total] / 21 篇
```
