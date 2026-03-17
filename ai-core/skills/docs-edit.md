---
name: docs-edit
description: Google Docs 文件操作。讀取、追加文字、建立新文件、進階編輯。優先使用 gws CLI。
triggers:
  - 編輯文件
  - 寫入 Docs
  - 開 Google Docs
  - 追加文字
  - 建立文件
  - Google Docs
requires_args: false
args_format: "[選填：文件名稱或 ID + 操作描述]"
---

# skill: docs-edit — Google Docs 文件操作

讀取文件內容、追加文字、建立新文件、進階批次編輯。

## 根目錄

以 Repo 根目錄為基準。gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`。

## 工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機 + gws CLI | `gws docs +write` / `documents get/create/batchUpdate` |
| 無終端機 | 提醒教師手動操作 Google Docs |

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

### Step 1 — 確認目標文件

教師提供文件名稱或 ID。若只有名稱，先搜尋 Drive 取得 ID：

```bash
gws drive files list --params '{"q":"name='\''文件名稱'\'' and mimeType='\''application/vnd.google-apps.document'\''"}' --format table
```

### Step 2 — 執行操作

**讀取文件內容：**
```bash
gws docs documents get --params '{"documentId":"DOC_ID"}'
```

**追加文字（簡單）：**
```bash
gws docs +write --document DOC_ID --text '要追加的文字'
```

**建立新文件：**
```bash
gws docs documents create --json '{"title":"新文件標題"}'
```

**進階批次編輯（插入、刪除、格式化）：**
```bash
gws docs documents batchUpdate --params '{"documentId":"DOC_ID"}' --json '{
  "requests": [
    {
      "insertText": {
        "location": {"index": 1},
        "text": "插入的文字\n"
      }
    }
  ]
}'
```

### Step 3 — 報告結果

回報操作結果。若為讀取，摘要顯示文件內容重點。

## 注意事項

- `+write` 只能追加純文字到文件尾端；需要格式化或插入特定位置時使用 `batchUpdate`
- `batchUpdate` 的 `index` 是字元位置，`1` = 文件開頭
- 若文件 ID 未知，先從 Drive 搜尋
- 刪除文件內容需教師確認
