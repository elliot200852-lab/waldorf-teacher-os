---
name: status
description: 輕量查詢班級目前的工作位置與下一步，不載入完整脈絡。5行內回應。
triggers:
  - 現在在哪
  - 做到哪了
  - 快速查詢
  - 進度如何
requires_args: true
args_format: "[班級代碼] (9c/8a/7a)"
---

# skill: status — 快速查詢當前工作位置

比 load 更輕量。只確認「現在在哪、下一步是什麼」，不載入完整脈絡。

## 參數

班級代碼（9c / 8a / 7a）。未提供則詢問：「請問要查詢哪個班級？（9c / 8a / 7a）」

## 根目錄

`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`

## 讀取順序

只讀取以下兩個檔案：

1. `{workspace}/projects/class-[班級]/working/english-session.yaml`
2. `{workspace}/projects/class-[班級]/project.yaml`（只在 english-session 無位置資訊時補充）

# {workspace} 路徑解析：
# 從 acl.yaml 取得當前使用者的 workspace 路徑。
# David：workspaces/Working_Member/Codeowner_David/
# 教師：workspaces/Working_Member/Teacher_{姓名}/

## 輸出格式

5 行以內，不解釋，不補充背景。

---

**class-[班級] 狀態**

位置：（`current_position.block` + `current_position.step`，若有 `sub_block` 或 `unit_number` 一併顯示）
下一步：（`next_action.description`）
待確認：（`next_action.input_needed_from_teacher`，若為 null 顯示「無」）
待決問題：（`open_questions` 條數，若有則列出；若為空顯示「無」）

---

## 注意事項

- 若 `current_position` 所有欄位均為 `null`，顯示「尚未開始，建議使用 load 技能初始化」
- 不輸出 YAML 原文，不補充任何解釋
- 輸出結束後直接等待指令，不詢問「需要我做什麼嗎？」
