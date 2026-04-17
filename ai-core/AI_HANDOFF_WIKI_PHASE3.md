---
aliases:
  - "Wiki Phase 3 交接文件"
type: handoff
created: 2026-04-06
delete_after_read: true
---

# Wiki 拓撲化 Phase 3 交接

> **讀完本文件後，請刪除此檔案（`git rm ai-core/AI_HANDOFF_WIKI_PHASE3.md`）。**
> 這是一次性交接，不需要留在 repo 裡。

---

## Phase 1 已完成（commit a62cdb3）

- `ai-core/reference/wikilink-protocol.yaml` — 全 repo 連結規範
- `setup/scripts/link-published.py` — CreatorHub 外部連結回填腳本
- `setup/scripts/wiki-bootstrap.py` — 教案/學習單 wikilink 回填腳本
- 41 篇已部署故事回填 `published_url` + `## 連結`
- 35 個教案/學習單回填 `related:` wikilinks
- 多位教師 workspace 互連

## Phase 2 已完成（本次 session）

### 新增功能

1. **`obsidian-check.py --link-check` 模式**
   - 檔案：`setup/scripts/obsidian-check.py`
   - 掃描全 repo 的 .md 檔，依 `wikilink-protocol.yaml` 的 `placement` 規則判斷每個檔案是否缺少 `related:` 或 `## 連結`
   - 輸出 `LINK_ORPHAN` 類別，格式：`FILE:LINK_ORPHAN:path|type|missing:what`
   - 目前偵測到 167 個缺連結檔案（主要是 story 系列缺 `related:` frontmatter）

2. **`obsidian-sync.md` Step 1.5 — 連結完整性檢查**
   - 在 obsidian-sync 流程中新增連結檢查步驟
   - 執行 `--link-check`，向教師報告缺連結清單
   - 教師確認後 AI 自動補齊 `related:` 和 `## 連結`

3. **概念頁系統**
   - 目錄：`wiki/concepts/{texts,themes,grammar}/`
   - 建立門檻：跨 2 科/班出現即建立
   - 已建立 5 頁：
     - `wiki/concepts/texts/The-House-on-Mango-Street.md`（跨 English + walking-reading-taiwan）
     - `wiki/concepts/texts/Sandra-Cisneros.md`
     - `wiki/concepts/grammar/連接詞.md`
     - `wiki/concepts/grammar/動詞片語.md`
     - `wiki/concepts/grammar/關係代名詞.md`
   - 格式依 `wikilink-protocol.yaml` 的 `concept_pages` 區段

### 修正問題

- A001/A002/A003 frontmatter 重複 `aliases:` 已修復
- 141 個檔案的 `published_url` 去除引號（Obsidian 可直接點擊）
- `link-published.py` 修正為不加引號寫入

### 概念頁增長機制

概念頁不是一次建完的，靠兩個機制持續增長：

| 機制 | 觸發時機 | 做什麼 |
|------|----------|--------|
| lesson-engine Stage 4 | 每次產出教案 | 在 `related:` 自動加入已存在的概念頁 wikilinks |
| lesson-engine Stage 6 | 每次寫 wiki 日誌 | 偵測是否有新的跨科實體達門檻，建議建立新概念頁 |
| obsidian-sync Step 1.5 | 每次執行 sync | `--link-check` 掃描全 repo，發現跨 2 科/班的新實體時建議建立 |

概念頁放在 `wiki/concepts/`（`shared_writable`），所有註冊教師共用。

---

## Phase 3 待做

### 1. 批量補齊 167 個 LINK_ORPHAN 的 `related:` frontmatter

**現狀**：`--link-check` 已偵測到 167 個缺連結檔案
- story_component: 116 個（缺 related）
- story_content: 48 個（缺 related，部分缺 body）
- wiki_entry: 3 個（缺 related）

**做法**：
- 優先處理 wiki_entry（3 個，手動品質高）
- story_content 和 story_component 可批量處理：
  - content 的 `related:` 連到同目錄的 narration/images/chalkboard
  - component 的 `related:` 連回 content 主檔
  - 已有 `published_url` 的加入 CreatorHub 外部連結
- 建議寫一個 `link-orphan-fix.py` 腳本批量處理 story 類

### 2. lesson-engine 整合概念頁連結

**檔案**：`ai-core/skills/lesson-engine.md`
**做什麼**：Stage 4 產出教案時，掃描 `wiki/concepts/` 已有的概念頁，若教案內容涉及已有概念，自動在 `related:` 加入 wikilink

**實作**：
- 掃描 `wiki/concepts/**/*.md` 的 `aliases` frontmatter
- 建立 alias → 概念頁檔名的對照表
- 教案 body 中出現 alias 時，自動加入 `related: ["[[概念頁名]]"]`

### 3. wiki 日誌自動偵測新概念

**檔案**：`ai-core/skills/lesson-engine.md`（Stage 6）
**做什麼**：寫 wiki 日誌時，檢查本次教案涉及的實體（作者、文本、文法概念）是否已跨 2 科/班出現但尚無概念頁。若是，提醒教師並建議建立。

### 4. `wiki/concepts/themes/` — 跨科主題概念頁

Phase 2 已建立 texts/ 和 grammar/，但 themes/ 仍為空。候選：
- 「殖民與抵抗」— 若 walking-reading-taiwan + 9D 台灣文學都涉及
- 「identity」— 若 English + walking-reading-taiwan 都涉及
- 「土地與勞動」— 若 farm-internship + walking-reading-taiwan 都涉及

待 9D 台灣文學 Block 1 啟動後，跨科素材會自然累積。

### 5. wiki-bootstrap.py 二次掃描

Phase 1 有 40 個檔案被跳過（無 frontmatter metadata 無法推斷連結）。概念頁建立後，可重跑 `--apply` 把概念頁連結加進已有 `related:` 的檔案。

### 6. Obsidian Base View — wiki 概念頁篩選視圖

建立 `wiki/concepts/concepts.base`，讓教師在 Obsidian 中以表格視圖瀏覽所有概念頁，篩選欄位：type、tags、last_refreshed。

---

## 關鍵檔案快速參考

| 用途 | 路徑 |
|------|------|
| 連結規範 | `ai-core/reference/wikilink-protocol.yaml` |
| 外部連結腳本 | `setup/scripts/link-published.py` |
| 教案連結腳本 | `setup/scripts/wiki-bootstrap.py` |
| 偵測引擎 | `setup/scripts/obsidian-check.py`（含 `--link-check`）|
| Obsidian sync 技能 | `ai-core/skills/obsidian-sync.md`（含 Step 1.5）|
| Wiki 擴張路線圖 | `wiki/_wiki-handoff.md` |
| 概念頁目錄 | `wiki/concepts/{texts,themes,grammar}/` |
| 概念頁格式 | `wikilink-protocol.yaml` → `concept_pages` 區段 |
