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
| `student-note.md` | 學生觀察記錄 | 「記錄學生」「記一下誰」 |
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

1. **在此目錄新建 `[技能名稱].md`**，依照以下結構撰寫：
   ```
   # skill: [技能名稱] — [說明]

   ## 參數
   ## 根目錄
   ## 讀取的檔案
   ## 執行步驟
   ## 輸出格式
   ## 注意事項
   ```

2. **在 `ai-core/skills-manifest.md` 的技能索引表新增一行**：
   | `[觸發語]` | `[技能名稱]` | `ai-core/skills/[技能名稱].md` |

3. **（選用，Claude Code slash command）** 在 `.claude/commands/` 新建薄層入口：
   ```markdown
   # /[技能名稱] — [說明]
   > Claude Code 薄層入口 — 技能正本：`ai-core/skills/[技能名稱].md`

   讀取並執行：`ai-core/skills/[技能名稱].md`
   （AI 自動偵測 Repo 根目錄位置）

   $ARGUMENTS：[參數說明]
   ```

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

*維護者：TeacherOS CreatorHub Admin。最後更新：2026-03-08*

