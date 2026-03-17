---
name: wrap-up
description: End-of-session progress sync, Obsidian tag fix, and git commit+push. Triggers on '收工', '收尾', '存檔', '儲存', '更新進度', '結束今天', 'commit', '備份', or any expression meaning 'save and finish'. Updates YAML progress markers, fixes Obsidian tags, commits and pushes changes.
---

# 收工（進度同步 + 存檔推送）

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/wrap-up.md`

## 注意事項

- 本入口不包含任何執行邏輯——YAML 更新、Obsidian 修正、git 操作均在正本中定義
- 若正本更新，本入口無需同步修改
- wrap-up 是多 AI Agent 系統中唯一的工作銜接機制
