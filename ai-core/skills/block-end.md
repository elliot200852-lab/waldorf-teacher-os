---
name: block-end
description: 15堂主課程區塊結束後執行。收集教師觀察，產出教學反思筆記，為下一個弧線定位起點。
triggers:
  - 區塊結束
  - 做反思
  - block完成了
  - 這個block完成
  - 主課程結束
requires_args: true
args_format: "[班級代碼] (9c/8a/7a)"
---

# skill: block-end — 主課程區塊結尾反思

在 15 堂主課程區塊結束後，產出教學反思筆記，為下一個弧線定位起點。

## 參數

班級代碼（9c / 8a / 7a）。未提供則詢問。

## 根目錄

`/Users/Dave/Desktop/WaldorfTeacherOS-Repo/`

## 執行步驟

### Step 1 — 讀取本區塊記錄

1. `projects/class-[班級]/working/english-session.yaml`（本區塊的決策與產出記錄）
2. `projects/class-[班級]/working/students.yaml`（學生學習狀態）

**Reference 模組（必讀）：**

3. `ai-core/reference/pedagogy-framework.yaml`（15 堂弧線結構、年級發展邏輯）
4. `ai-core/reference/subject-english.yaml`（英文科哲學）

### Step 2 — 收集教師的課堂觀察

詢問教師（語音友善，分段問）：

1. 「這個區塊整體下來，你覺得學生的回應怎麼樣？」
2. 「哪個環節或活動最有效？」
3. 「哪個地方你覺得下次想要調整？」

AI 將口述整理為結構化記錄。

### Step 3 — 產出結尾反思筆記

---

**區塊結尾反思｜class-[班級]｜[日期]**

**本區塊完成了什麼**
（從 confirmed_decisions 和 output_files 摘取，加上教師補充）

**學生回應觀察**
（整理自教師口述）

**有效的部分**
（整理自教師口述）

**下次調整方向**
（整理自教師口述，附 AI 的具體建議 1–2 句）

**下一個弧線建議起點**
（根據本次反思 + 年級發展邏輯，提出 1–2 個方向供教師選擇）

---

### Step 4 — 儲存反思筆記

詢問：「確認將反思筆記附加至 `projects/class-[班級]/content/english/block-reflections.md` 嗎？（是 / 否）」

採附加邏輯，不覆蓋前次反思。

### Step 5 — 更新 english-session.yaml

自動生成 diff：

```yaml
english_session:
  last_updated: [今天日期]
  current_position:
    block_status: completed
  confirmed_decisions:
    - 區塊反思完成，下次起點：[教師選擇的方向]
  next_action:
    description: [下一個區塊或單元的起點]
```

詢問確認後寫入。

## 注意事項

- 反思筆記是給教師自己看的，語氣自由，可包含直覺觀察
- 不刪除舊的反思記錄，採附加邏輯（每次反思有日期標記）
- 若教師說「沒時間詳細說」，提供極簡版：只記錄「最有效的一件事」和「下次想調整的一件事」
- 若無學生回應記錄，提示：「可以用語音說說你對這個區塊的直覺感受，我幫你整理。」
