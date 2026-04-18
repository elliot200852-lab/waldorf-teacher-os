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

### Step 0.5 — 地圖新鮮度檢查

在掃描前先確認架構地圖是最新的：

```bash
python3 setup/scripts/map-validate.py --validate
```

- 若有 **errors**：警告教師「地圖包含錯誤，建議先修復再繼續」
- 若有 **backward warnings**（目錄未覆蓋）：自動執行 `python3 setup/scripts/map-validate.py --rebuild-dirs`
- 若 地圖檔不存在：跳過此步驟（graceful 退化，obsidian-check.py 會自動退化為無建議模式）

### Step 1 — 執行偵測腳本（地圖驅動過濾 + 身份 scope）

**身份 scope 原則（v2.0 分支模型）：**
obsidian-sync 只改執行者能 commit 的檔案範圍。HOME.md 收錄（NOT_IN_HOME）不受 scope 限制，因為只動 HOME.md 本身；但 aliases / frontmatter / wikilinks 的寫入必須局限在執行者 workspace 內，不跨線污染其他老師的檔案。

**scope 決策：**

| 身份 | 執行指令 |
|------|---------|
| admin（David） | `--exclude-scope="workspaces/Working_Member/Teacher_*"` — 掃全 repo，排除其他老師 workspace |
| 老師 | `--write-scope="workspaces/Working_Member/Teacher_{姓名}"` — 只動自己 workspace |

從 `ai-core/acl.yaml` 取得當前使用者的 workspace 路徑，轉成對應的 scope 參數。

**執行：**

```bash
# David（admin）
python3 setup/scripts/obsidian-check.py --map-filter --exclude-scope="workspaces/Working_Member/Teacher_*"

# 老師（以 {姓名} 代入）
python3 setup/scripts/obsidian-check.py --map-filter --write-scope="workspaces/Working_Member/Teacher_{姓名}"
```

解析輸出，取得分類清單：
- `UNLABELED_MD` — 缺少 `aliases:` frontmatter 的 .md 檔（已過 scope 過濾）
- `UNLABELED_YAML` — 前 5 行無中文字元的 .yaml 檔（已過 scope 過濾）
- `ROUTED` — 未收錄 HOME.md，但地圖有匹配路由（全 repo，不過濾）
- `UNROUTED` — 未收錄 HOME.md，且地圖無匹配路由（全 repo，不過濾）

輸出格式：
- `FILE:NOT_IN_HOME:path|section` — 有路由（ROUTED）
- `FILE:NOT_IN_HOME_UNROUTED:path` — 無路由（UNROUTED）

若所有類別皆為 0，回應：「所有檔案已標籤且收錄 HOME.md，不需要更新。」結束。

### Step 1.5 — 連結完整性檢查（wikilink）

連結檢查同樣套用身份 scope：

```bash
# David
python3 setup/scripts/obsidian-check.py --link-check --skip-home-check --count-only --exclude-scope="workspaces/Working_Member/Teacher_*"

# 老師
python3 setup/scripts/obsidian-check.py --link-check --skip-home-check --count-only --write-scope="workspaces/Working_Member/Teacher_{姓名}"
```

解析輸出中的 `LINK_ORPHAN` 數量。

- 若為 0：跳過，不報告
- 若大於 0：執行完整掃描取得清單

```bash
# 帶上與 Step 1 相同的 scope 參數
python3 setup/scripts/obsidian-check.py --link-check --skip-home-check <scope flag>
```

解析 `FILE:LINK_ORPHAN:path|type|missing:what` 清單，向教師報告：

```
連結檢查：N 個檔案缺連結
- story_content: X 個（缺 related / body）
- story_component: X 個（缺 related）
- wiki_entry: X 個（缺 related / body）
- lesson_plan: X 個
要自動補齊嗎？
```

**教師確認後**，AI 逐一處理：

| 缺什麼 | AI 做什麼 |
|--------|----------|
| `related` | 在 frontmatter 加 `related: []`，AI 根據同目錄檔案和上下文填入初始 wikilinks |
| `body` | 在檔案末尾加 `## 連結` 區段，依 `wikilink-protocol.yaml` 的模板格式填入 |

**規則**：
- story_content 的 `## 連結` 用 `story_template`（含 CreatorHub 外部連結 + narration/images/chalkboard wikilinks）
- wiki_entry 的 `## 連結` 用 `body_section_format.template`
- 學習單不加 body section（學生會看到）
- 已有正確連結的檔案不動（冪等）
- 量大時（> 30 個），先處理 wiki_entry 和 lesson_plan，story 類留到下次

### Step 2 — 為未標籤的 .md 檔加上 aliases

逐一處理 `FILE:NEW_MD:` 清單中的每個檔案：

1. 讀取檔案前 30 行
2. 根據**路徑位置**和**內容前幾行**，產生 1-2 個簡短中文 alias
3. 寫入 frontmatter

**命名規則：**

| 路徑模式 | alias 生成策略 |
|----------|--------------|
| `ai-core/skills/*.md` | 若已有 `name:` 但無 `aliases:`，從 `name:` 複製為 aliases |
| `.claude/commands/*.md` | 若已有 `name:` 但無 `aliases:`，從 `name:` 複製為 aliases |
| `.claude/skills/*/SKILL.md` | 若已有 `name:` 但無 `aliases:`，從 `name:` 複製為 aliases |
| `.agents/skills/*/SKILL.md` | 若已有 `name:` 但無 `aliases:`，從 `name:` 複製為 aliases |
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

### Step 4 — 報告未收錄 HOME.md 的檔案（地圖驅動分流）

若 `ROUTED` 和 `UNROUTED` 皆為 0，不需要報告，跳到 Step 5。

**嚴禁事項：**
- **絕對不使用「（自動收錄）」作為說明文字** — pre-commit hook 會攔截
- **UNROUTED 檔案絕對不自動寫入** — 必須報告、教師決定後才寫入
- **不塞到「根目錄散檔」** — 那是最後手段，幾乎所有檔案都有更精確的歸屬

**執行流程（兩條路徑）：**

#### A. ROUTED 檔案（有地圖路由）

1. 讀取 `FILE:NOT_IN_HOME:path|section` 清單
2. 向教師報告：列出每個檔案、建議區段、建議的中文說明
3. 教師確認後寫入（可能調整區段或說明）
4. 寫入格式：`| [[路徑\|顯示名]] | 中文說明 |`

#### B. UNROUTED 檔案（無地圖路由）

1. 讀取 `FILE:NOT_IN_HOME_UNROUTED:path` 清單
2. 向教師報告：「以下檔案不在地圖路由範圍內，需要您決定歸屬：」
3. **不提供建議、不自動寫入**
4. 教師告知區段後，AI 再寫入 HOME.md
5. 若教師決定某路徑模式今後應自動歸類，AI 同時在 `repo-structure-map.yaml` 中新增對應 rule

> **路由規則存放位置：** `ai-core/reference/repo-structure-map.yaml`
> 驗證工具：`python3 setup/scripts/map-validate.py --validate`

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
- **HOME.md 寫入的四條鐵規：**
  1. 絕對不使用「（自動收錄）」— pre-commit hook 會攔截含此字樣的 HOME.md
  2. 必須比對區段結構表找到精確位置，不塞到「根目錄散檔」
  3. ROUTED 檔案：向教師報告建議後寫入
  4. UNROUTED 檔案：**絕對不自動寫入**，等教師明確指示
- wrap-up 技能不觸發 HOME.md 收錄（使用 `--skip-home-check`），只有本技能處理 HOME.md
- 若偵測腳本不存在，提示：「請先確認 `setup/scripts/obsidian-check.py` 存在。」
