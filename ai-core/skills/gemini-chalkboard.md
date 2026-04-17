---
name: gemini-chalkboard
description: >
  Gemini 黑板畫生成共用技能。12 步標準化流程：開啟 Gemini → 貼入 prompt → 等待生成 →
  下載 → 圖片內容驗證 → 重命名。三個 daily pipeline（story / ancient-myths / botany）
  共用此技能，不再各自重複實作。
triggers: []
requires_args: true
version: 1.0.0
created: 2026-03-30
platforms: [claude-code, cowork]
---

# skill: gemini-chalkboard — 黑板畫生成（共用）

所有頻道的 Gemini 黑板畫生成統一流程。由各 daily pipeline 的黑板畫步驟呼叫。

**不可獨立觸發**——此技能只在 daily pipeline 內部被引用。

---

## 預授權操作

此步驟已完全預授權，AI 直接操作，不詢問教師。全程零確認。
若出現任何「Allow browser action」提示，自動允許。

---

## 頻道路由表

| ID 前綴 | 頻道 | 檔名前綴 | 檔名範例 |
|---------|------|---------|---------|
| A, C~G + 3 位數 | taiwan-stories | `AssemblyStory` | `AssemblyStory-A014-chalkboard.png` |
| BT + 3 位數 | taiwan-stories | `AssemblyStory` | `AssemblyStory-BT001-chalkboard.png` |
| EN + 3 位數 | taiwan-stories | `AssemblyStory` | `AssemblyStory-EN001-chalkboard.png` |
| AM + 3 位數 | ancient-myths | `AncientMyths` | `AncientMyths-AM007-chalkboard.png` |
| TW + 2 位數 | ancient-myths | `AncientMyths` | `AncientMyths-TW01-chalkboard.png` |
| B + 3 位數（001~030） | botany | `Botany` | `Botany-B008-chalkboard.png` |

**AI 自動判斷：** 根據 `STORY_ID` 前綴決定頻道與檔名前綴，不需呼叫端指定。
**注意：** B-encounter 區塊使用 `EN` 前綴（非 `B`），避免與 Botany 衝突。

---

## 呼叫參數

由各 daily pipeline 傳入：

- **STORY_ID**：課號（A014 / AM007 / B008）
- **STORY_DIR**：故事目錄完整路徑（含 chalkboard-prompt.md）
- **VERSION**：版本標記（null 或 "v2"）——影響 Step 12 的檔名

---

## 技術規範

- **瀏覽器工具**：完全使用 `mcp__Claude_in_Chrome__*`（CDP 瀏覽器擴充套件）
- **禁止**使用 `mcp__computer-use__*`（排程模式下無使用者在場，呼叫必定逾時）
- **Prompt 注入方式**：在頁面 JS 中 dispatch `ClipboardEvent('paste')` + `InputEvent('input')`，繞過 OS clipboard 授權

---

## 操作流程（12 個強制子步驟）

### Step 1 — 讀取 prompt

讀取 `{STORY_DIR}/chalkboard-prompt.md` 中的 `## English Prompt` 段落。

### Step 2 — 組合完整 prompt

第一行寫 `請你生成一張圖片`，空一行，接英文 prompt 全文。

```
請你生成一張圖片

[English prompt 全文]
```

**重要：** 此中文前綴觸發 Gemini 的圖片生成模式，不可省略。

### Step 3 — 開啟 Gemini

使用 `mcp__Claude_in_Chrome__tabs_context_mcp`（`createIfEmpty: true`）取得 tab，再 `navigate` 到 `https://gemini.google.com`。

→ **截圖確認頁面已載入**

### Step 4 — 確認 Pro 模式

確認畫面中可見「Pro」標示。

- 若看不到：點擊模型選擇器（右上角或對話框右側的下拉選單）切換到 Pro
- → **截圖確認「Pro」標示可見**

### Step 5 — 選擇圖像生成工具

點擊對話框內的「工具」選單按鈕（齒輪圖示或「工具」文字）→ **截圖確認選單已展開** → 點擊選單中的「建立圖像」選項 → **截圖確認已選取**。

若找不到「工具」按鈕，嘗試直接點擊首頁的「生成圖片」快捷按鈕（pill-shaped 按鈕）。

### Step 6 — 點擊文字輸入區

點擊文字輸入區，確認游標已就位。

### Step 7 — 注入 prompt

使用 `javascript_tool` 注入 Step 2 組合的完整 prompt：

```javascript
const prompt = `請你生成一張圖片\n\n[英文 prompt 全文]`;
const editor = document.querySelectorAll('[contenteditable="true"]')[0];
editor.focus();
// 方法一：ClipboardEvent paste（模擬貼上，繞過 OS clipboard 授權）
const dt = new DataTransfer();
dt.setData('text/plain', prompt);
editor.dispatchEvent(new ClipboardEvent('paste', {
  clipboardData: dt, bubbles: true, cancelable: true
}));
// 若 paste 無效（文字未出現），改用 InputEvent
editor.dispatchEvent(new InputEvent('input', {
  inputType: 'insertFromPaste', data: prompt, bubbles: true
}));
```

**驗證：** 用 `javascript_tool` 讀取 `editor.textContent.length`，若為 0 → 重試最多 3 次。

**互動模式備案：** 若 JS 注入全部失敗，可改用 `type` action 直接輸入（較慢但可靠）。

### Step 8 — 送出

用 `javascript_tool` 點擊送出按鈕（搜尋 aria-label 含「傳送」或 type="submit" 的按鈕），或按 Enter。

→ **截圖確認訊息已送出**

### Step 9 — 等待圖片生成

每 5-10 秒執行以下兩個動作：

1. **`javascript_tool`**：`window.scrollTo(0, document.body.scrollHeight)` — **必須往下捲動**，Gemini 的圖片在頁面底部生成，不捲動無法確認
2. **截圖或 `get_page_text`**：檢查是否仍顯示 "Creating your image..." 或 "正在建立"

最多等 **60 秒**（6 次）。每次都要捲動，不能只在原位盲等。

判斷標準：截圖中出現完整圖片（非載入動畫）。

### Step 10 — 下載

圖片出現後：

1. 點擊圖片放大
2. 點擊右上角下載按鈕（向下箭頭圖示）
3. 等待 3 秒
4. → **截圖確認出現「正在下載」提示或下載完成**

### Step 11 — 圖片內容驗證（強制，不可跳過）

**目的：** Gemini 偶爾會生成與 prompt 完全無關的圖片。若不驗證就組裝上傳，錯誤圖片會一路進入 PDF 和 CreatorHub。

下載完成後，AI 必須**讀取圖片檔案**（用 Read tool 讀取圖片）：

1. 從 `chalkboard-prompt.md` 的**中文說明**中提取 3-5 個**必須出現的視覺元素**
   - 例：「菩提樹」「盤坐人影」「宮殿」「晨星」
   - 例：「樟樹」「根系」「樹冠」「大地」
   - 例：「拼板舟」「海洋」「星空」「飛魚」
2. 讀取下載的圖片，判斷這些元素是否在圖中出現
3. 判定結果：
   - **PASS**：至少 2/3 以上的關鍵元素可辨識 → 繼續 Step 12
   - **FAIL**：圖片內容與主題明顯不符（例：prompt 要求佛陀但出現火車）→ **重新生成**（回到 Step 3，最多重試 2 次）
4. 輸出驗證結果：`[gemini-chalkboard] 圖片內容驗證：PASS — 可辨識：[元素列表]`

### Step 12 — 重命名與登錄

在 `~/Downloads/` 找到最新下載的圖檔。

**圖檔搜尋策略（4 層）：**

1. 精確匹配 `{前綴}-{STORY_ID}-chalkboard.png`
2. 模糊匹配：檔名含 STORY_ID + "chalkboard"
3. Gemini 預設檔名：`Gemini_Generated_Image_*`，取 30 分鐘內最新
4. 任何含 STORY_ID 的圖檔

若 4 種策略全部失敗 → 重試整個流程（最多 3 次）。

**重命名規則：**

- 標準模式：`{前綴}-{STORY_ID}-chalkboard.png`
- 版本模式：`{前綴}-{STORY_ID}-v2-chalkboard.png`

**登錄：** 更新 `{STORY_DIR}/chalkboard-prompt.md` 的「下載檔名」欄位。

---

## Checkpoint 條件

進入下一步（組裝 HTML/PDF）前，必須滿足：

- [ ] `~/Downloads/{前綴}-{STORY_ID}[-v2]-chalkboard.png` 存在
- [ ] 檔案大小 > 50KB
- [ ] Step 11 圖片內容驗證 = PASS
- [ ] `chalkboard-prompt.md` 下載檔名欄位已填入

全部不滿足 → FAIL，依各 daily pipeline 的錯誤處理邏輯處理。

---

## 排程模式 fallback

若 Claude in Chrome 完全不可用（CDP 連線失敗）：

- SKIP 整個流程
- 標記 `chalkboard: pending`
- HTML/PDF 照常產出但不含黑板畫嵌入
- 在 pipeline-status.yaml 記錄：`chalkboard: pending`

---

## 圖檔存放規則

- 黑板畫圖檔**只存在 `~/Downloads/`**，不複製到 Repo
- assemble 腳本直接從 `~/Downloads/` 讀取
- Repo 內只存 `.md` 檔案

---

## 注意事項

- **MIME 偵測**：`assemble-base.js` 已用 magic bytes 偵測真實圖片格式（不靠副檔名），Gemini 下載的 `.png` 若實際為 JPEG 會被正確識別
- **壓縮**：`compress-image.js` 在組裝階段自動壓縮（sips+cwebp → WebP），此技能不負責壓縮
- **版本模式**：`--version=v2` 時，assemble 腳本會跳過 Drive 上舊檔清除，保留歷史版本
