---
name: calendar
description: Google Calendar 行事曆操作。查詢行程、新增/修改/刪除事件。優先使用 gws CLI。
triggers:
  - 查行事曆
  - 排課表
  - 加行事曆
  - 看行程
  - 新增行程
  - 改行程
  - 刪行程
  - calendar
requires_args: false
args_format: "[選填：操作類型 + 日期或事件描述]"
---

# skill: calendar — Google Calendar 行事曆操作

查詢行程、新增事件、修改或刪除行事曆項目。

## 根目錄

以 Repo 根目錄為基準。gws CLI 指令參考：`ai-core/reference/gws-cli-guide.md`。

## 工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機 + gws CLI | `gws calendar +insert/+agenda` / `events list/get/update/delete` |
| 無終端機 | 提醒教師手動操作 Google Calendar |

## 執行步驟

### Step 0 — 確認 gws CLI 可用

```bash
command -v gws && gws auth status
```

### Step 1 — 判斷操作類型

| 教師說 | 操作 |
|--------|------|
| 「看行程」「這週有什麼」 | 查詢行程 |
| 「加行程」「排進去」 | 新增事件 |
| 「改時間」「換日期」 | 修改事件 |
| 「取消」「刪掉那個」 | 刪除事件（需確認） |

### Step 2 — 執行操作

**查詢近期行程：**
```bash
gws calendar +agenda --format table
```

**查詢指定日期範圍：**
```bash
gws calendar events list --params '{"calendarId":"primary","timeMin":"START_ISO","timeMax":"END_ISO","singleEvents":true,"orderBy":"startTime"}' --format table
```

**新增事件：**
```bash
gws calendar +insert --calendar primary --summary '標題' --start 'YYYY-MM-DDTHH:MM:SS' --end 'YYYY-MM-DDTHH:MM:SS'
```

或用自然語言快速新增：
```bash
gws calendar events quickAdd --params '{"calendarId":"primary","text":"明天早上 9 點開會"}'
```

**修改事件：**
```bash
gws calendar events patch --params '{"calendarId":"primary","eventId":"EVENT_ID"}' --json '{"summary":"新標題","start":{"dateTime":"新時間"},"end":{"dateTime":"新結束"}}'
```

**刪除事件（需教師確認）：**
```bash
gws calendar events delete --params '{"calendarId":"primary","eventId":"EVENT_ID"}'
```

### Step 3 — 報告結果

以簡潔中文回報。查詢結果以表格呈現。

## 注意事項

- 刪除行程必須向教師確認後才執行
- 時間格式為 ISO 8601（`YYYY-MM-DDTHH:MM:SS`）
- 預設行事曆為 `primary`，教師若有多個行事曆需確認目標
