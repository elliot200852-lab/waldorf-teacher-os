# TeacherOS — 歷次 Session 完成工作記錄

> 此文件為 AI_HANDOFF.md 的歷史紀錄卸載區。AI 平時不讀取。
> 需要查閱過去決策或技術細節時才開啟。

---

## 2026-02-27 第一次 session

| 項目 | 說明 |
|------|------|
| Reference 資料夾機制 | 建立 8 個 reference 資料夾（_di-framework、各班級、各科目層），邏輯寫入 project.yaml |
| 輸出格式協議 | 確認版本後 Markdown → Pandoc → .docx → Google Docs，已寫入 project.yaml |
| 產出品質標準 | 建立 strategy-output-quality-standard.md 與 strategy-analysis-quality-example.md |
| Block 2 模板建立 | english-di-block2.md 完整建立（2-A 單元教學流程 + 2-B 差異化任務與驗收機制） |
| Block 1 品質校準 | 教學目標條列式（兩句話如詩）、語言基本功列為哲學底線 |
| Block 1 範例 | block1-output-example-draft.md（9C 教學大綱完整範例） |
| Pandoc 安裝 | 系統已安裝 Pandoc 3.9 |
| v04 版本 | 打 tag 推上 GitHub |

---

## 2026-02-27 第二次 session

| 項目 | 說明 |
|------|------|
| Google Drive 自動輸出 | build.sh 建立，動態讀取 environment.env，路徑自動解析，AI 代跑無需教師輸入指令 |
| Google Drive 資料夾 | 建立 class-9c/8a/7a 各 english 子資料夾，已與本機同步 |
| 環境設定系統 | setup/ 資料夾建立：environment.env.example、setup-check.sh、environment.env（David 個人，gitignored） |
| 教師試用手冊 | teacher-guide.md 建立，含 GitHub clone、三種 AI 工具選項、TeacherOS 改寫說明 |
| 手冊 publish | 教師試用手冊已輸出為 .docx，存入 Google Drive TeacherOS 根目錄 |
| project.yaml 更新 | 輸出格式協議、reference 機制、environment 設定系統全部寫入 |

---

## 2026-02-28 第三次 session：系統盤點與狀態快照

| 項目 | 說明 |
|------|------|
| Context Review | 全資料夾 30+ 檔案完整審查，產出 `ai-core/reviews/context-review-20260228.md` |
| system-status.yaml | 建立精簡系統狀態快照（20 行），供 AI 開工前快速掃描 |
| AI_HANDOFF.md 更新 | 登錄新檔案、更新專案狀態表 |

---

## 2026-02-28 第四次 session：學生知識庫建構

| 項目 | 說明 |
|------|------|
| 架構重構 | 建立 `roster.yaml`（真名+ID，gitignored）、`students.yaml`（班級共用）、各科 `di-profile.yaml` |
| 學生知識庫協議 | 建立 `student-knowledge-protocol.md`（角色確認必問、讀寫路由表），登錄於 AI_HANDOFF |
| 9C DI 分類 | 完成 9C 全班 22 人英文課 DI 觀察（ABCD、優勢、細項、成績）輸入 |

---

## 2026-02-28 第五次 session：9C 英文教學大綱設計

| 項目 | 說明 |
|------|------|
| 108 課綱語言參考表 | `108-curriculum-language-reference.md` 存入 `_di-framework/content/`；寫入主控索引 |
| 9C 英文 reference 建立 | 存入兩份研究文件：差異化教學策略研究、Mango Street 小說教學研究報告 |
| 9C 英文教學大綱 v1 | 三軸架構（小說 + 語言工坊 + 108 課綱），雙路徑存檔 + Google Drive 輸出完成 |
| 評量比例定案 | 小說討論 20% + 創意寫作 20% + 詞彙溝通 25% + 文法閱讀 25% + 學習歷程 10% |
| Block 1 完成 | 9C 英文 Block 1 全部流程跑完，english-session.yaml 進度錨點更新 |

---

## 2026-02-28 第六次 session：TeacherOS 系統四區塊閉環完備

| 項目 | 說明 |
|------|------|
| 課前準備硬性阻擋 | 更新 teacher-guide.md 與 Block 1 模板，導入對話開頭主動詢問並阻擋無檔案狀態的機制 |
| Block 3 實作完成 | english-di-block3.md：非同步模糊比對與拆解能力，三維紀錄庫（學生/單元/反思），強制 [YYYY-MM-DD] 標籤 |
| Block 4 實作完成 | english-di-block4.md：結案合併單檔評量總檔架構，含 200 字全班歷程摘要及個別學生描述 |
| 檢索降載機制 | Block 2 前置讀取設定只讀最近三筆日期，避免資訊超載 |

---

## 2026-03-01 導師模組與 Google 行事曆連動

| 項目 | 說明 |
|------|------|
| 導師模組框架建立 | homeroom-template.md 定義 HM Block 1-4 工作流、學生日誌標籤分離機制 |
| 9C 導師基礎建設 | 建立 class-9c/homeroom/ 目錄、進度錨點 session.yaml 與 calendar.md |
| Google iCal 解析系統 | 建立支援 Google 私人/公開網址的 Python 擷取工具，行事曆快照更新機制 |
| SOP 協議登錄 | 在 AI_HANDOFF.md 與 student-knowledge-protocol.md 加入導師角色協議 |
| Block 1 寫作風格邊界 | 在 english-di-block1.md 新增規範：禁止道德型收尾句、禁止強調語堆疊、評量表不加詮釋句 |
| 9C 教學大綱 v2 | 套用新風格邊界，產出 v2，雙路徑存檔，已輸出 Google Drive |
| build.sh 中文化 | Google Drive 輸出全面中文化（資料夾 + 檔名），自動子資料夾分類 |

---

## 2026-03-01 Logo 排版與浮水印（由 Gemini 完成）

| 項目 | 說明 |
|------|------|
| Logo Inline 排版 | 捨棄 Table 佈局，改採 Inline Image；以 w:position (Half-points) 提昇文字基線，實現垂直置中 |
| 華德福水彩背景 | 產出淡色水彩渲染 JPG (waldorf-bg.jpg，20KB)，以 `<wp:anchor behindDoc="1">` 做全頁浮水印 |
| gcal-write.py | Google Calendar API OAuth2 寫入腳本，首次授權完成，token.json 已儲存 |
| build.sh 擴充 | 新增 homeroom 偵測、/tmp 暫存避免 Stale NFS，輸出前先刪舊檔再複製 |

---

## 2026-03-01 YAML 可讀性改善 + 系統 Review

| 項目 | 說明 |
|------|------|
| YAML 中文識別標頭 | 為所有 project.yaml 與 session.yaml 加入五行 # 註解識別區塊（不影響結構） |
| AI_HANDOFF.md 瘦身 | 從 420 行壓縮至 ~50 行；歷史紀錄移至本文件 |
| 系統全面 Review | 提出 9 項結構與 UX 問題，依優先順序逐項修正 |

---

## 2026-03-01 系統 8 項優化全部完成 + Demo HTML

| 項目 | 說明 |
|------|------|
| UX0：AI_HANDOFF.md 精簡 | 420 行→66 行（84% 削減）；只留：載入協議、開工報告格式、結束規則、參考表 |
| UX0：session-log.md 建立 | 歷史紀錄從 HANDOFF 移出，新建 ai-core/reviews/session-log.md（AI 平時不讀取） |
| UX0：system-status.yaml 維護協議 | 加入「讀取 on-demand / 寫入 every session-end」明文協議；內容校正至正確現況 |
| 結構1：build.sh Front Matter | 新增 `fm_value()` 函式讀取 Markdown Front Matter；解析順序：FM → 路徑推斷 → 報錯含操作說明 |
| 結構1：6 份內容檔加入 Front Matter | class-9c 英文（v1/v2）與導師通知（v1/v2）各兩路徑，共 6 份 .md 加入 YAML Header |
| 結構2：cross_module_notes | class-9c/project.yaml 新增 `cross_module_notes: active/resolved` 跨線協調結構；首筆：導師↔英文春季班親會 |
| UX1：voice_input_protocol | teacheros.yaml 新增語音輸入 5 條協議（模糊→推斷、最多追問一次等） |
| UX2：startup_report_template | teacheros.yaml 新增開工報告標準模板；session_start 步驟加入 cross_module_notes 掃描 |
| UX2：session_end steps | teacheros.yaml 新增 session_end 四步驟明文協議 |
| UX3：8A/7A dormant status | 兩班 project.yaml 加入 `status: dormant`，定義啟動觸發語與 AI 執行步驟 |
| UX3：teacher-guide.md 第十節 | 新增「新增班級或科目」完整 SOP（啟動休眠班、新班克隆、新增科目三情境） |
| UX4：current_week 欄位 | english-session.yaml 新增 `current_week: 0`，附 10 週單元換算對照表（comments） |
| Demo HTML | `publish/teacheros-demo.html`（153KB，自含）：4 分頁（英文老師/導師/主課程/架構師），waldorf-bg + logo 以 base64 嵌入，互動展開卡片 |
| generate-demo.py | `publish/generate-demo.py`：產生 demo HTML 的 Python 腳本，base64 資產嵌入邏輯 |
| Q&A：Session Protocol | 確認 Claude Code 可全自動執行 session-end；ChatGPT/Gemini/Antigravity 只能輸出 YAML 變更，需手動 apply 或由 Claude Code 收尾 |
