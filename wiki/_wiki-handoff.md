---
aliases:
  - "Wiki 擴張路線圖"
  - "Wiki Handoff"
type: wiki-reference
tags:
  - wiki-reference
  - system
---

# 備課知識庫（Block Wiki）— 擴張路線圖

> 本文件記錄 wiki/ 系統的設計決策與未來擴張方向。
> 給未來的 AI session 和教師閱讀，確保知識延續。

---

## 目前狀態（Phase 1）

wiki/ 採扁平結構，每次 lesson-engine 完成階段五後，自動從對話擷取一篇備課日誌。

- 觸發點：lesson-engine 階段六（自動執行，預設寫入）
- 存放：`wiki/{class}-{subject}-w{week}-{seq}.md`
- 權限：`acl.yaml` 的 `shared_writable`，所有註冊教師可寫
- 內容來源：從備課對話自動擷取，教師零額外負擔
- Frontmatter：豐富版，支援 Obsidian Bases 多維篩選

---

## 決策歷程

### 為什麼掛在 lesson-engine，不是 block-end？

block-end 技能自建立以來從未被任何教師實際使用過（包含 David）。lesson-engine 是每位教師每天實際在用的工具。觸發點必須在教師的自然工作流中，不能要求額外動作。

### 為什麼預設自動寫入？

如果需要教師確認才寫入，大多數時候教師會跳過（因為備課結束後想趕快去上課）。預設寫入確保知識不會因為「忘了確認」而流失。教師說「不用」才跳過。

### 為什麼不建子目錄？

Phase 1 的目標是累積原始資料。在文章數量不足（< 50 篇）時，索引結構是過度設計。扁平結構 + Obsidian 搜尋 + graph view 足以應付早期使用。

### 為什麼從對話擷取，不訪談教師？

教師在備課對話中已經說了為什麼選這個素材、為什麼這樣設計 DI、為什麼調整某個環節。這些決策理由是最有價值的知識，不需要事後再問一次。

---

## Phase 2 — 已啟動（2026-04-06）

### 新增基礎建設

- **`obsidian-check.py --link-check`**：掃描缺少 `related:` 或 `## 連結` 的 .md 檔，輸出 `LINK_ORPHAN` 類別
- **`obsidian-sync.md` Step 1.5**：連結完整性檢查，教師確認後 AI 自動補齊
- **連結規範**：`ai-core/reference/wikilink-protocol.yaml`（Phase 1 建立）

### 2-1. `wiki/concepts/texts/` — 作者與文本概念頁

已建立：
- `wiki/concepts/texts/The-House-on-Mango-Street.md` — 跨 English + walking-reading-taiwan
- `wiki/concepts/texts/Sandra-Cisneros.md`

觸發門檻：跨 2 科/班出現即建立（David 確認）。

### 2-2. `wiki/concepts/grammar/` — 文法概念頁

已建立：
- `wiki/concepts/grammar/連接詞.md` — 9C English Block 2 核心語法
- `wiki/concepts/grammar/動詞片語.md` — 9C English Block 2 核心語法
- `wiki/concepts/grammar/關係代名詞.md` — 9C English Week 8

### 2-3. `wiki/concepts/themes/` — 教學主題索引

尚未建立。待跨科主題累積足夠（如「殖民與抵抗」「identity」）再啟動。

---

## Phase 2 新增 — raw-ingest 管線（2026-04-06）

### 外部文件消化入口

- **`wiki/raw/`**：教師放入待消化文件的目錄（PDF、Word、TXT、MD）
- **`wiki/raw/.ingest-log.yaml`**：已消化清單，AI 自動維護
- **`wiki/sources/`**：消化後產出的來源摘要頁

### 觸發方式

說「整合新文件」或「消化 raw」，AI 執行 `ai-core/skills/raw-ingest.md`。

### 使用流程

1. 把文件（PDF/Word/TXT/MD）放入 `wiki/raw/`
2. 說「整合新文件」
3. AI 預覽將產出的頁面，確認後寫入
4. `wiki/sources/` 產出來源摘要頁，`wiki/concepts/` 可能新增概念頁
5. 用 Obsidian Graph View 查看新節點

### 技術規格

完整規格見 `ai-core/skills/raw-ingest.md`。

### 2-3. `design-reflection` — 備課設計反思（2026-04-07 啟動）

#### 新增內容類型

`type: design-reflection`，與 `lesson-wiki`（Phase 6 自動產出）互補。

| | lesson-wiki (Phase 6) | design-reflection (wiki-reflect) |
|---|---|---|
| 觸發 | 自動 | 教師說「備課反思」 |
| 內容 | 設計摘要（做了什麼） | 設計思考（為什麼這樣做、決策歷程） |
| 檔名 | `{class}-{subject}-w{week}-{seq}.md` | `{class}-{subject}-w{week}-{seq}-reflect.md` |
| 長度 | ~150-200 字 | ~300-500 字 |

#### 雙向連結機制

- **wiki-reflect ↔ Phase 6**：透過 `-reflect` 後綴配對，frontmatter `related:` 雙向連結
- **wiki-reflect ↔ teaching-log**：wiki-reflect 寫入時自動掃描 teaching-log 同堂課紀錄；teaching-log 寫入時教師可口頭觸發反向連結（「合併之前的反思」）
- **wiki-reflect ↔ concepts**：自動偵測概念頁並互加 wikilink

#### Tags 規則

骨架標籤固定（`design-reflection` + 班級 + 科目 + block），其餘由 AI 從反思內容自動萃取，不設上限。確保 Obsidian graph view 連結廣度。

#### 技術規格

完整規格見 `ai-core/skills/wiki-reflect.md`。

### 2-4. `wiki/semesters/` — 學期鳥瞰報告

自動從 wiki/lessons 彙整一學期的教學概覽：素材使用頻率、DI 策略分布、主題覆蓋度。

觸發時機：學期末，手動觸發或排程產出。

### 2-5. `teacheros-lint` skill — 全學期一致性檢查

對整個 wiki 跑一致性檢查：
- 素材重複度（同一文本在同學期被不同課重複使用）
- DI 軸偏斜（長期偏重某些模態）
- 主題覆蓋（孤島主題、跨年級銜接斷裂）

產出：`wiki/semesters/{year}-{season}-lint-report.md`

觸發時機：每個 block 結束時、學期末。

### 2-6. Obsidian Base View — 預建篩選視圖

利用 Obsidian Bases 功能，建立預設的篩選視圖：
- 按科目篩選（所有英文課 wiki）
- 按年級篩選（所有九年級 wiki）
- 按教師篩選（某位教師的全部 wiki）
- 按 DI 策略篩選（使用過 scaffold 的所有課）

---

## 啟動擴張的判斷標準

Phase 2 已啟動。後續擴張判斷標準：

1. 概念頁數量 > 20 時，考慮建立自動偵測與建議機制
2. 兩位以上教師開始貢獻 wiki 文章時，加入跨教師概念頁
3. wiki/ 內累積 50 篇以上時，啟動學期鳥瞰報告

---

## 技術參考

| 項目 | 位置 |
|------|------|
| lesson-engine 階段六規格 | `ai-core/skills/lesson-engine.md` |
| wiki 權限設定 | `ai-core/acl.yaml` → `shared_writable` |
| Obsidian 路由規則 | `ai-core/reference/repo-structure-map.yaml` |
| 原始構想文件 | David 的 Downloads/handoff-obsidian-wiki.md（未入版控） |

---

*建立日期：2026-04-06*
*Phase 1 啟動：lesson-engine 階段六*
*Phase 2 啟動：2026-04-06（概念頁 + link-check + obsidian-sync 整合）*
*Phase 2-3 啟動：2026-04-07（design-reflection 類型 + wiki-reflect 技能 + teaching-log 雙向整合）*
