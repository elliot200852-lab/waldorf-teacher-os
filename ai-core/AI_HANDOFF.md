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

**Step 6 — 學生知識庫操作協議（凡涉及學生資料時必讀）**
`projects/_di-framework/content/student-knowledge-protocol.md`
→ 讀完你會知道：如何讀取三層知識庫、角色確認必問問題、資料寫入路由、不可跳過的規則

**Step 7 — 導師模組主控索引（如進行導師業務、行事曆規劃，必讀）**
`projects/_di-framework/content/homeroom-template.md`
→ 讀完你會知道：導師四大作業區塊 (HM Block 1-4)、Google 日曆匯入機制、盲區提醒防呆 SOP

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
│   ├── AI_HANDOFF.md                ← 本文件
│   ├── system-status.yaml           ← 系統狀態快照（AI 開工前快速掃描）
│   └── reviews/                     ← 定期 Context Review 存放處（AI 平時不載入）
│       └── context-review-20260228.md
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
│   │       ├── english-di-template.md                ← 英文課主控索引
│   │       ├── english-di-block1.md                  ← 區塊一：學季整體規劃
│   │       ├── english-di-block2.md                  ← 區塊二：班級實際教學
│   │       ├── english-di-block3.md                  ← 區塊三：教學歷程紀錄與觀察
│   │       ├── english-di-block4.md                  ← 區塊四：學習評量與教學結案
│   │       ├── student-knowledge-protocol.md          ← [必讀 Step 6] 學生知識庫操作協議
│   │       ├── homeroom-template.md                   ← [必讀 Step 7] 導師模組主控索引
│   │       └── main-lesson-di-template.md            ← 主課程 DI 模板（待建立）
│   │
│   ├── class-9c/                    ← 9C 班（導師班：主課程 + 英文）
│   │   ├── project.yaml                ← 班級入口（含 class_files 檔案索引）
│   │   ├── roster.yaml                 ← 學生身份名冊（gitignored，含真名）
│   │   ├── students.yaml               ← 班級共用 DI 摘要 + 跨科特殊狀況
│   │   ├── reference/                  ← 班級參考文件
│   │   ├── working/
│   │   │   └── english-session.yaml    ← 英文課進度錨點
│   │   ├── english/
│   │   │   ├── lesson.yaml             ← 課程結構
│   │   │   ├── di-profile.yaml         ← 英文 DI 觀察（22 人完成）
│   │   │   ├── assessment.yaml         ← 英文評量設定
│   │   │   ├── content/                ← 英文產出目錄
│   │   │   └── reference/              ← 英文參考文件
│   │   ├── main-lesson/
│   │   │   ├── lesson.yaml
│   │   │   ├── di-profile.yaml         ← 主課程 DI 觀察（待填入）
│   │   │   ├── assessment.yaml
│   │   │   └── reference/              ← 主課程參考文件
│   │   └── homeroom/
│   │       ├── session.yaml            ← 導師進度錨點（含 Google iCal 更新紀錄）
│   │       ├── reference/
│   │       │   └── calendar.md         ← 班級獨立行事曆（已聯動 Google iCal）
│   │       └── content/                ← 導師產出（活動、溝通草稿）
│   │
│   ├── class-8a/                    ← 結構同 class-9c（無 main-lesson）
│   └── class-7a/                    ← 結構同 class-9c（無 main-lesson）
│
├── setup/                           ← 環境設定與使用說明
│   ├── environment.env.example      ← 個人設定範本（已提交）
│   ├── environment.env              ← David 個人設定（gitignored）
│   ├── setup-check.sh               ← 環境檢查腳本（新老師第一次使用）
│   └── teacher-guide.md             ← 教師試用手冊（已 publish 至 Google Drive）
│
├── publish/
│   └── build.sh                     ← 自動輸出腳本（.md → .docx → Google Drive）
│
└── manifests/                       ← 輸出打包（未來使用）
```

---

## 三、英文課 DI 模板架構

### 區塊化設計與 TeacherOS 工作流

```
[起點] Block 1：學季整體規劃（english-di-block1.md）
    ├─ 課前準備阻擋機制：AI 必須在 Step 1 攔截並要求老師提供研究/文本分析檔案，除非獲強制明確授權。
    └─ 產出：english-syllabus.md（教學大綱、核心檢核任務），作為最高指導原則。

[日常] Block 2：班級實際教學（english-di-block2.md） ◀︎─┐
    ├─ 2-A：單元教學流程設計（固定 45 分鐘四段結構）         │ (AI 主動查閱 Block 3 最近期紀錄，提出修正建議)
    └─ 2-B：差異化任務與驗收回饋機制設計                  │
                                                     │
[日常] Block 3：教學歷程紀錄與觀察（english-di-block3.md）─┘ (可獨立隨時插入)
    ├─ 收集與解構：將一次性的長文描述或錄音拆解，具備學生 ID 模糊對齊能力。
    └─ 產出三維紀錄庫 (皆帶 [YYYY-MM-DD] 日期標籤)：
         ├─ student-logs/{ID}-log.md (個別學生動態)
         ├─ unit-logs.md (班級整體進度與困難)
         └─ teacher-reflections.md (教學反思)
                                                     │
[結案] Block 4：學習評量與歷程結案（english-di-block4.md）◀︎─┘ (期末總結)
    ├─ 教學歷程合併 (讀取 unit-logs + teacher-reflections)
    └─ 期末專屬評量 (讀取 student-logs + 學季大綱任務 + 最終成績)
         └─ 產出單一合併檔：student-assessments-YYYYMMDD.md
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

## 五、歷次 session 完成工作記錄

### 2026-02-27 第一次 session

| 項目 | 說明 |
|------|------|
| Reference 資料夾機制 | 建立 8 個 reference 資料夾（_di-framework、各班級、各科目層），邏輯寫入 project.yaml |
| 輸出格式協議 | 確認版本後 Markdown → Pandoc → .docx → Google Docs，已寫入 project.yaml |
| 產出品質標準 | 建立 strategy-output-quality-standard.md 與 strategy-analysis-quality-example.md |
| Block 2 模板建立 | english-di-block2.md 完整建立（2-A 單元教學流程 + 2-B 差異化任務與驗收機制） |
| Block 1 品質校準 | 教學目標條列式（兩句話如詩）、語言基本功列為哲學底線 |
| Block 1 範例 | block1-output-example-draft.md（9C 教學大綱完整範例） |
| Pandoc 安裝 | 系統已安裝 Pandoc 3.9 |
| v04 版本 | 打 tag 推上 GitHub |

### 2026-02-28 第六次 session：TeacherOS 系統四區塊閉環完備

| 項目 | 說明 |
|------|------|
| 課前準備硬性阻擋 | 更新 `teacher-guide.md` 與 `Block 1` 模板，導入對話開頭主動詢問並阻擋無檔案狀態的機制（除非明確授權放行）。 |
| Block 3 實作完成 | 建立 `english-di-block3.md` 教學歷程紀錄與觀察：定義非同步模糊比對與拆解能力，建立 MD 格式的「三維紀錄庫」(學生/單元/反思) 取代舊底 YAML 囤積。寫入時強制綁定 `[YYYY-MM-DD]` 標籤。 |
| Block 4 實作完成 | 建立 `english-di-block4.md` 學習評量與教學結案：定義結案的「合併單檔評量」總檔架構，設定含 200 字「全班歷程摘要」及個別學生（質性描述、大綱檢核、分數）的輸出模板。**AI 產出評量需還原真名，並受 `.gitignore` 本機隱私保護**。 |
| 檢索降載機制 | 修改 `Block 2` 前置讀取，設定為只讀取日誌「最近三筆日期」，避免資訊超載；全面繪製 1 至 4 區塊的系統連接圖示。 |

### 2026-02-28 第五次 session：9C 英文教學大綱設計

| 項目 | 說明 |
|------|------|
| 108 課綱語言參考表 | `108-curriculum-language-reference.md` 存入 `_di-framework/content/`；寫入 `english-di-template.md` 主控索引（語言基本能力參考對照章節） |
| 9C 英文 reference 建立 | 存入兩份研究文件：`9C下學期英文差異化教學策略研究.md`、`The house on Mango Street 小說教學研究報告範本.md` |
| 9C 英文教學大綱 v1 | 以三份參考文件為基礎設計，確認三軸架構（小說 + 語言工坊 + 108 課綱），雙路徑存檔 + Google Drive 輸出完成 |
| 評量比例定案 | 小說討論 20% + 創意寫作 20% + 詞彙溝通 25% + 文法閱讀 25% + 學習歷程 10% |
| Block 1 完成 | 9C 英文 Block 1 全部流程跑完，english-session.yaml 進度錨點更新 |

### 2026-02-28 第四次 session：學生知識庫建構

| 項目 | 說明 |
|------|------|
| 架構重構 | 建立 `roster.yaml`（真名+ID，gitignored）、`students.yaml`（班級共用）、各科 `di-profile.yaml` |
| 學生知識庫協議 | 建立 `student-knowledge-protocol.md`（角色確認必問、讀寫路由表），登錄於 AI_HANDOFF |
| 9C DI 分類 | 完成 9C 全班 22 人英文課 DI 觀察（ABCD、優勢、細項、成績）輸入 |

### 2026-02-28 第三次 session：系統盤點與狀態快照

| 項目 | 說明 |
|------|------|
| Context Review | 全資料夾 30+ 檔案完整審查，產出 `ai-core/reviews/context-review-20260228.md` |
| system-status.yaml | 建立精簡系統狀態快照（20 行），供 AI 開工前快速掃描 |
| AI_HANDOFF.md 更新 | 登錄新檔案、更新專案狀態表 |

### 2026-02-27 第二次 session

| 項目 | 說明 |
|------|------|
| Google Drive 自動輸出 | build.sh 建立，動態讀取 environment.env，路徑自動解析，AI 代跑無需教師輸入指令 |
| Google Drive 資料夾 | 建立 class-9c/8a/7a 各 english 子資料夾，已與本機同步 |
| 環境設定系統 | setup/ 資料夾建立：environment.env.example、setup-check.sh、environment.env（David 個人，gitignored） |
| 教師試用手冊 | teacher-guide.md 建立，含 GitHub clone、三種 AI 工具選項、TeacherOS 改寫說明 |
| 手冊 publish | 教師試用手冊已輸出為 .docx，存入 Google Drive TeacherOS 根目錄 |
| project.yaml 更新 | 輸出格式協議、reference 機制、environment 設定系統全部寫入 |

### 2026-03-01 導師模組與 Google 行事曆連動
| 項目 | 說明 |
|------|------|
| 導師模組框架建立 | 建立 `homeroom-template.md` 定義 HM Block 1-4 工作流、學生日誌標籤分離機制 |
| 9C 導師基礎建設 | 建立 `class-9c/homeroom/` 目錄、進度錨點 `session.yaml` 與 `calendar.md` |
| Google iCal 解析系統 | 建立支援 Google 私人/公開網址的 Python 擷取工具，實現行事曆快照 (Snapshotting) 更新機制 |
| SOP 協議登錄 | 在 `AI_HANDOFF.md` 與 `student-knowledge-protocol.md` 加入導師角色協議 |

| 項目 | 說明 |
|------|------|
| Block 1 寫作風格邊界 | 在 `english-di-block1.md` 新增「寫作風格邊界」規範：禁止道德型收尾句、禁止強調語堆疊、教學目標寫行為而非感受、評量表不加詮釋句 |
| 9C 教學大綱 v2 | 套用新風格邊界，產出 v2，雙路徑存檔，已輸出 Google Drive |
| build.sh 中文化 | Google Drive 輸出全面中文化：資料夾 `班級專案/九年級C班/英文/教學大綱/`，檔名 `教學大綱-V2-20260301.docx` |
| 自動子資料夾分類 | build.sh 依檔名自動判斷類型：教學大綱 / 單元教學 / 差異化任務 / 學習評量 / 教學紀錄 |
| Google Drive 清理 | 刪除舊英文命名檔案，統一移至新中文結構 |

---

## 六、目前專案狀態（2026-03-01 更新）

| 專案 | 狀態 | 說明 |
|------|------|------|
| `_di-framework` | 完成 | Block 1–4 模板、品質標準、reference 機制、輸出協議全部就緒；Block 1 已加入寫作風格邊界 |
| 環境設定系統 | 完成 | build.sh 已中文化，輸出路徑自動分類，Google Drive 結構已重組 |
| 系統狀態快照 | 完成 | `ai-core/system-status.yaml` |
| Context Review | 完成 | `ai-core/reviews/context-review-20260228.md` |
| `class-9c` 英文 | Block 1 完成（v2），等待 Block 2 | 教學大綱 v2 已產出並輸出至 Google Drive；下一步：第一單元課堂設計（Block 2） |
| `class-8a` 英文 | 尚未開始 | 結構完整，等待：students.yaml 填入 |
| `class-7a` 英文 | 尚未開始 | 結構完整，等待：students.yaml 填入 |
| `class-9c` 主課程 | 尚未開始 | 等待：main-lesson-di-template.md 建立後啟動 |
| 教師試用計畫 | 準備中 | 手冊已備妥；9C 大綱 v2 為第一份樣品 |

---

## 七、接下來前三件優先工作

1. **9C 英文 Block 2 — 第一單元課堂設計（第 1–2 週）**
   - 教學大綱 v2 已確認，Block 2 隨時可啟動
   - 設計 2 節小說研讀課 + 2 節語言工坊課的 45 分鐘課堂流程
   - 參照：`english-di-block2.md`、`english-session.yaml`（進度錨點）

2. **8A / 7A 英文 — 填入 students.yaml，啟動 Block 1**
   - 8A 與 7A 結構就緒，等待學生 DI 資料輸入後即可執行大綱設計

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

### 學生資料讀寫協議

> 完整規則請見正式協議文件：
> `projects/_di-framework/content/student-knowledge-protocol.md`

**核心原則（不可跳過）：**
- 教師提供學生資訊前，**必須先問角色**（導師 / 英文老師 / 主課程老師 / 其他科任）
- 角色決定寫入位置（詳見協議文件的角色路由表）
- 日常操作：學生 ID 一律從 `roster.yaml` 查找，不接受以姓名操作
- **期末結案例外（Block 4）**：產出 `student-assessments*.md` 時，AI **必須主動反查還原真實姓名**以利列印。此特定檔案已由 `.gitignore` 排除，嚴禁推送。

### 輸出規範

| 情境 | 格式 |
|------|------|
| 備課內容、長文輸出 | Markdown（雙路徑、版本命名） |
| 確認版本後的正式文件 | Pandoc 轉 .docx → Google Docs |
| 狀態更新、結構變動 | YAML（只寫改動的區塊） |
| 語言 | 繁體中文 |
| 表情符號 | 不使用 |
| 教學策略建議 | 必須符合品質標準（strategy-output-quality-standard.md） |

### Google Drive 輸出協議（AI 必須執行）

每次 .md 版本確認後，AI 必須主動詢問：

> 「這份文件要輸出到 Google Drive 嗎？」

- 教師說「要」→ AI 執行 `./publish/build.sh <md檔案路徑>`，**不需教師輸入任何指令**
- 教師說「不用」→ 跳過，僅保留 .md 版本
- 腳本會自動從路徑解析班級與科目，AI 只需傳入檔案路徑
- 執行後告知教師：「已輸出至 Google Drive，同步後可在 Google Docs 開啟。」

---

## 九、新使用者環境設定

> 若需協助新老師進行本機環境（包含 Google Drive、Pandoc、Git Repo）之設定，
> **請改為查閱 `setup/teacher-guide.md`，該檔案有最完整的操作指南。**

---

*本文件最後更新：2026-03-01（Block 1 精進 + 輸出系統中文化）*
*GitHub：github.com/elliot200852-lab/waldorf-teacher-os*
