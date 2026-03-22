---
name: opening
description: 每次新對話的開場技能。確保 Repo 為最新版本（git pull origin main），然後讀取 AI_HANDOFF.md 並進入正常載入流程。這是所有工作的第一步。
triggers:
  - 開工
  - 開始
  - 我們今天開始吧
  - 新對話
  - 開機
  - start
  - 早安
  - 我來了
  - 準備好了
  - 今天開始
  - let's go
  - 上工
requires_args: false
---

# skill: opening — 新對話開場

每次新對話的第一步。確保教師的 Repo 是最新版本，然後進入正常的系統載入流程。

## 觸發條件

任何新對話開始時，教師說出接近以下意思的話，都應觸發此技能：
「開工」「我們今天開始吧」「新對話」「早安」「準備好了」「start」等。

**語音模式注意：** 教師以語音輸入為主，任何表達「準備開始工作」意圖的口語都應觸發，不等待精確指令。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 執行步驟

### Step 0 — 確保 Repo 為最新版本

**有終端機能力的 AI（Claude Code、Cowork 等）：**

依序執行以下指令：

```bash
# 1. 確認當前分支
git branch --show-current

# 2. 檢查是否有未 commit 的改動
git status --short

# 3. 抓取最新資訊
git fetch origin

# 4. 合併 main 的最新內容
git pull origin main
```

判斷邏輯：

| 狀況 | 處理 |
|------|------|
| `git status` 顯示有未 commit 的改動 | 先提醒：「你有未儲存的工作，要先存檔嗎？」若教師同意，觸發 `wrap-up` 技能，存完再繼續 |
| `git pull` 成功，無衝突 | 報告：「已更新至最新版本。」繼續 Step 1 |
| `git pull` 有衝突 | **停下來，不繼續載入。** 報告：「更新時發現檔案衝突，請聯繫 David 處理。」列出衝突的檔案清單 |
| `git pull` 顯示 "Already up to date" | 報告：「已是最新版本。」繼續 Step 1 |

**git pull 成功後 — 技能跨平台檢查（僅 Codeowner）：**

若當前使用者是 Codeowner（acl.yaml 中 admin），且 pull 有拉進新 commit，執行：

```bash
# 在 git pull 之前先記錄當前 HEAD
OLD_HEAD=$(git rev-parse HEAD)

# （執行 git pull origin main）

# pull 完成後，檢查新進的技能檔案是否缺跨平台支援
python3 setup/scripts/skill-platform-check.py --range "$OLD_HEAD..HEAD"
```

- 有警告 → 在 Step 4 開機摘要中加入提醒：「有 N 個技能檔案缺少 Windows 支援，需要修正」
- 無警告 → 靜默通過
- 非 Codeowner → 完全跳過此檢查（教師不需要看到此訊息）
- "Already up to date" → 跳過（沒有新 commit，不需要檢查）

**無終端機能力的 AI（Gemini 語音模式、ChatGPT 等）：**

輸出以下提醒，等待教師確認後才繼續：

> ⚠️ **開始前請先更新系統。**
> 請在終端機執行以下指令：
> ```
> cd 你的-waldorf-teacher-os-資料夾
> git pull origin main
> ```
> （Windows PowerShell 同樣適用上述指令。）
> 完成後告訴我「已更新」，我再繼續載入。

**每次開場都必須執行此步驟。** 如果教師跳過確認直接說其他指令，AI 應再次提醒：「我需要確認你的系統已更新到最新版本。請先執行 git pull origin main，或告訴我『已更新』。」

### Step 1 — 讀取 AI_HANDOFF.md

讀取 `ai-core/AI_HANDOFF.md`，取得完整的系統載入序列與技能觸發規則。

### Step 2 — 進入正常載入流程

依照 AI_HANDOFF.md 的「第一步」，依序讀取必讀檔案：

1. `ai-core/teacheros.yaml`
2. `ai-core/teacheros-foundation.yaml`
3. `ai-core/acl.yaml`
4. `{workspace}/teacheros-personal.yaml`
5. `projects/_di-framework/project.yaml`

### Step 2.5 — GWS 連線檢查（AI 自動，靜默）

若教師的 `{workspace}/teacheros-personal.yaml` 包含 `google_accounts` 區塊，且本機有 gws CLI：

```bash
gws gmail users getProfile --params '{"userId":"me"}' 2>/dev/null
```

| 結果 | 處理 |
|------|------|
| 成功（回傳 emailAddress） | 不報告，靜默通過。在 Step 4 的摘要中顯示「GWS 已連線」 |
| 401 / 失敗 | 在 Step 4 的摘要中顯示「GWS 未連線——需要時請說『設定 gws』」 |
| gws 未安裝（command not found） | 在 Step 4 的摘要中顯示「GWS 未安裝——需要時請說『設定 gws』」 |
| teacheros-personal.yaml 無 `google_accounts` | 完全跳過，不顯示任何 GWS 相關訊息 |

> 此步驟不阻擋開工流程。GWS 是選配功能，未設定的教師照常使用所有非 Google Workspace 的功能。

### Step 3 — 載入個人技能

依照 AI_HANDOFF.md 的「教師個人技能」章節：

1. 檢查 `{workspace}/personal-handoff.md` 是否存在
   - 若存在：讀取該文件，取得個人技能觸發對照表（這是個人技能的索引，相當於 AI_HANDOFF 的個人延伸層）
   - 若不存在：跳過，僅使用系統技能
2. 掃描 `{workspace}/skills/` 資料夾
3. 讀取每個 `.md` 檔的 YAML frontmatter
4. 將 `triggers` 和 `description` 暫存為觸發比對清單

### Step 4 — 報告系統狀態

輸出以下摘要：

---

**TeacherOS 已開機｜系統已更新**

**教師** [姓名]（[角色]）
**分支** [當前分支名稱]
**系統版本** [AI_HANDOFF.md 最後更新日期]
**個人技能** 已載入 [N] 個
**GWS** [已連線（email）/ 未連線 / 未設定]（僅在教師有設定 google_accounts 時顯示）

**上次工作紀錄**
（掃描 `{workspace}/projects/class-*/*/session.yaml` + `{workspace}/projects/*/session.yaml`（排除 `_di-framework`），列出最近有更新的班級科目與獨立專案，顯示 `last_updated` 與 `next_action.description`）

---

要載入哪個班級開始工作？或直接告訴我今天要做什麼。

## 注意事項

- 全程使用繁體中文
- Opening 技能完成後，若教師指定班級與科目，自然銜接 `load` 技能（不需教師再說「載入」）
- Opening 包含了 load 的前半段（必讀檔案載入），但不包含班級特定的載入（那是 load 的後半段）
- 如果教師開場就帶班級資訊（例如「開工，9C 英文」），則 Opening 完成後直接銜接 load 的班級載入部分，不重複讀取必讀檔案
- 此技能適用於所有 AI 平台（Claude Code、Gemini、ChatGPT、Cowork 等）
