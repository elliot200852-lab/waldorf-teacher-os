---
aliases:
  - "LINE 發送家長訊息"
name: send-line-message
description: >
  透過 LINE API 將撰寫好的訊息發送至班代群組的專屬技能。
  強制套用 david-voice 產生內容，並在教師確認草稿後才會實際發送。
  觸發詞：發送家長Line 訊息、傳 LINE 給家長、傳 LINE 給班代、Line 通知家長。
trigger_keywords:
  - 發送家長Line 訊息
  - 傳 LINE 給家長
  - 傳 LINE 給班代
  - Line 通知家長
---

# skill: send-line-message — LINE 發送家長訊息

## 觸發條件

當教師表達「發送家長Line 訊息」、「傳 LINE 給家長」、「傳 LINE 給班代」、「Line 通知家長」時觸發。

## 執行流程

### Step 1 — 釐清重點與套用語氣

1. 詢問教師要通知家長的重點內容。若觸發時教師已一併給予該內容，則直接跳至第 2 步。
2. **強制讀取並套用 `{workspace}/skills/david-voice.md` 的語氣規準與寫作紀律**。
3. 根據提供的情境，運用 David 的專屬語態，撰寫一段將發送至家長群組的訊息草稿。
4. **將產出的草稿呈現給教師審閱**，並詢問：「草稿如上，請問要確認發送，還是需要修改？」

### Step 2 — 攔截與等待核可

**絕對禁止在教師確認前擅自發送訊息，必須有明確的中斷與等待。** 
等待教師明確回覆「確認發送」、「發送」、「ok」或任何同意發送的指令。

### Step 3 — 發送與回報

1. 教師核可後，呼叫 Python 腳本發送 LINE 訊息。可以使用 standard input (stdin) 的方式將草稿傳給腳本：
   
   在終端機執行：
   ```bash
   cat << 'EOF' | python3 workspaces/Working_Member/Codeowner_David/scripts/send_line_message.py
   [此處替換為草稿內容]
   EOF
   ```
2. 檢查腳本的 stdout 執行結果：
   - 若回應包含 `SUCCESS`，回報教師：「LINE 訊息已成功發送。」
   - 若回應包含 `ERROR` 或 `FAILED`，將錯誤訊息如實提供給教師。
