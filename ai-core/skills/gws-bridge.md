---
skill_id: gws-bridge
title: GWS CLI Bridge — 從 Cowork/Linux VM 操作 Google Workspace
version: 1.0.0
created: 2026-03-21
triggers:
  - gws
  - google drive
  - drive upload
  - drive search
  - google workspace
  - 上傳到 drive
  - 上傳到雲端
  - gmail
  - google calendar
platforms:
  - cowork
  - claude-code
---

# GWS CLI Bridge — 從 Cowork/Linux VM 操作 Google Workspace

## 核心規則（每次 session 必讀）

Cowork 的 Linux VM **無法直接安裝或執行 GWS CLI**（npm proxy 被封鎖）。
必須透過 `mcp__Control_your_Mac__osascript` 橋接到 David 的 Mac 執行。

## GWS CLI 位置與帳號

```
GWS_BIN = /Users/Dave/.nvm/versions/node/v24.13.0/bin/gws
版本: v0.4.4
帳號 1（預設）: elliot200852@gmail.com
帳號 2: linintellectdave@gmail.com
```

## 呼叫模式

### 模式 A：從 Cowork 透過 osascript（推薦）

```applescript
do shell script "/Users/Dave/.nvm/versions/node/v24.13.0/bin/gws drive +upload /Users/Dave/Desktop/WaldorfTeacherOS-Repo/temp/file.pdf --parent FOLDER_ID 2>&1"
```

**關鍵**：
1. 必須使用 GWS CLI 的**絕對路徑**，不能依賴 PATH
2. 檔案路徑必須是 Mac 上的**絕對路徑**（`/Users/Dave/...`），不能用 VM 的 `/sessions/...`
3. 中文檔名在 `do shell script` 裡可用，但雙引號嵌套要小心
4. 如果 AppleScript 字串嵌套太深，改用 `--name` 參數指定上傳名稱

### 模式 B：從 Node.js 腳本（assemble-story.js 等）

```javascript
const GWS_BIN = '/Users/Dave/.nvm/versions/node/v24.13.0/bin/gws';
const { execSync } = require('child_process');
const result = execSync(`"${GWS_BIN}" drive +upload "${filePath}" --parent ${folderId} --name "${driveName}"`, {
  encoding: 'utf-8',
  timeout: 120000
});
const parsed = JSON.parse(result.trim());
// parsed.id = Drive file ID
```

### 模式 C：從 Claude Code（直接 Bash）

如果在 Claude Code（不是 Cowork）裡工作，Mac 上可以直接執行：

```bash
gws drive +upload file.pdf --parent FOLDER_ID
```

## 常用指令

### Drive 上傳
```
gws drive +upload <file> --parent <FOLDER_ID> [--name "顯示名稱"]
```

### Drive 搜尋
```
gws drive files list --params '{"q":"name contains '\''關鍵字'\''", "pageSize":10}'
```

### Drive 列出資料夾內容
```
gws drive files list --params '{"q":"'\''FOLDER_ID'\'' in parents", "pageSize":20}'
```

## 已知的 Drive 資料夾 ID

| 資料夾 | ID |
|--------|-----|
| 台灣的故事 | `1TBD6Xs-wVgqqlX3_13boy4xbBnjQ9LdY` |

## 路徑對照（VM ↔ Mac）

Cowork 的 workspace 實際掛載自 Mac 桌面：

| 環境 | 路徑 |
|------|------|
| VM (Cowork) | `/sessions/upbeat-kind-bell/mnt/WaldorfTeacherOS-Repo/` |
| Mac | `/Users/Dave/Desktop/WaldorfTeacherOS-Repo/` |

在 VM 裡寫檔 → 在 Mac 上的對應路徑可直接讀取。
但 osascript 裡的路徑必須用 Mac 版。

## 錯誤排除

| 症狀 | 原因 | 解法 |
|------|------|------|
| `command not found: gws` | osascript 不繼承 PATH | 使用絕對路徑 |
| `403 Forbidden` | VM 直接 npm install 被 proxy 擋 | 用 osascript 橋接，不在 VM 安裝 |
| AppleScript 編碼錯誤 | 中文 + 雙引號嵌套 | 用 `--name` 參數分離路徑與檔名 |
| `Invalid Value` Drive query | 引號嵌套問題 | 用 `'\''` 處理 AppleScript 單引號 |
