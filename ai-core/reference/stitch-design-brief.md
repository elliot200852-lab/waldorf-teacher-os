---
aliases:
  - "Stitch 設計規範"
  - "華德福視覺框架"
---

# Stitch Design Brief — WaldorfTeacherOS 通用視覺框架

> 用途：將 Markdown 內容貼入 Google Stitch 時，搭配本文件的 Prompt 模板，產出符合華德福美學的網頁。
> 維護者：David
> 建立日期：2026-03-19

---

## 1. 使用流程

```
Markdown 原稿 → 複製「Section 3 Prompt 模板」→ 將 Markdown 貼入指定位置 → 貼進 Stitch → 生成網頁
                                                                                    ↓
                                                                              瀏覽器分享 URL
                                                                                    ↓
                                                                              列印 / 匯出 PDF
```

**步驟細節：**

1. 在 TeacherOS 中完成 Markdown 原稿（家長信、課程大綱、活動通知等）
2. 開啟 [Google Stitch](https://stitch.withgoogle.com/)
3. 複製下方 Section 3 的 Prompt 模板
4. 將你的 Markdown 內容貼入模板的 `[CONTENT]` 區塊
5. 整段貼進 Stitch 的文字輸入框
6. Stitch 生成網頁後，微調細節（Voice Canvas 語音即可）
7. 交付：直接分享 URL，或用瀏覽器「列印 > 另存為 PDF」

---

## 2. 視覺設計規範（Design Tokens）

### 色彩系統

| 角色 | 色碼 | 用途 |
|------|------|------|
| 主色 — 暖土色 | `#8B6F47` | 標題、強調元素、按鈕 |
| 輔色 — 森林綠 | `#5B7553` | 次要標題、圖標、裝飾線 |
| 背景 — 米白 | `#FAF6F0` | 頁面底色 |
| 卡片背景 — 暖白 | `#FFFFFF` | 內容區塊底色 |
| 內文色 — 深褐 | `#3D3229` | 正文文字 |
| 淡裝飾 — 沙色 | `#E8DFD0` | 分隔線、邊框、背景裝飾 |
| 點綴 — 秋葉橘 | `#C47D3B` | 關鍵日期、CTA、重點標記 |

### 字型

- 標題：Serif 字型（Stitch 中選擇 Georgia, Playfair Display, 或 Noto Serif TC）
- 正文：圓潤的 Sans-serif（Noto Sans TC, Source Han Sans）
- 英文輔助：Lora（Serif）或 Inter（Sans-serif）
- 字級比例：標題 28–32px / 副標題 20–24px / 正文 16–18px / 註解 14px
- 行高：正文 1.75，標題 1.3

### 排版原則

- 最大內容寬度：720px（閱讀最佳寬度），置中
- 左右 padding：至少 24px（手機端 16px）
- 段落間距：1.5em
- 章節間距：3em
- 圖片圓角：8px，帶 2px 沙色邊框
- 卡片圓角：12px，帶微弱陰影（`box-shadow: 0 2px 8px rgba(0,0,0,0.06)`）

### 裝飾元素

- 頁面底色：不是平坦的單色，而是多層 CSS 漸層疊加模擬濕水彩暈染效果（米白 + 淡金 `#F5E6C8` + 腮紅 `#F0DDD5`，透明度 0.15–0.3）
- 頁首區域：較濃的水彩暈染帶（暖金漸入柔綠），文字浮於其上
- 章節分隔：水彩筆觸風格的 SVG 線條，或一排手繪風格的植物元素（小葉片、橡果、枝條剪影），森林綠低飽和
- 邊角裝飾：極低透明度（0.1–0.15）的植物插圖作為背景浮水印——壓花、蕨類印痕的感覺
- 引用區塊：左側不規則寬度的森林綠邊線（非完美直線）+ 水彩暈染米白底 + 斜體
- 重點框：水彩沙色暈染背景 + 手繪風格暖土色左邊框
- 圖片邊框：柔和不規則邊緣，仿佛照片放在水彩紙上，帶撕邊或暈邊效果
- 頁尾：學校名稱、學季、小字型聯絡資訊，上方以植物分隔線點綴
- 季節感：設計整體呼應當前季節——春天用嫩芽與淺綠，秋天用暖金與落葉

### 響應式要求

- 桌面：720px 內容寬度，兩側大量留白
- 平板：全寬 padding 24px
- 手機：全寬 padding 16px，字型不縮小
- 列印模式（@media print）：隱藏裝飾動畫、背景色轉白、確保分頁正確

---

## 3. Prompt 模板（直接貼入 Stitch）

```
Design a single-page web document with a warm, nature-inspired Waldorf school aesthetic. This is a parent-facing communication from a Waldorf school in Taiwan.

DESIGN DIRECTION:
- Color palette: warm earth tones — primary #8B6F47 (warm brown), secondary #5B7553 (forest green), background #FAF6F0 (cream), text #3D3229 (deep brown), accent #C47D3B (autumn orange). Use these colors with soft, blended transitions — never harsh solid blocks.
- Typography: Serif headings (Georgia or Playfair Display), rounded sans-serif body text (system font stack with Noto Sans TC for Chinese characters). Body text 17px, line-height 1.75
- Layout: single column, max-width 720px centered, generous whitespace, padding 24px minimum

WATERCOLOR & NATURE TEXTURE (critical — this defines the Waldorf identity):
- Page background: apply a subtle wet-on-wet watercolor wash texture using CSS gradients — soft, translucent layers of cream, pale gold (#F5E6C8), and blush pink (#F0DDD5) bleeding into each other, mimicking Waldorf wet watercolor painting. Use radial-gradient and linear-gradient with very low opacity (0.15–0.3) layered together.
- Header area: a larger, more saturated watercolor wash (warm gold fading to soft green) as background for the title area — as if painted by hand on wet paper. Edges should be soft and irregular, not geometric.
- Section dividers: instead of lines, use SVG or CSS shapes that resemble watercolor brush strokes — soft, organic, slightly transparent strokes in earth tones. Alternatively, use a row of hand-drawn style botanical elements (small leaves, acorns, or simple branch silhouettes) in muted forest green.
- Decorative corners or margins: subtle botanical illustrations or leaf motifs in very low opacity (0.1–0.15) as background decorations — visible but never competing with text. Think pressed flowers or fern prints.
- Card/callout backgrounds: instead of flat solid colors, use a watercolor-textured fill — soft, uneven color wash that looks painted rather than digital.
- Pull quotes or highlight boxes: wrap in a border that looks hand-drawn (slightly irregular stroke width, organic shape) rather than a perfect CSS rectangle.

NATURE ELEMENTS:
- Use inline SVG decorations: small leaf clusters, seed pods, or simple botanical line drawings as section markers
- Season-aware: the design should feel like the current season. For spring, use sprouting leaves and light greens; for autumn, use warm golds and falling leaf motifs. Include a CSS variable --season-accent that can be easily swapped.
- Footer decoration: a gentle horizon line with simple tree or hill silhouettes in very muted tones

OTHER DESIGN DETAILS:
- Quote blocks: left 3px irregular-width green border (not perfectly straight) with cream watercolor-wash background, italic text
- Highlight boxes: watercolor sand wash background with warm brown hand-drawn style left border
- Header: school name and semester info with a watercolor wash band behind it — soft edges, as if the text is floating on a painted surface
- Footer: compact contact info in small text, with a subtle botanical divider above
- Images (if any): display with soft, irregular borders — as if the photo is placed on watercolor paper with torn edges or a vignette fade
- Must be responsive (mobile-friendly) and print-friendly (@media print: simplify watercolor effects to solid pale tints, no animations, ensure readability)
- Overall feeling: like receiving a hand-painted letter on beautiful watercolor paper — the digital equivalent of Waldorf wet-on-wet painting. Warm, alive, organic. NOT corporate, NOT geometric, NOT digitally cold.

CONTENT (render this as the page body, preserving all headings, lists, and structure):

---

[在這裡貼入你的 Markdown 內容]

---

Generate a complete, self-contained HTML page with inline CSS. Include both Traditional Chinese and English font support. The page should feel like opening a thoughtfully designed letter, not a website.
```

---

## 4. Voice Canvas 微調用語參考

生成初版後，在 Stitch 的 Voice Canvas 中可用以下語音指令微調：

| 情境 | 語音指令範例 |
|------|-------------|
| 色調偏冷 | "Make the overall tone warmer, more earthy" |
| 字太小 | "Increase body text size to 18px" |
| 太擁擠 | "Add more whitespace between sections" |
| 加標頭 | "Add a header with the text '磊川華德福 — 第三學季通訊'" |
| 加頁尾 | "Add a footer with school contact info in small gray text" |
| 分隔線太硬 | "Replace the horizontal rules with organic leaf-shaped dividers" |
| 水彩太淡 | "Make the watercolor wash background more visible, increase opacity to 0.3" |
| 水彩太搶眼 | "Tone down the watercolor effects, reduce opacity to 0.1" |
| 加植物裝飾 | "Add subtle botanical leaf illustrations in the margins" |
| 換季節感 | "Switch the seasonal theme to autumn — warm golds, falling leaves" |
| 更手繪感 | "Make borders and dividers look more hand-drawn and irregular" |
| 想要不同版本 | "Show me three different color palette variations" |
| 準備列印 | "Add a print-friendly stylesheet — simplify watercolor to solid pale tints, white background" |
| 加日期標記 | "Highlight all dates in autumn orange (#C47D3B) with slight bold" |
| 中文字型 | "Use Noto Serif TC for headings and Noto Sans TC for body text" |

---

## 5. PDF 匯出注意事項

Stitch 本身不直接匯出 PDF，但生成的網頁可以透過瀏覽器列印功能轉換：

1. 在 Stitch 生成的頁面上按 `Cmd + P`（Mac）或 `Ctrl + P`（Windows）
2. 目的地選擇「另存為 PDF」
3. 邊界選擇「無」或「最小」（頁面本身已有 padding）
4. 勾選「背景圖形」以保留裝飾色塊

如果列印效果不理想，在 Stitch 中用語音指令：
- "Optimize this page for PDF printing — single page if possible"
- "Remove all hover animations and make backgrounds solid colors for print"

---

## 6. 擴展方向

此通用框架日後可衍生為專用模板：

- **家長信**：加入問候語區塊、簽名欄、學季時程表格
- **課程大綱**：加入週次表格、學習目標清單、差異化說明區
- **活動通知**：加入日期倒數、地圖嵌入、報名連結
- **學生作品展示**：加入圖片畫廊、學生反思引言

每個衍生模板只需修改 Section 3 的 Prompt，在 `DESIGN DIRECTION` 後加入該類型的特殊區塊需求即可。
