# TeacherOS — 通用技能目錄（ai-core/skills/）

> **這是所有 TeacherOS 技能的正本。**
> 任何具備檔案讀取能力的 AI Agent（Claude Code、Gemini、ChatGPT 等）都可以直接讀取並執行。

---

## 技能清單

| 技能檔案 | 用途 | 觸發語（教師說） |
|---------|------|----------------|
| `load.md` | 載入班級與科目脈絡，定位工作起點 | 「載入 9C english」「讀一下狀態」 |
| `status.md` | 快速確認目前進度 | 「現在在哪？」「9C english 做到哪了？」 |
| `syllabus.md` | 啟動學季整體教學大綱規劃 | 「開始大綱」「做學季規劃」 |
| `lesson.md` | 進入具體課堂教學設計 | 「進入備課」「做 Block 2」 |
| `session-end.md` | 對話結束前同步進度狀態 | 「收尾」「更新進度」 |
| `di-check.md` | 課程設計 DI 雙軸合規核對 | 「查 DI」「確認差異化」 |
| `ref.md` | 載入特定知識背景模組 | 「載入教學哲學」「看英文背景」 |
| `block-end.md` | 主課程區塊結尾反思 | 「區塊結束」「做反思」 |
| `rhythm.md` | 課堂節奏設計（吸氣↔呼氣） | 「設計節奏」「規劃這週」 |
| `homeroom.md` | 導師業務（班級經營、個案） | 「導師業務」「班級事件」 |
| `student-note.md` | 學生觀察記錄 | 「記錄學生」「記一下誰」 |
| `parent-letter.md` | 家長信草稿 | 「寫家長信」「學期評語」 |
| `save.md` | 儲存工作並上傳 GitHub | 「存檔」「儲存」 |
| `pull-request.md` | 發送合併申請 | 「發 PR」「合併申請」 |
| `sync-cowork.md` | 編譯 Cowork Folder Instructions | 「同步 Cowork」 |

---

## 如何使用

### Claude Code
直接輸入 `/load 9c english`、`/session-end 9c english` 等 slash command。
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

*維護者：TeacherOS Admin。最後更新：2026-03-04*
