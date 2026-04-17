---
aliases:
  - "Google Workspace CLI 指南"
---

# GWS CLI 參考指南（AI 專用）

> **重要：** GWS CLI 的安裝與認證由教師自行在個人環境完成（不再由 TeacherOS 系統統一設定）。
> 以下為 AI 在執行 Google Workspace 操作時的指令參考。

> **用途：** 所有 AI Agent 在執行 Google Workspace 操作前，讀取此文件以取得正確的指令語法。
> **CLI 路徑：** `gws`（若不在 PATH 中，用 `npx @googleworkspace/cli` 替代，或請教師執行 `npm install -g @googleworkspace/cli`）
> **認證：** 加密憑證存於本機（macOS/Linux: `~/.config/gws/`；Windows: `%APPDATA%\gws\`），首次使用需 `gws auth login --account EMAIL`。
> **跨平台：** 本指南適用 macOS、Linux、Windows。AI 應偵測 OS 後選擇對應指令。
> **版本：** 0.22.5（pre-v1.0，次版本更新可能有破壞性變更）
> **架構：** gws 在 runtime 讀取 Google Discovery Service JSON 動態建構 CLI 指令樹，Google 新增 API 端點時自動支援。

---

## 唯一整合路徑

**所有 Google Workspace 操作統一且唯一使用 gws CLI。** 不使用 MCP 連接器、不使用瀏覽器自動化、不使用直接 API 呼叫。

| 情境 | 處理方式 |
|------|---------|
| 有終端機的 AI（Claude Code、Gemini、Cowork） | 直接執行 gws CLI |
| 無終端機的 AI（Gemini 語音、ChatGPT） | 提示教師手動操作，提供 gws 指令供複製 |
| gws 未安裝 | 提示教師自行安裝 gws CLI（`npm install -g @googleworkspace/cli`） |

---

## 可用性確認

執行前先確認 gws CLI 可用：

```bash
# 1. 確認已安裝
command -v gws || npx @googleworkspace/cli --version
# 若都失敗 → 提示教師：npm install -g @googleworkspace/cli

# 2. 確認已登入（直接呼叫 API 驗證——不要用 gws auth status，其輸出不可靠）
gws gmail users getProfile --params '{"userId":"me"}'
# 若 401 → 需登入：gws auth login --account <教師的default email>

# 3. 確認帳號清單
gws auth list
```

若未安裝或未登入，提示教師：「請自行安裝 gws CLI（`npm install -g @googleworkspace/cli`）並執行 `gws auth login` 完成登入。」

---

## 指令語法

```
gws <service> <resource> [sub-resource] <method> [flags]
```

Help 可在每一層取得：

```bash
gws --help
gws drive --help
gws drive files --help
gws schema drive.files.list    # 查看該 API 的參數型別與必填欄位（debug 必備）
```

---

## 全域旗標（所有指令通用）

| 旗標 | 用途 | 範例 |
|------|------|------|
| `--params '<JSON>'` | URL/查詢參數 | `--params '{"fileId":"xxx"}'` |
| `--json '<JSON>'` | 請求本體（POST/PUT/PATCH） | `--json '{"name":"新檔"}'` |
| `--fields '<MASK>'` | 欄位遮罩，縮減回傳量省 token | `--fields 'files(id,name,mimeType)'` |
| `--upload <PATH>` | 上傳檔案（multipart） | `--upload ./report.pdf` |
| `--upload-content-type` | 強制指定上傳 MIME 類型 | `--upload-content-type image/png` |
| `--output <PATH>` | 二進位下載目的地 | `--output ./file.pdf` |
| `--page-all` | 自動分頁，每頁一行 NDJSON | 搭配 `jq` 處理 |
| `--page-limit <N>` | 最多抓幾頁（預設 10） | `--page-limit 5` |
| `--page-delay <MS>` | 頁間延遲毫秒（預設 100） | `--page-delay 200` |
| `--dry-run` | 預覽請求但不執行 | 檢查指令是否正確 |
| `--format` | 輸出格式：json / table / yaml / csv | `--format table` |

### 欄位遮罩（--fields）最佳實踐

列出或取得資源時，務必使用 `--fields` 縮減回傳資料量。大幅節省 context window：

```bash
# 不好——回傳完整物件，大量無用欄位
gws drive files list --params '{"pageSize":20}'

# 好——只回傳需要的欄位
gws drive files list --params '{"pageSize":20}' --fields 'files(id,name,mimeType,modifiedTime)'
```

### 自動分頁（--page-all）

不需手動處理 `nextPageToken`，gws 自動抓取所有頁面：

```bash
gws drive files list --params '{"pageSize":100}' --page-all | jq -r '.files[].name'
gws gmail users messages list --params '{"userId":"me","maxResults":100}' --page-all --page-limit 3
```

### Schema 查詢（debug 必備）

不確定某個 API 需要哪些參數時，先查 schema：

```bash
gws schema drive.files.list
gws schema gmail.users.messages.get
gws schema calendar.events.insert
```

---

## 多帳號切換

gws 支援多帳號。教師的帳號別名定義在 `{workspace}/teacheros-personal.yaml` 的 `google_accounts` 區塊。

**切換方式：** 在指令前加環境變數（注意：登入時用 `--account`，使用時用環境變數，兩者語法不同）。

```bash
# 使用預設帳號（不需額外設定）
gws gmail +send --to "someone@example.com" --subject "..." --body "..."

# 指定帳號（使用時）
GOOGLE_WORKSPACE_CLI_ACCOUNT=linintellectdave@gmail.com gws gmail +send --to "..." --subject "..." --body "..."

# 登入時綁定帳號（設定時）
gws auth login --account linintellectdave@gmail.com
```

**AI 判斷規則：**

1. 讀取 `teacheros-personal.yaml` 中的 `google_accounts.accounts[].keywords`
2. 比對教師口語指令中是否包含任何 keyword
3. 若命中 → 使用對應帳號
4. 若未命中 → 使用 `google_accounts.default`
5. 切換時主動告知教師：「使用 [別名] 帳號（[email]）」

---

## 核心服務指令速查

### 1. Gmail

| 操作 | 指令 |
|------|------|
| 寄信（純文字） | `gws gmail +send --to EMAIL --subject '主旨' --body '內文'` |
| 寄信（附件） | `gws gmail +send --to EMAIL --subject '主旨' --body '內文' --attach ./file.pdf` |
| 寄信（HTML） | `gws gmail +send --to EMAIL --subject '主旨' --body '<h1>標題</h1>' --html` |
| 寄信（CC/BCC） | `gws gmail +send --to EMAIL --cc CC_EMAIL --bcc BCC_EMAIL --subject '主旨' --body '...'` |
| 寄信（指定寄件別名） | `gws gmail +send --from ALIAS_EMAIL --to EMAIL --subject '...' --body '...'` |
| 寄信（存草稿不寄出） | `gws gmail +send --to EMAIL --subject '...' --body '...' --draft` |
| 回覆（自動串信） | `gws gmail +reply --message-id MSG_ID --body '回覆內容'` |
| 回覆全部 | `gws gmail +reply-all --message-id MSG_ID --body '回覆內容'` |
| 回覆全部（排除某人） | `gws gmail +reply-all --message-id MSG_ID --body '...' --remove exclude@email.com` |
| 轉寄 | `gws gmail +forward --message-id MSG_ID --to NEW_EMAIL --body '轉寄說明'` |
| 讀信（簡潔版） | `gws gmail +read --id MSG_ID` |
| 讀信（含標頭） | `gws gmail +read --id MSG_ID --headers` |
| 收件匣摘要 | `gws gmail +triage` |
| 收件匣摘要（指定數量） | `gws gmail +triage --max 20` |
| 收件匣摘要（加篩選） | `gws gmail +triage --query 'from:xxx'` |
| 列出信件 | `gws gmail users messages list --params '{"userId":"me","maxResults":10}'` |
| 搜尋信件 | `gws gmail users messages list --params '{"userId":"me","q":"from:xxx subject:yyy"}'` |
| 取得原始信件 | `gws gmail users messages get --params '{"userId":"me","id":"MSG_ID"}'` |
| 建立草稿 | `gws gmail users drafts create --params '{"userId":"me"}' --json '{"message":{"raw":"BASE64"}}'` |
| 寄送草稿 | `gws gmail users drafts send --params '{"userId":"me"}' --json '{"id":"DRAFT_ID"}'` |
| 刪信（丟垃圾桶） | `gws gmail users messages trash --params '{"userId":"me","id":"MSG_ID"}'` |

**中文主旨注意：** `+send --subject` 的中文會亂碼。中文主旨必須用 Python `email.mime.text.MIMEText` 組 MIME 訊息，透過 `drafts create` + `drafts send` 發送。純英文主旨可直接用 `+send`。詳見 `send-email` 技能。

**回覆鏈功能說明：** `+reply` / `+reply-all` / `+forward` 自動處理 RFC 5322 格式、MIME 編碼、base64、`In-Reply-To` / `References` / `threadId` 標頭、原文引用、內嵌圖片保留。附件上限 25MB。

### 2. Google Drive

| 操作 | 指令 |
|------|------|
| 上傳檔案 | `gws drive +upload --file '路徑' --parent FOLDER_ID` |
| 上傳（multipart，自訂 metadata） | `gws drive files create --json '{"name":"report.pdf"}' --upload ./report.pdf` |
| 上傳（指定 MIME） | `gws drive files create --json '{"name":"img.png"}' --upload ./img.png --upload-content-type image/png` |
| 列出檔案 | `gws drive files list --params '{"pageSize":20}' --fields 'files(id,name,mimeType)'` |
| 列出所有檔案（自動分頁） | `gws drive files list --params '{"pageSize":100}' --page-all` |
| 搜尋檔案 | `gws drive files list --params '{"q":"name contains '\''關鍵字'\''"}'` |
| 下載檔案 | `gws drive files get --params '{"fileId":"FILE_ID","alt":"media"}' --output '輸出路徑'` |
| 匯出 Google 文件為 PDF | `gws drive files export --params '{"fileId":"FILE_ID","mimeType":"application/pdf"}' --output '輸出.pdf'` |
| 建立資料夾 | `gws drive files create --json '{"name":"資料夾名","mimeType":"application/vnd.google-apps.folder","parents":["PARENT_ID"]}'` |
| 更新檔案內容 | `gws drive files update --params '{"fileId":"FILE_ID"}' --upload '新檔案路徑'` |
| 複製檔案 | `gws drive files copy --params '{"fileId":"FILE_ID"}' --json '{"name":"副本名稱"}'` |
| 刪除檔案 | `gws drive files delete --params '{"fileId":"FILE_ID"}'` |

### 3. Google Calendar

| 操作 | 指令 |
|------|------|
| 新增行程 | `gws calendar +insert --calendar primary --summary '標題' --start '2026-04-10T09:00:00' --end '2026-04-10T10:00:00'` |
| 新增行程（含地點） | `gws calendar +insert --calendar primary --summary '標題' --start '...' --end '...' --location '會議室'` |
| 新增行程（含說明） | `gws calendar +insert --calendar primary --summary '標題' --start '...' --end '...' --description '詳細內容'` |
| 新增行程（含出席者） | `gws calendar +insert --calendar primary --summary '標題' --start '...' --end '...' --attendee a@x.com --attendee b@x.com` |
| 新增行程（含 Meet） | `gws calendar +insert --calendar primary --summary '標題' --start '...' --end '...' --meet` |
| 快速新增（文字） | `gws calendar events quickAdd --params '{"calendarId":"primary","text":"明天早上 9 點開會"}'` |
| 查看今天行程 | `gws calendar +agenda --today` |
| 查看明天行程 | `gws calendar +agenda --tomorrow` |
| 查看本週行程 | `gws calendar +agenda --week` |
| 查看未來 N 天 | `gws calendar +agenda --days 14` |
| 查看特定日曆 | `gws calendar +agenda --calendar CALENDAR_ID` |
| 列出行程（原始 API） | `gws calendar events list --params '{"calendarId":"primary","timeMin":"2026-04-01T00:00:00Z","maxResults":10,"singleEvents":true,"orderBy":"startTime"}'` |
| 取得單一行程 | `gws calendar events get --params '{"calendarId":"primary","eventId":"EVENT_ID"}'` |
| 更新行程 | `gws calendar events patch --params '{"calendarId":"primary","eventId":"EVENT_ID"}' --json '{"summary":"新標題"}'` |
| 刪除行程 | `gws calendar events delete --params '{"calendarId":"primary","eventId":"EVENT_ID"}'` |

**時區：** `+agenda` 與 `+insert` 自動讀取 Google 帳號時區（快取 24 小時），不需手動指定。可用 `--timezone` / `--tz` 覆寫。

### 4. Google Sheets

| 操作 | 指令 |
|------|------|
| 讀取資料 | `gws sheets +read --spreadsheet SHEET_ID --range 'Sheet1!A1:D10'` |
| 附加一行（CSV 值） | `gws sheets +append --spreadsheet SHEET_ID --range 'Sheet1!A1' --values '["值1","值2","值3"]'` |
| 附加一行（JSON 值） | `gws sheets +append --spreadsheet SHEET_ID --range 'Sheet1!A1' --json-values '[["值1","值2"]]'` |
| 取得試算表資訊 | `gws sheets spreadsheets get --params '{"spreadsheetId":"SHEET_ID"}'` |
| 批次更新 | `gws sheets spreadsheets values batchUpdate --params '{"spreadsheetId":"SHEET_ID"}' --json '{"valueInputOption":"RAW","data":[{"range":"Sheet1!A1","values":[["新值"]]}]}'` |
| 建立新試算表 | `gws sheets spreadsheets create --json '{"properties":{"title":"新試算表"}}'` |
| 清除範圍 | `gws sheets spreadsheets values clear --params '{"spreadsheetId":"SHEET_ID","range":"Sheet1!A1:D10"}'` |

**Shell 跳脫注意：** Sheets 範圍使用 `!`，bash 會解讀為 history expansion。務必用單引號包覆：`'Sheet1!A1:D10'`。

### 5. Google Docs

| 操作 | 指令 |
|------|------|
| 追加文字 | `gws docs +write --document DOC_ID --text '要追加的文字'` |
| 取得文件內容 | `gws docs documents get --params '{"documentId":"DOC_ID"}'` |
| 建立新文件 | `gws docs documents create --json '{"title":"新文件標題"}'` |
| 批次更新（進階格式） | `gws docs documents batchUpdate --params '{"documentId":"DOC_ID"}' --json '{"requests":[...]}'` |

**限制：** `+write` 只能追加純文字。複雜格式（粗體、表格、圖片）需使用 `batchUpdate` 原始 API。

---

## 擴充服務

gws 因動態指令面，可存取所有 Google Discovery API。以下為 TeacherOS 可能用到的擴充服務：

### 6. Google Tasks（待辦事項）

| 操作 | 指令 |
|------|------|
| 列出待辦清單 | `gws tasks tasklists list` |
| 建立待辦清單 | `gws tasks tasklists insert --json '{"title":"新清單"}'` |
| 列出任務 | `gws tasks tasks list --params '{"tasklist":"TASKLIST_ID"}'` |
| 新增任務 | `gws tasks tasks insert --params '{"tasklist":"TASKLIST_ID"}' --json '{"title":"任務名稱","due":"2026-04-10T00:00:00Z"}'` |
| 完成任務 | `gws tasks tasks patch --params '{"tasklist":"TASKLIST_ID","task":"TASK_ID"}' --json '{"status":"completed"}'` |
| 刪除任務 | `gws tasks tasks delete --params '{"tasklist":"TASKLIST_ID","task":"TASK_ID"}'` |

限制：每人最多 2,000 個清單、20,000 個任務/清單、100,000 個任務/帳號。

### 7. Google Slides（簡報）

| 操作 | 指令 |
|------|------|
| 建立簡報 | `gws slides presentations create --json '{"title":"新簡報"}'` |
| 取得簡報 | `gws slides presentations get --params '{"presentationId":"PRES_ID"}'` |
| 取得頁面縮圖 | `gws slides presentations pages getThumbnail --params '{"presentationId":"PRES_ID","pageObjectId":"PAGE_ID"}'` |
| 批次更新 | `gws slides presentations batchUpdate --params '{"presentationId":"PRES_ID"}' --json '{"requests":[...]}'` |

### 8. Google People（聯絡人）

**已知問題：** gws CLI v0.18-v0.22 的 People API 呼叫存在 scope 傳遞 bug，即使 token 包含 `contacts` scope 仍回傳 403。在 gws 修復前，使用 wrapper 腳本：

```bash
# 搜尋聯絡人（推薦）
python3 setup/scripts/gws-contacts.py search "謝易霖"

# 列出所有聯絡人
python3 setup/scripts/gws-contacts.py list

# 列出並篩選
python3 setup/scripts/gws-contacts.py list --filter "謝"

# JSON 輸出（供程式處理）
python3 setup/scripts/gws-contacts.py search "名字" --json
```

Wrapper 腳本位於 `setup/scripts/gws-contacts.py`，讀取 gws 的加密憑證直接呼叫 People API。

**gws 原生指令（待 bug 修復後啟用）：**

| 操作 | 指令 |
|------|------|
| 搜尋聯絡人 | `gws people people searchContacts --params '{"query":"名字","readMask":"names,emailAddresses"}'` |
| 列出聯絡人 | `gws people people connections list --params '{"resourceName":"people/me","personFields":"names,emailAddresses"}'` |
| 新增聯絡人 | `gws people people createContact --json '{"names":[{"givenName":"名","familyName":"姓"}],"emailAddresses":[{"value":"email@x.com"}]}'` |

**注意：** 搜尋前需先送一次空查詢做 warmup（Google API 限制）。`personFields` 為必填。

### 9. Google Meet（會議紀錄）

| 操作 | 指令 |
|------|------|
| 建立會議空間 | `gws meet spaces create` |
| 列出會議紀錄 | `gws meet conferenceRecords list` |
| 查看參與者 | `gws meet conferenceRecords participants list --params '{"parent":"conferenceRecords/RECORD_ID"}'` |
| 查看逐字稿 | `gws meet conferenceRecords transcripts list --params '{"parent":"conferenceRecords/RECORD_ID"}'` |

### 10. Google Classroom（課堂）

| 操作 | 指令 |
|------|------|
| 列出課程 | `gws classroom courses list` |
| 建立課程 | `gws classroom courses create --json '{"name":"課程名","section":"班級"}'` |
| 列出作業 | `gws classroom courses courseWork list --params '{"courseId":"COURSE_ID"}'` |

### 11. Apps Script

| 操作 | 指令 |
|------|------|
| 推送本機檔案至 Apps Script 專案 | `gws script +push --script SCRIPT_ID --dir ./local-script-folder/` |

**警告：** `+push` 會覆蓋專案中的所有檔案（破壞性操作）。支援 .gs、.js、.html、appsscript.json。

---

## 跨服務工作流（gws workflow）

| 操作 | 指令 | 說明 |
|------|------|------|
| 今日站立會議報告 | `gws workflow +standup-report` | 今天的會議 + 待辦事項（唯讀） |
| 下場會議準備 | `gws workflow +meeting-prep` | 議程、出席者、連結文件（唯讀） |
| 信件轉待辦 | `gws workflow +email-to-task --message-id MSG_ID --tasklist LIST_ID` | 將 Gmail 信件轉為 Tasks 項目 |
| 本週摘要 | `gws workflow +weekly-digest` | 本週會議 + 未讀信統計（唯讀） |
| 公告 Drive 檔案 | `gws workflow +file-announce --file-id FILE_ID --space SPACE_ID` | 在 Chat 空間公告檔案 |

---

## 認證機制

### 認證優先順序（最高到最低）

| 優先 | 來源 | 設定方式 |
|------|------|---------|
| 1 | Access token | `GOOGLE_WORKSPACE_CLI_TOKEN` 環境變數 |
| 2 | 憑證檔案 | `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` 環境變數 |
| 3 | 加密憑證 | `gws auth login`（預設方式） |
| 4 | 明文憑證 | `~/.config/gws/credentials.json` |

### 認證子指令

```bash
gws auth setup          # 首次設定（需 gcloud CLI）
gws auth login           # OAuth 登入（選 scope）
gws auth login -s drive,gmail,sheets   # 只授權部分服務（避免 scope 上限）
gws auth export --unmasked   # 匯出憑證（CI/headless 用）
gws auth list            # 列出已登入帳號
```

**Scope 限制：** 未驗證的 OAuth app 限約 25 個 scope。用 `recommended` 預設會失敗。必須用 `-s` 指定個別服務。

### Service Account（伺服器端）

```bash
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/service-account.json
gws drive files list   # 不需 login
```

---

## 環境變數完整列表

| 變數 | 用途 |
|------|------|
| `GOOGLE_WORKSPACE_CLI_TOKEN` | 預取得的 OAuth2 access token |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | 憑證 JSON 路徑（user 或 service account） |
| `GOOGLE_WORKSPACE_CLI_ACCOUNT` | 指定使用的帳號（多帳號切換） |
| `GOOGLE_WORKSPACE_CLI_CLIENT_ID` | OAuth client ID（替代 client_secret.json） |
| `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` | 設定目錄覆寫（預設 `~/.config/gws`） |
| `GOOGLE_WORKSPACE_CLI_LOG` | stderr 日誌等級（如 `gws=debug`） |
| `GOOGLE_WORKSPACE_CLI_LOG_FILE` | JSON 日誌檔目錄（每日輪替） |
| `GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND` | 設為 `file` 改用檔案加密金鑰（替代 OS keyring） |
| `GOOGLE_WORKSPACE_PROJECT_ID` | GCP project ID 覆寫 |

所有環境變數也可寫入 `.env` 檔案（gws 自動讀取）。

---

## 錯誤處理

### Exit Codes

| 代碼 | 意義 | 處理 |
|------|------|------|
| 0 | 成功 | — |
| 1 | API 錯誤 | Google 回傳 4xx/5xx，檢查參數 |
| 2 | 認證錯誤 | 憑證遺失/過期/無效 → `gws auth login --account EMAIL` |
| 3 | 驗證錯誤 | 參數錯誤、未知服務、無效旗標 → 用 `gws schema` 檢查 |
| 4 | Discovery 錯誤 | 無法取得 API schema → 檢查網路 |
| 5 | 內部錯誤 | 非預期失敗 |

### 常見錯誤速查

| 錯誤 | 處理 |
|------|------|
| `command not found: gws` | 未安裝。嘗試 `npx @googleworkspace/cli`，或提示：`npm install -g @googleworkspace/cli` |
| `401 Unauthorized` | 需重新登入：`gws auth login --account EMAIL`（必須帶 --account） |
| `403 Forbidden` | scope 不足。提示：`gws auth login --account EMAIL -s gmail,drive,calendar,sheets,docs` |
| `404 Not Found` | 檔案/文件 ID 不存在，確認 ID 是否正確 |
| `429 Rate Limit` | 短暫等待後重試 |

---

## 已知限制

1. **中文主旨亂碼**：`gws gmail +send --subject` 的中文會 mojibake，須用 Python MIME workaround
2. **Docs +write 限純文字**：複雜格式需用 `batchUpdate` 原始 API
3. **Chat +send 限純文字**：卡片式訊息需用底層 API
4. **Script +push 為破壞性操作**：覆蓋專案所有檔案
5. **Forms create 限制**：只能設 title，其他欄位需另外 `batchUpdate`
6. **Keep 刪除不可復原**：永久刪除，無法還原
7. **Drive 同一檔案不可並行權限操作**
8. **Shell 跳脫**：Sheets 範圍的 `!` 在 bash 需用單引號（zsh 需雙引號）
9. **Discovery 快取 24 小時**：新建 API 端點最多需等 24 小時

---

*最後更新：2026-04-02*
