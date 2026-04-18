# Channel Feature Page — 規格書

> 年鑑（Almanac）風格的頻道內頁規格。
> 對應設計原型：Claude Design handoff《Series Feature》（2026-04-18）。
> 適用所有頻道——每個頻道內頁共用同一版型，只有**資料**不同。

---

## 一、Skeleton 架構的編寫說明

頻道內頁的資料骨幹來自 `creator-hub/data/channels.json`。
每個頻道原本只有 6 個基本欄位（`folderName` / `name` / `description` / `prefix` / `season` / `icon`），
為了支援「雜誌專題」式的內頁，新增一個**選填**的 `feature` 區塊。

### 1.1 channels.json 完整欄位表

| 欄位 | 必填 | 說明 |
|------|------|------|
| `folderName` | ✓ | Google Drive 資料夾名稱（同步用） |
| `name` | ✓ | 頻道中文名稱，顯示在 index 卡片與內頁 hero |
| `description` | ✓ | 簡短描述，index 卡片 + 內頁 hero 副標 |
| `prefix` | ✓ | 主系列代號（A / AM / B / I / SH / TL / ...） |
| `season` | ✓ | `spring` / `summer` / `autumn` / `winter`，影響配色 |
| `icon` | ✓ | Material Symbol 圖標名稱（向下相容，新版暫不顯示，保留） |
| `sort` | ✕ | 排序方式 `modifiedTime`（預設）或 `storyId` |
| `feature` | ✕ | 內頁編輯內容（見 §1.2） |

### 1.2 `feature` 區塊 — 內頁編輯內容

全部**選填**，未填則自動用 fallback 文字：

```jsonc
"feature": {
  "tagline": "一座島嶼的呼吸",              // hero 斜體小標（建議 10 字內）
  "number": "No. 01",                       // hero 左上編號（預設從 prefix 推導）
  "titleEn": "Stories of Formosa",          // hero 英文副標
  "grade": "五年級",                         // hero meta 年級
  "seasonLabel": "秋之章",                   // hero meta 章節（預設依 season 自動帶）
  "intro": {
    "lead": "這是一本為華德福教師而編的臺灣地誌。",
    "body": "從島嶼誕生的地質詩篇，到原住民看待星空的方式——每一則故事都設計為可以被講述、被繪畫、被演出。"
  },
  "pullQuote": "不是把臺灣當成資料，\n而是把臺灣當成一位需要被傾聽的長者。",
  "subSeries": {
    "A":  { "label": "核心故事",  "description": "系列主幹——以敘事為核心的完整故事單元。",        "accent": "#3a5a3a" },
    "EN": { "label": "英文延伸",  "description": "English extensions — 英文延伸閱讀與雙語教材。",    "accent": "#6b4a2e" },
    "BT": { "label": "黑板畫指引","description": "Blackboard teaching — 步驟圖、構圖、色粉示範。",   "accent": "#8b3a2e" }
  }
}
```

### 1.3 子系列（Sub-Series）偵測邏輯

子系列**不需要手動列出單元**——產生器會自動從 `files.json` 的 `storyId` 解析：

- `storyId` 規則：`{字母前綴}{數字}`，例：`A001`、`BT001`、`EN007`、`TW01`
- 產生器會把同前綴的單元歸在同一子系列
- 若 channels.json 有對應的 `subSeries[前綴]`，用其中的 `label` / `description` / `accent`
- 若無，用 fallback：`label = "{prefix} 系列"`、`description = ""`、`accent = 季節色`

### 1.4 新增頻道的最小範本

只要頻道的 storyId 有固定前綴，連 `feature` 都可以先不填——版型會用預設。想漂亮一點，補上 `feature.tagline` + `feature.intro.lead` 就有 80% 效果。

```jsonc
"my-new-channel": {
  "folderName": "我的新頻道",
  "name": "我的新頻道",
  "description": "一句話描述這個頻道在做什麼",
  "prefix": "MNC",
  "season": "autumn",
  "icon": "star"
}
```

---

## 二、進入頻道後的目錄安排（Page Structure）

點開任何頻道卡片 → `/channel/{id}.html` → 依以下順序由上而下呈現：

### 2.1 區塊流程

```
┌──────────────────────────────────────────────────────────┐
│ TOPNAV     ← Waldorf Creator Hub    A·Feature    系列 每日 關於 │ 細線
├──────────────────────────────────────────────────────────┤
│                                                           │
│    No. 01 · A-SERIES · 五年級 · 秋之章 · 共 24 單元 · 3 分部   │
│                                                           │
│    《一座島嶼的呼吸》                                       │
│    臺灣的故事                 ← 斜體大標＋漸層陰影          │
│    Stories of Formosa                                     │
│                                     ← 右側：副標描述         │
├──────────────────────────────────────────────────────────┤
│ 序 · INTRODUCTION                                          │
│                                                            │
│  「大字斜體引言」     正文段落，首行縮排，兩欄對齊。           │
│                                                            │
├──────────────────────────────────────────────────────────┤
│ 「 引句（居中大字）                                         │
│    不是把臺灣當成資料，                                     │
│    而是把臺灣當成需要被傾聽的長者。」                         │
│                        — 編者的話                          │
├──────────────────────────────────────────────────────────┤
│ 分部目錄 · SUB-SERIES                                      │
│                                                            │
│ 01. A 系列 │ 02. EN 系列 │ 03. BT 系列     ← 點擊跳轉錨點    │
│ 核心故事   │ 英文延伸    │ 黑板畫指引                        │
│ 16 單元    │ 7 單元      │ 1 單元                            │
├──────────────────────────────────────────────────────────┤
│ A-SERIES · 16 單元                                    A     │ ← 子系列 header
│ 核心故事                                                    │
│ 系列主幹——以敘事為核心的完整故事單元                         │
│                                                            │
│  ┌────────┐  ┌────────┐  ┌────────┐                       │
│  │ 封面圖  │  │ 封面圖  │  │ 封面圖  │   ← 每排 3 張         │
│  │ [A-01] │  │ [A-02] │  │ [A-03] │     (UnitCard)        │
│  │ 特寫    │  │         │  │         │                     │
│  ├────────┤  ├────────┤  ├────────┤                       │
│  │ 類型/週 │  │ 類型/週 │  │ 類型/週 │                       │
│  │ 標題    │  │ 標題    │  │ 標題    │                       │
│  │ 副標    │  │ 副標    │  │ 副標    │                       │
│  │ 摘句    │  │         │  │         │                     │
│  │ 閱讀→ 🏷📒 │                                             │
│  └────────┘                                                │
├──────────────────────────────────────────────────────────┤
│ EN-SERIES · 7 單元                                    EN   │
│ 英文延伸                                                    │
│  ... 同樣的網格 ...                                         │
├──────────────────────────────────────────────────────────┤
│ BT-SERIES · 1 單元                                    BT   │
│ ... 同樣的網格 ...                                          │
├──────────────────────────────────────────────────────────┤
│ ← 返回年鑑      Per aspera ad astra       下一系列 →         │
└──────────────────────────────────────────────────────────┘

            ┌─ 右側 sticky rail ─┐
            │ 本輯分部            │
            │ 序                  │
            │ 01. A 系列          │
            │ 02. EN 系列         │
            │ 03. BT 系列         │
            │                     │
            │ 我的書籤            │
            │ ⊡ A-03 ⊡ EN-02     │
            └─────────────────────┘
```

### 2.2 各區塊說明

| 區塊 | 用途 | 資料來源 |
|------|------|----------|
| **Topnav** | 返回 index 的細線列 | 固定文字，無需設定 |
| **Hero** | 頻道主視覺（縮窄版，不佔太高） | `name` / `feature.tagline` / `feature.titleEn` / meta 條 |
| **Intro 序** | 雜誌式兩欄引言 + 正文 | `feature.intro.lead` + `feature.intro.body` |
| **Pull Quote 引句** | 居中大字金句，雜誌感 | `feature.pullQuote` |
| **Sub-Series Directory** | 分部目錄——編號＋名稱＋單元數 | 自動從 files.json + `feature.subSeries` 套名 |
| **Sub-Series Section** × N | 每個子系列獨立一段，有自己的 header + 單元網格 | files.json 自動分組 |
| **Unit Card** | 單元卡片（每排 3 張） | 每個 storyId 一張 |
| **Scrollspy Rail** | 右側固定錨點索引，顯示當前位置 + 書籤清單 | 自動產生 + localStorage |
| **Colophon 頁尾** | 返回鏈結＋座右銘＋下一系列 | 固定樣式 |

### 2.3 單元卡片（Unit Card）內容

每張卡片從上到下：

1. **封面圖** 200px 高（有 `/thumbnails/{storyId}.jpg` 就用它，否則條紋 placeholder）
2. **「特寫」絲帶**（若 `featured: true`，左上深色小條）
3. **代號徽章**（storyId，左下邊框小條，顏色用子系列 accent）
4. **分隔細線**
5. **Meta**：`{type} · {duration}`（小字灰色）
6. **主標題**（Noto Serif TC，20px）
7. **副標**（Cormorant 斜體）
8. **摘句**（選填，左側彩色邊條引述）
9. **底部**：左側「閱讀 →」、右側 📒 筆記 🔖 書籤 icon（**第二期功能**，可先留但不實作邏輯）

### 2.4 互動

| 元素 | 行為 |
|------|------|
| 分部目錄卡 | 點擊 → scroll 到對應子系列 section（`#sub-{id}`） |
| 右側 scrollspy | 隨滾動高亮當前子系列；點擊跳轉 |
| 單元卡 | 點擊 → 該單元的 `/stories/{storyId}.html` |
| 書籤 icon | 切換 localStorage 書籤（`wch-bookmarks`）— 第二期 |
| 筆記 icon | 開啟 modal 寫筆記，存 localStorage（`wch-notes`）— 第二期 |

---

## 三、套用原則

1. **版型統一**：所有頻道內頁共用同一個 `generateChannelPage()` 函數輸出的結構
2. **資料差異化**：差異只來自 `channels.json` + `files.json`
3. **季節配色**：`season` 欄位決定主色與背景，其他細節以季節色自動延展
4. **無資料亦可生成**：`feature` 全空時自動 fallback 出可讀版本，頻道能先上線再逐步補內容

---

## 四、維護

- 新增頻道：在 `channels.json` 加一筆，同步 Drive，跑 `node scripts/generate-site.js`
- 豐富內頁：補 `feature` 欄位，重跑產生器
- 新增子系列：在 Drive 資料夾放入新前綴的 storyId（如 `DR001`），同步後自動成為一個新子系列；想要漂亮標題就在 `feature.subSeries` 補 `"DR": { label, description, accent }`

---

*最後更新：2026-04-18*
