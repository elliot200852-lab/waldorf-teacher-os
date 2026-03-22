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
| `git status` 顯示有未 commit 的改動 | 先提醒：「檢測到未儲存的工作。要現在存檔嗎？」等待教師回應。教師確認「要」→ 觸發 wrap-up 技能，完成後返回繼續 Step 0 的 git pull；教師說「不用」→ 跳過，直接 git pull（改動會保留在 working tree） |
| `git pull` 成功，無衝突 | 報告：「已更新至最新版本。」繼續 Step 1 |
| `git pull` 有衝突 | **停下來，不繼續載入。** 執行 `git diff --name-only --diff-filter=U` 列出衝突檔案。報告：「更新時發現以下檔案衝突：[檔案清單]。請聯繫 David 處理。」 |
| `git pull` 顯示 "Already up to date" | 報告：「已是最新版本。」繼續 Step 1 |

**git pull 成功後 — 技能跨平台檢查（僅 Codeowner）：**

若 pull 有拉進新 commit，記錄 OLD_HEAD 供後續使用：

```bash
# 在 git pull 之前先記錄當前 HEAD
OLD_HEAD=$(git rev-parse HEAD)

# （執行 git pull origin main）

# OLD_HEAD 與 HEAD 不同 → 有新 commit，記錄供 Step 2a 使用
```

- "Already up to date" → 無新 commit，Step 2a 跳過
- 有新 commit → 記錄 OLD_HEAD，Step 2a 會判斷是否執行跨平台檢查

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

### Step 2a — 技能跨平台檢查（僅 Codeowner，僅有新 commit 時）

讀完 acl.yaml 後，若當前使用者是 admin 角色且 Step 0 記錄了新 commit（OLD_HEAD != HEAD），執行：

```bash
# 跨平台 Python 偵測：先試 python3，不行再試 python
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then PYTHON_CMD="python"
fi

if [ -n "$PYTHON_CMD" ]; then
  $PYTHON_CMD setup/scripts/skill-platform-check.py --range "$OLD_HEAD..HEAD"
fi
```

```powershell
# Windows（PowerShell）
$py = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" }
      elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" }
      else { $null }
if ($py) { & $py setup/scripts/skill-platform-check.py --range "$OLD_HEAD..HEAD" }
```

| 結果 | 處理 |
|------|------|
| 有警告 | Step 4 摘要加入：「有 N 個技能檔案缺少 Windows 支援，需要修正」 |
| 無警告 | 靜默通過 |
| 非 Codeowner | 完全跳過（教師不需要看到） |
| 無新 commit | 跳過 |
| Python 未安裝 | 靜默跳過，不阻擋開工 |

### Step 2.5 — GWS 連線檢查（AI 自動，靜默，絕不阻擋開工）

**前置判斷（先檢查再呼叫，避免無謂等待）：**

1. 先執行 `command -v gws`（macOS/Linux）或 `where gws`（Windows），確認 gws 是否存在
   - 不存在 → 在 Step 4 摘要顯示「GWS 未安裝」，**直接進 Step 3**，不嘗試 npx
2. gws 存在 → 執行連線測試（見下方指令），**超時上限 5 秒**

```bash
# macOS / Linux（注意：macOS 原生無 timeout 指令，需用 Python 包裹）
if command -v gws >/dev/null 2>&1; then
  python3 -c "
import subprocess, sys
try:
    r = subprocess.run(['gws','gmail','users','getProfile','--params','{\"userId\":\"me\"}'],
                       capture_output=True, text=True, timeout=5)
    print(r.stdout)
    sys.exit(r.returncode)
except subprocess.TimeoutExpired:
    print('TIMEOUT')
    sys.exit(124)
" 2>/dev/null
fi
```

```powershell
# Windows（PowerShell）
if (Get-Command gws -ErrorAction SilentlyContinue) {
  try {
    $job = Start-Job -ScriptBlock { gws gmail users getProfile --params '{\"userId\":\"me\"}' 2>&1 }
    $result = Wait-Job -Job $job -Timeout 5
    if ($result) { Receive-Job -Job $job } else { Write-Output 'TIMEOUT' }
    Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
  } catch { Write-Output 'GWS_ERROR' }
}
```

| 結果 | 處理 |
|------|------|
| 成功（回傳 emailAddress） | 靜默通過。Step 4 摘要顯示「GWS 已連線（email）」 |
| 401 / 失敗 | Step 4 摘要顯示「GWS 未連線——需要時請說『設定 gws』」 |
| gws 未安裝（command not found） | Step 4 摘要顯示「GWS 未安裝——需要時請說『設定 gws』」 |
| 超時（> 5 秒無回應） | Step 4 摘要顯示「GWS 檢查逾時——需要時請說『設定 gws』」 |

> **此步驟絕對不阻擋開工流程。** 任何結果（包含錯誤、超時、未安裝）都只記錄到 Step 4 摘要，不中斷載入。AI 在此步驟遇到任何異常，一律靜默跳過繼續。

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
**Obsidian** [檢查 `.claude/.last-obsidian-check` 是否存在。存在 → 靜默通過。不存在 → 摘要加一行「上次收工未執行 Obsidian 檢查，建議本次收工時補跑」]

**上次工作紀錄**
（掃描 `{workspace}/projects/class-*/*/session.yaml` + `{workspace}/projects/*/session.yaml`，排除 `_di-framework` 與 `phase: 已結案` 的工作線。依 `last_updated` 由新到舊排序。顯示 `last_updated`、`next_action.description`。若 session.yaml 中有 `current_focus` 或 `open_questions`，一併顯示。）

---

要載入哪個班級開始工作？或直接告訴我今天要做什麼。

## 平行化指引（有能力的 AI Agent 適用）

以下步驟之間**沒有依賴關係**，AI Agent 可自行判斷並行執行以加速開機：

```
Phase A（可並行）：
  - 讀取 AI_HANDOFF.md、teacheros.yaml、teacheros-foundation.yaml、acl.yaml
  - GWS 連線檢查（Step 2.5，背景執行，不阻擋）

Phase B（序列，需要 Phase A 的 acl.yaml 結果）：
  - 解析 workspace 路徑
  - 讀取 {workspace}/teacheros-personal.yaml
  - 讀取 projects/_di-framework/project.yaml
  - 執行 Step 2a（若符合條件）

Phase C（可並行）：
  - 掃描個人技能 frontmatter（Step 3）
  - 掃描所有 session.yaml 進度（Step 4 資料來源）

Phase D（純輸出）：
  - 彙整報告（Step 4）
```

此指引為**授權性質**——AI Agent 有能力平行化時可自行採用，無此能力時按原順序序列執行亦可。不改變技能的正確性。

## 注意事項

- 全程使用繁體中文
- Opening 技能完成後，若教師指定班級與科目，自然銜接 `load` 技能（不需教師再說「載入」）
- Opening 包含了 load 的前半段（必讀檔案載入），但不包含班級特定的載入（那是 load 的後半段）
- 如果教師開場就帶班級資訊（例如「開工，9C 英文」），則 Opening 完成後直接銜接 load 的班級載入部分，不重複讀取必讀檔案
- 此技能適用於所有 AI 平台（Claude Code、Gemini、ChatGPT、Cowork 等）
