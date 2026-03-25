---
name: art-in-teaching
description: "藝術作品融入教學素材管線。當教師說「藝術作品融入教學」「art in teaching」「博物館素材」「博物館 API」「Met API」「Europeana」「藝術作品」「找藝術品」「素材畫廊」「拉幾張畫」「做素材展示」「museum」「art search」「找博物館素材」「找幾張畫」「搜尋藝術品」「museum resource」「找畫作」「找藝術作品來備課」「藝術素材」時觸發。串接 Met Museum 與 Europeana API，搜集藝術作品 metadata，生成課堂投影用 HTML 畫廊，支援 AI 教學加工（中文化、討論問題、ABCD 差異化建議）、跨來源聚合與 Drive 歸檔。適用於所有教師的跨科目藝術素材蒐集。"
---

# 藝術作品融入教學素材管線

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 參數

- 格式：`<搜尋關鍵字> [--source met|europeana|both] [--count N] [--grade 7|8|9]`
- 搜尋關鍵字為必填（英文）

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/art-in-teaching.md`

## 注意事項

- 本入口不包含任何執行邏輯——所有流程均在正本中定義
- 若正本更新，本入口無需同步修改
