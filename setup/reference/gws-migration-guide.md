---
aliases:
  - "GWS CLI 個人專案遷移指南"
tags:
  - setup
  - gws
  - migration
type: reference
---

# Google Workspace CLI 個人專案遷移指南

> **背景：** 原本所有教師共用 TeacherOS (TJOS) 的 Google Cloud 專案進行 gws CLI 認證。
> 為了讓每位教師擁有獨立的 Google Cloud 環境，請依照以下步驟建立自己的專案並完成遷移。
> **遷移完成後，TJOS 專案將被刪除。**

---

## 你需要準備的東西

- 你的 Google 帳號（用來登入 Google Cloud Console）
- 電腦上已安裝 gws CLI（如果還沒裝，執行 `npm install -g @googleworkspace/cli`）
- 約 15 分鐘

---

## 第一步：建立 Google Cloud 專案

1. 開啟瀏覽器，前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 用你的 Google 帳號登入
3. 點擊頁面上方的專案選擇器（通常顯示「選取專案」或現有專案名稱）
4. 點擊「**新增專案**」
5. 輸入專案名稱（建議：`我的名字-gws`，例如 `david-gws` 或 `佳芳-gws`）
6. 點擊「**建立**」
7. 等待專案建立完成（約 10 秒），確認已切換到新專案

---

## 第二步：啟用需要的 API

在新專案中，你需要啟用以下 API。最快的方式是直接點擊連結：

> **注意：** 點擊每個連結後，確認頁面上方顯示的是你剛建立的專案名稱。
> 如果不是，先用專案選擇器切換過去。

1. [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com) → 點擊「**啟用**」
2. [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com) → 點擊「**啟用**」
3. [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com) → 點擊「**啟用**」
4. [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com) → 點擊「**啟用**」
5. [Google Docs API](https://console.cloud.google.com/apis/library/docs.googleapis.com) → 點擊「**啟用**」
6. [Google Slides API](https://console.cloud.google.com/apis/library/slides.googleapis.com) → 點擊「**啟用**」
7. [Google Tasks API](https://console.cloud.google.com/apis/library/tasks.googleapis.com) → 點擊「**啟用**」
8. [People API](https://console.cloud.google.com/apis/library/people.googleapis.com) → 點擊「**啟用**」

---

## 第三步：設定 OAuth 同意畫面

1. 前往 [OAuth 同意畫面](https://console.cloud.google.com/apis/credentials/consent)
2. 選擇「**外部**」（External），點擊「建立」
3. 填寫以下欄位：
   - **應用程式名稱**：`GWS CLI`（或任何你喜歡的名字）
   - **使用者支援電子郵件**：選擇你的 email
   - **開發人員聯絡資訊**：填入你的 email
4. 其他欄位保持空白，點擊「**儲存並繼續**」
5. 在「範圍」頁面，直接點擊「**儲存並繼續**」（不需手動新增範圍）
6. 在「測試使用者」頁面：
   - 點擊「**新增使用者**」
   - 輸入你自己的 Google 帳號 email
   - 如果你有第二個帳號也要用 gws，一併加入
   - 點擊「**儲存並繼續**」
7. 確認摘要，點擊「**返回資訊主頁**」

---

## 第四步：建立 OAuth 憑證

1. 前往 [憑證頁面](https://console.cloud.google.com/apis/credentials)
2. 點擊上方的「**+ 建立憑證**」→ 選擇「**OAuth 用戶端 ID**」
3. 應用程式類型選擇「**電腦版應用程式**」（Desktop app）
4. 名稱填入 `GWS CLI`（或任何你喜歡的名字）
5. 點擊「**建立**」
6. 在彈出視窗中，點擊「**下載 JSON**」
7. 將下載的檔案重新命名為 `client_secret.json`

---

## 第五步：放置憑證檔案並重新認證

### macOS / Linux

```bash
# 1. 備份舊的設定（以防萬一）
cp ~/.config/gws/client_secret.json ~/.config/gws/client_secret.json.bak

# 2. 將新的 client_secret.json 複製到 gws 設定目錄
cp ~/Downloads/client_secret.json ~/.config/gws/client_secret.json

# 3. 刪除舊的 token（舊專案的 token 已無法使用）
rm -f ~/.config/gws/token_cache.json
rm -f ~/.config/gws/credentials.enc

# 4. 重新登入
gws auth login
```

### Windows（PowerShell）

```powershell
# 1. 備份舊的設定
Copy-Item "$env:APPDATA\gws\client_secret.json" "$env:APPDATA\gws\client_secret.json.bak"

# 2. 將新的 client_secret.json 複製到 gws 設定目錄
Copy-Item "$env:USERPROFILE\Downloads\client_secret.json" "$env:APPDATA\gws\client_secret.json"

# 3. 刪除舊的 token
Remove-Item "$env:APPDATA\gws\token_cache.json" -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\gws\credentials.enc" -ErrorAction SilentlyContinue

# 4. 重新登入
gws auth login
```

瀏覽器會開啟 Google 授權頁面，選擇你的帳號並允許所有權限。

---

## 第六步：驗證

執行以下指令確認認證成功：

```bash
gws gmail users getProfile --params '{"userId":"me"}'
```

如果看到你的 email 和訊息數量，就代表設定完成。

---

## 如果你有第二個 Google 帳號

如果你有兩個帳號需要使用（例如個人帳號 + 公用帳號），第二個帳號需要獨立的設定目錄：

### macOS / Linux

```bash
# 1. 建立第二帳號的設定目錄
mkdir -p ~/.config/gws-second

# 2. 複製同一份 client_secret.json 過去
cp ~/.config/gws/client_secret.json ~/.config/gws-second/client_secret.json

# 3. 用第二帳號登入
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-second gws auth login
```

### Windows（PowerShell）

```powershell
# 1. 建立第二帳號的設定目錄
New-Item -ItemType Directory -Path "$env:APPDATA\gws-second" -Force

# 2. 複製 client_secret.json
Copy-Item "$env:APPDATA\gws\client_secret.json" "$env:APPDATA\gws-second\client_secret.json"

# 3. 用第二帳號登入
$env:GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$env:APPDATA\gws-second"; gws auth login
```

授權時選擇你的第二個帳號。

---

## 常見問題

### Q: 授權頁面顯示「此應用程式未經驗證」

這是正常的。因為你的個人專案不需要通過 Google 驗證。點擊「**進階**」→「**前往 GWS CLI（不安全）**」即可繼續。

### Q: 授權時出現「存取權遭到封鎖：此應用程式的要求無效」

回到第三步，確認你已將自己的 email 加入「測試使用者」。

### Q: 我不確定自己有沒有裝 gws

在終端機執行：

```bash
gws --version
```

如果看到版本號（例如 `gws 0.22.5`），就是已安裝。
如果顯示 `command not found`，請執行：

```bash
npm install -g @googleworkspace/cli
```

### Q: 遷移後原本的資料會不見嗎？

不會。Google Cloud 專案只是認證管道，你的 Gmail、Drive、Calendar 等資料都在你的 Google 帳號中，與專案無關。

---

*建立日期：2026-04-15*
