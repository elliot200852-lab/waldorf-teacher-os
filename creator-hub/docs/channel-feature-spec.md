---
aliases:
  - CreatorHub 頻道內頁規格書
  - Channel Feature 規格書
tags:
  - creator-hub
  - design-spec
  - documentation
type: 規格書
teacher: David
---

# Channel Feature Page — 規格書（blocks 版）

> 年鑑（Almanac）風格的頻道內頁規格。
> 對應設計原型：Claude Design handoff《Series Feature》（2026-04-18）。
> 2026-04-18 更新：改採 **blocks 模型** + **opt-in layout flag**；僅當頻道設定 `feature.layout: "magazine"` 時啟用。

---

## 一、設計脈絡：為什麼是 blocks，不是 sub-series

最初的原型把頻道分成「平行的 sub-series」（如 A 系列／EN 系列／BT 系列），但這與 TeacherOS 實際的教學架構**不符**：

- **臺灣的故事**：A／EN／BT 是**依臺灣歷史時序推進的章節**（起源 → 大航海邂逅 → 植物誌），不是平行支線。未來還會加入 C/D/E/F/G（荷西、鄭氏、清、日治、戰後）。
- **古文明神話**：AM001-021 全用同一個前綴，但內部有**四大文明 block**（印度／波斯／巴比倫／埃及）＋**島嶼插曲（TW）**。單看前綴完全分不出四個 block。
- **植物學**：B001-030 全用 B 前綴，內部有 Kovacs Botany 的**四個 block**，需要用編號範圍才能切分。

因此 **block** 取代 sub-series 成為基本單位：
- 一個 block 可能對應**單一前綴**（A = A-origins）
- 一個 block 可能是**前綴 + 編號範圍**（AM001-007 = 印度）
- 一個 block 可能是**指定 storyId 清單**（TW01, TW02, TW03, TW04 = 島嶼插曲）

---

## 二、Skeleton 架構的編寫說明（channels.json）

### 2.1 完整欄位表

| 欄位 | 必填 | 說明 |
|------|------|------|
| `folderName` | ✓ | Google Drive 資料夾名稱（同步用） |
| `name` | ✓ | 頻道中文名稱，顯示在 index 卡片與內頁 hero |
| `description` | ✓ | 簡短描述，index 卡片 + 內頁 hero 副標 |
| `prefix` | ✓ | 頻道**主前綴**（用於 meta 顯示，非分 block 用） |
| `season` | ✓ | `spring` / `summer` / `autumn` / `winter`，影響配色 |
| `icon` | ✓ | Material Symbol 名稱（legacy 版使用；magazine 版保留不顯示） |
| `sort` | ✕ | 排序方式 `modifiedTime` 或 `storyId`（block 內部排序） |
| `feature` | ✕ | 內頁編輯內容（見 §2.2） |

### 2.2 `feature` — 內頁編輯內容

```jsonc
"feature": {
  "layout": "magazine",            // ← 關鍵 opt-in 開關；缺省或其他值 = legacy
  "tagline": "這片土地的記憶",
  "titleEn": "Stories of Formosa",
  "grade": "五年級",
  "seasonLabel": "跨年度",          // 可選；預設從 season 帶「春/夏/秋/冬之章」
  "intro": {
    "lead": "這是一本為華德福教師而編的臺灣地誌。",
    "body": "依臺灣歷史時序推進的長期敘事——..."
  },
  "pullQuote": "不是把臺灣當成資料，\n而是把臺灣當成一位需要被傾聽的長者。",
  "blocks": [ /* 見 §2.3 */ ]
}
```

**重要**：
- `layout: "magazine"` 是 magazine 版的**開關**。沒有這行，版型會退回 legacy（原本的 gradient 頁）。
- 三條線（taiwan-stories / ancient-myths / botany）的 `feature.blocks` **已全部寫好**備用；但**只有 taiwan-stories 目前掛上 `layout: "magazine"`**，其他兩條等準備好再打開。

### 2.3 `feature.blocks` — 章節定義

每個 block 是一個物件，必填 `id`, `code`, `title`, `match`；其他選填。

```jsonc
{
  "id": "A-origins",                        // 唯一識別（不衝突即可），對應 URL anchor #block-<id>
  "code": "A",                              // 右側大字（scrollspy 與 section header 顯示）
  "title": "島嶼的誕生與最初的人",            // 主標
  "subtitle": "史前—1624 · 起源篇",          // 小標（選填，顯示在 label 與 TOC）
  "accent": "#3a5a3a",                      // block 專屬強調色
  "description": "在我們之前，誰住在這裡？...", // 2-3 句簡介
  "match": { "prefix": "A" }                // 選誰屬於這個 block（見 §2.4）
}
```

### 2.4 `match` 三種匹配模式

| 模式 | 範例 | 選出的 storyId |
|------|------|---------------|
| **純前綴** | `{ "prefix": "A" }` | 所有以 A 開頭 |
| **前綴+數字範圍** | `{ "prefix": "AM", "from": 1, "to": 7 }` | AM001-AM007 |
| **明列清單** | `{ "ids": ["TW01", "TW02"] }` | 只有 TW01 / TW02 |

**匹配順序**：先按 blocks 陣列順序過濾，每個 storyId 只會匹配第一個命中的 block。未匹配的 storyId 會自動被集中到「其他單元」block 於最後呈現（通常只在 Drive 尚未整理時出現）。

### 2.5 新增 block 的最小範本

要加入 C-dutch-spanish 區塊：

```jsonc
{
  "id": "C-dutch-spanish",
  "code": "C",
  "title": "紅毛城的時代",
  "subtitle": "1624-1662 · 荷蘭與西班牙統治",
  "accent": "#7a5a42",
  "description": "遠方來的人，在這裡留下了什麼？",
  "match": { "prefix": "C" }
}
```

加入 blocks 陣列、重跑 `node scripts/generate-site.js` 即生效。

---

## 三、進入頻道後的目錄安排（Page Structure）

當 `feature.layout === "magazine"`，頁面由上而下依序：

```
┌──────────────────────────────────────────────────────────┐
│ TOPNAV  ← Waldorf Creator Hub   A · Feature No. 01  系列… │
├──────────────────────────────────────────────────────────┤
│  No. 01 · A-SERIES · 五年級 · 跨年度 · 共 24 單元 · 3 章節 │
│                                                           │
│   《這片土地的記憶》                                       │
│   臺灣的故事              ← 斜體大標＋漸層陰影            │
│   Stories of Formosa                                     │
│                                   ← 右上：簡短副標         │
├──────────────────────────────────────────────────────────┤
│ 序 · INTRODUCTION                                          │
│  大字斜體 lead        正文 body（兩欄）                    │
├──────────────────────────────────────────────────────────┤
│ 「 pull quote 居中大字                                     │
│                        — 編者的話                          │
├──────────────────────────────────────────────────────────┤
│ 分部目錄 · SUB-SERIES                                      │
│ 01. A · 起源篇 │ 02. EN · 大航海 │ 03. BT · 植物誌         │
│ 島嶼的誕生...   │ 海上來的人     │ 島嶼的植物王國           │
│ 16 單元         │ 7 單元         │ 1 單元                   │
├──────────────────────────────────────────────────────────┤
│ block section × N                                          │
│   A · 起源篇 · 16 單元                                A    │
│   島嶼的誕生與最初的人                                     │
│   在我們之前，誰住在這裡？...                              │
│   ┌────┐ ┌────┐ ┌────┐                                   │
│   │ 單元卡 │ 單元卡 │ 單元卡 │（每排 3 張）                │
└──────────────────────────────────────────────────────────┘
      右側：sticky scrollspy rail，顯示當前 block 高亮
```

| 區塊 | 資料來源 |
|------|----------|
| Topnav | 固定，顯示 `feature.number` 或預設 `No. 01` |
| Hero | `name` / `feature.tagline` / `feature.titleEn` / meta 條 |
| Intro | `feature.intro.lead` + `feature.intro.body` |
| Pull Quote | `feature.pullQuote`（無則略去） |
| Directory | `feature.blocks[i]` 的 code / title / subtitle / units.length |
| Block Section × N | 每個 block 一段：header（code 大字、title、subtitle、description）+ unit grid |
| Rail | 所有 block 的 title，隨滾動高亮 |
| Colophon | 固定文字 |

### 3.1 互動

| 元素 | 行為 |
|------|------|
| Directory 卡 | 點擊 → scroll 到 `#block-<id>` |
| Rail 連結 | 點擊跳轉；滾動時自動高亮 |
| 單元卡 | 點擊 → `/stories/{storyId}.html` 或 Drive view |

### 3.2 單元卡片（Unit Card）

每張卡片：

1. **封面圖** 180px 高
   - 有 `/thumbnails/{storyId}.jpg` → 顯示真圖（由 `extract-thumbnails.js` 產出）
   - 無 → 深色對角斜紋 placeholder
2. **代號徽章**（storyId，左下）
3. **分隔線**
4. **Meta**：`{type} · {檔案大小}`
5. **主標題**（從 files.json 的 `title`）
6. **底部**：左側「閱讀 →」

---

## 四、切換 layout 的流程

### 目前狀態（2026-04-18）

| 頻道 | layout | 狀態 |
|------|--------|------|
| taiwan-stories | **magazine** | ✅ 使用新版 |
| ancient-myths | legacy | blocks 已備，等驗證後打開 |
| botany | legacy | blocks 已備，等驗證後打開 |
| island-myths-3rd | legacy | 未做 feature |
| shanhaijing-3rd | legacy | 未做 feature |
| taiwan-literature-9d | legacy | 未做 feature |

### 要把某頻道升級到 magazine

1. 確認 `feature.blocks` 已寫完並與實際 storyId 對齊
2. 在 channels.json 該頻道加上 `"feature": { "layout": "magazine", ... }`
3. `node scripts/generate-site.js` 重新產生
4. 瀏覽 preview 確認
5. commit + push 觸發 CI deploy

### 要退回 legacy

把 `feature.layout` 改成任何非 `"magazine"` 的值（或拿掉該欄位）即可。blocks 資料會留著，不影響 legacy 頁顯示。

---

## 五、封面圖（thumbnail）流程

**不需要手動放**，由 `extract-thumbnails.js` 自動跑 fallback chain：

1. 從 story HTML 內嵌 base64 圖抽出
2. Drive `pic-fetch` 資料夾按故事標題關鍵字比對
3. `{channelId}-default.jpg`（本地預設）
4. Drive `pic-fetch` 內的 others / default / fallback
5. 本地 watercolor 水彩 placeholder（最後退路）

正式站 deploy 前 CI 會跑 extract-thumbnails.js；本地 preview 若看到斜紋 placeholder 是因為本地沒跑過，部署後會正常顯示。

---

## 六、維護

- 新增頻道：`channels.json` 加一筆 → 同步 Drive → `node scripts/generate-site.js`
- 新增 block：在該頻道的 `feature.blocks` 陣列加一塊，定義 `match` → 重跑
- 豐富既有頻道：補 `feature.intro` / `feature.pullQuote` / `feature.titleEn` 等，重跑

---

*最後更新：2026-04-18（改採 blocks 模型 + opt-in layout）*
