---
aliases:
  - "技能深度審查 2026-03-22"
  - "Opening Story-Daily Wrap-Up Review"
---

# TeacherOS 技能深度審查報告
**日期：** 2026-03-22
**審查者：** Claude Code (Opus 4.6) + Cowork (Gemini)
**審查範圍：** Opening、Story-Daily、Wrap-Up 三大核心技能
**方法：** 雙 AI 交叉審查 → 合併分析 → 二次驗證 → 逐項修正

---

## 一、審查方法與教訓

### 雙 AI 交叉驗證的價值

本次採用 Claude Code 和 Cowork (Gemini) 分別獨立審查，再合併分析。發現：

- Claude Code 初次審查有 **3 項誤判**（assemble-story.js 圖片 base64、taiwan_history_api.py、4 層搜尋策略），二次驗證時修正
- Cowork 發現 Claude Code 未注意的問題（macOS 無原生 `timeout` 指令、Glob 掃描跨平台風險）
- **結論：單一 AI 的審查不可盡信，交叉驗證有效降低誤判率**

### 修改原則的反思

每次 Deep Review 都傾向「加規格」而非「簡化」，有規格膨脹風險。
未來修改前應自問：**這是在修 bug，還是在加規格？** Bug 必修，規格新增要謹慎。

---

## 二、Opening（開機技能）— 10 項修正

修改檔案：`ai-core/skills/opening.md`

### 嚴重（已修正）

| # | 問題 | 修正方式 |
|---|------|---------|
| 1 | GWS 連線檢查缺 timeout（規格寫 5 秒但沒實作） | bash 改用 Python `subprocess.run(timeout=5)` 包裹（macOS 無原生 timeout）；PS 用 `Start-Job` + `Wait-Job -Timeout 5` |
| 2 | PowerShell `2>$null` 語法錯誤 | 改為 `2>&1`，加 `try/catch` 包裹 |

### 中等（已修正）

| # | 問題 | 修正方式 |
|---|------|---------|
| 3 | Python3 呼叫無跨平台 fallback | 新增 Step 2a，先試 `python3` 再試 `python`（bash + PS 雙版本） |
| 4 | Codeowner 技能檢查在 Step 0 執行，但 acl.yaml 到 Step 2 才讀（順序倒置） | 移至 Step 2a（acl.yaml 讀取之後） |
| 5 | 未 commit 改動時觸發 wrap-up 的條件不明 | 明確定義：先問教師 → 確認後觸發 → 完成後返回 git pull |
| 6 | git pull 衝突偵測未指定具體指令 | 加入 `git diff --name-only --diff-filter=U` |

### 低等 + 優化（已修正）

| # | 問題 | 修正方式 |
|---|------|---------|
| 7 | AI_HANDOFF 與 opening 重複 | 確認 AI_HANDOFF 已是簡要參照版，無需修改 |
| 8 | session.yaml 報告無排序、無排除規則 | 指定 `last_updated` DESC，排除 `_di-framework` 與 `phase: 已結案` |
| 9 | Step 4 摘要模板可擴充 | 加入 `current_focus`、`open_questions` 可選欄位 |
| 10 | 全部序列執行無平行化 | 新增「平行化指引」段落（Phase A/B/C/D，授權性質不強制） |

### 設計決策紀錄

- **GWS timeout 用 Python subprocess 而非 bash timeout**：因為 macOS 原生無 `timeout`，需裝 GNU coreutils 才有 `gtimeout`。用 Python 是最跨平台的方案。
- **平行化是「授權」不是「強制」**：AI agent 有能力時可自行平行化，無能力時序列執行也正確。不改變技能正確性。

---

## 三、Story-Daily（臺灣的故事管線）— 8 項修正

修改檔案：`story-daily.md`、`session.yaml`、`story-planner.md`、`story-research.md`、`story-writer.md`、`story-verify.md`、`story-archive.md`

### 審查修正（3 項誤判）

| 原始判斷 | 二次驗證結果 |
|---------|------------|
| assemble-story.js 缺圖片 base64 編碼 | **誤判** — 第 970-983 行有完整 `fs.readFileSync().toString('base64')` |
| taiwan_history_api.py 是空殼 | **誤判** — 有 7 個適配器實作，部分需 API Key |
| 4 層黑板畫搜尋未實現 | **誤判** — 第 955-1002 行完整實作 |

### P0 修正

| # | 問題 | 修正方式 |
|---|------|---------|
| 1 | `-v2-v2-` 檔名 bug（session.yaml 記錄 `beautify-A004-v2-v2-完整版.html`） | 根因：目錄名 `A004-v2` 被解析為 storyId 再加 `--version=v2`。修正 Step 6 指令說明（版本目錄和 --version 旗標二擇一，禁止同時使用）+ 修正 session.yaml 錯誤路徑 |
| 2 | current-task.yaml 在 Step 7 刪除但 Step 8 需要 | Step 8 改為使用記憶體中的 metadata，不依賴已刪除檔案 |
| 3 | Step 4+5 平行化無同步機制 | 補充等待匯合邏輯 + 定義 subagent 回傳格式 |
| 4 | 版本標記三方不統一（index/session/quality-log 各用不同格式） | 統一為嵌套模式（index.yaml 現行方式），session.yaml 從分列式改為嵌套式 |

### P1 修正

| # | 問題 | 修正方式 |
|---|------|---------|
| 5 | Checkpoint 與腳本行為不一致 | 驗證後確認已一致（exit code 2 = 驗證失敗），無需修改 |
| 6 | Pipeline 恢復邏輯無偵測機制 | 加入前置檢查段落：啟動時檢查 `pipeline-status.yaml` 是否存在 |
| 7 | 自動/互動模式切換信號未定義 | 定義判斷邏輯：排程=自動、手動=互動；planner 不需接收參數 |
| 8 | 5 個子技能的入口驗證與 checkpoint 矩陣重複 | 各子技能加入「權威來源：checkpoint 矩陣」參照，未來維護只改一處 |

### 設計決策紀錄

- **版本標記統一用嵌套模式**：index.yaml 已有此格式（A004 下嵌 v2:），session.yaml 和 quality-log 跟進。不用分列式（A004 + A004-v2 獨立鍵）是因為分列式會讓版本關係斷裂。
- **入口驗證保留但加參照**：不刪除子技能的入口驗證（獨立使用時需要），但標明 checkpoint 矩陣為權威來源。

---

## 四、Wrap-Up（收工技能）— 11 項修正

修改檔案：`ai-core/skills/wrap-up.md`、`ai-core/skills/opening.md`（marker 檢查）

### P0 修正

| # | 問題 | 修正方式 |
|---|------|---------|
| 1 | Push 失敗處理不完整 | 定義表格：branch behind → rebase + 重試（上限 2 次）；rebase 衝突 → `git rebase --abort` + 報告教師；認證/網路 → 報告 + 跳過；hook 攔截 → 排除後重試 1 次 |
| 2 | Subagent 平行化無回傳契約 | 定義回傳格式（status/changed_fields/files_modified/error）；git add 改為主 agent 統一執行 |
| 3 | 多班級失敗時繼續/停止邏輯不明 | 遵循優雅降級：單一班級失敗 → 記錄 → 繼續其他 → 摘要標記 |
| 4 | 未檢查當前 git branch | Step 4a 加入 `git branch --show-current`，非 main 時提醒教師 |

### P1 修正

| # | 問題 | 修正方式 |
|---|------|---------|
| 5 | Obsidian marker 機制斷裂（wrap-up 寫、opening 不讀） | Opening Step 4 補上 marker 檢查（不存在 → 提醒補跑） |
| 6 | Python3 跨平台偵測缺失 | Step 3 加入 python3/python fallback（bash + PS 雙版本） |
| 7 | Commit message 無格式規範 | 定義格式：`wrap-up: [摘要]` + 第二行列涉及內容 |
| 8 | last_updated 無時區說明 | 明確：YYYY-MM-DD 本地日期，不加時區（所有教師同時區） |

### P2 修正

| # | 問題 | 修正方式 |
|---|------|---------|
| 9 | confirmed_decisions 無去重 | 加入語意去重規則 |
| 10 | Obsidian 靜默通過隱藏執行狀態 | 改為簡短回報（完成/修正 N 個/部分跳過） |
| 11 | Context health 閾值不夠精準 | 加入「修改檔案數 > 30」指標 |

### 設計決策紀錄

- **Obsidian marker 保留**：David 決定保留（而非移除），Opening 端補上檢查邏輯。
- **git add 由主 agent 統一執行**：避免兩個 subagent 同時操作 git index 的競爭條件。
- **commit message 格式用 `wrap-up:` 前綴**：讓 git log 中收工 commit 一眼可辨。

---

## 五、未處理的 P2 項目（供下次參考）

| 技能 | 項目 | 狀態 |
|------|------|------|
| Story-Daily | story-verify.md 字數範圍調整（規格 300 vs 實際 650-1000） | 需教師確認合理範圍 |
| Story-Daily | taiwan_history_api.py 的 TCMB API Key | 待教師提供 |
| Story-Daily | Gemini 中文前綴觸發機制驗證 | 需實測 |
| Story-Daily | story-archive dry-run（A005 前跑一次） | 待執行 |

---

## 六、跨技能共通問題（Cowork 提出，尚未處理）

1. **跨平台實施缺統一 Python 執行層**——三個技能各自處理跨平台，建議建立 `platform-utils.py`。本次選擇在各技能文件內加 fallback，未建新腳本（David 選擇維持技能文件修正）。
2. **Subagent 平行化承諾 > 實際實現**——Opening 和 Wrap-Up 都改為「授權性質」（AI agent 有能力時自行採用）。Story-Daily 的 Step 4+5 平行化補充了同步機制。
3. **Obsidian marker 三端補齊**——wrap-up 寫入 + opening 讀取已完成。session-guard hook 不存在（低優先，暫不處理）。

---

*下次修改這三個技能時，先讀取本報告的「設計決策紀錄」段落，避免推翻已驗證的選擇。*
