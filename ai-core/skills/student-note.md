---
name: student-note
description: 記錄特定學生的課堂觀察或個案備註，附加至students.yaml。保持客觀描述，不含評判。
triggers:
  - 記錄學生
  - 個案觀察
  - 記一下誰
  - 觀察記錄
  - 學生備註
requires_args: true
args_format: "[班級代碼] [學生識別] (例: 9c 5號 或 9c 小明)"
---

# skill: student-note — 學生觀察記錄

記錄特定學生的課堂觀察或個案備註，附加至 students.yaml 的對應欄位。

## 參數

班級代碼 + 學生識別（座號、代號或名字）。
例：「9C，第 5 號」「9C，小明」「9C，後排那個」

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 執行步驟

### Step 1 — 讀取學生資料

讀取：`{workspace}/projects/class-[班級]/working/students.yaml`

# {workspace} 路徑解析：
# 從 acl.yaml 取得當前使用者的 workspace 路徑。
# Codeowner：workspaces/Working_Member/Codeowner_David/
# 教師：workspaces/Working_Member/Teacher_{姓名}/

找到對應學生的條目。若找不到，詢問：「未找到這位學生，是否要先確認名單？」

### Step 2 — 收集觀察記錄（語音友善）

提示教師：「請描述你觀察到的情況——可以說行為、情緒狀態、與同學的互動，或你有什麼擔憂。用語音說就好，我來整理。」

AI 將教師口述整理為以下結構：

```yaml
observation:
  date: [今天日期]
  context: [課堂 / 下課 / 導師時間 / 其他]
  behavior_note: [行為觀察，客觀描述，不含評判]
  emotional_note: [情緒狀態，若有觀察]
  di_relevance: [與學習優勢或 A/B/C/D 分類的關聯，若有]
  follow_up: [跟進動作，若無填 null]
```

整理後顯示給教師確認，可即時修改。

### Step 3 — 確認並寫入

詢問：「確認將這筆觀察附加至 students.yaml 嗎？（是 / 否）」

確認後：
- 將記錄附加至該學生的 `observations` 欄位（不覆蓋舊記錄）
- 更新學生條目的 `last_observed` 日期

### Step 4 — 後續建議

記錄完成後，主動提示：

- 若觀察涉及學習困難：「需要對這位學生設計差異化支援嗎？說「查 DI」我來協助。」
- 若觀察涉及情緒或人際問題：「需要進入導師業務流程處理嗎？說「導師業務」繼續。」
- 若已累積 3 筆以上觀察：「這位學生已有多筆觀察記錄，需要整理成個案摘要嗎？」

## 注意事項

- 輸出中統一使用學生代號或座號，不使用真實姓名（隱私保護）
- 觀察記錄採附加邏輯，舊記錄永不刪除
- `behavior_note` 只寫客觀描述（「站起來走動了三次」），不含評判語言（不寫「很不專心」）
- 語音輸入：「記一下 9C 五號學生」「幫我記錄一下誰誰誰」即可觸發
