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
- 下一課位置 = total + 1（格式：AM001 ~ AM021 + TW01 ~ TW04）
- 若 total >= 25 → 回報「全部 25 課已完成」，結束 pipeline

根據位置決定課號 ID（含 4 堂台灣原住民神話穿插課）：

| 位置 | ID | 說明 |
|------|----|------|
| 1-7 | AM001-AM007 | 古文明神話 |
| 8 | TW01 | 台灣原住民神話（穿插） |
| 9-12 | AM008-AM011 | 古文明神話 |
| 13 | TW02 | 台灣原住民神話（穿插） |
| 14-18 | AM012-AM016 | 古文明神話 |
| 19 | TW03 | 台灣原住民神話（穿插） |
| 20-24 | AM017-AM021 | 古文明神話 |
| 25 | TW04 | 台灣原住民神話（穿插） |

判定邏輯：若位置 = 8 → TW01；位置 = 13 → TW02；位置 = 19 → TW03；位置 = 25 → TW04；其餘按 AM 序號遞增

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
met_keywords: "..."   # 1-2 個英文關鍵字，供 Met/Europeana API 使用
started_at: 2026-XX-XXTXX:XX:XX
```

**`met_keywords` 推導規則**（從 mythology_topic 取英文神祇或文明名稱）：

| Block | 推導邏輯 | 範例 |
|-------|----------|------|
| block-1-india | 神祇英文名（Brahma / Vishnu / Shiva / Rama / Krishna / Buddha） | `"Shiva"` |
| block-2-persia | `"Persia ancient"` 或神祇名（Ahura Mazda → `"Zoroastrian"`) | `"Persia ancient"` |
| block-3-babylon | `"Mesopotamia"` 或 `"Gilgamesh"` 或 `"Babylon"` | `"Mesopotamia"` |
| block-4-egypt | 神祇英文名（Ra / Osiris / Isis / Horus / Sekhmet） | `"Osiris"` |
| island-interludes | `"Taiwan"` — Met 結果通常極少，以 Europeana 為主 | `"Taiwan"` |

---

## Step 2 — 素材研究（2 agent 並行）

**Agent A（本地 — theme-skeleton 神話摘要）**：
- 讀取 `theme-skeleton.yaml` 的該課 core_image + taiwan_connection
- 讀取 `theme-skeleton.md` 的該 Block 核心主題、意識階段、台灣意識錨點表格
- 從 AI 訓練知識補充該神話的故事素材（注意：無 Kovacs 原文，明確標註為 AI 知識）

**Agent B（線上 — 神話與文化搜尋）**：

搜尋策略：英文取品質，中文補可讀性。至少 5 次搜尋。

**TW0X 特殊規則**：當 ID 以 TW 開頭時，搜尋策略翻轉——中文來源為主（3 次），英文為輔（2 次）：

- **中文搜尋（主力層，3 次）**：用中文關鍵字搜尋台灣原住民神話的在地資料
  - 來源優先序：原住民族委員會 → 原視界 insight.ipcf.org.tw → 國立台灣博物館 → 玉山國家公園 → 中文維基百科 → 台灣教師部落格
  - 目標：取得最完整的原住民族神話敘事、文化脈絡、在地知識

- **英文搜尋（補充層，2 次）**：用英文關鍵字搜尋學術與百科補充
  - 來源優先序：English Wikipedia → 學術資料庫
  - 目標：補充國際視角與學術引用

**AM0XX 標準規則**（非 TW 開頭時適用）：

- **英文搜尋（品質層，3 次）**：用英文關鍵字搜尋該神話的學術與百科資料
  - 來源優先序：Britannica → 學術資料庫 → English Wikipedia → 博物館網站 → Wikimedia Commons 圖片
  - 目標：取得最完整的神話敘事素材、事實數據、圖像 URL

- **中文搜尋（呈現層，2 次）**：用中文關鍵字專找台灣老師可用的延伸資源
  - 來源優先序：中文維基百科 → 台灣教師部落格 → 兒童百科 → 國家教育研究院 → 博物館中文導覽
  - 目標：找到老師能直接閱讀的中文頁面，不追求學術深度，追求可讀性與延伸價值

- 每筆來源標記 `[中]` 或 `[英]`，中文來源排在前面

**合併產出**：`raw-materials.md`（Step 2.5 之前完成）
- theme-skeleton 核心意象摘要
- AI 知識補充的神話素材（明確標註來源為 AI 訓練知識）
- 台灣文化對應資料（中文）
- 資料來源（至少 5 筆含 URL，其中至少 2 筆為中文來源）
- 台灣文化呼應（1-2 段）

**Checkpoint**：raw-materials.md > 500 字 + 至少 5 筆 URL（其中 ≥ 2 筆中文）→ 否則 FAIL

---

## Step 2.5 — Museum API 圖像搜尋

**Step 2 完成後立即執行，不等 Step 3。**

從 `current-task.yaml` 讀取 `met_keywords`，執行 Met Museum API：

```bash
python3 setup/scripts/museum_resource_pipeline.py \
  "[met_keywords]" \
  --source met \
  --count 8
```

產出位置：`temp/museum_[met_keywords]_[日期]/museum-materials.yaml`

執行完成後，將 YAML 複製到故事資料夾：

```bash
cp temp/museum_[met_keywords]_[日期]/museum-materials.yaml \
   workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM0XX/museum-materials.yaml
```

**若有 Europeana Key**（環境變數 `EUROPEANA_KEY` 或 `current-task.yaml` 的 `europeana_key` 欄位）：

```bash
python3 setup/scripts/museum_resource_pipeline.py \
  "[met_keywords]" \
  --source europeana \
  --europeana-key "$EUROPEANA_KEY" \
  --count 5
```

將 Europeana YAML 的 `items` 追加到 `museum-materials.yaml` 的 `items` 列表中。

**Fallback**：
- API 失敗 / 回傳 0 件 / 連線逾時 → 跳過，`museum-materials.yaml` 不產出，Step 3 Agent E 改用純 WebSearch
- 不重試、不中斷 pipeline

---

## Step 3 — 撰寫 7 件套（3 agent 並行）

**Agent C（撰寫主力）**：
- 產出：`content.md`（800 字說書稿）+ `chalkboard-prompt.md`（黑板畫 Prompt）
- content.md 必須含 `## 故事本文` 和 `## 事實出處` 表格

**Agent D（教學精要）**：
- 產出：`waldorf-teaching.md`（300 字）
- **AM0XX 標準**：含三段：華德福教學指引（此課的意識發展重點）/ 施泰納框架對應 / 台灣文化呼應
- **TW0X 特殊**：含三段：華德福教學指引（此課的意識發展重點）/ 南島語族教學備註 / 台灣文化呼應。「南島語族教學備註」須明確說明：施泰納的意識演化框架不應強加於台灣原住民文化之上，應以尊重在地知識體系的方式進行教學

**Agent E（圖像與來源）**：
- 產出：`images.md`（至少 3 張圖 + URL + 授權，圖片描述用中文）+ `references.md`（所有來源）
- references.md 分兩區：`## 教師延伸閱讀（中文）` + `## 學術參考（英文）`，中文區在前
- **圖像取材**：以故事內容與教學需求為主，找能幫孩子理解故事的圖。若 `museum-materials.yaml` 存在，從中挑選與課程相關的館藏圖（標注 `[Met Museum CC0]` 或 `[Europeana]`）作為備選之一，與 Wikimedia Commons 及 WebSearch 結果並列評估，取最合適的。不相關的館藏圖不納入。

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

**4.11** 在 `~/Downloads/` 找到最新下載的圖檔（搜尋策略：AncientMyths-AM0XX 或 AncientMyths-TW0X → Gemini_Generated_Image → 任何含課號的圖），重命名為 `AncientMyths-AM0XX-chalkboard.png`（TW0X 課則為 `AncientMyths-TW0X-chalkboard.png`）

**Checkpoint**：`~/Downloads/AncientMyths-[課號]-chalkboard.png` 存在且 > 50KB → 否則重試（最多 3 次）

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

**黑板畫圖檔**：`~/Downloads/AncientMyths-[課號]-chalkboard.png`（base64 嵌入）

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
2. 更新 `project.yaml` 的 `story_count`（total + by_block），total 上限 25
3. 更新 `project.yaml` 的 `current_position`
4. 刪除 `current-task.yaml`

---

## Checkpoint 矩陣

| 轉換 | 驗證項 | 失敗等級 |
|------|--------|----------|
| 0→1 | project.yaml + theme-skeleton.yaml 存在 | FAIL |
| 1→2 | current-task.yaml 非空（含 met_keywords） | FAIL |
| 2→2.5 | raw-materials.md > 500 字 + 至少 5 筆 URL（其中 ≥ 2 筆中文） | FAIL |
| 2.5→3 | museum-materials.yaml 存在（API 有結果）或標記 skip（API 失敗） | WARN（不阻擋） |
| 3→4 | 6 檔全部存在 + chalkboard-prompt 含 `## English Prompt` | FAIL |
| 4→5 | ~/Downloads/AncientMyths-[課號]-chalkboard.png > 50KB | FAIL（重試 3 次）|
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
Pipeline 完成：[課號] [標題]

Step 0-1 前置+選題：PASS
Step 2   素材研究：PASS — raw-materials.md [N] 字
Step 3   撰寫：    PASS — 7 件套全部到位
Step 4   黑板畫：  PASS — ~/Downloads/AncientMyths-[課號]-chalkboard.png
Step 5   組裝：    PASS
  HTML：     temp/beautify-[課號]-古文明神話完整版.html
  PDF：      temp/[課號]-古文明神話完整版.pdf
  黑板畫嵌入：embedded
  事實超連結：[N] 個 URL
  投影圖像：  [N] 張
  Waldorf：  present
  參考來源：  [N] 筆
Step 6   Drive：   PASS — HTML + PDF 已上傳
Step 7   歸檔：    PASS — index.yaml + project.yaml 已更新

區塊進度：Block X [M/N]
全專案進度：[total] / 25 篇
```
