---
name: wiki-reflect
description: Extract design thinking and reflections from lesson planning conversations into shared wiki knowledge base. Triggers on '備課反思', '設計反思', 'wiki reflect', '寫反思', '記錄設計思考', '反思一下'. Complements lesson-engine Phase 6 (design summary) with deeper design reasoning. Supports bidirectional linking with teaching-log.
---

# 備課設計反思

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/wiki-reflect.md`

## 注意事項

- 本入口不包含任何執行邏輯——反思擷取、wikilink 雙向連結、teaching-log 整合均在正本中定義
- 若正本更新，本入口無需同步修改
