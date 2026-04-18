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

### Step 0 — 確保 Repo 為最新版本（v2.0 分支模型）

**設計目標：** 老師開工時要能拉到主系統的更新（ai-core/ / setup/ / projects/_di-framework / 共用技能等），但不要干擾或拉取其他老師個人分支的未合併進度。

**原理：** main 分支只存放已被 PR 合併的內容。老師在 `workspace/Teacher_xxx` 分支上工作時，把 main 合併進來，就能拿到系統更新，而**不會**拿到其他老師未合併的備課進度。

---

**有終端機能力的 AI（Claude Code、Cowork 等）：**

依序執行：

```bash
# 1. 確認當前分支
current_branch=$(git branch --show-current)

# 2. 檢查是否有未 commit 的改動
git status --short
```

**若有未 commit 的改動** → 先提醒：「你有未儲存的工作，要先存檔嗎？」若教師同意，觸發 `wrap-up` 技能，存完再繼續；若教師說不，AI 評估 merge 是否會衝突，若可能衝突就阻擋。

```bash
# 3. 只抓 main 的更新（不拉其他老師的分支 ref）
git fetch origin main
```

**先判斷教師身份**（從 Step 1.5 解析的 acl.yaml 結果取得 `is_admin`），再依**分支 × 身份**分流：

| 教師身份 | current_branch | 處理 |
|---------|---------------|------|
| **admin** | `main` | 執行 `git pull --ff-only origin main`。 |
| **admin** | `workspace/*` 或其他 | 提示「你目前在 `{分支名}`，admin 允許」，執行 `git fetch origin "$current_branch"` + `git pull --ff-only origin "$current_branch"`，再 `git merge origin/main --no-edit`。 |
| **老師** | `workspace/Teacher_{自己}` | 先同步自己分支：`git fetch origin "$current_branch" 2>/dev/null \|\| true` 然後 `git pull --ff-only origin "$current_branch" 2>/dev/null \|\| true`（若 remote 還沒有此分支就略過）。**接著合併系統更新**：`git merge origin/main --no-edit`。 |
| **老師** | `main` | **停下來**，報告：「你目前在 `main` 分支上，但教師應該在自己的 `workspace/Teacher_{姓名}` 分支工作。pre-commit hook 會擋你的 commit；建議現在就切回：`git switch workspace/Teacher_{姓名}`。要我幫你切嗎？」**不要**執行 `git pull origin main`（會把已 push 給 main 的內容拉進老師本機 main，但老師沒有 push main 的權限，後續會卡住）。 |
| **老師** | 其他（含 `workspace/Teacher_{別人}`） | **停下來**，報告：「你目前在 `{分支名}` 上，不是你的個人分支。要我幫你切回 `workspace/Teacher_{你的姓名}` 嗎？」 |

判斷結果：

| 狀況 | 處理 |
|------|------|
| 全部成功 / "Already up to date" | 報告：「已是最新版本，系統更新已拉取。」繼續 Step 1 |
| merge origin/main 有衝突 | **停下來，不繼續載入。** 報告：「合併系統更新時發生衝突。」列出衝突檔案清單，建議請教師聯繫 David |
| fetch 失敗（網路問題） | 報告：「無法連線 GitHub，改用本地現有版本繼續。」繼續 Step 1（降級） |

---

**無終端機能力的 AI（Gemini 語音模式、ChatGPT 等）：**

輸出以下提醒，等待教師確認後才繼續：

> ⚠️ **開始前請先更新系統。**
> 請在終端機執行以下指令（**老師在個人分支上**）：
> ```
> cd 你的-waldorf-teacher-os-資料夾
> git fetch origin main
> git merge origin/main --no-edit
> ```
> 若你是 David（在 main 分支），改執行 `git pull origin main`。
> 完成後告訴我「已更新」，我再繼續載入。

**每次開場都必須執行此步驟。** 如果教師跳過確認直接說其他指令，AI 應再次提醒：「我需要確認你的系統已更新到最新版本。請執行上面兩行指令，或告訴我『已更新』。」

---

**為什麼這樣做？**

- `git fetch origin main`（非 `--all`）：只抓 main 的更新，不下載其他老師分支的 ref，老師的 `git branch -r` 清單保持乾淨
- `git merge origin/main --no-edit`：把已審核合併進 main 的所有變更（系統層 + 已合併 PR）拉進老師個人分支；其他老師未 PR 的工作不在 main 裡，自然不會被拉進來
- 想看別人工作的老師仍可手動執行 `git fetch --all` + `git branch -r`（reclone guide Part C 第二部分有教）

### Step 1 — 讀取 AI_HANDOFF.md

讀取 `ai-core/AI_HANDOFF.md`，取得完整的系統載入序列與技能觸發規則。

### Step 1.5 — 確認教師身份（所有 AI 必須執行）

**在載入任何 workspace 檔案之前，必須先確認「現在的教師是誰」。**
`{workspace}` 路徑取決於此步驟的結果。若跳過此步驟，後續載入可能指向錯誤的 workspace。

**解析順序（依序嘗試，命中即停）：**

**方法 1 — 讀取 `setup/environment.env`**

讀取檔案，取得 `USER_EMAIL`。若存在且非空 → 用該 email 查 `ai-core/acl.yaml` → 取得 workspace 路徑。成功 → 跳到 Step 2。

若檔案不存在（新教師尚未執行安裝腳本）→ 繼續方法 2。

**方法 2 — 讀取 `.git/config` 檔案**（純文字讀取，不需終端機）

讀取 Repo 根目錄的 `.git/config`，找 `[user]` 區段下的 `email = xxx` 行。

- 用該 email 查 `ai-core/acl.yaml` 的 `email` 欄位
- 若為 GitHub noreply 格式（`username@users.noreply.github.com` 或 `數字+username@users.noreply.github.com`），提取 username，比對 `acl.yaml` 的 `github_username` 欄位
- 命中 → 取得 workspace 路徑 → 跳到 Step 2
- 未命中 → 繼續方法 3

**此方法對 Antigravity / Gemini 等無終端機的 AI 特別重要——它們無法執行 `git config` 指令，但可以直接讀取 `.git/config` 檔案。**

**方法 3 — 掃描 `workspaces/Working_Member/*/env-preset.env`**

掃描所有教師的 `env-preset.env`：

- 若整個 `Working_Member/` 下只有一個教師 workspace 含 `env-preset.env` → 直接使用（單一教師的 clone）
- 若有多個 → 繼續方法 4

**方法 4 — 直接詢問教師**

從 `ai-core/acl.yaml` 列出所有教師姓名：

> 我無法自動辨識你的身份。請確認你是誰：
> 1. [教師姓名 1]
> 2. [教師姓名 2]
> ...

教師選擇後 → 取得對應的 workspace 路徑。

若教師不在清單中 → 「你的帳號尚未註冊。請聯繫 David 設定 workspace。」→ **停止載入。**

**確認後：** 將 workspace 路徑暫存，後續 Step 2-4 的 `{workspace}` 皆使用此值。

### Step 2 — 進入正常載入流程

依照 AI_HANDOFF.md 的「第一步」，依序讀取必讀檔案：

1. `ai-core/teacheros.yaml`
2. `ai-core/teacheros-foundation.yaml`
3. `ai-core/acl.yaml`（Step 1.5 已讀取，不重複）
4. `{workspace}/teacheros-personal.yaml`
5. `projects/_di-framework/project.yaml`

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

**上次工作紀錄**
（掃描 `{workspace}/projects/class-*/*/session.yaml`，列出最近有更新的班級與科目，顯示 `last_updated` 與 `next_action.description`）

---

要載入哪個班級開始工作？或直接告訴我今天要做什麼。

## 注意事項

- 全程使用繁體中文
- Opening 技能完成後，若教師指定班級與科目，自然銜接 `load` 技能（不需教師再說「載入」）
- Opening 包含了 load 的前半段（必讀檔案載入），但不包含班級特定的載入（那是 load 的後半段）
- 如果教師開場就帶班級資訊（例如「開工，9C 英文」），則 Opening 完成後直接銜接 load 的班級載入部分，不重複讀取必讀檔案
- 此技能適用於所有 AI 平台（Claude Code、Gemini、ChatGPT、Cowork 等）
