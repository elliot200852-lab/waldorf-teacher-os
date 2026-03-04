---
name: load
description: 載入指定班級與科目的工作脈絡，輸出壓縮摘要作為本次對話的定位起點。任何對話開始時如教師提到班級名稱與「載入」「讀一下」等詞，立即執行。
triggers:
  - 載入
  - 讀一下狀態
  - 開始工作
  - 進入工作
requires_args: true
args_format: "[班級代碼] [科目] (例: 9c english、8a history、7a homeroom)"
---

# skill: load — TeacherOS 脈絡載入

載入指定班級與科目的工作脈絡，輸出壓縮摘要，作為本次對話的定位起點。

## 參數

班級代碼（9c / 8a / 7a）+ 科目（english / history / ml-taiwan-literature / homeroom 等）。
未提供班級則詢問：「請問這次要載入哪個班級？」
未提供科目則詢問：「要載入哪個科目？」或掃描該班級下所有科目資料夾列出選項。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 讀取順序

依序讀取以下檔案：

1. `ai-core/teacheros.yaml`
   → 系統路由中樞（載入順序、workspace 機制、session 協議）

2. `ai-core/teacheros-foundation.yaml`
   → 華德福教育共用根基（哲學、發展心理、課程原則、reference 觸發條件）

3. `ai-core/acl.yaml`
   → 比對當前使用者身份，取得 workspace 路徑與角色

4. `{workspace}/teacheros-personal.yaml`
   → 教師個人身份、科目信念、工作偏好

5. `projects/_di-framework/project.yaml`
   → 差異化教學框架（每次必載）

6. `{workspace}/projects/class-[班級]/project.yaml`
   → 班級脈絡與焦點

7. `{workspace}/projects/class-[班級]/[科目]/session.yaml`
   → 科目進度錨點

# {workspace} 路徑解析：
# 從 acl.yaml 取得當前使用者的 workspace 路徑。
# Codeowner：workspaces/Working_Member/Codeowner_David/
# 教師：workspaces/Working_Member/Teacher_{姓名}/

## 輸出格式

讀取完成後，輸出以下摘要。**不貼出完整 YAML 原文**，只從檔案中提取關鍵欄位。

---

**TeacherOS 已載入｜class-[班級]｜[科目]**

**教師** [從身份 YAML 讀取姓名與角色]
**DI 框架** 雙軸強制：學習優勢（每份設計涵蓋至少 2–3 種）+ A/B/C/D 矩陣

**班級焦點**
（從 `class-[班級]/project.yaml` 的 `current_focus` 與 `next_steps` 摘取）

**[科目]課目前位置**
（從 `[科目]/session.yaml` 的 `current_position` 與 `next_action` 摘取，
格式：「區塊 X → 步驟 Y｜下一步：[描述]」）

**待決問題**
（從 `[科目]/session.yaml` 的 `open_questions` 摘取；若為空則顯示「無」）

---

準備就緒。今天要推進哪個方向？

## 注意事項

- 全程使用繁體中文
- 若欄位值為 `null`、空陣列或「待填入」，顯示「尚未設定」，不報錯
- 不主動讀取 `students.yaml`，等教師明確需要 DI 資料時再讀取
- 摘要結束後不補充任何解釋，直接等待教師指令
