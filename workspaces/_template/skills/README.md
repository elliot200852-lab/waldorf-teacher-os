# 教師個人技能（Personal Skills）

此資料夾存放教師自建的個人化工作技能。

## 格式規範

每個技能為一個獨立 `.md` 檔案，頂部必須包含 YAML frontmatter：

```yaml
---
name: 技能名稱（英文，小寫，用連字號分隔）
description: 一句話描述技能用途（AI 用此欄位判斷是否觸發）
triggers:
  - 觸發語一
  - 觸發語二
requires_args: true/false
args_format: "[參數格式說明]"（若 requires_args 為 true）
author: 建立者姓名
created: 建立日期
---
```

frontmatter 之後為完整的執行指令（Markdown 格式）。

## 與系統技能的關係

- **系統技能**（`ai-core/skills/`）：所有教師共用，由管理員維護
- **個人技能**（此資料夾）：教師自建，僅在自己的 workspace 生效

## AI 掃描規則

AI 在載入教師 workspace 後，應掃描此資料夾內所有 `.md` 檔的 frontmatter。
當教師的口語指令符合任一技能的 `triggers` 或 `description`，載入該技能全文並執行。
個人技能與系統技能名稱衝突時，**系統技能優先**。
