---
name: art-in-teaching
description: >
  藝術作品融入教學素材管線。串接 Met Museum 與 Europeana API，搜集藝術作品、生成課堂投影畫廊、AI 教學加工、跨來源聚合、素材歸檔。
  當教師提到博物館素材搜尋、藝術作品查找、Met API、Europeana、課堂素材展示時觸發。
triggers:
  - 藝術作品融入教學
  - art in teaching
  - 博物館素材
  - 博物館 API
  - Met API
  - Europeana
  - 藝術作品
  - 找藝術品
  - 素材畫廊
  - 拉幾張畫
  - 做素材展示
  - museum
  - art search
  - 找博物館素材
requires_args: true
args_format: "<搜尋關鍵字> [--source met|europeana|both] [--count N] [--grade 7|8|9]"
---

# skill: art-in-teaching — 藝術作品融入教學素材管線

串接 Met Museum 與 Europeana API，搜集藝術作品 metadata，生成課堂投影用 HTML 畫廊，並提供 AI 教學加工、跨來源聚合與素材歸檔功能。

## 適用對象

所有教師。跨科目適用（英文、歷史、人文與社會、跨領域主題課程）。

## 參數

- `<keyword>`（必填）：搜尋關鍵字（英文），例如 "autumn landscape"、"van gogh"、"impressionism"
- `[--source met|europeana|both]`（選填）：來源，預設 `met`
- `[--count N]`（選填）：搜尋數量，預設 15
- `[--grade 7|8|9]`（選填）：年級，影響 Stage 3 的 AI 加工深度
- `[--europeana-key KEY]`（選填）：Europeana API Key，使用 europeana 或 both 時必填

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 來源優先邏輯

- **Met Museum**（預設/主要）：免費 CC0，無需 API Key，公共領域藝術品為主
- **Europeana**（備案）：需免費 API Key，歐洲文化遺產範圍更廣
- 教師未指定時，預設使用 Met；搜尋結果不足時建議加入 Europeana

## 五階段流程

Stage 1-2 為必要流程，Stage 3-5 為選配（教師決定是否繼續）。

---

### Step 0 — 前置檢查

1. 從 `ai-core/acl.yaml` 確認使用者身份與 workspace 路徑
2. 確認 Python 可用
3. 確認 PyYAML 已安裝
4. 若使用 Europeana，確認 API Key 已提供

```bash
# macOS / Linux
python3 -c "import yaml; print('PyYAML OK')"
```

```powershell
# Windows（PowerShell）
python -c "import yaml; print('PyYAML OK')"
```

> **跨平台注意：** AI 應先偵測可用的 Python 指令（`python3` 或 `python`）。

---

### Stage 1 — 搜尋（Search）

執行 Python 管線腳本，搜集藝術作品 metadata 並輸出統一 YAML。

```bash
# macOS / Linux — Met（預設）
python3 setup/scripts/museum_resource_pipeline.py "<keyword>" --source met --count 15

# macOS / Linux — Europeana
python3 setup/scripts/museum_resource_pipeline.py "<keyword>" --source europeana --europeana-key <KEY> --count 15

# macOS / Linux — 雙來源
python3 setup/scripts/museum_resource_pipeline.py "<keyword>" --source both --europeana-key <KEY> --count 15
```

```powershell
# Windows（PowerShell）— Met（預設）
python setup/scripts/museum_resource_pipeline.py "<keyword>" --source met --count 15

# Windows（PowerShell）— Europeana
python setup/scripts/museum_resource_pipeline.py "<keyword>" --source europeana --europeana-key <KEY> --count 15

# Windows（PowerShell）— 雙來源
python setup/scripts/museum_resource_pipeline.py "<keyword>" --source both --europeana-key <KEY> --count 15
```

**產出位置：** `temp/museum_<keyword>_<date>/`

產出檔案：

| 檔案 | 內容 |
|------|------|
| `museum-materials.yaml` | 統一格式的藝術作品 metadata（YAML，機器可讀） |

報告結果：

```
搜尋完成：<keyword>（來源：<source>）

產出位置：temp/museum_<keyword>_<date>/
- 作品數量：N 件
- 來源：Met Museum / Europeana / 雙來源
[若有 WARNINGS，列出]

要生成畫廊嗎？或直接進入 AI 教學加工？
```

---

### Stage 2 — 畫廊（Gallery）

生成課堂投影用 HTML 畫廊，並自動開啟瀏覽器預覽。

```bash
# macOS / Linux
python3 setup/scripts/museum_resource_pipeline.py "<keyword>" --source <source> --count <N> --gallery
# 開啟瀏覽器
open temp/museum_<keyword>_<date>/gallery.html
```

```powershell
# Windows（PowerShell）
python setup/scripts/museum_resource_pipeline.py "<keyword>" --source <source> --count <N> --gallery
# 開啟瀏覽器
Start-Process "temp\museum_<keyword>_<date>\gallery.html"
```

產出檔案：

| 檔案 | 內容 |
|------|------|
| `gallery.html` | 課堂投影用 HTML 畫廊（含圖片、標題、藝術家、年代） |

---

### Stage 3 — AI 教學加工（AI Enrichment）（選配）

教師確認後，由 Claude 在對話中直接加工。**不需要外部腳本。**

讀取 `temp/museum_<keyword>_<date>/museum-materials.yaml`，對每件作品進行教學加工：

1. **中文化**
   - `title_zh`：作品名稱中文翻譯
   - `desc_zh`：50-80 字作品說明（適合課堂口述）

2. **討論問題（三層次）**
   - 觀察層（看到什麼）：引導學生描述畫面元素
   - 感受層（感覺什麼）：連結個人經驗與情感
   - 思考層（想到什麼）：連結課程主題、歷史脈絡、跨學科概念

3. **ABCD 差異化建議**（依 `projects/_di-framework/project.yaml` 的雙軸矩陣）
   - **A 群（高能力 x 高動機）**：延伸研究任務、藝術家思想比較、跨作品分析
   - **B 群（低能力 x 高動機）**：鷹架式引導、視覺化筆記、配對討論、小步驟成功經驗
   - **C 群（高能力 x 低動機）**：選擇性挑戰、連結個人興趣、策展式任務、減少無效重複
   - **D 群（低能力 x 低動機）**：感官體驗優先、降低焦慮、簡化選擇題、從具體操作切入

加工結果寫入 `temp/museum_<keyword>_<date>/museum-materials-enriched.yaml`。

---

### Stage 4 — 跨來源聚合（Cross-source Aggregation）（選配）

若已使用 `--source both`，此步驟為自動去重與排序。
若先以 Met 搜尋、再追加 Europeana，可在此階段合併：

```bash
# macOS / Linux — 先跑 Met，再跑 Europeana，手動合併
python3 setup/scripts/museum_resource_pipeline.py "<keyword>" --source met --count 15
python3 setup/scripts/museum_resource_pipeline.py "<keyword>" --source europeana --europeana-key <KEY> --count 10
```

```powershell
# Windows（PowerShell）
python setup/scripts/museum_resource_pipeline.py "<keyword>" --source met --count 15
python setup/scripts/museum_resource_pipeline.py "<keyword>" --source europeana --europeana-key <KEY> --count 10
```

AI 讀取兩次產出的 YAML，合併去重後寫回統一檔案。

---

### Stage 5 — 歸檔至 Drive（Archive）（選配）

將素材歸檔至教師的 Google Drive。

```bash
# macOS / Linux
gws drive files create --name "<keyword>-museum-materials.yaml" \
  --parents "<DRIVE_FOLDER_ID>" \
  --upload-file "temp/museum_<keyword>_<date>/museum-materials.yaml"

gws drive files create --name "<keyword>-gallery.html" \
  --parents "<DRIVE_FOLDER_ID>" \
  --upload-file "temp/museum_<keyword>_<date>/gallery.html"
```

```powershell
# Windows（PowerShell）
gws drive files create --name "<keyword>-museum-materials.yaml" `
  --parents "<DRIVE_FOLDER_ID>" `
  --upload-file "temp\museum_<keyword>_<date>\museum-materials.yaml"

gws drive files create --name "<keyword>-gallery.html" `
  --parents "<DRIVE_FOLDER_ID>" `
  --upload-file "temp\museum_<keyword>_<date>\gallery.html"
```

---

## 快速指令對照

| 教師說 | 執行 |
|--------|------|
| 「找幾張梵谷的畫」 | Stage 1（Met，keyword: van gogh） |
| 「做素材展示」 | Stage 1 + 2（搜尋 + 畫廊） |
| 「拉幾張畫來備課」 | Stage 1 + 2 + 3（搜尋 + 畫廊 + AI 加工） |
| 「用 Europeana 找中世紀素材」 | Stage 1（Europeana，keyword: medieval） |
| 「兩個來源都搜」 | Stage 1（both） |
| 「上傳到 Drive」 | Stage 5 |

## 產出檔案總覽

| 階段 | 檔案 | 內容 |
|------|------|------|
| Stage 1 | `museum-materials.yaml` | 統一格式藝術作品 metadata |
| Stage 2 | `gallery.html` | 課堂投影 HTML 畫廊 |
| Stage 3 | `museum-materials-enriched.yaml` | AI 加工後的教學素材（含中文、討論題、DI 建議） |

所有產出位於 `temp/museum_<keyword>_<date>/`。

## API 來源

1. **Met Museum Collection API** — 免費、CC0、無需 Key
2. **Europeana Search API** — 免費、需註冊取得 Key

## 注意事項

- Met API 回傳的圖片為公共領域（CC0），可自由用於教學
- Europeana 的圖片授權各異，AI 會標註每件作品的 `rights` 欄位
- Stage 3 的 AI 加工在對話中完成，不需額外腳本
- 年級參數影響 Stage 3 討論問題的深度與詞彙難度
- Stage 2 畫廊生成後，AI 自動翻譯所有作品的中文標題與簡短描述，回寫 YAML 並重新生成畫廊。教師打開就有中文

## Repo 零膨脹原則

本技能的所有產出（YAML、HTML 畫廊、圖片、Teaching Notes）**不進 Git**。

- `temp/` 和 `**/museum_output/` 已加入 `.gitignore`
- 所有產出為**用完即棄**——上課投影完即可刪除
- 需要永久保留的素材 → Stage 5 上傳 Google Drive
- 畫廊中的 Teaching Notes 可用 Export All 按鈕匯出為 Markdown，自行保存

**教師不需要擔心素材搜集會讓 Repo 變大。**
