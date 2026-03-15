---
aliases:
  - "新教師模板說明"
---

# Workspace 快速指南

> 本資料夾是你的**個人教學工作空間**。
> David 會透過 `add-teacher.py` 自動建立你的工作空間，
> 資料夾命名格式為 `Teacher_{你的姓名}`（例：`Teacher_林信宏`），
> 存放於 `workspaces/Working_Member/` 下。

---

## 什麼是 Workspace？

**Workspace（工作空間）** 是 TeacherOS 為每位老師設計的個人化檔案夾。

它包含：
- **你的教師身份與教學哲學** — 一次性填寫，供 AI 長期參考
- **你的班級專案** — 每個班級一個資料夾，記錄學生、課程進度、產出內容
- **個人化的設定與模板** — 覆寫系統預設，適應你的教學風格

### 核心理念：三層內容模型

TeacherOS 採用「**共享參考 → 範本複製 → 老師創作**」的三層架構：

```
第 1 層：共享參考庫（Shared Reference）
  └─ ai-core/teacheros.yaml              ← 系統路由中樞
     ai-core/teacheros-foundation.yaml   ← 華德福教育共用根基
     ai-core/reference/                  ← 教學哲學完整參考文件
  └─ 系統標準、最佳實踐、理論框架
     [所有老師共用，大家可以讀，但只有 David 修改]

第 2 層：工作空間模板（Workspace Template）
  └─ workspaces/_template/
  └─ 新老師的起點：完全可客製化的空白範本
     複製時自動適應個別老師的需求

第 3 層：老師創作層（Teacher-Created Content）
  └─ workspaces/Working_Member/Teacher_{姓名}/
  └─ 你的班級、課程設計、教材、評量、進度記錄
     完全由你掌控、長期累積、AI 協助維護
```

這個設計確保：
- **標準化的教學框架** 保持一致性
- **個人化的執行** 尊重每位老師的獨特風格
- **集體知識** 能被記錄與分享

---

## 快速開始

### 第一步：David 建立你的 Workspace

David（管理員）會執行 `python3 setup/add-teacher.py`，自動為你建立工作空間：

```
workspaces/Working_Member/Teacher_{你的姓名}/
```

你不需要手動複製範本，腳本會自動完成。

### 第二步：填寫身份資訊

編輯下列檔案，填入你的資訊：

1. **`workspace.yaml`** — 工作空間基本設定
   - 你的姓名、email、職稱
   - 你管理的班級清單

2. **`teacheros-personal.yaml`** — 個人教學哲學（最重要的檔案）
   - 教育信念、教學方法、科目理念
   - AI 系統會在每次對話時讀取，用來理解你的教學風格
   - 華德福共用哲學已在 `teacheros-foundation.yaml` 中提供，你只需填入「你自己的」部分

### 第三步：建立班級

每個你教的班級對應一個資料夾：

```
workspaces/Working_Member/Teacher_林信宏/
  ├── projects/
  │   ├── class-8a/           ← 八年級
  │   │   ├── project.yaml
  │   │   ├── students.yaml
  │   │   ├── english/
  │   │   │   ├── di-profile.yaml
  │   │   │   └── content/
  │   │   ├── working/
  │   │   │   └── english-session.yaml
  │   │   └── ...
  │   └── class-7th-homeroom/ ← 七年級導師課
  │       └── ...
```

---

## 重要檔案說明

### 核心設定檔

| 檔案 | 用途 | 填寫難度 |
|------|------|--------|
| **`workspace.yaml`** | 記錄老師身份、班級清單、工作空間狀態 | 簡單 |
| **`teacheros-personal.yaml`** | 個人教學哲學、科目理念（AI 長期參考，最重要的檔案） | 中等 |
| **`README.md`** | 本檔案，說明工作空間結構 | — |

### 班級檔案（在 `projects/class-{code}/` 中）

| 檔案 | 用途 |
|------|------|
| **`project.yaml`** | 班級基本設定、班級背景、教學科目 |
| **`students.yaml`** | 學生名單、DI 分類（差異化教學） |
| **`{subject}/di-profile.yaml`** | 各科的學生能力×動機分析 |
| **`working/{subject}-session.yaml`** | 工作進度錨點（Block / Step / 下一步） |
| **`{subject}/content/`** | 備課內容、教材、評量（產出資料夾） |

---

## 工作範例參考

想看看完成的 workspace 長什麼樣？

**參考位置**：`workspaces/工作範例參考/`

這個範例展示了：
- 完整的班級資料夾結構
- 已填寫的 project.yaml、students.yaml
- 英文課的 di-profile 與工作進度
- 產出的教材與備課內容

你可以：
1. 直接打開這個資料夾查看結構
2. 複製其中的某個檔案作為你的範本
3. 參考其內容決定自己的班級設定

**重點**：這個範例的內容是虛構的（學生 ID 是代碼），你的資料夾應該填入真實的班級名稱與學生資訊。

---

## 工作流程：AI 如何協助你

### 當你開始新的工作時：

1. **AI 讀取你的身份** → 載入 teacheros-personal.yaml
2. **AI 掃描班級進度** → 讀取 working/*.yaml 了解你在哪一步
3. **AI 報告現況** → 「你的八年級英文在 Block 2 第 3 步，接下來需要設計 Unit 2 的課程」
4. **開始工作** → 你說「設計下一個單元」，AI 執行

### 當你完成工作時：

1. **AI 記錄決定** → 更新 working/*.yaml 的進度錨點
2. **AI 保存產出** → 把課程設計、教材存到 content/ 資料夾
3. **AI 告知下一步** → 「下次可以開始備課細節」或「等你上課後再評量」

---

## 檔案結構總覽

```
workspaces/
├── _template/                    ← 新老師的起點（複製這裡）
│   ├── README.md                 ← 你在看的檔案
│   ├── workspace.yaml            ← 工作空間設定
│   ├── teacheros-personal.yaml   ← 個人教學哲學（最重要）
│   └── projects/
│       └── _class-template/      ← 班級資料夾的範本
│           ├── project.yaml
│           ├── students.yaml
│           ├── {subject}/
│           │   ├── di-profile.yaml
│           │   └── content/
│           └── working/
│               └── {subject}-session.yaml
│
├── 工作範例參考/                  ← 完整範例
│   ├── workspace.yaml
│   ├── teacheros-personal.yaml
│   └── projects/
│       └── class-claude/
│
└── Working_Member/               ← 所有活躍教師的工作空間
    ├── Codeowner_David/          ← David（管理員）的工作空間
    │   ├── workspace.yaml
    │   ├── teacheros-personal.yaml
    │   └── projects/
    │       ├── class-9c/
    │       └── class-9d/
    │
    └── Teacher_林信宏/            ← 你的工作空間（由 add-teacher.py 建立）
        ├── workspace.yaml
        ├── teacheros-personal.yaml
        └── projects/
            └── class-8a/
                └── ...
```

---

## 常見問題

### Q：我是公立學校老師，不是華德福。我需要改變什麼？

**A**：完全沒問題。

- TeacherOS 支援任何教學哲學
- 在 `teacheros-personal.yaml` 中填寫**你的**教育信念，不必侷限於華德福
- AI 系統會根據你的哲學來設計課程，不會強制特定風格

### Q：我是小學老師，不需要「差異化教學」或「DI Profile」嗎？

**A**：差異化教學（Differentiated Instruction, DI）是所有年級、所有科目都適用的教學策略。

- 小學、中學、高中都需要
- 英文、數學、自然、藝術都需要
- 如果你有特殊生或學習進度差異大的班級，DI Profile 會特別有幫助
- 不用也沒關係，但使用它會讓 AI 設計更貼近學生需求的課程

### Q：我可以只填寫必要欄位，其他留空嗎？

**A**：可以。

- 「填空」的欄位都是選項，不填不會出錯
- AI 會根據有填的欄位進行工作，對空白欄位使用預設值
- 你可以隨時補充、修改

### Q：我的班級資訊敏感（含學生名單），怎麼保護隱私？

**A**：

- `roster.yaml`（實名學生名單）通常加入 `.gitignore`，不上傳到雲端
- `students.yaml` 可以用學生 ID（如 CL-01、CL-02）代替真名
- 如果用 Git 管理，確保 `.gitignore` 包含敏感檔案
- 將工作空間存在本機，定期備份

### Q：多位老師可以共享一個班級的工作空間嗎？

**A**：目前的設計是**一個工作空間一個老師**。

- 如果你們要協作，可以在專案層面分工（例如 David 負責英文、Lin 負責導師課）
- 每人有自己的 workspace，在班級資料夾層面互相參考
- 未來可能支援協作機制，目前建議通過 Git 或檔案分享來協調

### Q：我之前用其他系統記錄課程。我的筆記能轉移到這裡嗎？

**A**：可以逐步轉移。

- AI 可以幫你將舊筆記轉換成 TeacherOS 的格式（Markdown 或 YAML）
- 建議：先建立新班級的基本結構，再慢慢搬遷歷史資料
- 不著急，邊用邊適應效果更好

---

## 聯絡與支援

有任何問題或建議，請聯絡：

**David**（系統設計者 & 主持人）

- 對 TeacherOS 結構有疑問？
- 想客製化工作流程？
- 發現系統 bug 或不順手的地方？

直接聯絡我，我們一起改進。

---

## 最後的話

這份文件很長，但**不需要一次全讀**。

建議流程：
1. 先讀「快速開始」，複製範本，填寫基本資訊
2. 建立第一個班級，試著用 AI 設計一堂課
3. 邊用邊回來查詢「檔案說明」或「常見問題」
4. 3-5 堂課後，你會自然理解整套系統

**歡迎來到你的個人教學工作空間！**
