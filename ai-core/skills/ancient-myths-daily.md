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
Step 4   Gemini 黑板畫生成（gemini-chalkboard，12 子步驟）
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

**合併產出**：`[ID]-raw-materials.md`（Step 2.5 之前完成）
- theme-skeleton 核心意象摘要
- AI 知識補充的神話素材（明確標註來源為 AI 訓練知識）
- 台灣文化對應資料（中文）
- 資料來源（至少 5 筆含 URL，其中至少 2 筆為中文來源）
- 台灣文化呼應（1-2 段）

**⚠️ 資料來源格式（嚴格遵守，供 assemble 腳本 URL 注入事實出處表使用）**：

```
1. **[key 與 [ID]-content.md 事實出處「來源」欄完全一致]**
   URL: https://...
   [中/英] 備考說明
```

- 例：[ID]-content.md 事實出處表「來源」欄寫 `Britannica — Ramayana (Indian epic)`，[ID]-raw-materials.md 的 key 就必須是 `**Britannica — Ramayana (Indian epic)**`
- **禁止**：`**名稱** — 來源 — https://...`（腳本無法正確解析此格式的 key）
- **禁止**：`1. **名稱**\n來源 — URL`（URL 前無 `URL:` 標頭）

**Checkpoint**：[ID]-raw-materials.md > 900 字 + 至少 5 筆 URL（其中 ≥ 2 筆中文）→ 否則 FAIL

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
   workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM0XX/AM0XX-museum-materials.yaml
```

**若有 Europeana Key**（環境變數 `EUROPEANA_KEY` 或 `current-task.yaml` 的 `europeana_key` 欄位）：

```bash
python3 setup/scripts/museum_resource_pipeline.py \
  "[met_keywords]" \
  --source europeana \
  --europeana-key "$EUROPEANA_KEY" \
  --count 5
```

將 Europeana YAML 的 `items` 追加到 `[ID]-museum-materials.yaml` 的 `items` 列表中。

**Fallback**：
- API 失敗 / 回傳 0 件 / 連線逾時 → 跳過，`[ID]-museum-materials.yaml` 不產出，Step 3 Agent E 改用純 WebSearch
- 不重試、不中斷 pipeline

---

## Step 3 — 撰寫 7 件套（3 agent 並行）

**Agent C（撰寫主力）**：
- 產出：`[ID]-content.md`（800 字說書稿）+ `[ID]-chalkboard-prompt.md`（黑板畫 Prompt）
- [ID]-content.md 必須含 `## 故事本文` 和 `## 事實出處` 表格
- **[ID]-content.md 格式模板（嚴格遵守，不可偏離）**：

```markdown
---
aliases:
  - "AM0XX [標題]"
id: AM0XX
title: [標題]
block: block-X-[文明]
lesson: [課號數字]
age_group: 10-11
consciousness: [該課的意識階段描述]
---

## 故事本文

[800 字說書稿，以 --- 分隔段落]

---

## 事實出處

| 事實 | 來源 |
|------|------|
| [完整事實描述，含括號標註文獻名稱與年代] | [來源名稱] — [具體頁面或條目] |
```

- **事實出處表規則**：
  - 「事實」欄必須是完整句子，描述故事中引用的具體事實，括號標註原始文獻名與年代
  - 「來源」欄格式：`來源網站名稱 — 具體條目名稱`（例：`Wikipedia — Matsya`、`Britannica — Manu`）
  - 禁止只列關鍵字（如「五兄弟姓名、神聖父系」）——必須寫成完整描述
  - 至少 5 筆事實出處

**Agent D（教學精要）**：
- 產出：`[ID]-waldorf-teaching.md`（300 字）
- **AM0XX 標準**：含三段：華德福教學指引（此課的意識發展重點）/ 施泰納框架對應 / 台灣文化呼應
- **TW0X 特殊**：含三段：華德福教學指引（此課的意識發展重點）/ 南島語族教學備註 / 台灣文化呼應。「南島語族教學備註」須明確說明：施泰納的意識演化框架不應強加於台灣原住民文化之上，應以尊重在地知識體系的方式進行教學

**Agent E（圖像與來源）**：
- 產出：`[ID]-images.md`（至少 3 張圖 + **必須有 `- 連結：https://...`** + 授權，圖片描述用中文）+ `[ID]-references.md`（所有來源）
- **[ID]-images.md 每張圖必須包含以下欄位（缺少連結即 FAIL）**：
  ```
  ### 圖 N：[標題]
  - 說明：[說明文字]
  - 圖片描述：[中文圖像描述]
  - 授權：[Met Museum CC0 / Wikimedia Commons CC / ...]
  - 連結：https://...    ← 必填，Met 圖用 source_url，Wikimedia 用 commons 頁面 URL
  - 建議使用時機：[說書哪個段落]
  ```
  Met Museum 圖的連結從 `[ID]-museum-materials.yaml` 的 `source_url` 欄位取得（格式：`https://www.metmuseum.org/art/collection/search/[id]`）
- [ID]-references.md 分兩區：`## 教師延伸閱讀（中文）` + `## 學術參考（英文）`，中文區在前
- **[ID]-references.md 格式模板（嚴格遵守，不可偏離）**：

```markdown
---
aliases:
  - "AM0XX [標題] 參考資料"
---

# AM0XX 參考來源：[標題]

## 教師延伸閱讀（中文）

1. 來源名稱 — 條目標題 — https://url — 類型
2. 來源名稱 — 條目標題 — https://url — 類型

## 學術參考（英文）

3. Source Name — Entry Title — https://url — 類型
4. Source Name — Entry Title — https://url — 類型
```

- **[ID]-references.md 格式規則**：
  - 每一筆為單行，格式固定：`序號. 來源名稱 — 條目標題 — URL — 類型標籤`
  - 類型標籤限用：`百科`、`學術`、`教學`、`官方`
  - 禁止多行描述、禁止 `URL:` 前綴格式、禁止 `**粗體**` 標題、禁止 `[已驗證]` 標記、禁止 `適用：` 描述段落
  - 不設「圖像來源」「原住民族文化對照來源」「紙本書籍」「需要進一步驗證的來源」等額外區塊——所有來源一律歸入中文或英文兩區
  - 組裝腳本 `assemble-ancient-myths.js` 的 `parseReferences()` 以格式 A 解析，偏離格式會導致來源丟失

- **圖像取材**：以故事內容與教學需求為主，找能幫孩子理解故事的圖。若 `[ID]-museum-materials.yaml` 存在，從中挑選與課程相關的館藏圖（標注 `[Met Museum CC0]` 或 `[Europeana]`）作為備選之一，與 Wikimedia Commons 及 WebSearch 結果並列評估，取最合適的。不相關的館藏圖不納入。

**主線程**：三者完成後，品質自檢 → `[ID]-quality-report.md`

**Checkpoint**：執行自動驗證腳本

```bash
node publish/scripts/validate-story.js AM0XX
```

- 全部 PASS → 繼續 Step 4
- 有 FAIL → 當場修正，修正後重新執行，不得進入 Step 4
- 只有 WARN（廢棄欄位等相容性提示）→ 記錄，不阻擋 Step 4

驗證範圍：7 件套存在、frontmatter 必填欄位、故事本文字數（>800）、事實出處筆數（≥5）、[ID]-images.md 圖數與連結、[ID]-raw-materials.md 字數與 URL、**交叉驗證**（[ID]-content.md 來源 key ↔ [ID]-raw-materials.md）

---

## Step 4 — 黑板畫生成

**執行共用技能 `ai-core/skills/gemini-chalkboard.md`。**

參數：
- STORY_ID = [當前課號，如 AM007]
- STORY_DIR = 故事目錄完整路徑
- VERSION = [版本標記，若有]

完整操作流程（12 步）、圖片內容驗證 checkpoint、重試邏輯、排程 fallback 均定義於 `gemini-chalkboard.md`。

**Checkpoint**：gemini-chalkboard.md 的 Checkpoint 全部通過（檔案存在 + > 50KB + 圖片內容驗證 PASS + 下載檔名已登錄）→ 否則重試（最多 3 次）。排程模式下若 Claude in Chrome 不可用 → SKIP，標記 `chalkboard: pending`。

---

## Step 5 — 組裝 HTML/PDF

```bash
node publish/scripts/assemble-ancient-myths.js \
  workspaces/Working_Member/Codeowner_David/projects/ancient-myths-grade5/stories/AM0XX \
  --pdf --upload
```

**組裝清單（5 項必需 + 1 選用）**：
1. `[ID]-content.md` — 故事正文 + 事實出處表
2. `[ID]-waldorf-teaching.md` — Waldorf 教學指引
3. `[ID]-images.md` — 投影圖像清單
4. `[ID]-chalkboard-prompt.md` — Gemini 中英文 prompt
5. `[ID]-references.md` — 參考來源
6. `[ID]-raw-materials.md` — 素材包（選用，供 URL 交叉匹配）

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

**上傳成功後，觸發 CreatorHub 網站部署：**

```bash
gh workflow run deploy-channel.yml
```

此指令觸發 GitHub Actions 的 sync + deploy 流程（~3 分鐘），確保新故事立即出現在 CreatorHub 網站上。若 `gh` 指令不可用或上傳被跳過，不觸發。

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
| 2→2.5 | [ID]-raw-materials.md > 900 字 + 至少 5 筆 URL（其中 ≥ 2 筆中文） | FAIL |
| 2.5→3 | [ID]-museum-materials.yaml 存在（API 有結果）或標記 skip（API 失敗） | WARN（不阻擋） |
| 3→4 | `node validate-story.js AM0XX` 全 PASS | FAIL |
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
Step 2   素材研究：PASS — [ID]-raw-materials.md [N] 字
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
