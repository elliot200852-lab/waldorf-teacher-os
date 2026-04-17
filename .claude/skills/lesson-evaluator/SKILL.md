---
name: lesson-evaluator
description: Evaluate the quality of a completed Waldorf lesson plan using 7 dimensions — lesson type identification, rhythm analysis, DI fit check, teacher workload, application context, cross-lesson patterns, and holistic impression. Produces a structured report with PASS/REVISE/REDO verdict. Use this skill whenever the user asks to evaluate, review, or quality-check a lesson — including requests like '評估課程', '跑品質檢查', '評估教案', 'evaluate', 'lesson evaluate', or '這堂課設計得如何'. Works as the Evaluator half of the Generator-Evaluator pair with lesson-engine.
---

# 課程設計品質評估｜路由入口

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/lesson-evaluator.md`

## 與 lesson-engine 的關係

lesson-engine（生成器）和 lesson-evaluator（評估器）形成 Generator-Evaluator 配對：

- **lesson-engine**：設計課程，內建 Stage 3 稽核員做 10 原則檢查
- **lesson-evaluator**：補充 Stage 3 未覆蓋的維度——課型適配、節奏量化、教師操作負荷、應用語境、跨課堂模式

建議使用方式：備課完 commit，下次新 session 再跑 evaluator（Context Isolation 標準模式）。

## 注意事項

- 本入口不包含任何執行邏輯——所有評估維度、判定標準、校準紀錄均在正本中定義
- 若正本更新，本入口無需同步修改
- 已通過 5 堂教師校準（v2），涵蓋教學課、測驗課、概念引入課、閱讀課、教學參考模式
- 接受兩種教案格式：標準教案（content/）和教學參考模式（content/）
