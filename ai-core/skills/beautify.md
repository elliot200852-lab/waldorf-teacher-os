---
name: beautify
description: >
  華德福美化文件輸出。將 Markdown 內容轉換為精美的華德福風格 HTML 文件，支援四季視覺切換（春/夏/秋/冬）。
  當教師提到美化文件、做漂亮版、HTML 輸出、精美版本、套模板時觸發。
triggers:
  - 美化
  - 做漂亮版
  - HTML 輸出
  - 精美版
  - beautify
  - 套模板
  - 漂亮版本
  - 美化輸出
  - 做精美的
  - 美化這份
requires_args: false
args_format: "[檔案路徑] [--season spring|summer|autumn|winter]"
---

# skill: beautify — 華德福美化文件輸出

將教師的 Markdown 內容轉換為精美的華德福風格 HTML 文件。以 Stitch 生成的模板為基礎，內建四季視覺系統（春/夏/秋/冬），完全不依賴外部服務。

## 適用對象

所有教師。適用於任何需要美化輸出的文件類型（家長信、課程大綱、活動通知、教學指南、學生作品展示等）。

## 參數

- `[檔案路徑]`（選填）：目標 .md 檔案路徑。省略時使用當前工作線最新的 .md 產出。
- `[--season spring|summer|autumn|winter]`（選填）：季節主題。省略時自動偵測當前月份。

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：嘗試 `git rev-parse --show-toplevel`。

## 四季視覺系統

| 季節 | 月份 | 主色 | 輔色 | 氛圍 |
|------|------|------|------|------|
| spring | 3-5 月 | `#6B7F5E` 新芽綠 | `#9B7BB0` 紫藤 | 嫩葉、花苞、輕盈 |
| summer | 6-8 月 | `#4A7C6F` 深翠綠 | `#C47D3B` 陽光橘 | 陽光、向日葵、活力 |
| autumn | 9-11 月 | `#8B6F47` 暖土棕 | `#5B7553` 森林綠 | 落葉、橡果、溫暖 |
| winter | 12-2 月 | `#5E6B7F` 靜灰藍 | `#7B6B60` 枯枝褐 | 霜雪、松枝、寧靜 |

季節自動偵測邏輯：
```
3-5 月 → spring
6-8 月 → summer
9-11 月 → autumn
12-2 月 → winter
```

## 執行步驟

### Step 0 — 前置確認

1. 確認基礎模板存在：`publish/templates/waldorf-base.html`
2. 確認設計規範存在：`ai-core/reference/stitch-design-brief.md`
3. 確認目標 .md 檔案存在（教師指定或從 session.yaml 推斷最新產出）

若基礎模板不存在，停下並提示教師。

### Step 1 — 讀取設計規範與模板

依序讀取：
1. `ai-core/reference/stitch-design-brief.md` — 完整設計規範（色碼、字型、排版、裝飾元素）
2. `publish/templates/waldorf-base.html` — HTML 骨架與四季 CSS 變數系統

關鍵理解：
- 模板中的 `{{佔位符}}` 是結構參考，不是字面替換——AI 應理解每個區塊的用途，根據內容智慧分配
- CSS 變數（`--primary`、`--secondary` 等）透過 `<html class="季節">` 自動切換
- 所有元件類別（`watercolor-wash-header`、`torn-edge`、`hand-drawn-border`）直接從模板複製使用

### Step 2 — 判斷季節與文件類型

**季節判斷：**
1. 教師指定 `--season` → 直接使用
2. 未指定 → 取當前月份自動偵測

**文件類型推斷（影響佈局選擇）：**

| 類型 | 偵測方式 | 佈局特點 |
|------|---------|---------|
| 家長信 | 檔名含 `notice`/`letter`/`通知`/`家長` | hero + 引用 + 敘事 + 日期重點框 + 簽名結語 |
| 課程大綱 | 檔名含 `syllabus`/`大綱`/`規劃` | hero + 多段敘事 + 表格/清單重點框 |
| 活動通知 | 檔名含 `activity`/`event`/`活動` | hero + 日期重點框 + 短敘事 |
| 教學指南 | 檔名含 `guide`/`指南`/`教案` | hero + 多段敘事 + 步驟清單 |
| 通用 | 以上皆不符 | hero + 敘事（依內容結構自動分配） |

### Step 3 — 讀取 .md 內容

讀取目標檔案，識別以下結構元素：
- `# h1` → 映射到 hero 標題
- `## h2` → 映射到章節標題
- `> blockquote` → 映射到 pull quote
- 含日期的清單 → 映射到 highlight box
- 正文段落 → 映射到 narrative section
- 簽名行（最末的姓名/職稱） → 映射到 closing signature

### Step 4 — 生成 HTML

**核心原則：**
- 生成完整的 self-contained HTML 檔案（單一檔案，inline CSS + CDN 引用）
- `<html class="對應季節">` 設定正確的季節 class
- 從 `waldorf-base.html` 複製 CSS 定義（四季變數、watercolor-wash、torn-edge 等所有類別）
- 從 `waldorf-base.html` 複製佈局結構，根據內容選擇需要的區塊
- **不使用模板中的佔位符做字面替換**——而是理解每個區塊的設計意圖，將 .md 內容智慧分配

**定案字級與間距（2026-03-19 David 確認，不可自行變更）：**

| 元素 | 字級 | 行高 |
|------|------|------|
| 正文段落（drop-cap / body） | 18px | 1.6 |
| 章節標題 h3 | text-xl | — |
| 小標題 h4 | 18px | — |
| 列表子項 | 17px | 1.55 |
| 重點框內文 | 18px | 1.5 |
| 重點框標題 | 18px | — |
| 結語 | text-lg | — |

| 元素 | 間距規格 |
|------|---------|
| main 容器 | max-w-[900px], px-8, py-6 |
| hero section | mb-6, header p-5 mb-3 |
| 分隔線 | gap-3, py-3, icon text-sm |
| 重點框 | px-5 py-3, my-4 |
| 議程/敘事段落 | mb-6, 項目 space-y-3 |
| 結語 | mb-4, py-3 |
| 頁尾 | mt-4, pb-6, gap-3 |

**區塊選用規則：**
- hero section → **必用**（每份文件都有標題區）
- divider → **必用**（季節裝飾分隔線）
- pull quote → **有 blockquote 時使用**
- narrative section → **有正文段落時使用**（可多段）
- highlight box → **有重要清單或日期時使用**
- bento grid → **有圖片時使用**（無圖片則跳過）
- closing → **有簽名或結語時使用**
- footer → **必用**

**季節裝飾圖標對照：**

| 季節 | 主圖標 | 分隔線圖標 |
|------|--------|-----------|
| spring | `eco` | `local_florist` |
| summer | `sunny` | `filter_vintage` |
| autumn | `park` | `eco` |
| winter | `ac_unit` | `spa` |

### Step 5 — 預覽

1. 建立暫存目錄（若不存在）：

```bash
# macOS / Linux
mkdir -p temp/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path temp/
```

2. 存入暫存檔案：`temp/beautify-{原始檔名}-{timestamp}.html`

3. 開啟瀏覽器預覽：

```bash
# macOS
open "temp/beautify-{filename}.html"

# Windows (PowerShell)
Start-Process "temp\beautify-{filename}.html"
```

4. 詢問教師：「已在瀏覽器中開啟預覽。滿意嗎？要調整什麼？」

5. 若教師要求調整，修改 HTML 後重新存檔並刷新預覽。

### Step 6 — 格式選擇與輸出

教師確認預覽滿意後：

1. **詢問輸出格式**：「要輸出哪種格式？」
   - (1) 僅 HTML
   - (2) 僅 PDF
   - (3) 兩者都要

2. **依選擇執行：**

   **HTML 輸出：**
   - 存入對應的 content/ 資料夾
   - 命名規則：`{原始檔名}-美化版.html`

   **PDF 輸出（自動化，不再手動 Cmd+P）：**
   - 確認暫存 HTML 存在（Step 5 產生的 temp/ 檔案）
   - **預設以自然版面生成 PDF**（不加 `--fit-page`），讓內容以最舒適的視覺呈現：
     ```bash
     node publish/scripts/html-to-pdf.js <html-path> <pdf-path>
     ```
   - PDF 命名規則：`{原始檔名}-美化版.pdf`
   - 生成後開啟 PDF 讓教師預覽
   - **最後詢問**：「PDF 已生成。如果需要壓縮到特定頁數（例如一頁），告訴我，我會個案處理。」
   - 若教師要求壓縮：
     - 壓成一頁 → `node publish/scripts/html-to-pdf.js <html-path> <pdf-path> --fit-page`
     - 填滿兩頁 → `node publish/scripts/html-to-pdf.js <html-path> <pdf-path> --fit-page --pages=2`
     - 可先用 `--dry-run` 量測再決定策略

   **兩者都要：**
   - 先存 HTML，再從該 HTML 生成 PDF（同上流程）

3. **詢問上傳**：「要上傳到 Google Drive 嗎？」
   - 若要：使用 GWS CLI 上傳所選格式的檔案到對應的 Drive 資料夾

### fit-page 參數說明

| 參數 | 說明 |
|------|------|
| `--fit-page` | 自動調整間距，讓內容填滿目標頁數 |
| `--pages=N` | 目標頁數（預設 1），搭配 `--fit-page` |
| `--dry-run` | 僅量測，輸出 JSON 不生成 PDF |

### dry-run JSON 欄位

| 欄位 | 說明 |
|------|------|
| `scale` | 間距縮放倍率（< 1 壓縮，> 1 放大） |
| `font_scale` | 字級縮放倍率（僅多頁模式 > 1） |
| `squeeze_level` | `comfortable`（>= 0.80）/ `tight`（>= 0.65）/ `very_tight`（< 0.65） |
| `recommendation` | `ok` 或 `suggest_2_pages` |

## 注意事項

- 全程使用繁體中文
- 生成的 HTML 依賴 CDN（Tailwind、Google Fonts）——離線環境無法正確渲染
- 圖片：若 .md 中無圖片引用，不要自行插入圖片，用 Material Icons 作為裝飾替代
- 中文字體 fallback 鏈已內建：Noto Sans TC → PingFang TC → Microsoft JhengHei → sans-serif
- @media print 樣式已內建在模板中，PDF 列印時自動套用（白底、隱藏導航、避免切斷內容）
- PDF 生成依賴 Puppeteer（首次使用需 `npm install puppeteer`）
- PDF 版面規格固定於 `publish/scripts/html-to-pdf.js`，修改需經 David 確認
- 若 Puppeteer 未安裝，AI 應提示安裝指令並在安裝後重試
- 此技能適用於所有 AI 平台（Claude Code、Gemini、ChatGPT）——無終端機的 AI 可跳過 Step 5 的瀏覽器開啟與 PDF 自動生成，改為直接輸出 HTML 內容
