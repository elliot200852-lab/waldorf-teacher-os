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

## 執行架構（平行化）

收工流程分為四個 Phase，Phase A 內的兩個步驟可平行執行以節省時間：

```
Phase A（平行）：Step 1 進度同步（subagent）+ Step 3 Obsidian（subagent）
Phase B（序列）：Step 2 Cowork 同步（依賴 Step 1 的 session.yaml）
Phase C（序列）：Step 4 Git 存檔推送（依賴 Phase A + B 的所有檔案變更）
Phase D（純輸出）：Step 5 摘要 + Step 6 開機提醒 + Step 7 Session 邊界
```

**AI 執行指引（Claude Code 限定）：**

Phase A 時，主 agent 同時啟動兩個 subagent：

1. **Subagent A**（進度同步）：傳入本次對話的工作摘要（涉及的班級/科目/專案、確認的決策、下一步）+ session.yaml 路徑。Subagent 讀取 → 提取變動 → 寫入 → 回報。
2. **Subagent B**（Obsidian）：執行 obsidian-check.py → 補 aliases → 更新 marker → 回報。

**Subagent 回傳契約（MANDATORY）：**

```
Subagent A 回傳：
{
  "status": "success" | "partial" | "error",
  "changed_fields": ["current_position.block", "next_action.description", ...],
  "files_modified": ["projects/class-9c/english/session.yaml", ...],
  "error": null | "error message"
}

Subagent B 回傳：
{
  "status": "success" | "partial" | "error",
  "stats": { "md_labeled": 5, "yaml_labeled": 2, "home_updated": 3 },
  "files_modified": ["HOME.md", "stories/A-origins/A001/content.md", ...],
  "error": null | "error message"
}
```

**git add 同步規則：** Subagent 只修改檔案內容，**不執行 git add**。兩個 subagent 完成後，主 agent 統一執行 `git add`（使用兩方 `files_modified` 的合集），避免 git index 競爭條件。

兩個 subagent 完成後，主 agent 繼續 Phase B → C → D。

**非 Claude Code 平台（Gemini、ChatGPT）：** 無 subagent 能力，按 Step 1 → 2 → 3 → 4 → 5 → 6 → 7 序列執行。

---

## 執行步驟

### Step 1 — 進度同步（Phase A，可平行）

讀取相關的 session.yaml，從本次對話中提取變動並寫入。

**1a. 讀取現有狀態**

讀取：`{workspace}/projects/class-[班級]/[科目]/session.yaml`
或：`{workspace}/projects/[專案名]/session.yaml`（獨立專案，如 stories-of-taiwan）

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
| `last_updated` | 自動填入今天日期（YYYY-MM-DD，教師本地日期，不加時區後綴——所有教師在同一時區，無需複雜化） |

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
- 若涉及多個班級/科目，逐一處理。**降級規則：** 單一班級的 session.yaml 更新失敗（檔案不存在、格式錯誤等）→ 記錄該班級的錯誤 → 繼續處理其他班級 → Step 5 摘要中列出失敗項目。不因單一班級失敗而跳過所有進度同步
- 若本次對話無任何可提取的變動，輸出「session.yaml 維持不變」

### Step 2 — Cowork 同步（Phase B，依賴 Step 1）

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

### Step 3 — Obsidian 標籤與索引（Phase A，可平行）

執行 obsidian-check.py（完整掃描，不加 flag）。

**跨平台 Python 偵測：** 先嘗試 `python3`，若不存在再嘗試 `python`，確認版本 >= 3.8。

```bash
# macOS / Linux
if command -v python3 >/dev/null 2>&1; then
  python3 setup/scripts/obsidian-check.py
elif command -v python >/dev/null 2>&1; then
  python setup/scripts/obsidian-check.py
else
  echo "Python not found, skipping Obsidian check"
fi
```

```powershell
# Windows（PowerShell）
$py = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" }
      elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" }
      else { $null }
if ($py) { & $py setup/scripts/obsidian-check.py } else { Write-Output "Python not found, skipping" }
```

- 有未標籤的 .md → 自動加上 aliases frontmatter（根據路徑與內容前 30 行產生）
- 有未標籤的 .yaml → 自動加上中文標頭註解
- 有未收錄 HOME.md 的檔案 → 自動插入根目錄 `HOME.md` 對應區段
- 標籤/索引修正完成後，將修改的檔案加入 git 暫存區
- 全部正常 → 簡短回報：「Obsidian 檢查完成，無需修正。」（不再完全靜默，確保教師知道此步驟已執行）
- 部分修正 → 回報：「Obsidian 已修正 N 個檔案。」
- 部分失敗 → 回報：「Obsidian 修正完成，但以下檔案跳過：[清單]（原因：[原因]）。」
- **完成後更新 marker**（讓 session-guard hook 知道本 session 已執行）：
  - macOS/Linux：`touch .claude/.last-obsidian-check`
  - Windows：`python3 -c "from pathlib import Path; Path('.claude/.last-obsidian-check').touch()"`
  - 或直接用 Python：`Path('.claude/.last-obsidian-check').touch()`（AI 在任何平台都可執行）

詳細的標籤產生規則與 HOME.md 區段判斷邏輯，參見 `ai-core/skills/obsidian-sync.md`。

### Step 4 — Git 存檔與推送（Phase C，依賴 Step 1+2+3）

**4a. 檢查分支與變更**

```bash
# 1. 確認當前分支
git branch --show-current
```

- 若不在 `main` 分支 → 提醒教師：「目前在 [分支名] 分支，不是 main。要繼續在此分支 commit 嗎？」等待確認
- 若在 main → 繼續

```bash
# 2. 檢查是否有未儲存的更動
git status --short
```

- 若沒有任何更動 → 輸出「目前沒有新的更動，不需要存檔」，跳到 Step 5
- 若有更動 → 繼續

**4b. 產出 commit message**

- 若教師觸發時已提供說明（例如「收工，備註完成 Unit 2」）→ 直接使用
- 若未提供 → **AI 自行根據變更內容摘要產出簡潔中文備註，不詢問教師**

**commit message 格式：**
```
wrap-up: [一句話摘要]

涉及：[session.yaml 變動欄位 / Obsidian 修正數 / 其他變更摘要]
```

範例：
```
wrap-up: 9C 英文 week 5 完成，進度同步

涉及：session.yaml current_position + next_action、Obsidian 3 個 .md 補 aliases
```

**4c. 執行存檔**

```bash
git add [相關檔案]
git commit -m "[中文備註]"
git push
```

**Push 失敗處理（嚴格定義）：**

| 失敗原因 | 處理 | 重試上限 |
|---------|------|---------|
| 遠端有新 commit（branch behind） | `git pull --rebase origin main` → 若 rebase 成功 → 重試 push | 最多 2 次 |
| rebase 產生衝突 | `git rebase --abort`（還原到 rebase 前狀態）→ 報告教師「push 失敗：遠端有衝突，需手動處理」→ 跳到 Step 5 | 0（不重試） |
| 認證/網路問題 | 報告教師「push 失敗：[錯誤訊息]」→ 跳到 Step 5（commit 已完成，下次 push 即可） | 0 |
| pre-commit hook 攔截 | 讀取 hook 輸出，識別被攔截的檔案 → 嘗試排除被攔截檔案後重新 `git add` + `git commit` → 若全部被攔截 → 報告「Git 存檔跳過（權限不足）」→ 繼續 Step 5 | 1 次 |

**關鍵原則：commit 失敗不阻擋 Step 5-7 的輸出。遵循優雅降級。**

**4d. 確認結果**

記錄 commit hash，供 Step 5 摘要使用。
不需要顯示原始 git 輸出，用中文摘要即可。

### Step 5 — 本次工作摘要（Phase D，純輸出）

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

**Pattern 提煉提醒：** 摘要輸出後，若本次 session 涉及備課或教學設計工作，追加一句：
> 本次 session 有值得存成 pattern 的教學洞察嗎？說「存 pattern」我來提煉。

此提醒只在涉及教學工作的 session 出現。純系統工程 session 不出現。

### Step 6 — 跨平台開機提醒（Phase D，純輸出）

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

### Step 7 — Session 邊界判斷（Phase D，純輸出）

收工完成後，檢視本次 session 的工作量。若符合以下任一條件：
- 涉及 2 個以上不同工作線（如英文 + 導師 + 系統工程）
- 對話輪數已超過 20 輪
- 曾重新讀取先前已載入的檔案（表示 context 已被壓縮）
- 本次修改檔案數 > 30（大規模變更，context 負擔高）

→ 在收工摘要最後加上：
「本次 session 工作量較大，建議下次任務開新對話以確保載入品質。」

若不符合以上條件，不輸出此提醒。

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
| Step 7 Session 邊界 | （不會失敗） | 必定執行判斷，符合條件才輸出提醒 |

Step 5、Step 6、Step 7 是純輸出步驟，必定執行。即使前面所有步驟都失敗，教師仍會看到完整摘要、開機提醒和 session 邊界建議。

### 其他

- `confirmed_decisions` 與 `open_questions` 採**附加邏輯**：新增項目，不清空舊項目。**去重：** 新決策若與既有項目語意相同（大小寫不敏感、同義詞判斷），不重複附加
- `open_questions` 中若某問題本次已解決，從列表移除
- 不更新 `project.yaml`，除非教師明確要求
- Step 2 的 Cowork 同步是自動步驟，不計入「無可更新」的判斷
- Step 3 的 Obsidian 修正遵循 `obsidian-sync.md` 的命名規則與區段判斷
- Step 4 不顯示原始 git 輸出，用中文摘要
- Step 6 的跨平台提醒是固定輸出，確保非 Claude Code 環境的教師不會遺忘載入步驟
- 此技能取代原本的 `session-end` 和 `save` 兩個技能
