---
aliases:
  - "AI 交接文件 v3"
---

# TeacherOS AI 交接文件（v3）

> 日期：2026-03-03
> 上一次工作者：Claude (Cowork Mode)
> 版本：v3（取代 v2，新增第三輪變更：Git 協作模型、AI 技能擴充、教師手冊重寫）
> 目的：記錄所有架構修改，供下一個 AI 工作階段無縫接手

---

## 一、三輪工作摘要

**第一輪**：以「Teacher Claude」身份模擬八年級英文教師，完成 Block 1-4 全流程測試，並根據測試結果建立 Workspace 機制、修正七大架構問題。

**第二輪**：標準化 Workspace 命名規則、建立 Working_Member 容器層、搬遷 David 的班級資料、建立 Engineer_Reference 版本化歸檔。

**第三輪（本次新增）**：建立 Git 多人協作模型、建立 save / pull-request 技能、自動化 branch 建立與切換、重寫 teacher-guide.md 以「AI 口語指令」為主要操作方式。

---

## 二、第三輪核心設計決策

### 決策 1：Git 協作模型 — Collaborator + Branch

**考慮過的方案**：

| 方案 | 優點 | 致命缺點 |
|------|------|----------|
| Fork 模式 | 完全隔離，教師不影響彼此 | 教師無法看到彼此的檔案（除非 David 合併後），違反學校社群共享精神 |
| Collaborator + Branch 模式 | 所有人在同一 repo，`git fetch` 即可看到彼此的工作 | 需要 Branch Protection 防止直接推 main |

**最終選擇**：Collaborator + Branch 模式

**配套保護機制**：
- **Branch Protection Rule**（GitHub 設定）：保護 main branch，所有合併必須通過 PR，只有 David 可批准
- **CODEOWNERS**：`.github/CODEOWNERS` 定義 David 為所有核心路徑的 Code Owner
- **Pre-commit Hook**：本地軟性保護，提醒教師不要修改授權範圍外的檔案（可被 `--no-verify` 繞過）
- **個人 Branch**：每位教師在 `workspace/{Teacher_ID}` branch 上自由 commit，不需要任何審批

**關鍵澄清**：Branch Protection 只保護 main branch 的合併，不影響教師在自己 branch 上的日常 commit。教師一天 commit 多少次都不需要 David 批准。

### 決策 2：雙路徑操作模式

| 方式 | 適用對象 | 操作方法 |
|------|----------|----------|
| 方式 A：跟 AI 說 | 使用能讀取專案檔案的 AI 工具（Claude Code、Gemini Antigravity 等） | 直接口語指令，AI 讀取技能檔並自動執行 |
| 方式 B：終端機腳本 | AI 工具不支援檔案讀取時的備用方案 | `bash setup/save.sh "說明"` |

**工具無關性原則**：技能正本統一在 `ai-core/skills/`，任何有檔案讀取能力的 AI 都可直接讀取並執行。不限定 Claude Code，Gemini、ChatGPT 等亦適用。

### 決策 3：教師手冊以 AI 口語指令為主

David 明確指示：教師不應學習終端機指令，所有 Git 操作應透過 AI 口語指令完成。終端機指令僅作為附錄備用。

---

## 三、第三輪新增與修改檔案清單

### 新增檔案

| 檔案 | 用途 |
|------|------|
| `ai-core/skills/save.md` | 存檔技能 — 教師說「存檔」觸發 git add + commit + push |
| `ai-core/skills/pull-request.md` | 合併申請技能 — 教師說「發 PR」觸發合併申請流程 |
| `.claude/commands/save.md` | Claude Code 薄層入口 → 指向 `ai-core/skills/save.md` |
| `.claude/commands/pull-request.md` | Claude Code 薄層入口 → 指向 `ai-core/skills/pull-request.md` |
| `setup/save.sh` | 一行存檔腳本：`bash setup/save.sh "說明"` 自動執行 git add → commit → push |
| `setup/quick-start.sh` | 教師一鍵安裝腳本（新增 Check 8：自動偵測並切換個人 branch） |

### 修改檔案

| 檔案 | 修改內容 |
|------|----------|
| `setup/add-teacher.sh` | 新增 Step 6 `create_teacher_branch()` — 自動建立 `workspace/{Teacher_ID}` branch 並推送至 GitHub |
| `setup/teacher-guide.md` | 第十三節全面重寫：Git 工作流程改為 AI 口語指令為主、終端機為附錄 |
| `ai-core/AI_HANDOFF.md` | 技能觸發表新增 save 與 pull-request 兩項，新增工具無關性說明 |

---

## 四、技能系統完整對照表（截至 v3）

| 技能 | 教師說 | 檔案路徑 | 用途 |
|------|--------|----------|------|
| `load` | 「載入 9C」 | `ai-core/skills/load.md` | 載入班級脈絡 |
| `status` | 「現在在哪？」 | `ai-core/skills/status.md` | 查詢進度 |
| `syllabus` | 「開始大綱」 | `ai-core/skills/syllabus.md` | 啟動 Block 1 |
| `lesson` | 「進入備課」 | `ai-core/skills/lesson.md` | Block 2 課堂設計 |
| `session-end` | 「收尾」 | `ai-core/skills/session-end.md` | 更新進度 |
| `di-check` | 「查 DI」 | `ai-core/skills/di-check.md` | DI 合規核對 |
| `ref` | 「載入教學哲學」 | `ai-core/skills/ref.md` | 載入 Reference |
| `homeroom` | 「導師業務」 | `ai-core/skills/homeroom.md` | 班級經營 |
| `block-end` | 「區塊結束」 | `ai-core/skills/block-end.md` | Block 反思 |
| `rhythm` | 「設計節奏」 | `ai-core/skills/rhythm.md` | 週節奏規劃 |
| `student-note` | 「記錄學生」 | `ai-core/skills/student-note.md` | 觀察記錄 |
| `parent-letter` | 「寫家長信」 | `ai-core/skills/parent-letter.md` | 家長通知 |
| **`save`** | 「存檔」「幫我存」 | `ai-core/skills/save.md` | **Git 存檔並上傳** |
| **`pull-request`** | 「發 PR」「送回主系統」 | `ai-core/skills/pull-request.md` | **合併申請** |

（粗體為本次新增）

---

## 五、Branch 生命週期

```
David 執行 add-teacher.sh
       │
       ▼
  建立 workspace 資料夾
  更新 acl.yaml 權限
  建立 workspace/{Teacher_ID} branch ← Step 6（新增）
  推送 branch 至 GitHub
       │
       ▼
教師執行 quick-start.sh
       │
       ▼
  Check 1-7: 環境檢查
  Check 8: 自動偵測 workspace/ branch ← 新增
           → 單一 branch → 自動切換
           → 多個 branch → 列出選項
           → 無 branch → 提示聯絡 David
       │
       ▼
教師在個人 branch 上自由工作
  ├── 日常：「存檔」→ save 技能 → git add + commit + push
  ├── 看別人的工作：「幫我看其他老師的檔案」→ git fetch
  └── 學期末：「發 PR」→ pull-request 技能 → 向 main 發 PR
       │
       ▼
David 在 GitHub 審核 PR → 合併進 main
```

---

## 六、目前的資料夾結構（權威版 v3）

```
WaldorfTeacherOS-Repo/
│
├── ai-core/                              ← 系統核心（只有 David 修改）
│   ├── teacheros.yaml                    ← 教師身份、哲學、workspace_system
│   ├── acl.yaml                          ← 權限控制（角色、路徑、命名規則）
│   ├── AI_HANDOFF.md                     ← AI 技能系統與工作啟動流程
│   ├── system-status.yaml                ← 系統現況快照
│   └── skills/                           ← 技能正本（所有 AI 共用）
│       ├── save.md                       ← ★ 新增：存檔技能
│       ├── pull-request.md               ← ★ 新增：合併申請技能
│       └── ...（其餘技能）
│
├── projects/                             ← 共用教學框架
│   ├── _di-framework/                    ← 差異化教學共用框架
│   └── _class-template/                  ← 空白班級範本
│
├── workspaces/                           ← 所有教師的工作空間
│   ├── README.md
│   ├── _template/                        ← 新老師範本
│   ├── 工作範例參考/                      ← Block 1-4 完整範例（唯讀）
│   └── Working_Member/                   ← 所有活躍教師
│       └── Codeowner_David/              ← David 的工作空間
│           └── projects/
│               ├── class-9c/             ← 25 個檔案
│               └── class-9d/             ← 7 個檔案
│
├── Engineer_Reference/                   ← 版本化歸檔
│   ├── TeacherOS-AI-交接文件_v1_20260303.md
│   ├── TeacherOS-AI-交接文件_v2_20260303.md
│   ├── TeacherOS-AI-交接文件_v3_20260303.md  ← 本文件
│   └── ...
│
├── setup/                                ← 設定工具
│   ├── quick-start.sh                    ← 教師一鍵安裝（含 branch 自動切換）
│   ├── add-teacher.sh                    ← 管理員建立 workspace + branch
│   ├── save.sh                           ← ★ 新增：一行存檔腳本
│   ├── teacher-guide.md                  ← 教師手冊 v2.0（AI 口語指令版）
│   └── ...
│
├── .claude/commands/                     ← Claude Code slash command 入口
│   ├── save.md                           ← ★ 新增
│   └── pull-request.md                   ← ★ 新增
│
└── .github/
    └── CODEOWNERS
```

---

## 七、三層保護機制總覽

| 層級 | 機制 | 執行位置 | 強度 | 保護內容 |
|------|------|----------|------|----------|
| 第一層 | Pre-commit Hook | 本地（教師電腦） | 軟（可被 `--no-verify` 繞過） | 提醒教師不要修改授權範圍外的檔案 |
| 第二層 | CODEOWNERS | GitHub 伺服器 | 硬（配合 Branch Protection） | 指定核心路徑的 Code Owner |
| 第三層 | Branch Protection Rule | GitHub 伺服器 | 硬（GitHub 強制執行） | 保護 main branch，合併需 PR + David 審批 |

**重要區分**：Branch Protection 只攔截「合併到 main」，不攔截教師在個人 branch 上的任何 commit 或 push。

---

## 八、接手指引（v3 更新）

### AI 工作階段啟動流程

#### Step 1：載入系統身份層
1. 讀取 `ai-core/teacheros.yaml` — 教師身份、哲學、workspace_system
2. 讀取 `ai-core/acl.yaml` — 使用者身份與授權範圍
3. 讀取 `ai-core/AI_HANDOFF.md` — 技能系統與工作啟動流程

#### Step 2：確認工作上下文
4. 辨識使用者身份，從 acl.yaml 找到對應 workspace 路徑
5. 若是班級工作：從 workspace 內載入班級檔案
   ```
   workspaces/Working_Member/{Teacher_姓名}/projects/class-{code}/
     ├── project.yaml        ← 班級脈絡
     ├── students.yaml       ← 學生樣態
     ├── roster.yaml         ← 完整名單（敏感資料）
     └── {subject}/working/{subject}-session.yaml  ← 進度錨點
   ```
6. 若是新教師：載入 workspace 的 teacheros-personal.yaml，引導至 teacher-guide.md

#### Step 3：主動報告系統狀態
```
已載入系統。[教師名] [班級] 的 [科目] 課程目前在 Block [X] Step [Y]。
上次工作：[last_action]
下一步：[next_action]

說「進入備課」我會直接設計；說「查狀態」我會更新進度。要開始嗎？
```

### 系統驗證檢查表（v3 更新）

- [ ] `workspaces/Working_Member/` 存在
- [ ] `workspaces/Working_Member/Codeowner_David/` 含 class-9c（25 檔）、class-9d（7 檔）
- [ ] `workspaces/工作範例參考/projects/class-claude/` 含完整 Block 1-4 產出
- [ ] `ai-core/acl.yaml` 含 Teacher Claude 與 David（Codeowner）條目
- [ ] `ai-core/teacheros.yaml` 含 workspace_system 與 workspace_naming 區塊
- [ ] `ai-core/AI_HANDOFF.md` 含 save 與 pull-request 技能觸發語
- [ ] `ai-core/skills/save.md` 存在且 Step 1-4 完整
- [ ] `ai-core/skills/pull-request.md` 存在且 Step 1-5 完整
- [ ] `.claude/commands/save.md` 與 `.claude/commands/pull-request.md` 存在
- [ ] `setup/save.sh` 存在且可執行
- [ ] `setup/add-teacher.sh` 含 `create_teacher_branch()` 函式（Step 6）
- [ ] `setup/quick-start.sh` 含 Check 8（branch 自動偵測與切換）
- [ ] `setup/teacher-guide.md` 版本 >= 2.0，第十三節為 AI 口語指令版
- [ ] GitHub 已啟用 Branch Protection Rule（由 David 在 GitHub 設定）
- [ ] `projects/` 下不再有 class-9c、class-9d、class-claude（已搬遷）

---

## 九、已知待辦事項

### 優先度：高
1. **Pre-commit Hook 更新**：`setup/hooks/pre-commit` 尚未支援 Working_Member 路徑驗證
2. **差異化教學系統細項設計**：`projects/_di-framework/` Block 4 評量部分需進一步開發
3. **system-status.yaml 更新**：尚未反映 Workspace 架構、Working_Member 結構、Git 協作模型

### 優先度：中
4. **GitHub Branch Protection Rule 設定**：David 需在 GitHub repo Settings 中確認 main 分支已開啟保護
5. **Google Calendar 整合適配**：`setup/gcal-write.py` 需支援 workspace 內班級路徑
6. **其他科目範本**：`_class-template/` 目前只有英文骨架
7. **教案模板庫**：`workspaces/_template/templates/` 尚未建立

### 優先度：低
8. **Google Docs 輸出**：端對端流程尚未實裝
9. **AI_HANDOFF.md 定期更新**：建議每個工作週期後更新
10. **班級路徑 AI_HANDOFF.md 修正**：AI_HANDOFF.md 第二步的班級路徑仍指向舊的 `projects/class-{9c/8a/7a}/`，應更新為 workspace 路徑

---

## 十、接手者注意事項

### 禁止操作
- 勿刪除 `workspaces/工作範例參考/`（教學參考，所有教師依賴）
- 勿修改 `ai-core/acl.yaml` 中的 `protected_always` 路徑
- 勿在 `ai-core/` 中新增教師特定設定（應放各自 workspace）
- 勿直接編輯他人 workspace
- 勿移動或重命名 `Working_Member/`（所有路徑引用依賴此名稱）
- 勿直接合併 PR（只有 David 有權合併）

### 應該做的操作
- 新教師上線時使用 `add-teacher.sh`（不要手動建立）
- 重要輸出檔案歸檔至 `Engineer_Reference/` 並遵循版本命名規則
- 修改核心檔案後更新此交接文件
- 教師說「存檔」時讀取並執行 `ai-core/skills/save.md`
- 教師說「發 PR」時讀取並執行 `ai-core/skills/pull-request.md`

---

*本文件由 Claude (Cowork Mode) 生成於 2026-03-03*
*v3：新增 Git 協作模型（Collaborator + Branch）、save/pull-request 技能、branch 自動化、teacher-guide AI 口語指令重寫*
