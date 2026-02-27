# /status — 快速查詢當前工作位置

比 /load 更輕量。只確認「現在在哪、下一步是什麼」，不載入完整脈絡。

## 使用方式

```
/status 9c
/status 8a
/status 7a
```

## 執行規則

`$ARGUMENTS` 是班級代碼（9c、8a 或 7a）。

若未提供 `$ARGUMENTS`，先詢問：「請問要查詢哪個班級？（9c / 8a / 7a）」，等待回應後再繼續。

## 讀取順序

只讀取以下兩個檔案（根目錄：`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`）：

1. `projects/class-$ARGUMENTS/working/english-session.yaml`
2. `projects/class-$ARGUMENTS/project.yaml`（只在 english-session 無位置資訊時補充）

## 輸出格式

5 行以內，不解釋，不補充背景。

---

**class-$ARGUMENTS 狀態**

位置：（`current_position.block` + `current_position.step`，若有 `sub_block` 或 `unit_number` 一併顯示）
下一步：（`next_action.description`）
待確認：（`next_action.input_needed_from_teacher`，若為 null 顯示「無」）
待決問題：（`open_questions` 條數，若有則列出；若為空顯示「無」）

---

## 注意事項

- 若 `current_position` 所有欄位均為 `null`，顯示「尚未開始，建議使用 /load $ARGUMENTS 初始化」
- 不輸出 YAML 原文，不補充任何解釋
- 輸出結束後直接等待指令，不詢問「需要我做什麼嗎？」
