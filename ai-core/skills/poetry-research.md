---
name: poetry-research
description: 英文備課素材研究工具。輸入主題，自動串接五個免費 API（PoetryDB、Datamuse、Free Dictionary、Gutendex、Open Library），產出詩歌、詞彙卡、語意場、練習單與書單。
triggers:
  - 詩歌研究
  - 英文詩歌研究
  - 英文詩歌備課
  - poetry research
  - find poems
requires_args: true
---

# skill: poetry-research — 英文備課素材研究

輸入一個主題（英文），自動串接五個免費 API，產出結構化的備課素材。

## 適用對象

David 及英文科教師。

## 參數

- `<topic>`（必填）：研究主題（英文），例如 "courage"、"the sea"、"identity and belonging"
- `[grade]`（選填）：年級（7/8/9），預設 9
- `[subject]`（選填）：科目，預設 english

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 執行步驟

### Step 0 — 確認使用者身份

從 `ai-core/acl.yaml` 取得當前使用者的 workspace 路徑。

### Step 1 — 執行研究腳本

```bash
# macOS / Linux
python3 setup/scripts/research_pipeline_v2.py "<topic>" --grade <grade> --subject <subject> --workspace "<workspace_path>"

# Windows（PowerShell）
python setup/scripts/research_pipeline_v2.py "<topic>" --grade <grade> --subject <subject> --workspace "<workspace_path>"
```

> **跨平台注意：** AI 應先偵測可用的 Python 指令（`python3` 或 `python`）。

### Step 2 — 報告結果

讀取腳本輸出，向教師報告：

```
研究完成：<topic>（<grade> 年級 <subject>）

產出位置：{workspace}/poetry_output/<topic>/
- 詩歌：N 首
- 詞彙卡：N 張
- 語意連結：N 個
- 書籍：N 本
[若有 WARNINGS，列出]

要看哪份產出？或直接進入課程設計？
```

### Step 3 — 後續銜接

教師確認後，可自然銜接：
- 「看詩」→ 讀取 `poems.md`
- 「看詞彙」→ 讀取 `vocab-cards.md`
- 「進入備課」→ 觸發 `lesson` 或 `subject-lesson-45` 技能
- 「再研究一個主題」→ 重新執行 Step 1

## 產出檔案

| 檔案 | 內容 |
|------|------|
| `research-output.yaml` | 完整研究資料（YAML，機器可讀） |
| `poems.md` | 詩歌合集（含作者、行數、相關度） |
| `vocab-cards.md` | 詞彙卡（音標、定義、例句提示） |
| `practice-sheet.md` | 練習單（詞彙配對、押韻、詩歌回應、創意寫作） |
| `semantic-map.md` | 語意地圖（Mermaid mindmap，可在 Obsidian 渲染） |

## API 來源

全部免費、不需 API Key：
1. PoetryDB — 詩歌搜尋
2. Datamuse — 語義關聯、押韻、同義詞（含詞頻過濾）
3. Free Dictionary — 詞彙定義、音標、例句
4. Gutendex — Project Gutenberg 公版書搜尋
5. Open Library — 書目資料與延伸閱讀

## 注意事項

- PoetryDB 對抽象現代主題（identity, belonging, empathy）命中率低，這是 API 本身的限制
- 三個主題並行跑可能觸發 Free Dictionary 的 rate limit，腳本已內建 retry 機制
- 產出存放在教師 workspace 內的 `poetry_output/` 資料夾，不影響其他教師
- 年級影響詩歌長度上限、詞頻門檻與詞彙數量（見腳本中的 GRADE_PROFILES）
