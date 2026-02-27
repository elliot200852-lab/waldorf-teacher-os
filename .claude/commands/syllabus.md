# /syllabus — 啟動學季教學大綱規劃

學季初使用。載入班級資料，啟動 Block 1 完整流程，
從「教學方向」協作產出「兩學季教學大綱」。

## 使用方式

```
/syllabus 9c
/syllabus 8a
/syllabus 7a
```

## 執行規則

`$ARGUMENTS` 是班級代碼（9c、8a 或 7a）。

若未提供 `$ARGUMENTS`，先詢問：「請問要為哪個班級規劃教學大綱？（9c / 8a / 7a）」

## 執行步驟

### Step 1 — 讀取必要檔案

依序讀取（根目錄：`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`）：

1. `projects/class-$ARGUMENTS/project.yaml`
2. `projects/class-$ARGUMENTS/working/students.yaml`
3. `projects/class-$ARGUMENTS/working/english-session.yaml`
4. `projects/_di-framework/content/english-di-block1.md`

### Step 2 — 確認是否已有既有大綱

從 `english-session.yaml` 的 `output_files.syllabus_versions` 確認：

- 若已有版本，提示：「此班已有 [版本號] 大綱（[日期]）。要建立新版本，還是修改現有版本？」等待確認後繼續
- 若尚無版本，直接進入 Step 3

### Step 3 — 輸出開場摘要

---

**學季大綱規劃已啟動｜class-$ARGUMENTS**

**班級 DI 概況**
（從 students.yaml 摘取英文科目 A/B/C/D 人數 + 學習優勢分布）

**需要收集的資訊（共 8 項）**
1. 標題與學年度
2. 班級
3. 授課老師
4. 教學目標
5. 教學策略
6. 教學規劃（兩學季單元方向）
7. 學生任務
8. 評量方式（各項合計必須 = 100%）

---

### Step 4 — 啟動 Block 1 Step 1

依照 `english-di-block1.md` 的流程，開始逐項收集 8 個必要欄位。

不一次問所有問題。先詢問前 3 項（教學目標 / 主題方向 / 教材），
收到回應後繼續收集剩餘項目。

### Step 5 — 資訊收集完成後，執行 DI 強化

依照 `english-di-block1.md` Step 2，對教師輸入進行 DI 雙軸檢核：
- 學習優勢覆蓋度
- A/B/C/D 矩陣覆蓋度

若有缺口，給出具體補強建議後，詢問是否調整，再進入 Step 6。

### Step 6 — 產出教學大綱

依照 `english-di-block1.md` Step 3 的格式規範產出大綱。

**版本命名規則：**
- 新建：v1（若已有則依序遞增）
- 檔名格式：`english-syllabus-v{N}-{YYYYMMDD}.md`

**雙路徑同時寫入：**

| 路徑 | 用途 |
|------|------|
| `projects/class-$ARGUMENTS/content/english/english-syllabus-v{N}-{YYYYMMDD}.md` | 班級視角 |
| `projects/class-$ARGUMENTS/english/content/english-syllabus-v{N}-{YYYYMMDD}.md` | 英文科目視角 |

寫入前確認：「確認產出 [檔名] 並寫入雙路徑嗎？（是 / 否）」

### Step 7 — 更新 english-session.yaml

大綱產出後，自動生成 session-end diff，更新以下欄位：
- `current_position.block: 一`
- `current_position.step: 3`（已完成）
- `output_files.syllabus_versions`（新增版本記錄）
- `next_action.description: 進入區塊二，開始第一單元實際教學設計`

詢問：「確認更新 english-session.yaml 嗎？（是 / 否）」

## 注意事項

- 大綱語言面向學生與家長，不使用教學術語，不外露 DI 分類標籤
- 評量各項百分比合計必須等於 100%，若不符合，請教師調整後再產出
- 若 students.yaml 尚未填入 DI 資料，提示後繼續，由教師在對話中口頭描述班級狀況
