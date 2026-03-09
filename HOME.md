# WaldorfTeacherOS — 首頁

> 意義架構師的知識地圖入口

---

## 母文件（教育哲學根基）

- [[AI 時代華德福教師的定位與價值]] — 我是誰、我為什麼在這裡
- [[華德福七至九年級學生生命樣態與課程的連結]] — 學生的靈魂在經歷什麼
- [[TeacherOS × 專案三層記憶系統指引手冊]] — 三層記憶系統操作指引

---

## 系統核心（ai-core）

### 系統設定（YAML）

| 檔案 | 說明 |
|------|------|
| [[teacheros.yaml]] | 系統路由中樞 — 載入順序、workspace 機制、session 協議 |
| [[teacheros-foundation.yaml]] | 華德福教育共用根基 — 教育哲學、發展心理、課程原則 |
| [[acl.yaml]] | 使用者權限控制 — Email 對應 workspace 路徑與角色 |
| [[system-status.yaml]] | 系統狀態快照 |
| [[agent-sync-spec.yaml]] | 多 AI Agent 同步規格 |

### AI 入口與流程

- [[AI_HANDOFF]] — AI 入口文件（30 秒進入工作狀態）

### Reference 知識模組（YAML）

| 檔案 | 說明 |
|------|------|
| [[pedagogy-framework.yaml]] | 華德福教育學框架 |
| [[subject-english.yaml]] | 英文科教學哲學與設計原則 |
| [[subject-history.yaml]] | 歷史科教學哲學與設計原則 |
| [[student-development.yaml]] | 學生發展與班級經營框架 |

### Reference 操作文件

- [[gws-cli-guide]] — Google Workspace CLI 使用指南
- [[overlay-contribution-guide]] — 科目覆蓋層貢獻指引

### 系統回顧紀錄

- [[session-log]] — 歷次 session 完成紀錄
- [[architecture-review-2026-03-04]] — 架構回顧
- [[context-review-20260228]] — 脈絡回顧

---

## 技能系統（Skills）

- [[ai-core/skills/README\|技能總目錄]] — 所有技能一覽
- [[skills-manifest]] — 技能索引（觸發語 + 路徑對照）

| 技能 | 觸發語 | 說明 |
|------|--------|------|
| [[opening]] | 「開工」「早安」 | 新對話開場 |
| [[load]] | 「載入 9C english」 | 載入班級與科目脈絡 |
| [[status]] | 「現在在哪」 | 快速查詢進度 |
| [[syllabus]] | 「開始大綱」 | 學季教學大綱規劃 |
| [[lesson]] | 「進入備課」 | 課堂教學設計 |
| [[session-end]] | 「收尾」 | 對話結束同步狀態 |
| [[di-check]] | 「查 DI」 | 差異化合規核對 |
| [[ref]] | 「載入教學哲學」 | 按需載入 Reference |
| [[homeroom]] | 「導師業務」 | 班級經營與個案討論 |
| [[block-end]] | 「區塊結束」 | 主課程區塊反思 |
| [[rhythm]] | 「設計節奏」 | 課堂節奏設計 |
| [[student-note]] | 「記錄學生」 | 學生觀察記錄 |
| [[parent-letter]] | 「寫家長信」 | 家長信草稿 |
| [[save]] | 「存檔」 | Git commit + push |
| [[pull-request]] | 「發 PR」 | 合併申請 |
| [[sync-cowork]] | 「同步 Cowork」 | 編譯 instructions |
| [[drive]] | 「上傳到雲端」 | Google Drive 同步 |
| [[calendar]] | 「查行事曆」 | Google Calendar 操作 |
| [[send-email]] | 「寄信」 | Gmail 寄送 |
| [[sheets]] | 「開試算表」 | Google Sheets 操作 |
| [[docs-edit]] | 「編輯文件」 | Google Docs 編輯 |
| [[subject-lesson-45]] | 「設計一堂課」 | 45 分鐘單堂課設計引擎 |
| [[english-45]] | 「英文課設計」 | 英文科覆蓋層 |
| [[git-history]] | 「更新週記」 | Git History 週記管理 |
| [[sync-agents]] | 「同步 Agent」 | 多 AI Agent 同步 |

---

## 差異化教學框架（_di-framework）

### 框架設定（YAML）

| 檔案 | 說明 |
|------|------|
| [[projects/_di-framework/project.yaml\|DI 框架 project.yaml]] | 差異化教學規則、產出協議、品質標準入口 |

### 操作文件

- [[di-classification-guide]] — DI 分類指引（A/B/C/D 學生矩陣）
- [[system-logic-map]] — 系統邏輯地圖
- [[student-knowledge-protocol]] — 學生知識協定
- [[english-di-template]] — 英文差異化模板
- [[homeroom-template]] — 導師課模板
- [[strategy-output-quality-standard]] — 策略產出品質標準
- [[108-curriculum-language-reference]] — 108 課綱語言參照

### 英文差異化區塊設計

- [[english-di-block1]] — Block 1
- [[english-di-block2]] — Block 2
- [[english-di-block3]] — Block 3
- [[english-di-block4]] — Block 4

### 參考範例

- [[block1-output-example-draft]] — Block 1 產出範例
- [[strategy-analysis-quality-example]] — 策略分析品質範例
- [[教師AI備課指南-從零建立你的第一個Skill]] — 新手技能建立指南

---

## David 的工作空間

### 個人設定（YAML）

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/teacheros-personal.yaml\|David 個人身份層]] | 教學信念、工作偏好、AI 互動風格 |
| [[workspaces/Working_Member/Codeowner_David/workspace.yaml\|David workspace 狀態]] | Workspace 狀態追蹤 |

### 9C 班級

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/project.yaml\|9C 班級設定]] | 班級脈絡、科目清單、當前焦點 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/roster.yaml\|9C 學生名冊]] | 學生名單 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/students.yaml\|9C 學生 DI 分析]] | 學生能力 x 動機矩陣 |

**9C 英文**

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/english/session.yaml\|9C 英文進度錨點]] | 目前 Block/Step、下一步行動 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/english/di-profile.yaml\|9C 英文 DI 設定]] | 英文課差異化教學設定 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/english/lesson.yaml\|9C 英文教案]] | 課堂教案紀錄 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/english/assessment.yaml\|9C 英文評量]] | 評量設計 |
| [[english-syllabus-v2-20260301]] | 英文學季大綱 v2 |
| [[9C-week5-1-v1-教師教案]] | 第五週第一節教案 |
| [[9C-week5-1-v1-學習單]] | 第五週第一節學習單 |
| [[9C下學期英文差異化教學策略研究]] | DI 策略研究 |
| [[The house on Mango Street 小說教學研究報告範本]] | 小說教學研究 |

**9C 導師**

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/homeroom/session.yaml\|9C 導師進度錨點]] | 導師業務進度 |
| [[行程總覽與規劃建議]] | 服務學習之旅規劃 |
| [[homeroom-notice-v2-20260301]] | 導師通知 v2 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/homeroom/reference/calendar\|9C 行事曆]] | 班級行事曆 |

**9C 農場實習**

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/farm-internship/session.yaml\|9C 農場實習進度]] | 農場實習進度錨點 |
| [[farm-internship-analysis-114]] | 農場實習分析報告 |
| [[week4-返校工作計畫]] | 第四週返校計畫 |
| [[week4-分享會流程與場次]] | 第四週分享會流程 |

**9C 主課程（待定）**

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/ml-undecided/di-profile.yaml\|9C 主課程 DI 設定]] | 差異化設定 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/ml-undecided/lesson.yaml\|9C 主課程教案]] | 教案紀錄 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/ml-undecided/assessment.yaml\|9C 主課程評量]] | 評量設計 |

### 9D 班級

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9d/project.yaml\|9D 班級設定]] | 班級脈絡、科目清單 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9d/roster.yaml\|9D 學生名冊]] | 學生名單 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9d/students.yaml\|9D 學生 DI 分析]] | 學生能力 x 動機矩陣 |

**9D 台灣文學主課程**

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9d/ml-taiwan-literature/session.yaml\|9D 台灣文學進度錨點]] | 目前 Block/Step |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9d/ml-taiwan-literature/di-profile.yaml\|9D 台灣文學 DI 設定]] | 差異化設定 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9d/ml-taiwan-literature/lesson.yaml\|9D 台灣文學教案]] | 教案紀錄 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9d/ml-taiwan-literature/assessment.yaml\|9D 台灣文學評量]] | 評量設計 |

---

## 郭耀新老師的工作空間

### 個人設定（YAML）

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Teacher_郭耀新/teacheros-personal.yaml\|郭耀新個人身份層]] | 教學信念、工作偏好 |
| [[workspaces/Working_Member/Teacher_郭耀新/workspace.yaml\|郭耀新 workspace 狀態]] | Workspace 狀態 |

- [[workspaces/Working_Member/Teacher_郭耀新/manual\|郭耀新操作手冊]] — TeacherOS 快速參考

### 教學筆記

- [[114學年教學計劃（9資訊-郭耀新）]] — 九年級資訊科技教學計畫
- [[114學年度冬、春學季 ─ 程式設計進階：微控制器與物聯網]] — G12 程式設計進階

### 9A 班級（資訊科技）

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9a/project.yaml\|9A 班級設定]] | 班級脈絡與科目清單 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9a/roster.yaml\|9A 學生名冊]] | 學生名單 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9a/students.yaml\|9A 學生 DI 分析]] | 學生能力 x 動機矩陣 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9a/information_technology/di-profile.yaml\|9A 資訊科技 DI 設定]] | 差異化設定 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9a/working/information_technology-session.yaml\|9A 資訊科技進度錨點]] | 目前 Block/Step |

### 9B 班級（資訊科技）

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9b/project.yaml\|9B 班級設定]] | 班級脈絡與科目清單 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9b/roster.yaml\|9B 學生名冊]] | 學生名單 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9b/students.yaml\|9B 學生 DI 分析]] | 學生能力 x 動機矩陣 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9b/information_technology/di-profile.yaml\|9B 資訊科技 DI 設定]] | 差異化設定 |
| [[workspaces/Working_Member/Teacher_郭耀新/projects/class-9b/working/information_technology-session.yaml\|9B 資訊科技進度錨點]] | 目前 Block/Step |

---

## 快速導航

- [[Obsidian 快速上手指南]] — Obsidian 怎麼用
- [[setup/teacher-guide\|新教師環境設定指南]] — 新老師如何加入
- `Cmd + O` — 快速開啟任何筆記
- `Cmd + Shift + G` — 全域圖譜
