---
name: raw-ingest
description: 外部文件消化管線。將 wiki/raw/ 目錄中的文件（PDF、Word、TXT、MD）讀取後，自動生成 wiki 來源摘要頁與概念頁，並建立 wikilink 連結至既有知識圖。教師說「整合新文件」「消化 raw」「raw-ingest」觸發。
triggers:
  - 整合新文件
  - 消化 raw
  - 消化文件
  - raw-ingest
  - 整理素材
  - 把文件放進 wiki
  - 消化這份文件
  - 整理新資料
requires_args: false
args_format: "[選填：指定檔案路徑或檔名]"
---

# skill: raw-ingest — 外部文件消化管線

將教師放入 `wiki/raw/` 的外部文件（書籍章節、研究論文、學校文件、參考資料）讀取後，自動生成 wiki 頁面並整合進知識圖。

---

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄：嘗試 `git rev-parse --show-toplevel`，或從已知工作目錄推斷。

---

## 目錄結構

```
wiki/
  raw/                    ← 教師放入待消化文件的入口目錄
    .ingest-log.yaml      ← 已消化記錄（AI 自動維護）
    [任意檔案名]          ← 待消化的原始文件
  sources/                ← 消化後的來源摘要頁（由本技能產出）
    [文件摘要].md
  concepts/               ← 既有概念頁目錄（本技能可新增或更新）
    texts/
    grammar/
    themes/               ← 本技能主要貢獻的跨科主題概念頁
    [其他分類]/
```

---

## 執行步驟

### Step 0 — 確認入口目錄存在

```python
# 跨平台：偵測 wiki/raw/ 是否存在
import os
raw_dir = os.path.join(repo_root, "wiki", "raw")
if not os.path.exists(raw_dir):
    # 提示教師：wiki/raw/ 尚未建立，幫我建好之後把文件放進去就好
```

若 `wiki/raw/` 不存在：
- 回報：「wiki/raw/ 目錄不存在。我幫你建立，建立後把你想消化的文件放進去，再說『整合新文件』。」
- 建立目錄 + `.ingest-log.yaml`（初始空白），然後停止，等教師放入文件。

---

### Step 1 — 掃描待消化文件

讀取 `wiki/raw/.ingest-log.yaml`，取得已消化清單。

掃描 `wiki/raw/` 中的所有非隱藏檔案，與已消化清單比對，找出**新文件**。

支援格式：`.pdf` `.docx` `.doc` `.txt` `.md` `.xlsx` `.xls`

若教師指定了特定檔案（args），只處理該檔案。
若無指定，批次處理所有新文件（一次最多 5 份，避免 context 超載）。

**若無新文件：**
> 「wiki/raw/ 中沒有新文件。把你想消化的文件放進去，再說『整合新文件』。」

---

### Step 2 — 讀取文件內容

依副檔名選擇讀取方法：

| 格式 | 讀取方式 |
|------|----------|
| `.md` `.txt` | 直接用 Read 工具讀取 |
| `.pdf` | 使用 MCP PDF 工具（`read_pdf_content`）；若不可用，嘗試 `python3 -m pdfminer.high_level` |
| `.docx` `.doc` | 觸發 `anthropic-skills:docx`，指示其「讀取並回傳純文字內容」 |
| `.xlsx` `.xls` | 觸發 `anthropic-skills:xlsx`，指示其「讀取並回傳主要內容摘要」 |

讀取失敗時：
- 記錄失敗原因，跳過該文件
- 繼續處理下一份
- 最後回報失敗清單，請教師手動確認格式

**長文件（超過 50 頁或 20,000 字）：**
詢問教師：「這份文件很長，要全部消化，還是指定頁數範圍？」

---

### Step 3 — AI 分析與知識萃取

對每份文件的內容執行以下分析：

**3-1. 識別文件性質**

判斷文件屬於哪種類型：
- `book-chapter`：書籍章節（施泰納著作、教育論著、學術書）
- `research-paper`：研究論文或學術報告
- `school-document`：學校文件（行事曆、會議記錄、政策文件）
- `reference-material`：教學參考資料（地方文史、文化素材）
- `raw-notes`：個人筆記或未成形材料

**3-2. 萃取關鍵資訊**

針對不同文件類型，萃取：

| 文件類型 | 萃取重點 |
|----------|----------|
| book-chapter | 核心論點、關鍵概念詞彙、引文、與既有課程的連結 |
| research-paper | 研究問題、主要發現、方法、與教學實踐的相關性 |
| school-document | 重要日程、決策、待辦事項、影響教學的事項 |
| reference-material | 地點、人物、事件、素材適用的年級與科目 |
| raw-notes | 教師意圖、關鍵詞、未完成思路 |

**3-3. 連結至既有知識圖**

掃描現有 `wiki/` 目錄，找出文件中提到的：
- 既有概念頁（grammar、texts、themes）
- 既有課程 wiki 頁（lesson-wiki）
- 人物或文本（authors、works）

建立雙向連結清單。

**3-4. 識別新概念**

判斷是否需要建立新概念頁：
- 文件中反覆出現但 wiki 中尚無對應頁的重要概念 → 建立新概念頁
- 跨科/跨班級會重複使用的資源 → 進入 `wiki/concepts/themes/` 或對應分類

---

### Step 4 — 產出預覽（讓教師確認再寫入）

輸出以下預覽（不寫入檔案）：

```
【raw-ingest 預覽 — 待消化：[檔案名]】

將產出以下頁面：

1. wiki/sources/[slug].md — 來源摘要頁
   標題：[自動擬定]
   摘要：[3-5 行]
   新增概念頁連結：[清單]
   連結至既有頁面：[清單]

2. wiki/concepts/[分類]/[概念名].md（若有新概念）
   [概念一]：[一行描述]
   [概念二]：[一行描述]

確認後我將寫入。說「寫入」繼續，說「調整一下 [事項]」我會修改再確認。
```

---

### Step 5 — 寫入 wiki 頁面

教師確認後，寫入以下頁面：

**來源摘要頁格式**（`wiki/sources/[slug].md`）：

```markdown
---
aliases:
  - "[文件標題]"
  - "[作者或出版單位]"
type: source-raw
source_type: [book-chapter | research-paper | school-document | reference-material | raw-notes]
original_file: "wiki/raw/[原始檔名]"
ingested_date: [YYYY-MM-DD]
author: "[作者，若無填 unknown]"
subject_relevance:
  - [相關科目1]
  - [相關科目2]
grade_relevance:
  - [年級，若不限填 all]
tags:
  - source-raw
  - [source_type]
  - [其他相關標籤]
related:
  - "[[既有概念頁1]]"
  - "[[既有概念頁2]]"
---

# [文件標題]

## 摘要

[3-5 行。說明這份文件是什麼、核心主張、對教學的價值。]

## 關鍵觀點

[3-7 條列，每條一行。來自文件本身，非 AI 發明。]

## 對教學的啟發

[2-4 條列。具體說明如何連結到現有課程或備課場景。]

## 關鍵引文

> [直接引用，附頁碼或段落位置（若可取得）]

## 連結至既有知識

- [[既有概念頁1]] — [一句話說明連結原因]
- [[既有概念頁2]] — [一句話說明連結原因]
- [[相關課堂]] — [一句話說明連結原因]

## 新增概念頁

- [[新概念1]] — [一句話描述]
- [[新概念2]] — [一句話描述]
```

**新概念頁格式**（沿用既有 `wiki/concepts/` 格式）：

```markdown
---
aliases:
  - "[概念名稱]"
type: concept-[分類]
auto_generated: true
source: "[[來源摘要頁]]"
last_refreshed: [YYYY-MM-DD]
tags:
  - concept
  - concept-[分類]
  - [相關科目或主題]
related:
  - "[[來源摘要頁]]"
  - "[[相關概念]]"
---

# [概念名稱]

[2-4 行。說明概念定義，與教學的關聯。]

## 出現在哪些來源

- [[來源摘要頁]] — [一句話說明]

## 相關概念

- [[相關概念1]]

## 連結

- [[來源摘要頁]]
```

---

### Step 6 — 更新 ingest-log

寫入 `wiki/raw/.ingest-log.yaml`，追加已消化記錄：

```yaml
ingested:
  - file: "[原始檔名]"
    date: "[YYYY-MM-DD]"
    source_page: "wiki/sources/[slug].md"
    concept_pages:
      - "wiki/concepts/[分類]/[概念].md"
    status: done  # done | failed | partial
    notes: ""
```

---

### Step 7 — 回報結果

```
【raw-ingest 完成】

已消化：[N] 份文件
新增頁面：
  - wiki/sources/[slug].md
  - wiki/concepts/[分類]/[概念].md（若有）

Obsidian 中開啟 wiki/ 即可在 Graph View 看到新節點。
下次說「整合新文件」時，只有 wiki/raw/ 中的新檔案會被處理。
```

---

## 注意事項

- **不覆蓋既有概念頁**：若概念頁已存在，只在現有頁面的「出現在哪些來源」段落追加新連結，不重寫整頁
- **不消化已消化的檔案**：`.ingest-log.yaml` 是唯一依據，不靠時間戳或大小判斷
- **跨平台相容**：路徑處理使用 Python `os.path.join()`，不硬寫 `/` 或 `\\`
- **批次上限**：單次消化最多 5 份，避免 context 超載。超過時提示：「發現 [N] 份新文件，本次先消化前 5 份，完成後再說一次『整合新文件』繼續。」
- **語言**：所有 wiki 頁面內容使用繁體中文，英文術語保留原文

---

## 技術參考

| 項目 | 位置 |
|------|------|
| 既有 wiki 格式範本 | `wiki/concepts/texts/Sandra-Cisneros.md`、`wiki/9c-english-w7-3.md` |
| wiki 路線圖 | `wiki/_wiki-handoff.md` |
| PDF 工具 | MCP `pdf_tools` → `read_pdf_content` |
| DOCX 工具 | `anthropic-skills:docx` |
| wiki 權限設定 | `ai-core/acl.yaml` → `shared_writable` |

---

*建立日期：2026-04-06*
*版本：v1.0.0*
