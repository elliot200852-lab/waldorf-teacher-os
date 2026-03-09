---
name: session-end
description: 對話結束前同步進度。掃描本次對話有變動的欄位，產生 YAML diff 並寫入該科目的 session.yaml。每次對話結束必須執行。
triggers:
  - 收尾
  - 更新進度
  - 結束今天
  - 同步進度
  - 儲存進度
requires_args: true
args_format: "[班級代碼] [科目] (例: 9c english、8a history)"
---

# skill: session-end — 對話收尾同步

從當前對話中提取有變動的資訊，產生 YAML diff，寫入該科目的 session.yaml。
只更新有變動的欄位，不重寫整份文件。

## 參數

班級代碼（9c / 8a / 7a）+ 科目（english / history / homeroom 等）。
未提供班級則詢問：「請問要收尾哪個班級的工作？」
未提供科目則詢問：「要收尾哪個科目？」或從本次對話內容推斷科目。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 執行步驟

### Step 1 — 讀取現有狀態

讀取：`{workspace}/projects/class-[班級]/[科目]/session.yaml`

# {workspace} 路徑解析：
# 從 acl.yaml 取得當前使用者的 workspace 路徑。
# Codeowner：workspaces/Working_Member/Codeowner_David/
# 教師：workspaces/Working_Member/Teacher_{姓名}/

### Step 2 — 掃描當前對話，提取變動

從本次對話中，識別以下欄位是否有新資訊或變動：

| 欄位 | 判斷依據 |
|------|---------|
| `current_position` | 這次工作推進到哪個區塊 / 步驟 / 單元 |
| `confirmed_decisions` | 這次對話中教師確認的設計決策（如：主題選定、評量比例、單元架構） |
| `next_action.description` | 下一次對話應從哪裡繼續 |
| `next_action.input_needed_from_teacher` | 下次開始前教師需要準備或決定的事項 |
| `open_questions` | 尚未解決的問題，或本次新產生的問題 |
| `output_files` | 本次產出了哪些 .md 檔案（記錄路徑與版本號） |
| `last_updated` | 自動填入今天日期（格式：YYYY-MM-DD） |

### Step 3 — 產生 YAML diff

只列出有變動的欄位。格式如下：

```yaml
# session-end diff｜class-[班級]｜[科目]｜[今天日期]
# 以下為有變動的欄位，其餘欄位維持不變

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

若某欄位在本次對話中沒有任何變動，從 diff 中完全省略。

### Step 4 — 確認並寫入

輸出 diff 後，詢問：

「確認寫入 `[科目]/session.yaml` 嗎？（是 / 否）」

- 若確認：將 diff 中的欄位合併寫入原檔案，不覆蓋未列出的欄位
- 若否定：保留 diff 供教師手動調整，不執行寫入

### Step 5 — 同步 Cowork Folder Instructions

寫入 session.yaml 後，**自動執行** `ai-core/skills/sync-cowork.md` 的快速模式（只更新區塊三）。

前提：`INSTRUCTIONS.md` 必須已存在（由首次 sync-cowork 或 quick-start 生成）。若不存在，提示教師先執行一次「同步 Cowork」。

具體操作：
1. 識別當前教師（git config user.email → acl.yaml → workspace 路徑）
2. 讀取 `ai-core/system-status.yaml` 和剛更新的 `{workspace}/projects/class-*/working/*.yaml`
3. 更新 `INSTRUCTIONS.md` 的「三、當前系統狀態」區塊
4. 更新 metadata header 的 `last_compiled` 日期
5. 輸出一行確認：「Cowork INSTRUCTIONS.md 區塊三已同步。」

**不需要另外詢問確認** — 這是 session-end 的自動延伸步驟。

若本次工作涉及**架構變動**（新增班級、新增科目、修改 DI 框架、新增/修改技能），教師會說「這次架構有改動」，則改為執行 sync-cowork 的完整模式（從 INSTRUCTIONS.template.md 全區塊重編譯）。

### Step 5.5 — Obsidian 索引檢查

執行 `python3 setup/scripts/obsidian-check.py --count-only`

若有未標籤或未收錄的檔案，在收尾摘要附加提醒：

> 「提醒：有 N 個新檔案尚未加入 Obsidian 索引。下次存檔時會自動處理，或說「sync Obsidian」立即處理。」

若全部正常，不輸出任何提醒（靜默通過）。

此步驟**只提醒，不自動修改檔案**。

### Step 6 — 跨平台開機提醒

進度同步完成後，輸出以下提醒：

> 📌 **下次啟動新對話時：**
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

- `confirmed_decisions` 與 `open_questions` 採**附加邏輯**：新增項目，不清空舊項目
- `open_questions` 中若某問題本次已解決，從列表移除
- 不更新 `project.yaml`，除非教師明確要求
- 若本次對話沒有任何可提取的變動，回應：「本次對話無可更新的狀態，session.yaml 維持不變。」但仍**檢查 INSTRUCTIONS.md 的 last_compiled 日期是否超過 3 天**，若超過則執行一次區塊三同步
- Step 5 的 Cowork 同步是自動步驟，不計入「無可更新」的判斷——即使 YAML 無變動，若 INSTRUCTIONS.md 過期仍會更新
- Step 6 的跨平台提醒是每次收尾的固定輸出，確保非 Claude Code 環境的教師不會遺忘載入步驟
