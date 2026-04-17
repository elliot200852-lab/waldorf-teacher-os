---
name: story-research
description: >
  「臺灣的故事」素材搜尋技能。接收 story-planner 的選題結果，呼叫 taiwan_history_api.py 搜尋多資料源，
  並以 AI 輔助研究補充無 API 來源的內容，產出原始素材包。
  當教師提到搜尋素材、找資料、查史料、搜集故事素材時觸發。
triggers:
  - 搜尋素材
  - 找資料
  - 查史料
  - story research
  - 搜集故事素材
  - 找臺灣資料
  - 搜尋臺灣故事
requires_args: false
---

# skill: story-research — 臺灣的故事・素材搜尋

接收 story-planner 產出的選題，透過 taiwan_history_api.py 與 AI 研究，蒐集有憑有據的原始素材。

## 適用對象

David（管理員）。

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 前置條件

- `requests` 已安裝（`pip install requests --break-system-packages`）
- story-planner 已產出 `current-task.yaml`，或教師直接提供主題

## 讀取的檔案

1. `{workspace}/projects/stories-of-taiwan/current-task.yaml` — 今日選題
2. `{workspace}/projects/stories-of-taiwan/taiwan_history_api.py` — 搜尋引擎（自動優先查詢 TCMB 本地索引）
3. `{workspace}/projects/stories-of-taiwan/project.yaml` — 資料源狀態
4. `ai-core/reference/corpus-taic.yaml` — 台灣主權語料庫（TAIC）查詢指引
5. `ai-core/reference/tcmb-local-index.yaml` — TCMB 本地索引查詢指引（53,000+ 筆，免網路）

## 入口驗證（由 story-daily pipeline 強制執行）

**權威來源：** `story-daily.md` Checkpoint 矩陣 Step 1→2 列。以下為快速參照，若有衝突以 checkpoint 矩陣為準。

1. `projects/stories-of-taiwan/current-task.yaml` 存在
2. `current-task.yaml` 中 `story_id`、`title`、`sub_theme`、`search_keywords` 欄位非空
3. `search_keywords` 至少包含 1 個關鍵字

## 執行步驟

### Step 0 — 前置檢查

```bash
# macOS / Linux
python3 -c "import requests; print('requests OK')"
```

```powershell
# Windows（PowerShell）
python -c "import requests; print('requests OK')"
```

若 requests 未安裝：

```bash
pip install requests --break-system-packages
```

### Step 1 — API 自動搜尋

從 current-task.yaml 讀取 search_keywords 和 data_sources_priority，逐一搜尋。
**TCMB 本地優先：** taiwan_history_api.py 在指定 `--sources tcmb` 時會自動先查本地 SQLite 索引（`~/.cache/teacheros/tcmb-local.db`），有結果即不打 live API。若本地索引不存在，先執行 `python3 tcmb_downloader.py --build --all`。

```bash
# macOS / Linux — 範例（TCMB API Key 已自動從 environment.env 讀取，不需手傳）
cd "{workspace}/projects/stories-of-taiwan"
python3 taiwan_history_api.py "搜尋關鍵字" --sources tcmb boch tm --format markdown --output /tmp/raw-materials.md
```

```powershell
# Windows（PowerShell）
cd "{workspace}\projects\stories-of-taiwan"
python taiwan_history_api.py "搜尋關鍵字" --sources tcmb boch tm --format markdown --output $env:TEMP\raw-materials.md
```

對每個 search_keyword 執行搜尋，合併結果。

### Step 1.5 — TAIC 語料庫查詢

API 搜尋後、AI 輔助研究前，查詢台灣主權 AI 訓練語料庫（TAIC）作為補充與交叉驗證：

1. **載入查詢指引**：讀取 `ai-core/reference/corpus-taic.yaml`，確認與本次主題相關的資料分類
2. **網頁搜尋**：用 WebSearch 搜尋 `site:taic.moda.gov.tw [搜尋關鍵字]`，或直接瀏覽 https://taic.moda.gov.tw 以關鍵字查詢
3. **優先領域**：歷史文物、在地文化、原住民族三類與「臺灣的故事」最直接相關
4. **記錄結果**：找到的 TAIC 資料集記錄在素材包的「資料來源」區塊，標記 `[來源：TAIC]`、`[授權：開放資料/待確認]`

> **TAIC 與 taiwan_history_api 的關係：** 兩者互補而非取代。taiwan_history_api 提供即時精確查詢，TAIC 提供經品質篩選的統一格式語料與 taiwan_history_api 未涵蓋的來源（如原民會資料）。

### Step 2 — AI 輔助研究

API 搜尋與 TAIC 查詢是起點。AI 必須進一步：

1. **網路搜尋**：用 WebSearch 補充 API 與 TAIC 無法覆蓋的資料（特別是 archives、nhrm、tm 這些無 API 的來源）
2. **交叉比對**：同一事件至少找到兩個獨立來源（TAIC 可作為其中之一）
3. **圖像搜尋**：尋找 CC 授權或教育用途的歷史圖像、地圖
4. **地理定位**：確認事件發生地的現代地名與座標

### Step 3 — 整理素材包

將所有蒐集到的資料整理為統一格式：

```markdown
# 素材包：[故事 ID] [建議標題]

## 核心事實
- 時間：
- 地點：
- 人物：
- 事件摘要：（100 字內）

## 資料來源
1. [來源名稱] — [URL] — [可信度：高/中/低]
2. ...

## 可用圖像
1. [圖像描述] — [URL] — [授權：CC/教育用途/待確認]
2. ...

## 相關地圖
1. [地圖描述] — [URL/來源]

## 延伸素材（可選用）
- 相關人物傳記
- 同時期其他事件
- 現代遺跡/紀念

## AI 研究備註
- 資料缺口：（哪些面向找不到資料）
- 爭議點：（若有不同史觀的詮釋）
- 建議敘事角度：
```

## 輸出格式

素材包存入 `{workspace}/projects/stories-of-taiwan/stories/[區塊]/[ID]/[ID]-raw-materials.md`。

## 注意事項

- **有憑有據原則**：每個核心事實必須標註來源，不可憑 AI 訓練資料直接斷言
- API 搜尋可能無結果（特別是 BOCH 若仍維護中）——記錄失敗但不中斷流程
- 圖像授權不確定時標記「待確認」，不自動排除
- 搜尋間隔 0.3 秒，避免觸發頻率限制
- 所有臨時檔案使用 `tempfile.mkdtemp()` 或 `tempfile.gettempdir()`，不硬編碼 `/tmp/`
- 路徑使用 `pathlib.Path()`
