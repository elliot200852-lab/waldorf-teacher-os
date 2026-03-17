---
name: send-email
description: "Send email via Gmail using gws CLI. Triggers on '寄信', '寄 Email', '發郵件', '寄給', or any request to send email. Handles Chinese subject encoding via Python MIME, supports multiple Google accounts. Cross-platform: works on macOS and Windows."
---

# Gmail 寄送

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 參數

- 格式：`<收件人> [主旨]`，例如 `someone@example.com 會議通知`
- 收件人為必要參數，主旨可在執行中補充

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/send-email.md`

## 注意事項

- 本入口不包含任何執行邏輯——MIME 編碼、帳號切換、gws 指令均在正本中定義
- 若正本更新，本入口無需同步修改
- 中文主旨必須使用 Python MIME 編碼方式，不可直接用 gws --subject
