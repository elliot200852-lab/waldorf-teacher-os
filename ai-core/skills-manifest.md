---
aliases:
  - "技能索引"
---

# TeacherOS CreatorHub — 技能索引（Skills Manifest）

> 觸發語 → 技能名稱 → 檔案路徑的快速對照表。
> 任何 AI Agent 讀取此檔案即可建立觸發比對清單。

---

## 系統技能索引

| 觸發語 | 技能名稱 | 路徑 |
|--------|---------|------|
| 「開工」「早安」「新對話」「start」 | opening | `ai-core/skills/opening.md` |
| 「載入」「讀一下」+ 班級 + 科目 | load | `ai-core/skills/load.md` |
| 「現在在哪」「做到哪了」 | status | `ai-core/skills/status.md` |
| 「開始大綱」「學季規劃」 | syllabus | `ai-core/skills/syllabus.md` |
| 「進入備課」「做 Block」「開始設計」 | lesson | `ai-core/skills/lesson.md` |
| 「收工」「存檔」「收尾」「結束今天」 | wrap-up | `ai-core/skills/wrap-up.md` |
| 「查 DI」「確認差異化」 | di-check | `ai-core/skills/di-check.md` |
| 「載入教學哲學」「看背景」「ref」 | ref | `ai-core/skills/ref.md` |
| 「區塊結束」「做反思」「block 完成」 | block-end | `ai-core/skills/block-end.md` |
| 「設計節奏」「規劃這週」「吸氣呼氣」 | rhythm | `ai-core/skills/rhythm.md` |
| 「導師業務」「班級事件」「個案討論」 | homeroom | `ai-core/skills/homeroom.md` |
| 「記錄學生」「觀察記錄」「記一下誰」 | student-note | `ai-core/skills/student-note.md` |
| 「寫家長信」「學期評語」「家長通知」 | parent-letter | `ai-core/skills/parent-letter.md` |
| 「發 PR」「合併申請」「送回主系統」 | pull-request | `ai-core/skills/pull-request.md` |
| 「同步 Cowork」「更新 Cowork」 | sync-cowork | `ai-core/skills/sync-cowork.md` |
| 「加入新老師」「新增教師」「add teacher」 | add-teacher | `ai-core/skills/add-teacher.md` |
| 「上傳到雲端」「傳到 Drive」「同步 Drive」 | drive | `ai-core/skills/drive.md` |
| 「查行事曆」「排課表」「加行事曆」 | calendar | `ai-core/skills/calendar.md` |
| 「寄信」「寄 Email」「發郵件」「寄給」 | send-email | `ai-core/skills/send-email.md` |
| 「開試算表」「寫入 Sheets」「讀 Sheets」 | sheets | `ai-core/skills/sheets.md` |
| 「編輯文件」「寫入 Docs」「開 Google Docs」 | docs-edit | `ai-core/skills/docs-edit.md` |
| 「設計一堂課」「45/90 分鐘」「連堂」「主課程」「lesson design」 | lesson-engine | `ai-core/skills/lesson-engine.md` |
| 「英文課設計」「English lesson」 | english-45 | `ai-core/skills/english-45.md`（由 lesson-engine 載入） |
| 「填進去 Git history」「更新週記」 | git-history | `ai-core/skills/git-history.md` |
| 「sync Obsidian」「更新索引」「補標籤」 | obsidian-sync | `ai-core/skills/obsidian-sync.md` |
| 「設定 gws」「安裝 gws」「gws setup」 | gws-setup | `ai-core/skills/gws-setup.md` |
| 「生成新檔案」「建立新文件」「新增文件」「產出新文件」 | new-doc | `ai-core/skills/new-doc.md` |

---

## 教師個人技能

個人技能位於 `{workspace}/skills/*.md`，由 AI 在載入 workspace 後自動掃描 frontmatter。
詳見 `ai-core/AI_HANDOFF.md`「教師個人技能」段落。

---

*最後更新：2026-03-12*
