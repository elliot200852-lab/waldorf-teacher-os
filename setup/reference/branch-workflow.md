---
aliases:
  - "一師一分支工作流"
  - "Branch Workflow Guide"
title: TeacherOS v2.0 — 一師一分支工作流程
date: 2026-04-17
audience: 所有教師（Codeowner 與 Teacher 角色共用）
---

# TeacherOS v2.0 — 一師一分支工作流程

## 核心觀念（30 秒版）

從 v2.0 開始，每位教師在 GitHub 上有一條**專屬分支**：

```
workspace/Teacher_林詩閔
workspace/Teacher_劉佳芳
workspace/Teacher_郭耀新
...（每位教師一條）
```

**你永遠不會直接 push 到 main。**
main 是所有人共享的基準，只有 David 能合併。
你的日常工作 100% 在自己的分支上進行。

這樣做的好處：
- 你的實驗、草稿、半成品不會影響到其他教師
- 別人的改動也不會打斷你的工作
- 需要整合時，走 Pull Request（PR）正式審核流程

---

## 你的分支怎麼運作

### Clone 之後第一次

`bash setup/start.sh`（Mac）或 `.\setup\start.ps1`（Windows）會自動：

1. 偵測你的 GitHub username
2. 從 `ai-core/acl.yaml` 找到你對應的分支名
3. 自動 checkout 到 `workspace/Teacher_你的名字`

如果分支還沒建，AI 會自動從 main 建一條給你。

### 日常開工

對 Claude Code 說「**開工**」，AI 做的事：

1. `git fetch origin` — 拉最新資訊
2. `git pull origin workspace/Teacher_你的名字` — 更新你自己的分支
3. （如果 main 有新東西）`git merge origin/main` — 把 main 的新更新合進你的分支
4. 載入系統檔案與班級 session
5. 報告上次工作位置

**你要做的只有說「開工」，其他都是 AI 處理。**

### 日常收工

對 Claude Code 說「**收工**」，AI 做的事：

1. 把你今天的改動 commit 到你的分支
2. `git push origin workspace/Teacher_你的名字`
3. 更新 session.yaml 的進度錨點

**你的工作只進你的分支，不會碰到 main。**

---

## 什麼時候會動到 main

只有在兩種情況：

### 情況 A：你的工作需要合併進 main

例如：你寫的教案或技能其他教師也想用，或 David 想把它併進系統共通層。

你說「**發 PR**」或「**合併申請**」，AI 會：
1. 確認你當前在自己的分支、已推送
2. 用 `gh pr create` 開一個 Pull Request
3. 指定 David 為審核者（CODEOWNERS 自動生效）
4. 給你 PR 連結

David 審核通過後合併。合併後你自己分支下次「開工」會自動同步新的 main。

### 情況 B：David 更新了系統檔案

例如：AI_HANDOFF.md、技能正本、ACL 有更新。

你不需要做任何事——下次「開工」時，AI 會自動把 main 的新內容 merge 到你的分支。
如果有衝突（極少），AI 會停下來問你。

---

## 分支上可以做什麼

**可以（而且應該）：**
- 任何備課、教案、教學紀錄、學生觀察
- 個人技能（`workspaces/你的名字/skills/` 下的 .md）
- 個人偏好設定（`teacheros-personal.yaml`）
- 實驗性的 prompt、筆記、草稿

**不可以（會被 GitHub Action 擋下）：**
- 修改別人的 workspace（`workspaces/另一位老師/`）
- 修改系統核心（`ai-core/`、`setup/`、`.github/`）
  → 這些一定要走 PR 由 David 審核

---

## 常見操作對照表

| 你想做的事 | 對 Claude Code 說 |
|---|---|
| 開始今天的工作 | 開工 |
| 存檔（commit + push 到自己分支）| 收工 |
| 把工作合併進 main | 發 PR / 合併申請 |
| 拉 main 的最新內容 | 更新 / 同步 main |
| 看自己做到哪了 | 現在在哪 / 做到哪了 |
| 切換班級/科目 | 載入 9C 英文（依實際班級） |

**全程用中文，不需要記任何 git 指令。**

---

## 萬一出事怎麼辦

### 情況 1：AI 說「分支衝突」

不要慌，也不要自己下指令。跟 AI 說「**幫我處理衝突**」，
AI 會列出衝突的檔案、用你能理解的方式讓你決定保留哪一版。

### 情況 2：不小心在 main 上做了工作

AI 會在「開工」時就切到你的分支，所以理論上不會發生。
如果真的發生了（例如你手動 checkout main），跟 AI 說「**我剛剛在 main 上工作了**」，
AI 會把那些改動搬到你的分支，main 保持乾淨。

### 情況 3：你想直接看其他老師在做什麼

可以看，但不要改。
```bash
git checkout origin/workspace/Teacher_別人的名字  # 看看就好
git checkout workspace/Teacher_你的名字           # 回自己的
```

---

## 設計理念（選讀）

**為什麼不讓每個人直接用 main？**
一個人的實驗半成品 push 到 main，全部 13 位教師下次 clone 或 pull 都會拉到那個半成品。風險太高。

**為什麼不用 fork？**
Fork 是 GitHub 上的分離 repo，權限與協作複雜度高。教師的場域需要輕巧的單一 repo + 分支隔離。

**為什麼不用 feature branch？**
Feature branch 適合工程專案的短期任務分支。教師的工作是**持續性的**——一整學期的備課、學生觀察、教學反思都在同一條線上。一師一分支對應的是「教師的工作是連續的、長期的」，而不是「任務是短期的」。

---

## 架構關鍵檔案（你不用碰，但知道一下）

| 檔案 | 功能 |
|---|---|
| `ai-core/acl.yaml` | 誰對應哪條分支、誰可以寫哪些路徑 |
| `ai-core/skills/opening.md` | 開工流程（含 GitHub username 識別與分支自動切換）|
| `ai-core/skills/wrap-up.md` | 收工流程（push 到你的分支）|
| `.github/CODEOWNERS` | 系統路徑的審核守門員（David 審核）|
| `setup/scripts/pre-push-check.py` | 本機提交前的檢查（阻擋誤 push 到 main）|

---

*建立日期：2026-04-17*
*搭配通知：`setup/reference/migration-v2-notice.md`*
