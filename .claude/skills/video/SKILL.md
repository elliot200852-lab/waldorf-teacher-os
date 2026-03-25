---
name: video
description: Remotion video production workflow. Triggers on '做影片', '製作影片', '影片', 'video', '渲染影片', 'render video', or any request to create, edit, or render a video. Handles asset preparation, composition coding, Studio preview, teacher review loop, and final render.
---

# Remotion 影片製作

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/video.md`

## 注意事項

- 本入口不包含任何執行邏輯——素材準備、程式碼撰寫、Studio 預覽、渲染流程均在正本中定義
- 若正本更新，本入口無需同步修改
- 環境建置請使用 `video-setup` 技能
