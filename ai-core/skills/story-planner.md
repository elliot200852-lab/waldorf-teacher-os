---
name: story-planner
description: >
  「臺灣的故事」每日選題技能。根據年度主題骨架與已完成索引，決定今日故事主題，產出搜尋關鍵字與子主題定位。
  當教師提到今天的故事、選題、下一篇故事、臺灣故事選題時觸發。
triggers:
  - 今天的故事
  - 選題
  - story plan
  - 臺灣故事選題
  - 故事選題
requires_args: false
---

# skill: story-planner — 臺灣的故事・每日選題

根據年度主題骨架（theme-skeleton.yaml）與故事總索引（index.yaml），自動選定今日故事主題，產出搜尋關鍵字供 story-research 使用。

## 適用對象

所有具 workspace 權限的教師。

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 讀取的檔案

1. `{workspace}/projects/stories-of-taiwan/project.yaml` — 專案進度
2. `{workspace}/projects/stories-of-taiwan/themes/theme-skeleton.yaml` — 主題骨架
3. `{workspace}/projects/stories-of-taiwan/index.yaml` — 已完成故事索引

## 入口驗證（由 story-daily pipeline 強制執行）

**權威來源：** `story-daily.md` Checkpoint 矩陣 Step 0→1 列。以下為快速參照，若有衝突以 checkpoint 矩陣為準。

啟動本技能前，必須確認以下條件全部滿足，否則回報 FAIL 並停止：

1. `projects/stories-of-taiwan/index.yaml` 存在且可被 YAML 解析
2. `projects/stories-of-taiwan/themes/theme-skeleton.yaml` 存在
3. `projects/stories-of-taiwan/project.yaml` 存在

## 執行步驟

### Step 1 — 定位當前區塊

讀取 project.yaml 和 theme-skeleton.yaml，確認：
- 當前季節對應的區塊（A-G）
- 該區塊下的子主題清單
- 每個子主題的目標篇數與已完成篇數（從 index.yaml 計算）

報告格式：
```
目前位於：區塊 [X] — [區塊標題]
子主題進度：
  - [子主題 1]：已完成 M / 目標 N 篇
  - [子主題 2]：已完成 M / 目標 N 篇
  ...
```

### Step 2 — 選定今日主題

選題邏輯：
1. 優先選擇進度最少的子主題（確保均衡推進）
2. 同一子主題內，按邏輯順序推進（如「島嶼誕生」先地質再考古）
3. 考慮與前一篇故事的敘事連貫性（讀取 index.yaml 最後一篇的 tags）

產出：
```yaml
today_story:
  block: A-origins
  sub_theme: 島嶼誕生
  suggested_title: "（AI 建議標題，教師可修改）"
  search_keywords:
    - 關鍵字 1
    - 關鍵字 2
    - ...
  data_sources_priority: [tcmb, boch, tm]
  connection_to_previous: "前一篇講了 XXX，今天延伸到..."
  story_id: A001  # 自動編號
```

### Step 3 — 確認或調整

向教師報告選題結果，等待確認。教師可以：
- 直接確認 → 進入 story-research
- 修改方向 → AI 重新選題
- 指定特定主題 → 覆蓋自動選題

## 輸出格式

YAML 格式的選題結果，存入 `{workspace}/projects/stories-of-taiwan/current-task.yaml`（暫存，story-archive 完成後清除）。

## 注意事項

- 不執行實際搜尋——搜尋由 story-research 處理
- 選題結果需經教師確認才進入下一步
- 若教師直接指定主題（如「今天寫霧社事件」），跳過自動選題，直接產出搜尋關鍵字
- 所有路徑使用 `pathlib.Path()`，不使用硬編碼路徑分隔符
