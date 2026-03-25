---
name: gws-setup
description: "Google Workspace CLI installation and setup. Triggers on '設定 gws', '安裝 gws', 'gws setup'. Handles cross-platform installation (macOS via Homebrew/npm, Windows via npm/winget), OAuth authentication, and client secret configuration."
---

# Google Workspace CLI 安裝與設定

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/gws-setup.md`

## 注意事項

- 本入口不包含任何執行邏輯——跨平台安裝流程、OAuth 設定均在正本中定義
- 若正本更新，本入口無需同步修改
- 支援 macOS 和 Windows，正本內含兩個平台的完整安裝路徑
