---
aliases:
  - "AI 入口文件"
---

# TeacherOS CreatorHub — AI 入口（AI_HANDOFF）

任何 AI 在對話開始時讀取此文件，即可在 30 秒內進入工作狀態。
不需要教師重新解釋背景。

---

## 第零步：確保 Repo 為最新版本

**每次新對話開始，在讀取任何檔案之前，必須先確認教師的 Repo 已更新至最新版本。**

完整執行規格見：`ai-core/skills/opening.md`

簡要邏輯：

| AI 能力 | 行為 |
|---------|------|
| 有終端機（Claude Code、Cowork） | 自動執行 `git fetch origin` → `git pull origin main`，報告結果 |
| 無終端機（Gemini 語音、ChatGPT） | 提醒教師手動執行 `git pull origin main`，等待確認後才繼續 |

如果教師有未 commit 的改動，先提醒存檔（觸發 wrap-up 技能）再 pull。
如果 pull 有衝突，**停止載入**，請教師聯繫 David。

確認更新完成後，進入第一步。

---

## 第一步：依序讀取以下檔案

**必讀（所有工作類型，嚴格按順序載入）**

1. `ai-core/teacheros.yaml`
   → 系統路由中樞：載入順序、workspace 機制、session 協議、多 AI Agent 協調

2. `ai-core/teacheros-foundation.yaml`
   → 華德福教育共用根基：教育哲學、發展心理、課程原則、AI 使命、reference 觸發條件
   → **所有教師共讀，是課程設計的思想底層**

3. `ai-core/acl.yaml`
   → 比對當前使用者 Email，確認 workspace 路徑與角色（admin / teacher）

4. `{workspace}/teacheros-personal.yaml`
   → 教師個人身份、科目信念、工作偏好（從 acl.yaml 取得 workspace 路徑）

5. `projects/_di-framework/project.yaml`
   → 差異化教學框架規則、產出協議、品質標準入口、輸出格式規範

**依工作類型按需讀取（教師會說明，或從工作線 YAML 推斷）**

| 工作類型 | 額外讀取 |
|----------|----------|
| 課程設計（任何科目） | `projects/_di-framework/content/[科目]-di-template.md` |
| 導師業務 | `projects/_di-framework/content/homeroom-template.md` |
| 涉及學生資料 | `projects/_di-framework/content/student-knowledge-protocol.md` |
| 品質確認 | `projects/_di-framework/content/strategy-output-quality-standard.md` |

**指定班級（依教師指示，或從上次工作線 YAML 推斷）**

班級資料位於各教師的 workspace 內：
- 管理者（Codeowner）：`workspaces/Working_Member/Codeowner_{姓名}/projects/class-{code}/`
- 一般教師：`workspaces/Working_Member/Teacher_{姓名}/projects/class-{code}/`

載入順序：
- `{workspace}/projects/class-{code}/project.yaml` — 班級脈絡與焦點
- `{workspace}/projects/class-{code}/{科目}/session.yaml` — 各科目進度錨點

每個科目資料夾（english/、homeroom/、ml-taiwan-literature/ 等）內都有自己的 `session.yaml`。
掃描規則：`class-*/*/session.yaml`（一層子資料夾內找 session.yaml）。

---

## 第二步：載入後主動報告（語音模式優先）

讀完必讀檔案後，立即說：

> 「已載入系統。[班級] [科目] 目前在 Block [X] Step [Y]，下一步：[next_action 欄位內容]。
> 說「進入備課」我會直接開始設計；說「收尾」我會同步進度。是否直接開始？」

不要問「要做什麼」。要從進度錨點讀出現況，主動報告，等教師確認。

---

## 技能執行規則（任何 AI 必須遵守）

偵測到以下觸發語時，**不需追問，立即**執行：
1. 讀取對應的 `ai-core/skills/[技能].md`（根目錄：Repo 根目錄）
2. 依照檔案中的步驟一步一步執行
3. 技能完成後自然回到對話

| 偵測到這些詞語 | 立即讀取並執行 |
|-------------|--------------|
| 「開工」「開始」「新對話」「早安」「我來了」「準備好了」「start」 | `ai-core/skills/opening.md` |
| 「載入」「讀一下」+ 班級名 + 科目 | `ai-core/skills/load.md` |
| 「現在在哪」「做到哪了」 | `ai-core/skills/status.md` |
| 「開始大綱」「學季規劃」 | `ai-core/skills/syllabus.md` |
| 「進入備課」「做 Block」「開始設計」 | `ai-core/skills/lesson.md` |
| 「收工」「收尾」「存檔」「儲存」「更新進度」「結束今天」「commit」「備份」 | `ai-core/skills/wrap-up.md` |
| 「查 DI」「確認差異化」 | `ai-core/skills/di-check.md` |
| 「載入教學哲學」「看背景」「ref」 | `ai-core/skills/ref.md` |
| 「導師業務」「班級事件」「個案討論」 | `ai-core/skills/homeroom.md` |
| 「區塊結束」「做反思」「block 完成」 | `ai-core/skills/block-end.md` |
| 「設計節奏」「規劃這週」「吸氣呼氣」 | `ai-core/skills/rhythm.md` |
| 「記錄學生」「觀察記錄」「記一下誰」「學生紀錄」 | `ai-core/skills/student-note.md` |
| 「教學紀錄」「教學回顧」「今天上課」「教學反思」 | `ai-core/skills/teaching-log.md` |
| 「寫家長信」「學期評語」「家長通知」 | `ai-core/skills/parent-letter.md` |
| 「sync Obsidian」「更新索引」「補標籤」「整理首頁」 | `ai-core/skills/obsidian-sync.md` |
| 「發 PR」「合併申請」「送回主系統」 | `ai-core/skills/pull-request.md` |
| 「同步 Cowork」「更新 Cowork」「編譯 instructions」 | `ai-core/skills/sync-cowork.md` |
| 「加入新老師」「新增老師」「新增教師」「add teacher」 | `ai-core/skills/add-teacher.md` |
| 「上傳到雲端」「同步 Drive」「傳到 Drive」 | `ai-core/skills/drive.md` |
| 「查行事曆」「排課表」「加行事曆」 | `ai-core/skills/calendar.md` |
| 「寄信」「寄 Email」「發郵件」「寄給」 | `ai-core/skills/send-email.md` |
| 「開試算表」「寫入 Sheets」「讀 Sheets」 | `ai-core/skills/sheets.md` |
| 「編輯文件」「寫入 Docs」「開 Google Docs」 | `ai-core/skills/docs-edit.md` |
| 「設定 gws」「安裝 gws」「gws setup」 | `ai-core/skills/gws-setup.md` |
| 「生成新檔案」「建立新文件」「新增文件」「產出新文件」 | `ai-core/skills/new-doc.md` |
| 「設計一堂課」「45 分鐘」「lesson design」 | `ai-core/skills/subject-lesson-45.md` |
| 「英文課設計」「English lesson」 | `ai-core/skills/english-45.md` |
| 「填進去 Git history」「Git history 編寫」「更新週記」「git 回顧」 | `ai-core/skills/git-history.md` |
| 「做影片」「製作影片」「影片」「video」「渲染影片」 | `ai-core/skills/video.md` |
| 「建立影片專案」「設定 Remotion」「video setup」「影片環境」 | `ai-core/skills/video-setup.md` |
| 「同步檢查」「檢查系統」「sync agents」「系統一致性」 | `ai-core/skills/sync-agents.md` |
| 「下載字幕」「抓字幕」「YouTube 字幕」「提取字幕」「extract subtitles」 | `ai-core/skills/yt-subtitle.md` |

**語音模式注意：** 教師以語音輸入為主，措辭不精確。任何接近以上觸發語的表達（包含口語省略、方言轉換）都應觸發對應技能，不等待精確指令。

**工具無關性：** 以上規則適用於任何 AI 工具（Claude Code、Gemini、未來任何工具）。技能正本統一在 `ai-core/skills/`，任何有檔案讀取能力的 AI 都可直接執行。

**Google Workspace 操作：** 所有 Google Workspace 操作（Drive、Calendar、Gmail、Sheets、Docs）統一使用 gws CLI（跨工具通用）。無終端機時提示教師手動操作。完整指令參考見 `ai-core/reference/gws-cli-guide.md`。

---

## 教師個人技能（Personal Skills）

除系統技能外，每位教師可在 `{workspace}/skills/` 建立個人技能。
AI 完成第一步後，掃描該資料夾的 YAML frontmatter（`triggers` + `description`），暫存為觸發比對清單。
個人技能與系統技能同名時，**優先使用個人版本**並通知教師。教師可說「用系統的 [技能名]」切換。

完整掃描規則、衝突處理範例、格式規範見 `ai-core/skills/opening.md` Step 3。
個人技能範本見 `workspaces/_template/skills/EXAMPLE-recitation.md`。

---

## 第三步：對話結束前主動提醒

多個 AI Agent 可能交替使用，wrap-up 是唯一的工作銜接機制。
若教師未主動說「收工」，AI 應在對話尾聲主動提醒：
「今天的工作要更新進度嗎？說『收尾』我來處理。」

（wrap-up 的觸發語與執行規格已定義於上方「技能執行規則」，不重複列出。）

---

## 第四步：Session 管理（保持 AI 工作品質）

AI 的 context window 有限。長對話後，早期載入的教育哲學、DI 框架、語氣錨點會被壓縮或摘要化，導致工作品質下降。

**AI 必須在以下情況主動建議教師收工並開新 session：**

1. 對話已超過 20 輪以上的實質工作交換
2. 工作主題即將大幅切換（例：從備課 → 系統工程，或從英文 → 導師業務）
3. AI 發現自己需要重新讀取先前已載入的檔案（表示內容已被壓縮）
4. 教師指出回應品質下降、忘記指示、或語氣偏離

**建議措辭：**
「這個 session 已經工作了一段時間，建議收工後開新對話，讓我重新載入完整的系統設定。說『收工』我來處理。」

**原則：重新開工永遠比在壓縮後的 context 裡硬撐更有效率。一個 session 做一件主要的事。**

---

## 技能系統（Skills）

**技能正本：** `ai-core/skills/`（所有 AI 共用）。每個技能為獨立 `.md` 檔。
完整觸發語對照見上方「技能執行規則」，不重複列出。

**Claude Code 使用者：** 技能為 slash command，直接輸入 `/load 9c english`、`/lesson 9c english 2` 等指令。
`.claude/commands/` 為薄層入口，讀取後自動指向 `ai-core/skills/` 正本。

**Gemini / ChatGPT / 其他有檔案能力的 AI：**
1. 讀取 `ai-core/skills/README.md` 取得技能目錄
2. 讀取對應技能的 `.md` 檔案取得完整規格
3. 依照規格執行

**新增技能：** 完整 6 步驟見 `ai-core/skills/README.md`「如何新增技能」。必須同時建立正本（`ai-core/skills/`）、Anthropic Skills 封包（`.claude/skills/`）、Command 入口（`.claude/commands/`），並通過跨平台檢核（macOS + Windows）。

---

## Reference 知識模組（按需載入）

以下模組在 `teacheros-foundation.yaml` 的 `reference_loading_protocol` 已定義觸發條件。
AI 在相關工作場景中應主動讀取，無需教師指示。
**重要：** foundation 已包含每個 reference 的操作性設計原則（`_design_principles`），日常備課通常不需要載入完整 reference。只有深度設計或教師主動要求時才載入。

| 模組 | 路徑 | 主動觸發場景 |
|------|------|-------------|
| pedagogy | `ai-core/reference/pedagogy-framework.yaml` | 深入分析學生發展、課程哲學的完整脈絡 |
| english | `ai-core/reference/subject-english.yaml` | 英文課深度設計、施泰納語言哲學完整論述 |
| history | `ai-core/reference/subject-history.yaml` | 歷史課深度設計、台灣主體史觀完整論述 |
| student | `ai-core/reference/student-development.yaml` | 班級經營深度分析、個案討論、修復式正義完整框架 |

---

## 附錄：其他參考入口

| 需求 | 位置 |
|------|------|
| 技能正本目錄（所有 AI 共用）| `ai-core/skills/`（入口：`ai-core/skills/README.md`） |
| 技能索引（觸發語 + 路徑對照）| `ai-core/skills-manifest.md` |
| 歷次 session 完成紀錄 | `ai-core/reviews/session-log.md`（AI 平時不載入） |
| 定期系統 Review 紀錄 | `ai-core/reviews/`（AI 平時不載入） |
| 新老師環境設定 | `setup/teacher-guide.md` |
| 當前系統狀態快照 | `ai-core/system-status.yaml`（需要時才讀） |
| 新增班級或科目 | 見 `setup/teacher-guide.md` 的「新增班級 SOP」章節 |
| 使用者權限 | `ai-core/acl.yaml` |

---

*最後更新：2026-03-17（Skill Creator 升級：新增技能必含 Anthropic 封包 + 跨平台檢核）*
*GitHub：github.com/elliot200852-lab/waldorf-teacher-os*
