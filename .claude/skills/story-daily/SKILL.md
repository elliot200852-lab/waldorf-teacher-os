---
name: story-daily
description: "臺灣的故事每日全流程管線。一鍵觸發從選題、素材搜尋、撰寫三件套、品質檢查、組裝HTML/PDF到上傳Google Drive的完整7步驟自動化管線。觸發語：'臺灣的故事'、'每日臺灣的故事'、'寫一篇臺灣的故事'、'Daily Story of Taiwan'、'daily story'、'stories of taiwan'。適用於所有提到臺灣故事管線、每日故事產製、故事自動化流程的情境。"
---

# 臺灣的故事・每日全流程管線

> 本 SKILL.md 是 Cowork Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/story-daily.md`

## 子技能依賴（由 story-daily 依序呼叫）

| 順序 | 子技能 | 正本路徑 |
|------|--------|---------|
| 1 | story-planner | `ai-core/skills/story-planner.md` |
| 2 | story-research | `ai-core/skills/story-research.md` |
| 3 | story-writer | `ai-core/skills/story-writer.md` |
| 4 | story-verify | `ai-core/skills/story-verify.md` |
| 5 | assemble-story.js | `publish/scripts/assemble-story.js` |
| 6 | story-archive | `ai-core/skills/story-archive.md` |

## 注意事項

- 本入口不包含任何執行邏輯——所有流程均在正本中定義
- 若正本更新，本入口無需同步修改
- GWS CLI 橋接方式依平台而異，詳見 `ai-core/skills/gws-bridge.md`
