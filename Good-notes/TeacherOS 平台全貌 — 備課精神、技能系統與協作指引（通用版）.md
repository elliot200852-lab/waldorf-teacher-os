---
aliases:
  - "平台全貌指引（通用版）"
---

# TeacherOS 平台全貌 — 備課精神、技能系統與協作指引

> 這份筆記是整個 TeacherOS 的「為什麼」與「怎麼做」。
> 技術架構看 [全站檔案總覽](../HOME.md)，哲學根基看 [AI 時代華德福教師的定位與價值](ai-core/AI%20時代華德福教師的定位與價值.md)。
> 這裡談的是：用這套系統備課的精神、建立 Skill 的實戰心法、以及加入這個架構工作前該想清楚的事。

---
## 一、備課的核心精神

### 教師是意義架構師，不是內容搬運工

華德福教師的備課不是「找素材填進時間表」，而是回答一個問題：
**這堂課如何回應學生此刻的內在發展需求？**

這個問題的答案藏在三層結構裡：

| 層次 | 問的問題 | 對應檔案 |
|------|---------|---------|
| 哲學層 | 人是什麼？教育為了什麼？ | [teacheros-foundation.yaml](ai-core/teacheros-foundation.yaml) |
| 發展層 | 這個年齡的學生正在經歷什麼？ | [pedagogy-framework.yaml](ai-core/reference/pedagogy-framework.yaml) |
| 科目層 | 這個學科如何成為心靈的解藥？ | [subject-english.yaml](ai-core/reference/subject-english.yaml)、[subject-history.yaml](ai-core/reference/subject-history.yaml) |

> **核心原則**
> 每堂課設計完成後，自問三件事：
> 1. **頭**（Head）——學生的思考力被挑戰了嗎？
> 2. **心**（Heart）——學生的情感被觸動了嗎？
> 3. **手**（Hands）——學生的身體有參與嗎？

### 差異化不是選項，是預設

每一份課程設計必須同時滿足兩個軸線：

**軸一：學習優勢**（語言型 / 圖像型 / 動作型 / 藝術型）
— 每堂課至少涵蓋 2-3 種入口。

**軸二：能力 x 動機矩陣**（A / B / C / D）
— A 學生需要延伸挑戰，D 學生需要安全的起步點。

完整框架見 [DI 框架 project.yaml](projects/_di-framework/project.yaml)。
品質標準（包含五條自檢規則：心理素描開頭、消除抽象標籤、描述課堂畫面、結合具體內容、教師可直接拿走用）完整規格見 [策略產出品質標準](projects/_di-framework/content/strategy-output-quality-standard.md)。


### 現象學式學習：體驗先於概念

不預先給結論。引入新概念的順序永遠是：
**體驗 → 觀察 → 討論 → 概念化**

設計時刻意保留「生成性負載」——任務含足夠的模糊性，迫使學生親自觀察、推論與掙扎。AI 設計的教材必須在「支持」與「留白」之間取得平衡。

---
## 二、備課的實戰技巧

### 跟 AI 對話的五個原則

這些原則來自實際建立 Skill 的歷程，完整實戰紀錄見 [教師AI備課指南-從零建立你的第一個Skill](projects/_di-framework/reference/教師AI備課指南-從零建立你的第一個Skill.md)。

**原則一：先給方向，不給細節**
好的起手式：「幫我設計一堂九年級英文課，主題是 moral dilemma。」
壞的起手式：把所有細節全部塞進第一句話。讓 AI 先提方案，你再回饋。

**原則二：回饋要具體**
「書寫部分太多，入門層改為圈選和填空」比「這個不太好」有用一百倍。
你給 AI 的資訊越具體，修正就越精準。

**原則三：質疑 AI 的前提**
AI 聲稱的「學術共識」不一定正確。你要把進教室的東西，你自己先確認過。

**原則四：把多個需求疊在一起**
「差異化 + 文法整合」一句話同時解決兩個問題。這需要你對教學的全局觀。

**原則五：退後一步看系統**
不只修細節，還要問：「整個流程缺了什麼？」David 就是這樣發現 Skill 需要第四階段（產出）的。

### 45 分鐘課堂的節奏公式
吸氣（暖身 5-7 分鐘）→ 深呼吸（核心活動 30 分鐘）→ 呼氣（收尾 5-8 分鐘）

口頭活動是主體，書寫是輔助。入門層只做圈選填空，挑戰層限 1-2 句。
每堂課必須有 follow-up 小任務（不像作業的作業），讓學生帶著餘韻離開。

技能正本見 [subject-lesson-45](ai-core/skills/subject-lesson-45.md)，英文科覆蓋層見 [english-45](ai-core/skills/english-45.md)。

---
## 三、Skill 系統的 Know-How

### Skill 是什麼？

Skill 是一份你寫好的「操作手冊」。AI 每次接到任務時先讀這份手冊，按照你定義的流程和標準工作。你不需要每次重新交代——**你只需要給主題。**

技能目錄見 [技能總目錄 README](ai-core/skills/README.md)。
觸發語對照見 [skills-manifest](ai-core/skills/skills-manifest.md)。

### 系統技能 vs 個人技能

| 類型 | 路徑 | 誰能改 | 範例 |
|------|------|--------|------|
| 系統技能 | `ai-core/skills/` | 只有管理員 | [opening](ai-core/skills/opening.md)、[lesson](ai-core/skills/lesson.md)、[session-end](ai-core/skills/session-end.md) |
| 個人技能 | `{workspace}/skills/` | 教師自己 | 朗誦練習、科目覆蓋層 |

個人技能與系統技能同名時，在你自己的 session 中自動使用個人版本。
個人技能範本見 `workspaces/_template/skills/`。

### 引擎 + 覆蓋層架構（Engine + Overlay）

`subject-lesson-45` 是通用設計引擎，定義五階段工作流。各科目可建立覆蓋層（overlay），補充科目專屬的原則與規格。

你說「設計一堂九年級英文課」
↓
引擎載入 → subject-lesson-45.md（通用五階段流程）
↓
Step 0 自動載入覆蓋層 → english-45.md（英文科專屬原則）
↓
四階段執行：研究 → 設計（暫停確認）→ 審核 → 產出
↓
輸出：教師教案.md + 學生學習單.md

建立新覆蓋層的範本見 [EXAMPLE-subject-overlay](workspaces/_template/skills/EXAMPLE-subject-overlay.md)。

### 建立 Skill 的實戰步驟

> **提示：Skill 是「長」出來的，不是「寫」出來的**
> 你不可能一次寫出完美的 Skill。先跑一次、發現問題、修正、再跑一次。

1. **識別你反覆在做的事** — 過去一個月重複做了什麼備課工作？
2. **先跑一次** — 直接請 AI 幫你做一次，記下你的反應
3. **把回饋整理成原則** — 你反覆交代的東西，就是 Skill 裡要寫的東西
4. **請 AI 幫你寫成 Skill** — 「根據我們的對話，幫我建立一個 Skill」
5. **用新主題再跑一次** — 測試、發現新問題、繼續迭代

完整的實戰紀錄（從第一版到第三版的演變）見 [教師AI備課指南-從零建立你的第一個Skill](projects/_di-framework/reference/教師AI備課指南-從零建立你的第一個Skill.md)。

### 新增一個系統技能的流程

1. 在 `ai-core/skills/` 新建 `.md` 檔，包含：觸發條件、執行步驟、輸出格式
2. 在 [skills-manifest](ai-core/skills/skills-manifest.md) 加一行索引
3. （Claude Code 用戶）在 `.claude/commands/` 建薄層入口

---
## 四、加入 TeacherOS 前該想清楚的事

### 你需要的心理準備

> **注意：這不是一個讓你「更輕鬆備課」的工具**
> 這是一個讓你「更清楚地認識自己的教學」的系統。
> 初期投入的時間比你想像的多。回報在三個月後才開始顯現。

**1. 你必須先回答：我到底是怎麼工作的？**

要教 AI 怎麼幫你工作，你得先把自己的工作方式說清楚。這個過程本身就是一種專業成長——很多教師第一次被迫把「我就是這樣教的」轉化為可以寫下來的原則。

**2. 你必須接受：第一版一定不好用**

Skill 不是寫出來就完美的。它需要實際跑過、被學生和課堂檢驗、然後修正。這不是失敗，是系統在成長。

**3. 你必須願意：用 YAML 記錄狀態**

TeacherOS 的記憶不在你腦子裡，在 YAML 檔案裡。每次對話結束前更新進度錨點（session.yaml），下次對話 AI 才能接手。這個習慣需要刻意養成。

三層記憶模型的完整操作指引見 [TeacherOS × 專案三層記憶系統指引手冊](ai-core/TeacherOS%20×%20專案三層記憶系統指引手冊.md)。

### 你需要的動機

問自己兩個問題：

1. **「我有沒有一件事，反覆在做，每次都要從頭來過？」**
   如果有，TeacherOS 能幫你把它系統化。

2. **「我願不願意花時間把自己的教學智慧寫下來？」**
   如果願意，你建立的每一個 Skill、每一份 YAML，都是你的知識資產。
   它不會隨著換工具、換 AI 而消失——因為它是純文字，可搬移、可版本控制。

### 這套系統不適合的人

- 只想要 AI 直接給你一份教案，不想參與修改的人
- 不願意學習基本的 Git 操作（存檔、同步）的人
- 認為「AI 備課 = 偷懶」的人（這套系統比手動備課更累，但更系統化）

---
## 五、日常工作流程

### 每次對話的固定節奏

開場（opening）
├── git pull（確保最新版本）
├── 載入系統（teacheros.yaml → foundation → acl → personal → DI 框架）
└── 報告現況（各班各科的 Block/Step + 下一步）
↓
工作（load → lesson / syllabus / homeroom ...）
├── 載入班級脈絡（project.yaml + session.yaml）
├── 執行對應技能
└── 產出內容存入 content/*.md
↓
收尾（session-end）
├── 條列今次確認的決定
├── 更新 session.yaml 進度錨點
└── 告知下次工作起點

對應技能：[opening](ai-core/skills/opening.md) → [load](ai-core/skills/load.md) → [lesson](ai-core/skills/lesson.md) / [syllabus](ai-core/skills/syllabus.md) / [homeroom](ai-core/skills/homeroom.md) → [session-end](ai-core/skills/session-end.md)

### 檔案架構速覽

你的 workspace/
├── teacheros-personal.yaml ← 你是誰（Layer 1）
├── workspace.yaml ← 工作空間狀態
├── skills/ ← 你的個人技能
└── projects/
└── class-9c/
├── project.yaml ← 班級脈絡（Layer 2）
├── students.yaml ← 學生 DI 分析
├── english/
│ ├── session.yaml ← 進度錨點（Layer 3）
│ ├── di-profile.yaml
│ └── content/ ← 產出的教案、學習單
└── homeroom/
├── session.yaml
└── content/

完整架構見 [全站檔案總覽](../HOME.md)。

### 多工具協作

TeacherOS 不綁定單一 AI。Claude Code、Gemini、ChatGPT 都能用——只要能讀取檔案，就能執行技能。

工具切換靠 session.yaml 保持連續：
- 切換前：執行 [session-end](ai-core/skills/session-end.md)
- 切換後：執行 [load](ai-core/skills/load.md)

AI 入口文件 [AI_HANDOFF](ai-core/AI_HANDOFF.md) 是所有 AI 的起點——30 秒進入工作狀態。

---
## 六、檢討與持續改進

### 系統層級的檢討機制

| 時機 | 做什麼 | 參考 |
|------|--------|------|
| 每次對話結束 | 更新 session.yaml 進度錨點 | [session-end](ai-core/skills/session-end.md) |
| 每個教學區塊結束 | Block-end 反思：學生反應、教學調整、DI 效果 | [block-end](ai-core/skills/block-end.md) |
| 每學期 | 架構回顧：哪些 Skill 有效、哪些需要修正 | [architecture-review-2026-03-04](ai-core/reviews/architecture-review-2026-03-04.md) |

### Skill 的迭代原則

1. **每跑一次就可能發現新原則** — 記下來，更新 Skill
2. **學生的反應是最終檢驗標準** — 教案好不好用，教室裡見真章
3. **品質標準要定期校準** — 見 [strategy-output-quality-standard](projects/_di-framework/content/strategy-output-quality-standard.md)

### 給自己的提醒

> **David 的話**
> 「AI 能做的事讓 AI 做。你走進教室，看著學生的眼睛，用你自己的話說故事——這是機器永遠無法觸及的時刻。」

建立 Skill 的真正意義不是「讓 AI 幫你備課」，而是**把你的教學智慧系統化**。你花在 AI 上的每一分鐘，不是在學技術，而是在更清楚地認識自己的教學哲學。

---

## 延伸閱讀

| 主題 | 連結 |
|------|------|
| 全站檔案索引 | [全站檔案總覽](../HOME.md) |
| 華德福教師在 AI 時代的定位 | [AI 時代華德福教師的定位與價值](ai-core/AI%20時代華德福教師的定位與價值.md) |
| 學生發展與課程連結 | [華德福七至九年級學生生命樣態與課程的連結](ai-core/華德福七至九年級學生生命樣態與課程的連結.md) |
| 三層記憶系統操作指引 | [TeacherOS × 專案三層記憶系統指引手冊](ai-core/TeacherOS%20×%20專案三層記憶系統指引手冊.md) |
| Skill 建立實戰紀錄 | [教師AI備課指南-從零建立你的第一個Skill](projects/_di-framework/reference/教師AI備課指南-從零建立你的第一個Skill.md) |
| 差異化教學框架 | [DI 框架 project.yaml](projects/_di-framework/project.yaml) |
| 技能總目錄 | [技能總目錄 README](ai-core/skills/README.md) |
| 新教師環境設定 | [teacher-guide.md](setup/teacher-guide.md) |
