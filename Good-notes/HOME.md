---
aliases:
  - "首頁"
  - "TeacherOS 首頁"
  - "知識地圖"
---

# WaldorfTeacherOS — 全站檔案總覽

> 意義架構師的知識地圖入口｜所有檔案一覽

---

## 母文件（教育哲學根基）

| 檔案 | 說明 |
|------|------|
| [[AI 時代華德福教師的定位與價值]] | 我是誰、我為什麼在這裡 |
| [[華德福七至九年級學生生命樣態與課程的連結]] | 學生的靈魂在經歷什麼 |
| [[TeacherOS × 專案三層記憶系統指引手冊]] | 三層記憶系統操作指引 |
| [[TeacherOS 平台全貌 — 備課精神、技能系統與協作指引\|平台全貌指引]] | 備課精神、Skill 建立心法、加入架構的準備 |
## 平台指引（從這裡開始）

| 檔案 | 說明 |
|------|------|
| [[TeacherOS 平台全貌 — 備課精神、技能系統與協作指引\|平台全貌指引]] | 備課精神、Skill 建立心法、加入 TeacherOS 前該想清楚的事 |
| [[TeacherOS 平台全貌 — 備課精神、技能系統與協作指引（通用版）\|平台全貌指引（通用版）]] | 通用版，適合外部分享 |
| [[教師AI備課指南-從零建立你的第一個Skill]] | 實戰紀錄：從零建立第一個 Skill 的完整歷程 |

---

## 系統核心（ai-core/）

### 系統設定（YAML）

| 檔案 | 說明 |
|------|------|
| [[ai-core/teacheros.yaml\|teacheros.yaml]] | 系統路由中樞 — 載入順序、workspace 機制、session 協議 |
| [[ai-core/teacheros-foundation.yaml\|teacheros-foundation.yaml]] | 華德福教育共用根基 — 哲學、發展心理、課程原則 |
| [[ai-core/acl.yaml\|acl.yaml]] | 使用者權限控制 — Email 對應 workspace 與角色 |
| [[ai-core/system-status.yaml\|system-status.yaml]] | 系統狀態快照 |
| [[ai-core/agent-sync-spec.yaml\|agent-sync-spec.yaml]] | 多 AI Agent 同步規格 |

### AI 入口與流程

| 檔案 | 說明 |
|------|------|
| [[AI_HANDOFF]] | AI 入口文件（30 秒進入工作狀態） |
| [[ai-core/sync_check.py\|sync_check.py]] | Agent 同步檢查腳本 |

### Reference 知識模組（YAML）

| 檔案 | 說明 |
|------|------|
| [[ai-core/reference/pedagogy-framework.yaml\|pedagogy-framework.yaml]] | 華德福教育學框架 |
| [[ai-core/reference/subject-english.yaml\|subject-english.yaml]] | 英文科教學哲學與設計原則 |
| [[ai-core/reference/subject-history.yaml\|subject-history.yaml]] | 歷史科教學哲學與設計原則 |
| [[ai-core/reference/student-development.yaml\|student-development.yaml]] | 學生發展與班級經營框架 |

### Reference 操作文件

| 檔案 | 說明 |
|------|------|
| [[gws-cli-guide]] | Google Workspace CLI 使用指南 |
| [[overlay-contribution-guide]] | 科目覆蓋層貢獻指引 |

### 系統回顧紀錄

| 檔案 | 說明 |
|------|------|
| [[session-log]] | 歷次 session 完成紀錄 |
| [[architecture-review-2026-03-04]] | 架構回顧（2026-03-04） |
| [[context-review-20260228]] | 脈絡回顧（2026-02-28） |

---

## 技能系統（Skills）

### 技能目錄與索引

| 檔案 | 說明 |
|------|------|
| [[ai-core/skills/README\|技能總目錄 README]] | 所有技能一覽 |
| [[skills-manifest]] | 技能索引（觸發語 + 路徑對照） |

### 系統技能正本（ai-core/skills/）

| 技能 | 觸發語 | 說明 |
|------|--------|------|
| [[opening]] | 「開工」「早安」 | 新對話開場 |
| [[load]] | 「載入 9C english」 | 載入班級與科目脈絡 |
| [[status]] | 「現在在哪」 | 快速查詢進度 |
| [[syllabus]] | 「開始大綱」 | 學季教學大綱規劃 |
| [[lesson]] | 「進入備課」 | 課堂教學設計 |
| [[wrap-up]] | 「收工」「存檔」「收尾」 | 進度同步 + Obsidian 修正 + Git 存檔推送 |
| [[di-check]] | 「查 DI」 | 差異化合規核對 |
| [[ref]] | 「載入教學哲學」 | 按需載入 Reference |
| [[homeroom]] | 「導師業務」 | 班級經營與個案討論 |
| [[block-end]] | 「區塊結束」 | 主課程區塊反思 |
| [[rhythm]] | 「設計節奏」 | 課堂節奏設計 |
| [[student-note]] | 「記錄學生」 | 學生觀察記錄 |
| [[parent-letter]] | 「寫家長信」 | 家長信草稿 |
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
| [[obsidian-sync]] | 「補標籤」「更新索引」 | Obsidian 標籤與索引同步 |

---

## 差異化教學框架（_di-framework/）

### 框架設定

| 檔案 | 說明 |
|------|------|
| [[projects/_di-framework/project.yaml\|DI 框架 project.yaml]] | 差異化教學規則、產出協議、品質標準入口 |

### 操作文件

| 檔案 | 說明 |
|------|------|
| [[system-logic-map]] | 系統邏輯地圖（母文件） |
| [[di-classification-guide]] | DI 分類指引（A/B/C/D 學生矩陣） |
| [[student-knowledge-protocol]] | 學生知識協定 |
| [[english-di-template]] | 英文差異化模板 |
| [[homeroom-template]] | 導師課模板 |
| [[strategy-output-quality-standard]] | 策略產出品質標準 |
| [[108-curriculum-language-reference]] | 108 課綱語言參照 |

### 英文差異化區塊設計

| 檔案 | 說明 |
|------|------|
| [[english-di-block1]] | Block 1 — 學季整體規劃 |
| [[english-di-block2]] | Block 2 — 班級實際教學 |
| [[english-di-block3]] | Block 3 — 延伸與深化 |
| [[english-di-block4]] | Block 4 — 評量與反思 |

### 參考範例

| 檔案 | 說明 |
|------|------|
| [[block1-output-example-draft]] | Block 1 產出範例 |
| [[strategy-analysis-quality-example]] | 策略分析品質範例 |
| [[教師AI備課指南-從零建立你的第一個Skill]] | 新手技能建立指南 |

---

## 工程與開發者文件

### Engineer_Reference/

| 檔案 | 說明 |
|------|------|
| [[Engineer_Reference/CHANGELOG_v7_20260303.md\|CHANGELOG v7]] | 系統變更紀錄 |
| [[Engineer_Reference/TeacherOS-AI-交接文件_v1_20260303.md\|AI 交接文件 v1]] | 工程交接文件第一版 |
| [[Engineer_Reference/TeacherOS-AI-交接文件_v2_20260303.md\|AI 交接文件 v2]] | 工程交接文件第二版 |
| [[Engineer_Reference/TeacherOS-AI-交接文件_v3_20260303.md\|AI 交接文件 v3]] | 工程交接文件第三版 |
| [[Engineer_Reference/TeacherOS-工作範例展示_v1_20260303.html\|工作範例展示 HTML]] | 英文科工作範例展示頁 |
| [[Engineer_Reference/TeacherOS-測試報告-三合一_v1_20260303.docx\|測試報告 DOCX]] | 三合一測試報告 |

### .github/

| 檔案 | 說明 |
|------|------|
| [[.github/CODEOWNERS\|CODEOWNERS]] | GitHub 審核規則（David 必審） |

### .gitignore

| 檔案 | 說明 |
|------|------|
| [[.gitignore]] | Git 忽略規則 |

---

## 環境設定與腳本（setup/）

### 安裝與設定

| 檔案 | 說明 |
|------|------|
| [[setup/teacher-guide.md\|teacher-guide.md]] | 新教師環境設定指南 |
| [[setup/teacher-guide-v2.1.html\|teacher-guide-v2.1.html]] | 設定指南 HTML v2.1 |
| [[setup/teacher-guide-v2.2.html\|teacher-guide-v2.2.html]] | 設定指南 HTML v2.2 |
| [[setup/quick-start.sh\|quick-start.sh]] | 快速安裝腳本 |
| [[setup/setup-check.sh\|setup-check.sh]] | 環境檢查腳本 |
| [[setup/environment.env.example\|environment.env.example]] | 環境變數範本 |

### 教師管理

| 檔案 | 說明 |
|------|------|
| [[setup/add-teacher.sh\|add-teacher.sh]] | 新增教師腳本（建立 workspace + 寫入 ACL） |
| [[setup/install-hooks.sh\|install-hooks.sh]] | 安裝 Git hooks |
| [[setup/hooks/pre-commit\|hooks/pre-commit]] | Pre-commit hook（ACL 路徑檢查） |

### 工具腳本

| 檔案 | 說明 |
|------|------|
| [[setup/scripts/obsidian-check.py\|obsidian-check.py]] | Obsidian 標籤偵測腳本 |
| [[setup/save.sh\|save.sh]] | 存檔腳本 |
| [[setup/gcal-write.py\|gcal-write.py]] | Google Calendar 寫入工具 |
| [[setup/add-logo.py\|add-logo.py]] | Logo 加入工具 |

### 靜態資源

| 檔案 | 說明 |
|------|------|
| [[setup/assets/logo.png\|logo.png]] | TeacherOS Logo 原圖 |
| [[setup/assets/logo-ready.png\|logo-ready.png]] | Logo 已處理版 |
| [[setup/assets/waldorf-bg.jpg\|waldorf-bg.jpg]] | 華德福背景圖 |

---

## 輸出與發佈（publish/）

| 檔案 | 說明 |
|------|------|
| [[publish/build.sh\|build.sh]] | 主要發佈腳本（Markdown → DOCX → Google Drive） |
| [[publish/batch-docreview.py\|batch-docreview.py]] | 批次文件審閱工具 |
| [[publish/images/core_spirit.png\|core_spirit.png]] | 圖片：核心精神 |
| [[publish/images/di_matrix.png\|di_matrix.png]] | 圖片：差異化矩陣 |
| [[publish/images/di_steps.png\|di_steps.png]] | 圖片：差異化步驟 |
| [[publish/images/workflow.png\|workflow.png]] | 圖片：工作流程 |

---

## 教師工具下載區（Tool Download/）

### 總覽

| 檔案 | 說明 |
|------|------|
| [[Tool Download/README.md\|Tool Download README]] | 工具下載區說明 |

### 英文寫作訂正系統

| 檔案 | 說明 |
|------|------|
| [[Tool Download/英文寫作訂正系統/README.md\|寫作訂正系統 README]] | 系統說明 |
| [[Tool Download/英文寫作訂正系統/學生使用手冊-Writing-Checker.docx\|學生使用手冊 DOCX]] | 學生操作手冊 |
| [[Tool Download/英文寫作訂正系統/開啟系統.url\|開啟系統 URL]] | Windows 捷徑 |
| [[Tool Download/英文寫作訂正系統/開啟系統.webloc\|開啟系統 webloc]] | macOS 捷徑 |

### 音檔轉逐字稿（macOS）

| 檔案 | 說明 |
|------|------|
| [[Tool Download/音檔轉逐字稿-macOS/README.md\|逐字稿工具 README]] | 工具說明 |
| [[Tool Download/音檔轉逐字稿-macOS/.env.example\|.env.example]] | 環境變數範本 |
| [[Tool Download/音檔轉逐字稿-macOS/transcribe.py\|transcribe.py]] | Python 轉錄腳本 |
| [[Tool Download/音檔轉逐字稿-macOS/transcribe.sh\|transcribe.sh]] | Shell 轉錄腳本 |
| [[Tool Download/音檔轉逐字稿-macOS/setup.sh\|setup.sh]] | 安裝腳本 |
| [[Tool Download/音檔轉逐字稿-macOS/build_app.applescript\|build_app.applescript]] | macOS App 打包腳本 |

---

## 展示網站

### site/（Firebase 主站）

| 檔案 | 說明 |
|------|------|
| [[site/index.html\|index.html]] | 首頁 |
| [[site/architecture.html\|architecture.html]] | 系統架構頁 |
| [[site/david-live.html\|david-live.html]] | David 即時展示頁 |
| [[site/di-framework.html\|di-framework.html]] | 差異化教學框架頁 |
| [[site/evolution.html\|evolution.html]] | 系統演化頁 |
| [[site/skills.html\|skills.html]] | 技能系統頁 |
| [[site/workspace-demo.html\|workspace-demo.html]] | Workspace 展示頁 |
| [[site/teacher-guide-v2.2.html\|teacher-guide-v2.2.html]] | 教師指南頁 |
| [[site/style.css\|style.css]] | 樣式表 |
| [[site/script.js\|script.js]] | JavaScript |
| [[site/firebase.json\|firebase.json]] | Firebase 設定 |
| [[site/.firebaserc\|.firebaserc]] | Firebase 專案設定 |

### 網站展示/（備用展示站）

| 檔案 | 說明 |
|------|------|
| [[網站展示/public/index.html\|index.html]] | 公開首頁 |
| [[網站展示/TeacherOS_Infographic.html\|TeacherOS 資訊圖表]] | 系統資訊圖表 |
| [[網站展示/TeacherOS系統完整介紹.html\|系統完整介紹]] | 系統完整介紹頁 |
| [[網站展示/teacheros-demo.html\|teacheros-demo.html]] | Demo 展示頁 |
| [[網站展示/新手入門操作手冊拷貝.html\|新手入門操作手冊]] | 新手入門 |
| [[網站展示/英文科工作範例展示拷貝.html\|英文科工作範例]] | 英文科範例展示 |
| [[網站展示/TeacherOS-AI-交接文件-20260303.md\|AI 交接文件]] | 展示用交接文件 |
| [[網站展示/generate-demo.py\|generate-demo.py]] | Demo 生成腳本 |
| [[網站展示/firebase.json\|firebase.json]] | Firebase 設定 |
| [[網站展示/.firebaserc\|.firebaserc]] | Firebase 專案設定 |

---

## Git History 週記

| 檔案 | 說明 |
|------|------|
| [[Git History/git-history.md\|git-history 週記]] | Git 工作週記 |
| [[Git History/_pdf-config.md\|PDF 輸出設定]] | 週記 PDF 設定 |

---

## David 的工作空間

### 個人設定

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

9C 英文內容產出：

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/english/content/english-syllabus-v1-20260228.md\|英文大綱 v1（科目路徑）]] | 學季大綱第一版 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/english/content/english-syllabus-v2-20260301.md\|英文大綱 v2（科目路徑）]] | 學季大綱第二版 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/content/english/english-syllabus-v1-20260228.md\|英文大綱 v1（班級路徑）]] | 班級視角副本 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/content/english/english-syllabus-v2-20260301.md\|英文大綱 v2（班級路徑）]] | 班級視角副本 |
| [[9C-week5-1-v1-教師教案]] | 第五週第一節教案 |
| [[9C-week5-1-v1-學習單]] | 第五週第一節學習單 |
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/english/content/README.md\|英文 content README]] | 內容資料夾說明 |

9C 英文參考資料：

| 檔案 | 說明 |
|------|------|
| [[9C下學期英文差異化教學策略研究]] | DI 策略研究 |
| [[The house on Mango Street 小說教學研究報告範本]] | 小說教學研究 |

**9C 導師**

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/homeroom/session.yaml\|9C 導師進度錨點]] | 導師業務進度 |

9C 工作全貌筆記：

| 檔案 | 說明 |
|------|------|
| [[Good-notes/9C 班工作全貌 — 導師與英文教學\|9C 班工作全貌]] | 導師 + 英文教學的完整工作脈絡與方向 |

9C 導師內容產出：

| 檔案 | 說明 |
|------|------|
| [[行程總覽與規劃建議]] | 服務學習之旅規劃 |
| [[V1-可行性評估報告]] | 服務學習之旅 V1 可行性評估 |
| [[homeroom-notice-v1-20260301]] | 導師通知 v1 |
| [[homeroom-notice-v2-20260301]] | 導師通知 v2 |

9C 導師參考資料：

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/homeroom/reference/calendar\|9C 行事曆]] | 班級行事曆 |

**9C 農場實習**

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Codeowner_David/projects/class-9c/farm-internship/session.yaml\|9C 農場實習進度]] | 農場實習進度錨點 |

9C 農場實習內容產出：

| 檔案 | 說明 |
|------|------|
| [[week4-返校工作計畫]] | 第四週返校計畫 |
| [[week4-分享會流程與場次]] | 第四週分享會流程 |

9C 農場實習參考資料：

| 檔案 | 說明 |
|------|------|
| [[farm-internship-analysis-114]] | 114 學年農場實習分析報告 |

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

### 個人設定

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Teacher_郭耀新/teacheros-personal.yaml\|郭耀新個人身份層]] | 教學信念、工作偏好 |
| [[workspaces/Working_Member/Teacher_郭耀新/workspace.yaml\|郭耀新 workspace 狀態]] | Workspace 狀態 |
| [[workspaces/Working_Member/Teacher_郭耀新/manual\|郭耀新操作手冊]] | TeacherOS 快速參考 |
| [[workspaces/Working_Member/Teacher_郭耀新/README.md\|郭耀新 README]] | Workspace 說明 |

### 教學筆記

| 檔案 | 說明 |
|------|------|
| [[114學年教學計劃（9資訊-郭耀新）]] | 九年級資訊科技教學計畫 |
| [[114學年度冬、春學季 ─ 程式設計進階：微控制器與物聯網]] | G12 程式設計進階 |

### 個人技能

| 檔案 | 說明 |
|------|------|
| [[workspaces/Working_Member/Teacher_郭耀新/skills/EXAMPLE-recitation.md\|EXAMPLE-recitation]] | 個人技能範例 |
| [[workspaces/Working_Member/Teacher_郭耀新/skills/README.md\|技能 README]] | 個人技能說明 |

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

## 模板與範例

### 新教師模板（workspaces/_template/）

| 檔案 | 說明 |
|------|------|
| [[workspaces/_template/README.md\|模板 README]] | 模板使用說明 |
| [[workspaces/_template/teacheros-personal.yaml\|個人身份模板]] | 教師身份 YAML 範本 |
| [[workspaces/_template/workspace.yaml\|Workspace 狀態模板]] | 工作空間 YAML 範本 |
| [[workspaces/_template/skills/README.md\|技能 README 模板]] | 個人技能說明範本 |
| [[workspaces/_template/skills/EXAMPLE-recitation.md\|EXAMPLE-recitation 模板]] | 朗誦技能範例 |
| [[workspaces/_template/skills/EXAMPLE-subject-overlay.md\|EXAMPLE-subject-overlay 模板]] | 科目覆蓋層技能範例 |

新教師班級模板：

| 檔案 | 說明 |
|------|------|
| [[workspaces/_template/projects/_class-template/project.yaml\|班級 project.yaml 模板]] | 班級設定範本 |
| [[workspaces/_template/projects/_class-template/roster.yaml\|學生名冊模板]] | 名冊範本 |
| [[workspaces/_template/projects/_class-template/students.yaml\|學生 DI 分析模板]] | DI 分析範本 |
| [[workspaces/_template/projects/_class-template/english/di-profile.yaml\|英文 DI 設定模板]] | 英文差異化範本 |
| [[workspaces/_template/projects/_class-template/working/english-session.yaml\|英文 session 模板]] | 英文進度錨點範本 |

### 工作範例參考（Teacher Claude）

| 檔案 | 說明 |
|------|------|
| [[workspaces/工作範例參考/teacheros-personal.yaml\|Teacher Claude 身份]] | 範例教師身份 |
| [[workspaces/工作範例參考/workspace.yaml\|Teacher Claude workspace]] | 範例工作空間狀態 |
| [[workspaces/工作範例參考/projects/class-claude/project.yaml\|範例班級設定]] | 範例班級 |
| [[workspaces/工作範例參考/projects/class-claude/roster.yaml\|範例學生名冊]] | 範例名冊 |
| [[workspaces/工作範例參考/projects/class-claude/students.yaml\|範例學生 DI]] | 範例 DI 分析 |
| [[workspaces/工作範例參考/projects/class-claude/index.md\|範例班級索引]] | 班級總覽 |

範例英文課產出：

| 檔案 | 說明 |
|------|------|
| [[workspaces/工作範例參考/projects/class-claude/english/di-profile.yaml\|範例英文 DI 設定]] | 差異化設定 |
| [[workspaces/工作範例參考/projects/class-claude/working/english-session.yaml\|範例英文進度]] | 進度錨點 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/english-syllabus-v1-20260303.md\|範例英文大綱 v1]] | 學季大綱 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/english-unit-1-v1-20260303.md\|範例單元一]] | 單元一教學設計 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/english-units-2-4-v1-20260303.md\|範例單元二至四]] | 單元二至四教學設計 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/student-assessments-20260510.md\|範例學生評量]] | 學生評量結果 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/teacher-term-report-20260510.md\|範例學期報告]] | 教師學期報告 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/records/unit-logs.md\|範例單元紀錄]] | 教學單元紀錄 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/records/teacher-reflections.md\|範例教師反思]] | 教師反思紀錄 |
| [[workspaces/工作範例參考/projects/class-claude/english/content/records/student-logs/sample-logs.md\|範例學生紀錄]] | 學生學習紀錄 |

範例導師課產出：

| 檔案 | 說明 |
|------|------|
| [[workspaces/工作範例參考/projects/class-claude/homeroom/session.yaml\|範例導師進度]] | 導師進度錨點 |
| [[workspaces/工作範例參考/projects/class-claude/homeroom/content/season-plan.md\|範例學季計畫]] | 導師學季計畫 |
| [[workspaces/工作範例參考/projects/class-claude/homeroom/content/term-summary.md\|範例學期總結]] | 學期總結 |
| [[workspaces/工作範例參考/projects/class-claude/homeroom/content/comms/daily-observations-and-comms.md\|範例每日觀察]] | 每日觀察與溝通 |
| [[workspaces/工作範例參考/projects/class-claude/homeroom/content/activities/spring-activities.md\|範例春季活動]] | 春季班級活動 |

範例測試報告：

| 檔案 | 說明 |
|------|------|
| [[workspaces/工作範例參考/projects/class-claude/TeacherOS-測試報告-三合一.docx\|測試報告 DOCX]] | 三合一測試報告 |

---

## Claude Code 設定（.claude/）

### 設定檔

| 檔案 | 說明 |
|------|------|
| [[.claude/settings.json\|settings.json]] | Claude Code 全域設定 |
| [[.claude/settings.local.json\|settings.local.json]] | 本機設定（不上傳） |
| [[.claude/launch.json\|launch.json]] | Dev server 啟動設定 |
| [[.claude/scripts/session-init.py\|session-init.py]] | Session 初始化腳本 |

### Claude Code Skills

| 檔案 | 說明 |
|------|------|
| [[.claude/skills/subject-lesson-45/SKILL.md\|subject-lesson-45 SKILL]] | 45 分鐘課堂設計 Skill |
| [[.claude/skills/deploy/SKILL.md\|deploy SKILL]] | 部署 Skill |

### Claude Code Commands（薄層入口 → ai-core/skills/）

| 指令 | 指向技能 |
|------|---------|
| [[.claude/commands/opening.md\|/opening]] | opening |
| [[.claude/commands/load.md\|/load]] | load |
| [[.claude/commands/status.md\|/status]] | status |
| [[.claude/commands/syllabus.md\|/syllabus]] | syllabus |
| [[.claude/commands/lesson.md\|/lesson]] | lesson |
| [[.claude/commands/wrap-up.md\|/wrap-up]] | wrap-up（收工） |
| [[.claude/commands/di-check.md\|/di-check]] | di-check |
| [[.claude/commands/ref.md\|/ref]] | ref |
| [[.claude/commands/homeroom.md\|/homeroom]] | homeroom |
| [[.claude/commands/block-end.md\|/block-end]] | block-end |
| [[.claude/commands/rhythm.md\|/rhythm]] | rhythm |
| [[.claude/commands/student-note.md\|/student-note]] | student-note |
| [[.claude/commands/parent-letter.md\|/parent-letter]] | parent-letter |
| [[.claude/commands/pull-request.md\|/pull-request]] | pull-request |
| [[.claude/commands/sync-cowork.md\|/sync-cowork]] | sync-cowork |
| [[.claude/commands/drive.md\|/drive]] | drive |
| [[.claude/commands/calendar.md\|/calendar]] | calendar |
| [[.claude/commands/send-email.md\|/send-email]] | send-email |
| [[.claude/commands/sheets.md\|/sheets]] | sheets |
| [[.claude/commands/docs-edit.md\|/docs-edit]] | docs-edit |
| [[.claude/commands/git-history.md\|/git-history]] | git-history |
| [[.claude/commands/obsidian-sync.md\|/obsidian-sync]] | obsidian-sync |

---

## 根目錄散檔

| 檔案 | 說明 |
|------|------|
| [[INSTRUCTIONS.md\|INSTRUCTIONS]] | Cowork 用 Instructions（編譯產出） |
| [[INSTRUCTIONS.template.md\|INSTRUCTIONS 模板]] | Instructions 模板源檔 |
| [[draft-overlay-contribution-guide]] | 覆蓋層貢獻指引草稿 |
| [[git-history.skill]] | Git History Skill 定義檔 |
| [[subject-lesson-45.skill]] | 45 分鐘課堂設計 Skill 定義檔 |
| [[workspaces/README.md\|Workspaces README]] | Workspace 目錄說明 |
| [[Obsidian 快速上手指南]] | Obsidian 怎麼用 |

---

## 快速導航

- `Cmd + O` — 快速開啟任何筆記
- `Cmd + Shift + G` — 全域圖譜
- `Cmd + P` → 輸入指令 — 命令面板
