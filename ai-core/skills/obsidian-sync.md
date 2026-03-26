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

### Step 4 — 報告未收錄 HOME.md 的檔案（確認後才寫入）

讀取 `FILE:NOT_IN_HOME:` 清單，**向教師報告**哪些檔案不在 HOME.md 中。

若 `NOT_IN_HOME` 為 0，不需要報告，跳到 Step 5。

**嚴禁事項：**
- **絕對不使用「（自動收錄）」作為說明文字** — pre-commit hook 會攔截
- **不自動寫入** — 必須先報告、教師確認後才寫入
- **不塞到「根目錄散檔」** — 那是最後手段，幾乎所有檔案都有更精確的歸屬

**執行流程：**

1. 逐一比對下方「區段結構表」，找出每個檔案的精確歸屬區段
2. 向教師報告：列出每個檔案、建議區段、建議的中文說明
3. 教師確認後寫入（可能調整區段或說明）
4. 寫入時使用正確的中文說明，格式為 `| [[路徑\|顯示名]] | 中文說明 |`

**HOME.md 區段結構表（精確比對，依優先順序）：**

AI 必須從上往下比對，找到**第一個符合的規則**就停。

| 路徑模式 | 歸入 HOME.md 區段 | 備註 |
|----------|-------------------|------|
| `workspaces/.../Codeowner_David/teacheros-personal.yaml` | `## David 的工作空間 > ### 個人設定` | |
| `workspaces/.../Codeowner_David/skills/*.md` | `## David 的工作空間 > ### 個人技能` | |
| `workspaces/.../Codeowner_David/scripts/*` | `## David 的工作空間 > ### 個人腳本` | |
| `workspaces/.../Codeowner_David/poetry_output/**` | `## David 的工作空間 > ### 詩歌研究素材產出` | 依主題子區段 |
| `workspaces/.../class-9c/project.yaml` | `## David 的工作空間 > ### 9C 班級`（班級設定表格） | |
| `workspaces/.../class-9c/english/**` | `## David 的工作空間 > ### 9C 班級 > 9C 英文` | content/ 歸到「內容產出」 |
| `workspaces/.../class-9c/homeroom/**` | `## David 的工作空間 > ### 9C 班級 > 9C 導師` | |
| `workspaces/.../class-9c/farm-internship/**` | `## David 的工作空間 > ### 9C 班級 > 9C 農場實習` | |
| `workspaces/.../class-9c/walking-reading-taiwan/**` | `## David 的工作空間 > ### 9C 班級 > 9C 走讀臺灣` | |
| `workspaces/.../class-9d/**` | `## David 的工作空間 > ### 9D 班級` | 依科目細分 |
| `workspaces/.../ancient-myths-grade5/**` | `## David 的工作空間 > ### 古文明神話（五年級）` | |
| `workspaces/.../stories-of-taiwan/**` | `## David 的工作空間 > ### 臺灣的故事` | 依故事編號 |
| `workspaces/.../taiwanese-history/**` | `## David 的工作空間 > ### 臺灣歷史課程文稿` | |
| `workspaces/.../botany-grade5/**` | `## David 的工作空間 > ### 五年級植物學` | |
| `workspaces/.../deep-review-*` | `## David 的工作空間 > ### 系統深度審查` | |
| `workspaces/.../Codeowner_David/**`（其他） | `## David 的工作空間`（找最接近的子區段） | |
| `workspaces/.../Teacher_郭耀新/**` | `## 郭耀新老師的工作空間`（依子區段） | |
| `workspaces/.../Teacher_陳佩珊/**` | `## 陳佩珊老師的工作空間`（依子區段） | |
| `workspaces/.../Teacher_林詩閔/**/student-logs/*` | `## 林詩閔老師 > ### 4C 班級 > 學生紀錄` | 按姓氏排序 |
| `workspaces/.../Teacher_林詩閔/**` | `## 林詩閔老師的工作空間`（依子區段） | |
| `workspaces/.../Teacher_*/**` | 對應教師的 `##` 區段（依子區段） | |
| `ai-core/skills/*.md` | `## 技能系統 > ### 系統技能正本` | 三欄表格 |
| `ai-core/reference/*.yaml` | `## 系統核心 > ### Reference 知識模組（YAML）` | |
| `ai-core/reference/*.md` | `## 系統核心 > ### Reference 操作文件` | |
| `ai-core/reviews/*` | `## 系統核心 > ### 系統回顧紀錄` | |
| `ai-core/*.yaml` | `## 系統核心 > ### 系統設定（YAML）` | |
| `ai-core/*.md` | `## 系統核心 > ### AI 入口與流程` | |
| `projects/_di-framework/content/*` | `## 差異化教學框架 > ### 操作文件` 或 `### 英文差異化區塊設計` | |
| `projects/_di-framework/reference/*` | `## 差異化教學框架 > ### 參考範例` | |
| `projects/_di-framework/*` | `## 差異化教學框架 > ### 框架設定` | |
| `.claude/skills/*/SKILL.md` | `## Claude Code 設定 > ### Claude Code Skills` | |
| `.claude/skills/*/references/*` | `## Claude Code 設定 > ### Claude Code Skills` | 歸到對應 skill 旁 |
| `.claude/commands/*.md` | `## Claude Code 設定 > ### Claude Code Commands` | |
| `.claude/*` | `## Claude Code 設定 > ### 設定檔` | |
| `Git History/*` | `## Git History 週記` | |
| `setup/scripts/*` | `## 環境設定與腳本 > ### 工具腳本` | |
| `setup/*` | `## 環境設定與腳本` | 依子區段 |
| `publish/*` | `## 輸出與發佈` | |
| `Good-notes/*` | `## Good-notes 建造日誌` | |
| 根目錄 `.md` / `.yaml` | `## 根目錄散檔` | **最後手段** |

**若沒有匹配的區段：** 向教師報告「找不到適合的 HOME.md 區段，建議位置是 [最接近的區段]」，由教師決定。

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
- **HOME.md 寫入的三條鐵規：**
  1. 絕對不使用「（自動收錄）」— pre-commit hook 會攔截
  2. 必須比對區段結構表找到精確位置，不塞到「根目錄散檔」
  3. 教師確認後才寫入，每個條目附正確的中文說明
- wrap-up 技能不觸發 HOME.md 收錄（使用 `--skip-home-check`），只有本技能處理 HOME.md
- 若偵測腳本不存在，提示：「請先確認 `setup/scripts/obsidian-check.py` 存在。」
