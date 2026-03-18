---
name: poetry-research
description: "英文備課素材研究工具。當教師說「詩歌研究」「poetry research」「找詩」「研究素材」「主題研究」「topic research」「備課研究」「find poems」「幫我找 [主題] 的詩」「research [topic]」「查 [topic] 的素材」時觸發。輸入英文主題，自動串接 PoetryDB、Datamuse、Free Dictionary、Gutendex、Open Library 五個 API，產出詩歌、詞彙卡、語意場、練習單與書單。適用於 David 及英文科教師的課堂素材蒐集。"
---

# 英文備課素材研究

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 參數

- 格式：`<topic> [--grade 7|8|9] [--subject english]`
- topic 為必填的英文主題詞

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/poetry-research.md`

## 注意事項

- 本入口不包含任何執行邏輯——所有流程均在正本中定義
- 若正本更新，本入口無需同步修改
