---
name: sync-cowork
description: 更新 INSTRUCTIONS.md（Cowork folder instructions）。從 YAML 系統編譯最新狀態快照，讓 Cowork 的上下文保持同步。
triggers:
  - 同步 Cowork
  - 更新 Cowork
  - 編譯 instructions
  - sync cowork
requires_args: false
---

# skill: sync-cowork — 編譯 Cowork Folder Instructions

從 YAML 系統的 Source of Truth 編譯 `INSTRUCTIONS.md`，讓 Cowork 在下次開啟資料夾時載入最新上下文。

## 根目錄

`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`

## 使用時機

1. **自動觸發：** session-end 的 Step 5 會呼叫此技能的「快速模式」，只更新區塊三（當前狀態）
2. **手動觸發：** David 說「同步 Cowork」或「更新 Cowork」時執行完整重編譯
3. **架構變動後：** 當 DI 框架、技能系統、YAML 結構有重大改動，David 會說「這次架構有改動，Cowork 全區塊都要更新」

## 執行步驟

### Step 1 — 判斷更新範圍

| 觸發情境 | 更新範圍 |
|----------|---------|
| session-end 自動呼叫 | 只更新**區塊三**（當前系統狀態） |
| David 說「同步 Cowork」 | 更新**區塊三** + 檢查區塊一/二/四是否需要調整 |
| David 說「架構有改動」 | **全部六個區塊**重新編譯 |

### Step 2 — 讀取 Source of Truth

依更新範圍讀取：

**區塊三（必讀）：**
- `ai-core/system-status.yaml`
- 各班 `working/*.yaml`（掃描有變動的班級）

**區塊一（身份錨點，架構更新時讀取）：**
- `ai-core/teacheros.yaml`

**區塊二（檔案地圖，架構更新時讀取）：**
- 掃描目錄結構，確認有無新增班級、科目、資料夾

**區塊四（品質標準，架構更新時讀取）：**
- `projects/_di-framework/project.yaml`
- `projects/_di-framework/content/strategy-output-quality-standard.md`

### Step 3 — 編譯寫入

讀取現有 `INSTRUCTIONS.md`，只更新對應區塊的內容。

**區塊三更新規則：**
- 從 `system-status.yaml` 提取各班進度
- 從 `working/*.yaml` 提取最新的 `current_position`、`next_action`
- 更新 metadata header 的 `last_compiled` 日期
- 保持其他區塊不變

**全區塊更新規則：**
- 區塊一：從 `teacheros.yaml` 重新濃縮身份描述（保持簡潔，不超過原有篇幅）
- 區塊二：重新掃描目錄結構，更新檔案地圖
- 區塊三：同上
- 區塊四：從 DI 框架重新提取核心規則與品質標準
- 區塊五：檢查角色邊界是否需要調整（例如新增了 Cowork 可以做的事）
- 區塊六：維持不變（除非更新協議本身有變）

### Step 4 — 確認

輸出變更摘要：

```
Cowork INSTRUCTIONS.md 已更新：
- 區塊三：9C 英文 Block [X] Step [Y] → [next_action]
- last_compiled: [今天日期]
[如有其他區塊變動，列出]
```

不需要詢問確認（因為是從 Source of Truth 編譯，不涉及判斷）。

## 注意事項

- INSTRUCTIONS.md 是**編譯產物**，永遠從 YAML 生成，不反向寫回 YAML
- 如果 YAML 和 INSTRUCTIONS.md 有衝突，以 YAML 為準
- 區塊三的格式要保持簡潔——Cowork 載入時不需要看到完整 YAML 欄位，只需要人類可讀的進度摘要
- 保持 INSTRUCTIONS.md 的 HTML 註解 metadata header（last_compiled、source_files 等），供追蹤用
