---
name: video-setup
description: 建立 Remotion 影片專案環境。在 Repo 內建立 video/ 子專案、設定跨平台輸出路徑與素材目錄、更新 .gitignore。適用於任何需要影片製作能力的教師。
triggers:
  - 建立影片專案
  - 設定 Remotion
  - video setup
  - 影片環境
  - 安裝影片工具
  - remotion setup
requires_args: false
---

# skill: video-setup — 建立 Remotion 影片專案

在 TeacherOS Repo 內建立 Remotion 影片製作環境，讓教師可以用程式化方式產出教學影片。

## 設計原則

Repo 內只放程式碼，素材與產出物都在 Repo 外部：

```
~/Videos/TeacherOS/           ← Repo 外部（不進 Git）
├── assets/                   ← 素材（照片、音檔）
│   └── photos/               ← 依用途分子目錄
└── *.mp4                     ← 渲染輸出

<REPO>/video/                 ← Repo 內（進 Git）
└── src/                      ← 影片程式碼
```

## 觸發條件

教師說出接近以下意思的話：
「建立影片專案」「設定 Remotion」「video setup」「影片環境」「安裝影片工具」

## 根目錄

以 Repo 根目錄為基準（相對路徑）。
AI 自動偵測根目錄位置：嘗試 `git rev-parse --show-toplevel`，或從當前已知的工作目錄推斷。

## 前置條件

- Node.js >= 20（建議 v22+）
- npm
- 終端機執行能力（此技能無法在無終端機的 AI 環境中自動執行）

## 跨平台工具能力矩陣

| AI 能力 | 行為 |
|---------|------|
| 有終端機（Claude Code、Cowork） | 自動執行所有步驟 |
| 無終端機（Gemini 語音、ChatGPT） | 逐步輸出指令，請教師在終端機手動執行並回報結果 |

## 執行步驟

> **跨平台注意：** 本技能支援 macOS 和 Windows。
> - 路徑使用 `/`（AI 工具會自動處理分隔符）
> - 暫存目錄：macOS 用 `/tmp/`，Windows 用 `%TEMP%`，或統一用 `python3 -c "import tempfile; print(tempfile.gettempdir())"`
> - 套件安裝：macOS 用 `npm` 或 `brew`，Windows 用 `npm` 或 `winget`

### Step 1 — 確認 Node.js 版本

```bash
node -v
```

確認版本 >= 20。若版本過低，提醒教師更新 Node.js。

### Step 2 — 建立輸出與素材目錄

在教師的家目錄下建立統一的影片工作目錄（Repo 外部）。

**macOS / Linux：**
```bash
mkdir -p ~/Videos/TeacherOS/assets
```

**Windows（PowerShell）：**
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\Videos\TeacherOS\assets"
```

| 平台 | 實際路徑 |
|------|---------|
| macOS | `/Users/教師名/Videos/TeacherOS/` |
| Linux | `/home/教師名/Videos/TeacherOS/` |
| Windows | `C:\Users\教師名\Videos\TeacherOS\` |

`assets/` 子目錄用於存放照片、音檔等素材。`remotion.config.ts` 會自動指向此處。

### Step 3 — 建立 Remotion 子專案

在 Repo 根目錄下執行：

```bash
cd <REPO_ROOT>
npx create-video@latest video
```

**互動式選項建議：**
- Template: **Blank**（最乾淨的起點）
- TailwindCSS: **Yes**（方便排版）
- Install dependencies: **Yes**

> **注意：** `npx create-video@latest` 是互動式指令。有終端機的 AI 應嘗試自動執行；若互動提示無法繞過，請教師手動在終端機中完成此步驟，完成後回報。

### Step 4 — 設定跨平台路徑

編輯 `video/remotion.config.ts`，確認路徑設定使用 `os.homedir()` + `path.join()`（跨平台安全）：

```typescript
import path from "path";
import os from "os";
import { Config } from "@remotion/cli/config";

const baseDir = path.join(os.homedir(), "Videos", "TeacherOS");

Config.setOutputLocation(baseDir);
Config.setPublicDir(path.join(baseDir, "assets"));
```

> **為什麼不用 `process.env.HOME`？** 此變數在 Windows 上不存在（Windows 用 `USERPROFILE`）。`os.homedir()` 是 Node.js 標準 API，在 macOS、Linux、Windows 皆能正確解析。

### Step 5 — 更新 .gitignore

**Repo 根目錄 `.gitignore`** — 新增以下條目：

```gitignore
# Remotion 影片專案（追蹤原始碼，排除產出物與依賴）
video/node_modules/
video/out/
video/dist/
video/.remotion/
```

確認 `video/` 目錄本身不被排除（原始碼應納入版本控制）。

### Step 6 — 驗證安裝

```bash
cd <REPO_ROOT>/video
npm run dev
```

若 Remotion Studio 成功啟動（預設 http://localhost:3000），表示安裝完成。
按 `Ctrl+C` 關閉預覽伺服器。

## 驗證清單

- [ ] `video/` 目錄存在且包含 Remotion 專案結構
- [ ] `~/Videos/TeacherOS/assets/` 目錄已建立
- [ ] `remotion.config.ts` 使用 `os.homedir()` + `path.join()`（跨平台）
- [ ] `.gitignore` 已加入 video 相關排除規則
- [ ] `npm run dev`（在 video/ 下）可啟動 Remotion Studio

## 素材管理（照片、音檔、影片片段）

### 存放位置

```
~/Videos/TeacherOS/assets/    ← 所有素材的根目錄
├── photos/                   ← 照片（依專案或用途命名子目錄亦可）
├── audio/                    ← 背景音樂、旁白
└── [其他子目錄]/              ← 依需求自由新增
```

### 運作邏輯

- `remotion.config.ts` 已將 Remotion 的 public 目錄指向 `~/Videos/TeacherOS/assets/`
- 程式碼中用 `staticFile("photos/xxx.jpg")` 引用素材，Remotion 自動從 assets/ 讀取
- 素材不在 Repo 內，不會推上 Git，不會膨脹專案

### 教師操作方式

1. **放入素材**：將照片或音檔放到 `~/Videos/TeacherOS/assets/` 的對應子目錄
2. **告訴 AI**：「我在 Downloads 放了一個照片資料夾」或「素材在 assets/photos/ 裡了」
3. **AI 處理**：自動將素材複製到 assets/ 並在程式碼中用 `staticFile()` 引用

### 素材生命週期

| 階段 | 能否刪除素材 | 原因 |
|------|------------|------|
| 開發中（預覽、調整） | 不能 | Studio 預覽需要讀取素材 |
| 渲染完成、可能還會修改 | 不建議 | 重新渲染需要素材 |
| 影片定稿、確定不再修改 | 可以安全刪除 | MP4 已獨立，不依賴素材 |

刪除素材後，Repo 中的程式碼仍在（但無法重新渲染該影片）。

### AI 工作協議

- 教師提供素材時，AI 自動複製到 `~/Videos/TeacherOS/assets/` 對應子目錄
- AI 在程式碼中一律使用 `staticFile()` 引用，不硬寫絕對路徑
- AI 不主動刪除素材，由教師決定何時清理

## 日常使用參考

| 操作 | 指令 |
|------|------|
| 啟動 Remotion Studio（預覽） | `cd video && npm run dev` |
| 渲染影片（指定檔名） | `cd video && npx remotion render src/index.ts <CompositionName> --output ~/Videos/TeacherOS/<filename>.mp4` |
| 升級 Remotion | `cd video && npx remotion upgrade` |

> **Windows 教師：** 渲染指令的 `~/Videos/TeacherOS/` 改為 `%USERPROFILE%\Videos\TeacherOS\`，或直接指定完整路徑。

## 注意事項

- 全程使用繁體中文回報進度
- `video/` 子專案有自己的 `package.json` 與 `node_modules/`，與 Repo 其他部分獨立
- **Repo 內只有程式碼**：影片輸出（MP4）和素材（照片、音檔）都存放在 `~/Videos/TeacherOS/`，不進 Git
- 若教師已有 `video/` 目錄，先確認是否要覆蓋，避免損毀現有工作
- 此技能為一次性設定。設定完成後，日常影片製作不需重新執行
- **Windows 教師注意**：確認 Node.js 已加入 PATH；建議使用 PowerShell 而非 CMD
