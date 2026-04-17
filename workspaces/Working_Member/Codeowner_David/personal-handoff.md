---
aliases:
  - "David 個人技能索引"
---

# David — Personal Handoff

> 此文件是 David 的個人技能索引，由 `opening.md` 在載入 workspace 時自動讀取。
> 系統技能觸發表見 `ai-core/AI_HANDOFF.md`；此文件僅列出 David 個人技能。

---

## 個人技能觸發對照表

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「寫文章」「寫貼文」「FB 文」「部落格」「演講稿」「品牌文」 | `david-voice` | `{workspace}/skills/david-voice.md` |
| 「pua」「進入除錯模式」「不要放棄」「換路徑查到底」「再試一次」 | `pua-debugging` | `{workspace}/skills/pua-debugging.md` |
| 「片語測驗」「片語考試」「phrase quiz」「動詞片語測驗」 | `phrase-quiz` | `{workspace}/skills/phrase-quiz.md` |
| 「上傳展示」「素材展示」「showcase」「放到展示頁」「deploy showcase」 | `showcase-deploy` | `{workspace}/skills/showcase-deploy.md` |

---

## 衝突處理

若個人技能與系統技能同名，在 David 的 session 中使用個人版本。
詳見 `ai-core/AI_HANDOFF.md`「教師個人技能」段落。

---

## 已完成：Repo 架構地圖工程化

**狀態：** 全 6 Phase 已完成（2026-03-26）

### 完成的產出

| 檔案 | 說明 |
|------|------|
| `ai-core/reference/repo-structure-map.yaml` | 架構地圖（74 條路由、81 個區段、231 個目錄） |
| `setup/scripts/map-generate-initial.py` | 初始生成腳本（從 HOME.md wikilink 反推） |
| `setup/scripts/map-validate.py` | 驗證與維護工具（--validate / --suggest / --rebuild-dirs） |
| `setup/scripts/obsidian-check.py` | 升級：讀取地圖，輸出 `FILE:NOT_IN_HOME:path|section` |
| `ai-core/skills/obsidian-sync.md` | 精簡：移除 33 行嵌入表格，改讀腳本建議 |
| `setup/scripts/pre-commit-check.py` | 新增地圖一致性警告（HOME.md 標頭異動/新目錄） |

### 日常維護指令

```bash
# 驗證地圖完整性
python3 setup/scripts/map-validate.py --validate

# 新增目錄後重建
python3 setup/scripts/map-validate.py --rebuild-dirs

# 查某個檔案該歸哪個區段
python3 setup/scripts/map-validate.py --suggest "path/to/file.md"
```

---

## 教學檔案查詢協議（MyPages Wiki）

> David 個人的十年教學實踐檔案（346 篇原始文件 + 41 篇知識頁），
> 不適用於其他教師。AI 在備課時自動查閱，不需教師指示。

**檔案根目錄：** `bases/my-pages-wiki/`

### 備課時的查閱規則

進入備課或課程設計時，AI 必須：
1. 先讀對應科目的 **overview** — 掌握 David 過去怎麼教這個科目
2. 主題相近時，進 **raw/** 搜尋具體教案或素材
3. **有既有版本** → 基於舊版迭代，不從零開始
4. **沒有既有版本** → 從零設計，但參考 concept 頁的教學哲學

### 科目對照索引

| 科目 | Overview | Concept 頁 | Entity 頁 | Raw 搜尋路徑 |
|------|----------|-----------|-----------|-------------|
| 英文 | `wiki/_overview-英文教學.md` | `concept-華德福外語教學`、`concept-雙軌並行教學策略`、`concept-自由的哲學與英語教學` | `the-house-on-mango-street`（G9）、`round-table-arthurian-legends`（G7） | `raw/英文教學/` |
| 歷史 | `wiki/_overview-歷史教學.md` | `concept-華德福歷史教育-3到9年級` | `台灣史主課-2025-8b`、`現代史主課-2025-9c` | `raw/歷史教學/` |
| 台灣文學 | `wiki/_overview-語文教學與跨領域.md` | — | `亞細亞孤兒-吳濁流`、`summary-9c-台灣近現代文學與歷史` | `raw/語文教學-中文台灣文學/` |
| 導師/班經 | `wiki/_overview-班級經營.md` | `concept-華德福班級經營` | `一報還一報-9c-畢業戲劇-2026` | `raw/班級經營/` |
| 跨領域 | `wiki/_overview-跨領域與專題.md` | `concept-走讀台灣`、`concept-八年級專題報告` | — | `raw/跨領域與專題/` |

> 所有 wiki 頁面路徑皆相對於 `bases/my-pages-wiki/`。
> Entity/Concept 頁名對應 `wiki/` 資料夾內的 `.md` 檔。

---

*維護者：David。最後更新：2026-04-11*
