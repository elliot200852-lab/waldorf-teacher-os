---
name: lesson
description: Enter lesson design workflow for a specific class, subject, and block. Use when the user says '進入備課', '做 Block', '開始設計', or specifies a class and wants to design lessons. Requires class code and subject, optionally block number.
---

# 課堂教學設計

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 參數

- 格式：`<班級代碼> <科目> [區塊編號]`，例如 `9c english 2`、`9d ml-taiwan-literature`
- 若未指定區塊編號，從 session.yaml 的 current_position 推斷

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/lesson.md`

## 注意事項

- 本入口不包含任何執行邏輯——Block/Step 工作流均在正本中定義
- 若正本更新，本入口無需同步修改
