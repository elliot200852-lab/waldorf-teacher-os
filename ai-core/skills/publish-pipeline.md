---
name: publish-pipeline
description: 統一發布管線：任何頻道的「最後一哩」。執行 assemble → validate → upload → 更新 index。 支援三個頻道：taiwan-stories（A-G prefix）、botany（B prefix）、ancient-myths（AM/TW prefix）。 當教師提到發布、組裝上傳、跑管線、publish、assemble and upload 時觸發。
triggers:
  - 發布
  - 組裝上傳
  - 跑管線
  - publish
  - assemble and upload
  - 組裝並上傳
platforms:
  - cowork
  - claude-code
requires_args: true
version: 1.0.0
created: 2026-03-29
---

# skill: publish-pipeline — 統一發布管線

任何頻道的「最後一哩」：assemble → validate → upload → 更新 index.yaml。
所有組裝腳本已共用 `assemble-base.js`，本技能負責路由到正確的腳本與路徑。

---

## 預授權操作

以下操作已獲得完整預授權，AI 必須直接執行，不得逐一詢問：

- Node.js 腳本執行（assemble-*.js）
- Google Drive 上傳（透過 gws CLI）
- Repo 內 index.yaml / project.yaml 更新
- 檔案讀取與寫入

---

## 頻道路由表

| 頻道 ID | ID 格式 | 組裝腳本 | stories 根目錄 | index.yaml | project.yaml |
|---------|---------|---------|---------------|------------|-------------|
| taiwan-stories | A001~G999 | `assemble-story.js` | `stories-of-taiwan/stories/` | `stories-of-taiwan/index.yaml` | `stories-of-taiwan/project.yaml` |
| botany | B001~B030 | `assemble-botany.js` | `botany-grade5/stories/` | `botany-grade5/index.yaml` | `botany-grade5/project.yaml` |
| ancient-myths | AM001~AM025, TW01~TW99 | `assemble-ancient-myths.js` | `ancient-myths-grade5/stories/` | `ancient-myths-grade5/index.yaml` | `ancient-myths-grade5/project.yaml` |

所有路徑前綴：`workspaces/Working_Member/Codeowner_David/projects/`

---

## 參數解析

教師可能的觸發方式：

```
「發布 B008」
「組裝上傳 AM006」
「publish A013」
「跑管線 stories/B008」
「組裝並上傳 ancient-myths AM006」
```

**AI 判斷邏輯：**

1. 從指令中提取 story ID（A~G###、B###、AM###、TW##）
2. 根據 ID prefix 自動判斷頻道：
   - `A~G` + 3 位數 → taiwan-stories
   - `B` + 3 位數 → botany（注意：B 同時匹配 taiwan-stories 的 B-INDIGENOUS，需看數字範圍。B001~B030 = botany，B1XX+ = taiwan-stories）
   - `AM` + 3 位數 → ancient-myths
   - `TW` + 2 位數 → ancient-myths（島嶼插曲）
3. 若教師給了完整路徑（如 `stories/B008`），直接使用
4. 若有歧義（如「B005」可能是 botany 或 taiwan-stories B block），詢問教師

**版本旗標：** 教師說「第二版」「v2」時，加入 `--version=v2`

---

## 執行流程

### Step 1 — 定位故事目錄

根據頻道路由表 + story ID，組合完整路徑：

```
{project_root}/stories/{block_dir}/{story_id}/
```

- taiwan-stories：block_dir 依 ID 首字母（A→A-origins, B→B-indigenous, ...）
- botany / ancient-myths：直接 `stories/{story_id}/`（或 `stories/{block_dir}/{story_id}/`，需檢查哪個存在）

**驗證：** 確認目錄存在且包含必要的 .md 檔案。

### Step 2 — 執行 assemble（含圖片壓縮）

```bash
node publish/scripts/assemble-{channel}.js {story_dir} --pdf --upload [--version=v2]
```

腳本會自動執行以下流程（含壓縮）：

```
Gemini 下載圖片（~/Downloads/）
     ↓
[compress-image.js] 壓縮為 JPEG（quality=82, max=1600px）
     ↓
[assemble-base.js]  base64 內嵌 → 組裝 HTML
     ↓
[html-to-pdf.js]    生成 PDF
     ↓
[gws CLI]           上傳 Google Drive
```

壓縮引擎優先級（自動偵測）：
1. `sips`（macOS 系統內建，無需安裝）
2. `magick`（ImageMagick v7+）
3. `convert`（ImageMagick v6）
4. 無可用工具 → 跳過壓縮並輸出警告，組裝流程繼續

壓縮輸出：`temp/compressed/<basename>-compressed.jpg`

**個別測試壓縮器：**
```bash
node publish/scripts/compress-image.js --detect
node publish/scripts/compress-image.js ~/Downloads/some-image.png
```

**注意：** 腳本已內建嚴格驗證（content paragraphs、fact table、images、chalkboard、teaching guide/narration）。驗證失敗會 exit code 2，AI 需回報錯誤並建議修正。

### Step 3 — 驗證輸出

確認腳本輸出：
- [ ] HTML 檔案存在且 > 10KB
- [ ] PDF 檔案存在且 > 50KB（若 --pdf）
- [ ] 腳本 exit code = 0
- [ ] Drive 上傳成功（log 中有 `[upload] OK`）

### Step 4 — 更新 index.yaml

讀取對應頻道的 `index.yaml`，加入/更新條目：

```yaml
{story_id}:
  title: "..."
  block: "..."
  created: 2026-XX-XX
  files:
    html: "{filename}.html"
    pdf: "{filename}.pdf"
  drive_uploaded: true
```

若為版本模式（v2），在原條目下嵌套：

```yaml
{story_id}:
  # ... 原有內容 ...
  latest_version: v2
  v2:
    files:
      html: "{filename}.html"
      pdf: "{filename}.pdf"
    created: 2026-XX-XX
```

### Step 5 — 更新 project.yaml

更新對應頻道的 `project.yaml`：
- `story_count.total` += 1（僅新增時，非覆蓋）
- `last_updated: 2026-XX-XX`

### Step 5b — 觸發 CreatorHub 網站部署

上傳成功後，觸發 GitHub Actions 部署：

```bash
gh workflow run deploy-channel.yml
```

~3 分鐘後新內容即出現在 CreatorHub 網站。若 `gh` 不可用，跳過（不阻擋），在回報中標記。

### Step 6 — 回報

輸出完成摘要，格式同各 daily pipeline 的 Step 7/8：

```
── publish-pipeline 完成 ──
  頻道：{channel_name}
  課號：{story_id} — {title}
  HTML：{html_path}
  PDF：{pdf_path}
  Drive：已上傳 ✓ / 跳過
  Index：已更新 ✓
  Project：story_count = {new_count}
```

---

## 與 daily pipeline 的關係

各 daily pipeline（story-daily / botany-daily / ancient-myths-daily）的 Step 5-7（組裝 + 上傳 + 歸檔）可改為呼叫本技能：

```
Step 5-7: 執行 publish-pipeline --channel {channel} --story-id {ID}
```

這不是強制替換——daily pipeline 可以繼續直接呼叫 assemble 腳本。publish-pipeline 的價值在於：
1. 單獨執行「最後一哩」（素材已就緒，只需組裝上傳）
2. 統一的 index.yaml / project.yaml 更新邏輯
3. 跨頻道的一致操作介面

---

## 錯誤處理

| 狀況 | 處理 |
|------|------|
| 故事目錄不存在 | 回報路徑錯誤，列出該頻道現有的故事 ID |
| 必要 .md 檔案缺失 | 回報缺失清單，建議用對應的 daily pipeline 補齊 |
| 驗證失敗（exit 2） | 回報具體驗證錯誤，建議修正方向 |
| 黑板畫未找到 | 提示教師先用 Gemini 生成並下載到 ~/Downloads/ |
| gws 未連線 | 回報上傳跳過，HTML/PDF 已存本地，提示 `gws auth login` |
| index.yaml 不存在 | 建立新的 index.yaml |
