---
name: story-archive
description: >
  「臺灣的故事」歸檔與索引技能。將通過品質檢查的故事三件套正式歸檔，
  更新故事總索引（index.yaml）與專案進度（project.yaml）。
  當教師提到歸檔故事、更新索引、故事存檔時觸發。
triggers:
  - 歸檔故事
  - 歸檔
  - 更新故事索引
  - story archive
  - 故事存檔
  - 存入故事庫
requires_args: false
---

# skill: story-archive — 臺灣的故事・歸檔與索引

將通過品質檢查的故事正式歸入故事庫，更新索引與進度追蹤。

## 適用對象

David（管理員）。

## 根目錄

以 Repo 根目錄為基準。

## 讀取的檔案

1. `{workspace}/projects/stories-of-taiwan/current-task.yaml` — 今日任務
2. `{workspace}/projects/stories-of-taiwan/reviews/[ID]-quality.md` — 品質報告
3. `{workspace}/projects/stories-of-taiwan/index.yaml` — 現有索引
4. `{workspace}/projects/stories-of-taiwan/project.yaml` — 專案進度

## 前置條件

story-verify 已產出品質報告，且狀態為 PASSED 或教師手動確認歸檔。

## 入口驗證（由 story-daily pipeline 強制執行）

啟動本技能前，必須確認以下條件全部滿足，否則回報 FAIL 並停止：

1. `projects/stories-of-taiwan/reviews/[ID]-quality.md` 存在
2. 品質報告總評狀態為 PASSED 或 NEEDS_REVISION（FAILED → 拒絕歸檔）
3. `projects/stories-of-taiwan/current-task.yaml` 存在
4. `projects/stories-of-taiwan/index.yaml` 存在且可被 YAML 解析

## 執行步驟

### Step 1 — 確認歸檔資格

讀取品質報告，確認狀態：
- PASSED → 直接歸檔
- NEEDS_REVISION → 需教師確認才歸檔
- FAILED → 拒絕歸檔，提示需修正

### Step 2 — 更新故事總索引

在 `index.yaml` 的 `stories` 列表追加一筆：

```yaml
- id: A001
  title: 故事標題
  block: A-origins
  sub_theme: 島嶼誕生
  era: 史前
  location: 臺東卑南
  date_created: 2026-04-01
  files:
    content: stories/A-origins/A001/content.md
    narration: stories/A-origins/A001/narration.md
    images: stories/A-origins/A001/images.md
  sources: [tcmb, boch]
  quality_check: passed
  tags: [考古, 遺址, 卑南, 史前文化]
```

更新 `total_stories` 計數。

### Step 3 — 更新專案進度

在 `project.yaml` 的 `story_count` 中，更新對應區塊的計數。

### Step 4 — 清理暫存

刪除 `current-task.yaml`（已完成的任務不需保留）。
保留 `raw-materials.md`（作為來源追溯的備份）。

### Step 5 — 報告歸檔結果

```
已歸檔：[ID] — [標題]
區塊 [X] 進度：[已完成] / [目標] 篇
全專案進度：[總數] / [年度目標] 篇
```

## 輸出格式

- 更新 `index.yaml`（追加條目 + 更新計數）
- 更新 `project.yaml`（更新 story_count + last_updated）
- 刪除 `current-task.yaml`

## 注意事項

- 只更新 YAML 中有變動的區塊，不重寫全部
- 歸檔操作是冪等的——重複執行不會產生重複條目（以 story ID 為唯一鍵）
- 所有路徑使用 `pathlib.Path()`
- YAML 讀寫使用 Python `yaml` 模組（`pip install pyyaml --break-system-packages`）
