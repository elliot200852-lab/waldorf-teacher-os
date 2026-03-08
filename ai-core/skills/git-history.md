---
name: git-history
description: 管理 WaldorfTeacherOS Git History 週記。追加本次工作成果為週記條目，或從 git log 補寫缺漏段落。
triggers:
  - 填進去 Git history
  - Git history 編寫
  - 更新週記
  - 補寫 git history
  - git 回顧
  - 專案紀錄
  - commit 摘要
requires_args: false
args_format: "[選填：模式說明，如「把這次的工作填進去」或「補寫到最新」]"
---

# skill: git-history — Git History 週記管理

管理 WaldorfTeacherOS 專案的系統架構回顧週記（`Git History/git-history.md`）。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 操作模式

本技能有兩種模式，根據教師觸發語自動判斷：

| 教師說 | 模式 |
|--------|------|
| 「填進去 Git history」「把這個填進去」 | 模式一：追加當前工作 |
| 「Git history 編寫」「補寫 git history」「git 回顧」 | 模式二：從 git log 補寫 |

---

## 模式一：追加當前工作

教師完成一段工作後觸發，將本次對話中的成果整理為週記條目。

### 執行步驟

1. **回顧當前對話**：提取本次工作 session 中完成的主要事項——建了什麼、改了什麼、為什麼這樣做
2. **讀取現有週記**：讀取 `Git History/git-history.md`，確認目前寫到哪一週、最後的段落結構
3. **判斷歸屬週次**：根據今天日期，確定這段內容屬於哪一週的回顧
4. **撰寫條目**：用系統架構師視角，以 2-4 段繁體中文散文撰寫新內容，風格與現有段落一致
5. **插入文件**：
   - 若該週段落已存在 → 將新內容合併到該週「核心建設」區塊的適當位置
   - 若該週段落尚不存在 → 建立完整的新週段落（標題、副標、起心動念、核心建設、貢獻與意義、檢討）
6. **輸出 PDF**（選用）：若教師要求，依 PDF 輸出規格產出

---

## 模式二：從 git log 補寫

教師一段時間未更新週記後觸發，從 git log 補寫所有缺漏段落。

### 執行步驟

1. **讀取現有週記**：確認目前已記錄到哪一週的哪個日期
2. **取得未記錄的 commit**：
   ```bash
   cd [repo根目錄] && git log --all --format="%h|%ai|%s" --reverse --since="<上次記錄的最後日期>"
   ```
3. **按週分組**：將 commit 按日曆週分組
4. **逐週撰寫**：為每個缺漏的週次撰寫完整回顧段落
5. **更新文件**：將所有新段落按時間順序插入 `Git History/git-history.md`
6. **輸出 PDF**（選用）：若教師要求，依 PDF 輸出規格產出

---

## 寫作風格

- 不逐條列 commit，歸納為有意義的敘事
- 語調：冷靜、客觀、帶溫度
- 重要概念用 **粗體**
- 技術名詞保留英文（如 YAML、CLI、ACL）
- 解釋「為什麼」比「做了什麼」更重要
- 所有輸出使用繁體中文

## 週記段落格式

```markdown
## 第 N 週｜YYYY/MM/DD（X）– MM/DD（X）

### 一句話描述本週核心轉變

開場段落：本週的整體脈絡與驅動力。

**起心動念：** 為什麼做這些事。

**核心建設：**

按時間順序，以散文敘述本週重要變動。每個重要主題一個段落。

**貢獻與意義：** 這週的工作對整體系統的意義。

**檢討：** 冷靜的事後反思，指出可以做得更好的地方。
```

## PDF 輸出規格

**必讀**：輸出 PDF 前，先讀取 `Git History/_pdf-config.md` 取得完整的工具設定與規格。

核心要點：
- 引擎：Python reportlab（Platypus）
- 字型：Helvetica（拉丁）+ DroidSansFallbackFull（CJK）
- CJK 字元以 `is_cjk()` 偵測後用 `<font name="CJK">` 包裹
- 命名：`git-history_YYYY-MM-DD_v{N}.pdf`
- **不要用 weasyprint、pandoc、或其他工具**

## 讀取的檔案

| 檔案 | 用途 |
|------|------|
| `Git History/git-history.md` | 週記正本（讀取 + 寫入） |
| `Git History/_pdf-config.md` | PDF 產出設定（產 PDF 時必讀） |

## 注意事項

- 週記是敘事文件，不是 changelog；保持架構師反思的語氣
- 插入新內容時保持現有段落不變，只新增或合併
- 若對話中未完成具體工作（例如純討論），告知教師「本次沒有可記錄的建設成果」
- PDF 產出非預設動作——教師明確要求時才執行
