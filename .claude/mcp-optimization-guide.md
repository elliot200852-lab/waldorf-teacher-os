# MCP 工具精簡策略

> 產生日期：2026-03-23
> 來源：ECC (Everything Claude Code) 最佳實踐 + TeacherOS 實際工具盤點

## 現況

目前載入約 107+ 個 MCP 工具。Claude Code 的 deferred loading 機制已緩解
最嚴重的 context 佔用問題（schema 按需載入），但工具名稱仍全數列在 system prompt。

ECC 建議：MCP 總數不超過 20-30 個，啟用不超過 10 個 / 80 個工具。

## 工作類型與實際需要的 MCP

| MCP Server | 備課 | 導師業務 | 臺灣的故事 | 系統工程 |
|------------|------|---------|-----------|---------|
| GWS (Drive/Gmail/Cal/Sheets/Docs) | 需要 | 需要 | 需要 (Drive) | 偶爾 |
| GCal (cloud) | 偶爾 | 需要 | 不需要 | 不需要 |
| Gmail (cloud) | 偶爾 | 需要 | 不需要 | 不需要 |
| Google Drive (cloud) | 需要 | 偶爾 | 需要 | 不需要 |
| Claude Preview | 不需要 | 不需要 | 不需要 | 偶爾 |
| Claude in Chrome | 不需要 | 不需要 | 需要 (Gemini) | 偶爾 |
| Control Chrome | 不需要 | 不需要 | 需要 (Gemini) | 偶爾 |
| Control Mac | 不需要 | 不需要 | 偶爾 | 偶爾 |
| PDF Tools | 偶爾 | 偶爾 | 不需要 | 不需要 |
| Apple Notes | 不需要 | 偶爾 | 不需要 | 不需要 |
| Telegram | 偶爾 | 偶爾 | 不需要 | 不需要 |
| scheduled-tasks | 不需要 | 不需要 | 需要 | 偶爾 |
| mcp-registry | 不需要 | 不需要 | 不需要 | 不需要 |
| claude-code | 始終需要 | 始終需要 | 始終需要 | 始終需要 |

## 建議操作

### 方案 A：手動停用（每次開工時）

在 Claude Code 中用 `/mcp` 查看並停用不需要的 MCP。
缺點：每次都要手動，David 可能忘記。

### 方案 B：工作模式別名（推薦）

建立 shell alias，用不同的 settings 啟動 Claude Code：

```bash
# 在 ~/.zshrc 或 ~/.bashrc 加入
alias claude-teach='cd ~/Desktop/WaldorfTeacherOS-Repo && claude'   # 預設（全載入）
alias claude-lite='cd ~/Desktop/WaldorfTeacherOS-Repo && claude --disabledMcpServers "Claude_Preview,PDF_Tools_-_Fill__Analyze__Extract__View,Read_and_Write_Apple_Notes,mcp-registry"'
```

注意：`--disabledMcpServers` 的可用性取決於 Claude Code 版本，需測試。

### 方案 C：接受現狀，觀察效能

deferred loading 已大幅緩解問題。如果目前未感受到明顯的 context 壓力或
回應品質下降，可暫不處理，優先投資在 PreCompact hook（已完成）和
subagent model 分級（項目 4）上。

## 可立即安全停用的 MCP

以下 MCP 在 David 的日常工作中幾乎不會用到，停用不影響任何技能：

1. **mcp-registry** — 搜尋/建議新 MCP 用，維運期不需要
2. **Claude Preview** — 開發者前端預覽工具，教學工作不需要
3. **Apple Notes** — 目前未在任何技能或工作流中使用

停用方式：`/mcp` → 找到對應 MCP → 停用
