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
→ 讀完你會知道：所有課程設計的方法論規則、兩個軸線定義、模板強制要求

**Step 3 — 英文課 DI 模板主控索引（如進行英文課工作，必讀）**
`projects/_di-framework/content/english-di-template.md`
→ 讀完你會知道：對話開始協議、區塊架構、產出路徑規範、進度錨點機制

**Step 4 — 今日工作的班級或科目**
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
│   │   └── content/
│   │       ├── system-logic-map.md          ← 母文件：三維定位系統
│   │       ├── english-di-template.md       ← 英文課主控索引（已建立）
│   │       ├── english-di-block1.md         ← 區塊一：學季整體規劃（已建立）
│   │       ├── english-di-block2.md         ← 區塊二：班級實際教學（待建立）
│   │       ├── english-di-template.md       ← 英文課 DI 模板（已建立）
│   │       ├── main-lesson-di-template.md   ← 主課程 DI 模板（待建立）
│   │
│   ├── class-9c/                    ← 9C 班（導師班：主課程 + 英文）
│   │   ├── project.yaml
│   │   ├── working/
│   │   │   ├── students.yaml            ← 學生 DI 樣態（待填入）
│   │   │   └── english-session.yaml     ← 英文課進度錨點（已建立）
│   │   ├── content/english/             ← 班級視角產出目錄（已建立）
│   │   └── english/content/             ← 英文科目視角產出目錄（已建立）
│   │
│   ├── class-8a/                    ← 結構同 class-9c
│   └── class-7a/                    ← 結構同 class-9c
│
└── manifests/                       ← 輸出打包（未來使用）
```

---

## 三、英文課 DI 模板架構（本 session 核心成果）

### 區塊化設計

```
english-di-template.md（主控索引）
    │
    ├─ Block 1：學季整體規劃（english-di-block1.md）【已建立】
    │   Step 1 教師輸入 → Step 2 AI 雙軸檢核 → Step 3 產出教學大綱
    │   必要欄位：標題、班級、授課老師、教學目標、教學策略、
    │             教學規劃、學生任務、評量方式（含佔分百分比）
    │
    └─ Block 2：班級實際教學（english-di-block2.md）【待建立】
        ├─ 2-A：逐單元教學流程
        └─ 2-B：課外延伸支援（A/B/C/D 差異化）
```

### 防迷路機制：進度錨點

- 每個班級維護一份 `working/english-session.yaml`
- 每次對話開始：AI 讀取錨點並向教師報告當前位置
- 每次對話結束：AI 更新錨點（位置 + 決定 + 下一步）
- 教師重新定位指令：說「回到中軸」即可

### 產出管理：雙路徑 + 版本控制

| 事項 | 規則 |
|------|------|
| 儲存位置 | 同時存入班級視角（`content/english/`）與科目視角（`english/content/`）|
| 命名格式 | `{類型}-v{N}-{YYYYMMDD}.md`（例：`english-syllabus-v1-20260227.md`）|
| 版本策略 | 不覆蓋舊版，每次新建版本；老師自行決定哪個版本列印 |
| 更新規則 | 教師指定更新時，需明確確認，兩路徑同步更新 |

---

## 四、目前專案狀態（2026-02-27）

| 專案 | 狀態 | 說明 |
|------|------|------|
| `_di-framework` | 進行中 | 核心架構完成；英文課 Block 1 已建立；Block 2 待建立 |
| `class-9c` | 待啟動 | 結構完整，等待：學生樣態填入、英文課 Block 2 完成後才能開始備課 |
| `class-8a` | 待啟動 | 結構完整，等待：學生資料填入 |
| `class-7a` | 待啟動 | 結構完整，等待：學生資料填入 |

---

## 五、接下來前三件優先工作

1. **建立 Block 2（班級實際教學）**（`english-di-block2.md`）
   - 2-A：單元教學流程（45 分鐘結構、DI 分層、能力弧線）
   - 2-B：課外延伸支援（四類差異化任務 + 後續追蹤 + students.yaml 回饋）

2. **填入各班 students.yaml**
   - 需 David 提供：英文課「高能力」「高動機」的定義、A/B/C/D 人數分布、學習優勢分布

3. **建立主課程 DI 設計模板**（`main-lesson-di-template.md`）
   - 適用 9C，連續 15 堂（3 週）的弧線邏輯，與英文課結構不同

---

## 六、工作協議（你必須遵守）

### 每次對話開始

1. 讀取 `ai-core/teacheros.yaml`
2. 讀取 `projects/_di-framework/project.yaml`
3. 讀取 `projects/_di-framework/content/english-di-template.md`（進行英文課工作時）
4. 讀取對應班級的 `working/english-session.yaml`（確認進度錨點）
5. 向 David 報告當前位置，等待確認後開始

### 每次對話結束

1. 條列今天確認的決定
2. 更新 `english-session.yaml`（只改動有變化的欄位）
3. 告知 David 下次需要準備什麼

### 輸出規範

| 情境 | 格式 |
|------|------|
| 備課內容、長文輸出 | Markdown（雙路徑、版本命名） |
| 狀態更新、結構變動 | YAML（只寫改動的區塊） |
| 語言 | 繁體中文 |
| 表情符號 | 不使用 |

---

*本文件最後更新：2026-02-27*
*GitHub：github.com/elliot200852-lab/waldorf-teacher-os*
