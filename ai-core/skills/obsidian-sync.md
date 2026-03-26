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

### Step 4 — 報告未收錄 HOME.md 的檔案（不自動寫入）

讀取 `FILE:NOT_IN_HOME:` 清單，**向教師報告**哪些檔案不在 HOME.md 中。

**重要：不自動將檔案寫入 HOME.md。**

過去的「自動收錄」機制會把所有未索引的檔案（包括腳本、暫存檔、XML 碎片）不加判斷地塞進 HOME.md 並標為「自動收錄」，導致 HOME.md 嚴重臃腫。現改為報告模式：

1. 列出未收錄的檔案清單
2. 建議每個檔案應歸入哪個 HOME.md 區段
3. 詢問教師：「要加入 HOME.md 嗎？」
4. 教師確認後才寫入，且寫入時必須附上正確的中文說明（不使用「自動收錄」）

**區段判斷參考（供 AI 建議用）：**

| 路徑模式 | 建議區段 |
|----------|---------|
| `ai-core/skills/*.md` | 系統技能正本 |
| `ai-core/reference/*.md` / `*.yaml` | Reference 知識模組 |
| `projects/_di-framework/**` | 差異化教學框架 |
| `workspaces/Working_Member/Codeowner_David/**` | David 的工作空間（依班級/科目細分） |
| `workspaces/Working_Member/Teacher_*/**` | 對應教師的工作空間 |
| `setup/**` | 環境設定與腳本 |
| `publish/**` | 輸出與發佈 |

若 `NOT_IN_HOME` 為 0，不需要報告。

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
- HOME.md 的修改需教師確認後才執行，不再自動附加「自動收錄」條目
- 若偵測腳本不存在，提示：「請先確認 `setup/scripts/obsidian-check.py` 存在。」
