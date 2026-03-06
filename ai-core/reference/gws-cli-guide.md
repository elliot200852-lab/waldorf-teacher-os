# GWS CLI 參考指南（AI 專用）

> **用途：** 所有 AI Agent 在執行 Google Workspace 操作前，讀取此文件以取得正確的指令語法。
> **CLI 路徑：** `gws`（若未在 PATH 中：`~/.nvm/versions/node/v24.13.0/bin/gws`）
> **認證：** 加密憑證存於 `~/.config/gws/`，首次使用需 `gws auth login`。

---

## 工具優先順序（所有 Google Workspace 技能統一遵守）

| 優先 | 路徑 | 適用 AI | 說明 |
|------|------|---------|------|
| 1 | gws CLI | 所有有終端機的 AI | 跨工具通用，功能最完整 |
| 2 | MCP 連接器 | Claude Code（若已安裝） | 部分服務有 MCP，作為備案 |
| 3 | 提示教師手動操作 | 無終端機的 AI（Gemini 語音等） | 提供操作指引，教師自行執行 |

---

## 可用性確認

執行前先確認 gws CLI 可用：

```bash
# 確認已安裝
command -v gws

# 確認已登入（回傳 JSON，檢查 token_cache_exists）
gws auth status
```

若未安裝或未登入，退回 MCP 或提示教師。

---

## 多帳號切換

gws 支援多帳號。教師的帳號別名定義在 `{workspace}/teacheros-personal.yaml` 的 `google_accounts` 區塊。

**切換方式：** 在指令前加環境變數。

```bash
# 使用預設帳號（不需額外設定）
gws gmail +send --to "someone@example.com" --subject "..." --body "..."

# 指定帳號
GOOGLE_WORKSPACE_CLI_ACCOUNT=linintellectdave@gmail.com gws gmail +send --to "..." --subject "..." --body "..."
```

**AI 判斷規則：**

1. 讀取 `teacheros-personal.yaml` 中的 `google_accounts.accounts[].keywords`
2. 比對教師口語指令中是否包含任何 keyword
3. 若命中 → 使用對應帳號
4. 若未命中 → 使用 `google_accounts.default`
5. 切換時主動告知教師：「使用 [別名] 帳號（[email]）」

---

## 五大服務指令速查

### 1. Gmail

| 操作 | 指令 |
|------|------|
| 寄信（純文字） | `gws gmail +send --to EMAIL --subject '主旨' --body '內文'` |
| 寄信（HTML/CC/BCC） | `gws gmail users messages send --params '{"userId":"me"}' --json '{"raw":"BASE64_RFC2822"}'` |
| 寄草稿 | `gws gmail users drafts send --params '{"userId":"me"}' --json '{"id":"DRAFT_ID"}'` |
| 收件匣摘要 | `gws gmail +triage` |
| 列出信件 | `gws gmail users messages list --params '{"userId":"me","maxResults":10}'` |
| 讀信 | `gws gmail users messages get --params '{"userId":"me","id":"MSG_ID"}'` |
| 刪信（丟垃圾桶） | `gws gmail users messages trash --params '{"userId":"me","id":"MSG_ID"}'` |
| 搜尋信件 | `gws gmail users messages list --params '{"userId":"me","q":"from:xxx subject:yyy"}'` |

### 2. Google Drive

| 操作 | 指令 |
|------|------|
| 上傳檔案 | `gws drive +upload --file '路徑' --parent FOLDER_ID` |
| 列出檔案 | `gws drive files list --params '{"pageSize":20}'` |
| 搜尋檔案 | `gws drive files list --params '{"q":"name contains '\''關鍵字'\''"}'` |
| 下載檔案 | `gws drive files get --params '{"fileId":"FILE_ID","alt":"media"}' --output '輸出路徑'` |
| 匯出 Google 文件 | `gws drive files export --params '{"fileId":"FILE_ID","mimeType":"application/pdf"}' --output '輸出.pdf'` |
| 建立資料夾 | `gws drive files create --json '{"name":"資料夾名","mimeType":"application/vnd.google-apps.folder","parents":["PARENT_ID"]}'` |
| 刪除檔案 | `gws drive files delete --params '{"fileId":"FILE_ID"}'` |
| 更新檔案內容 | `gws drive files update --params '{"fileId":"FILE_ID"}' --upload '新檔案路徑'` |

### 3. Google Calendar

| 操作 | 指令 |
|------|------|
| 新增行程（快速） | `gws calendar +insert --calendar primary --summary '標題' --start '2026-03-10T09:00:00' --end '2026-03-10T10:00:00'` |
| 快速新增（文字） | `gws calendar events quickAdd --params '{"calendarId":"primary","text":"明天早上 9 點開會"}'` |
| 查看近期行程 | `gws calendar +agenda` |
| 列出行程 | `gws calendar events list --params '{"calendarId":"primary","timeMin":"2026-03-06T00:00:00Z","maxResults":10,"singleEvents":true,"orderBy":"startTime"}'` |
| 取得單一行程 | `gws calendar events get --params '{"calendarId":"primary","eventId":"EVENT_ID"}'` |
| 更新行程 | `gws calendar events patch --params '{"calendarId":"primary","eventId":"EVENT_ID"}' --json '{"summary":"新標題"}'` |
| 刪除行程 | `gws calendar events delete --params '{"calendarId":"primary","eventId":"EVENT_ID"}'` |

### 4. Google Sheets

| 操作 | 指令 |
|------|------|
| 讀取資料 | `gws sheets +read --spreadsheet SHEET_ID --range 'Sheet1!A1:D10'` |
| 附加一行 | `gws sheets +append --spreadsheet SHEET_ID --range 'Sheet1!A1' --values '["值1","值2","值3"]'` |
| 取得試算表資訊 | `gws sheets spreadsheets get --params '{"spreadsheetId":"SHEET_ID"}'` |
| 批次更新 | `gws sheets spreadsheets values batchUpdate --params '{"spreadsheetId":"SHEET_ID"}' --json '{"valueInputOption":"RAW","data":[{"range":"Sheet1!A1","values":[["新值"]]}]}'` |
| 建立新試算表 | `gws sheets spreadsheets create --json '{"properties":{"title":"新試算表"}}'` |

### 5. Google Docs

| 操作 | 指令 |
|------|------|
| 追加文字 | `gws docs +write --document DOC_ID --text '要追加的文字'` |
| 取得文件內容 | `gws docs documents get --params '{"documentId":"DOC_ID"}'` |
| 建立新文件 | `gws docs documents create --json '{"title":"新文件標題"}'` |
| 批次更新（進階） | `gws docs documents batchUpdate --params '{"documentId":"DOC_ID"}' --json '{"requests":[...]}'` |

---

## 錯誤處理

| 錯誤 | 處理 |
|------|------|
| `command not found: gws` | 未安裝。提示：`npm install -g @googleworkspace/cli` |
| `401 Unauthorized` / auth 失敗 | 需重新登入：`gws auth login` |
| `403 Forbidden` | scope 不足。提示：`gws auth login --scope gmail,drive,calendar,sheets,docs` |
| `404 Not Found` | 檔案/文件 ID 不存在，確認 ID 是否正確 |
| `429 Rate Limit` | 短暫等待後重試 |

---

## 輸出格式

所有指令預設輸出 JSON。可用 `--format` 切換：

```bash
gws calendar +agenda --format table    # 表格（人類友善）
gws drive files list --format yaml     # YAML
gws gmail +triage --format csv         # CSV
```

---

*最後更新：2026-03-06*
