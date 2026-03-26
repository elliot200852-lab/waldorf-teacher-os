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

*維護者：David。最後更新：2026-03-26*
