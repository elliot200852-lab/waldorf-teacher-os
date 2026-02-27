# 英文課差異化教學設計模板｜主控索引

> 本文件為英文課 DI 設計的**主控索引與工作協議**。
> 各區塊的實際工作流程與產出規範，分別存放於獨立的 block 檔案。
> 適用班級：class-7a / class-8a / class-9c

---

## 每次對話開始協議（AI 必須執行）

在任何英文課備課對話開始時，AI 必須依序完成以下步驟，**不可跳過**：

```
1. 讀取 ai-core/teacheros.yaml
2. 讀取 projects/_di-framework/project.yaml
3. 讀取對應班級的 projects/class-{班級}/working/students.yaml
4. 讀取對應班級的進度錨點檔案：
       projects/class-{班級}/working/english-session.yaml
5. 依據 english-session.yaml 的 current_position，讀取對應的 block 檔案：
       projects/_di-framework/content/english-di-block{N}.md
6. 向教師報告：「現在在區塊 __，Step __，上次確認的是 __，今天繼續做 __。」
7. 等待教師確認或修正，再開始工作。
```

**如果進度錨點檔案不存在：** 從區塊一 Step 1 開始，讀取 `english-di-block1.md`，對話結束後建立錨點檔案。

**如果對話途中察覺岔題：** AI 必須主動說「我們先回到中軸：目前在 {區塊/Step}，確認要繼續嗎？」

---

## 產出檔案位置規範

### 雙路徑儲存

每份產出檔案**同時存放於兩個路徑**，內容完全相同：

| 路徑 | 用途 |
|------|------|
| `projects/class-{班級}/content/english/` | 班級視角（所有科目集中） |
| `projects/class-{班級}/english/content/` | 英文科目視角（科目自主管理） |

### 版本命名規則

**產出檔案以日期與版本號命名，不覆蓋舊有版本：**

```
{類型}-v{版本號}-{YYYYMMDD}.md
```

| 產出物 | 範例檔名 |
|--------|----------|
| 教學大綱 | `english-syllabus-v1-20260227.md` |
| 單元教學流程 | `english-unit-1-v1-20260301.md` |
| 課外延伸任務 | `english-extension-1-v1-20260305.md` |

> 每次新增內容建立新版本（v2、v3…），舊版本保留。
> 老師自行決定哪個版本要列印給學生——系統不代為決定。

### 檔案操作協議（AI 必須執行）

**（一）新增產出時：**
1. 自動產生版本號（確認現有最高版本號 + 1）
2. 同時寫入兩個路徑
3. 向教師回報：「已建立 `{檔案名稱}`，存入兩個路徑。」
4. 將新版本記錄至 `english-session.yaml` 的 `output_files`

**（二）教師指定更新某個版本時：**
1. 先確認：「確認要更新 `{版本檔名}` 嗎？兩個路徑都會同步更新。」
2. 得到教師明確確認後，同時更新兩個路徑
3. 若兩個路徑更新結果不一致，立即報告

**（三）不允許的操作：**
- 未經確認自動覆蓋任何現有版本
- 只更新單一路徑（必須雙路徑同步）
- 替教師決定哪個版本是「最終版」

---

## 區塊架構與連接邏輯

### 設計原則

- 每個區塊是**可獨立觸發**的工作單元，不強制按順序依序全部跑完
- 區塊之間有**建議的前後參照關係**，後續區塊應引用前置區塊的產出
- 所有區塊共享同一進度錨點（`english-session.yaml`），確保跨區塊跨對話的連貫性

### 區塊登錄

| 區塊 | 名稱 | 檔案 | 狀態 | 建議前置 | 核心產出 |
|------|------|------|------|----------|----------|
| Block 1 | 學季整體規劃 | [english-di-block1.md](english-di-block1.md) | 已建立 | — | `english-syllabus.md` |
| Block 2 | 班級實際教學 | `english-di-block2.md` | 待建立 | Block 1 | `english-unit-{n}.md` + `english-extension-{n}.md` |
| Block 3+ | 待定 | — | 待確認 | — | — |

### 區塊連接說明

```
Block 1（學季整體規劃）
    └─ 產出：english-syllabus.md（教學大綱）
              ↓ 作為基準參照
Block 2（班級實際教學）
    ├─ 2-A：逐單元教學流程（對照大綱單元）
    │         └─ 產出：english-unit-{n}.md
    └─ 2-B：課外延伸支援（依課堂觀察觸發）
              └─ 產出：english-extension-{n}.md
                        ↓ 觀察回饋
                  students.yaml（動態標籤更新）
```

**區塊間的參照規則：**
- Block 2 啟動前，應先確認 Block 1 的 `english-syllabus.md` 已存在
- 若尚未完成 Block 1，可先啟動 Block 2 但需標記大綱為「暫定」
- 任何區塊的產出都必須記錄至 `english-session.yaml` 的 `output_files`

---

## 設計限制條件（繼承自 `_di-framework`）

所有依本模板產出的課程設計，必須通過以下檢核：

1. **一人執行可行性：** 單一教師在實際課堂中可操作，不依賴額外人力
2. **差異化是設計預設：** 不是補救手段，而是備課階段的標準流程
3. **避免標準化：** 不同班級允許各自發展，策略保留彈性
4. **DI 對學生不可見：** 分類標籤與分組邏輯僅供教師與 AI 使用，不外露給學生

---

## 進度錨點機制（每次對話結束時執行）

每個班級各自維護：`projects/class-{班級代碼}/working/english-session.yaml`

### 錨點檔案格式

```yaml
english_session:
  class: class-9c
  last_updated: 2026-XX-XX

  current_position:
    block: 一             # 一 / 二 / 三...
    step: 1              # 1 / 2 / 3
    sub_block: null      # 區塊二時填入：2-A / 2-B
    unit_number: null    # 區塊二時填入：目前在第幾單元

  confirmed_decisions:
    - "學期主題方向：XXXX"
    - "教材核心文本：XXXX"

  next_action:
    description: "下次對話要做的第一件事"
    input_needed_from_teacher: "教師需要在下次對話前準備的資訊（若無則留空）"

  output_files:
    syllabus: null                    # Block 1 產出
    units_completed: []               # Block 2-A 產出
    extensions_completed: []          # Block 2-B 產出

  open_questions:
    - "問題一"
```

### AI 於對話結束前的必做動作

1. 以條列方式向教師確認：「今天決定了哪些事」
2. 更新錨點檔案（只改動有變化的欄位）
3. 告知教師「下次開始前需要準備什麼」（若有）
4. 若有產出檔案，確認已存入正確路徑

### 教師重新定位指令

當你覺得對話偏離主軸，直接說以下任何一句：
- 「回到中軸」
- 「我們現在在哪裡？」
- 「重新定位」

AI 收到後必須立刻讀取錨點檔案，報告當前位置，然後問：「要繼續這裡，還是調整方向？」

---

*本模板最後更新：2026-02-27*
*母文件：`_di-framework/content/system-logic-map.md`*
*框架版本：`_di-framework/project.yaml`*
