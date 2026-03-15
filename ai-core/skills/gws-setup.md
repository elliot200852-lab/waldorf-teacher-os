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

## 操作類型標記

本技能中的每一步標記為以下兩種：

- **AI 自動** — AI 直接在終端執行，教師不需要做任何事
- **需教師操作** — 會開啟瀏覽器或需要教師輸入，AI 必須暫停並等待教師完成

## 跨平台注意事項

本技能需適用 macOS、Linux、Windows。AI 在執行前應偵測 OS：

| 項目 | macOS | Linux | Windows（PowerShell / Git Bash） |
|------|-------|-------|------|
| 開啟瀏覽器 | `open "URL"` | `xdg-open "URL"` | `start "URL"` |
| 套件管理 | Homebrew / nvm | nvm / 系統 apt | nvm-windows / 官方 Node 安裝包 |
| gws 設定路徑 | `~/.config/gws/` | `~/.config/gws/` | `%APPDATA%\gws\` |

> AI 應在 Step 1 偵測 OS（`uname -s` 或 `$env:OS`），後續步驟自動選用對應指令。
> 若 gws 不在 PATH 中，優先嘗試 `npx @googleworkspace/cli`，不要寫死路徑。

## 執行步驟

### Step 0 — 確認帳號資訊（AI 自動）

讀取教師的 `{workspace}/teacheros-personal.yaml`，檢查是否有 `google_accounts` 區塊。

- 有 → 記下 `default` 帳號與 `accounts` 清單，進入 Step 1
- 沒有 → **停止**，提示教師：

> 你的 teacheros-personal.yaml 還沒有填寫 `google_accounts`。
> 請先填入你的 Google 帳號資訊，格式參考 David 的範本：
> `workspaces/Working_Member/Codeowner_David/teacheros-personal.yaml` 的 `google_accounts` 區塊。
> 填好後再說「設定 gws」。

### Step 1 — 檢查前置條件：Node.js / npm（AI 自動）

```bash
node --version && npm --version
```

- 通過 → 進入 Step 2
- 失敗 → 提示教師：「請先安裝 Node.js（https://nodejs.org），安裝完成後再說『設定 gws』。」

### Step 2 — 檢查 gws CLI 是否已安裝（AI 自動）

```bash
command -v gws && gws --version
```

- 已安裝 → 顯示版本，進入 Step 3
- 不在 PATH 但 Node.js 可用 → 嘗試 `npx @googleworkspace/cli --version`
- 完全未安裝 → AI 自動執行安裝：

```bash
npm install -g @googleworkspace/cli
```

安裝完成後確認：

```bash
gws --version
```

> 若安裝後仍然 `command not found`，代表全域 npm bin 不在 PATH 中。
> AI 可用 `npx @googleworkspace/cli` 替代所有 `gws` 指令，或提示教師將 npm bin 加入 PATH。

### Step 2.5 — 部署 OAuth client_secret（AI 自動）

檢查使用者本機是否已有 `client_secret.json`：

- macOS / Linux：`~/.config/gws/client_secret.json`
- Windows：`%APPDATA%\gws\client_secret.json`

**已存在** → 跳過，進入 Step 3。

**不存在** → 從 Repo 複製：

```bash
# macOS / Linux
mkdir -p ~/.config/gws
cp setup/gws-client-secret.json ~/.config/gws/client_secret.json
```

```powershell
# Windows（PowerShell）
New-Item -ItemType Directory -Force -Path "$env:APPDATA\gws"
Copy-Item setup\gws-client-secret.json "$env:APPDATA\gws\client_secret.json"
```

> 這份檔案是 TeacherOS Google Cloud 專案的 OAuth 用戶端識別檔，不含任何個人資料。
> 使用者的授權 token 在登入後才產生，存於本機加密檔案中，不進入 Git。

### Step 3 — 登入主帳號（需教師操作）

AI 執行：

```bash
gws auth login --account <default帳號email>
```

> **重要：** 必須使用 `--account EMAIL` 參數綁定帳號。不帶此參數會將憑證存到通用路徑，導致多帳號機制失效。

**執行後 AI 必須暫停，向教師說明：**

> 瀏覽器已開啟 Google 登入頁面。請完成以下操作：
>
> 1. 在瀏覽器中選擇你的主要 Google 帳號（{default 帳號}）
> 2. 畫面可能會顯示「Google 尚未驗證這個應用程式」的警告——這是正常的（TeacherOS 是內部工具）
>    - 點擊「進階」→「前往 TeacherOS（不安全）」
> 3. 畫面會顯示「Google Workspace CLI 要求存取你的 Google 帳戶」
> 4. 點擊「允許」（Allow）
> 5. 看到「Authentication successful」或類似成功訊息後，回到這裡告訴我「好了」
>
> （如果瀏覽器沒有自動開啟，AI 用偵測到的 OS 對應指令開啟瀏覽器。）

**等待教師確認後**，AI 驗證登入（不要用 `gws auth status`，它的輸出不可靠）：

```bash
gws gmail users getProfile --params '{"userId":"me"}'
```

- 回傳 emailAddress 且與 default 帳號一致 → 進入 Step 4
- 失敗 → 提示教師重試，或檢查是否選對帳號

### Step 4 — 多帳號設定（需教師操作，若有多帳號）

讀取 `google_accounts.accounts` 清單。若只有一個帳號，跳到 Step 5。

若有多個帳號，對每個額外帳號：

AI 執行：

```bash
gws auth login --account <額外帳號email>
```

> **重要：** 登入時用 `--account EMAIL` 綁定帳號；使用 API 時用 `GOOGLE_WORKSPACE_CLI_ACCOUNT=EMAIL` 環境變數切換帳號。兩者語法不同，不可混淆。

**執行後 AI 暫停，向教師說明：**

> 瀏覽器已開啟。這次請選擇你的第二個帳號（{額外帳號 email}）並按「允許」。
> 如果看到「Google 尚未驗證這個應用程式」警告，點「進階」→「前往 TeacherOS（不安全）」即可。
> 完成後告訴我「好了」。
>
> （如果瀏覽器沒有自動開啟，AI 用偵測到的 OS 對應指令開啟瀏覽器。）

**等待教師確認後**，AI 驗證：

```bash
GOOGLE_WORKSPACE_CLI_ACCOUNT=<額外帳號email> gws gmail users getProfile --params '{"userId":"me"}'
```

- 回傳 emailAddress 且與額外帳號一致 → 繼續下一個帳號
- 失敗 → 提示教師重試

重複此流程直到所有帳號都登入完成。最後確認帳號清單：

```bash
gws auth list
```

### Step 5 — 驗證各服務可用（AI 自動）

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

若出現 403 scope 不足（**需教師操作**）：

AI 執行：

```bash
gws auth login --account <主帳號email> --scopes gmail,drive,calendar,sheets,docs
```

> 瀏覽器已開啟。這次 Google 會要求你授權更多服務（Gmail、Drive、Calendar、Sheets、Docs）。
> 請選擇同一個帳號，點擊「允許」，完成後告訴我「好了」。

等待教師確認後重新測試。

### Step 6 — 回報結果（AI 自動）

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
- 認證憑證存於本機（macOS/Linux: `~/.config/gws/`；Windows: `%APPDATA%\gws\`），不進入 Git
- 重複執行本技能是安全的——登入只是刷新 token，不會產生重複帳號
- gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`
