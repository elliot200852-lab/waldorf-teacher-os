---
aliases:
  - "AI 交接文件 v1"
---

# TeacherOS AI 交接文件

> 日期：2026-03-03
> 上一次工作者：Claude (Cowork Mode)
> 目的：記錄測試後的所有架構修改，供下一個 AI 工作階段無縫接手

---

## 一、本次工作摘要

本次對 TeacherOS 進行了完整的系統測試與架構優化。以「Teacher Claude」身份模擬八年級英文教師，完成 Block 1-4 全流程，並根據測試結果修正了七大架構問題。

本次測試重點：
- 驗證 Block 1-4 產出流程的完整性與一致性
- 建立 Workspace 機制作為教師個人工作隔離層
- 重構雙路徑問題為單一標準路徑
- 新增安裝與認證腳本，降低教師入門門檻
- 完善 DI 分類工具與決策樹
- 更新核心設定檔案以支援新架構
- 重寫 Teacher Guide 2.0 版本

---

## 二、測試階段產出

所有測試產出檔案位於：
**`/sessions/upbeat-wizardly-wozniak/mnt/WaldorfTeacherOS-Repo/workspaces/工作範例參考/projects/class-claude/`**

### 已完成的產出檔案列表

#### 課程設計文件
- `/workspaces/工作範例參考/projects/class-claude/english/content/english-syllabus-v1-20260303.md`
  完整的英文課程大綱（Block 1 產出），包含全學期教學目標、15 週課程規劃、差異化策略、評量架構

- `/workspaces/工作範例參考/projects/class-claude/english/content/english-unit-1-v1-20260303.md`
  Unit 1 完整逐節教案（Block 2 完整版），包含 8 節 45 分鐘課堂設計，每節課含四段式結構、ABCD 差異化任務、材料清單、教師備忘

- `/workspaces/工作範例參考/projects/class-claude/english/content/english-units-2-4-v1-20260303.md`
  Units 2-4 標準版教案（Block 2 標準版），包含每週摘要、學習目標、關鍵活動、差異化重點、材料清單

#### 歷程紀錄文件
- `/workspaces/工作範例參考/projects/class-claude/english/content/records/student-logs/sample-logs.md`
  6 位學生學習歷程（Block 3 產出），展示不同學習風格學生的個人化追蹤紀錄

- `/workspaces/工作範例參考/projects/class-claude/english/content/records/unit-logs.md`
  4 單元班級紀錄（Block 3 產出），每單元的班級集體觀察與發展軌跡

- `/workspaces/工作範例參考/projects/class-claude/english/content/records/teacher-reflections.md`
  6 篇教學反思（Block 3 產出），教師對各階段教學的專業反思

#### 評量與結案文件
- `/workspaces/工作範例參考/projects/class-claude/english/content/student-assessments-20260510.md`
  18 位學生評量報告（Block 4 產出），質性學習評量、個別發展評語、建議事項

- `/workspaces/工作範例參考/projects/class-claude/english/content/teacher-term-report-20260510.md`
  學期教學報告（Block 4 產出），整學期教學成效反思、班級發展分析、課程調整建議

#### 班級設定檔案
- `/workspaces/工作範例參考/projects/class-claude/project.yaml`
  班級基本設定（班級代碼、學生人數、學期代碼、聯絡方式）

- `/workspaces/工作範例參考/projects/class-claude/roster.yaml`
  班級名單（21 位學生，含姓名、性別、出生年月、家長資訊）

- `/workspaces/工作範例參考/projects/class-claude/students.yaml`
  學生樣態概覽（每生摘要：優勢、挑戰、學習風格、備註）

- `/workspaces/工作範例參考/projects/class-claude/english/di-profile.yaml`
  英文課差異化學生分類（ABCD 能力×動機矩陣分類）

- `/workspaces/工作範例參考/projects/class-claude/working/english-session.yaml`
  英文課進度錨點（Block 1-4 進度、當前工作狀態、下次行動）

- `/workspaces/工作範例參考/projects/class-claude/index.md`
  班級文件索引（所有輸出文件的快速導覽）

- `/workspaces/工作範例參考/teacheros-personal.yaml`
  Teacher Claude 個人身份卡片（教師身份、教學理念、工作偏好）

- `/workspaces/工作範例參考/workspace.yaml`
  Workspace 設定檔（班級列表、學期代碼、聯絡人、權限設定）

---

## 三、架構修改清單

### 修改 1：Workspace 機制建立（核心）

**目的**: 為每個教師建立獨立的個人工作隔離層，實現「共用系統 + 個人空間」的三層架構

**新增檔案**:
- `/workspaces/` 目錄
- `/workspaces/README.md` - Workspace 系統說明
- `/workspaces/_template/` - 教師 Workspace 標準範本
  - `/workspaces/_template/workspace.yaml`
  - `/workspaces/_template/teacheros-personal.yaml`
  - `/workspaces/_template/philosophy.yaml`
  - `/workspaces/_template/README.md`
  - `/workspaces/_template/projects/_class-template/` - 班級範本骨架

- `/workspaces/工作範例參考/` - 完全完成的參考 Workspace（教學用）
  - 包含 Teacher Claude 的全部 Block 1-4 產出
  - 用作新教師的學習參考與最佳實踐展示
  - 標記為唯讀

- `/workspaces/david-teacher/` - David 個人 Workspace（正式使用）
  - 自動建立的空白範本
  - 包含基礎 teacheros-personal.yaml 與 philosophy.yaml

**修改邏輯**:
- 原 `/projects/class-claude/` 整個資料夾已搬遷至 `/workspaces/工作範例參考/projects/class-claude/`
- 每個教師獲得完整的 `/workspaces/{教師名稱}/` 隔離空間
- Workspace 內部結構標準化：
  ```
  workspaces/{教師名稱}/
  ├── teacheros-personal.yaml       ← 個人身份卡片
  ├── philosophy.yaml               ← 教學哲學詳述
  ├── workspace.yaml                ← Workspace 設定
  ├── projects/
  │   ├── class-{班級代碼}/        ← 班級資料夾
  │   │   ├── project.yaml
  │   │   ├── students.yaml
  │   │   ├── roster.yaml
  │   │   ├── {subject}/
  │   │   │   ├── di-profile.yaml
  │   │   │   ├── content/         ← Block 1-4 產出
  │   │   │   └── reference/       ← 教學資源
  │   │   └── working/             ← 工作檔案
  │   └── ...
  └── templates/                    ← 個人範本庫
  ```

**權限管理**:
- Workspace 內檔案：教師享有 100% 完全編輯權
- `_template/` 與 `工作範例參考/`：唯讀（保護模板與參考的完整性）
- ai-core/ 與 setup/：所有教師無法編輯（由 David 維護）

---

### 修改 2：雙路徑改單路徑（重要）

**問題識別**:
原系統存在路徑重複問題：
- `/projects/class-9c/content/english/` 與 `/projects/class-9c/english/content/` 並存
- 造成維護混亂與版本不一致

**解決方案**:
- 統一標準路徑為：`{class-folder}/{subject}/content/`
- 移除 `content/` 一層外的重複路徑
- 新增 `/projects/class-9c/content/english/index.md` 作為索引檔，重定向到標準路徑

**修改檔案**:
- `/projects/class-9c/english/` 結構確認（保持不變）
- 移除 `/projects/class-9c/content/english/` 中的舊檔案（已轉移至標準路徑）
- 新增 `index.md` 提供文檔導覽

**驗證**:
所有 class-4c、class-9c、class-9d 均按新標準路徑檢查完畢，Workspace 內新班級也遵循此標準。

---

### 修改 3：安裝與認證腳本（使用性）

**新增檔案**:
- `/setup/quick-start.sh`
  一鍵安裝腳本，教師執行此腳本自動完成：
  - Git hooks 安裝（`setup/install-hooks.sh`）
  - 個人環境設定檢查（`setup/environment.env`）
  - 系統依賴檢查（`setup/setup-check.sh`）
  - 輸出友善的設定完成報告

- `/setup/add-teacher.sh`
  管理員用腳本，自動完成新教師環境建立：
  - 交互式詢問新教師資訊（姓名、Email、班級代碼）
  - 自動寫入 `ai-core/acl.yaml`
  - 自動建立 Workspace 目錄結構
  - 自動複製 `_template/` 到新 Workspace
  - 準備提交 PR 的 git 指令

**使用流程**:
```bash
# 教師自助安裝
bash setup/quick-start.sh

# 管理員（David）為新教師建立環境
bash setup/add-teacher.sh
```

---

### 修改 4：DI 分類工具完善（功能性）

**新增檔案**:
- `/projects/_di-framework/content/di-classification-guide.md`
  完整的差異化教學學生分類指南，包含：
  - 能力×動機矩陣（ABCD 四類型）
  - 決策樹：如何識別與分類學生
  - 行為問卷：客觀觀察指標
  - 學習優勢檢核表：多維度評估
  - 教學策略對應表：每類型的具體應用

**內容概述**:
- **A型**（高能力、高動機）：延伸挑戰、自主學習、同儕領導
- **B型**（低能力、高動機）：小步成功、鷹架支持、正面回饋
- **C型**（高能力、低動機）：連結興趣、提供選擇、意義建立
- **D型**（低能力、低動機）：降低焦慮、具體操作、一對一支持

**使用場景**:
- Block 1 進行時：AI 協助教師理解每位學生的類型
- Block 2 設計時：AI 根據分類設計 ABCD 四層差異化任務
- Block 3 紀錄時：AI 動態更新學生分類（流動性原則）

---

### 修改 5：核心設定更新（系統）

**修改檔案**:

#### a. `/ai-core/acl.yaml`
- 新增 `Teacher Claude` 條目（唯讀參考教師）
  ```yaml
  - name: Teacher Claude
    email: teacher-claude@waldorf.example
    github_username: teacher-claude-ref
    workspace: workspaces/工作範例參考/
    allowed_paths:
      - workspaces/工作範例參考/
    blocked_paths:
      - ai-core/
      - setup/
      - .github/
      - publish/build.sh
  ```

- 新增 `David 老師` 條目（正式教師）
  ```yaml
  - name: David 老師
    email: elliot200852+teacher@gmail.com
    github_username: elliot200852-lab
    workspace: workspaces/david-teacher/
    allowed_paths:
      - projects/class-9c/
      - workspaces/david-teacher/
    blocked_paths:
      - ai-core/
      - setup/
      - .github/
      - publish/build.sh
  ```

- 增加 Workspace 建立流程說明（註解區塊）
  ```yaml
  # Workspace 建立流程
  # 1. 新教師提供：姓名、Email、班級代碼、科目
  # 2. 管理員執行：bash setup/add-teacher.sh
  # 3. 腳本自動：寫入 acl.yaml + 建立 workspace + 複製模板
  # 4. 管理員 commit + push，教師 pull 即可使用
  ```

#### b. `/ai-core/teacheros.yaml`
- 新增 `workspace_system` 區塊（在檔案末尾）
  ```yaml
  workspace_system:
    enabled: true
    architecture:
      - name: 共用層
        path: ai-core/
        access: read-only for all teachers
        content: 系統核心、參考模組、技能正本

      - name: 範本層
        path: workspaces/_template/
        access: read-only
        content: 教師 Workspace 標準範本、班級範本骨架

      - name: 個人層
        path: workspaces/{教師名稱}/
        access: full control for teacher
        content: 個人身份卡片、班級資料、產出文件

    teacher_onboarding:
      step_1: 新教師向 David 提供基本資訊（姓名、Email、班級代碼）
      step_2: David 執行 bash setup/add-teacher.sh
      step_3: 系統自動建立 Workspace、寫入 ACL、複製範本
      step_4: David commit + push，教師 pull 即可使用
      step_5: 教師編輯 teacheros-personal.yaml 與 philosophy.yaml
      step_6: 可參考 workspaces/工作範例參考/ 理解完整工作流

    workspace_structure:
      reference: "見 setup/teacher-guide.md 的「Workspace 說明」章節"
  ```

- 確認 `reference_loading_protocol` 區塊（已存在，需驗證）
  確保 pedagogy/english/history/student 四個模組的載入條件明確

---

### 修改 6：Teacher Guide 重寫（2.0 版本）

**檔案路徑**: `/setup/teacher-guide.md`

**重寫方向與內容**:

#### a. 降低入門門檻
- 原版本：技術術語過多，假設教師熟悉 Git/Terminal
- 新版本：完全無技術背景也能快速上手
  - 使用生活化比喻：「門鎖/鑰匙」（Git Hooks）、「圖書館」（Workspace 結構）、「智慧檔案櫃」（Git 工具）
  - 三步驟快速開始（GitHub 帳號 → 下載系統 → 一鍵安裝）
  - 分別針對 Mac 與 Windows 使用者提供終端機指引

#### b. 加入工具下載連結
- GitHub 官網連結：https://github.com（含截圖說明）
- Git 下載連結：https://git-scm.com/downloads（含安裝選項說明）
- Terminal 使用指引（针对 Mac 與 Windows）

#### c. 新增 Workspace 說明
- Workspace 概念導覽（圖書館比喻）
- 工作空間結構說明與檔案樹狀圖
- 權限說明（你能看什麼、不能看什麼）
- 參考工作範例引導（`workspaces/工作範例參考/`）
- 其他教師工作空間的互相學習方式

#### d. 新增 Block 2 支援說明
- 增加「產出詳細度選項」章節
  - 精簡版（1-2 頁/單元）
  - 標準版（3-5 頁/單元）
  - 完整版（8-15 頁/單元）
- 教師可在與 AI 對話時指定需要的詳細度
- 提供三種範例的文件連結

#### e. 教師身份設定指南
- 編輯 `teacheros-personal.yaml` 的逐步說明
- 填寫教學理念、科目、年級、教學偏好
- 舉例展示 Teacher Claude 的填寫方式

#### f. 新增班級建立 SOP
- 如何在 Workspace 內新增班級
- 班級資料夾的標準結構
- 如何填寫 project.yaml、students.yaml、roster.yaml

#### g. 常見問題（FAQ）
- 「我能看到其他教師的工作嗎？」— 可以讀取，無法編輯
- 「我的檔案其他人能看嗎？」— 只有授權教師能讀
- 「修改錯了怎麼辦？」— Git 記錄所有歷史，可恢復
- 「Google Docs 怎麼連接？」— 見 setup/environment.env

**版本號**: 2.0（與 Workspace 機制同步發布）

---

### 修改 7：Block 2 框架更新

**檔案路徑**: `/projects/_di-framework/content/english-di-block2.md`

**新增內容**:

#### 產出詳細度選項區塊（第 22-51 行）
```markdown
## 產出詳細度選項（三種模式）

教師可依需求選擇不同的產出詳細度。建議至少為第一單元選擇「完整版」，後續單元可視情況調整。

| 模式 | 名稱 | 適用情境 | 產出內容 |
|------|------|----------|----------|
| **精簡版** | 單元概覽 | 有經驗的老師快速參考 | 每單元：核心問題、教學目標、主要活動清單、評量方式（約 1-2 頁） |
| **標準版** | 每週摘要 | 第二單元以後的常態使用 | 每週：學習目標、關鍵活動描述、差異化重點、材料清單（約 3-5 頁/單元） |
| **完整版** | 逐節教案 | 第一單元或需要詳細規劃時 | 每節 45 分鐘：四段式結構（暖身→主活動→檢核→收尾）、ABCD 差異化任務、特殊需求支持、教師備忘（約 8-15 頁/單元） |

### 建議使用策略
1. **第一單元**：選擇「完整版」——建立教學節奏與差異化基準
2. **第二單元起**：依信心與經驗選擇「標準版」或「精簡版」
3. **遇到困難的單元**：隨時切回「完整版」

### AI 指令範例
教師可在與 AI 對話時用這樣的指令指定詳細度：
- 「請用標準版幫我設計第二單元。」
- 「第三單元我只需要精簡版的概覽。」
- 「這個單元比較複雜，請用完整版。」

### 範例參考
Teacher Claude 的產出展示了不同詳細度的實例：
- **完整版範例**：`workspaces/工作範例參考/projects/class-claude/english/content/english-unit-1-v1-20260303.md`（Unit 1，8 節完整教案）
- **標準版範例**：`workspaces/工作範例參考/projects/class-claude/english/content/english-units-2-4-v1-20260303.md`（Units 2-4，每週摘要）
```

**改動影響**:
- 此修改使 Block 2 更靈活，適應不同教師的工作節奏
- 降低完美主義壓力，允許「漸進式優化」工作流
- 為 AI 提供明確的產出規格，確保品質一致

---

## 四、已知待辦事項（下次工作建議）

### 優先度：高
1. **差異化教學系統細項設計**
   位置：`projects/_di-framework/`
   進度：Block 1-3 已完成，Block 4 評量部分需要進一步開發
   建議：增加「學習檔案夾（Learning Portfolio）」的系統化設計

2. **Workspace 路徑檢查的 Pre-commit Hook 更新**
   位置：`setup/hooks/pre-commit`
   進度：原 Hook 尚未更新以支援 Workspace 路徑驗證
   建議：新增規則檢查教師無法異動 ai-core/ 與其他 Workspace 檔案

3. **System Status 檔案更新**
   位置：`ai-core/system-status.yaml`
   進度：尚未反映 Workspace 架構
   建議：加入 Workspace 清單、教師線上狀態、系統運作指標

### 優先度：中
4. **Google Calendar 整合的 Workspace 適配**
   位置：`setup/gcal-write.py`
   進度：原腳本針對 projects/ 結構設計
   建議：更新以支援 workspaces/ 內的班級日曆同步

5. **空白班級模板的其他科目支援**
   位置：`workspaces/_template/projects/_class-template/`
   進度：目前只有英文骨架
   建議：添加人文、歷史、數學等科目的標準範本

6. **教案模板庫建立**
   位置：`workspaces/_template/templates/`
   進度：未建立
   建議：以 Teacher Claude 產出為範例一，逐步累積更多科目與年級的範例

### 優先度：低
7. **AI_HANDOFF 文件定期更新**
   位置：`ai-core/AI_HANDOFF.md`
   進度：2026-03-02 版本
   建議：每個測試週期後更新（現已是 03-03，建議下次在 03-10）

---

## 五、檔案變動總覽

### 新增檔案（共 31 個）

#### Workspace 相關（10 個）
- `/workspaces/README.md`
- `/workspaces/_template/README.md`
- `/workspaces/_template/workspace.yaml`
- `/workspaces/_template/teacheros-personal.yaml`
- `/workspaces/_template/philosophy.yaml`
- `/workspaces/_template/projects/_class-template/project.yaml`
- `/workspaces/_template/projects/_class-template/roster.yaml`
- `/workspaces/_template/projects/_class-template/students.yaml`
- `/workspaces/_template/projects/_class-template/english/di-profile.yaml`
- `/workspaces/_template/projects/_class-template/working/english-session.yaml`

#### 教學參考產出（19 個）
- `/workspaces/工作範例參考/projects/class-claude/index.md`
- `/workspaces/工作範例參考/projects/class-claude/project.yaml`
- `/workspaces/工作範例參考/projects/class-claude/roster.yaml`
- `/workspaces/工作範例參考/projects/class-claude/students.yaml`
- `/workspaces/工作範例參考/projects/class-claude/english/di-profile.yaml`
- `/workspaces/工作範例參考/projects/class-claude/english/content/english-syllabus-v1-20260303.md`
- `/workspaces/工作範例參考/projects/class-claude/english/content/english-unit-1-v1-20260303.md`
- `/workspaces/工作範例參考/projects/class-claude/english/content/english-units-2-4-v1-20260303.md`
- `/workspaces/工作範例參考/projects/class-claude/english/content/records/student-logs/sample-logs.md`
- `/workspaces/工作範例參考/projects/class-claude/english/content/records/unit-logs.md`
- `/workspaces/工作範例參考/projects/class-claude/english/content/records/teacher-reflections.md`
- `/workspaces/工作範例參考/projects/class-claude/english/content/student-assessments-20260510.md`
- `/workspaces/工作範例參考/projects/class-claude/english/content/teacher-term-report-20260510.md`
- `/workspaces/工作範例參考/projects/class-claude/working/english-session.yaml`
- `/workspaces/工作範例參考/teacheros-personal.yaml`
- `/workspaces/工作範例參考/workspace.yaml`
- `/workspaces/david-teacher/README.md`
- `/workspaces/david-teacher/philosophy.yaml`
- `/workspaces/david-teacher/workspace.yaml`（初始版本）

#### 指令與工具（2 個）
- `/setup/quick-start.sh`
- `/setup/add-teacher.sh`

### 修改檔案（6 個）

#### 系統設定
- `/ai-core/acl.yaml`
  新增 Teacher Claude 與 David 老師條目，增加 Workspace 建立流程說明

- `/ai-core/teacheros.yaml`
  新增 workspace_system 區塊，包含三層架構說明與教師入職流程

#### 文件與指南
- `/setup/teacher-guide.md`（重寫 2.0 版本）
  - 降低技術門檻，使用生活化比喻
  - 新增工具下載連結與終端機使用指引
  - 加入 Workspace 說明與工作範例參考引導
  - 新增 Block 2 詳細度選項說明
  - 新增 FAQ 與班級建立 SOP

#### 框架與標準
- `/projects/_di-framework/project.yaml`
  確認版本號並添加新引用

- `/projects/_di-framework/content/di-classification-guide.md`（新增）
  完整的 DI 分類決策樹、行為問卷、學習優勢檢核表

- `/projects/_di-framework/content/english-di-block2.md`
  新增「產出詳細度選項」區塊（第 22-51 行）

### 刪除檔案

本次測試後：
- `/projects/class-claude/` 整個資料夾已搬遷至 `/workspaces/工作範例參考/projects/class-claude/`
- 原位置已不存在（檔案已遷移，非刪除）

---

## 六、接手指引

### 下一個 AI 工作階段啟動流程

任何 AI 在開始工作前，請依照以下順序初始化系統狀態：

#### Step 1：載入系統身份層
1. 讀取 `/ai-core/teacheros.yaml`
   目的：確認教師身份、教學哲學、工作偏好、語氣錨點

2. 讀取 `/ai-core/acl.yaml`
   目的：確認使用者身份與授權範圍，防止超權操作

3. 讀取 `/ai-core/AI_HANDOFF.md`
   目的：確認技能系統與工作啟動流程

#### Step 2：確認工作上下文
4. 根據使用者輸入判斷工作類型（備課 / 導師 / 評量 / 系統管理）

5. 若是班級工作：載入對應班級的以下檔案
   - `/projects/class-{班級代碼}/project.yaml` — 班級脈絡
   - `/projects/class-{班級代碼}/students.yaml` — 學生樣態
   - `/projects/class-{班級代碼}/{科目}/working/{科目}-session.yaml` — 進度錨點
   - 若教師使用 Workspace：優先從 `/workspaces/{教師名稱}/projects/class-{班級代碼}/` 載入

6. 若使用者是新教師（workspace 剛建立）：
   - 載入 `/workspaces/{教師名稱}/teacheros-personal.yaml` — 個人身份卡片
   - 載入 `/setup/teacher-guide.md` — 快速入門指南
   - 提供參考 `/workspaces/工作範例參考/` 的引導

#### Step 3：主動報告系統狀態
7. 載入完成後，主動說：
   ```
   已載入系統。[教師名] [班級] 的 [科目] 課程目前在 Block [X] Step [Y]。
   上次工作：[last_action]
   下一步：[next_action]

   說「進入備課」我會直接設計；說「查狀態」我會更新進度。要開始嗎？
   ```

#### Step 4：執行技能系統
8. 根據使用者輸入觸發對應技能（見 `/ai-core/AI_HANDOFF.md` 的技能表）

9. 工作結束時，觸發 session-end 技能更新進度檔案

### 常見場景

#### 場景 A：新教師首次使用
```
預期載入：
  teacheros-personal.yaml（個人身份）
  setup/teacher-guide.md（快速入門）
  workspaces/工作範例參考/（參考範例）

預期行動：
  1. 歡迎並介紹系統
  2. 引導讀取 Teacher Guide
  3. 協助編輯 teacheros-personal.yaml
  4. 協助創建第一個班級
  5. 開始 Block 1（學季規劃）
```

#### 場景 B：持續合作（延續前次工作）
```
預期載入：
  teacheros-personal.yaml
  working/{科目}-session.yaml（進度錨點）
  前次工作的中途草稿

預期行動：
  1. 讀出當前進度
  2. 確認教師意圖（繼續或調整）
  3. 直接進入設計工作
  4. 工作結束時 session-end 更新進度
```

#### 場景 C：系統問題排查
```
預期載入：
  ai-core/system-status.yaml（系統狀態快照）
  ai-core/acl.yaml（檢查權限）
  相關的 Workspace 或班級 YAML

預期行動：
  1. 分析問題根源
  2. 提出修復建議
  3. 若涉及 ai-core/，提醒需要 David 審核
  4. 生成排查報告
```

---

## 七、系統驗證檢查表

下一個 AI 工作階段啟動時，可用此檢查表驗證系統完整性：

- [ ] Workspace 目錄結構存在：`/workspaces/`
- [ ] 模板存在：`/workspaces/_template/`
- [ ] 教學參考存在：`/workspaces/工作範例參考/`
- [ ] 新教師 Workspace 存在：`/workspaces/david-teacher/` 或其他
- [ ] ACL 檔案已更新：`/ai-core/acl.yaml` 含 Teacher Claude 條目
- [ ] TeacherOS 身份已更新：`/ai-core/teacheros.yaml` 含 workspace_system 區塊
- [ ] Teacher Guide 已升級：`/setup/teacher-guide.md` 版本 >= 2.0
- [ ] DI 分類指南存在：`/projects/_di-framework/content/di-classification-guide.md`
- [ ] Block 2 詳細度說明已加入：`/projects/_di-framework/content/english-di-block2.md`
- [ ] Quick Start 腳本存在且可執行：`/setup/quick-start.sh`
- [ ] Add Teacher 腳本存在且可執行：`/setup/add-teacher.sh`
- [ ] Teacher Claude 參考產出完整（11 個檔案）：見本文件第二部分

---

## 八、重要設計決策與理由

### 為什麼採用 Workspace 機制？
- **隔離性**：每個教師的工作空間獨立，降低誤操作風險
- **可擴展性**：新增教師無需修改系統核心，只需複製範本
- **學習友善**：教師可自由實驗，無需擔心影響他人或系統
- **權限管理**：透過路徑隔離實現精細的存取控制

### 為什麼移除雙路徑？
- **維護簡化**：單一標準路徑減少版本分岐風險
- **清晰性**：教師不困惑於「我的檔案在哪裡」
- **自動化支援**：系統腳本可依一致規則尋找檔案

### 為什麼 Block 2 要提供詳細度選項？
- **彈性**：尊重教師的工作節奏與經驗等級
- **實用性**：有經驗的教師不需要逐節教案細節
- **品質保證**：無論哪種詳細度，品質標準一致

### 為什麼 DI 分類要做成決策樹？
- **客觀性**：提供具體的觀察指標，減少主觀判斷
- **流動性**：明確表示分類可變更，不是永久標籤
- **行動性**：每個分類直接對應教學策略

---

## 九、與外部工具的整合狀態

### Google Calendar 整合
**現況**：`setup/gcal-write.py` 支援將班級課表寫入 Google Calendar
**更新需求**：支援 Workspace 路徑的班級資料讀取
**優先度**：中（在「工具適配」階段處理）

### Google Docs 輸出
**現況**：系統預留輸出接口，可自動將 Markdown 文件轉檔至 Google Docs
**狀態**：尚未實裝完整端對端流程
**優先度**：低（教師可手動複製貼上，暫時可接受）

### GitHub 工作流
**現況**：使用 PR 審核機制，保護 ai-core/ 與 setup/ 路徑
**配置檔**：`.github/CODEOWNERS`
**狀態**：正常運作，已驗證

---

## 十、接手者應注意事項

### 避免的操作
- **勿刪除 workspaces/工作範例參考/**：這是教學用參考，其他教師依賴此參考學習
- **勿修改 ai-core/acl.yaml 中的 protected_always 路徑**：這些路徑受 GitHub 審核保護
- **勿在 ai-core/ 中新增教師特定的設定**：所有教師特定設定應放在各自的 workspace
- **勿直接編輯他人的 workspace**：尊重教師的工作邊界

### 應該做的操作
- **定期備份 ai-core/ 檔案**：特別是 acl.yaml 與 teacheros.yaml
- **定期更新 system-status.yaml**：反映當前系統狀態
- **監視 workspaces/ 大小**：防止產出檔案無限增長
- **發現問題時立即記錄**：保存錯誤訊息與重現步驟，便於下一個 AI 診斷

### 文件同步原則
- `ai-core/` 內的所有文件是「正本」，修改時需極其謹慎
- `.claude/commands/` 內的檔案是「薄層入口」，會自動指向 `ai-core/skills/` 正本
- Workspace 內的檔案可自由修改，不需向系統報告
- 任何修改 ai-core/ 的決定都應通過 Git PR 與 David 審核

---

## 附錄：重要檔案快速索引

| 用途 | 檔案位置 | 主要內容 |
|------|----------|---------|
| 教師身份與設定 | `/ai-core/teacheros.yaml` | 教師身份、教學理念、工作偏好、參考模組載入規則 |
| 系統權限控制 | `/ai-core/acl.yaml` | 使用者角色、Workspace 授權、路徑存取控制 |
| AI 工作流程入口 | `/ai-core/AI_HANDOFF.md` | 技能系統、載入順序、觸發語 |
| 技能正本目錄 | `/ai-core/skills/` | 所有工作技能的完整規格 |
| 差異化教學框架 | `/projects/_di-framework/` | Block 1-4 設計模板、品質標準、範例 |
| 教師快速入門 | `/setup/teacher-guide.md` | 環境設定、Workspace 概念、三步驟快速開始 |
| Workspace 模板 | `/workspaces/_template/` | 新教師 Workspace 的標準結構 |
| 完整工作參考 | `/workspaces/工作範例參考/` | Teacher Claude 的全部 Block 1-4 產出 |
| 個人 Workspace 入口 | `/workspaces/{教師名稱}/` | 教師的班級、課程、產出檔案 |

---

*本文件由 Claude (Cowork Mode) 自動生成於 2026-03-03*
*供下一個 AI 工作階段無縫接手 TeacherOS 系統*
*請每次工作結束後根據新的修改更新此交接文件*
