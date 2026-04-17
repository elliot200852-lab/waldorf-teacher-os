---
aliases:
  - "Tool Call 紀律規範"
  - "AI Token 預算管理政策"
---
## Tool Call 紀律（防止 token 浪費）

AI 的每一次 tool call 都消耗 token 預算。在 Max 5x 配額下，浪費即降級。
但紀律的目的是消除冗餘，不是犧牲精準度。該讀的檔案一定要讀。

### 三層載入與計數規則

**第一層：啟動必讀 → 不計入上限**

每次 session 開始時依 `AI_HANDOFF.md` 載入的檔案，不受本規則限制：
- `CLAUDE.md` → `AI_HANDOFF.md`
- `teacheros.yaml`、`teacheros-foundation.yaml`、`acl.yaml`
- `{workspace}/teacheros-personal.yaml`
- `projects/_di-framework/project.yaml`
- `opening.md` 執行的 `git fetch` / `git pull`

**第二層：工作觸發載入 → 不計入上限，但不得重複讀取**

進入具體任務時，依 AI_HANDOFF 工作類型表或技能觸發表讀取的檔案：
- 技能正本（如 `lesson-engine.md`、overlay 檔）的**首次讀取**
- 班級 `project.yaml` + 科目 `session.yaml`
- 科目 DI template（如 `english-di-template.md`）
- AI_HANDOFF reference 表定義的主動觸發讀取（如備課時讀 `steiner-pedagogy-methods.yaml`）

這些是任務必需的，首次讀取不計入上限。
但同一 session 內**已讀過的檔案不得重複讀取**（已在 context 中）。

**第三層：任務執行中的 tool call → 計入上限，受本規則約束**

啟動完成、工作檔案就位後，所有後續 tool call 開始計數。
這包括：寫入檔案、執行腳本、搜尋資料、目錄操作等。

### 執行前：先列計畫

收到任務後，先用 2-3 行列出執行計畫（預計幾次 tool call、每次做什麼），再動手。
不要邊想邊調用。

### 軟上限（僅計第三層）

| 任務類型 | tool call 軟上限 |
|---------|-----------------|
| 搜尋 / 查詢 | 5 次 |
| 一般任務 | 10 次 |
| lesson-engine 五階段流程 | 15 次 |

接近或超過上限時暫停，說明為何需要更多，等教師確認後才繼續。
複雜任務（含 PDF 輸出 + Drive 上傳 + 美化）可能合理超限，但須報告。

### 合併原則

- 能一次 Bash 完成多條指令的不要拆成多條（用 `&&` 串接）
- 能用 `glob` 一次定位的不要逐層搜尋
- 能並行調用的獨立 tool call 放在同一輪送出
- 讀取檔案用 Read 工具（不用 `cat`），但多條 shell 指令應合併為一次 Bash

### 禁止行為

- 預防性搜尋（「先看看有沒有…」——沒被要求就不要看）
- 重複搜尋同一關鍵字或近義詞
- 未被要求的目錄探索或檔案結構巡覽
- 對同一 session 內已在 context 中的檔案重複讀取

### Tool Call Audit

當可省略比例超過 30% 時，AI 主動附上 audit。教師也可隨時要求。

格式：

```
### Tool Call Audit
- 啟動載入（第一層）：N₁ 次（不計）
- 工作觸發（第二層）：N₂ 次（不計）
- 任務執行（第三層）：N₃ 次 ← 受軟上限約束
| # | 工具 | 理由 | 必要/可省略 |
|---|------|------|-------------|
| 1 | Write | 寫入 lesson output | 必要 |
| 2 | Bash | 確認輸出目錄存在 | 可省略 |
可省略比例：X/N₃
```

可省略超過 30% → 在 audit 末尾寫一行改善方案。

### 教師喊停時

教師指出 tool call 過多或浪費時：
1. 立即停止
2. 輸出已完成部分的 audit
3. 提出精簡替代計畫，等確認後繼續
