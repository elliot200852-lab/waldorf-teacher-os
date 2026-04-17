---
name: notebooklm-setup
description: NotebookLM MCP CLI（nlm）安裝與設定。自動偵測 OS，引導完成安裝、登入、MCP 連接，適用 Claude Code 與 Google Antigravity，Windows 與 macOS 均支援。
triggers:
  - 安裝 NotebookLM
  - 設定 NotebookLM
  - 連接 NotebookLM
  - nlm 安裝
  - nlm setup
  - NotebookLM 安裝
  - NotebookLM 設定
  - 裝 nlm
requires_args: false
cross_platform: true
---

# skill: notebooklm-setup — NotebookLM MCP CLI 安裝與設定

引導教師完成 NotebookLM MCP 的安裝、Google 登入與 AI 工具連接。
安裝完成後，教師就能在 Claude Code 或 Antigravity 裡直接用自然語言操控 NotebookLM。

## 工具能力矩陣

| AI 工具 + 作業系統 | 執行方式 |
|-------------------|---------|
| Claude Code（macOS / Windows） | AI 直接在 Bash 工具執行所有指令 |
| Antigravity（macOS） | AI 直接在 Bash 工具執行所有指令 |
| Antigravity（Windows）| ⚠️ **特殊處理**：uv 安裝必須由教師手動在 PowerShell 執行（見 Step 1） |
| 其他有終端機的 AI | 同 Claude Code 模式 |

## 操作類型標記

- **AI 自動** — AI 直接在終端執行，教師不需要做任何事
- **需教師操作** — 需教師手動執行或在瀏覽器操作，AI 必須暫停等待

## 原理說明

```
Claude / Antigravity ←(MCP 協定)→ nlm（翻譯官）←(Google 登入)→ NotebookLM
```

`nlm` 是翻譯官：它模擬瀏覽器操作，讓 AI 能透過 MCP 標準接口操控 NotebookLM。

---

## 執行步驟

### Step 0 — 偵測環境（AI 自動）

執行：

```bash
# macOS / Linux
uname -s
```

```powershell
# Windows PowerShell
$env:OS
```

同時確認 AI 工具類型（Claude Code / Antigravity / 其他），記錄後續步驟所需的 MCP 目標名稱：

| AI 工具 | MCP 連接目標 |
|---------|------------|
| Claude Code（桌面版 / CLI） | `claude-code` |
| Google Antigravity | `antigravity` |
| Cursor | `cursor` |
| Windsurf | `windsurf` |

若無法自動偵測，詢問教師：「你使用的是 Claude Code 還是 Google Antigravity？」

### Step 1 — 安裝 uv

> `uv` 是 Python 工具鏈管理器，用於安裝 `nlm`。

**AI 自動執行前，先確認 uv 是否已安裝：**

```bash
uv --version
```

- 已安裝 → 顯示版本，跳到 Step 2
- 未安裝 → 依 OS 安裝：

#### macOS / Linux（AI 自動）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安裝後重新載入 shell 環境（Claude Code 的 Bash 工具開新 session 即可）：

```bash
uv --version
```

#### Windows（⚠️ 需教師操作）

**Windows 上，不論使用 Claude Code 還是 Antigravity，uv 安裝指令必須在 PowerShell 中執行。**
AI 的 Bash 工具在 Windows 底層是 Git Bash，不支援 PowerShell 的 `irm` 指令，強行執行會卡住。

AI 暫停，向教師說明：

> **請手動開啟 PowerShell**（Win + X → 選「Windows PowerShell」或「終端機」），
> 貼上並執行以下指令：
>
> ```powershell
> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
> ```
>
> 執行完成後，**關閉 PowerShell，重新開一個新的 PowerShell 視窗**（PATH 才會更新），
> 確認安裝成功：
>
> ```powershell
> uv --version
> ```
>
> 能看到版本號後告訴我「好了」。

等待教師確認後繼續。

### Step 2 — 安裝 NotebookLM MCP CLI（nlm）（AI 自動）

```bash
uv tool install notebooklm-mcp-cli
```

安裝完成後確認：

```bash
nlm --version
```

- 成功顯示版本 → 進入 Step 3
- `nlm: command not found`：

  - macOS / Linux → 重新載入 shell：`source ~/.bashrc` 或 `source ~/.zshrc`，再試
  - Windows → 關閉 PowerShell 重新開啟，再執行 `nlm --version`

若仍失敗，提示教師將 uv 的路徑加入 PATH：
- Windows：`%APPDATA%\uv\bin`
- macOS / Linux：`~/.local/bin`

### Step 3 — 登入 Google 帳號（需教師操作）

AI 執行：

```bash
nlm login
```

AI 暫停，向教師說明：

> 瀏覽器已自動開啟 Google 登入頁面。
> 請選擇你用來登入 NotebookLM 的 Google 帳號，完成授權。
> 登入成功後，CLI 會自動擷取認證資訊，頁面會顯示「已成功登入」。
> 完成後告訴我「好了」。
>
> 如果瀏覽器沒有自動開啟，請執行 `nlm login --manual`，按照終端機指示操作。

等待教師確認後，驗證登入狀態：

```bash
nlm doctor
```

- 顯示認證成功 → 進入 Step 4
- 顯示未認證 → 重新執行 `nlm login`，確認在瀏覽器中有按「允許」

### Step 4 — 設定 MCP 連接（AI 自動）

依 Step 0 偵測到的 AI 工具，執行對應指令：

```bash
# Claude Code
nlm setup add claude-code

# Google Antigravity
nlm setup add antigravity

# Cursor
nlm setup add cursor

# Windsurf
nlm setup add windsurf
```

確認設定成功：

```bash
nlm setup list
```

應看到對應工具出現在清單中，狀態為已設定。

> MCP 設定檔位置：
> - Claude Code：`~/.claude/` 內
> - Antigravity：`~/.gemini/antigravity/mcp_config.json`（Windows：`C:\Users\{使用者}\.gemini\...`）

### Step 5 — 建立本機資料夾（AI 自動）

依 OS 建立 NotebookLM 輸出資料夾：

```bash
# macOS / Linux
mkdir -p ~/Documents/NotebookLM/{slides,infographics,audio,video,docs,sheets,mindmaps,quizzes}
```

```powershell
# Windows（PowerShell）
$dirs = "slides","infographics","audio","video","docs","sheets","mindmaps","quizzes"
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Documents\NotebookLM\$_" }
```

### Step 6 — 重啟 AI 工具並驗證（需教師操作）

AI 向教師說明：

> **請完全關閉 [偵測到的 AI 工具名稱]，然後重新開啟。**
> MCP 伺服器會在啟動時自動載入。
> 重新開啟後告訴我「好了」。

等待教師確認後，AI 嘗試連接 NotebookLM：

呼叫 `notebook_list`（透過 MCP 工具）：
- 成功（即使回傳空清單） → 連接成功，進入 Step 7
- 失敗 → 提示：「MCP 工具未出現，可能需要再確認一次有完全重啟。若問題持續，執行 `nlm setup list` 確認設定是否存在。」

### Step 7 — 功能驗證（AI 自動）

1. 建立測試筆記本：呼叫 `notebook_create`，名稱為「連線測試」
2. 確認建立成功
3. 刪除測試筆記本：呼叫 `notebook_delete`

### Step 8 — 回報結果（AI 自動）

輸出安裝摘要：

```
| 項目 | 狀態 |
|------|------|
| uv | vX.X.X |
| nlm CLI | vX.X.X |
| Google 帳號 | {email}（已登入） |
| MCP 連接（{工具名}） | 已設定 |
| 本機資料夾 | ~/Documents/NotebookLM/ 已建立 |
| 連線測試 | 成功 |
```

完成後提示：「現在可以說『NotebookLM 做簡報』或『NotebookLM 做心智圖』來開始使用。」

---

## 安裝失敗：清除重來

若安裝過程中遇到錯誤，告訴 AI「上次安裝 NotebookLM 失敗，幫我清除重來」，AI 會執行：

```bash
nlm setup remove claude-code    # 或 antigravity
uv tool uninstall notebooklm-mcp-cli
nlm logout
```

清除完成後從 Step 1 重新開始。

## 常見問題

| 問題 | 解法 |
|------|------|
| `nlm: command not found` | 重開終端機或 PowerShell，或將 uv bin 路徑加入 PATH |
| `uv: command not found` | Windows 重開 PowerShell；macOS/Linux 執行 `source ~/.zshrc` |
| 登入後 `nlm doctor` 顯示未認證 | 重新執行 `nlm login` |
| 瀏覽器沒有自動開啟 | 執行 `nlm login --manual` |
| Claude Code / Antigravity 看不到 NotebookLM 工具 | 確認執行了 `nlm setup add [工具名]` 且完全重啟了 AI 工具 |
| Windows Antigravity 安裝卡住 | 確認使用 PowerShell（不是 Antigravity 的 Bash 工具）執行 uv 安裝指令 |
