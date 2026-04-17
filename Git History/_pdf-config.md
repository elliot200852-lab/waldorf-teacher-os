---
aliases:
  - "PDF 輸出設定"
---

# Git History PDF 輸出設定

## 工具方案
- **引擎**：Python reportlab（Platypus 排版模組）
- **字型策略**：雙字型——Helvetica（拉丁字母）+ DroidSansFallbackFull（CJK）
- **字型路徑**：`/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf`
- **關鍵技術**：`is_cjk()` 逐字元偵測 → `<font name="CJK">` 標籤包裹中文字元
- **腳本參考**：`generate_pdf_v2.py`（雙字型版本，勿用 v1）

## 輸出規格
- 頁面大小：A4
- 邊距：25mm 四邊
- 字級：內文 10pt / H2 15pt / H3 12pt
- 行距：1.7 倍
- 配色：標題 #4a6741（華德福綠）/ 內文 #1a1a2e / 輔助 #555555
- 頁首：左「WaldorfTeacherOS Git History」/ 右 日期版本
- 頁碼：置中底部

## 命名規則
`git-history_YYYY-MM-DD_v{N}.pdf`

## 輸出位置（重要）

**PDF 不進此資料夾。** 產出後直接丟以下任一處：
- 本地暫存：`~/Downloads/` 或 `/tmp/`（檢視完刪除）
- 永久留存：Google Drive（例如「TeacherOS-專案三層記憶 / Git History PDF」）

此資料夾只放 `.md`（週記正本、設定、附屬筆記）。`.gitignore` 已對 `Git History/*.pdf` 加守門。

## 注意事項
- weasyprint 在此環境無法安裝（proxy 限制）
- pandoc + xelatex 可用但 DroidSansFallback 缺拉丁字元，效果差
- **確定方案：reportlab 雙字型，不要再嘗試其他工具**
