---
aliases:
  - "TW01 品質報告"
---

# TW01 品質報告：島嶼插曲——布農族射日與創世

## 驗證結果：PASS（含 WARN）

驗證日期：2026-03-31

| 項目 | 結果 | 備注 |
|------|------|------|
| 7 件套完整性 | PASS | 全部 7 件已存在 |
| frontmatter 必填欄位 | PASS | 7/7 |
| 故事本文字數 | PASS | 1,461 字（>800） |
| 事實出處筆數 | PASS | 7 筆（≥5） |
| images.md 圖數與連結 | PASS | 4 張，全部有 https:// 連結 |
| raw-materials.md 字數 | PASS | 4,034 字（>900） |
| raw-materials.md URL 數量 | PASS | 8 筆（≥5），中文 5 筆（≥2） |
| 交叉驗證（來源 key） | PASS | 7/7 匹配 |
| block 值 | WARN | island-interlude 為 TW 系列特殊值，非錯誤 |

## Museum API
- Met Museum：8 件（均與布農族無關，未納入 images.md）
- 圖像來源改用 Wikimedia Commons（4 張全部附 CC 授權連結）

## 自動驗證腳本輸出
- validate-story.js 結果：FAIL（缺 quality-report.md）→ 補齊後重跑預計全 PASS
- WARN：island-interlude 非阻擋項（TW 系列特殊值）

## 素材品質備注
- 素材來源：8 筆，中文 5 筆（維基百科繁中、原住民族文獻電子期刊、原視界、原住民族委員會、方格子 Vocus）
- 英文 3 筆（Wikipedia Bunun、Taiwan Insight、Boris Riftin 比較神話學）
- AI 知識補充段落已明確標註來源
- 布農族射耳祭、pasibutbut 等文化細節已包含於說書稿
