# TeacherOS × 專案三層記憶系統指引手冊

## 執行摘要

你要建立的不是「把所有資料塞進同一個筆記本」的系統，而是一套**可移植、可重複載入、可出版**的教師工作流：

- **YAML 管結構**：讓 AI 每次「秒懂你是誰、專案在哪、今天要推進哪條工作線」。適合存「狀態與邏輯骨架」；語法核心是縮排、清單、映射（key/value）。
- **Markdown 管內容**：真正的備課輸出（教案文字、故事稿、活動流程、講義）。
- **三層記憶**：TeacherOS（不常變）→ Project（專案生命線）→ Working（工作線分流）。
- **打包輸出**：用 manifest 指定「要輸出的檔案清單與章節順序」，再用 MkDocs / Pandoc 輸出成網站或文件。

---

## 背景與目標

兩個關鍵現實：
1. 多個 AI 工具之間通常**不會自動共享**同一份背景；要靠你用「可再載入的檔案」把上下文帶進去。
2. 若把所有內容都塞進單一資料容器，會造成 Context 爆炸、重點模糊、推理品質下降。

因此目標是：
- 用 `TeacherOS.yaml` 固定「你作為教師的教學哲學與偏好」
- 用 `project.yaml` 固定「該專案的意義、現況、下一步」
- 用 `working/*.yaml` 分流「課程線、評量線、學生觀察線、家長溝通線」
- 用 `content/**/*.md` 存「真正備課內容」
- 用 `manifests/*.yaml` + `publish/build.yaml` 讓專案能被「一鍵打包輸出」成網站/PDF/Word

> 補充：YAML 內容可用中文（含 key 也可）。為了跨工具解析穩定，採用「Key 英文、Value 中文」的策略。

---

## 三層記憶模型

```
┌──────────────────────────┐
│ LAYER 1  Teacher Memory  │
│ TeacherOS.yaml           │
│ 「我是誰／怎麼教」           │
└─────────────┬────────────┘
             │ 定錨方法與語氣
             ▼
┌──────────────────────────┐
│ LAYER 2  Project Memory  │
│ projects/<p>/project.yaml│
│ 「這個專案在哪裡」           │
└─────────────┬────────────┘
             │ 分流工作脈絡
             ▼
┌──────────────────────────┐
│ LAYER 3  Working Memory  │
│ working/lesson.yaml      │
│ working/assessment.yaml  │
│ working/students.yaml    │
│ working/communication.yaml│
│ 「今天推進哪一條線」          │
└──────────────────────────┘

（內容世界：projects/<p>/content/**/*.md）
```

### Layer 1：TeacherOS.yaml

**用途**：定義「你是怎樣的老師」與「AI 該如何協助」。像作業系統設定檔，**少改、長用**。

放什麼：教學哲學、年級範圍、常用輸出格式、差異化矩陣、回應風格。

### Layer 2：Project（projects/\<p\>/project.yaml）

**用途**：專案生命線：目的、背景限制、當前焦點、下一步。它是 AI 下次接續工作的「起點」。

**關鍵原則**：Project.yaml 是「狀態」，不是「完整報告」。先用 Minimal 版啟動，再滾動式增補。

### Layer 3：Working（projects/\<p\>/working/*.yaml）

**用途**：把同一個專案內的不同工作線拆開，避免混線。

- `lesson.yaml`：教學階段理解（不是每堂課一份）
- `assessment.yaml`：證據來源、rubric 維度、評量敘述規則
- `students.yaml`：班級能量、困難點、成長跡象（供回饋/評語）
- `communication.yaml`：家長訊息主軸、疑慮、溝通排程

**只在需要時才出生**：當你開始反覆做某類任務（例如一直在寫家長信），就開一個對應的 sub-yaml。

---

## YAML 與 Markdown 的分工表

| 類型 | 放什麼 | 典型檔案 | 何時更新 |
|------|--------|----------|----------|
| YAML（結構/狀態） | 核心意圖、進度、下一步、規則、分類 | TeacherOS.yaml、project.yaml、working/*.yaml | 每次工作結束「更新狀態」 |
| Markdown（內容/輸出） | 教案文字、故事全文、活動細節、講義、板書、反思 | content/**/*.md | 每次產出可直接使用的備課內容 |

---

## 每日工作流程

1. **載入**：丟 TeacherOS.yaml + project.yaml（以及今天要推進的 working/*.yaml）
2. **協作**：自由發散設計課程/評量/家長信，產出 Markdown 內容
3. **更新**：收工前請 AI「只更新變動區塊」到 YAML（不要重寫全部）
4. **存檔**：把更新後 YAML 與新增/修改的 Markdown 存回資料夾

---

## 檔案與資料夾建議結構

```
TeacherOS-Repo/
├── ai-core/
│   └── teacheros.yaml
├── projects/
│   └── <專案名>/
│       ├── project.yaml
│       ├── working/
│       │   ├── lesson_01.yaml
│       │   ├── assessment.yaml
│       │   ├── students.yaml
│       │   └── communication.yaml
│       ├── content/
│       │   ├── overview.md
│       │   ├── lessons/day01.md
│       │   └── stories/story_01.md
│       ├── assets/
│       └── exports/
├── manifests/
│   └── <專案名>.yaml
└── publish/
    ├── build.yaml
    └── templates/
```

---

## 實務建議與常用 Prompt

### 何時建立 lesson.yaml

`lesson.yaml` 代表「教學階段」，不是「單堂課」。建立新 lesson.yaml 的三個訊號：
- **教學意圖改變**：從「適應勞動」轉到「理解責任」
- **教學策略轉向**：從故事導入改成學生自主/實作主導
- **班級狀態質變**：能量、抵抗、合作氛圍出現明顯轉折

若只是換活動、換故事、內容細節調整：**只更新 Markdown**。

### 何時只更新 Markdown

- 你今天多寫了一段故事全文、增加了講義題目、調整了活動流程細節
- 但「核心目標/階段/下一步教學動作」沒有變

### 請 AI 更新 YAML 的 Prompt 範例

**Prompt A：收工時更新 Project（Minimal）**
```
請根據我們今天的討論，更新 project.yaml，只更新以下區塊：current_focus、next_action。
不要改動其他欄位。輸出為完整 YAML（可直接覆蓋檔案）。
```

**Prompt B：蒸餾 lesson.yaml（只留結構理解）**
```
請把今天的課程設計內容「蒸餾」成 lesson_01.yaml：
1) 不要包含故事全文或活動逐字稿
2) 只保留：theme、developmental_focus、current_phase、core_pedagogical_move、student_response、next_teaching_move
3) 用中文 value、英文 key
```

**Prompt C：從對話生成 lesson.md**
```
請把我們今天定案的教案輸出成 content/lessons/day01.md，包含：課程目標、材料、
流程（分段+時間）、教師講述重點、學生任務、收束反思提問。最後加一段「備忘」給我（教師用）。
```
