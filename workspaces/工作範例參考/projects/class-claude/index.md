# Claude 老師八年級英文班 - 專案檔案索引

## 概述

這是 Claude 老師於 2026 年 3 月完成的八年級英文教學專案的完整檔案索引。本專案涵蓋全年四個學習塊（Block 1-4），展示了 Waldorf 教育法與創意寫作教學的完整整合。

## 核心專案設定檔案

### project.yaml
- **路徑**: `project.yaml`
- **說明**: 本專案的主要配置文件，包含專案元數據、課程設定及教學目標

### roster.yaml
- **路徑**: `roster.yaml`
- **說明**: 班級花名冊，記錄所有學生的基本資訊

### students.yaml
- **路徑**: `students.yaml`
- **說明**: 學生詳細資料，包括個人檔案、學習進度追蹤等

## 英文教學內容

### 課程綱要與單元規劃

#### 英文課程綱要
- **路徑**: `english/content/english-syllabus-v1-20260303.md`
- **說明**: 完整的英文科課程綱要（版本 1，2026年3月3日），包括教學目標、進度規劃、評量方式

#### 第一單元教案
- **路徑**: `english/content/english-unit-1-v1-20260303.md`
- **說明**: 第一學習塊（Block 1）詳細教案，包含主題導入、活動設計、Freedom Writers Diary 相關教學

#### 第二至四單元教案
- **路徑**: `english/content/english-units-2-4-v1-20260303.md`
- **說明**: 第二、三、四學習塊（Block 2-4）的統合教案

### 學生評量與記錄

#### 單元日誌
- **路徑**: `english/content/records/unit-logs.md`
- **說明**: 各學習塊的教學進度記錄，包含每堂課的重點、學生參與情況

#### 學生個人日誌樣本
- **路徑**: `english/content/records/student-logs/sample-logs.md`
- **說明**: 學生個人學習日誌的示例，展示學生成長歷程與反思

#### 教師教學反思
- **路徑**: `english/content/records/teacher-reflections.md`
- **說明**: Claude 老師在四個學習塊中的教學反思，包括教法改進、學生回饋整理

#### 學生評量報告
- **路徑**: `english/content/student-assessments-20260510.md`
- **說明**: 期末學生評量結果，包含各項能力指標評分、學生表現分析

#### 教師學期總結報告
- **路徑**: `english/content/teacher-term-report-20260510.md`
- **說明**: 全學年教學總結報告，涵蓋教學成效評估、班級發展、建議改進

## 英文科教學設定

### 差異化教學檔案
- **路徑**: `english/di-profile.yaml`
- **說明**: 英文科的差異化教學（Differentiated Instruction）設定，包括各層級學生的教學策略

### 英文課程工作檔案
- **路徑**: `working/english-session.yaml`
- **說明**: 英文課程的工作記錄與課堂內容，用於課程進行中的即時追蹤

## 班級導師相關文件

### homeroom 目錄
- **路徑**: `homeroom/`
- **說明**: 班級導師職務相關文件（目前為空或僅含系統檔案）

## 輔助文件

### 測試報告
- **路徑**: `TeacherOS-測試報告-三合一.docx`
- **說明**: TeacherOS 系統測試報告文件（Word 格式）

- **路徑**: `TeacherOS-測試報告-三合一拷貝.docx`
- **說明**: TeacherOS 系統測試報告的備份副本

## 檔案結構總覽

```
class-claude/
├── index.md                              # 本檔案 - 專案檔案索引
├── project.yaml                          # 專案設定
├── roster.yaml                           # 班級花名冊
├── students.yaml                         # 學生資料
├── english/
│   ├── di-profile.yaml                   # 差異化教學設定
│   └── content/
│       ├── english-syllabus-v1-20260303.md           # 課程綱要
│       ├── english-unit-1-v1-20260303.md             # 第一單元教案
│       ├── english-units-2-4-v1-20260303.md          # 第二至四單元教案
│       ├── student-assessments-20260510.md           # 學生評量
│       ├── teacher-term-report-20260510.md           # 期末報告
│       └── records/
│           ├── unit-logs.md              # 教學進度記錄
│           ├── teacher-reflections.md    # 教師反思
│           └── student-logs/
│               └── sample-logs.md        # 學生日誌範例
├── working/
│   └── english-session.yaml              # 課程工作記錄
├── homeroom/                             # 班級導師目錄
├── content/                              # 備份內容（英文/content）
└── 其他文件/
    ├── TeacherOS-測試報告-三合一.docx
    └── TeacherOS-測試報告-三合一拷貝.docx
```

## 教學特色

### 採用教材
- **Freedom Writers Diary** - 作為主要創意寫作教材
- Waldorf 教育法 - 強調藝術、敘事、個人成長

### 教學重點
1. 創意寫作與個人表達
2. 批判性思維與文學分析
3. 學生自主性與反思能力
4. 班級社群建構與同儕學習

### 班級資訊
- 年級：八年級
- 科目：英文（主要）+ 班級導師職務
- 學生人數：18 名
- 教學週期：四個學習塊（Block 1-4）
- 狀態：已完成

## 使用說明

本索引提供了對所有專案檔案的完整指引。所有教案、評量記錄及教師反思均以 Markdown 格式保存，便於查閱、修改及參考。此專案可作為新進教師的教學範例，特別是在 Waldorf 教育法下的英文教學實踐參考。

---

**最後更新**: 2026 年 3 月 3 日
**教師**: Claude
**職務**: 八年級英文科任教師 + 班級導師
