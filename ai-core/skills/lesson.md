---
name: lesson
description: 載入班級DI資料，進入具體課堂教學設計流程。支援兩種模式：區塊規劃（Block）與單堂設計（45 分鐘）。
triggers:
  - 進入備課
  - 做Block
  - 開始設計
  - 課堂設計
  - 設計課堂
  - 設計一堂課
  - 45分鐘
  - lesson design
requires_args: true
args_format: "[班級代碼] [科目] [區塊編號 或 45] (例: 9c english 2、8a history 1、9c english 45)"
---

# skill: lesson — 進入指定班級課程設計流程

支援兩種模式：

- **區塊模式**（Block）：載入 DI 資料，進入學季區塊的設計工作流程
- **單堂模式**（45）：載入通用引擎 + 科目覆蓋層，設計一堂 45 分鐘課

## 參數

格式：`[班級代碼] [科目] [區塊編號 或 45]`

- 班級代碼：9c / 8a / 7a
- 科目：english / history / homeroom 等
- 第三參數：
  - `1` 或 `2` → 區塊模式（學季整體規劃 / 班級實際教學）
  - `45` → 單堂模式（45 分鐘課堂設計）
- 若缺少任一參數，詢問補齊後再繼續

## 路由邏輯

根據第三參數決定執行路徑：

### 當第三參數為 `45` → 單堂設計模式

1. 讀取通用引擎：`ai-core/skills/subject-lesson-45.md`
2. 依引擎 Step 0 的邏輯載入科目覆蓋層（先找 `ai-core/skills/[科目]-45.md`，找不到則找 `{workspace}/skills/draft-[科目]-45.md`）
3. 若覆蓋層都不存在 → 提示教師：「目前沒有 [科目] 的覆蓋層，將僅使用通用引擎設計。」
4. 將班級代碼傳入引擎 Step 0，由引擎接管後續五階段工作流

### 當第三參數為 `1` 或 `2` → 區塊設計模式

進入下方原有的區塊設計流程。

---

## 區塊設計模式（Block）

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

### Step 1 — 讀取必要檔案

依序讀取：

1. `{workspace}/projects/class-[班級]/[科目]/session.yaml`（確認目前位置）
2. `{workspace}/projects/class-[班級]/working/students.yaml`（DI 人數與學習優勢資料）

# {workspace} 路徑解析：
# 從 acl.yaml 取得當前使用者的 workspace 路徑。
# Codeowner：workspaces/Working_Member/Codeowner_David/
# 教師：workspaces/Working_Member/Teacher_{姓名}/

3. 依區塊編號讀取對應模板：
   - 區塊一：`projects/_di-framework/content/[科目]-di-block1.md`
   - 區塊二：`projects/_di-framework/content/[科目]-di-block2.md`
   （若該科目的模板不存在，提示教師並詢問是否使用通用 DI 框架）

**Reference 模組（課程設計必讀）：**

4. `ai-core/reference/pedagogy-framework.yaml`（年級發展樣態 + 課程鏡像邏輯）
5. `ai-core/reference/subject-[科目].yaml`（科目哲學 + 教師核心任務）
   （若該科目的 reference 不存在，跳過並提示教師）

### Step 2 — 輸出定位摘要

---

**已就位｜class-[班級]｜[科目]區塊[編號]**

**班級 DI 概況**
（從 students.yaml 摘取該科目的 A/B/C/D 人數分布 + 學習優勢分布）

**目前進度**
（從 [科目]/session.yaml 摘取 current_position，若為空顯示「尚未開始」）

**本區塊工作目標**
（從模板摘取該區塊的 purpose，1–2 句）

---

### Step 3 — 進入工作流程

輸出定位摘要後，直接執行對應區塊模板的 Step 1，開始向教師收集所需資訊。

不等待教師說「開始」，直接就位提問。

## 注意事項

- 若 students.yaml 的 DI 資料欄位為「待填入」，提示：「students.yaml 尚未填入 DI 資料，建議先填入後再進行設計，或繼續並在設計中手動說明班級狀況。」
- 若 session.yaml 顯示目前已在不同區塊，提示教師確認是否切換
- 區塊二模板若尚未建立，回應：「[科目]-di-block2.md 尚未建立，建議先使用 syllabus 技能完成區塊一。」
