---
name: drive-transfer
description: Google Drive 跨帳號檔案傳輸。教師之間互傳檔案：傳（分享給對方）或收（從「與我共用」複製到自己的 Drive）。
triggers:
  - 傳檔案給
  - 傳給
  - 傳給老師
  - 分享 Drive 檔案
  - drive transfer
  - 收檔案
  - 收 Drive
  - 拿 Drive 檔案
  - 收對方傳來的
requires_args: false
args_format: "[選填：傳給 人名 / 收 人名 的檔案]"
---

# skill: drive-transfer — Google Drive 跨帳號檔案傳輸

教師之間（或教師與管理員）透過 Google Drive 互傳檔案。

Drive API 不支援直接跨帳號搬檔案，因此拆成兩個動作：
- **傳（Send）**：把自己 Drive 的檔案分享給對方（加權限）
- **收（Receive）**：把對方分享給自己的檔案複製到自己的 Drive 資料夾

## 根目錄

以 Repo 根目錄為基準。gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`。

## 工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機 + gws CLI | 直接執行 `gws drive` 指令 |
| 無終端機 | 引導教師手動在 Google Drive 網頁操作分享 |

## 執行步驟

### Step 0 — 確認 gws CLI 可用

```bash
command -v gws && gws auth status
```

若未安裝或未登入，提示教師：「請自行安裝 gws CLI（`npm install -g @googleworkspace/cli`）並執行 `gws auth login` 完成登入。」

### Step 1 — 判斷操作方向

| 教師說 | 操作 |
|--------|------|
| 「傳給 [人名]」「分享檔案給 [人名]」 | → Send 流程（Step 2a） |
| 「收檔案」「收 [人名] 傳來的」「拿 Drive 檔案」 | → Receive 流程（Step 2b） |

### Step 2a — Send（傳檔案給對方）

**1. 確認目標對象**

從 `ai-core/acl.yaml` 查找對方的 email：
- 教師說「傳給 David」→ `elliot200852@gmail.com`
- 教師說「傳給王琬婷」→ `hsinhunglin520@gmail.com`
- 若對方不在 acl.yaml → 詢問教師提供 email

**2. 確認來源檔案**

教師提供檔案名稱或關鍵字，用 gws 搜尋：

```bash
gws drive files list --params '{"q":"name contains '\''關鍵字'\''","pageSize":10}' --fields 'files(id,name,mimeType)' --format table
```

若教師指定資料夾，搜尋該資料夾內的檔案：

```bash
gws drive files list --params '{"q":"'\''FOLDER_ID'\'' in parents","pageSize":20}' --fields 'files(id,name,mimeType)' --format table
```

**3. 向教師確認**

> 要把「[檔名]」分享給 [對方姓名]（[email]）嗎？預設為唯讀，需要給編輯權嗎？

**4. 執行分享**

```bash
gws drive permissions create --params '{"fileId":"FILE_ID"}' --json '{"role":"reader","type":"user","emailAddress":"TARGET_EMAIL"}'
```

若教師要求編輯權：role 改為 `writer`。
若是資料夾，同樣用 `permissions create`，子檔案會自動繼承權限。

**5. 報告結果**

> 已把「[檔名]」分享給 [對方姓名]。對方可在 Google Drive「與我共用」中看到。

### Step 2b — Receive（收對方傳來的檔案）

**1. 列出「與我共用」的最近檔案**

```bash
gws drive files list --params '{"q":"sharedWithMe=true","orderBy":"modifiedTime desc","pageSize":10}' --fields 'files(id,name,mimeType,owners,modifiedTime)' --format table
```

若教師指定來源者，加上 owner 過濾：

```bash
gws drive files list --params '{"q":"sharedWithMe=true and '\''SOURCE_EMAIL'\'' in owners","orderBy":"modifiedTime desc","pageSize":10}' --fields 'files(id,name,mimeType,modifiedTime)' --format table
```

**2. 教師選擇檔案**

列出清單，讓教師選擇要收哪些檔案。

**3. 確認目標資料夾**

教師指定 Drive 中的目標資料夾。若未指定，詢問或用 Drive 根目錄。

**4. 複製到自己的 Drive**

```bash
gws drive files copy --params '{"fileId":"FILE_ID"}' --json '{"name":"檔名","parents":["TARGET_FOLDER_ID"]}'
```

**5. 報告結果**

> 已把「[檔名]」複製到你的 Drive [資料夾名]。

## 帳號處理

- 讀取 `{workspace}/teacheros-personal.yaml` 的 `google_accounts`
- 預設使用 default 帳號
- 教師指定帳號關鍵字時，在 gws 指令前加：`GOOGLE_WORKSPACE_CLI_ACCOUNT=<email>`

## 跨平台

- gws CLI 在 macOS / Windows 均可用，無平台特定指令
- 若未來需要擴展為自動化腳本，一律用 Python 撰寫

## 與 send-email 的區分

「**寄**」= Email，「**傳**」= Drive 檔案。

| 教師說 | 觸發技能 |
|--------|---------|
| 「寄給 David」「寄信給…」 | send-email |
| 「傳給 David」「傳檔案給…」 | drive-transfer |

若語意模糊（例如「把這個給 David」），AI 應追問：「是要寄 Email 還是傳 Drive 檔案？」

## 注意事項

- Send 不會移動或刪除原檔，僅新增對方的存取權限
- Receive 是複製，不是移動。「與我共用」中的原始檔案仍在
- 分享整個資料夾時，內部所有檔案自動繼承權限
- 此技能適用於所有 AI 平台（Claude Code、Gemini、ChatGPT 等）
