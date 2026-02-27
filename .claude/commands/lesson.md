# /lesson — 進入指定班級課程設計流程

載入班級 DI 資料，直接進入指定區塊的設計工作流程。
跳過手動說明脈絡的步驟，直接就位開工。

## 使用方式

```
/lesson 9c 1      ← 9C 班，區塊一（學季整體規劃）
/lesson 9c 2      ← 9C 班，區塊二（班級實際教學）
/lesson 8a 1
/lesson 7a 2
```

## 執行規則

`$ARGUMENTS` 格式：`[班級代碼] [區塊編號]`

- 班級代碼：9c / 8a / 7a
- 區塊編號：1 / 2
- 若缺少任一參數，詢問補齊後再繼續

## 執行步驟

### Step 1 — 讀取必要檔案

依序讀取（根目錄：`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`）：

1. `projects/class-[班級]/working/english-session.yaml`（確認目前位置）
2. `projects/class-[班級]/working/students.yaml`（DI 人數與學習優勢資料）
3. 依區塊編號讀取對應模板：
   - 區塊一：`projects/_di-framework/content/english-di-block1.md`
   - 區塊二：`projects/_di-framework/content/english-di-block2.md`

### Step 2 — 輸出定位摘要

---

**已就位｜class-[班級]｜英文課區塊[編號]**

**班級 DI 概況**
（從 students.yaml 摘取英文科目的 A/B/C/D 人數分布 + 學習優勢分布）

**目前進度**
（從 english-session.yaml 摘取 current_position，若為空顯示「尚未開始」）

**本區塊工作目標**
（從模板摘取該區塊的 purpose，1–2 句）

---

### Step 3 — 進入工作流程

輸出定位摘要後，直接執行對應區塊模板的 Step 1，開始向教師收集所需資訊。

不等待教師說「開始」，直接就位提問。

## 注意事項

- 若 students.yaml 的 DI 資料欄位為「待填入」，提示：「students.yaml 尚未填入 DI 資料，建議先填入後再進行設計，或繼續並在設計中手動說明班級狀況。」
- 若 english-session.yaml 顯示目前已在不同區塊，提示教師確認是否切換
- 區塊二模板若尚未建立，回應：「english-di-block2.md 尚未建立，建議先使用 /syllabus [班級] 完成區塊一。」
