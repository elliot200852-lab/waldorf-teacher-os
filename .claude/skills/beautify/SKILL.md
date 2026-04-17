---
name: beautify
description: "華德福美化文件輸出。將 Markdown 內容轉換為精美的華德福風格 HTML 文件，支援四季視覺切換（春/夏/秋/冬）。當教師說「美化」「做漂亮版」「HTML 輸出」「精美版」「beautify」「套模板」「漂亮版本」「美化輸出」「做精美的」「美化這份」「華德福風格輸出」「做好看一點」時觸發。"
---

# 華德福美化文件輸出

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 參數

- 格式：`[檔案路徑] [--season spring|summer|autumn|winter]`
- 檔案路徑可省略（預設使用當前工作線最新產出）
- 季節可省略（預設自動偵測當前月份）

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/beautify.md`

## 注意事項

- 本入口不包含任何執行邏輯——設計規範、四季系統、生成流程均在正本中定義
- 若正本更新，本入口無需同步修改
- 需要的參考檔案：`publish/templates/waldorf-base.html`（基礎模板）、`ai-core/reference/stitch-design-brief.md`（設計規範）
