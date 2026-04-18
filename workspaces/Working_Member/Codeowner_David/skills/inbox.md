---
name: inbox
description: Codeowner GitHub 待辦收件匣。抓當前 open issues 與 PRs，依「David 需要動作」優先級分類。老師都在各自 workspace 分支工作看不見，這是集中視圖。
triggers:
  - inbox
  - 待辦
  - codeowner inbox
  - github 待辦
  - 我要做什麼
  - 有哪些需求
  - 誰有需求
  - 查 issue
  - 看看 issue
  - 看 pr
  - 收件匣
  - 需要我處理什麼
  - github 狀態
requires_args: false
---

# skill: inbox — Codeowner GitHub 收件匣

抓 repo 的 open issues 與 PRs，依據「David 需要動作」的緊急程度分類顯示。

## 背景

David 是 codeowner。老師採 v2.0 分支模型後各自在 `workspace/Teacher_xxx` 分支工作，
他看不見他們的進度與需求。GitHub 的 PR 與 Issue 是唯一的集中視圖，需要一個 skill
把所有 open 項目拉出來、依優先級分類、標記哪些需要他動作。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。

## 執行步驟

### Step 1 — 檢查 gh CLI

```bash
command -v gh >/dev/null && gh auth status 2>&1 | head -3
```

若未登入，回報 David 需要 `gh auth login` 並停止。

### Step 2 — 執行抓取腳本

```bash
python3 workspaces/Working_Member/Codeowner_David/scripts/inbox.py
```

### Step 3 — AI 後處理與建議

腳本已做了機械分類；AI 讀完輸出後還要做**人的判斷**：

1. **不逐條重述**輸出內容（David 自己會看分類表）
2. **主動標記 1-3 件最該先處理的**，優先級規則：
   - PR「已批准可合併」→ 直接 merge
   - PR「等我 review」> 3 天 → 拖久會卡老師工作
   - Issue「指派給我」> 7 天 → 應該有進展或關閉
   - Issue「安全通報」→ 需要判斷是真警報還是 false positive，若為後者建議批次關閉
3. 若 inbox 乾淨（統計行顯示「PR 0 · Issue 0」），直接回報「收件匣乾淨，沒有待動作項目」
4. 若發現大量同類 Issue（如多個 `identity-violation` label），主動提議批次處理

### Step 4 — 依 David 的決定執行後續動作

常見後續動作：
- **Merge PR**：`gh pr merge {N} --squash` 或 `--merge`（依情境）
- **關閉 Issue**：`gh issue close {N} --comment "..."`
- **批次處理**：for loop + gh issue close

執行前務必等 David 確認（尤其是批次操作）。

## 輸出格式

腳本原始輸出（表格）+ AI 的「建議優先動作」兩段。

## 設計備註

- 腳本不寫入任何檔案，純 read-only 抓取
- `gh issue list` / `gh pr list` 即時查詢 GitHub，不經本機快取
- 分類邏輯（PR_PRIORITY / ISS_PRIORITY）在腳本頂部可調整
- 「需要動作」統計只含 approved/need_review/ci_failing PR 與 mine/security Issue

## 何時不用

- David 已在 GitHub 網頁上手動處理某些項目時，等他處理完再跑（避免 race condition 或誤判）
- 如果他只是想問「還有 X 個 PR 嗎」這種簡單查詢，用 `gh pr list` 一行即可，不需要完整 inbox
