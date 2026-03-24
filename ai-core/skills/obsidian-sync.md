---
name: obsidian-sync
description: 掃描 Repo 中缺少中文標籤的檔案，自動補上 aliases / 中文標頭，並將未收錄檔案加入 HOME.md。
triggers:
  - sync Obsidian
  - 更新索引
  - 補標籤
  - 整理首頁
requires_args: false
---

# skill: obsidian-sync — Obsidian 標籤與索引同步

掃描 Repo，為缺少中文標籤的 .md / .yaml 檔案補上標籤，並將未收錄 HOME.md 的檔案加入首頁索引。

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 執行步驟

### Step 1 — 執行偵測腳本

```bash
python3 setup/scripts/obsidian-check.py
```

> **跨平台注意：** Windows 上可能需使用 `python` 而非 `python3`，AI 應先偵測可用的 Python 指令（`python3` 或 `python`）。可用 `python3 --version || python --version` 判斷。

解析輸出，取得三類檔案清單：
- `UNLABELED_MD` — 缺少 `aliases:` frontmatter 的 .md 檔
- `UNLABELED_YAML` — 前 5 行無中文字元的 .yaml 檔
- `NOT_IN_HOME` — 未被 HOME.md 引用的檔案

若三類皆為 0，回應：「所有檔案已標籤且收錄 HOME.md，不需要更新。」結束。

### Step 2 — 為未標籤的 .md 檔加上 aliases

逐一處理 `FILE:NEW_MD:` 清單中的每個檔案：

1. 讀取檔案前 30 行
2. 根據**路徑位置**和**內容前幾行**，產生 1-2 個簡短中文 alias
3. 寫入 frontmatter

**命名規則：**

| 路徑模式 | alias 生成策略 |
|----------|--------------|
| `ai-core/skills/*.md` | **跳過**（使用 `name:` 欄位） |
| `.claude/commands/*.md` | **跳過**（使用 `name:` 欄位） |
| `.claude/skills/*/SKILL.md` | **跳過**（使用 `name:` 欄位） |
| `projects/_di-framework/content/*.md` | 從標題或首段提取教學關鍵詞 |
| `workspaces/.../content/*.md` | 「[班級] [科目] [內容摘要]」 |
| `ai-core/reference/*.md` | 從標題提取，加上「參考文件」 |
| 其他 | 從標題或檔名翻譯 |

**frontmatter 格式：**

```yaml
---
aliases:
  - "中文別名"
---
```

若檔案已有 `---` 開頭但缺少 `aliases:`，在既有 frontmatter 內插入 `aliases:` 欄位，不破壞其他欄位。
若檔案沒有 frontmatter，在檔案最前方新增完整 `---` 區塊。

### Step 3 — 為未標籤的 .yaml 檔加上中文標頭

逐一處理 `FILE:NEW_YAML:` 清單中的每個檔案：

1. 讀取檔案前 20 行
2. 根據路徑與內容，產生中文標頭註解區塊
3. 寫入檔案最前方（在任何 YAML 內容之前）

**標頭格式：**

```yaml
# ━━━
# 【TeacherOS {層級}】
# 名稱：{中文名稱}
# 路徑：{相對路徑}
# ━━━
```

層級判斷：
- `teacheros.yaml` / `teacheros-foundation.yaml` → Layer 1 系統核心
- `project.yaml` → Layer 2 專案記憶
- `session.yaml` / `lesson.yaml` / `assessment.yaml` / `di-profile.yaml` → Layer 3 工作線
- `roster.yaml` / `students.yaml` → 班級資料
- `acl.yaml` / `system-status.yaml` → 系統設定
- 其他 → 設定檔

### Step 3.5 — 清理 HOME.md（先清再補）

在新增任何條目之前，先處理偵測腳本回報的清理類別：

**DEAD_LINK（死連結）：**
- 從 HOME.md 中刪除該行（整行 wikilink 表格列）
- 若刪除後表格變空，連同表頭一起刪除

**EMPTY_FILE（空檔）：**
- 提醒教師確認是否刪除該空檔
- 教師同意 → 刪除檔案 + 從 HOME.md 移除對應條目
- 教師拒絕 → 跳過，保留現狀

**PRIVATE_IN_HOME（不該收錄的檔案）：**
- 從 HOME.md 刪除該行
- 這類檔案包含：private/ 路徑下的檔案、已搬走的圖片/音訊/影片

清理完成後再執行 Step 4。

### Step 4 — 更新 HOME.md

讀取根目錄的 `HOME.md`，將 `FILE:NOT_IN_HOME:` 清單中的檔案插入對應區段。

**分類強制規則（SUGGEST 欄位）：** 偵測腳本輸出 `FILE:NOT_IN_HOME:{path}:SUGGEST:{section}`。

**AI 必須嚴格依照 SUGGEST 欄位決定插入位置，禁止自行推斷或堆入根目錄散檔。** 具體流程：

1. 解析 SUGGEST 欄位，判斷目標 H2 區段（如「David 的工作空間」）和 H3 子區段（如「botany-grade5」）
2. 在 HOME.md 中搜尋對應的 H2/H3 區段
3. **若 H3 區段已存在** → 插入該區段的表格末尾
4. **若 H3 區段不存在但 H2 存在** → 在該 H2 區段末尾（`---` 分隔線之前）自動建立新 H3 區段，含表頭
5. **若 H2 也不存在** → 依 H2 固定順序規則建立新 H2 區段後再建 H3
6. **絕對不可**將任何 `workspaces/` 路徑下的檔案放入「根目錄散檔」

**獨立專案自動建區規則（關鍵）：**

教師 workspace 下 `projects/` 中非 `class-*` 的目錄（如 `botany-grade5`、`stories-of-taiwan`、`taiwanese-history`）為獨立專案。每個獨立專案必須有自己的 H3 區段：

1. H3 標題格式：`### {專案顯示名}`（從 project.yaml 的 `project:` 欄位取得中文名；無 project.yaml 則用目錄名）
2. 區段內按子目錄結構分組（專案設定 → 參考章節 → 各 story/lesson ID）
3. 與 `stories-of-taiwan` 相同的子架構邏輯適用於所有故事型專案（有 `stories/` 子目錄的專案）：每個 ID 獨立標題 + 表格

**HOME.md H2 區段固定順序（AI 不可變更）：**

1. `## David 的工作空間`
2. 各教師的工作空間（`## [教師名]老師的工作空間`），按加入順序排列
3. `## 教師環境預填（env-preset.env）`
4. `## 技能系統（Skills）`
5. `## Good-notes 建造日誌`
6. 其餘區段（差異化教學框架、母文件、系統核心、設定等）

**新教師區段自動建立規則：**

當 `workspaces/Working_Member/Teacher_{姓名}/**` 路徑的檔案出現在 NOT_IN_HOME 清單中，
但 HOME.md 中尚無 `## {姓名}老師的工作空間` 區段時：

1. 在最後一位老師的工作空間 `---` 分隔線之後、`## 教師環境預填` 之前，插入新區段
2. 參照現有老師區段的格式（### 個人設定、### 個人技能、### 班級 等），按檔案路徑結構自動分組
3. 不可將新教師的檔案堆入「根目錄散檔」

**第一層：大區段判斷**

| 路徑模式 | 插入區段 |
|----------|---------|
| `ai-core/skills/*.md` | 系統技能正本 |
| `ai-core/reference/*.md` / `*.yaml` | Reference 知識模組 / 操作文件 |
| `ai-core/reviews/*.md` | 系統回顧紀錄 |
| `projects/_di-framework/**` | 差異化教學框架 |
| `workspaces/Working_Member/Codeowner_David/**` | David 的工作空間（依班級/科目細分） |
| `workspaces/Working_Member/Teacher_*/**` | 對應教師的工作空間（若區段不存在則自動建立） |
| `Good-notes/**` | Good-notes 建造日誌 |
| `setup/**` | 環境設定與腳本 |
| `publish/**` | 輸出與發佈 |
| `.claude/**` | Claude Code 設定 |
| 根目錄散檔 | 根目錄散檔（僅限不屬於任何教師 workspace 的真正散檔） |

**第二層：子架構感知（HOME.md 必須反映檔案系統的實際組織方式）**

大區段確定後，AI 必須進一步檢查檔案所在的子目錄結構，讓 HOME.md 的排列與檔案系統的資料夾層級對齊。核心原則：**HOME.md 是 Obsidian 的導覽地圖，它的分組邏輯必須鏡像檔案系統的資料夾結構。**

子架構規則（依優先順序匹配）：

| 路徑模式 | 分組方式 | HOME.md 呈現 |
|----------|---------|-------------|
| `{專案}/stories/[區塊或直接]/[ID]/` | 每個 ID 獨立為一組 | `**[ID] [標題]**` 標題 + 表格 |
| `{專案}/stories/[區塊]/[ID]-v2/` | v2 歸入對應原版 ID 的表格 | 在原版表格末尾追加 `v2 content` 等行 |
| `{專案}/reviews/[ID]-quality.md` | 品質報告歸入對應 ID | 在對應表格末尾追加 `品質報告` 行 |
| `{專案}/kovacs-chapters/` 等參考章節目錄 | 整批歸為一個子表格 | `**[目錄顯示名]**` 標題 + 表格 |
| `class-*/[科目]/` | 每個科目獨立為一組 | 沿用現有科目標題 |
| `class-*/[科目]/content/` | 內容歸入對應科目 | 追加到科目表格末尾 |
| `class-*/student-notes/` | 學生紀錄依座號排列 | 沿用現有學生紀錄區塊 |

**泛化原則：** 上述 `{專案}` 匹配所有獨立專案（stories-of-taiwan、botany-grade5、taiwanese-history 等）。新專案出現時，自動套用相同邏輯，無需修改此規則。

**具體操作（適用所有故事型專案）：**

1. 從檔案路徑提取專案名、ID（如 `B002`）、子目錄結構
2. 在 HOME.md 中找到該專案的 H3 區段（如 `### 五年級植物學`）
3. 檢查該 ID 是否已有粗體標題（搜尋 `**B002`）
4. 若無 → 在該專案區段最後一個 ID 的表格之後，新建 `**[ID] [標題]**` + 新表格
5. 若有 → 將新檔案追加到該 ID 的現有表格中
6. 標題從 content.md 的 frontmatter `title:` 欄位提取
7. v2 版本不建獨立標題，追加到原版表格末尾
8. 品質報告追加到對應 ID 表格最後一行
9. **若整個 H3 區段不存在** → 自動建立（見上方「獨立專案自動建區規則」）

**wikilink 格式規則：**

故事檔案使用短名顯示（不重複故事 ID）：

```markdown
| [[完整路徑/content|content]] | 故事正文 |
| [[完整路徑/narration|narration]] | 教師說書稿 |
```

非故事檔案使用中文名顯示：

```markdown
| [[路徑/檔名|中文名]] | 說明 |
```

**排序規則：**

- 故事 ID 按字母 + 數字升序（A001 → A002 → ... → B001）
- 同一故事內：content → narration → images → chalkboard → raw-materials → v2 系列 → 品質報告
- 科目按既有順序，新科目附加到末尾

若無法匹配任何子架構規則，退回到大區段邏輯，附加到最接近的現有區段末尾。

### Step 5 — 輸出摘要

```
Obsidian 同步完成：
- N 個 .md 已加上 aliases
- N 個 .yaml 已加上中文標頭
- N 個檔案已加入 HOME.md
```

## 注意事項

- 此技能**只讀偵測腳本的結果**，不自行掃描檔案系統
- aliases 產生需要理解檔案內容，因此必須由 AI 執行，不能純腳本處理
- 不修改已有正確標籤的檔案
- HOME.md 的修改採**先清後補**邏輯：Step 3.5 清理死連結與殘留，Step 4 新增條目
- **個人設定區段嚴格限定：** 只放 `teacheros-personal.yaml`、`workspace.yaml`、`env-preset.env`、`README.md`。其他所有檔案必須歸入對應子區段，不可堆入個人設定
- **非文字檔不收錄 HOME.md：** `.png`、`.jpg`、`.mp3`、`.mp4` 等二進位檔案，若在 `private/` 或已被 gitignore，不應出現在 HOME.md 中
- 若偵測腳本不存在，提示：「請先確認 `setup/scripts/obsidian-check.py` 存在。」
