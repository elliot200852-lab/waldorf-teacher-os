---
name: add-teacher
description: >
  管理員專用。互動式建立新教師 Workspace：收集資訊、建立目錄與模板、更新 ACL 權限、建立 Git 分支、
  連接 Google Workspace 服務。完成後產出新教師的下一步清單。
triggers:
  - 加入新老師
  - 新增老師
  - 新增教師
  - 建立新 workspace
  - add teacher
  - onboard teacher
requires_args: false
args_format: "[選填：老師姓名 email GitHub帳號] (可一次提供或逐步輸入)"
admin_only: true
author: David
created: 2026-03-09
---

# skill: add-teacher — 加入新老師（管理員專用）

互動式建立新教師的 Workspace、ACL 權限與 Git 分支。
取代 `setup/add-teacher.py`（或舊版 `add-teacher.sh`）的手動流程，改由 AI 對話引導完成。

## 權限

此技能僅限 admin 角色使用。Step 0 會驗證身份。

## 參數

選填。David 可一次提供所有資訊（例如「加入新老師 王美玲 mei@school.tw wangml」），
AI 從語句中解析已知欄位，再補問缺失的必填欄位。

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：`git rev-parse --show-toplevel`。

## 讀取的檔案

| 檔案 | 用途 |
|------|------|
| `ai-core/acl.yaml` | 權限驗證 + 重複檢查 + 寫入新條目 |
| `workspaces/_template/teacheros-personal.yaml` | 複製為新教師的身份模板 |
| `workspaces/_template/workspace.yaml` | 複製並填入已知欄位 |
| `workspaces/_template/README.md` | 複製為新教師的快速指南 |
| `workspaces/_template/skills/*` | 複製個人技能範例 |
| `workspaces/_template/projects/_class-template/` | 班級資料夾骨架（若需建班級） |

---

## 執行步驟

### Step 0 — 權限驗證

1. 讀取 `ai-core/acl.yaml`
2. 確認當前操作者在 `roles.admin` 清單中（比對 MEMORY.md 使用者身份或 git config user.email）
3. 非 admin → **終止**，輸出：「此技能僅限管理員使用。」

---

### Step 1 — 告知必要欄位，收集教師資訊

向 David 顯示以下欄位清單：

---

**建立新教師 Workspace 需要以下資訊：**

**必填：**
- 姓名（中文）
- Email（將用於 ACL 比對，須與教師的 environment.env USER_EMAIL 一致）
- GitHub 帳號

**選填（可之後再設定）：**
- 職稱/角色（例：八年級英文科任教師）
- 班級代碼（例：8a、9c）——若提供，會一併建立班級資料夾
- 主要科目（例：英文、數學）

請提供資訊，可以一次說完或逐步提供。

---

**解析邏輯：**
- 從 David 的口語中提取所有可識別的欄位
- 已提供的欄位直接填入，未提供的必填欄位逐一補問
- 選填欄位若未提供，不追問，使用預設值或留空

**自動產生的值：**
- `teacher_id`：從中文姓名產生拼音（例：王美玲 → wang-mei-ling），依現有慣例
- `workspace_folder`：`Teacher_{中文姓名}`（例：`Teacher_王美玲`）
- 若 David 想自訂 workspace_folder 名稱，允許覆寫

---

### Step 2 — 確認資訊

整理並向 David 確認：

---

**即將建立以下教師 Workspace：**

| 項目 | 值 |
|------|-----|
| 姓名 | {name} |
| Email | {email} |
| GitHub | {github_username} |
| 職稱 | {role / 未提供} |
| Workspace | `workspaces/Working_Member/Teacher_{name}/` |
| 班級 | {class_code / 無，之後再建} |
| 科目 | {subject / 未提供} |

確認後開始建立？

---

等待 David 確認。若需修改，回到 Step 1 修正。

---

### Step 3 — 冪等性檢查

在建立之前，逐一檢查：

| 檢查項目 | 若已存在 | 處理方式 |
|---------|---------|---------|
| `workspaces/Working_Member/Teacher_{name}/` | 目錄已存在 | 詢問：「Workspace 目錄已存在。要補齊缺失檔案（不覆蓋已有的），還是跳過此步驟？」 |
| email 已在 acl.yaml teachers 清單中 | 重複 email | 詢問：「此 email 已註冊給 {existing_name}。要更新該筆記錄，還是取消？」 |
| `workspace/Teacher_{name}` branch | branch 已存在 | 報告：「Git 分支已存在，跳過建立。」 |
| GitHub Collaborator | 已是 collaborator | 報告：「{github_username} 已是 Collaborator，跳過邀請。」 |
| `projects/class-{code}/` | class 目錄已存在 | 報告：「班級資料夾已存在，直接使用。」 |

---

### Step 4 — 建立 Workspace 目錄與檔案

**4a. 建立目錄結構**

```
workspaces/Working_Member/Teacher_{name}/
├── teacheros-personal.yaml  ← 從 _template 複製
├── workspace.yaml           ← 從 _template 複製並填入已知資訊
├── env-preset.env           ← 自動產生，必填欄位已預填
├── README.md                ← 從 _template 複製
├── skills/                  ← 從 _template/skills/ 複製（含範例）
└── projects/
    └── .gitkeep
```

**4b. 填入 workspace.yaml 已知欄位**

讀取模板 `workspaces/_template/workspace.yaml`，將佔位符替換為實際值：

- `teacher_identity.name` → {name}
- `teacher_identity.teacher_id` → {teacher_id}
- `teacher_identity.role` → {role 或留模板預設}
- `teacher_identity.email` → {email}
- `workspace_status` → active
- `created_date` → {今天日期 YYYY-MM-DD}

**4c. 產生 env-preset.env（環境預填檔）**

在 workspace 根目錄建立 `env-preset.env`，包含從 Step 1 收集到的必填欄位：

```
USER_NAME={name}
USER_EMAIL={email}
WORKSPACE_ID=Teacher_{name}
GITHUB_USERNAME={github_username}
```

此檔案被追蹤（commit 到 main），不含機密資訊（所有欄位已在 acl.yaml 中公開）。
教師執行 `bash setup/start.sh`（或 Windows 的 `.\setup\start.ps1`）時，系統自動比對 `git config user.email`，
找到匹配的 preset 後複製為 `setup/environment.env`，免去手動填寫。

**4d. 預填 teacheros-personal.yaml（可選）**

若 David 在 Step 1 有口述新教師的背景（教學科目、年級、角色等），
將這些資訊填入 teacheros-personal.yaml 的對應欄位：

| 若 David 說了 | 填入欄位 |
|-------------|---------|
| 科目 | `teaching_scope.subjects` |
| 年級 | `teaching_scope.grade_focus` |
| 職稱 | `teacher_identity.role` |

主觀欄位（教學信念 `my_belief`、工作風格 `working_style`）保留「填空」佔位符，
由教師本人日後填寫。

若 David 未口述任何背景，保留原始模板不動。

**4e. 自動填入 google_accounts 區塊（必做）**

模板中的 `google_accounts` 區塊使用 `{USER_EMAIL}` 佔位符。
建立 teacheros-personal.yaml 時，**一律自動將 `{USER_EMAIL}` 替換為教師的 email**
（即 Step 1 收集的 email，與 acl.yaml 中的 email 相同）。

不需要額外詢問教師的 Google 帳號——直接使用已收集的 email。

替換範圍：
- `google_accounts.default`
- `google_accounts.accounts[0].email`

若教師日後有多個 Google 帳號，可自行在 teacheros-personal.yaml 中新增 accounts 條目。

---

### Step 5 — 更新 ACL

讀取 `ai-core/acl.yaml`，在 `roles.teachers` 清單尾部附加新條目：

```yaml
    - name: {name}
      email: {email}
      github_username: {github_username}
      workspace: workspaces/Working_Member/Teacher_{name}/
      allowed_paths:
        - workspaces/Working_Member/Teacher_{name}/
      blocked_paths:
        - ai-core/
        - setup/
        - .github/
        - publish/build.sh
```

若 Step 1 有提供 class_code 且 workspace 下已建立班級資料夾：
- **不需要**在 allowed_paths 追加 `projects/class-{code}/`
  （班級資料夾位於教師 workspace 內，已被 workspace 路徑涵蓋）

若 Step 3 檢查發現 email 已存在且 David 選擇更新，
用 Edit 工具修改既有條目而非新增。

---

### Step 6 — 建立班級資料夾（若有 class_code）

若 Step 1 有提供 class_code：

1. 在新教師的 workspace 下建立：
   `workspaces/Working_Member/Teacher_{name}/projects/class-{class_code}/`
2. 從 `workspaces/_template/projects/_class-template/` 複製完整骨架
3. 填入 `project.yaml` 的基本資訊（class_code、subject、teacher_id、日期）

若有多個 class_code（David 可能說「他帶 9A 和 9B」），逐一建立。

若 class_code 未提供，跳過此步驟。

---

### Step 7 — Git 操作

**7a. 本地 commit + push**

```bash
# 1. 在 main 上 commit（admin 權限，ACL 需在 main 上才能生效）
git add workspaces/Working_Member/Teacher_{name}/
git add ai-core/acl.yaml
git commit -m "新增教師 {name} 的 Workspace 與 ACL 權限"
git push origin main

# 2. 建立教師個人分支供日後使用
git checkout -b workspace/Teacher_{name}
git push -u origin workspace/Teacher_{name}

# 3. 回到 main
git checkout main
```

若 branch 已存在（Step 3 檢查結果），跳過 branch 建立。

**7b. GitHub Collaborator 邀請**

將新教師加為 GitHub Repo 的 Collaborator（Write 權限），使其可以 push 到自己的 branch。

```bash
gh api repos/{owner}/{repo}/collaborators/{github_username} \
  -X PUT -f permission=write
```

- `{owner}/{repo}` 從 `git remote get-url origin` 自動解析
- 每位教師各執行一次
- 成功回應：HTTP 201（新邀請）或 204（已是 collaborator）
- 邀請發出後，教師需在 GitHub 上接受邀請（會收到 email 通知）

**冪等性**：若教師已是 collaborator，API 回傳 204，不影響現有權限。

---

### Step 8 — 確認個人需求

分兩部分詢問 David：

**8a. 班級與工作設定**
1. 需要建立更多班級嗎？
2. 新教師有沒有想馬上開始做的工作？
   （例如「他想從學季規劃開始」→ 告知對應技能觸發語 `/syllabus`）
3. 新教師主要用哪個 AI 工具？
   - Claude Code → 提醒跑 `bash setup/start.sh`（Mac）或 `.\setup\start.ps1`（Windows）
   - 其他平台 → 提醒讀取 `ai-core/AI_HANDOFF.md`

**8b. Google Workspace 連接**

核心是 **gws CLI**（`@googleworkspace/cli`）——一次授權即連接所有 Google Workspace 服務
（Drive、Calendar、Gmail、Sheets、Docs 等）。

詢問 David：
- 新教師是否要現在就設定 gws？
- 若要，確認新教師的 Google 帳號（填入 environment.env）

設定步驟（整合進 Step 9 的下一步清單）：
1. 安裝 gws CLI：`npm install -g @googleworkspace/cli`
2. 授權登入：`gws auth login`（瀏覽器開啟 Google 登入，一次授權涵蓋所有服務）
3. 若需要 Google Drive Desktop 本機同步，另行安裝

若 David 說暫時不需要，在清單中標記為「選用」。

---

### Step 9 — 輸出摘要與下一步清單

**9a. 建立完成摘要**

---

**新教師 Workspace 建立完成**

| 項目 | 狀態 |
|------|------|
| Workspace 目錄 | `workspaces/Working_Member/Teacher_{name}/` |
| 環境預填檔 | `env-preset.env` 已建立（start.sh / start.ps1 自動偵測） |
| ACL 權限 | 已更新 `ai-core/acl.yaml` |
| Git 分支 | `workspace/Teacher_{name}` |
| GitHub 權限 | Collaborator 邀請已發送（Write） |
| 班級資料夾 | {class-{code} 已建立 / 無} |
| Git 存檔 | {commit hash} 已推送 |

---

**9b. 產出新教師下一步清單**

以下清單可直接複製傳給新教師：

---

歡迎加入 TeacherOS！以下是你的專屬設定步驟：

**1. 取得專案**
```
git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git
cd waldorf-teacher-os
```

**2. 執行環境安裝**

Mac / Linux：
```
bash setup/start.sh
```

Windows（PowerShell）：
```
.\setup\start.ps1
```

**3. 確認個人設定**
安裝腳本會自動偵測你的 `env-preset.env` 並建立 `setup/environment.env`，
必填欄位（姓名、Email、Workspace ID、GitHub 帳號）已由管理員預先填好。
若需補充 Google Drive 等選填設定，可之後編輯 `setup/environment.env`。

**4. 連接 Google Workspace（選用，所有 Google 服務一次設定）**
```
npm install -g @googleworkspace/cli
gws auth login
```
瀏覽器會開啟 Google 登入頁面，授權後即可使用 Drive、Calendar、Gmail、Sheets、Docs 等服務。

**5. 安裝 Google Drive Desktop（選用，用於本機同步）**
下載安裝：https://www.google.com/drive/download/

**6. 開始使用**
對 AI 說「開工」，系統會自動載入你的 Workspace。

**7. 填寫你的教學哲學**
編輯 `workspaces/Working_Member/Teacher_{name}/teacheros-personal.yaml`
這是你的教學身份檔案，AI 會根據這份文件理解你的教學風格與偏好。

你的個人分支：`workspace/Teacher_{name}`
你的 Workspace：`workspaces/Working_Member/Teacher_{name}/`

有任何問題聯繫 David。

---

## 注意事項

### 優雅降級

每步失敗時報告問題後繼續下一步，不中斷整體流程。

| 步驟 | 可能失敗 | 降級處理 |
|------|---------|---------|
| Step 4 建立目錄 | 權限不足、磁碟滿 | 報告錯誤，繼續 Step 5 |
| Step 5 更新 ACL | acl.yaml 語法問題 | 報告錯誤，建議手動修改，繼續 Step 7 |
| Step 6 班級資料夾 | 模板缺失 | 報告缺失的模板檔案，建空目錄，繼續 |
| Step 7a Git 操作 | push 失敗 | 嘗試 `git pull --rebase` 後重試，仍失敗則報告 |
| Step 7b Collaborator 邀請 | gh API 失敗、帳號不存在 | 報告失敗的帳號，列出手動邀請指令，繼續 Step 8 |

### 冪等性保證

- 目錄已存在 → 只補齊缺失檔案（不覆蓋已有的）
- ACL 條目已存在 → 更新而非重複新增
- Branch 已存在 → 跳過建立
- Collaborator 已存在 → API 回傳 204，無副作用
- Class folder 已存在 → 跳過建立

### 與 add-teacher.py / add-teacher.sh 的關係

- **共存**，不刪除腳本（Python 版 `add-teacher.py` 為跨平台主版本，Shell 版 `add-teacher.sh` 為備用）
- 技能比腳本多了：預填 teacheros-personal.yaml、確認個人需求、Google Workspace 連接指引、產出新教師通知清單
- 技能使用 AI 的 Read/Write/Edit/Bash 工具完成操作
