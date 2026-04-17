---
name: wiki-reflect
description: 從備課對話擷取設計思考與反思，存入共享知識庫 wiki/。與 lesson-engine Phase 6（設計摘要）互補——Phase 6 記錄「做了什麼」，wiki-reflect 記錄「為什麼這樣做」。支援反向連結 teaching-log。所有教師通用。
triggers:
  - 備課反思
  - 設計反思
  - wiki reflect
  - 寫反思
  - 記錄設計思考
  - 反思一下
requires_args: false
args_format: "[選填：班級代碼 科目 週次] (例: 9c english w8)"
---

# skill: wiki-reflect — 備課設計反思

從備課對話擷取教師的設計思考歷程，存入共享知識庫 `wiki/`。

## 核心定位

| | teaching-log | Phase 6 (auto) | wiki-reflect |
|---|---|---|---|
| **時機** | 上完課之後 | 備課完自動 | 備課過程中/完成後，教師觸發 |
| **內容** | 課堂觀察、感受、備忘 | 設計摘要（做了什麼） | 設計思考（為什麼這樣做、決策歷程） |
| **輸出** | `{workspace}/teaching-log.md` | `wiki/{class}-{subject}-w{week}-{seq}.md` | `wiki/{class}-{subject}-w{week}-{seq}-reflect.md` |
| **對象** | 自己 | 所有教師 | 所有教師 |

wiki-reflect 記錄的是**設計決策的思考歷程**——草稿的初始想法、教師審閱後的判斷、教育哲學層面的理由、未解決的問題。這些內容在對話結束後會消失，但對教師成長和知識傳承最有價值。

## 參數

選填。若在備課 session 中（已有 class/subject context），AI 直接從對話擷取。
若不在備課 session 中，AI 詢問「哪堂課？」。
也可直接指定：「備課反思 9C english w8」。

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 執行步驟

### Step 1 — 確認反思對象

判斷當前是否在備課 session 中（有 class/subject/week context）：

| 狀況 | 處理 |
|------|------|
| 在備課 session 中（剛完成 lesson-engine 或正在備課對話） | 直接使用當前 context，不詢問 |
| 教師帶參數（例：「備課反思 9C english w8」） | 使用指定參數 |
| 無 context、無參數 | 詢問：「哪堂課的反思？（例：9C 英文 第八週）」 |

確認後取得：`{class}`、`{subject}`、`{week}`、`{seq}`（若有）。

### Step 2 — 反向連結 teaching-log（自動）

掃描 `{workspace}/teaching-log.md`，搜尋同堂課的紀錄：

1. 讀取 teaching-log.md
2. 比對每筆 `## YYYY-MM-DD #tag1 #tag2 ...` 紀錄
3. 匹配條件：同班級 tag（如 `#9C`）+ 同科目 tag（如 `#英文`），日期在最近 14 天內

| 結果 | 處理 |
|------|------|
| 找到匹配紀錄 | 記錄其標題（`## YYYY-MM-DD #tag1 #tag2`），稍後加入 `## 連結` 段落。**注意：** Obsidian heading anchor 會自動去掉 `#` 符號，所以 wikilink 寫法為 `[[teaching-log#2026-03-26 英文 教學流程 9C]]`（不含 `#`），不是 `[[teaching-log#2026-03-26 #英文 #教學流程 #9C]]` |
| 找不到 | 留空。日後教師補寫 teaching-log 時可口頭觸發反向連結 |
| teaching-log.md 不存在 | 跳過，不報錯 |

### Step 3 — 組裝反思草稿

從本次對話歷史自動擷取，組裝以下內容。**所有段落為建議結構，教師可自由調整、增刪、重新命名。**

#### 擷取來源

1. **草稿的初始想法**：對話早期 AI 提出的設計方案、出發點假設
2. **教師的判斷與調整**：教師審閱後改了什麼、為什麼改（尋找教師否決或修改 AI 建議的對話段落）
3. **為什麼這樣設計**：教育哲學層面的理由——頭心手、呼吸節奏、DI 考量、學生發展階段
4. **未解決的問題**：備課過程中浮現但未處理的疑問或待觀察事項

#### 擷取原則

- 保留教師的原始用語和判斷邏輯，不美化不潤飾
- 不含學生姓名或代碼（DI 用 A/B/C/D 軸）
- 設計決策的「為什麼」比「做了什麼」重要——Phase 6 已記錄「做了什麼」
- 若對話中教師沒有明確的設計思考（例如只是照 AI 建議執行），誠實告知：「這次備課的對話中沒有明顯的設計決策分歧或深層思考，要寫反思嗎？」

### Step 4 — 預覽與確認

顯示完整的反思草稿（含 frontmatter），讓教師確認：

```
以下是備課反思草稿：

（完整 Markdown 預覽）

確認寫入嗎？要調整內容或段落嗎？
```

教師可以：
- 確認直接寫入
- 口頭補充內容（AI 整合後再確認）
- 要求調整特定段落
- 取消

### Step 5 — 寫入 wiki/

#### 檔名

```
wiki/{class}-{subject}-w{week}-{seq}-reflect.md
```

範例：
- `wiki/9c-english-w8-1&2-reflect.md`
- `wiki/9d-ml-taiwan-literature-w8-syllabus-reflect.md`

`-reflect` 後綴與 Phase 6 自動版配對。若無明確 seq（例如課程大綱反思），用語意 slug（如 `syllabus`）。

#### Frontmatter 規格

```yaml
---
aliases:
  - "{CLASS} {科目中文} W{week} 備課反思"
  - "{CLASS} {Subject} W{week} Reflect"
type: design-reflection
date: {今天日期}
class: {class code}
subject: {subject}
block: {block number}
week: {week number}
teacher: {教師姓名}
theme: "{教案的 theme 欄位}"
text: "{核心文本名稱，若無則 null}"
tags:
  # 骨架標籤（固定四個）
  - design-reflection
  - {class code}
  - {subject}
  - block-{N}
  # 內容標籤（AI 從反思內容自動萃取，不設上限）
  # 萃取邏輯：掃描文本名、作者、教學法概念、DI 策略關鍵字、
  #           課程設計手法（連堂設計、呼吸轉換、分組深讀…）
  # 確保 Obsidian graph view 和 Bases 的連結廣度
  - {文本名}
  - {作者}
  - {教學法關鍵字}
  - {DI 策略}
  - {課程設計手法}
related:
  - "[[{對應的 Phase 6 wiki 檔，若存在}]]"
  - "[[{教案檔}]]"
  - "[[{學習單檔}]]"
  - "[[{teaching-log heading link，若 Step 2 找到}]]"
  # AI 自動偵測並追加相關概念頁
---
```

#### 文章模板

```markdown
# {CLASS} {科目中文} W{week} 備課反思

## 草稿的初始想法
{AI 從對話擷取：最初的設計意圖、出發點}

## 教師的判斷與調整
{AI 從對話擷取：教師審閱後改了什麼、為什麼改}

## 為什麼這樣設計
{教育哲學層面的理由 — 頭心手、呼吸節奏、DI 考量}

## 未解決的問題
{這次備課過程中浮現但未處理的疑問}

## 連結
- Phase 6 日誌：[[{class}-{subject}-w{week}-{seq}]]
- 教案：[[{教案檔名}]]
- 學習單：[[{學習單檔名}]]
- 前一堂反思：[[{class}-{subject}-w{prev}-reflect]]（若存在）
- 教學紀錄：[[teaching-log#YYYY-MM-DD heading（去掉 # 符號）]]（若 Step 2 找到）
- 文本：[[{text concept page}]]（若 text 欄位非空）
- 作者：[[{author concept page}]]（若可辨識作者）
```

段落名稱為建議，教師可自由增刪重組。唯一固定的是 `## 連結` 段落（確保 wikilink 完整性）。

### Step 6 — 雙向 wikilink 更新

寫入完成後，自動更新相關檔案的連結：

1. **Phase 6 wiki 檔**（若存在 `wiki/{class}-{subject}-w{week}-{seq}.md`）：
   在其 `related:` frontmatter 加上 `"[[{class}-{subject}-w{week}-{seq}-reflect]]"`

2. **teaching-log**（若 Step 2 找到匹配紀錄）：
   在 teaching-log 該筆紀錄中找到合適位置（紀錄末尾、下一個 `---` 之前），加上：
   `> 備課反思：[[{class}-{subject}-w{week}-{seq}-reflect]]`

3. **概念頁**（若 `wiki/concepts/` 下有相關頁面）：
   掃描 frontmatter 中的 text/tags，若概念頁已存在，在概念頁的 `related:` 加上反向連結

### Step 7 — 報告完成

```
備課反思已寫入：wiki/{filename}-reflect.md
- 雙向連結：{已連結的檔案清單}
- Tags：{tag 清單}
```

## teaching-log ↔ wiki-reflect 雙向整合

### 方向一：wiki-reflect → teaching-log（自動，Step 2）

wiki-reflect 寫入時，自動掃描 teaching-log 有無同堂課紀錄。有就在 `related:` 和 `## 連結` 加 wikilink。

### 方向二：teaching-log → wiki-reflect（教師口頭觸發）

教師做 teaching-log 時，可以口頭說以下任何表達：
- 「合併之前的反思」
- 「連結 wiki reflect」
- 「加上備課反思」
- 「把反思連進來」

AI 執行：
1. 從當前 teaching-log 紀錄推斷班級 + 科目 + 近期週次
2. 掃描 `wiki/` 找到匹配的 `-reflect.md` 檔
3. 在 teaching-log 該筆紀錄末尾加上：`> 備課反思：[[{class}-{subject}-w{week}-{seq}-reflect]]`
4. 反向更新 wiki-reflect 檔的 `related:`，加上 `[[teaching-log#YYYY-MM-DD heading（去掉 # 符號）]]`

Obsidian graph view 會自然顯示「備課前的設計思考」和「上完課的教學觀察」之間的連結。

## 概念頁自動偵測

與 Phase 6 相同的邏輯：

1. 提取本次反思中的實體（文本名、作者、文法概念、主題詞）
2. 掃描 `wiki/concepts/` 下已有的概念頁
3. 跨科出現 2 次以上的實體，若尚無概念頁，建議建立（不自動建立，預覽後教師確認）
4. 已有概念頁的實體，自動在 frontmatter `related:` 互加 wikilink

## 與其他技能的關係

- **lesson-engine Phase 6**：Phase 6 是自動產出的設計摘要（做了什麼），wiki-reflect 是手動觸發的設計反思（為什麼這樣做）。兩者透過 `-reflect` 後綴配對，frontmatter `related:` 雙向連結
- **teaching-log**：teaching-log 記錄上完課的教學觀察（主體是課堂經驗），wiki-reflect 記錄備課過程的設計思考（主體是設計決策）。雙向整合見上方說明
- **raw-ingest**：raw-ingest 消化外部文件到 wiki。wiki-reflect 從對話擷取內部知識到 wiki。兩者互不干擾，共享 wiki/ 的概念頁連結網
- **block-end**：block-end 是整個區塊結束的結構化反思。wiki-reflect 是單堂課/單次備課的設計反思。粒度不同

## 注意事項

- 全程使用繁體中文
- 反思內容保留教師原始用語，不過度潤飾
- 不含學生姓名或代碼
- 若備課對話中沒有明顯的設計決策或深層思考，誠實告知教師，不硬擠內容
- 語音輸入友善：「反思一下」「備課反思」即可觸發
- 此技能為所有教師通用，任何已註冊的教師都可使用
- 跨平台：無平台相依指令，macOS 和 Windows 均可執行
