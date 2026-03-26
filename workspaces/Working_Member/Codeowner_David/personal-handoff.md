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

## 待接續工作：Repo 架構地圖工程化

**狀態：** 計畫已核准，尚未開始實作。
**計畫檔：** `.claude/plans/zazzy-chasing-whistle.md`（完整 6 Phase 設計）

### 背景

HOME.md 的檔案歸位邏輯（obsidian-sync Step 4）原本是硬寫在技能 prompt 裡的 34 條 Markdown 表格，導致反覆出錯（檔案放錯位置、自動收錄等問題）。前一個 session 已完成緊急修復：
- 清除 HOME.md 全部 28 條「自動收錄」殘留，逐一歸位到正確區段
- 重寫 obsidian-sync Step 4 為 34 條精確路由規則
- pre-commit hook 攔截「自動收錄」

但這仍是 prompt-level 解法。David 決定做工程級升級。

### 要做的事

建立 `ai-core/reference/repo-structure-map.yaml` — Repo 自己的完整架構地圖，三個區段：
1. **rules** — 路徑模式 → HOME.md 區段的路由規則（first-match-wins）
2. **sections** — HOME.md 的完整區段樹（用於 forward validation）
3. **tracked_directories** — 所有 git-tracked 目錄（用於 backward validation，自動生成）

### 執行順序（6 Phase）

1. **Phase 6：初始生成** — 寫 `setup/scripts/map-generate-initial.py`，從 HOME.md wikilink 反推生成地圖初版
2. **Phase 1：建立地圖檔** — 審查初版，補完為完整 `repo-structure-map.yaml`
3. **Phase 2：驗證腳本** — 寫 `setup/scripts/map-validate.py`（`--validate` / `--pre-commit` / `--rebuild-dirs` / `--rebuild-sections` / `--auto-fix`）
4. **Phase 3：升級 obsidian-check.py** — 讀取地圖、`suggest_section()` 函數、輸出 `FILE:NOT_IN_HOME:path|section` 格式
5. **Phase 4：精簡 obsidian-sync.md** — 移除嵌入表格，改讀腳本建議
6. **Phase 5：pre-commit hook** — 偵測 HOME.md 標頭異動或新目錄 → 警告地圖可能需更新

### 關鍵技術決策（已確認）

- Python 3.14 + PyYAML 6.0.3（已安裝）
- `PurePath.match()` 支援 `**`（Python 3.12+）
- 地圖直接用 YAML（不需要 JSON 中間層）
- 觸發機制是 pre-commit 警告（不阻擋 commit）
- obsidian-check.py 若地圖不存在則 graceful 退化

### 驗證清單（10 點，必須全過）

見計畫檔「驗證方式（嚴格）」段落。

---

*維護者：David。最後更新：2026-03-26*
