---
name: send-email
description: 透過 Gmail 寄送郵件。確認收件人與內容後直接寄出，支援 CC/BCC 與 HTML。優先使用 gws CLI。
triggers:
  - 寄信
  - 寄 email
  - 發郵件
  - 寄給
  - send email
  - 寫信給
  - 發 email
  - 寄 mail
requires_args: false
args_format: "[選填：收件人 Email]"
---

# skill: send-email — Gmail 寄信

確認收件人、主旨、內文後，直接寄出郵件。不存草稿匣。

## 根目錄

以 Repo 根目錄為基準。gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`。

## 工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機 + gws CLI | `gws gmail +send` 直寄純文字；HTML 用 `users messages send` |
| 無終端機（Gemini 語音等） | AI 協助撰寫內文，提醒教師自行從 Gmail 寄出 |

## 執行步驟

### Step 0 — 確認 gws CLI 可用

**macOS / Linux：**
```bash
command -v gws && gws auth status
```

**Windows（PowerShell）：**
```powershell
Get-Command gws -ErrorAction SilentlyContinue && gws auth status
```

若未安裝或未登入，提示教師手動寄送。

### Step 1 — 確認信件參數

從教師指令或對話脈絡中取得：

- **收件人（to）**：必填
- **主旨（subject）**：必填
- **內文（body）**：必填，可從對話中既有內容取用
- **CC / BCC**：選填

若資訊不完整，一次詢問所有缺少的欄位，不逐一追問。

### Step 2 — 向教師確認

摘要顯示：

> 收件人：xxx@example.com
> 主旨：[主旨]
> 內文前幾行...
>
> 確認寄出？

教師確認後進入 Step 3。

### Step 3 — 寄出

> **編碼警告**：`gws gmail +send --subject` 無法正確處理中文主旨（會產生 mojibake 亂碼）。
> **只有純英文主旨**才能用 `+send` 快捷指令。含中文主旨一律走草稿流程。

**方法 A — 純英文主旨的純文字信件：**

```bash
gws gmail +send --to 'EMAIL' --subject 'English subject only' --body '內文'
```

**方法 B — 中文主旨（必須使用此方法）、HTML 格式、CC/BCC、或多收件人：**

使用 Python `email.mime` 模組組裝 MIME 訊息，確保 header 編碼正確：

```python
import base64, json, subprocess
from email.mime.text import MIMEText

import shutil
gws = shutil.which("gws")  # 自動偵測 gws 路徑
params_me = json.dumps({"userId": "me"})

# 組裝 MIME 訊息（自動處理中文 Subject 的 RFC 2047 編碼）
msg = MIMEText("內文內容", "plain", "utf-8")  # HTML 信件改 "html"
msg["To"] = "recipient@example.com"
msg["Subject"] = "中文主旨完全沒問題"
# msg["Cc"] = "cc@example.com"       # 選填
# msg["Bcc"] = "bcc@example.com"     # 選填

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
draft_json = json.dumps({"message": {"raw": raw}})

# 建立草稿
r1 = subprocess.run(
    [gws, "gmail", "users", "drafts", "create",
     "--params", params_me, "--json", draft_json],
    capture_output=True, text=True,
)
draft_id = json.loads(r1.stdout)["id"]

# 寄出草稿
send_json = json.dumps({"id": draft_id})
subprocess.run(
    [gws, "gmail", "users", "drafts", "send",
     "--params", params_me, "--json", send_json],
    capture_output=True, text=True,
)
```

**批次寄信**時，將收件人放入 list 迴圈執行即可（每人各建一封草稿再寄出）。

### Step 4 — 報告結果

寄送成功後回報：

> 已寄出。收件人：xxx@example.com，主旨：[主旨]。

若失敗，顯示錯誤訊息並建議排除方式。

## 常用指令速查

| 操作 | 指令 |
|------|------|
| 純文字寄信（英文主旨） | `gws gmail +send --to EMAIL --subject 'Subject' --body '內文'` |
| 中文主旨寄信 | Python MIME + drafts create → drafts send（見 Step 3 方法 B） |
| 收件匣摘要 | `gws gmail +triage` |
| 搜尋信件 | `gws gmail users messages list --params '{"userId":"me","q":"搜尋條件"}'` |
| 讀信 | `gws gmail users messages get --params '{"userId":"me","id":"MSG_ID"}'` |

## 注意事項

- 教師說「寄」就寄，不存草稿匣（草稿僅作為寄送中繼，寄出即刪除）
- **中文主旨禁用 `+send`**——這是已知 bug，會產生 mojibake 亂碼。一律走 Python MIME 草稿流程
- 信件附件目前不支援自動處理，需提醒教師手動附加
- 全程使用繁體中文回應
