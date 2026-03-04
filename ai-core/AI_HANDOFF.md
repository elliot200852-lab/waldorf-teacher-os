# TeacherOS — AI 入口（AI_HANDOFF）

任何 AI 在對話開始時讀取此文件，即可在 30 秒內進入工作狀態。
不需要 David 重新解釋背景。

---

## 第一步：依序讀取以下檔案

**必讀（所有工作類型）**

1. `ai-core/teacheros.yaml`
   → 教師身份、工作偏好、語氣錨點、AI 協作目標

2. `projects/_di-framework/project.yaml`
   → 差異化教學框架規則、產出協議、品質標準入口、輸出格式規範

**依工作類型按需讀取（David 會說明，或從工作線 YAML 推斷）**

| 工作類型 | 額外讀取 |
|----------|----------|
| 英文課設計 | `projects/_di-framework/content/english-di-template.md` |
| 導師業務 | `projects/_di-framework/content/homeroom-template.md` |
| 涉及學生資料 | `projects/_di-framework/content/student-knowledge-protocol.md` |
| 品質確認 | `projects/_di-framework/content/strategy-output-quality-standard.md` |

**指定班級（依 David 指示，或從上次工作線 YAML 推斷）**

班級資料位於各教師的 workspace 內：
- David：`workspaces/Working_Member/Codeowner_David/projects/class-{code}/`
- 其他教師：`workspaces/Working_Member/Teacher_{姓名}/projects/class-{code}/`

載入順序：
- `{workspace}/projects/class-{code}/project.yaml` — 班級脈絡與焦點
- `{workspace}/projects/class-{code}/working/english-session.yaml` — 英文課進度錨點
- `{workspace}/projects/class-{code}/homeroom/session.yaml` — 導師業務進度錨點（如有）

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
| 「載入」「讀一下」+ 班級名 | `ai-core/skills/load.md` |
| 「現在在哪」「做到哪了」 | `ai-core/skills/status.md` |
| 「開始大綱」「學季規劃」 | `ai-core/skills/syllabus.md` |
| 「進入備課」「做 Block」「開始設計」 | `ai-core/skills/lesson.md` |
| 「收尾」「更新進度」「結束今天」 | `ai-core/skills/session-end.md` |
| 「查 DI」「確認差異化」 | `ai-core/skills/di-check.md` |
| 「載入教學哲學」「看英文背景」「ref」 | `ai-core/skills/ref.md` |
| 「導師業務」「班級事件」「個案討論」 | `ai-core/skills/homeroom.md` |
| 「區塊結束」「做反思」「block 完成」 | `ai-core/skills/block-end.md` |
| 「設計節奏」「規劃這週」「吸氣呼氣」 | `ai-core/skills/rhythm.md` |
| 「記錄學生」「觀察記錄」「記一下誰」 | `ai-core/skills/student-note.md` |
| 「寫家長信」「學期評語」「家長通知」 | `ai-core/skills/parent-letter.md` |
| 「存檔」「儲存」「幫我存」「commit」「備份」 | `ai-core/skills/save.md` |
| 「發 PR」「合併申請」「送回主系統」「通知 David 合併」 | `ai-core/skills/pull-request.md` |
| 「同步 Cowork」「更新 Cowork」「編譯 instructions」 | `ai-core/skills/sync-cowork.md` |

**語音模式注意：** David 以語音輸入為主，措辭不精確。任何接近以上觸發語的表達（包含口語省略、方言轉換）都應觸發對應技能，不等待精確指令。

**工具無關性：** 以上規則適用於任何 AI 工具（Claude Code、Gemini、未來任何工具）。技能正本統一在 `ai-core/skills/`，任何有檔案讀取能力的 AI 都可直接執行。

---

## 第三步：對話結束時必須更新

偵測到「收尾」「更新進度」「結束今天」→ **立即執行 `ai-core/skills/session-end.md`**

兩個 AI Agent 每日切換（Claude Code ↔ Google Antigravity），session-end 是唯一的工作銜接機制。每次對話結束前若教師未主動說收尾，AI 應主動提醒：「今天的工作要更新進度嗎？說「收尾」我來處理。」

---

## 技能系統（Skills）

TeacherOS 內建標準化技能，對應不同工作場景。

**技能正本：** `ai-core/skills/`（所有 AI 共用）
每個技能為獨立 `.md` 檔，任何具備檔案讀取能力的 AI Agent 皆可直接讀取並執行。

**Claude Code 使用者：** 技能為 slash command，直接輸入 `/load 9c`、`/lesson 9c 2` 等指令。
`.claude/commands/` 為薄層入口，讀取後自動指向 `ai-core/skills/` 正本。

**Gemini / ChatGPT / 其他有檔案能力的 AI：**
1. 讀取 `ai-core/skills/README.md` 取得技能目錄
2. 讀取對應技能的 `.md` 檔案（如 `ai-core/skills/session-end.md`）取得完整規格
3. 依照規格執行

**新增技能：** 在 `ai-core/skills/` 新建 `.md` 檔，在 `skills-manifest.md` 加索引即完成。

| 技能 | 教師說 | 用途 |
|------|--------|------|
| `load` | 「載入 9C」「讀一下狀態」 | 載入班級脈絡，定位工作起點 |
| `status` | 「現在在哪？」 | 快速查詢進度 |
| `syllabus` | 「開始大綱」「做學季規劃」 | 啟動 Block 1 |
| `lesson` | 「進入備課」「做 Block 2」 | 課堂教學設計 |
| `session-end` | 「收尾」「更新進度」 | 對話結束前同步狀態 |
| `di-check` | 「查 DI」「確認差異化」 | DI 雙軸合規核對 |
| `ref` | 「載入教學哲學」「看英文背景」 | 按需載入 Reference 模組 |

---

## Reference 知識模組（按需載入）

以下模組在 `teacheros.yaml` 的 `reference_loading_protocol` 已定義觸發條件。
AI 在相關工作場景中應主動讀取，無需教師指示。

| 模組 | 路徑 | 主動觸發場景 |
|------|------|-------------|
| pedagogy | `ai-core/reference/pedagogy-framework.yaml` | 學生發展分析、課程設計哲學 |
| english | `ai-core/reference/subject-english.yaml` | 英文課設計、科目定位 |
| history | `ai-core/reference/subject-history.yaml` | 歷史課設計、台灣史觀 |
| student | `ai-core/reference/student-development.yaml` | 班級經營、個案討論 |

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

*最後更新：2026-03-03*
*GitHub：github.com/elliot200852-lab/waldorf-teacher-os*
