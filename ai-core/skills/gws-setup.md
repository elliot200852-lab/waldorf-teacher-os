---
name: gws-setup
description: Google Workspace CLI（gws）安裝與設定。檢查前置條件、安裝、登入、多帳號設定、驗證。
triggers:
  - 設定 gws
  - 安裝 gws
  - gws setup
  - gws 設定
  - 裝 gws
requires_args: false
---

# skill: gws-setup — Google Workspace CLI 安裝與設定

互動式引導完成 gws CLI 的安裝、登入與多帳號設定。

## 根目錄

以 Repo 根目錄為基準。

## 工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機（Claude Code、Cowork） | 自動執行每一步，報告結果 |
| 無終端機（Gemini 語音等） | 逐步提示教師手動執行指令 |

## 執行步驟

### Step 1 — 檢查前置條件：Node.js / npm

```bash
node --version && npm --version
```

- 通過 → 進入 Step 2
- 失敗 → 提示教師安裝 Node.js（https://nodejs.org），安裝後重新執行本技能

### Step 2 — 檢查 gws CLI 是否已安裝

```bash
command -v gws && gws --version
```

- 已安裝 → 顯示版本，進入 Step 3
- 未安裝 → 執行安裝：

```bash
npm install -g @googleworkspace/cli
```

安裝完成後確認：

```bash
gws --version
```

### Step 3 — 登入主帳號

讀取教師的 `{workspace}/teacheros-personal.yaml`，取得 `google_accounts.default` 作為主帳號。

```bash
gws auth login
```

瀏覽器會跳出 Google 授權頁面。教師完成授權後回到終端。

驗證登入：

```bash
gws auth status
```

確認 token 存在且有效。

### Step 4 — 多帳號設定（若有）

讀取 `google_accounts.accounts` 清單，若有多個帳號，逐一登入：

```bash
GOOGLE_WORKSPACE_CLI_ACCOUNT=<第二帳號email> gws auth login
```

每個帳號登入後驗證：

```bash
GOOGLE_WORKSPACE_CLI_ACCOUNT=<第二帳號email> gws auth status
```

若教師只有一個帳號，跳過此步。

### Step 5 — 驗證各服務可用

用主帳號快速測試三個核心服務：

```bash
# Gmail
gws gmail users getProfile --params '{"userId":"me"}'

# Calendar
gws calendar +agenda

# Drive
gws drive files list --params '{"pageSize":1}'
```

每個服務回報：可用 / 不可用（附錯誤訊息）。

若出現 403 scope 不足：

```bash
gws auth login --scope gmail,drive,calendar,sheets,docs
```

### Step 6 — 回報結果

以表格呈現設定結果：

```
| 項目 | 狀態 |
|------|------|
| Node.js | vXX.XX.X |
| gws CLI | vX.X.X |
| 主帳號（xxx@gmail.com） | 已登入 |
| 第二帳號（yyy@gmail.com） | 已登入 / 未設定 |
| Gmail | 可用 |
| Calendar | 可用 |
| Drive | 可用 |
```

## 注意事項

- 本技能不會修改教師的 teacheros-personal.yaml，僅讀取帳號資訊
- 認證憑證存於 `~/.config/gws/`，不進入 Git
- 若教師尚未在 teacheros-personal.yaml 填入 google_accounts，提示教師先填寫
- gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`
