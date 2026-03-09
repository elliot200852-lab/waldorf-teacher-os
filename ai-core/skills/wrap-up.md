---
name: wrap-up
description: >
  對話收尾一站完成：同步進度 → Cowork 編譯 → Obsidian 標籤修正 → Git 存檔推送 → 工作摘要 → 開機提醒。
  凡是表達「對話結束」「工作告一段落」語意的指令，都應觸發此技能。
triggers:
  - 收工
  - 存檔
  - 收尾
  - 結束今天
  - 儲存
  - 儲存進度
  - 更新進度
  - commit
  - 上傳
  - 備份今天的工作
  - 今天工作結束
  - 讓我們結束吧
  - 今天到這裡
  - 下班
  - 工作告一段落
requires_args: false
args_format: "[選填：班級代碼 科目] (例: 9c english)"
---

# skill: wrap-up — 收工（進度同步 + 存檔推送）

對話結束時的一站式收尾流程。整合原 `session-end`（進度同步）與 `save`（Git 存檔）的所有功能。

教師說「收工」「存檔」「今天到這裡」或任何表達結束語意的指令，都執行此技能。

## 參數

選填：班級代碼 + 科目（例：`9c english`）。
- 若未提供，從本次對話內容自動推斷涉及的班級與科目
- 若無法推斷且有教學進度變動，才詢問
- 若本次對話未涉及任何教學工作（純筆記、純設定），Step 1 自動跳過

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：`git rev-parse --show-toplevel`，或從當前工作目錄推斷。

## 執行步驟

### Step 1 — 進度同步

讀取相關的 session.yaml，從本次對話中提取變動並寫入。

**1a. 讀取現有狀態**

讀取：`{workspace}/projects/class-[班級]/[科目]/session.yaml`

```
# {workspace} 路徑解析：
# 從 acl.yaml 取得當前使用者的 workspace 路徑。
# Codeowner：workspaces/Working_Member/Codeowner_David/
# 教師：workspaces/Working_Member/Teacher_{姓名}/
```

**1b. 掃描對話，提取變動**

從本次對話中，識別以下欄位是否有新資訊：

| 欄位 | 判斷依據 |
|------|---------|
| `current_position` | 這次工作推進到哪個區塊 / 步驟 / 單元 |
| `confirmed_decisions` | 教師確認的設計決策（主題選定、評量比例、單元架構等） |
| `next_action.description` | 下一次對話應從哪裡繼續 |
| `next_action.input_needed_from_teacher` | 下次開始前教師需要準備的事項 |
| `open_questions` | 尚未解決的問題，或新產生的問題 |
| `output_files` | 本次產出的 .md 檔案（路徑與版本號） |
| `last_updated` | 自動填入今天日期（YYYY-MM-DD） |

**1c. 產生 YAML diff 並寫入**

只列出有變動的欄位：

```yaml
# wrap-up diff｜class-[班級]｜[科目]｜[今天日期]
# 以下為有變動的欄位，其餘維持不變

session:
  last_updated: [今天日期]

  current_position:
    block: [值]          # 若有變動
    step: [值]           # 若有變動
    sub_block: [值]      # 若有變動
    unit_number: [值]    # 若有變動

  confirmed_decisions:   # 只附加新決策，不刪除舊項目
    - [新確認的決策]

  next_action:
    description: [下一步描述]
    input_needed_from_teacher: [教師需準備的事項，若無填 null]

  open_questions:        # 只附加新問題，已解決的從原列表移除
    - [待決問題]

  output_files:
    syllabus_versions:   # 若有新產出才更新
      - version: [vN]
        date: [YYYYMMDD]
        paths:
          class_view: [路徑]
          subject_view: [路徑]
```

- 若某欄位無變動，從 diff 中省略
- **直接寫入** session.yaml，不需額外確認（收工就是要存）
- `confirmed_decisions` / `open_questions` 採附加邏輯
- 若涉及多個班級/科目，逐一處理
- 若本次對話無任何可提取的變動，輸出「session.yaml 維持不變」

### Step 2 — Cowork 同步

自動執行 `ai-core/skills/sync-cowork.md` 的快速模式（只更新區塊三）。

具體操作：
1. 識別當前教師（git config user.email → acl.yaml → workspace 路徑）
2. 讀取 `ai-core/system-status.yaml` 和已更新的 session.yaml
3. 更新 `INSTRUCTIONS.md` 的「三、當前系統狀態」區塊
4. 更新 metadata header 的 `last_compiled` 日期
5. 輸出一行確認：「Cowork INSTRUCTIONS.md 區塊三已同步。」

**不需要詢問確認** — 這是自動延伸步驟。

特殊情境：
- 教師說「架構有改動」→ 改為完整模式（全區塊重編譯）
- `last_compiled` 超過 3 天且 Step 1 無變動 → 仍執行一次區塊三同步
- INSTRUCTIONS.md 不存在 → 提示先執行一次「同步 Cowork」

### Step 3 — Obsidian 標籤與索引

執行 `python3 setup/scripts/obsidian-check.py`（完整掃描，不加 flag）。

- 有未標籤的 .md → 自動加上 aliases frontmatter（根據路徑與內容前 30 行產生）
- 有未標籤的 .yaml → 自動加上中文標頭註解
- 有未收錄 HOME.md 的檔案 → 自動插入 `Good-notes/HOME.md` 對應區段
- 標籤/索引修正完成後，將修改的檔案加入 git 暫存區
- 全部正常 → 靜默通過（不輸出任何訊息）

詳細的標籤產生規則與 HOME.md 區段判斷邏輯，參見 `ai-core/skills/obsidian-sync.md`。

### Step 4 — Git 存檔與推送

**4a. 檢查變更**

執行 `git status`，確認是否有未儲存的更動。

- 若沒有任何更動 → 輸出「目前沒有新的更動，不需要存檔」，跳到 Step 5
- 若有更動 → 繼續

**4b. 產出 commit message**

- 若教師觸發時已提供說明（例如「收工，備註完成 Unit 2」）→ 直接使用
- 若未提供 → **AI 自行根據變更內容摘要產出簡潔中文備註，不詢問教師**

**4c. 執行存檔**

```bash
git add [相關檔案]
git commit -m "[中文備註]"
git push
```

- push 失敗 → 嘗試 `git pull --rebase` 後重試
- 仍失敗 → 用簡單語言說明狀況，建議聯絡 David
- pre-commit hook 攔截 → 向教師解釋哪些檔案超出授權範圍，跳到 Step 5
  - AI 可嘗試只 commit 授權範圍內的檔案（排除被攔截的檔案後重試）
  - 若全部被攔截 → 報告「Git 存檔跳過（權限不足）」，繼續 Step 5

**4d. 確認結果**

記錄 commit hash，供 Step 5 摘要使用。
不需要顯示原始 git 輸出，用中文摘要即可。

### Step 5 — 本次工作摘要

每次收工必輸出。表格格式：

```
**本次工作摘要**

| 項目 | 內容 |
|------|------|
| 產出檔案 | [新建/修改的 .md 列表] |
| YAML 變動 | [哪個 session.yaml 更新了哪些欄位] |
| Obsidian 修正 | [若有：N 個 .md 補 aliases、N 個加入 HOME.md] |
| Git | [commit hash] 已推送 |
```

若某項目為空（例如無 YAML 變動），從表格中省略該行。

### Step 6 — 跨平台開機提醒

每次收工必輸出，固定內容：

> **下次啟動新對話時：**
>
> **第一步：更新系統**
> 在終端機執行 `git pull origin main`，確保你有最新版本。
>
> **第二步：告訴 AI 開工**
> 說「開工」或「請讀取 `ai-core/AI_HANDOFF.md` 並依照載入序列初始化」。
> AI 會自動載入系統、報告進度，接續今天的工作。
>
> （使用 Claude Code 的教師可直接輸入 `/opening`，AI 會自動處理 git pull 與載入。）

此提醒在所有 AI 平台（Claude Code、Gemini、ChatGPT 等）皆適用。

## 注意事項

### 優雅降級原則（Graceful Degradation）

**核心規則：每一步失敗時，報告問題後繼續下一步。收工流程不因單一步驟失敗而中斷。**

各步驟的降級行為：

| 步驟 | 可能失敗原因 | 降級處理 |
|------|------------|---------|
| Step 1 進度同步 | session.yaml 不存在、路徑錯誤 | 報告「找不到 session.yaml，進度未同步」→ 繼續 Step 2 |
| Step 2 Cowork 同步 | INSTRUCTIONS.md 不存在、模板缺失 | 報告「Cowork 未同步」→ 繼續 Step 3 |
| Step 3 Obsidian 修正 | obsidian-check.py 不存在、Python 缺失 | 報告「Obsidian 檢查跳過」→ 繼續 Step 4 |
| Step 4 Git 存檔 | pre-commit hook 攔截、push 失敗 | 報告具體原因 → 繼續 Step 5（摘要中註明 Git 未完成） |
| Step 5 工作摘要 | （不會失敗） | 必定輸出，包含前面步驟的成功/失敗狀態 |
| Step 6 開機提醒 | （不會失敗） | 必定輸出 |

Step 5 和 Step 6 是純輸出步驟，必定執行。即使前面所有步驟都失敗，教師仍會看到完整摘要和下次開機提醒。

### 其他

- `confirmed_decisions` 與 `open_questions` 採**附加邏輯**：新增項目，不清空舊項目
- `open_questions` 中若某問題本次已解決，從列表移除
- 不更新 `project.yaml`，除非教師明確要求
- Step 2 的 Cowork 同步是自動步驟，不計入「無可更新」的判斷
- Step 3 的 Obsidian 修正遵循 `obsidian-sync.md` 的命名規則與區段判斷
- Step 4 不顯示原始 git 輸出，用中文摘要
- Step 6 的跨平台提醒是固定輸出，確保非 Claude Code 環境的教師不會遺忘載入步驟
- 此技能取代原本的 `session-end` 和 `save` 兩個技能
