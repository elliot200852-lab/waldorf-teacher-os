---
name: botany-daily
description: 五年級植物學每日故事管線。從選題到上傳的完整 8 步驟： 確認下一課 → 素材研究（Kovacs + 台灣植物 WebSearch）→ 撰寫 7 件套 → 品質檢查 → Gemini 黑板畫生成 → 組裝 HTML/PDF → 上傳 Google Drive → 歸檔索引。
triggers:
  - 植物學故事
  - 每日植物學
  - 寫一篇植物學
  - botany daily
  - botany story
platforms:
  - cowork
  - claude-code
  - gemini
requires_args: false
version: 1.1.0
created: 2026-03-24
updated: 2026-04-17
---

# 五年級植物學每日故事管線 v1.1.0

## 專案路徑

```
workspaces/Working_Member/Codeowner_David/projects/botany-grade5/
```

## 工作規則

授權、版本、檔名、強制完成規則全部依 `teacheros-personal.yaml` 的 `ai_working_rules` 區塊。

**本 pipeline 補充**：
- Drive 目標資料夾 ID：`1jjtNmAtzcpbzVmHY8Dz8Dqz4w2fMJbU4`（「植物學五年級」）
- 運行模式：全自動（無任何確認點）

---

## Pipeline 步驟總覽

```
Step 0   前置確認（project.yaml + theme-skeleton.yaml）
Step 1   建立任務（current-task.yaml + 子資料夾）
Step 2   素材研究（2 agent 並行：Kovacs + 台灣植物）
Step 3   撰寫 7 件套（3 agent 並行）
Step 4   Gemini 黑板畫生成（gemini-chalkboard，12 子步驟）
Step 5   組裝 HTML/PDF（assemble-botany.js）
Step 6   上傳 Google Drive
Step 7   歸檔（index.yaml + project.yaml）
```

---

## Step 0 — 前置確認

讀取 `project.yaml`：
- `story_count.total` = 已完成數
- 下一課號 = total + 1（格式：B001 ~ B030）
- 若 total >= 30 → 回報「全部 30 課已完成」，結束 pipeline

讀取 `theme-skeleton.yaml`，取出該課的：
- title, kovacs_chapter, block, core_image, taiwan_species, taiwan_connection, art_response

---

## Step 1 — 建立任務

1. 建立 `stories/B0XX/` 子資料夾
2. 寫入 `current-task.yaml`：

```yaml
lesson_id: B0XX
title: "..."
kovacs_chapter: "XX_..."
block: block-X-...
taiwan_species: [...]
search_keywords: [...]
started_at: 2026-XX-XXTXX:XX:XX
```

---

## Step 2 — 素材研究（2 agent 並行）

**Agent A（本地 — Kovacs 章節摘要）**：
- 讀取 `kovacs-chapters/XX_*.md`
- 摘要：核心教學意象、說故事手法、科學事實、兒童發展類比

**Agent B（線上 — 台灣植物搜尋）**：
- WebSearch 搜尋台灣植物資料（至少 3 次搜尋）
- 搜尋目標：學名/分布/特有種/俗諺/Wikimedia Commons 圖片 URL
- 來源優先序：TaiCOL → 林務局 → 特生中心 → 維基百科 → iNaturalist

**合併產出**：`[ID]-raw-materials.md`
- Kovacs 核心段落摘要（英文，標註章節）
- 台灣植物對應資料（中文）
- 資料來源（至少 3 筆含 URL）
- 台灣俗諺（1-2 句）

**Checkpoint**：[ID]-raw-materials.md > 500 字 + 至少 3 筆 URL → 否則 FAIL

---

## Step 3 — 撰寫 7 件套（3 agent 並行）

**Agent C（撰寫主力）**：
- 產出：`[ID]-content.md`（800 字說書稿）+ `[ID]-chalkboard-prompt.md`（黑板畫 Prompt）
- [ID]-content.md 必須含 `## 故事本文` 和 `## 事實出處` 表格

**Agent D（教學精要）**：
- 產出：`[ID]-kovacs-teaching.md`（300 字）
- 含三段：教學巧妙之處 / 與當代科學的對話 / 台灣植物趣事+俗諺

**Agent E（圖像與來源）**：
- 產出：`[ID]-images.md`（至少 3 張圖 + URL + 授權）+ `[ID]-references.md`（所有來源）

**主線程**：三者完成後，品質自檢 → `[ID]-quality-report.md`

**Checkpoint**：6 檔全部存在 + [ID]-chalkboard-prompt 含 `## English Prompt` → 否則 FAIL

---

## Step 4 — 黑板畫生成

**執行共用技能 `ai-core/skills/gemini-chalkboard.md`。**

參數：
- STORY_ID = [當前課號，如 B008]
- STORY_DIR = 故事目錄完整路徑
- VERSION = [版本標記，若有]

完整操作流程（12 步）、圖片內容驗證 checkpoint、重試邏輯、排程 fallback 均定義於 `gemini-chalkboard.md`。

**Checkpoint**：gemini-chalkboard.md 的 Checkpoint 全部通過（檔案存在 + > 50KB + 圖片內容驗證 PASS + 下載檔名已登錄）→ 否則重試（最多 3 次）。排程模式下若 Claude in Chrome 不可用 → SKIP，標記 `chalkboard: pending`。

---

## Step 5 — 組裝 HTML/PDF

```bash
node publish/scripts/assemble-botany.js \
  workspaces/Working_Member/Codeowner_David/projects/botany-grade5/stories/B0XX \
  --pdf --upload
```

**組裝清單（5 項必需 + 1 選用）**：
1. `[ID]-content.md` — 故事正文 + 事實出處表
2. `[ID]-kovacs-teaching.md` — Kovacs 教學精要
3. `[ID]-images.md` — 投影圖像清單
4. `[ID]-chalkboard-prompt.md` — Gemini 中英文 prompt
5. `[ID]-references.md` — 參考來源
6. `[ID]-raw-materials.md` — 素材包（選用，供 URL 交叉匹配）

**黑板畫圖檔**：`~/Downloads/Botany-B0XX-chalkboard.png`（base64 嵌入）

**輸出驗證（exit code 2 = 失敗）**：
- 故事段落數 > 0
- 事實出處表 > 0 且至少 1 筆有 URL
- 圖像清單 > 0
- Kovacs 教學精要存在
- 參考來源 > 0
- 黑板畫已嵌入（或 pending）

若失敗 → 讀取錯誤訊息修正 → 重試（最多 2 次）

---

## Step 6 — 上傳 Google Drive

assemble-botany.js 的 `--upload` 旗標自動處理：
- 上傳 HTML + PDF 到「植物學五年級」資料夾（ID: `1jjtNmAtzcpbzVmHY8Dz8Dqz4w2fMJbU4`）
- 舊檔 upsert（同 lesson_id 的舊檔先刪再傳）

**fallback**：GWS CLI 不可用 → 跳過上傳，HTML/PDF 存 `temp/`，標記 `drive_upload: pending`

**上傳成功後，觸發 CreatorHub 網站部署：**

```bash
gh workflow run deploy-channel.yml
```

此指令觸發 GitHub Actions 的 sync + deploy 流程（~3 分鐘），確保新故事立即出現在 CreatorHub 網站上。若 `gh` 指令不可用或上傳被跳過，不觸發。

---

## Step 7 — 歸檔

1. 追加 `index.yaml` 條目（id, title, block, kovacs_chapter, taiwan_species, date_created, files, quality_check, drive, tags）
2. 更新 `project.yaml` 的 `story_count`（total + by_block）
3. 更新 `project.yaml` 的 `current_position`
4. 刪除 `current-task.yaml`

---

## Checkpoint 矩陣

| 轉換 | 驗證項 | 失敗等級 |
|------|--------|----------|
| 0→1 | project.yaml + theme-skeleton.yaml 存在 | FAIL |
| 1→2 | current-task.yaml 非空 | FAIL |
| 2→3 | [ID]-raw-materials.md > 500 字 + 至少 3 筆 URL | FAIL |
| 3→4 | 6 檔全部存在 + [ID]-chalkboard-prompt 含 `## English Prompt` | FAIL |
| 4→5 | ~/Downloads/Botany-B0XX-chalkboard.png > 50KB | FAIL（重試 3 次）|
| 5→6 | HTML + PDF 存在 + 黑板畫 base64 嵌入 | FAIL |
| 6→7 | Drive 上傳成功 | WARN |

---

## 排程模式 Fallback

| 情境 | fallback |
|------|----------|
| Claude in Chrome 不可用（Step 4） | SKIP 黑板畫，標記 pending，HTML/PDF 照產 |
| GWS CLI 不可用 | 跳過上傳，存本地 |
| 任何步驟 FAIL | 寫入 pipeline-status.yaml，下次提示教師 |

---

## 完成報告格式

```
Pipeline 完成：B0XX [標題]

Step 0-1 前置+選題：PASS
Step 2   素材研究：PASS — [ID]-raw-materials.md [N] 字
Step 3   撰寫：    PASS — 7 件套全部到位
Step 4   黑板畫：  PASS — ~/Downloads/Botany-B0XX-chalkboard.png
Step 5   組裝：    PASS
  HTML：     temp/beautify-B0XX-植物學完整版.html
  PDF：      temp/B0XX-植物學完整版.pdf
  黑板畫嵌入：embedded
  事實超連結：[N] 個 URL
  投影圖像：  [N] 張
  Kovacs：   present
  參考來源：  [N] 筆
Step 6   Drive：   PASS — HTML + PDF 已上傳
Step 7   歸檔：    PASS — index.yaml + project.yaml 已更新

區塊進度：Block X [M/N]
全專案進度：[total] / 30 篇
```
