---
name: opening
description: TeacherOS new conversation startup sequence. Triggers on any greeting or start-work expression — '開工', '開始', '早安', '我來了', '準備好了', 'start', "let's go", '上工', or any expression meaning 'ready to work'. Ensures repo is up-to-date (git pull), loads all required YAML files, scans personal skills, and reports system status.
---

# 新對話開場

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/opening.md`

## 注意事項

- 本入口不包含任何執行邏輯——git pull、系統載入、狀態報告均在正本中定義
- 若正本更新，本入口無需同步修改
- Opening 是所有工作的第一步，完成後可自然銜接 `load` 技能
