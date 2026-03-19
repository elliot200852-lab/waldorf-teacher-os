---
aliases:
  - "技能索引"
---

# TeacherOS — 技能索引（Skills Index）

> **所有技能的完整執行規格位於：`ai-core/skills/`**
> 本文件是輕量索引，列出技能名稱、觸發語與規格檔案路徑。

---

## 技能觸發對照表

| 教師說 | 技能 | 完整規格 |
|--------|------|---------|
| 「開工」「開始」「早安」「我來了」「start」 | `opening` | `ai-core/skills/opening.md` |
| 「載入 9C」「讀一下狀態」 | `load` | `ai-core/skills/load.md` |
| 「現在在哪？」「9C 做到哪了？」 | `status` | `ai-core/skills/status.md` |
| 「開始大綱」「做學季規劃」 | `syllabus` | `ai-core/skills/syllabus.md` |
| 「進入備課」「做 Block 2」 | `lesson` | `ai-core/skills/lesson.md` |
| 「收工」「存檔」「收尾」「結束今天」「儲存」 | `wrap-up` | `ai-core/skills/wrap-up.md` |
| 「查 DI」「確認差異化」 | `di-check` | `ai-core/skills/di-check.md` |
| 「載入教學哲學」「看英文背景」 | `ref` | `ai-core/skills/ref.md` |
| 「導師業務」「班級事件」「個案討論」 | `homeroom` | `ai-core/skills/homeroom.md` |
| 「區塊結束」「做反思」「這個 block 完成了」 | `block-end` | `ai-core/skills/block-end.md` |
| 「設計節奏」「規劃這週」「吸氣呼氣」 | `rhythm` | `ai-core/skills/rhythm.md` |
| 「記錄學生」「個案觀察」「記一下誰」「學生紀錄」 | `student-note` | `ai-core/skills/student-note.md` |
| 「教學紀錄」「教學回顧」「今天上課」「教學反思」 | `teaching-log` | `ai-core/skills/teaching-log.md` |
| 「寫家長信」「學期評語」「家長通知」 | `parent-letter` | `ai-core/skills/parent-letter.md` |
| 「同步 Cowork」「更新 Cowork」 | `sync-cowork` | `ai-core/skills/sync-cowork.md` |
| 「寄信」「寄 Email」「發郵件」「寄給」 | `send-email` | `ai-core/skills/send-email.md` |
| 「上傳到雲端」「同步 Drive」「傳到 Drive」 | `drive` | `ai-core/skills/drive.md` |
| 「查行事曆」「排課表」「加行事曆」 | `calendar` | `ai-core/skills/calendar.md` |
| 「開試算表」「寫入 Sheets」「讀 Sheets」 | `sheets` | `ai-core/skills/sheets.md` |
| 「編輯文件」「寫入 Docs」「開 Google Docs」 | `docs-edit` | `ai-core/skills/docs-edit.md` |
| 「設計一堂課」「45 分鐘」「lesson design」 | `subject-lesson-45` | `ai-core/skills/subject-lesson-45.md` + 科目覆蓋層 |
| 「英文課設計」「English lesson」 | `english-45`（覆蓋層） | `ai-core/skills/english-45.md` |
| 「填進去 Git history」「Git history 編寫」「更新週記」「git 回顧」 | `git-history` | `ai-core/skills/git-history.md` |
| 「sync Obsidian」「更新索引」「補標籤」「整理首頁」 | `obsidian-sync` | `ai-core/skills/obsidian-sync.md` |
| 「加入新老師」「新增老師」「新增教師」「add teacher」 | `add-teacher` | `ai-core/skills/add-teacher.md` |
| 「設定 gws」「安裝 gws」「gws setup」 | `gws-setup` | `ai-core/skills/gws-setup.md` |
| 「生成新檔案」「建立新文件」「新增文件」「產出新文件」 | `new-doc` | `ai-core/skills/new-doc.md` |
| 「發 PR」「合併申請」「送回主系統」 | `pull-request` | `ai-core/skills/pull-request.md` |
| 「建立影片專案」「設定 Remotion」「video setup」「影片環境」 | `video-setup` | `ai-core/skills/video-setup.md` |
| 「同步檢查」「檢查系統」「sync agents」「系統一致性」 | `sync-agents` | `ai-core/skills/sync-agents.md` |
| 「詩歌研究」「英文詩歌研究」「英文詩歌備課」「poetry research」 | `poetry-research` | `ai-core/skills/poetry-research.md` |
| 「博物館素材」「找藝術品」「拉幾張畫」「做素材展示」「art search」「Met API」「Europeana」 | `art-in-teaching` | `ai-core/skills/art-in-teaching.md` |

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

*維護者：David。技能正本路徑：`ai-core/skills/`。最後更新：2026-03-19（新增 art-in-teaching 藝術作品融入教學素材管線技能）*
