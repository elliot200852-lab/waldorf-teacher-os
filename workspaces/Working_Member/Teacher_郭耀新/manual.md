---
aliases:
  - "郭耀新操作手冊"
---

# TeacherOS 快速參考手冊

> 2026-03-06 整理

---

## 架構三層

1. **`ai-core/`** — 系統根基，全校共用，只有 David 能改
2. **`projects/_di-framework/`** — 差異化教學框架，每次備課必載
3. **`workspaces/Working_Member/Teacher_郭耀新/`** — 我的個人工作區，100% 自主

---

## Session 工作循環

```
/load [班級] [科目]   → 載入脈絡，AI 報告目前進度
   ↓ 進行備課工作
/session-end          → AI 掃描對話，產生 diff，寫入 session.yaml
/save                 → git push 上傳 GitHub
```

---

## session.yaml 位置

```
workspaces/Working_Member/Teacher_郭耀新/projects/class-{code}/{subject}/session.yaml
```

記錄：目前 Block/Step、下一步行動、已確認決策、待決問題、產出檔案路徑。

---

## 身份驗證

`acl.yaml` 以 Email 對應 workspace 路徑與 `allowed_paths`。
我只能寫入自己的 workspace，`ai-core/`、`setup/`、`.github/` 永遠受保護。

### ACL 執行兩層機制

| 層 | 時機 | 可繞過？ |
|----|------|---------|
| **Pre-commit hook** (`setup/hooks/pre-commit`) | `git commit` 時（本機） | 是（`--no-verify`） |
| **GitHub CODEOWNERS** (`.github/CODEOWNERS`) | PR 合併時（GitHub） | 否（Branch Protection 開啟後） |

- `acl.yaml` 是資料來源，hook + GitHub 是執行者，LLM 是最前面的軟約束
- hook 靠 `.git/hooks/pre-commit` 觸發（git 原生慣例，名稱對了就自動執行）
- 每個人 clone 後需執行一次安裝腳本才會安裝 hook（Mac: `bash setup/start.sh`；Windows: `.\setup\start.ps1`；或直接 `python3 setup/install-hooks.py`）
- `acl-proposal.yaml`（`default: deny` 預設拒絕原則）是一個值得提交給 David 的安全改善提案

---

## 提案紀錄

### setup-check.sh Linux 修正（2026-03-06）

`setup/setup-check.sh` OS 偵測缺少 `Linux*)` 分支，Ubuntu 24 和 WSL2 被歸為 `unknown`，導致 Pandoc 提示顯示錯誤指令、Google Drive 檢查被跳過。
修正：加入 `Linux*)  OS_TYPE="linux" ;;`，Pandoc 提示加 `apt install pandoc`，Google Drive 改為提示使用瀏覽器版。已提交 David 審核。

### ACL 預設拒絕原則（2026-03-06）

現行 `acl.yaml` 每個教師條目需重複列出 `blocked_paths`，新增教師時容易遺漏。
提案：頂層加 `default: deny`，移除所有 `blocked_paths`，每個教師只保留 `allowed_paths`。效益：忘記設定只會少給權限不會多給，且每條目減少 4–5 行。已提交 David 審核。

---

## 詳細文件

- 系統路由：`ai-core/teacheros.yaml`
- 載入流程：`ai-core/skills/load.md`
- 收尾流程：`ai-core/skills/wrap-up.md`
- 權限設定：`ai-core/acl.yaml`

---

## 系統工具設定紀錄

### Google Workspace CLI (gws) 設定 (2026-03-07)

TeacherOS 更新加入了 Google Workspace CLI (gws) 整合，讓 AI 可直接操作 Google Drive、Calendar、Docs、Sheets 與 Gmail。

**先決條件：**
- Node.js 環境 (本機已具備 v24.11.0)。
- 必須擁有一個獨立的 OAuth Client ID。因此需要先安裝 `google-cloud-cli` 進行認證。

**完整設定步驟：**

1. **全域安裝 gws CLI**：
   ```bash
   npm install -g @googleworkspace/cli
   ```

2. **安裝 Google Cloud CLI** (以 Ubuntu 為例，用於 OAuth 認證輔助)：
   ```bash
   sudo apt-get install apt-transport-https ca-certificates gnupg curl
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   sudo apt-get update && sudo apt-get install google-cloud-cli
   ```

3. **登入 Google Cloud 帳號**：
   ```bash
   gcloud auth login
   ```
   *(自動跳出瀏覽器，選擇對應帳號 `dylankuo...`)*

4. **初始化 gws OAuth 憑證配置**：
   ```bash
   gws auth setup
   ```
   - 執行時終端機會要求輸入 `OAuth Client ID` 與 `Client Secret`。
   - 請前往 Google Cloud Console > APIs & Services > Credentials 建立一組「Desktop app」的 OAuth client。
   - 將獲得的 ID 與 Secret 貼回終端機完成綁定。

5. **認證並授權工作服務存取權**：
   ```bash
   gws auth login
   ```
   *(跳出瀏覽器，全選授權 Google Drive、Calendar、Docs 等權限)*

6. **檢查認證狀態**：
   ```bash
   gws auth status
   ```
   *(確認 `token_valid: true` 即代表所有設定就緒)*

*更新詳參：`ai-core/reference/gws-cli-guide.md`*
