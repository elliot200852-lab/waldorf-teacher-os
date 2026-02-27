# TeacherOS — AI 協作移交文件（AI_HANDOFF）

> 這份文件是 TeacherOS 的**通用 AI 入口**。
> 任何 AI 助理在對話開始時讀取此文件，即可立刻定位「你在協助誰、系統邏輯是什麼、現在做什麼、如何工作」。
> **不需要 David 重新解釋，直接進入工作狀態。**

---

## 你的第一步：依序讀取以下檔案

在開始任何工作之前，請先完整讀取以下檔案，順序不可顛倒：

**Step 1 — 教師身份層（必讀）**
`ai-core/teacheros.yaml`
→ 讀完你會知道：David 是誰、教學哲學、工作偏好、AI 協作目標

**Step 2 — 差異化教學框架（必讀）**
`projects/_di-framework/project.yaml`
→ 讀完你會知道：所有課程設計的方法論規則、兩個軸線定義、模板強制要求、產出品質標準、輸出格式協議、reference 機制

**Step 3 — 品質標準（必讀）**
`projects/_di-framework/content/strategy-output-quality-standard.md`
→ 讀完你會知道：所有差異化教學建議的產出品質底線——先說人再說策略、禁止抽象標籤、具體課堂畫面感

**Step 4 — 英文課 DI 模板主控索引（如進行英文課工作，必讀）**
`projects/_di-framework/content/english-di-template.md`
→ 讀完你會知道：對話開始協議、區塊架構、產出路徑規範、進度錨點機制

**Step 5 — 今日工作的班級或科目**
`projects/class-{9c/8a/7a}/project.yaml`（依 David 指定）
→ 讀完你會知道：今天要推進哪個班級、目前焦點是什麼

讀完後，向 David 確認：「我已載入系統，今天要做什麼？」

---

## 一、你在協助誰

**David**，台灣體制外華德福實驗學校的教師。

| 欄位 | 內容 |
|------|------|
| 教學年級 | 七、八、九年級 |
| 身份角色 | 9C 班導師；同時教 7A、8A、9C 英文；教 9C 主課程 |
| 教學科目 | 英文、人文與社會、歷史、跨領域主題課程 |
| 工作方式 | 語音輸入為主、系統建構型思考、專案式設計 |
| 學校性質 | 依台灣實驗教育三法運作，無外部課綱約束，教師擁有完整課程自主權 |
| 成功定義 | 學生的發展性目標（身心靈整合、長期人格成熟），不是考試成績 |
| 時間制度 | 採「學季制」，兩學季 = 一學年（相當於上下學期） |

**David 的 AI 時代定位：意義架構師（Meaning Architect）**
使用 AI 技術自動化課程規劃與行政作業，將節省的精力 100% 重新投入教室中無法被數位化的人文互動。

---

## 二、TeacherOS 系統架構

### 三層記憶模型

```
Layer 1 — teacheros.yaml（教師身份層）
  路徑：ai-core/teacheros.yaml
  用途：教學哲學、工作偏好、AI 協作目標
  原則：核心不變。每次對話必須載入。

Layer 2 — project.yaml（專案記憶層）
  路徑：projects/<專案名>/project.yaml
  用途：專案目的、當前焦點、下一步
  原則：AI 下次工作的「起點」。

  重要：_di-framework/project.yaml 是共用框架，
        每次工作前必須在班級 project.yaml 之前載入。

Layer 3 — working/*.yaml（工作線記憶層）
  路徑：projects/<班級>/working/students.yaml
        projects/<班級>/working/english-session.yaml（進度錨點）
  用途：學生 DI 樣態、英文課工作進度與版本追蹤
```

### 資料夾架構

```
WaldorfTeacherOS-Repo/
│
├── ai-core/
│   ├── teacheros.yaml               ← [必讀 Step 1] 教師身份層
│   └── AI_HANDOFF.md                ← 本文件
│
├── projects/
│   │
│   ├── _di-framework/               ← [必讀 Step 2] 差異化教學共用框架
│   │   ├── project.yaml
│   │   ├── reference/               ← 方法論參考文件
│   │   │   ├── strategy-analysis-quality-example.md  ← The Giver 策略分析範例（品質基準）
│   │   │   └── block1-output-example-draft.md        ← Block 1 教學大綱產出範例
│   │   └── content/
│   │       ├── system-logic-map.md                   ← 母文件：三維定位系統
│   │       ├── strategy-output-quality-standard.md   ← [必讀 Step 3] 產出品質標準
│   │       ├── english-di-template.md                ← 英文課主控索引（已建立）
│   │       ├── english-di-block1.md                  ← 區塊一：學季整體規劃（已建立、已校準品質）
│   │       ├── english-di-block2.md                  ← 區塊二：班級實際教學（已建立）
│   │       └── main-lesson-di-template.md            ← 主課程 DI 模板（待建立）
│   │
│   ├── class-9c/                    ← 9C 班（導師班：主課程 + 英文）
│   │   ├── project.yaml
│   │   ├── reference/               ← 班級參考文件
│   │   ├── working/
│   │   │   ├── students.yaml            ← 學生 DI 樣態（待填入）
│   │   │   └── english-session.yaml     ← 英文課進度錨點（已建立）
│   │   ├── content/english/             ← 班級視角產出目錄
│   │   ├── english/
│   │   │   ├── content/                 ← 英文科目視角產出目錄
│   │   │   └── reference/              ← 英文科參考文件
│   │   └── main-lesson/
│   │       ├── content/                 ← 主課程產出目錄
│   │       └── reference/              ← 主課程參考文件
│   │
│   ├── class-8a/                    ← 結構同 class-9c（無 main-lesson）
│   └── class-7a/                    ← 結構同 class-9c（無 main-lesson）
│
├── publish/                         ← 輸出打包（待建立轉換腳本）
└── manifests/                       ← 輸出打包（未來使用）
```

---

## 三、英文課 DI 模板架構

### 區塊化設計

```
english-di-template.md（主控索引）
    │
    ├─ Block 1：學季整體規劃（english-di-block1.md）【已建立、已校準品質】
    │   Step 1 教師輸入 → Step 2 AI 雙軸檢核 → Step 3 產出教學大綱
    │   必要欄位：標題、班級、授課老師、教學目標、教學策略、
    │             教學規劃、學生任務、評量方式（含佔分百分比）
    │   寫作風格：每條兩句話如寫詩、語言基本功不可省略
    │   品質範例：reference/block1-output-example-draft.md
    │
    └─ Block 2：班級實際教學（english-di-block2.md）【已建立】
        ├─ 2-A：單元教學流程設計
        │   三階段對話流程：策略層（AI 分析）→ 教師選擇 → 產出
        │   彈性單元（單節 / 多節 / 主題式）+ 固定 45 分鐘四段結構
        │   （Warm-up → Main Activity → Check → Closing）
        │
        └─ 2-B：差異化任務與驗收回饋機制設計
            ├─ 課中差異化延伸（預裝式，不需老師即時指派）
            ├─ 家庭任務（習慣導向、輕量、可驗收）
            └─ 減負驗收機制（同儕支援方式）
```

### 防迷路機制：進度錨點

- 每個班級維護一份 `working/english-session.yaml`
- 每次對話開始：AI 讀取錨點並向教師報告當前位置
- 每次對話結束：AI 更新錨點（位置 + 決定 + 下一步）
- 教師重新定位指令：說「回到中軸」即可

### 產出管理：雙路徑 + 版本控制 + Google Docs 輸出

| 事項 | 規則 |
|------|------|
| 儲存位置 | 同時存入班級視角（`content/english/`）與科目視角（`english/content/`）|
| 命名格式 | `{類型}-v{N}-{YYYYMMDD}.md`（例：`english-syllabus-v1-20260227.md`）|
| 版本策略 | 不覆蓋舊版，每次新建版本；老師自行決定哪個版本列印 |
| 更新規則 | 教師指定更新時，需明確確認，兩路徑同步更新 |
| 確認版本後 | Pandoc 轉 .docx → 上傳 Google Drive → 自動成 Google Docs |

### Reference 資料夾機制

- 教師說「請把這一份文件列為重要參考文件」→ AI 存入對應 reference/ 資料夾
- 三個層次：DI 框架層 / 班級層 / 科目層
- 範疇不明確時 AI 主動詢問

---

## 四、產出品質標準（所有 AI 必須遵守）

**完整規範：** `_di-framework/content/strategy-output-quality-standard.md`
**品質範例：** `_di-framework/reference/strategy-analysis-quality-example.md`

核心規則摘要：

1. **先說人，再說策略**：每類學生（A/B/C/D）以心理素描開頭，再展開教學做法
2. **禁止抽象標籤**：「鷹架支持」「延伸挑戰」「連結興趣」不可作為策略本身——必須展開為課堂中的具體畫面
3. **每條策略有畫面感**：老師讀完後腦海能浮現課堂場景
4. **語氣像教師專業對話**：帶溫度、有人味，華德福精神自然融入但不堆砌術語
5. **可直接操作**：老師讀完可以明天帶進教室
6. **語言基本功不可省略**：華德福英文課不排斥單字、句型、文法基礎——這是語言的肉體

---

## 五、2026-02-27 本次 session 完成的工作

| 項目 | 說明 |
|------|------|
| Reference 資料夾機制 | 建立 8 個 reference 資料夾（_di-framework、各班級、各科目層），邏輯寫入 project.yaml |
| 輸出格式協議 | 確認版本後 Markdown → Pandoc → .docx → Google Docs，已寫入 project.yaml |
| 產出品質標準 | 建立 strategy-output-quality-standard.md（強制品質指令）與 strategy-analysis-quality-example.md（The Giver 範例） |
| 品質標準寫入 project.yaml | output_quality_standard 區塊，含 5 條核心規則與自檢清單 |
| Block 2 模板建立 | english-di-block2.md 完整建立（2-A 單元教學流程 + 2-B 差異化任務與驗收回饋機制設計） |
| Block 1 品質校準 | 教學目標改為條列式（兩句話如詩）、教學策略精簡加幽默、語言基本功列為哲學底線 |
| Block 1 範例 | block1-output-example-draft.md（9C 教學大綱完整範例），已驗證 PDF 排版 |
| Pandoc 安裝 | 已在系統安裝 Pandoc，可執行 .md → .docx 轉換 |

---

## 六、目前專案狀態（2026-02-27 更新）

| 專案 | 狀態 | 說明 |
|------|------|------|
| `_di-framework` | 進行中 | 核心架構完成；Block 1 已建立並校準品質；Block 2 已建立；品質標準已建立 |
| `class-9c` | 待啟動 | 結構完整（含 reference），等待：學生樣態填入後即可開始備課 |
| `class-8a` | 待啟動 | 結構完整（含 reference），等待：學生資料填入 |
| `class-7a` | 待啟動 | 結構完整（含 reference），等待：學生資料填入 |

---

## 七、接下來前三件優先工作

1. **填入各班 students.yaml**
   - 需 David 提供：英文課「高能力」「高動機」的定義、A/B/C/D 人數分布、學習優勢分布
   - 可以先從一個班開始（建議 9C，導師班）

2. **實際執行 Block 1 — 為一個班級產出教學大綱**
   - Block 1 模板與品質標準已就緒，可以開始實際產出第一份教學大綱
   - 建議從 9C 開始

3. **建立主課程 DI 設計模板**（`main-lesson-di-template.md`）
   - 適用 9C，連續 15 堂（3 週）的弧線邏輯，與英文課結構不同

---

## 八、工作協議（你必須遵守）

### 每次對話開始

1. 讀取 `ai-core/teacheros.yaml`
2. 讀取 `projects/_di-framework/project.yaml`
3. 讀取 `projects/_di-framework/content/strategy-output-quality-standard.md`（品質標準）
4. 讀取 `projects/_di-framework/content/english-di-template.md`（進行英文課工作時）
5. 讀取對應班級的 `working/english-session.yaml`（確認進度錨點）
6. 向 David 報告當前位置，等待確認後開始

### 每次對話結束

1. 條列今天確認的決定
2. 更新 `english-session.yaml`（只改動有變化的欄位）
3. 告知 David 下次需要準備什麼

### 輸出規範

| 情境 | 格式 |
|------|------|
| 備課內容、長文輸出 | Markdown（雙路徑、版本命名） |
| 確認版本後的正式文件 | Pandoc 轉 .docx → Google Docs |
| 狀態更新、結構變動 | YAML（只寫改動的區塊） |
| 語言 | 繁體中文 |
| 表情符號 | 不使用 |
| 教學策略建議 | 必須符合品質標準（strategy-output-quality-standard.md） |

---

*本文件最後更新：2026-02-27*
*GitHub：github.com/elliot200852-lab/waldorf-teacher-os*
