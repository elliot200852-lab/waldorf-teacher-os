---
name: pull-request
description: 學期末或階段性完成時，協助教師將工作發送合併申請（Pull Request）給管理者，請求合併進主系統。
triggers:
  - 發 PR
  - 合併申請
  - 送回主系統
  - 通知管理者可以合併
  - 我想合併
  - pull request
requires_args: false
args_format: "[選填：PR 標題或說明]"
---

# skill: pull-request — 發送合併申請

協助教師將個人 branch 的工作成果，發送合併申請（Pull Request）給管理者審核。

## 什麼時候用

- 學期結束，備課已完整
- 完成一個完整的 Block（例如 Block 1 大綱定稿）
- 有一份教材想讓其他老師在主系統中看到

## 執行步驟

### Step 1 — 確認所有工作已儲存

先執行 `git status`，檢查是否有未儲存的更動。

若有未儲存的更動，先提醒教師：
> 「你還有一些工作尚未儲存。要先幫你存檔嗎？」

若教師同意，先執行 save 技能（git add + commit + push），再繼續。

### Step 2 — 收集 PR 資訊

讀取教師身份 YAML：`{workspace}/teacheros-personal.yaml`（workspace 路徑從 `ai-core/acl.yaml` 取得）以取得教師姓名。

若教師已提供說明，直接使用。若未提供，詢問：

> 「要用什麼標題通知管理者？例如：『[教師姓名]：[班級][科目]學期末備課整合』」

> 「有什麼需要管理者特別留意的嗎？（沒有的話直接說『沒有』就好）」

### Step 3 — 確認當前 branch 與遠端狀態

```bash
git branch --show-current
git push
```

確認教師在自己的個人 branch 上（格式：`workspace/Teacher_{姓名}`），且最新的工作已 push 到遠端。

### Step 4 — 引導教師到 GitHub 完成 PR

向教師提供清楚的步驟說明：

> 「好的，你的工作都已經上傳了。現在請到 GitHub 完成最後幾步：
>
> 1. 打開 TeacherOS 的 GitHub 頁面
> 2. 頁面上方會出現黃色提示欄，點擊『Compare & pull request』
> 3. 標題填：[教師提供的標題]
> 4. 說明欄填：[教師提供的說明，或『本學期備課完成，請審核合併。』]
> 5. 點擊『Create pull request』就完成了
>
> 管理者會收到通知，審核後合併。你不需要等待，可以繼續工作。」

### Step 5（選用） — 若 AI 環境支援 gh CLI

如果當前環境安裝了 GitHub CLI（`gh`），可以直接執行：

```bash
gh pr create --title "[標題]" --body "[說明]" --base main
```

執行成功後回應：
> 「合併申請已送出！管理者會收到通知。PR 連結：[URL]」

## 注意事項

- 教師的 branch 名稱格式為 `workspace/Teacher_{姓名}` 或 `workspace/Codeowner_{姓名}`
- PR 的 base branch 永遠是 `main`
- 不要自動合併 PR，只有管理者有權合併
- 若教師不在個人 branch 上（例如在 main 上），先提醒並協助切換
