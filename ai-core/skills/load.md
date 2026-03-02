---
name: load
description: 載入指定班級的工作脈絡，輸出壓縮摘要作為本次對話的定位起點。任何對話開始時如教師提到班級名稱與「載入」「讀一下」等詞，立即執行。
triggers:
  - 載入
  - 讀一下狀態
  - 開始工作
  - 進入工作
requires_args: true
args_format: "[班級代碼] (9c/8a/7a)"
---

# skill: load — TeacherOS 脈絡載入

載入指定班級的工作脈絡，輸出壓縮摘要，作為本次對話的定位起點。

## 參數

班級代碼（9c / 8a / 7a）。未提供則詢問：「請問這次要載入哪個班級？（9c / 8a / 7a）」

## 根目錄

`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`

## 讀取順序

依序讀取以下四個檔案：

1. `ai-core/teacheros.yaml`
2. `projects/_di-framework/project.yaml`
3. `projects/class-[班級]/project.yaml`
4. `projects/class-[班級]/working/english-session.yaml`

## 輸出格式

讀取完成後，輸出以下摘要。**不貼出完整 YAML 原文**，只從檔案中提取關鍵欄位。

---

**TeacherOS 已載入｜class-[班級]**

**教師** David，華德福七至九年級，英文 / 人文 / 歷史
**DI 框架** 雙軸強制：學習優勢（每份設計涵蓋至少 2–3 種）+ A/B/C/D 矩陣

**班級焦點**
（從 `class-[班級]/project.yaml` 的 `current_focus` 與 `next_steps` 摘取）

**英文課目前位置**
（從 `english-session.yaml` 的 `current_position` 與 `next_action` 摘取，
格式：「區塊 X → 步驟 Y｜下一步：[描述]」）

**待決問題**
（從 `english-session.yaml` 的 `open_questions` 摘取；若為空則顯示「無」）

---

準備就緒。今天要推進哪個方向？

## 注意事項

- 全程使用繁體中文
- 若欄位值為 `null`、空陣列或「待填入」，顯示「尚未設定」，不報錯
- 不主動讀取 `students.yaml`，等教師明確需要 DI 資料時再讀取
- 摘要結束後不補充任何解釋，直接等待教師指令
