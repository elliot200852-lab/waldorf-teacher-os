---
aliases:
  - "技能總目錄"
---

# TeacherOS CreatorHub — 系統技能目錄（ai-core/skills/）

> **這是所有 TeacherOS CreatorHub 系統技能的正本。**
> 任何具備檔案讀取能力的 AI Agent（Claude Code、Gemini、ChatGPT 等）都可以直接讀取並執行。

---

## 技能清單

| 技能檔案 | 用途 | 觸發語（教師說） |
|---------|------|----------------|
| `opening.md` | 新對話開場：更新 Repo → 載入系統 → 報告狀態 | 「開工」「開始」「早安」「start」 |
| `load.md` | 載入班級與科目脈絡，定位工作起點 | 「載入 9C english」「讀一下狀態」 |
| `status.md` | 快速確認目前進度 | 「現在在哪？」「9C english 做到哪了？」 |
| `syllabus.md` | 啟動學季整體教學大綱規劃 | 「開始大綱」「做學季規劃」 |
| `lesson.md` | 進入具體課堂教學設計 | 「進入備課」「做 Block 2」 |
| `wrap-up.md` | 收工：進度同步 + Cowork 編譯 + Obsidian 修正 + Git 存檔推送 | 「收工」「存檔」「收尾」「結束今天」 |
| `di-check.md` | 課程設計 DI 雙軸合規核對 | 「查 DI」「確認差異化」 |
| `ref.md` | 載入特定知識背景模組 | 「載入教學哲學」「看英文背景」 |
| `block-end.md` | 主課程區塊結尾反思 | 「區塊結束」「做反思」 |
| `rhythm.md` | 課堂節奏設計（吸氣↔呼氣） | 「設計節奏」「規劃這週」 |
| `homeroom.md` | 導師業務（班級經營、個案） | 「導師業務」「班級事件」 |
| `student-note.md` | 學生個人觀察紀錄（一人一檔，累加，日期 + tag） | 「記錄學生」「記一下誰」「學生紀錄」 |
| `teaching-log.md` | 教師教學紀錄（一師一檔，累加，日期 + tag） | 「教學紀錄」「教學回顧」「今天上課」 |
| `parent-letter.md` | 家長信草稿 | 「寫家長信」「學期評語」 |
| `pull-request.md` | 發送合併申請 | 「發 PR」「合併申請」 |
| `sync-cowork.md` | 編譯 Cowork Folder Instructions | 「同步 Cowork」 |
| `send-email.md` | 透過 gws CLI 寄送 Email | 「寄信」「寄 Email」「寄給」 |
| `drive.md` | Google Drive 檔案操作（上傳/下載/搜尋） | 「上傳到雲端」「傳到 Drive」 |
| `calendar.md` | Google Calendar 行程管理 | 「查行事曆」「加行事曆」 |
| `sheets.md` | Google Sheets 讀寫操作 | 「開試算表」「寫入 Sheets」 |
| `docs-edit.md` | Google Docs 文件編輯 | 「編輯文件」「寫入 Docs」 |
| `subject-lesson-45.md` | 45 分鐘單堂課設計通用引擎（需搭配科目覆蓋層） | 「設計一堂課」「45 分鐘」「lesson design」 |
| `english-45.md` | 英文科覆蓋層（搭配 `subject-lesson-45.md` 使用） | 「英文課設計」「English lesson」 |
| `git-history.md` | Git History 週記管理（追加或補寫） | 「填進去 Git history」「Git history 編寫」「更新週記」 |
| `add-teacher.md` | 管理員專用：互動式建立新教師 Workspace 與權限 | 「加入新老師」「新增教師」 |
| `gws-setup.md` | Google Workspace CLI 安裝、登入與多帳號設定 | 「設定 gws」「安裝 gws」 |
| `new-doc.md` | 新建 Markdown 文件前確認存放路徑、檔名、是否複製 | 「生成新檔案」「建立新文件」「新增文件」 |
| `obsidian-sync.md` | Obsidian 標籤與索引自動修正 | 「sync Obsidian」「更新索引」「補標籤」 |
| `video-setup.md` | 建立 Remotion 影片專案環境 | 「建立影片專案」「設定 Remotion」「video setup」 |
| `sync-agents.md` | 多 AI agent 系統一致性檢查 | 「同步檢查」「sync agents」「系統一致性」 |
| `yt-subtitle.md` | YouTube 字幕擷取與教學素材轉換 | 「下載字幕」「抓字幕」「YouTube 字幕」「extract subtitles」 |
| `teach-animation.md` | 教學動畫生成（Revideo）：概念解說、時間線、流程圖動畫 | 「教學動畫」「做動畫」「概念動畫」「animate」 |

---

## 引擎＋覆蓋層架構（Engine + Overlay）

`subject-lesson-45.md` 是通用設計引擎，定義五階段工作流（研究 → 設計 → 稽核 → 產出 → 匯出）與六條通用原則。各科目可建立覆蓋層（overlay），補充科目專屬原則、研究任務、稽核維度與產出規格。

**載入順序**：引擎先載入 → Step 0 自動載入對應覆蓋層

**覆蓋層搜尋路徑**（依序）：
1. `ai-core/skills/[科目]-45.md`（系統共用覆蓋層）
2. `{workspace}/skills/draft-[科目]-45.md`（教師個人草稿覆蓋層）
3. 若皆不存在 → 提示教師尚無此科目覆蓋層

**現有覆蓋層**：
- `english-45.md` — 英文科（七至九年級）

**建立新覆蓋層**：見 `workspaces/_template/skills/EXAMPLE-subject-overlay.md`

---

## 如何使用

### Claude Code
直接輸入 `/load 9c english`、`/wrap-up 9c english` 等 slash command。
`.claude/commands/` 中的入口檔案會引導 Claude Code 讀取此目錄的正本。

### 其他 AI（Gemini、ChatGPT、任何有檔案讀取能力的 AI Agent）
1. 讀取此 README，了解有哪些技能可用
2. 讀取對應技能的 `.md` 檔案，取得完整執行規格
3. 依照規格執行

---

## 如何新增技能

### Step 1 — 撰寫正本（必做）

在此目錄新建 `[技能名稱].md`，依照以下結構撰寫：

```
# skill: [技能名稱] — [說明]

## 參數
## 根目錄
## 讀取的檔案
## 執行步驟
## 輸出格式
## 注意事項
```

### Step 2 — 跨平台檢核（必做，新增與修改皆適用）

所有技能必須同時支援 macOS 和 Windows。**新增或修改**技能後，逐項檢查：

| 項目 | macOS / Linux | Windows | 通用替代方案 |
|------|--------------|---------|-------------|
| Python 呼叫 | `python3` | `python` | 先偵測：`python3 --version \|\| python --version` |
| 指令偵測 | `command -v xxx` | `Get-Command xxx` | `python3 -c "import shutil; print(shutil.which('xxx'))"` |
| 臨時目錄 | `/tmp/` | `%TEMP%` | `tempfile.mkdtemp()` 或 `tempfile.gettempdir()` |
| 路徑分隔 | `/` | `\` | `pathlib.Path()` |
| 家目錄 | `~/` | `%USERPROFILE%` | `Path.home()` |
| Shell 腳本 | `bash xxx.sh` | N/A | 改用 Python 腳本，shell 只留薄層入口 |

若技能中有終端機指令，必須同時提供 bash 與 PowerShell 兩種寫法，或使用 Python 統一入口。
完整跨平台公約見 `ai-core/reference/cross-platform.yaml`。

### Step 3 — 更新三份索引文件（必做）

- `ai-core/skills/README.md`（本文件）— 技能清單表新增一行
- `ai-core/skills/skills-manifest.md` — 觸發對照表新增一行
- `ai-core/AI_HANDOFF.md` — 技能觸發表與技能清單各新增一行
- 三份文件的「最後更新」日期同步改為當天

### Step 4 — 建立 Anthropic Skills 封包（必做）

在 `.claude/skills/[技能名稱]/SKILL.md` 建立封包入口，讓 Claude Code 能透過 NLP 語意自動觸發。

```markdown
---
name: [技能名稱]
description: "[豐富的自然語言描述，涵蓋所有可能的觸發語句——中文、英文、口語變體皆列出。越詳細，Claude Code 的觸發比對越精準。]"
---

# [中文標題]

> 本 SKILL.md 是 Claude Code Anthropic Skills 的入口。
> 正本位於 TeacherOS 技能系統，確保所有觸發路徑讀取同一份規格。

## 參數（若有）

- 格式：`<參數1> [參數2]`

## 執行方式

讀取並執行以下檔案（以 Repo 根目錄為基準）：

1. `ai-core/skills/[技能名稱].md`

## 注意事項

- 本入口不包含任何執行邏輯——所有流程均在正本中定義
- 若正本更新，本入口無需同步修改
```

**封包設計原則：**
- SKILL.md 只做路由，**絕不包含執行邏輯**（確保正本唯一性）
- `description` 欄位是觸發精準度的關鍵——把所有觸發語、同義詞、口語變體都寫進去
- 封包層是純 metadata，不含任何 OS 指令，macOS / Windows 行為完全一致
- 個人技能的封包路由指向 `{workspace}/skills/` 而非 `ai-core/skills/`

### Step 5 — 建立 Claude Code Command 薄層入口（必做）

在 `.claude/commands/` 新建入口，讓 `/[技能名稱]` slash command 可用：

```markdown
# /[技能名稱] — [說明]
> Claude Code 薄層入口 — 技能正本：`ai-core/skills/[技能名稱].md`

讀取並執行：`ai-core/skills/[技能名稱].md`
（AI 自動偵測 Repo 根目錄位置）

$ARGUMENTS：[參數說明]
```

### Step 6 — 更新 HOME.md（必做）

將新技能加入 Obsidian HOME.md 的對應區段：
- 正本 → 「系統技能正本」表格
- 封包 → 「Claude Code Skills（Anthropic Skills 封包）」表格
- Command → 「Claude Code Commands」表格

### 完整檢查清單

新增**或修改**技能完成前，確認以下全部到位：

- [ ] `ai-core/skills/[技能名稱].md` — 正本已建立或更新
- [ ] **跨平台檢核通過** — AI 必須逐步列出檢查結果（見下方格式），不可跳過
- [ ] `ai-core/skills/README.md` — 技能清單已更新
- [ ] `ai-core/skills/skills-manifest.md` — 觸發對照已更新
- [ ] `ai-core/AI_HANDOFF.md` — 觸發表已更新
- [ ] `.claude/skills/[技能名稱]/SKILL.md` — Anthropic Skills 封包已建立
- [ ] `.claude/commands/[技能名稱].md` — Claude Code Command 已建立
- [ ] `HOME.md` — Obsidian 索引已更新（正本 + 封包 + Command 三處）

#### 跨平台檢核回報格式（必做）

**新增或修改技能後，AI 必須主動輸出以下表格，不等教師詢問：**

```
**跨平台檢核結果**

| 步驟 | 有終端指令？ | macOS | Windows | 狀態 |
|------|------------|-------|---------|------|
| Step 1 | 有 | bash ✓ | PowerShell ✓ | OK |
| Step 2 | 無 | — | — | OK |
| Step 3 | 有 | bash ✓ | PowerShell ✗ | 需修正 |
```

- 每個 Step 逐一檢查，不可籠統帶過
- 有終端指令的步驟，必須確認 bash 和 PowerShell 兩種寫法都存在
- 發現缺漏時當場修正，修正後重新輸出表格
- 此檢核同時適用於「新增技能」與「修改既有技能」

---

## 根目錄

本目錄中所有技能檔案使用**相對路徑**（以 Repo 根目錄為基準）。
AI 應自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

---

---

## 教師個人技能

除系統技能外，每位教師可在自己的 workspace 建立個人技能：`{workspace}/skills/*.md`

個人技能格式與系統技能一致（YAML frontmatter + Markdown 執行步驟）。
範本見 `workspaces/_template/skills/EXAMPLE-recitation.md`。

**衝突處理：** 個人技能與系統技能同名時，在教師自己的 session 中使用個人版本。
詳見 `ai-core/AI_HANDOFF.md`「教師個人技能」段落。

---

*維護者：TeacherOS CreatorHub Admin。最後更新：2026-03-18（新增 teach-animation 教學動畫技能）*

