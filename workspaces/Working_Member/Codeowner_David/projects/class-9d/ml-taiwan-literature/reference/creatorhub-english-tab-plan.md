---
aliases:
  - CreatorHub 英文化計畫
  - TL 英文 Tab
tags:
  - class/9d
  - subject/ml-taiwan-literature
  - type/plan
  - project/creator-hub
class: class-9d
subject: ml-taiwan-literature
type: plan
teacher: 林信宏
status: 待執行
created: 2026-04-15
---

# CreatorHub 臺灣文學頻道 — 英文摘要 Tab 計畫

## 目標

在 CreatorHub 的 `taiwan-literature-9d` 頻道頁加入 ZH/EN 語言切換 Tab。
EN 模式下，卡片顯示英文摘要，點擊導向 Google Drive 上的英文摘要文件。

不做完整英文 HTML 鏡像 — 英文版只提供摘要，用連結導向 Drive。

## 現狀

- 頻道頁：`https://waldorfcreatorhubdatabase.web.app/channel/taiwan-literature-9d.html`
- 由 `creator-hub/scripts/generate-site.js` 產生靜態 HTML
- 頻道設定：`creator-hub/data/channels.json`（key: `taiwan-literature-9d`）
- 目前無任何 i18n 機制
- 故事頁連結指向 Google Drive HTML 檔

## 方案

### 切換行為

| 模式 | 卡片標題 | 卡片描述 | 點擊連結 |
|------|---------|---------|---------|
| ZH（預設） | 中文標題（不變） | 現有欄位 | 現有 Drive HTML |
| EN | 英文標題 | 1-2 句英文摘要 | Drive 英文摘要文件 |

### 需要產出的內容

每個 Day（TL01-TL11）各一份：

1. **英文標題**（e.g. "Day 1 — Gateway: How to Enter a Story"）
2. **卡片摘要**（1-2 句，顯示在頻道頁卡片上）
3. **完整英文摘要文件**（~300-500 字，上傳 Drive）：
   - 本堂主題與教學意圖
   - 使用的文本與活動概述
   - DI 策略摘要
   - 教學反思亮點（有的話）

來源：`ml-taiwan-literature/content/lesson-0X-v*.md`

### 資料格式

新增 `creator-hub/data/i18n/taiwan-literature-9d-en.json`：

```json
{
  "channel": {
    "name": "Taiwan Literature Main Lesson (Grade 9) | David Lin",
    "description": "\"The People of This Island\" — From displacement to rootedness, from silence to voice. 8 days x 120 min with full lesson plans and teaching reflections."
  },
  "stories": {
    "TL01": {
      "title": "Day 1 — Gateway: How to Enter a Story",
      "summary": "Students encounter Zheng Qingwen's lyrical novella...",
      "driveUrl": "https://drive.google.com/file/d/XXXXX/view"
    }
  }
}
```

## 程式改動

**只改一個檔案 + 一個新增檔案：**

### 1. `creator-hub/scripts/generate-site.js`

修改 `generateChannelPage()` 函式：
- 讀取 i18n JSON（若該頻道存在對應檔案）
- Header 區加入 ZH / EN Tab 按鈕（Tailwind 樣式，與現有設計一致）
- 文字元素加 `data-zh` / `data-en` 屬性
- 卡片在 EN 模式多顯示一行 summary
- 卡片連結在 EN 模式指向 `driveUrl`
- 嵌入 ~40 行 vanilla JS：toggle + localStorage 記憶
- 僅對有 i18n 檔案的頻道啟用（其他頻道不受影響）

### 2. 新增 `creator-hub/data/i18n/taiwan-literature-9d-en.json`

英文摘要資料（標題 + 卡片摘要 + Drive URL）

### 不改動的東西

- `channels.json` 結構不動
- 其他頻道不受影響
- 現有中文版 story HTML 不動
- 部署流程不動

## 工作量估算

| 項目 | 時間 |
|------|------|
| generate-site.js Tab 機制 | ~1.5 小時 |
| i18n JSON + 英文摘要撰寫（8 Day x ~500 字） | ~2 小時 |
| 英文摘要上傳 Drive + 取得連結 | ~30 分鐘 |
| 本地測試 + 部署 | ~30 分鐘 |
| **合計** | **~4-5 小時** |

## 執行順序

```
Step 1 — 撰寫 8 份英文摘要（AI 初稿 → David 審）
Step 2 — 建立 i18n JSON + 修改 generate-site.js
Step 3 — 本地測試 Tab 切換
Step 4 — 上傳英文摘要至 Drive，取得 URL 填入 JSON
Step 5 — 部署
```

## 驗證

1. `node creator-hub/scripts/generate-site.js`
2. 瀏覽器開啟頻道頁 → Tab 按鈕出現
3. 點 EN → 文字切換、摘要顯示、連結導向 Drive
4. 點 ZH → 回到中文版
5. 重新整理 → localStorage 記住偏好
6. 其他頻道頁無 Tab（未受影響）
