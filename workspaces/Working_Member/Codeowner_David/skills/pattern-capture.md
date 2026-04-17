---
aliases:
  - "教學 Pattern 提煉"
name: pattern-capture
type: personal-skill
description: >
  從備課對話中提煉可重用的教學 pattern，存為個人技能檔案。
  Pattern 會被 opening 技能自動掃描，未來設計類似課程時自動注入為設計參考。
triggers:
  - 存 pattern
  - 提煉 pattern
  - extract pattern
  - save pattern
  - 這個做法存起來當 pattern
  - 看 pattern
  - 列 pattern
  - list patterns
requires_args: false
author: David
created: 2026-03-23
---

# Pattern Capture — 教學 Pattern 提煉

從備課對話中提煉可重用的教學洞察，存成 pattern 檔案。
Opening 技能會自動掃描 pattern 的 triggers，未來設計課程時主動提及。

## 兩種模式

### 模式 A：提煉 pattern

觸發：「存 pattern」「提煉 pattern」「這個做法存起來當 pattern」

**執行步驟：**

1. **辨識**：從對話脈絡（最近 5 輪）中辨識教學洞察
   - 什麼做法有效？什麼做法失敗？為什麼？
   - 這個洞察是否可泛化到其他課程？（只對這次有效的不算 pattern）

2. **摘要確認**：向教師簡述，一句話確認
   > Pattern：{標題}——{一句話描述}
   > 觸發詞：{列表}
   > 要存嗎？

3. **寫入**：教師確認後，建立 `{workspace}/skills/pattern-{name}.md`

### 模式 B：列出已有 pattern

觸發：「看 pattern」「列 pattern」「list patterns」

**執行步驟：**

1. 掃描 `{workspace}/skills/pattern-*.md`
2. 讀取每個檔案的 frontmatter
3. 輸出列表：

| # | Pattern | 觸發詞 | 來源 | 日期 |
|---|---------|--------|------|------|
| 1 | {name} | {triggers} | {class/subject} | {date} |

---

## Pattern 檔案格式

```markdown
---
aliases:
  - "{中文別名}"
name: pattern-{kebab-case-name}
type: teaching-pattern
description: >
  {一句話描述核心洞察}
triggers:
  - {觸發詞1}
  - {觸發詞2}
source:
  class: {來源班級}
  subject: {來源科目}
  date: {發現日期}
---

# Pattern: {中文標題}

## 洞察

{2-3 句話：這個 pattern 是什麼、為什麼有效}

## 來源情境

{什麼情況下發現的：班級、主題、學生反應}

## 適用場景

{什麼時候該套用}

## 操作要點

- {具體做法 1}
- {具體做法 2}
- {具體做法 3}
```

## 重用機制

Pattern 檔案存在 `{workspace}/skills/` 中，opening Step 3 會自動掃描 frontmatter。
AI 在課程設計時比對到觸發詞，會讀取 pattern 全文並作為設計參考（非硬性規則）。

AI 應主動告知教師：「根據你之前的 pattern [{name}]，建議 {做法}。要套用嗎？」

## 注意事項

- Pattern 是知識，不是執行步驟。被觸發時注入為設計約束，不產出成品。
- 只存可泛化的洞察。「這堂課用了某首詩」不是 pattern；「連接詞教學需攤開多節」才是。
- Pattern 可以隨時修改或刪除。教學是動態的，pattern 也會進化。
