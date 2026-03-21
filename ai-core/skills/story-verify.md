---
name: story-verify
description: >
  「臺灣的故事」品質檢查技能。對 story-writer 產出的三件套進行事實查核、敘事連貫性檢查、格式合規檢查。
  當教師提到檢查故事、品質確認、驗證故事、故事校對時觸發。
triggers:
  - 檢查故事
  - 品質確認
  - 驗證故事
  - story verify
  - 故事校對
  - 確認故事品質
requires_args: false
---

# skill: story-verify — 臺灣的故事・品質檢查

對三件套產出進行多維度品質檢查，確保有憑有據、敘事連貫、格式合規。

## 適用對象

David（管理員）。

## 根目錄

以 Repo 根目錄為基準。

## 讀取的檔案

1. `{workspace}/projects/stories-of-taiwan/stories/[區塊]/[ID]/content.md`
2. `{workspace}/projects/stories-of-taiwan/stories/[區塊]/[ID]/narration.md`
3. `{workspace}/projects/stories-of-taiwan/stories/[區塊]/[ID]/images.md`
4. `{workspace}/projects/stories-of-taiwan/stories/[區塊]/[ID]/raw-materials.md` — 對照素材包
5. `{workspace}/projects/stories-of-taiwan/index.yaml` — 前後篇脈絡

## 入口驗證（由 story-daily pipeline 強制執行）

啟動本技能前，必須確認以下條件全部滿足，否則回報 FAIL 並停止：

1. `stories/[區塊]/[ID]/content.md` 存在且字數 > 300
2. `stories/[區塊]/[ID]/narration.md` 存在
3. `stories/[區塊]/[ID]/images.md` 存在且至少包含 1 張主圖（含「來源」欄位）
4. `stories/[區塊]/[ID]/chalkboard-prompt.md` 存在且含 `## English Prompt` 段落

## 執行步驟

### Step 1 — 事實查核（Fact Check）

逐一檢查 content.md 中的每個史實錨點：

| 檢查項目 | 標準 | 結果 |
|----------|------|------|
| 每個核心事實有標註來源 | 必須 | PASS/FAIL |
| 來源連結可存取 | 建議（無法存取標記為「待確認」） | PASS/WARN/FAIL |
| 斷言性事實至少有兩個獨立來源 | 必須 | PASS/FAIL |
| 日期/地名/人名正確性 | 必須（交叉比對） | PASS/FAIL |
| 無 AI 幻覺（fabrication） | 必須（比對素材包） | PASS/FAIL |

### Step 2 — 敘事品質檢查

| 檢查項目 | 標準 | 結果 |
|----------|------|------|
| 故事本文 300-500 字 | 必須 | PASS/FAIL |
| 有具體人物或人的視角 | 必須 | PASS/FAIL |
| 有感官細節（看到/聽到/摸到） | 必須 | PASS/FAIL |
| 語言適合五年級（無過度抽象概念） | 必須 | PASS/WARN |
| 與前一篇有連結（非第一篇時） | 建議 | PASS/WARN |
| 不說教、不灌輸 | 必須 | PASS/FAIL |

### Step 3 — 說書稿檢查

| 檢查項目 | 標準 | 結果 |
|----------|------|------|
| 開場/本文/收尾三段完整 | 必須 | PASS/FAIL |
| 有語氣標註 | 必須 | PASS/FAIL |
| 有圖像展示時機標註 | 必須 | PASS/FAIL |
| 總朗讀時間 7-10 分鐘（估算） | 建議 | PASS/WARN |
| 有差異化提示 | 必須 | PASS/FAIL |

### Step 4 — 圖像清單檢查

| 檢查項目 | 標準 | 結果 |
|----------|------|------|
| 至少一張主圖 | 必須 | PASS/FAIL |
| 每張圖有來源與授權標示 | 必須 | PASS/FAIL |
| 圖像連結可存取 | 建議 | PASS/WARN |
| 有投影順序建議 | 必須 | PASS/FAIL |

### Step 5 — 產出品質報告

```markdown
# 品質檢查報告：[ID] [標題]

## 總評
- 狀態：PASSED / NEEDS_REVISION / FAILED
- 檢查時間：[日期]

## 事實查核
- [逐項結果]

## 敘事品質
- [逐項結果]

## 說書稿
- [逐項結果]

## 圖像清單
- [逐項結果]

## 需修正項目（若有）
1. [具體修正建議]
2. ...
```

## 輸出格式

品質報告存入 `{workspace}/projects/stories-of-taiwan/reviews/[ID]-quality.md`。
同時更新 `reviews/quality-log.yaml`，追加一筆紀錄。

## 後續動作

- **PASSED**：自動進入 story-archive 歸檔
- **NEEDS_REVISION**：列出修正項目，等待教師決定是修正還是接受
- **FAILED**：不歸檔，需重新執行 story-writer

## 注意事項

- 品質檢查應由獨立的 AI 思路執行（建議使用 subagent），避免自己寫自己檢查的偏見
- 事實查核是最重要的——寧可標記「待確認」也不可放過未經驗證的斷言
- 所有路徑使用 `pathlib.Path()`
