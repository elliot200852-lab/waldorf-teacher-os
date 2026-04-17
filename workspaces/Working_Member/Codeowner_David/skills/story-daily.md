---
name: story-daily
description: >
  「臺灣的故事」每日全流程管線。一鍵觸發從選題到上傳的完整 7 步驟：
  自動編號 → 選題（story-planner）→ 素材搜尋（story-research）→ 撰寫三件套 + 黑板畫 prompt（story-writer）→
  品質檢查（story-verify）→ 組裝 HTML/PDF 並上傳 Google Drive（assemble-story.js）→ 歸檔索引（story-archive）。
  當教師提到臺灣的故事、每日臺灣的故事、寫一篇臺灣的故事、Daily Story of Taiwan、daily story、stories of taiwan 時觸發。
triggers:
  - 臺灣的故事
  - 每日臺灣的故事
  - 寫一篇臺灣的故事
  - Daily Story of Taiwan
  - daily story
  - stories of taiwan
platforms: [cowork, claude-code, gemini]
requires_args: false
version: 2.2.0
created: 2026-03-21
updated: 2026-03-22
---

# skill: story-daily — 臺灣的故事・每日全流程管線

一鍵觸發完整的故事產製流程，從選題到上傳 Google Drive 全部自動化。
本技能是編排器（orchestrator），依序呼叫 5 個子技能 + 1 個 Node.js 腳本。

**工作規則**：授權模型、版本管理、檔名規範、強制完成規則全部依
`workspaces/Working_Member/Codeowner_David/teacheros-personal.yaml` 的 `ai_working_rules` 區塊。
本檔不重述。story-daily 特有差異：Step 1 互動模式下的選題確認是唯一例外。

---

## 資料流總覽（DATA FLOW MAP）

```
Step 0-1: plan
  輸入：index.yaml, theme-skeleton.yaml
  輸出：current-task.yaml
  存放：projects/stories-of-taiwan/

Step 2: research
  輸入：current-task.yaml
  輸出：[ID]-raw-materials.md
  存放：stories/[block]/[ID]/

Step 3: write
  輸入：[ID]-raw-materials.md
  輸出：[ID]-content.md, [ID]-narration.md, [ID]-images.md, [ID]-chalkboard-prompt.md
  存放：stories/[block]/[ID]/

Step 4: verify
  輸入：[ID]-content.md, [ID]-narration.md, [ID]-images.md, [ID]-raw-materials.md
  輸出：reviews/[ID]-quality.md
  存放：projects/stories-of-taiwan/reviews/

Step 5: gemini（瀏覽器操作）
  輸入：[ID]-chalkboard-prompt.md 中的 English Prompt
  操作：開啟 Gemini → 貼入 prompt → 等待生成 → 下載圖片 → 重命名
  輸出：AssemblyStory-[ID]-chalkboard.png
  存放：~/Downloads/（不進 Repo）

Step 6: assemble
  輸入（5 項）：
    1. stories/[block]/[ID]/[ID]-content.md
    2. stories/[block]/[ID]/[ID]-narration.md
    3. stories/[block]/[ID]/[ID]-images.md
    4. stories/[block]/[ID]/[ID]-chalkboard-prompt.md（含下載檔名指向 ~/Downloads/）
    5. ~/Downloads/AssemblyStory-[ID]-chalkboard.png
  額外輸入：stories/[block]/[ID]/[ID]-raw-materials.md（URL 超連結來源）
  設計規範：ai-core/reference/stitch-design-brief.md + publish/templates/waldorf-base.html
  執行指令（強制帶旗標）：
    node publish/scripts/assemble-story.js stories/[block]/[ID] --pdf --upload
  輸出：
    1. temp/beautify-[ID]-完整版.html
    2. temp/[ID]-完整版.pdf
    3. Google Drive「台灣的故事」資料夾（HTML + PDF）

Step 7: archive
  輸入：[ID]-content.md（提取 metadata）
  輸出：更新 index.yaml, project.yaml
  清理：刪除 current-task.yaml
```

**關鍵規則：**
- 黑板畫圖檔只存 ~/Downloads/，不複製到 Repo
- assemble-story.js 必須帶 `--pdf --upload` 旗標，不可省略
- 事實出處表必須有可點擊的超連結（來自 [ID]-raw-materials.md 的 URL）
- 投影圖像清單必須完整呈現（標題、描述、來源、URL、授權、展示時機）
- [ID]-chalkboard-prompt.md 中的「下載檔名」欄位必須在 Step 5 完成後立即填入

---

## 步驟間 Checkpoint 矩陣（MANDATORY CHECKPOINT MATRIX）

**每個步驟啟動前，AI 必須驗證前一步驟的產出。驗證未通過 → 立即回報 FAIL 並停止 pipeline（除非標記 WARN）。**

**每個 checkpoint 輸出必須包含實際檔案大小（bytes），不能只寫 PASS/FAIL。格式：`[CHECKPOINT Step X→Y] PASS — [ID]-file.md (2,345 bytes)` 或 `FAIL — 原因`。**

| 轉換點 | 驗證項目 | 失敗等級 |
|--------|---------|---------|
| **前置** | 若目標故事子資料夾已存在且含 `[ID]-content.md`：(1) 若教師指令含版本關鍵字（第二版/v2/重跑等）→ 自動切換到版本子資料夾 `[ID]-v2/`，不覆蓋原版；(2) 若教師未提及版本 → 覆蓋模式，但必須先報告「將覆蓋 [ID]/ 的現有產出（[ID]-content.md: XX bytes, 最後修改: YYYY-MM-DD）」 | WARN → 報告後繼續 |
| Step 0→1 | `index.yaml` 存在且可解析；`theme-skeleton.yaml` 存在 | FAIL → 停止 |
| Step 1→2 | `current-task.yaml` 存在 + `story_id`、`title`、`sub_theme`、`search_keywords` 欄位非空 | FAIL → 停止 |
| Step 2→3 | `[ID]-raw-materials.md` 存在 + 字數 > 500 + 「資料來源」段落至少 3 筆含 URL 的來源 | FAIL → 停止 |
| Step 3→4 | `[ID]-content.md` 存在且字數 > 300；`[ID]-narration.md` 存在；`[ID]-images.md` 存在且至少 1 張主圖；`[ID]-chalkboard-prompt.md` 存在且含 `## English Prompt` 段落 | FAIL → 停止 |
| Step 4→5 | `reviews/[ID]-quality.md` 存在 + 總評狀態為 PASSED 或 NEEDS_REVISION（FAILED → 停止） | FAIL → 停止 |
| Step 5→6 | `~/Downloads/AssemblyStory-[ID]-chalkboard.png` 存在 + 檔案大小 > 50KB；`[ID]-chalkboard-prompt.md` 下載檔名欄位已填入；**gemini-chalkboard Step 11 圖片內容驗證 = PASS**（AI 讀取圖片確認主題吻合） | FAIL → 重試 Step 5（最多 3 次：重新掃描 ~/Downloads/ + 重新從 Gemini 下載），仍失敗則停止 pipeline。**排程模式例外**：若 Claude in Chrome 不可用，依排程 fallback 表處理（SKIP + 待補圖） |
| Step 6→7 | `temp/beautify-[ID]-完整版.html` 存在；`temp/[ID]-完整版.pdf` 存在；HTML 中 source URLs > 0；HTML 中 Images > 0；Drive 上傳成功回傳 file ID | FAIL → 停止 |
| Step 7→8 | `index.yaml` 中已存在該 story_id 的條目；`current-task.yaml` 已刪除；AI 已在記憶體中保留報告所需 metadata（story_id、title、block） | WARN → 繼續但在報告中標記 |

**Checkpoint 執行方式：**
- AI 在進入每個新步驟前，逐項檢查上表對應的驗證項目
- 檢查結果以 `[CHECKPOINT Step X→Y] PASS / FAIL / WARN: 原因` 格式輸出（含實際檔名，如 `A001-content.md (2,345 bytes)`）
- FAIL 等級：立即停止 pipeline，寫入 `pipeline-status.yaml`，回報教師
- WARN 等級：記錄問題，繼續執行，在 Step 8 完成報告中標記

---

## 排程模式 fallback（SCHEDULED MODE FALLBACK）

排程任務（Cowork Scheduled Task）在無人值守的環境下執行，可能遇到以下工具不可用的情況：

| 情境 | fallback 行為 |
|------|-------------|
| Claude in Chrome 不可用（Step 5） | 跳過 Step 5，將 `pipeline-status.yaml` 標記 `chalkboard: pending`；Step 6 組裝時使用純文字替代方案（無黑板畫嵌入），HTML/PDF 照常產出並上傳 |
| osascript 橋接不可用 | 跳過所有需要 osascript 的操作（圖片讀取、Mac 端檔案操作）；改用 VM 內可用的 Node.js 直接執行組裝 |
| GWS CLI 不可用 | 跳過 Drive 上傳，HTML/PDF 存入 `temp/`，在 `pipeline-status.yaml` 標記 `drive_upload: pending` |
| 任何步驟 FAIL | 寫入 `pipeline-status.yaml`（含 FAIL 步驟、原因、已完成步驟列表），下次手動 session 啟動時提示教師 |

**`pipeline-status.yaml` 格式：**
```yaml
story_id: A004
pipeline_version: 2.1.0
started_at: 2026-03-22T10:30:00
mode: scheduled
steps:
  step_0_1: { status: PASS }
  step_2:   { status: PASS }
  step_3:   { status: PASS }
  step_4:   { status: PASS }
  step_5:   { status: SKIP, reason: "Claude in Chrome unavailable" }
  step_6:   { status: PASS, note: "No chalkboard image embedded" }
  step_7:   { status: PASS }
pending_actions:
  - "chalkboard: 需手動執行 Step 5 並重新組裝"
  - "drive_upload: 需確認 HTML/PDF 已上傳"
```

---

## 適用對象

David（管理員）。其他教師 clone Repo 後亦可使用。

## 適用平台

| 平台 | 排程方式 | 備註 |
|------|---------|------|
| Cowork | Scheduled Task（`stories-of-taiwan-daily`，Mon-Fri 10:30） | 全自動 |
| Claude Code | 手動觸發（說「臺灣的故事」或 `/story-daily`） | Mac/Windows |
| 其他 AI | 手動觸發 + 讀取本檔案 | 需有檔案讀寫與網路搜尋能力 |
| 無 AI 環境 | 手動撰寫 5 份 .md → `node assemble-story.js` | 只需 Node.js |

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 前置條件

- Node.js 已安裝（assemble-story.js 所需）
- GWS CLI 已安裝並認證（上傳 Google Drive 所需；詳見 `ai-core/skills/gws-bridge.md`）
- `requests` Python 套件已安裝（story-research 的 API 搜尋所需）

## 讀取的檔案（啟動時）

1. `projects/stories-of-taiwan/project.yaml` — 專案進度
2. `projects/stories-of-taiwan/themes/theme-skeleton.yaml` — 主題骨架
3. `projects/stories-of-taiwan/index.yaml` — 已完成故事索引

---

## 執行步驟

### 前置檢查 — Pipeline 恢復偵測

啟動時，AI 先檢查 `projects/stories-of-taiwan/pipeline-status.yaml` 是否存在：

- **存在** → 讀取內容，向教師報告：「上次 pipeline 未完成（[story_id]，中斷於 Step [X]，原因：[reason]）。要從中斷處繼續嗎？」
  - 教師確認「繼續」→ 跳至 `pipeline-status.yaml` 記錄的下一個待執行步驟
  - 教師確認「重跑」→ 刪除 `pipeline-status.yaml`，從 Step 0 重新開始
  - 教師確認「放棄」→ 刪除 `pipeline-status.yaml`，結束
- **不存在** → 正常從 Step 0 開始

### Step 0 — 自動編號

讀取 `index.yaml`，找出最新的 story ID，自動遞增：

**編號邏輯：**
- 每個區塊使用字母前綴：A = origins, **BT = botany（臺灣植物誌）**, **EN = encounter（大航海時代）**, C = colonial, D = qing, E = japanese, F = modern, G = contemporary
- 注意：BT-botany 使用 `BT` 前綴（非 `B`），EN-encounter 使用 `EN` 前綴（非 `B`），均避免與植物學五年級 Botany（B001~B030）衝突
- 區塊內流水號三位數：A001, A002, ..., EN001, EN002, ..., C001
- 讀取 index.yaml 中該區塊最大編號，+1
- 若區塊內尚無故事，從 001 開始

**報告格式：**
```
下一篇故事編號：[ID]
區塊：[block_name] — [區塊標題]
區塊進度：已完成 [M] / 目標 [N] 篇
```

### Step 1 — 選題（story-planner）

讀取並執行 `ai-core/skills/story-planner.md`。

產出：`projects/stories-of-taiwan/current-task.yaml`（暫存選題結果）。

**模式判斷：**
- **自動模式**：當 pipeline 由排程任務（Scheduled Task）觸發時 → 跳過教師確認，直接進入 Step 2
- **互動模式**：當教師手動說出觸發語時 → 向教師報告選題結果，等待確認

**判斷信號：** AI 檢查自身啟動來源。若為排程任務回呼（如 CronCreate 觸發或 Scheduled Task 派發），判定為自動模式；否則為互動模式。story-planner.md 不需要接收模式參數——模式判斷由 story-daily 編排器負責，planner 只負責選題邏輯。

### Step 2 — 素材搜尋（story-research）

讀取並執行 `ai-core/skills/story-research.md`。

產出：`stories/[區塊]/[ID]/[ID]-raw-materials.md`。

注意：故事檔案使用子資料夾 + ID 前綴命名（`A001/A001-raw-materials.md`）。每個檔案以所屬資料夾 ID 為前綴，確保檔名在搜尋與引用時具備唯一性。

### Step 3 — 撰寫三件套 + 黑板畫 prompt（story-writer）

讀取並執行 `ai-core/skills/story-writer.md`。

產出（全部存入 `stories/[區塊]/[ID]/`）：
- `[ID]-content.md` — 故事正文 + 事實出處表
- `[ID]-narration.md` — 教師說書稿
- `[ID]-images.md` — 投影圖像清單 + 黑板畫步驟

**額外產出黑板畫 prompt：**

在三件套完成後，根據故事主題與視覺需求，撰寫 `[ID]-chalkboard-prompt.md`：

```markdown
# 黑板畫 Prompt：[ID] [標題]

## English Prompt（Gemini 製圖用）

請你生成一張圖片

[200 字以內的英文 prompt，使用具象藝術語言描述構圖、色彩、光影、氛圍]

## 中文翻譯

[對應的中文翻譯]

## 迭代紀錄

| 版本 | 調整重點 | 結果 |
|------|---------|------|
| v1 | 初版 | 待評估 |

## 下載檔案名

（Gemini 產圖後手動填入）
```

**核心原則：概念先行，藝術補強。** prompt 描述的是一幅在黑色背景上用粉筆繪製的華德福風格黑板畫，畫面必須能傳達故事的核心意象。

**重要：Prompt 第一行固定為「請你生成一張圖片」（中文指令），空一行後接英文描述。此中文前綴觸發 Gemini 的圖片生成模式。AI 在 Step 5 操作 Gemini 時，貼入的完整 prompt 必須包含此前綴。**

### Step 4+5 — 品質檢查與黑板畫生成（平行執行）

**Step 3 完成後，AI 必須同時啟動以下兩項工作以節省時間並減少 context drift：**

**（平行任務 A）啟動 subagent 執行 Step 4 品質檢查：**
- 將以下資訊傳給 subagent：story ID、故事子資料夾完整路徑、story-verify.md 路徑
- Subagent 讀取 [ID]-content.md、[ID]-narration.md、[ID]-images.md、[ID]-chalkboard-prompt.md、[ID]-raw-materials.md
- 依 `ai-core/skills/story-verify.md` 規格執行完整品質檢查
- 產出 `projects/stories-of-taiwan/reviews/[ID]-quality.md`
- 回報 PASSED / NEEDS_REVISION / FAILED

**（平行任務 B）主 agent 同時執行 Step 5 Gemini 黑板畫生成：**
- 主 agent 保留瀏覽器操作能力（Claude in Chrome 工具只有主 agent 可用）
- 執行下方的 Step 5 完整操作流程

**同步匯合（MANDATORY SYNCHRONIZATION）：**

主 agent 必須等待兩個平行任務都完成後，才能進入 Step 6。匯合邏輯：

1. **等待**：主 agent 完成 Step 5 後，檢查 subagent（Step 4）是否已回傳結果。若未完成，等待 subagent 完成。
2. **Subagent 回傳格式**：
   ```
   {
     "status": "PASSED" | "NEEDS_REVISION" | "FAILED",
     "quality_report_path": "projects/stories-of-taiwan/reviews/[ID]-quality.md",
     "issues": ["issue1", "issue2"]  // 僅 NEEDS_REVISION/FAILED 時
   }
   ```
3. **匯合後判斷**：
   - Step 4 = PASSED 且 Step 5 = PASS → 繼續 Step 6
   - Step 4 = NEEDS_REVISION → 主 agent 根據 issues 修正對應檔案，重新提交給 subagent 驗證（最多 2 次）
   - Step 4 = FAILED → 暫停流程，通知教師
   - Step 5 = FAIL → 依 Checkpoint Step 5→6 重試邏輯處理

### Step 5 — 黑板畫生成

**執行共用技能 `ai-core/skills/gemini-chalkboard.md`。**

參數：
- STORY_ID = [當前故事 ID]
- STORY_DIR = stories/[block]/[ID] 的完整路徑
- VERSION = [版本標記，若有]

完整操作流程（12 步）、圖片內容驗證 checkpoint、重試邏輯、排程 fallback 均定義於 `gemini-chalkboard.md`。

**完成條件：** gemini-chalkboard.md 的 Checkpoint 全部通過（檔案存在 + > 50KB + 圖片內容驗證 PASS + 下載檔名已登錄）。

### Step 6 — 組裝 HTML/PDF 並上傳 Google Drive

執行 `assemble-story.js`，將 5 份 .md 檔 + 黑板畫圖片組裝成美化 HTML + PDF。

**渲染規範：** 遵循 `ai-core/skills/beautify.md` 的設計規範（四季視覺系統、字級間距、季節裝飾）。組裝腳本直接套用 `publish/templates/waldorf-base.html` 模板。

**指令（旗標為強制，不可省略）：**

```bash
# macOS / Linux（從 Repo 根目錄執行）
node publish/scripts/assemble-story.js stories/[區塊]/[ID] --pdf --upload

# 版本模式（不覆蓋原版，加版本號到檔名）
# 注意：傳入的是版本子資料夾 [ID]-v2，腳本會從目錄名自動解析 storyId。
# --version 旗標只在目錄名不含版本號時才需要，避免 storyId 與 version 雙重疊加。
# 正確用法（二擇一）：
node publish/scripts/assemble-story.js stories/[區塊]/[ID]-v2 --pdf --upload
# 或：
node publish/scripts/assemble-story.js stories/[區塊]/[ID] --pdf --upload --version=v2
# 錯誤用法（會產生 -v2-v2- 雙重版本號）：
# node publish/scripts/assemble-story.js stories/[區塊]/[ID]-v2 --pdf --upload --version=v2  ← 禁止

# Cowork VM（透過 osascript 橋接 Mac 執行）
osascript: cd [repo-path] && node publish/scripts/assemble-story.js [story-dir] --pdf --upload
```

**腳本的 6 項強制檢查清單：**
1. `[ID]-content.md` — 故事正文 + 事實出處表（表中來源須有可點擊的 URL 超連結）
2. `[ID]-narration.md` — 教師說書稿（含節奏表、段落指引）
3. `[ID]-images.md` — 投影圖像清單（每張圖須有標題、描述、來源、URL、授權、展示時機）
4. `[ID]-chalkboard-prompt.md` — Gemini 中英文 prompt + 下載檔名
5. `~/Downloads/AssemblyStory-[ID]-chalkboard.png` — 黑板畫圖檔（Step 5 已下載）
6. `[ID]-raw-materials.md` — 提供 URL 超連結來源（選用但強烈建議）

**完成條件（全部必須滿足，否則回報 FAIL）：**
- HTML 輸出：`temp/beautify-[ID]-完整版.html` 存在
- PDF 輸出：`temp/[ID]-完整版.pdf` 存在且 > 100KB
- 黑板畫：HTML 中 Drawing 狀態為 `embedded`（assemble-story.js v2.1.0 會在黑板畫缺失時以 exit code 2 終止，不再靜默跳過）
- 事實出處：HTML 中 source URLs 數量 > 0
- 投影圖像：HTML 中 Images 數量 > 0
- Google Drive：HTML + PDF 已上傳至「台灣的故事」資料夾

**Step 6 輸出驗收（MANDATORY OUTPUT VALIDATION）：**

assemble-story.js v2.1.0 內建嚴格驗證門檻（exit code 2 = 驗證失敗），自動檢查以下 5 項：
1. 故事段落數 > 0（[ID]-content.md 解析結果非空）
2. 事實出處表項目數 > 0 且至少 1 筆有可點擊 URL
3. 圖像清單項目數 > 0
4. 黑板畫圖檔已嵌入為 base64（非 fallback 文字）
5. 說書稿節奏表項目數 > 0

若腳本回傳 exit code 2，AI 必須：
1. 讀取腳本輸出的錯誤訊息，判斷哪個組件缺失
2. 回到對應的子步驟修正（例：黑板畫缺失 → 回 Step 5 重新生成）
3. 修正後重新執行 assemble-story.js
4. 最多重試 2 次，仍失敗則 FAIL 停止 pipeline

**上傳策略（upsert）：** 上傳前先搜尋 Drive 資料夾中同 storyId 的所有舊檔並刪除，再上傳新版。確保資料夾內每篇故事永遠只有最新的 HTML + PDF 各一份。此邏輯已內建於 assemble-story.js v2.0.0 的 `--upload` 流程中。

**上傳目標：** Google Drive 資料夾「台灣的故事」（ID: `1TBD6Xs-wVgqqlX3_13boy4xbBnjQ9LdY`）。

**GWS CLI 呼叫方式依平台而異（詳見 `ai-core/skills/gws-bridge.md`）：**
- Cowork：透過 osascript 橋接 Mac 執行
- Claude Code / 其他：直接在終端機執行 `gws drive +upload`

**上傳成功後，觸發 CreatorHub 網站部署：**

```bash
gh workflow run deploy-channel.yml
```

此指令觸發 GitHub Actions 的 sync + deploy 流程（~3 分鐘），確保新故事立即出現在 CreatorHub 網站上。若 `gh` 指令不可用，跳過（不阻擋 pipeline），在完成報告中標記「CreatorHub 部署：未觸發（gh CLI 不可用）」。

### Step 7 — 歸檔索引（story-archive）

讀取並執行 `ai-core/skills/story-archive.md`。

注意：`index.yaml` 中的 `files` 路徑需使用子資料夾 + ID 前綴格式：
```yaml
files:
  content: stories/A-origins/A001/A001-content.md
  narration: stories/A-origins/A001/A001-narration.md
  images: stories/A-origins/A001/A001-images.md
```

### Step 8 — 完成報告

**注意：** Step 7 (archive) 會刪除 `current-task.yaml`。Step 8 的報告資料（story_id、title、block 等）必須使用 AI 在 pipeline 執行過程中已暫存在記憶體中的資訊，或從 Step 7 回傳的歸檔結果取得。不依賴 `current-task.yaml`。

產出完成摘要（必須包含每一步的 PASS/FAIL 狀態）：

```
=== 臺灣的故事・每日管線完成 ===
故事編號：[ID]
標題：[title]
區塊：[block] — [block_title]

Pipeline 狀態：
  Step 0-1 選題：    [PASS/FAIL]
  Step 2   素材搜尋：[PASS/FAIL]
  Step 3   撰寫：    [PASS/FAIL]
  Step 4   品質檢查：[PASS/FAIL]
  Step 5   黑板畫：  [PASS/FAIL] — ~/Downloads/AssemblyStory-[ID]-chalkboard.png
  Step 6   組裝：    [PASS/FAIL]
    HTML：     [temp/beautify-[ID]-完整版.html]
    PDF：      [temp/[ID]-完整版.pdf]
    黑板畫嵌入：[embedded / not found]
    事實超連結：[N 個 URL]
    投影圖像：  [N 張]
    Google Drive：[已上傳 / 未上傳（原因）]
  Step 7   歸檔：    [PASS/FAIL]

檔案清單：
  - stories/[block]/[ID]/[ID]-content.md
  - stories/[block]/[ID]/[ID]-narration.md
  - stories/[block]/[ID]/[ID]-images.md
  - stories/[block]/[ID]/[ID]-chalkboard-prompt.md
  - stories/[block]/[ID]/[ID]-raw-materials.md
  - temp/beautify-[ID]-完整版.html
  - temp/[ID]-完整版.pdf
  - ~/Downloads/AssemblyStory-[ID]-chalkboard.png

區塊進度：[M] / [N] 篇
全專案進度：[total] / [annual_target] 篇
===
```

**若任何步驟為 FAIL，AI 必須在報告中明確標示失敗原因，不得隱藏。**

---

## 子資料夾結構

每篇故事以獨立子資料夾存放：

```
stories/
  A-origins/
    A001/
      A001-content.md
      A001-narration.md
      A001-images.md
      A001-chalkboard-prompt.md
      A001-raw-materials.md
    A002/
      A002-content.md
      ...
  B-indigenous/
    B001/
      B001-content.md
      ...
```

Repo 內只存 `.md` 檔案。黑板畫圖檔保留在本機 `~/Downloads/`，不進 Repo。

---

## 故障處理

| 狀況 | 處理 |
|------|------|
| API 搜尋全部失敗 | 僅用 AI 網路搜尋補充，在報告中標記 |
| story-verify 未通過 | 自動修正最多 2 次，仍失敗則暫停 |
| 黑板畫圖檔不存在（互動模式） | 重試 Step 5 最多 3 次（4 種搜尋策略 + 重新從 Gemini 下載），仍失敗則 FAIL 停止 pipeline |
| 黑板畫圖檔不存在（排程模式） | Claude in Chrome 不可用時，SKIP + 標記「待補圖」，HTML/PDF 照產但不含黑板畫 |
| GWS CLI 未安裝/未認證 | 跳過上傳，HTML/PDF 存本地，提示手動上傳 |
| Node.js 未安裝 | 跳過 Step 5（組裝），提示安裝 |
| index.yaml 不存在 | 從 A001 開始，建立新 index.yaml |

---

## 注意事項

- 本技能是編排器，不包含各子步驟的細節邏輯——細節全在子技能的正本中
- 排程模式下全部步驟自動推進；互動模式下 Step 1（選題）需教師確認
- 所有路徑使用 `path.join()` 或 `pathlib.Path()`，支援 macOS / Windows / Linux
- 不使用表情符號
