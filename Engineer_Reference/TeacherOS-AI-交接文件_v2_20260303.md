---
aliases:
  - "AI 交接文件 v2"
---

# TeacherOS AI 交接文件（v2）

> 日期：2026-03-03
> 上一次工作者：Claude (Cowork Mode)
> 版本：v2（取代 v1，反映第二輪架構重組）
> 目的：記錄測試後的所有架構修改，供下一個 AI 工作階段無縫接手

---

## 一、本次工作摘要

本次對 TeacherOS 進行了兩輪完整的架構重組。

**第一輪**：以「Teacher Claude」身份模擬八年級英文教師，完成 Block 1-4 全流程測試，並根據測試結果建立 Workspace 機制、修正七大架構問題。

**第二輪**：標準化 Workspace 命名規則、建立 Working_Member 容器層、搬遷 David 的班級資料、建立 Engineer_Reference 版本化歸檔。

兩輪重組後的系統核心變更：

1. 建立 Workspace 三層架構（共享參考 → 範本複製 → 老師創作）
2. 統一 Workspace 命名規則：`{Role}_{RealName}`
3. 建立 `workspaces/Working_Member/` 作為所有活躍教師的上層容器
4. 搬遷 David 的 class-9c、class-9d 至 `Codeowner_David` workspace
5. 建立 `Engineer_Reference/` 版本化歸檔資料夾
6. 重構雙路徑為單一標準路徑 + index.md
7. 新增安裝腳本（quick-start.sh）與認證腳本（add-teacher.sh）
8. 完善 DI 分類工具與 Block 2 三種詳細度
9. 重寫 Teacher Guide 2.0
10. 更新所有核心設定檔路徑引用

---

## 二、目前的資料夾結構（權威版）

```
WaldorfTeacherOS-Repo/
│
├── ai-core/                              ← 系統核心（只有 David 修改）
│   ├── teacheros.yaml                    ← 教師身份、哲學、workspace_system
│   ├── acl.yaml                          ← 權限控制（角色、路徑、命名規則）
│   ├── AI_HANDOFF.md                     ← AI 技能系統與工作啟動流程
│   ├── system-status.yaml                ← 系統現況快照
│   └── skills/                           ← 技能正本
│       └── ...
│
├── projects/                             ← 共用教學框架（班級資料已移至 workspace）
│   ├── _di-framework/                    ← 差異化教學共用框架
│   │   ├── project.yaml
│   │   └── content/
│   │       ├── di-classification-guide.md
│   │       └── english-di-block2.md
│   └── _class-template/                  ← 空白班級範本（由 add-teacher.sh 複製）
│
├── workspaces/                           ← 所有教師的工作空間
│   ├── README.md                         ← Workspace 系統說明
│   ├── _template/                        ← 新老師範本
│   │   ├── README.md
│   │   ├── workspace.yaml
│   │   ├── teacheros-personal.yaml
│   │   ├── philosophy.yaml
│   │   └── projects/_class-template/
│   │
│   ├── 工作範例參考/                      ← Teacher Claude 的完整 Block 1-4 範例（唯讀）
│   │   ├── teacheros-personal.yaml
│   │   ├── workspace.yaml
│   │   └── projects/class-claude/
│   │       ├── project.yaml
│   │       ├── roster.yaml
│   │       ├── students.yaml
│   │       ├── english/
│   │       │   ├── di-profile.yaml
│   │       │   └── content/              ← 11 個教學產出檔案
│   │       └── working/english-session.yaml
│   │
│   └── Working_Member/                   ← 所有活躍教師的工作空間
│       └── Codeowner_David/              ← David 的工作空間
│           ├── teacheros-personal.yaml   ← David 原始的 teacheros.yaml 完整副本
│           ├── workspace.yaml            ← 班級清單：class-9c, class-9d
│           └── projects/
│               ├── class-9c/             ← 九年級英文+導師課（25 個檔案）
│               │   ├── project.yaml
│               │   ├── roster.yaml       ← 124 行完整學生名單
│               │   ├── students.yaml
│               │   └── ...
│               └── class-9d/             ← 九年級台灣文學主課程（7 個檔案）
│                   ├── project.yaml
│                   ├── roster.yaml
│                   └── ...
│
├── Engineer_Reference/                   ← 版本化歸檔（命名格式：{name}_v{N}_{YYYYMMDD}）
│   ├── TeacherOS-測試報告-三合一_v1_20260303.docx
│   ├── TeacherOS-AI-交接文件_v1_20260303.md
│   ├── TeacherOS-AI-交接文件_v2_20260303.md  ← 本文件
│   └── TeacherOS-工作範例展示_v1_20260303.html
│
├── setup/                                ← 設定工具
│   ├── quick-start.sh                    ← 教師一鍵安裝腳本
│   ├── add-teacher.sh                    ← 管理員建立教師 workspace 腳本
│   ├── teacher-guide.md                  ← 教師使用手冊 v2.0
│   ├── install-hooks.sh
│   ├── environment.env.example
│   └── setup-check.sh
│
├── publish/
│   └── build.sh
│
└── .github/
    └── CODEOWNERS
```

---

## 三、Workspace 命名規則（v2 新增）

### 規則

| 角色 | 命名格式 | 範例 | 存放位置 |
|------|----------|------|----------|
| 系統管理員 | `Codeowner_{Name}` | `Codeowner_David` | `workspaces/Working_Member/` |
| 一般教師 | `Teacher_{姓名}` | `Teacher_林信宏` | `workspaces/Working_Member/` |
| 系統範例 | 特殊命名 | `工作範例參考` | `workspaces/`（不在 Working_Member 下） |
| 範本 | 固定名 | `_template` | `workspaces/` |

### 設計理由

- 中文真名讓教師直覺識別自己的資料夾
- `{Role}_` 前綴在排序時自動分群
- `Working_Member/` 容器層隔離活躍 workspace 與系統層級資料夾

---

## 四、第二輪架構變動清單

### 變動 1：建立 Engineer_Reference 歸檔

**目的**：所有重要輸出文件（報告、交接文件、展示檔）的版本化歸檔，不散落在 workspace 中。

**命名規則**：`{文件名稱}_v{版本號}_{YYYYMMDD}.{副檔名}`

**已歸檔檔案**：
- `TeacherOS-測試報告-三合一_v1_20260303.docx`
- `TeacherOS-AI-交接文件_v1_20260303.md`
- `TeacherOS-AI-交接文件_v2_20260303.md`
- `TeacherOS-工作範例展示_v1_20260303.html`

### 變動 2：建立 Working_Member 容器

**目的**：所有活躍教師 workspace 統一放在 `workspaces/Working_Member/` 下，與 `_template/` 和 `工作範例參考/` 在資料夾層級上分開。

### 變動 3：Workspace 命名標準化

**舊命名**：`david-teacher`（已刪除）
**新命名**：`Codeowner_David`

**acl.yaml 模板更新**：新教師格式改為 `workspaces/Working_Member/Teacher_{教師姓名}/`

### 變動 4：David 班級資料搬遷

**搬遷來源與目標**：

| 來源 | 目標 | 檔案數 |
|------|------|--------|
| `projects/class-9c/` | `workspaces/Working_Member/Codeowner_David/projects/class-9c/` | 25 |
| `projects/class-9d/` | `workspaces/Working_Member/Codeowner_David/projects/class-9d/` | 7 |

**驗證方式**：
- `diff -r` 比對零差異
- roster.yaml 行數驗證（class-9c: 124 行, class-9d: 9 行）
- 複製完成後才刪除原始路徑

**David 的 teacheros-personal.yaml**：
- 直接複製 `ai-core/teacheros.yaml`（351 行，David 的原始設定，未做任何修改）

### 變動 5：add-teacher.sh 路徑更新

**修改內容**：
- Workspace 建立路徑：`workspaces/$TEACHER_ID` → `workspaces/Working_Member/$TEACHER_ID`
- 命名建議：自動生成 `Teacher_{姓名}` 格式
- ACL 條目路徑：同步更新為 `workspaces/Working_Member/` 前綴
- 自動確保 `Working_Member/` 目錄存在

### 變動 6：所有文件路徑同步更新

以下檔案的路徑引用已更新為新結構：

| 檔案 | 更新內容 |
|------|----------|
| `ai-core/acl.yaml` | David 條目改為 `Codeowner_David`，模板格式改為 `Teacher_{姓名}`，新增命名規則說明 |
| `ai-core/teacheros.yaml` | workspace_system 新增 workspace_naming 區塊，onboarding step_3 路徑更新 |
| `setup/teacher-guide.md` | 資料夾結構圖更新（Working_Member/、Codeowner_David），projects/ 說明簡化 |
| `workspaces/README.md` | 全面重寫，反映命名規則、Working_Member 結構、三層模型 |
| `workspaces/_template/README.md` | 三層模型路徑更新，快速開始改為 add-teacher.sh 自動建立，結構圖更新 |

---

## 五、已刪除的檔案與路徑

| 已刪除項目 | 原因 | 資料去向 |
|-----------|------|----------|
| `projects/class-9c/` | 搬遷至 David workspace | `Working_Member/Codeowner_David/projects/class-9c/` |
| `projects/class-9d/` | 搬遷至 David workspace | `Working_Member/Codeowner_David/projects/class-9d/` |
| `workspaces/david-teacher/` | 命名標準化替換 | `Working_Member/Codeowner_David/` |
| `projects/class-claude/` | 第一輪搬遷 | `workspaces/工作範例參考/projects/class-claude/` |

---

## 六、接手指引

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

### 系統驗證檢查表

- [ ] `workspaces/Working_Member/` 存在
- [ ] `workspaces/Working_Member/Codeowner_David/` 含 class-9c（25 檔）、class-9d（7 檔）
- [ ] `workspaces/工作範例參考/projects/class-claude/` 含完整 Block 1-4 產出
- [ ] `ai-core/acl.yaml` 含 Teacher Claude 與 David（Codeowner）條目，路徑指向 Working_Member/
- [ ] `ai-core/teacheros.yaml` 含 workspace_system 與 workspace_naming 區塊
- [ ] `setup/teacher-guide.md` 版本 >= 2.0，資料夾結構圖為最新
- [ ] `setup/add-teacher.sh` 路徑指向 `workspaces/Working_Member/`
- [ ] `Engineer_Reference/` 含版本化歸檔檔案
- [ ] `projects/` 下不再有 class-9c、class-9d、class-claude（已搬遷）
- [ ] `workspaces/david-teacher/` 不存在（已替換為 Codeowner_David）

---

## 七、已知待辦事項

### 優先度：高
1. **Pre-commit Hook 更新**：`setup/hooks/pre-commit` 尚未支援 Working_Member 路徑驗證
2. **差異化教學系統細項設計**：`projects/_di-framework/` Block 4 評量部分需進一步開發
3. **system-status.yaml 更新**：尚未反映 Workspace 架構與 Working_Member 結構

### 優先度：中
4. **Google Calendar 整合適配**：`setup/gcal-write.py` 需支援 workspace 內班級路徑
5. **其他科目範本**：`_class-template/` 目前只有英文骨架，需添加人文、歷史等
6. **教案模板庫**：`workspaces/_template/templates/` 尚未建立

### 優先度：低
7. **Google Docs 輸出**：端對端流程尚未實裝
8. **AI_HANDOFF.md 定期更新**：建議每個工作週期後更新

---

## 八、重要設計決策

### 為什麼用 Working_Member 容器？
活躍教師 workspace 與系統層級資料夾（_template、工作範例參考）在層級上分開，避免資料夾清單混亂。未來教師人數增加時，Working_Member 作為統一的管理入口。

### 為什麼用中文真名命名？
華德福學校社群規模小，教師互相熟悉，中文真名最直覺。`{Role}_` 前綴提供排序與分群功能。

### 為什麼班級資料搬進 workspace？
原設計班級在 `projects/` 根層級，但這意味著多位教師共用同一路徑空間。搬入 workspace 後，每位教師的班級資料完全隔離，權限管理更清晰。

### 為什麼保留 projects/ 資料夾？
`projects/` 現在只放共用框架（`_di-framework/`、`_class-template/`），作為「共享參考庫」的一部分，所有教師可讀但不修改。

---

## 九、接手者注意事項

### 禁止操作
- 勿刪除 `workspaces/工作範例參考/`（教學參考，所有教師依賴）
- 勿修改 `ai-core/acl.yaml` 中的 `protected_always` 路徑
- 勿在 `ai-core/` 中新增教師特定設定（應放各自 workspace）
- 勿直接編輯他人 workspace
- 勿移動或重命名 `Working_Member/`（所有路徑引用依賴此名稱）

### 應該做的操作
- 定期備份 `ai-core/` 核心檔案
- 新教師上線時使用 `add-teacher.sh`（不要手動建立）
- 重要輸出檔案歸檔至 `Engineer_Reference/` 並遵循版本命名規則
- 修改核心檔案後更新此交接文件

---

*本文件由 Claude (Cowork Mode) 生成於 2026-03-03*
*v2：反映 Working_Member 容器、命名標準化、班級搬遷等第二輪架構變動*
