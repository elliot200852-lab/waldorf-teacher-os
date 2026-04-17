---
aliases:
  - "TeacherOS v2.0 遷移通知"
title: TeacherOS v2.0 — 系統重啟通知
date: 2026-04-17
status: 待發送
audience: 所有 TeacherOS 使用者（教師 + 管理員）
channel: LINE 群組 / Email
---

# TeacherOS v2.0 — 系統重啟通知

## 一句話

**TeacherOS 進行了一次徹底的 Git 重置，你原本的資料夾將無法繼續使用，請依下方步驟重新安裝。**

---

## 為什麼要做這件事

過去一年累積的歷史中包含：
- 不應公開的機密檔案（OAuth 憑證）
- 早期實驗留下的大型二進位檔
- 冗餘的工具鏈整合（GWS 自動化）

這些讓 `.git` 膨脹到 647 MB，每次 clone 都要拉超過 900 MB。
v2.0 把這些全部清洗乾淨，只保留現在用到的內容。

---

## 你需要做的事（5 分鐘）

### 1. 確認你的工作已存檔

如果你對 AI 說過「收工」並看到「已推送」，就代表已存檔。
不確定的話，打開 Claude Code 跟 AI 說「**收工**」，它會幫你同步到雲端。

### 2. 刪掉舊的資料夾

```
/Users/你的使用者名稱/Desktop/WaldorfTeacherOS-Repo    (Mac)
C:\Users\你的使用者名稱\Desktop\WaldorfTeacherOS-Repo  (Windows)
```

直接拖進垃圾桶（或 Windows 的資源回收筒）就好。

### 3. 重新下載

打開終端機（Mac）或 PowerShell（Windows）：

```bash
cd ~/Desktop
git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git WaldorfTeacherOS-Repo
cd WaldorfTeacherOS-Repo
```

### 4. 執行一次設定

**Mac：**
```bash
bash setup/start.sh
```

**Windows：**
```powershell
.\setup\start.ps1
```

---

## 新的工作方式（重要）

**從今以後你只會在「自己的分支」上工作，不再直接動 main。**

你的分支名稱：`workspace/Teacher_你的名字`（例：`workspace/Teacher_林詩閔`）

AI 會自動幫你切到正確的分支，你什麼都不用做。
收工時 AI 會把你的工作推到你的分支，不會影響別人。
需要把工作合併進 main 時，AI 會幫你開 PR（Pull Request），由 David 審核。

完整說明：`setup/reference/branch-workflow.md`

---

## 如果你之前用過 Google Workspace 整合

（Drive 上傳、寄 Email、Calendar、Sheets 等）

這些功能的 CLI 工具（gws）**不再由 TeacherOS 統一安裝**，
需要你自己在個人環境裝一次。

請聯繫 David 取得 5 分鐘的安裝說明。
如果你從來沒用過這些功能，可以忽略這段。

---

## 常見問題

**Q1. 我重新 clone 之後，我之前的備課資料還在嗎？**
在。所有教案、學生資料、session.yaml 都完整保留在你的 workspace。只有「Git 歷史」被清掉了，你的實際檔案一個都沒少。

**Q2. 我舊資料夾裡有一些還沒推送的改動怎麼辦？**
**先說「收工」** 再刪舊資料夾。AI 會把你沒存的改動推上去。
如果已經刪了才想到，聯繫 David，系統有完整備份可以撈。

**Q3. 這個動作會影響我的 Claude Code 設定嗎？**
不會。Claude Code 的全域設定在 `~/.claude/`，不受 repo 重置影響。

**Q4. 為什麼不能直接 pull？**
因為 main 的歷史被重寫了，`git pull` 會失敗或產生大量衝突。重新 clone 是最乾淨的作法。

---

## 有問題找誰

- 技術問題：David（elliot200852@gmail.com）
- 步驟卡住：跟你的 Claude Code 說「我卡在第 X 步」，AI 會幫你診斷

---

*重置執行時間：2026-04-17*
*新 repo 起點 commit：`TeacherOS v2.0：乾淨起點（歷史已清洗）`*
