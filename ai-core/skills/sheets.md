---
name: sheets
description: Google Sheets 試算表操作。讀取、寫入、附加資料、建立新試算表。優先使用 gws CLI。
triggers:
  - 開試算表
  - 寫入 Sheets
  - 讀 Sheets
  - 看試算表
  - 加一行
  - 更新 Sheets
  - Google Sheets
requires_args: false
args_format: "[選填：試算表名稱或 ID + 操作描述]"
---

# skill: sheets — Google Sheets 試算表操作

讀取、寫入、附加資料列、建立新試算表。

## 根目錄

以 Repo 根目錄為基準。gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`。

## 工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機 + gws CLI | `gws sheets +read/+append` / `spreadsheets` 全 API |
| 無終端機 | 提醒教師手動操作 Google Sheets |

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

### Step 1 — 確認目標試算表

教師提供試算表名稱或 ID。若只有名稱，先搜尋 Drive 取得 ID：

```bash
gws drive files list --params '{"q":"name='\''試算表名稱'\'' and mimeType='\''application/vnd.google-apps.spreadsheet'\''"}' --format table
```

### Step 2 — 執行操作

**讀取資料：**
```bash
gws sheets +read --spreadsheet SHEET_ID --range 'Sheet1!A1:D10'
```

**附加一行：**
```bash
gws sheets +append --spreadsheet SHEET_ID --range 'Sheet1!A1' --values '["值1","值2","值3"]'
```

**批次更新（覆寫指定範圍）：**
```bash
gws sheets spreadsheets values batchUpdate --params '{"spreadsheetId":"SHEET_ID"}' --json '{"valueInputOption":"RAW","data":[{"range":"Sheet1!A1:C1","values":[["值1","值2","值3"]]}]}'
```

**建立新試算表：**
```bash
gws sheets spreadsheets create --json '{"properties":{"title":"新試算表名稱"}}'
```

**取得試算表資訊（工作表清單等）：**
```bash
gws sheets spreadsheets get --params '{"spreadsheetId":"SHEET_ID"}'
```

### Step 3 — 報告結果

讀取結果以表格或列點呈現。寫入操作回報成功與影響範圍。

## 注意事項

- 大量寫入建議用 `batchUpdate`，避免逐格操作
- 範圍格式：`工作表名稱!起始:結束`（例：`Sheet1!A1:D10`）
- 若試算表 ID 未知，先從 Drive 搜尋
