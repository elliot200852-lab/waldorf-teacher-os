---
name: load
description: Load a specific class and subject workspace for TeacherOS. Use when the user says '載入', '讀一下' followed by a class code and subject, e.g. '載入 9C english', 'load 9c homeroom'. Loads the class project.yaml and subject session.yaml into context.
---

# 載入班級與科目脈絡

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 參數

- 格式：`<班級代碼> <科目>`，例如 `9c english`、`9d ml-taiwan-literature`
- 班級代碼對應 `{workspace}/projects/class-{code}/`
- 科目對應該班級下的子資料夾

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/load.md`

## 注意事項

- 本入口不包含任何執行邏輯——載入序列、YAML 讀取規則均在正本中定義
- 若正本更新，本入口無需同步修改
- 若已透過 `opening` 技能完成必讀檔案載入，`load` 只需處理班級特定的部分
