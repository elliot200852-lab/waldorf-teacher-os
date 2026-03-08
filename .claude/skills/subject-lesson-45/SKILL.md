---
name: subject-lesson-45
description: Design a complete 45-minute Waldorf subject lesson for Grade 7-9 students. Use this skill whenever David asks to design, plan, or create a lesson for any subject (English, History, etc.) for seventh, eighth, or ninth graders — including requests like '幫我設計一堂課', '45分鐘英文課', '八年級歷史課設計', 'G9 English lesson', 'lesson design', or any mention of a specific text, poem, theme, or topic and wants it turned into a lesson. Also trigger when David provides a text or material and asks 'this can be used for a lesson' or '這可以怎麼上'. This skill replaces g9-english-45 and covers ALL grades (7-9) and ALL subjects with overlay support.
---

# 45 分鐘課堂設計｜統一路由入口

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. **通用引擎**：`ai-core/skills/subject-lesson-45.md`
2. **科目覆蓋層**：由引擎 Step 0 自動載入（路徑模式：`ai-core/skills/[科目]-45.md`）

## 注意事項

- 本入口不包含任何執行邏輯——所有設計原則、工作流、產出規格均在正本中定義
- 若正本更新，本入口無需同步修改
- 已取代舊版 `g9-english-45`（該技能僅覆蓋九年級英文，本版覆蓋七至九年級全科目）
