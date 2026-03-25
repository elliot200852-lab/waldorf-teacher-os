---
aliases:
  - "LINE 發送家長訊息"
name: send-line-message
description: >
  透過 LINE API 將撰寫好的訊息發送至班代群組的專屬技能。
  支援純文字與附檔（PDF 等）。附檔透過 gws 上傳至 Google Drive 取得公開連結，
  再以 LINE Flex Message 卡片呈現下載按鈕。
  強制套用 david-voice 產生內容，並在教師確認草稿後才會實際發送。
  觸發詞：發送家長Line 訊息、傳 LINE 給家長、傳 LINE 給班代、Line 通知家長。
trigger_keywords:
  - 發送家長Line 訊息
  - 傳 LINE 給家長
  - 傳 LINE 給班代
  - Line 通知家長
  - LINE
  - 傳 LINE
---

# skill: send-line-message — LINE 發送家長訊息

## 觸發條件

當教師表達「發送家長Line 訊息」、「傳 LINE 給家長」、「傳 LINE 給班代」、「Line 通知家長」，或在對話脈絡中要求透過 LINE 傳送訊息或檔案時觸發。

## 能力範圍

| 功能 | 支援 | 說明 |
|------|------|------|
| 純文字訊息 | 是 | 直接透過 LINE Push API 發送 |
| 附加檔案（PDF 等） | 是 | 先上傳至 Google Drive → 取得公開連結 → 以 Flex Message 卡片呈現下載按鈕 |
| 文字 + 附檔 | 是 | 同時發送，一次 API 呼叫 |

## 執行流程

### Step 1 — 釐清內容與判斷是否有附檔

1. 確認教師要通知家長的重點內容。若觸發時教師已一併給予，直接跳至第 2 步。
2. 判斷是否有附檔需求（教師提到「附上 PDF」「把檔案傳過去」「附檔」等）。
   - 有附檔 → 確認檔案路徑。
   - 無附檔 → 僅發送文字。
3. **強制讀取並套用 `{workspace}/skills/david-voice.md` 的語氣規準與寫作紀律**。
4. 撰寫訊息草稿，呈現給教師審閱。
5. 若有附檔，一併告知：「將附上 [檔名]，上傳至 Google Drive 後以卡片形式發送。」
6. 詢問：「草稿如上，請問要確認發送，還是需要修改？」

### Step 2 — 攔截與等待核可

**絕對禁止在教師確認前擅自發送訊息，必須有明確的中斷與等待。**
等待教師明確回覆「確認發送」、「發送」、「ok」、「是」或任何同意發送的指令。

### Step 3 — 上傳附檔與確認

若有附檔，先執行上傳，完成後回報教師：
- 上傳成功的檔名
- Drive 公開連結

等教師確認檔名與連結無誤後，再進入 Step 4 發送。
若無附檔，直接跳至 Step 4。

### Step 4 — 發送與回報

教師核可後，依據有無附檔選擇對應指令：

**純文字：**
```bash
cat << 'EOF' | python3 workspaces/Working_Member/Codeowner_David/scripts/send_line_message.py
[此處替換為草稿內容]
EOF
```

**文字 + 附檔（自動上傳至 Drive）：**
```bash
cat << 'EOF' | python3 workspaces/Working_Member/Codeowner_David/scripts/send_line_message.py --upload "/path/to/file.pdf"
[此處替換為草稿內容]
EOF
```

**文字 + 已有公開連結的附檔：**
```bash
cat << 'EOF' | python3 workspaces/Working_Member/Codeowner_David/scripts/send_line_message.py --file-url "https://..." --file-name "檔名.pdf"
[此處替換為草稿內容]
EOF
```

**僅附檔（無文字）：**
```bash
python3 workspaces/Working_Member/Codeowner_David/scripts/send_line_message.py --upload "/path/to/file.pdf"
```

檢查腳本的 stdout 執行結果：
- 若回應包含 `SUCCESS`，回報教師：「LINE 訊息已成功發送。」
- 若回應包含 `ERROR` 或 `FAILED`，將錯誤訊息如實提供給教師。

## 附檔說明

任何檔案（PDF、HTML、圖片等）都可以透過 gws 上傳到 Google Drive 取得公開連結，再以 LINE Flex Message 卡片發送。家長點擊按鈕即可開啟或下載。

**建議使用 PDF 格式。** PDF 任何人都能直接開啟，不需要 Google 帳戶。HTML 檔案雖可透過 Apps Script 渲染，但開啟時需要 Google 登入，家長未必有帳戶，不適合作為通知附檔。

## 跨平台注意

- macOS / Windows 均可執行（Python 3 + gws CLI）
- 路徑分隔符由 Python `pathlib` 處理，無需手動區分
