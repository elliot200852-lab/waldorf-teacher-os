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
2. `{workspace}/projects/stories-of-taiwan/taiwan_history_api.py` — 搜尋引擎
3. `{workspace}/projects/stories-of-taiwan/project.yaml` — 資料源狀態（API Key 等）

## 入口驗證（由 story-daily pipeline 強制執行）

啟動本技能前，必須確認以下條件全部滿足，否則回報 FAIL 並停止：

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

從 current-task.yaml 讀取 search_keywords 和 data_sources_priority，逐一搜尋：

```bash
# macOS / Linux — 範例
cd "{workspace}/projects/stories-of-taiwan"
python3 taiwan_history_api.py "搜尋關鍵字" --sources tcmb boch tm --format markdown --output /tmp/raw-materials.md
```

```powershell
# Windows（PowerShell）
cd "{workspace}\projects\stories-of-taiwan"
python taiwan_history_api.py "搜尋關鍵字" --sources tcmb boch tm --format markdown --output $env:TEMP\raw-materials.md
```

對每個 search_keyword 執行搜尋，合併結果。

### Step 2 — AI 輔助研究

API 搜尋只是起點。AI 必須進一步：

1. **網路搜尋**：用 WebSearch 補充 API 無法覆蓋的資料（特別是 archives、nhrm、tm 這些無 API 的來源）
2. **交叉比對**：同一事件至少找到兩個獨立來源
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

素材包存入 `{workspace}/projects/stories-of-taiwan/stories/[區塊]/[ID]/raw-materials.md`。

## 注意事項

- **有憑有據原則**：每個核心事實必須標註來源，不可憑 AI 訓練資料直接斷言
- API 搜尋可能無結果（特別是 BOCH 若仍維護中）——記錄失敗但不中斷流程
- 圖像授權不確定時標記「待確認」，不自動排除
- 搜尋間隔 0.3 秒，避免觸發頻率限制
- 所有臨時檔案使用 `tempfile.mkdtemp()` 或 `tempfile.gettempdir()`，不硬編碼 `/tmp/`
- 路徑使用 `pathlib.Path()`
