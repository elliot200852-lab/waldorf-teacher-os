# 學生知識庫操作協議
# Student Knowledge Base Protocol

> **文件性質**：DI 工作的必要前置協議，任何涉及學生資料的操作（讀取或寫入）前，AI 必須先執行本協議。
> **存放位置**：`projects/_di-framework/content/`
> **觸發時機**：每當教師開口描述學生能力、程度或喜好

---

## 一、知識庫架構（讀取地圖）

每個班級的學生知識由三層組成，AI 必須知道各層的功能：

```
projects/class-{x}/
│
├── roster.yaml            ← 身份層（真名 + ID + 座號，gitignored）
│                             → 誰是誰、ID 對照
│
├── students.yaml          ← 班級層（跨科共用）
│                             → 班級整體動態、特殊狀況、DI 統計摘要
│
├── english/
│   └── di-profile.yaml    ← 科目層（英文專屬）
│                             → 英文的定義、ABCD 分類、成績、個別觀察
│
├── main-lesson/
│   └── di-profile.yaml    ← 科目層（主課程專屬）
│
└── {其他科目}/
    └── di-profile.yaml    ← 科目層（依需求建立）
```

### 工作前的 AI 必讀清單

| 工作類型 | 必讀檔案 |
|----------|----------|
| 任何涉及學生的工作 | `roster.yaml` + `students.yaml` |
| 英文課程設計 | + `english/di-profile.yaml` |
| 主課程設計 | + `main-lesson/di-profile.yaml` |
| 產出個別學生評語 | 以上皆讀 + HTML 評量報告（按需讀取個別段落） |

---

## 二、前置角色確認（必要，不可跳過）

**每次教師提供學生資訊前，AI 必須先問：**

> 「請問你現在是以什麼角色提供這份資訊？
>   1. **導師**——班級整體觀察或跨科特殊狀況
>   2. **英文科任老師**——英文課的學生能力、程度、喜好
>   3. **主課程老師**——主課程的學生能力、程度、喜好
>   4. **其他科任老師**——請說明科目名稱」

### 角色 → 寫入位置

| 教師角色 | 資料寫入 | 使用 ID |
|----------|----------|---------|
| 導師 | `students.yaml` 的 `special_cases` 或 `class_dynamic` | 是 |
| 英文老師 | `english/di-profile.yaml` 的 `student_observations` | 是 |
| 主課程老師 | `main-lesson/di-profile.yaml` 的 `student_observations` | 是 |
| 其他科任 | `{科目}/di-profile.yaml`（不存在則先建立） | 是 |

> [!IMPORTANT]
> 學生 ID 必須從 `roster.yaml` 查找（格式：`9C-01`）。
> 不接受以姓名直接操作，避免同名錯誤。

---

## 三、資料寫入原則

### 3-1 寫什麼

| 類別 | 欄位 | 來源 |
|------|------|------|
| 科目定義 | `ability_definition`、`motivation_definition` | 教師口述 |
| DI 分類 | `di_type`（A/B/C/D） | 教師口述 |
| 能力程度 | `ability_level`（高/中/低） | 教師口述 |
| 動機程度 | `motivation_level`（高/低） | 教師口述 |
| 學習優勢 | `strengths`（語言型/圖像型/動作型/藝術型） | 教師口述 |
| 補充觀察 | `notes` | 教師口述（可選） |
| 歷史成績 | `prior_grades` | 成績單（系統解析） |

### 3-2 同步更新

每次科目層（di-profile.yaml）寫入後，AI **必須同步更新**班級層的統計摘要：

```yaml
# students.yaml 的 di_summary.{科目}
di_distribution:
  A: {count}
  B: {count}
  C: {count}
  D: {count}
```

### 3-3 不可做的事

- 不得在未確認角色前寫入任何學生資料
- 不得把個人觀察寫進 `students.yaml`（班級層只放統計，不放個人）
- 不得以姓名查找學生（一律用 ID）
- 不得一次將所有歷史評量報告全部灌入（按需讀取）

---

## 四、擴充其他科目

當新科目需要記錄學生 DI 資料時（例如數學老師加入）：

1. 在班級目錄下建立 `{科目}/di-profile.yaml`
2. 從 `english/di-profile.yaml` 複製結構（更改科目名稱、觀察者）
3. 在 `students.yaml` 的 `di_summary` 中新增對應條目
4. 更新 `.gitignore`（如有含真名的內容）

---

## 五、資料讀取效率原則

| 讀取時機 | 做法 |
|----------|------|
| 開始 DI 課程設計 | 只讀統計層（`students.yaml` 的 `di_summary`） |
| 需要某位學生的詳細資料 | 讀 `di-profile.yaml` 的對應 ID 段落 |
| 需要學生真名對應 | 讀 `roster.yaml`（只在需要時） |
| 需要歷史跨科表現 | 讀 HTML 評量報告的個別學生段落（不讀全文） |

> [!TIP]
> 80KB 的全班評量 HTML 不要一次全讀。
> 每次只讀需要的那位學生，成本降低 95%。
