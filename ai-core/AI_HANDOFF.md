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

- `projects/class-{9c/8a/7a}/project.yaml` — 班級脈絡與焦點
- `projects/class-{9c/8a/7a}/working/english-session.yaml` — 英文課進度錨點
- `projects/class-9c/homeroom/session.yaml` — 導師業務進度錨點

---

## 第二步：載入後主動報告（語音模式優先）

讀完必讀檔案後，立即說：

> 「已載入系統。[班級] [科目] 目前在 Block [X] Step [Y]，下一步是 [next_action 欄位內容]。是否直接開始？」

不要問「要做什麼」。要從進度錨點讀出現況，主動報告，等教師確認。

---

## 第三步：對話結束時必須更新

1. 更新對應的 `working/*.yaml` 進度錨點（只改有變動的欄位）
2. 更新 `ai-core/system-status.yaml`（反映真實現況）
3. 新產出的備課內容存入 `content/*.md`

---

## 附錄：其他參考入口

| 需求 | 位置 |
|------|------|
| 歷次 session 完成紀錄 | `ai-core/reviews/session-log.md`（AI 平時不載入） |
| 定期系統 Review 紀錄 | `ai-core/reviews/`（AI 平時不載入） |
| 新老師環境設定 | `setup/teacher-guide.md` |
| 當前系統狀態快照 | `ai-core/system-status.yaml`（需要時才讀） |
| 新增班級或科目 | 見 `setup/teacher-guide.md` 的「新增班級 SOP」章節 |

---

*最後更新：2026-03-01*
*GitHub：github.com/elliot200852-lab/waldorf-teacher-os*
