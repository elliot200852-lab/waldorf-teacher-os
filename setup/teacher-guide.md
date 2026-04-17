---
aliases:
  - "TeacherOS 教師使用手冊"
  - "Teacher Guide V2.6"
version: "2.6"
updated: 2026-04-17
audience: 慈心華德福全體合作教師
tags:
  - type/onboarding
  - type/reference
---

# TeacherOS｜華德福教師 AI 共創系統 使用手冊

**版本：2.6（對齊 TeacherOS v2.0 乾淨起點）**
**最後更新：2026-04-17**

---

## 這份指南在講什麼

TeacherOS 是一套讓 AI 協助教師完成備課的工作系統。你不用懂程式，只要用說話或打字的方式，跟 AI 一起完成四個主要區塊（Block 1-4）。

這份指南是**日常使用手冊**，適合：

- **新加入的老師**：從零開始設定你的工作環境
- **既有老師**：要回頭查某個流程、或想多了解系統結構
- **任何時候卡住**：參考「遇到問題時」章節

> **如果你是既有老師、要做 v2.0 的一次性重裝**，請改看：
> `setup/teacher-reclone-guide-2026-04.md`
> 那一份是專門寫給「舊資料夾要換新」的老師，跟完不必再跟這份。

---

## 一、四個工作區塊

| Block | 工作內容 | 觸發方式 |
|-------|----------|----------|
| Block 1 | 學季教學大綱（目標、策略、評量） | 「開始 7C 英文課學季大綱」 |
| Block 2 | 每堂課的 45 分鐘流程 + A/B/C/D 差異化任務 | 「設計 7C 英文第 2 單元」 |
| Block 3 | 課後教學歷程紀錄（自動拆解學生動態） | 「記錄今天 7C 英文課發生的事」 |
| Block 4 | 學期末質性評量報告 | 「9C 英文這學期做評量」 |

想看成品長什麼樣子，進入 `workspaces/工作範例參考/`。

---

## 二、首次安裝（新老師）

### Step 1. 申請 GitHub 帳號並聯絡 David

1. 到 [github.com](https://github.com) 免費註冊
2. 把你的 GitHub 帳號名稱與 Email 傳給 David
3. David 會把你加入專案、建立你的個人分支 `workspace/Teacher_你的姓名`

### Step 2. 安裝 Git 與 GitHub CLI

**Mac：**

```bash
# 安裝 Homebrew（若尚未安裝）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# 安裝 git 與 GitHub CLI
brew install git gh
# 登入 GitHub
gh auth login
```

**Windows：**

```powershell
# 安裝 Git
winget install --id Git.Git -e --source winget
# 安裝 GitHub CLI
winget install --id GitHub.cli -e --source winget
# 登入 GitHub
gh auth login
```

`gh auth login` 的選擇：GitHub.com → HTTPS → Yes → Login with a web browser。

### Step 3. 下載 TeacherOS

**Mac（終端機）：**

```bash
cd ~/Desktop
git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git WaldorfTeacherOS-Repo
cd WaldorfTeacherOS-Repo
```

**Windows（PowerShell）：**

```powershell
cd $HOME\Desktop
git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git WaldorfTeacherOS-Repo
cd WaldorfTeacherOS-Repo
```

### Step 4. 切換到你的個人分支

```
git checkout workspace/Teacher_你的姓名
git branch --show-current
```

第二行應該印出 `workspace/Teacher_你的姓名`，代表你在對的位置。

### Step 5. 執行一鍵安裝精靈

**Mac：**

```bash
bash setup/start.sh
```

**Windows：**

```powershell
.\setup\start.ps1
```

> 若 Windows 出現 `此系統上已停用指令碼執行`，先貼一次這行：
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

精靈會自動完成 9 個檢查，包含：Git / Pandoc / Pre-commit Hook / `environment.env` / Git 身份同步 / 個人分支確認 / Claude Code Hook。看到 `技術安裝完成！` 就完成了。

> Google Drive / Email / Calendar 等 gws 功能**完全選用**。精靈不會自動安裝，需要的老師請看「八、選配：Google Workspace CLI」。

---

## 三、認識你的工作空間

### 系統結構（只需要管你自己的部分）

```
WaldorfTeacherOS-Repo/
├── ai-core/                              ← 系統核心（所有人共用，不要改）
│   ├── teacheros.yaml                    ← 系統路由
│   ├── teacheros-foundation.yaml         ← 華德福共用根基
│   ├── acl.yaml                          ← 授權表（David 維護）
│   ├── AI_HANDOFF.md                     ← AI 每次必讀
│   ├── skills/                           ← 技能正本（所有 AI 共用）
│   └── reference/                        ← 科目深度參考
│
├── projects/_di-framework/               ← 差異化教學共用框架
│
├── workspaces/
│   ├── 工作範例參考/                     ← 完整範例，可看不可改
│   └── Working_Member/
│       └── Teacher_你的姓名/             ← ⭐ 這是你的領土
│           ├── teacheros-personal.yaml   ← 你的身份卡
│           ├── workspace.yaml            ← 工作狀態
│           ├── skills/                   ← 個人技能
│           └── projects/
│               └── class-7c/             ← 班級資料夾
│                   ├── project.yaml
│                   ├── students.yaml
│                   ├── english/
│                   │   └── session.yaml
│                   └── ...
│
├── setup/                                ← 設定工具（本資料夾）
└── publish/                              ← Markdown → Docx → Drive 輸出管線
```

### 你的書桌：`workspaces/Working_Member/Teacher_你的姓名/`

這個資料夾 100% 屬於你，AI 只會在此範圍內寫入。

### 其他老師的工作你可以「讀」但不能「改」

`git branch -r` 或問 AI「幫我看 xx 老師最近做了什麼」即可查閱，互不干擾。

---

## 四、建立個人身份與班級

### 個人身份（一次性）

打開 `workspaces/Working_Member/Teacher_你的姓名/teacheros-personal.yaml`，填寫：

- `teacher_identity`：姓名、Email、學校
- `teaching_scope`：年級、科目
- `subject_philosophies`：你對各科目的個人教學信念
- `voice_anchor`：你希望 AI 用什麼語氣跟你協作

不會填？直接對 AI 說：「幫我草擬 `teacheros-personal.yaml`，我教七年級英文，重視溝通與創意。」AI 會起草，你再微調。

### 新增班級

對 AI 說：「幫我建立 7C 班級資料夾，有 28 位學生。」AI 會：

1. 從 `projects/_class-template/` 複製骨架到你的 workspace
2. 填好 `project.yaml`、空白 `students.yaml`、各科目 `session.yaml`
3. 提醒你之後補學生名單

### 學生 A/B/C/D 分類

TeacherOS 使用「能力 × 動機」雙軸矩陣：

| 類別 | 能力 | 動機 | 教學方向 |
|------|------|------|---------|
| A | 高 | 高 | 延伸挑戰、自主探究、引導同儕 |
| B | 低 | 高 | 鷹架支持、小步驟成功經驗、建立自信 |
| C | 高 | 低 | 提升意義感、連結個人興趣、減少無效重複 |
| D | 低 | 低 | 降低焦慮、建立安全感、從具體操作切入 |

**重要**：分類只存在於 `students.yaml` 與 AI 對話中，學生看不到。這是教師的觀察工具，不是學生標籤。

詳細判斷指引：`projects/_di-framework/content/di-classification-guide.md`

---

## 五、每次使用的流程（日常三指令）

### 開場：「開工」

每次打開 AI 對話，第一句話說「開工」或「開工，9C 英文課」。

AI 會：

1. 自動執行 `git pull`（不用你動手）
2. 確認你站在自己的 `workspace/Teacher_xxx` 分支上
3. 載入系統脈絡與你的 workspace
4. 報告你上次做到哪裡、下一步是什麼

### 進行：自然對話

跟 AI 說你要做什麼：

- 「設計 7C 英文第 2 單元」
- 「記錄今天 7C 英文課的事」
- 「產出 9C 英文期末評量報告」

AI 會自動載入對應技能，按 Block 結構產出。

### 收尾：「收工」

一天結束時，對 AI 說「收工」（或「存檔」「備份」）。

AI 會：

1. 執行 `git status` 確認你改了哪些檔案
2. **只 add 你 workspace 內的檔案**（不動別人、不動共用目錄）
3. 寫一句中文 commit 訊息
4. 推送到你的個人分支

> **不要自己下 `git add .` 或 `git commit`。** 讓 AI 做，它會做安全檢查。
> 如果 AI 想用 `git add -A`、`--force` 或 `--no-verify`，**請你立刻喊停**，要它重做。

### 對話中的方向校正

- 「回到中軸」→ AI 重新定位，告知當前步驟
- 「我要繼續上次 7C 的工作」→ 載入對應 session.yaml

---

## 六、進 Block 2 之前：準備素材

啟動 Block 1 或 Block 2 之前，強烈建議：

1. 你自己先做主題研究（閱讀、文本分析、蒐集素材）
2. 把筆記整理成 1-2 份 Markdown
3. 對話開始時把這份素材丟給 AI 當基礎

AI 會以你的研究為錨點設計課程，而不是從零憑空生成。沒素材時 AI 會要你補，或要你明確授權它在無基礎下進行。

---

## 七、文件輸出到 Google Drive

AI 完成一份文件（例如 Block 1 大綱）後會問你：

> 「這份要輸出到 Google Drive 嗎？」

回答「要」之後：

- **Claude Code / Cowork 老師**：AI 自動執行 `publish/build.sh`，經 Pandoc 轉成 `.docx`，上傳到你 Drive 的對應資料夾
- **ChatGPT / Gemini 老師**：AI 提供格式化文字，你複製貼到 Google Docs

Pandoc 沒裝？安裝精靈會提醒你。Mac 用 `brew install pandoc`，Windows 從 [pandoc.org/installing.html](https://pandoc.org/installing.html) 下載。

---

## 八、選配：Google Workspace CLI（gws）

想讓 AI 直接操作你的 Google Drive / Calendar / Gmail？你需要**自行**安裝並設定 gws。

**這是選配功能。TeacherOS v2.0 之後不再統一安裝或管理 gws。** 每位老師用自己的 Google 帳號建立獨立的 OAuth 專案，David 看不到也不會碰你的資料。

簡要步驟：

```bash
# 安裝 Node.js LTS：https://nodejs.org
npm install -g @googleworkspace/cli
gws auth setup    # 建立你自己的 GCP OAuth 專案
gws auth login    # 瀏覽器登入
```

完整步驟請看 `ai-core/reference/gws-cli-guide.md`，或把這份指南 + `gws-cli-guide.md` 丟給 AI 並說：「教我設定 gws。」

不用 Drive / Email / Calendar 自動化的老師可跳過本章，完全不影響備課。

---

## 九、權限與安全：三層保護

| 層級 | 位置 | 作用 |
|------|------|------|
| AI 層 | 每次對話 | AI 讀取你的身份（`environment.env`），只在授權範圍內操作 |
| Git 層 | 每次 commit | Pre-commit Hook 攔截超出授權的檔案變更 |
| GitHub 層 | Pull Request | David 手動審核才能合併進 main |

### 你只會動到兩個地方

- `workspaces/Working_Member/Teacher_你的姓名/`（你的 workspace）
- 你自己的 `workspace/Teacher_你的姓名` 分支

### 如果 Hook 攔截了 commit

通常是 AI 不小心想 add 別人的檔案。把終端機畫面整段貼給 AI，它會自己排除。

---

## 十、個人技能（Personal Skills）

系統內建了大量技能（`/opening`、`/lesson`、`/syllabus` 等），放在 `ai-core/skills/`。你也可以在 `workspaces/Working_Member/Teacher_你的姓名/skills/` 建立**個人技能**，把你自己的固定工作流程教給 AI。

最小範本：

```yaml
---
name: recitation
description: 設計朗讀教學活動
triggers:
  - 朗讀教學
  - 設計朗讀
  - recitation
requires_args: false
---

# recitation — 朗讀教學設計

## 執行步驟
1. ...
2. ...
```

frontmatter 之後用 Markdown 寫步驟即可。完整範本：`workspaces/_template/skills/EXAMPLE-recitation.md`。

**個人技能與系統技能同名時**，AI 在你的 session 內優先使用個人版，並主動告訴你。想切回系統版說「用系統的 [技能名]」即可。

---

## 十一、學期末：合併回主系統

日常工作都存在你自己的個人分支，不會自動進 main。想讓某份備課成為全校共享版本時，發一個 Pull Request。

對 AI 說：

> 「這學期 9C 英文備課完成了，幫我發合併申請給 David。」

AI 會確認最新工作已推送、開 PR、填寫標題與摘要。David 收到通知審核後合併。

什麼時候該發 PR？

- 學期結束，整學期備課已完整
- 完成一個完整的 Block（例如 Block 1 大綱定稿）
- 有一份覺得很好、想讓其他老師也看到的教材

---

## 十二、快速指令速查

### 跟 AI 說的話

```
開工                             ← 每次新對話的第一句
開工，9C 英文課                   ← 帶班級開工，跳過詢問
記錄今天 9C 英文課的事            ← Block 3 教學紀錄
按 ABCD 設計差異化任務            ← DI 任務設計
回到中軸                         ← 對話偏離時重新定位
收工                             ← 結束時存檔並推送
幫我發合併申請給 David            ← 學期末發 PR
幫我看 xx 老師最近做了什麼        ← 查閱同事工作
```

### Slash Commands（Claude Code）

```
/opening      ← 自動 git pull + 載入系統 + 報告進度
/load 9c english   ← 載入班級科目脈絡
/lesson       ← 課堂教學設計（Block 2）
/syllabus     ← 學季大綱（Block 1）
/teaching-log ← 教學紀錄（Block 3）
/di-check     ← 雙軸合規檢查
/wrap-up      ← 收工（進度同步 + 存檔推送）
```

### 終端機指令（備用）

```bash
# 一次性安裝
bash setup/start.sh            # Mac
.\setup\start.ps1              # Windows

# 分支確認
git branch --show-current      # 看你在哪個分支
git checkout workspace/Teacher_你的姓名   # 回到自己的分支

# 日常 Git（建議都讓 AI 做）
git status
git pull origin workspace/Teacher_你的姓名
git push origin workspace/Teacher_你的姓名
```

---

## 十三、遇到問題時

### 先問 AI，不要先找 David

把畫面整段（終端機輸出、錯誤訊息）貼給 AI，加上「我在做什麼、卡在哪裡」。如果是設定檔問題，把 `environment.env`、`acl.yaml` 等檔案也餵給 AI 看。

試過 AI 仍無解 → 傳訊息給 David，附上：

1. 你做到哪一步
2. 終端機完整截圖
3. AI 之前的建議
4. 你試了之後發生什麼

### 常見狀況

| 狀況 | 怎麼做 |
|------|--------|
| AI 忘記我們在做什麼 | 說「回到中軸」 |
| 不知道進度在哪 | 問 AI：「現在到哪裡？」 |
| 文件沒出現在 Drive | 確認 gws 有登入；或 Google Drive for Desktop 有開 |
| Git commit 被攔截 | AI 會說明原因；多半是誤動別人檔案 |
| AI 拒絕操作某路徑 | 不在 ACL 範圍內，如需擴充請聯繫 David |
| 看不到 `start.sh` | 你不在 repo 根目錄，先 `cd WaldorfTeacherOS-Repo` |
| `git pull` 失敗／衝突 | 停下來，把完整輸出貼給 AI |
| 不小心在 main 分支做改動 | 停手、貼 `git status` 與 `git branch --show-current` 給 AI |

### 絕對不要做的事

- 不要直接改 `ai-core/`、`projects/_di-framework/`、`setup/`、`.github/` 裡的檔案
- 不要在 `main` 分支工作
- 不要用 `git add .` 或 `git add -A`
- 不要接受 AI 提議的 `--force` 或 `--no-verify`（幾乎都是錯的）

---

## 十四、關於這套系統

TeacherOS 不是「自動出教案」的工具，是「教師與 AI 共創夥伴」系統。AI 處理架構、格式、行政細節；你提供專業判斷、課堂經驗、教學靈魂。

**用得最有效的方式**：

- 帶著具體的班級、具體的學生進來
- 帶著你自己的想法與蒐集的素材進來
- 第一個單元可能慢，之後會越來越快
- 定期翻 `workspaces/工作範例參考/` 看成熟成品

---

## 附錄：本次系統大整理（v2.0）摘要

2026-04-17 做了一次徹底整理：

- 歷史中的機密檔（OAuth 憑證等）已清除
- 每位老師改用獨立的 `workspace/Teacher_xxx` 分支，互不覆蓋
- gws 自動安裝從系統移除，改為個人選配
- `.git` 從 647 MB 壓縮至約 30 MB

**既有老師的一次性重裝**：請看 `setup/teacher-reclone-guide-2026-04.md`。
**新加入的老師**：直接照本指南「二、首次安裝」執行。

---

*維護者：David（elliot200852@gmail.com）*
*GitHub：github.com/elliot200852-lab/waldorf-teacher-os*
*本指南對應 TeacherOS v2.0 乾淨起點（commit 93d9012）*
