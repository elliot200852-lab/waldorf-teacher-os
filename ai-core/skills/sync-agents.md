---
name: sync-agents
description: 執行 TeacherOS 多 AI agent 系統一致性檢查。掃描所有 skills、Claude commands、reference 模組、AI_HANDOFF.md 引用，輸出完整性報告。
triggers:
  - 同步檢查
  - 檢查系統
  - sync agents
  - 系統一致性
  - check system
requires_args: false
args_format: "[選填：--auto-fix 自動修正]"
---

# skill: sync-agents — 多 Agent 系統同步檢查

檢查 TeacherOS 系統的完整性與一致性，確保所有 AI agent 共用的設定保持同步。

## 執行步驟

1. 執行 `python3 ai-core/sync_check.py`
2. 閱讀報告輸出，逐項向教師說明結果
3. 若有 FAIL 或 WARN 項目，詢問教師是否執行自動修正
4. 若教師同意，執行 `python3 ai-core/sync_check.py --auto-fix`
5. 修正後再執行一次檢查確認

## 檢查項目

| 檢查 | 說明 |
|------|------|
| 核心檔案 | teacheros.yaml, acl.yaml, AI_HANDOFF.md 等是否存在 |
| Skill Frontmatter | 每個 skill 是否有 name / triggers / description |
| Claude 路由同步 | .claude/commands/ 是否與 ai-core/skills/ 一致 |
| Reference 模組 | ai-core/reference/ 檔案是否齊全 |
| Handoff 引用 | AI_HANDOFF.md 引用的路徑是否有效 |
| Manifest 一致性 | skills-manifest.md 與實際檔案是否一致 |

## Auto-Fix 能力

- 自動補齊遺漏的 Claude commands（建立 thin routing stub）
- 寫入修正記錄至 `ai-core/sync-changelog.md`
