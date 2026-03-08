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
| 「收尾」「更新進度」 | `session-end` | `ai-core/skills/session-end.md` |
| 「查 DI」「確認差異化」 | `di-check` | `ai-core/skills/di-check.md` |
| 「載入教學哲學」「看英文背景」 | `ref` | `ai-core/skills/ref.md` |
| 「導師業務」「班級事件」「個案討論」 | `homeroom` | `ai-core/skills/homeroom.md` |
| 「區塊結束」「做反思」「這個 block 完成了」 | `block-end` | `ai-core/skills/block-end.md` |
| 「設計節奏」「規劃這週」「吸氣呼氣」 | `rhythm` | `ai-core/skills/rhythm.md` |
| 「記錄學生」「個案觀察」「記一下誰」 | `student-note` | `ai-core/skills/student-note.md` |
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

---

## 使用方式

**Claude Code**
直接輸入 slash command，例如 `/opening`、`/load 9c`、`/session-end 9c`。
`.claude/commands/` 中的薄層入口會自動引導至 `ai-core/skills/` 的正本執行。

**其他 AI（Gemini、ChatGPT、任何有檔案讀取能力的 AI Agent）**
1. 讀取 `ai-core/skills/README.md` 了解技能目錄結構
2. 讀取對應技能的 `.md` 檔案取得完整執行規格
3. 依照規格執行

---

## 新增技能

見 `ai-core/skills/README.md` 的「如何新增技能」章節。

---

*維護者：David。技能正本路徑：`ai-core/skills/`。最後更新：2026-03-08*
