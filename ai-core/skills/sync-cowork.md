---
name: sync-cowork
description: 從 INSTRUCTIONS.template.md + 個人 YAML 編譯 INSTRUCTIONS.md（Cowork folder instructions）。支援多使用者，每位教師編譯自己的版本。
triggers:
  - 同步 Cowork
  - 更新 Cowork
  - 編譯 instructions
  - sync cowork
requires_args: false
---

# skill: sync-cowork — 編譯 Cowork Folder Instructions

從共用模板 `INSTRUCTIONS.template.md` + 教師個人 YAML 編譯 `INSTRUCTIONS.md`。
INSTRUCTIONS.md 已加入 .gitignore，每位教師在本機生成自己的版本，不進版本控制。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 架構說明

```
INSTRUCTIONS.template.md （committed，共用模板）
        ↓ sync-cowork 讀取模板
        ↓ + 教師個人 YAML（身份、班級進度）
        ↓ 編譯
INSTRUCTIONS.md （gitignored，個人編譯版）
        ↓ Cowork 開啟資料夾時自動載入
```

**模板中的標記：**
- `<!-- COMPILE:IDENTITY:START -->` ~ `<!-- COMPILE:IDENTITY:END -->` → 用教師身份填入
- `<!-- COMPILE:STATUS:START -->` ~ `<!-- COMPILE:STATUS:END -->` → 用教師班級進度填入
- 其餘區塊（二、四、五、六）為共用 STATIC 內容，從模板原樣複製

## 使用時機

1. **自動觸發：** wrap-up 的 Step 2 呼叫「快速模式」（只更新區塊三）
2. **手動觸發：** 教師說「同步 Cowork」「更新 Cowork」→ 更新區塊三 + 檢查其他區塊
3. **架構變動後：** 教師說「架構有改動」→ 從模板完整重編譯所有區塊
4. **首次生成：** 新教師 clone 後第一次執行，從模板 + 個人 YAML 生成完整 INSTRUCTIONS.md

## 執行步驟

### Step 0 — 識別當前教師

1. 讀取 `git config user.email`
2. 比對 `ai-core/acl.yaml`，找到對應的教師身份與 workspace 路徑
3. 確定 workspace 變數：

| 教師角色 | workspace 路徑 |
|---------|---------------|
| Codeowner（管理者） | `workspaces/Working_Member/Codeowner_{姓名}/` |
| 一般教師 | `workspaces/Working_Member/Teacher_{姓名}/` |

若比對失敗，詢問：「找不到你的 workspace，請確認 git config user.email 與 acl.yaml 是否一致。」

### Step 1 — 判斷更新範圍

| 觸發情境 | 更新範圍 |
|----------|---------|
| wrap-up 自動呼叫 | 只更新**區塊三**（當前系統狀態） |
| 教師說「同步 Cowork」 | 更新**區塊三** + 檢查區塊一是否有變動 |
| 教師說「架構有改動」 | **全部區塊**從模板重新編譯 |
| INSTRUCTIONS.md 不存在（首次） | **全部區塊**從模板重新編譯 |

### Step 2 — 讀取 Source of Truth

**區塊一（教師身份）：**

| 身份來源（所有使用者統一） |
|---------------------------|
| `{workspace}/teacheros-personal.yaml`（workspace 路徑從 `ai-core/acl.yaml` 取得） |

編譯規則：
- 從 YAML 提取：姓名、角色、學校類型、年級、科目、教學哲學、AI 立場、溝通偏好
- 濃縮為人類可讀的段落，不超過 300 字
- 保持溫暖專業的語氣

**區塊二（檔案地圖）：**
- 從 `INSTRUCTIONS.template.md` 的 STATIC 區塊原樣複製
- 架構更新時：掃描目錄結構，將 `{你的工作空間}` 替換為實際 workspace 路徑
- 列出教師自己的班級資料夾（從 `{workspace}/workspace.yaml` 的 classes 讀取）

**區塊三（當前狀態，必讀）：**
- `ai-core/system-status.yaml`（系統層級狀態：版本、框架完成度）
- `{workspace}/workspace.yaml`（教師的班級清單）
- 對每個 active 班級：掃描 `{workspace}/projects/class-{code}/*/session.yaml`（各科目進度錨點）

**區塊四、五、六（共用 STATIC）：**
- 從 `INSTRUCTIONS.template.md` 原樣複製
- 架構更新時讀取 `projects/_di-framework/project.yaml` 確認品質標準是否有變動

### Step 3 — 編譯寫入

**若 INSTRUCTIONS.md 已存在（日常更新）：**
- 讀取現有 INSTRUCTIONS.md
- 只替換需要更新的區塊內容
- 更新 metadata header（last_compiled、source_files）
- 保持其他區塊不變

**若 INSTRUCTIONS.md 不存在或需全區塊重編譯：**
1. 讀取 `INSTRUCTIONS.template.md` 作為骨架
2. 將 `<!-- COMPILE:IDENTITY:START -->` ~ `END` 之間的內容替換為編譯後的教師身份
3. 將 `<!-- COMPILE:STATUS:START -->` ~ `END` 之間的內容替換為編譯後的班級進度
4. 將 STATIC 區塊中的 `{你的工作空間}` 替換為實際 workspace 路徑
5. 寫入 metadata header：
   ```
   last_compiled: [今天日期]
   compiled_by: [當前 AI 工具名稱] (sync-cowork)
   compiled_for: [教師姓名] ([workspace 名稱])
   workspace: [workspace 路徑]
   template: INSTRUCTIONS.template.md
   source_files:
     - [列出所有讀取的 YAML 檔案]
   ```
6. 寫入 `INSTRUCTIONS.md`（根目錄）

### Step 4 — 確認

輸出變更摘要：

```
Cowork INSTRUCTIONS.md 已更新（{教師姓名}）：
- 區塊三：{班級} {科目} Block [X] Step [Y] → [next_action]
- last_compiled: [今天日期]
[如有其他區塊變動，列出]
```

不需要詢問確認（從 Source of Truth 編譯，不涉及判斷）。

## 注意事項

- INSTRUCTIONS.md 是**編譯產物**，永遠從 YAML + 模板生成，不反向寫回
- INSTRUCTIONS.md 已加入 .gitignore，**不會出現在 PR diff 中**，不會造成合併衝突
- 共用內容的修改入口是 `INSTRUCTIONS.template.md`（由管理者維護）
- 個人內容的修改入口是教師的 `teacheros-personal.yaml` 和各科目的 `session.yaml`
- 如果模板有更新（例如管理者修改了品質標準），教師下次執行 sync-cowork 時會自動同步
- 區塊三的格式保持簡潔——Cowork 不需要看 YAML 欄位名，只需人類可讀的進度摘要
- 保持 metadata header（HTML 註解格式），供追蹤編譯來源與時間
