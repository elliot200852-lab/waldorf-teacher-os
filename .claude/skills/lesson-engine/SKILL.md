---
name: lesson-engine
description: Design a complete Waldorf lesson for Grade 1-12 students. Supports 45-minute subject lessons, 90-minute double periods, and 120-minute Main Lessons. Use this skill whenever the user asks to design, plan, or create a lesson for any subject and any grade — including requests like '幫我設計一堂課', '45分鐘英文課', '八年級歷史課設計', 'lesson design', '連堂', '主課程設計', or any mention of a specific text, poem, theme, or topic and wants it turned into a lesson. Also trigger when the user provides a text or material and asks 'this can be used for a lesson' or '這可以怎麼上'. This skill covers ALL grades (1-12), ALL subjects, and ALL formats (45/90/120 min) with overlay support.
---

# 統一課程設計引擎｜路由入口

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. **統一引擎**：`ai-core/skills/lesson-engine.md`
2. **科目覆蓋層**：由引擎 Step 0 自動載入

## 注意事項

- 本入口不包含任何執行邏輯——所有設計原則、工作流、產出規格均在正本中定義
- 若正本更新，本入口無需同步修改
- 本引擎取代舊版 subject-lesson-45，支援 45/90/120 三種格式、1-12 年級全覆蓋
- 十條通用設計原則（含 GA 293/294 方法論）為鐵打層，所有課程設計必須通過稽核
