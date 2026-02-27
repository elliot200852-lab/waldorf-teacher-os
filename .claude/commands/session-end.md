# /session-end — 對話收尾同步

從當前對話中提取有變動的資訊，產生 YAML diff，寫入 english-session.yaml。
只更新有變動的欄位，不重寫整份文件。

## 使用方式

```
/session-end 9c
/session-end 8a
/session-end 7a
```

## 執行規則

`$ARGUMENTS` 是班級代碼（9c、8a 或 7a）。

若未提供 `$ARGUMENTS`，先詢問：「請問要收尾哪個班級的工作？（9c / 8a / 7a）」，等待回應後再繼續。

## 執行步驟

### Step 1 — 讀取現有狀態

讀取：`projects/class-$ARGUMENTS/working/english-session.yaml`

### Step 2 — 掃描當前對話，提取變動

從本次對話中，識別以下欄位是否有新資訊或變動：

| 欄位 | 判斷依據 |
|------|---------|
| `current_position` | 這次工作推進到哪個區塊 / 步驟 / 單元 |
| `confirmed_decisions` | 這次對話中教師確認的設計決策（如：主題選定、評量比例、單元架構） |
| `next_action.description` | 下一次對話應從哪裡繼續 |
| `next_action.input_needed_from_teacher` | 下次開始前教師需要準備或決定的事項 |
| `open_questions` | 尚未解決的問題，或本次新產生的問題 |
| `output_files` | 本次產出了哪些 .md 檔案（記錄路徑與版本號） |
| `last_updated` | 自動填入今天日期（格式：YYYY-MM-DD） |

### Step 3 — 產生 YAML diff

只列出有變動的欄位。格式如下：

```
# session-end diff｜class-$ARGUMENTS｜[今天日期]
# 以下為有變動的欄位，其餘欄位維持不變

english_session:
  last_updated: [今天日期]

  current_position:
    block: [值]          # 若有變動
    step: [值]           # 若有變動
    sub_block: [值]      # 若有變動
    unit_number: [值]    # 若有變動

  confirmed_decisions:   # 只附加新決策，不刪除舊項目
    - [新確認的決策]

  next_action:
    description: [下一步描述]
    input_needed_from_teacher: [教師需準備的事項，若無填 null]

  open_questions:        # 只附加新問題，已解決的從原列表移除
    - [待決問題]

  output_files:
    syllabus_versions:   # 若有新產出才更新
      - version: [vN]
        date: [YYYYMMDD]
        paths:
          class_view: [路徑]
          subject_view: [路徑]
```

若某欄位在本次對話中沒有任何變動，從 diff 中完全省略。

### Step 4 — 確認並寫入

輸出 diff 後，詢問：

「確認寫入 `english-session.yaml` 嗎？（是 / 否）」

- 若確認：將 diff 中的欄位合併寫入原檔案，不覆蓋未列出的欄位
- 若否定：保留 diff 供教師手動調整，不執行寫入

## 注意事項

- `confirmed_decisions` 與 `open_questions` 採**附加邏輯**：新增項目，不清空舊項目
- `open_questions` 中若某問題本次已解決，從列表移除
- 不更新 `project.yaml`，除非教師明確要求
- 若本次對話沒有任何可提取的變動，回應：「本次對話無可更新的狀態，english-session.yaml 維持不變。」
