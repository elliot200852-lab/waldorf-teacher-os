---
name: homeroom
description: 載入導師業務脈絡，進入班級經營、個案討論、家長溝通工作流程。涉及班級人際或事件時自動提示。
triggers:
  - 導師業務
  - 班級事件
  - 個案討論
  - 班親會
  - 班級經營
requires_args: true
args_format: "[班級代碼] (例: 9c、8a、7a)"
---

# skill: homeroom — 導師業務

載入導師業務工作脈絡，進入班級經營、個案討論、家長溝通工作流程。

## 參數

班級代碼。未提供則詢問：「請問要處理哪個班的導師業務？」

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 執行步驟

### Step 1 — 讀取必要檔案

1. `{workspace}/projects/class-[班級]/homeroom/session.yaml`（導師業務進度錨點）

# {workspace} 路徑解析：
# 從 acl.yaml 取得當前使用者的 workspace 路徑。
# Codeowner：workspaces/Working_Member/Codeowner_David/
# 教師：workspaces/Working_Member/Teacher_{姓名}/

2. `projects/_di-framework/content/homeroom-template.md`（若存在）

**Reference 模組（必讀）：**

3. `ai-core/reference/student-development.yaml`（外骨骼論、修復式正義、班級經營哲學）

若 `homeroom/session.yaml` 不存在，提示：「homeroom/session.yaml 尚未建立，是否現在初始化？」並依教師回應決定是否建立初始檔案。

### Step 2 — 輸出導師業務狀態報告

---

**導師業務已載入｜class-[班級]**

**目前焦點**
（從 session.yaml 摘取 current_focus；若為空顯示「無明確焦點」）

**待處理事項**
（從 session.yaml 摘取 pending_tasks；若無顯示「無」）

**下一步**
（從 session.yaml 摘取 next_action；若無顯示「尚未設定」）

---

### Step 3 — 等待指令，進入對應工作

依教師指令進入以下工作類型：

| 指令意圖 | 執行動作 |
|---------|---------|
| 「個案討論」「聊一下某學生」 | 讀取 students.yaml，進入學生狀態分析 |
| 「寫家長信」「家長通知」 | 執行 `ai-core/skills/parent-letter.md` |
| 「班會」「談話圈」 | 依修復式正義框架設計班會流程 |
| 「衝突」「事件」 | 引導修復性對話設計，不建議懲罰性處置 |
| 「學生觀察」「記一下誰」 | 執行 `ai-core/skills/student-note.md` |

### Step 4 — 收尾時更新 homeroom session

對話結束前提醒：「需要更新 homeroom/session.yaml 嗎？」

更新欄位：
- `current_focus`
- `pending_tasks`（附加新項目，移除已完成）
- `next_action`
- `last_updated`

## 注意事項

- 個案討論時涉及學生隱私，輸出使用學生代號或座號，不使用真實姓名
- 修復式正義優先：任何衝突事件，先理解影響，再提彌補方案，不建議懲罰性處置
- 語音輸入：教師說「導師業務」「班級事件」「個案討論」即可觸發
