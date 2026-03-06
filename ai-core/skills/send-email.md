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

```bash
command -v gws && gws auth status
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

**純文字信件（最常見）：**

```bash
gws gmail +send --to 'EMAIL' --subject '主旨' --body '內文'
```

**需要 HTML 格式、CC/BCC、或多收件人：**

先建立草稿再寄出：

```bash
# 建立草稿（base64 編碼的 MIME 訊息）
gws gmail users drafts create --params '{"userId":"me"}' --json '{"message":{"raw":"BASE64_ENCODED_MIME"}}'

# 寄出草稿
gws gmail users drafts send --params '{"userId":"me"}' --json '{"id":"DRAFT_ID"}'
```

### Step 4 — 報告結果

寄送成功後回報：

> 已寄出。收件人：xxx@example.com，主旨：[主旨]。

若失敗，顯示錯誤訊息並建議排除方式。

## 常用指令速查

| 操作 | 指令 |
|------|------|
| 純文字寄信 | `gws gmail +send --to EMAIL --subject '主旨' --body '內文'` |
| 收件匣摘要 | `gws gmail +triage` |
| 搜尋信件 | `gws gmail users messages list --params '{"userId":"me","q":"搜尋條件"}'` |
| 讀信 | `gws gmail users messages get --params '{"userId":"me","id":"MSG_ID"}'` |

## 注意事項

- 教師說「寄」就寄，不存草稿匣
- 信件附件目前不支援自動處理，需提醒教師手動附加
- 全程使用繁體中文回應
