---
aliases:
  - "技能索引"
---

# TeacherOS — 技能索引（Skills Index）

> **所有技能的完整執行規格位於：`ai-core/skills/`**
> 本文件是輕量索引，列出技能名稱、觸發語與規格檔案路徑。
> 技能按功能分為六類，協助 AI 在模糊語句時縮小搜尋範圍。

---

## A. 系統營運（TeacherOS 自身的運作）

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「開工」「開始」「早安」「我來了」「start」 | `opening` | `ai-core/skills/opening.md` |
| 「載入 9C」「讀一下狀態」 | `load` | `ai-core/skills/load.md` |
| 「現在在哪？」「9C 做到哪了？」 | `status` | `ai-core/skills/status.md` |
| 「收工」「存檔」「收尾」「結束今天」「儲存」 | `wrap-up` | `ai-core/skills/wrap-up.md` |
| 「sync Obsidian」「更新索引」「補標籤」「整理首頁」 | `obsidian-sync` | `ai-core/skills/obsidian-sync.md` |

## B. 教學核心（直接影響課堂設計與執行）

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「開始大綱」「做學季規劃」 | `syllabus` | `ai-core/skills/syllabus.md` |
| 「進入備課」「做 Block 2」 | `lesson` | `ai-core/skills/lesson.md` |
| 「設計一堂課」「45 分鐘」「lesson design」 | `subject-lesson-45` | `ai-core/skills/subject-lesson-45.md` + 科目覆蓋層 |
| 「設計節奏」「規劃這週」「吸氣呼氣」 | `rhythm` | `ai-core/skills/rhythm.md` |
| 「區塊結束」「做反思」「這個 block 完成了」 | `block-end` | `ai-core/skills/block-end.md` |
| 「查 DI」「確認差異化」 | `di-check` | `ai-core/skills/di-check.md` |
| 「載入教學哲學」「看英文背景」 | `ref` | `ai-core/skills/ref.md` |

**覆蓋層（非獨立技能，由引擎自動載入）：**

| 覆蓋層 | 依附引擎 | 路徑 |
|--------|---------|------|
| `english-45` | `subject-lesson-45` | `ai-core/skills/english-45.md` |

## C. 備課素材（課堂之前的準備工作）

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「詩歌研究」「poetry research」「找詩」 | `poetry-research` | `ai-core/skills/poetry-research.md` |
| 「博物館素材」「找藝術品」「拉幾張畫」「art search」 | `art-in-teaching` | `ai-core/skills/art-in-teaching.md` |
| 「美化」「做漂亮版」「beautify」「套模板」 | `beautify` | `ai-core/skills/beautify.md` |
| 「下載字幕」「抓字幕」「YouTube 字幕」 | `yt-subtitle` | `ai-core/skills/yt-subtitle.md` |
| 「教學動畫」「做動畫」「概念視覺化」「animate」 | `teach-animation` | `ai-core/skills/teach-animation.md` |
| 「做影片」「製作影片」「video」「渲染影片」「建立影片專案」「video setup」 | `video` | `ai-core/skills/video.md` |
| 「臺灣的故事」「每日臺灣的故事」「寫一篇臺灣的故事」「Daily Story of Taiwan」「daily story」「stories of taiwan」 | `story-daily` | `ai-core/skills/story-daily.md`（編排器，依序呼叫下列 5 子技能 + assemble-story.js） |
| 「今天的故事」「選題」「story plan」「臺灣故事選題」「故事選題」 | `story-planner` | `ai-core/skills/story-planner.md` |
| 「搜尋素材」「找資料」「查史料」「story research」 | `story-research` | `ai-core/skills/story-research.md` |
| 「產出故事」「生成三件套」「story write」「撰寫故事」 | `story-writer` | `ai-core/skills/story-writer.md` |
| 「檢查故事」「品質確認」「story verify」 | `story-verify` | `ai-core/skills/story-verify.md` |
| 「歸檔故事」「更新故事索引」「story archive」 | `story-archive` | `ai-core/skills/story-archive.md` |

## D. 導師與學生（人的工作）

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「導師業務」「班級事件」「個案討論」 | `homeroom` | `ai-core/skills/homeroom.md` |
| 「記錄學生」「個案觀察」「記一下誰」「學生紀錄」 | `student-note` | `ai-core/skills/student-note.md` |
| 「教學紀錄」「教學回顧」「今天上課」「教學反思」 | `teaching-log` | `ai-core/skills/teaching-log.md` |
| 「寫家長信」「學期評語」「家長通知」 | `parent-letter` | `ai-core/skills/parent-letter.md` |

## E. 外部服務（Google / Email / 雲端）

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「寄信」「寄 Email」「發郵件」「寄給」 | `send-email` | `ai-core/skills/send-email.md` |
| 「上傳到雲端」「同步 Drive」「傳到 Drive」 | `drive` | `ai-core/skills/drive.md` |
| 「查行事曆」「排課表」「加行事曆」 | `calendar` | `ai-core/skills/calendar.md` |
| 「開試算表」「寫入 Sheets」「讀 Sheets」 | `sheets` | `ai-core/skills/sheets.md` |
| 「編輯文件」「寫入 Docs」「開 Google Docs」 | `docs-edit` | `ai-core/skills/docs-edit.md` |
| 「設定 gws」「安裝 gws」「gws setup」 | `gws-setup` | `ai-core/skills/gws-setup.md` |

## F. 系統工程（低頻維運）

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「加入新老師」「新增老師」「add teacher」 | `add-teacher` | `ai-core/skills/add-teacher.md` |
| 「發 PR」「合併申請」「送回主系統」 | `pull-request` | `ai-core/skills/pull-request.md` |
| 「同步檢查」「sync agents」「系統一致性」 | `sync-agents` | `ai-core/skills/sync-agents.md` |
| 「同步 Cowork」「更新 Cowork」「編譯 instructions」 | `sync-cowork` | `ai-core/skills/sync-cowork.md` |
| 「填進去 Git history」「Git history 編寫」「更新週記」 | `git-history` | `ai-core/skills/git-history.md` |
| 「跨平台檢查」「check compat」「平台檢查」「相容性檢查」 | `check-compat` | `ai-core/skills/check-compat.md` |

---

## 退役紀錄

| 技能 | 退役日期 | 處置 |
|------|---------|------|
| `video-setup` | 2026-03-19 | 合併進 `video`（Step 0） |
| `new-doc` | 2026-03-19 | 功能過於單純，AI 常識可覆蓋 |

---

## 使用方式

**Claude Code**
直接輸入 slash command，例如 `/opening`、`/load 9c`、`/wrap-up 9c`。
`.claude/commands/` 中的薄層入口會自動引導至 `ai-core/skills/` 的正本執行。

**其他 AI（Gemini、ChatGPT、任何有檔案讀取能力的 AI Agent）**
1. 讀取 `ai-core/skills/README.md` 了解技能目錄結構
2. 讀取對應技能的 `.md` 檔案取得完整執行規格
3. 依照規格執行

---

## 新增或修改技能

完整流程見 `ai-core/skills/README.md`「如何新增技能」（6 步驟 + 檢查清單）。

**每次新增或修改技能，必須完成以下全部項目：**

1. `ai-core/skills/[技能名稱].md` — 正本（跨平台檢核通過）
2. `ai-core/skills/README.md` — 技能清單表
3. `ai-core/skills/skills-manifest.md`（本文件）— 觸發對照表
4. `ai-core/AI_HANDOFF.md` — 技能觸發表
5. `.claude/skills/[技能名稱]/SKILL.md` — Anthropic Skills 封包（純路由，不含邏輯）
6. `.claude/commands/[技能名稱].md` — Claude Code Command 薄層入口
7. `HOME.md` — Obsidian 索引（正本 + 封包 + Command 三處）

**跨平台規則：** 所有技能必須同時支援 macOS 和 Windows。詳見 README 的 Step 2 跨平台檢核表。

---

*維護者：David。技能正本路徑：`ai-core/skills/`。最後更新：2026-03-21（新增 story-daily 編排器 + 臺灣的故事管線 5 子技能）*
