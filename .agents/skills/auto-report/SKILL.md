---
name: 結案報告自動化產出 (Auto Report Generation)
aliases:
  - "結案報告自動化產出"
description: 讀取實驗教育計畫資料，自動抓取 Google Drive 與本地紀錄，並生成美化版的 Markdown、HTML 與 PDF 結案報告，最後直接上傳至雲端。
---

# 結案報告自動化產出技能 (Auto Report Generator)

這項技能可以系統化地協助你將零散的研習文字紀錄與雲端檔案，自動轉化為具有華德福美學排版風格的專業結案報告。

## 執行流程 (Execution Steps)

當使用者呼叫此技能時，請作為 AI Agent 嚴格按照以下流程執行任務：

### 1. 蒐集與準備資料 (Data Collection)
- 透過 `gws drive files list` 工具抓取指定的 Google Drive 參考資料夾檔案（如無指定，預設查詢「114學年度實驗教育計畫辦理研習」）。
- 讀取本地專案資料夾下的「活動筆記」、「表單回饋」等紀錄。

### 2. 產出 Markdown 初稿 (Drafting)
- 讀取本技能目錄下的參考模板 `./templates/report_template.md` 以了解報告「擴寫邏輯」與「語氣要求」（需使用專業教育行政用語及避免第一人稱）。
- 綜合第一部分的資料，將梳理後的文本寫入本地 Markdown 檔案，檔名預設為 `[專案名稱]_結案報告.md`。

### 3. 網頁與 PDF 格式美化 (Beautification)
- **產出 HTML**：使用本技能目錄下的專用轉換腳本，將 Markdown 加上 TailwindCSS 與華德福視覺風格：
  ```powershell
  node C:\Users\user\waldorf-teacher-os\.agents\skills\auto-report\scripts\build_html.js <絕對路徑/輸入的.md檔> <絕對路徑/輸出的.html檔>
  ```
- **產出 PDF**：使用 Windows 內建的 Microsoft Edge 進行無頭瀏覽器列印轉換：
  ```powershell
  & "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --print-to-pdf="<絕對路徑/輸出的.pdf檔>" "file:///<絕對路徑/輸出的.html檔>"
  ```

### 4. 雲端自動上傳與歸檔 (Cloud Archiving)
- 詢問使用者（或從對話上下文擷取）要上傳的目標 Google Drive Folder ID。
- 依序使用 `gws drive +upload "<絕對路徑>" --parent "<Folder ID>"` 指令，將產出的 `.md`, `.html`, 及 `.pdf` 三個檔案全數上傳。
- 完成後回報上傳成功的檔案網址或檔名給使用者。
