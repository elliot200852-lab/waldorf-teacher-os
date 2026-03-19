---
name: video
description: 使用 Remotion 製作影片。從素材準備、程式碼撰寫、Studio 預覽到最終渲染的完整工作流程。
triggers:
  - 做影片
  - 做一個影片
  - 製作影片
  - 拍影片
  - video
  - 影片
  - 渲染影片
  - render video
  - 建立影片專案
  - 設定 Remotion
  - video setup
  - 影片環境
  - 安裝影片工具
  - remotion setup
requires_args: false
---

# skill: video — Remotion 影片製作

使用 Repo 內的 Remotion 專案（`video/`）製作影片。本技能定義從素材到成品的完整工作流程。

> **前置條件：** `video/` 子專案已存在且可運作。若尚未建置，先執行下方 Step 0。

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：`git rev-parse --show-toplevel`。

## 執行步驟

### Step 0 — 環境建置（首次使用，僅執行一次）

> 原 `video-setup` 技能已合併至此。若 `video/` 目錄已存在且可運作，跳過此步驟。

**判斷邏輯：** 檢查 `<REPO_ROOT>/video/package.json` 是否存在。存在 → 跳到 Step 1；不存在 → 執行以下子步驟。

**設計原則：** Repo 內只放程式碼，素材與產出物都在 Repo 外部：

```
~/Videos/TeacherOS/           ← Repo 外部（不進 Git）
├── assets/                   ← 素材（照片、音檔）
│   └── photos/               ← 依用途分子目錄
└── *.mp4                     ← 渲染輸出

<REPO>/video/                 ← Repo 內（進 Git）
└── src/                      ← 影片程式碼
```

**Step 0.1 — 確認 Node.js 版本**

```bash
node -v
```

確認版本 >= 20。若版本過低，提醒教師更新 Node.js。

**Step 0.2 — 建立輸出與素材目錄**

macOS / Linux：
```bash
mkdir -p ~/Videos/TeacherOS/assets
```

Windows（PowerShell）：
```powershell
New-Item -ItemType Directory -Force -Path "$HOME\Videos\TeacherOS\assets"
```

**Step 0.3 — 建立 Remotion 子專案**

```bash
cd <REPO_ROOT>
npx create-video@latest video
```

互動式選項建議：Template: Blank、TailwindCSS: Yes、Install dependencies: Yes。
若互動提示無法繞過，請教師在終端機手動完成此步驟。

**Step 0.4 — 設定跨平台路徑**

編輯 `video/remotion.config.ts`，使用 `os.homedir()` + `path.join()`（跨平台安全）：

```typescript
import path from "path";
import os from "os";
import { Config } from "@remotion/cli/config";

const baseDir = path.join(os.homedir(), "Videos", "TeacherOS");

Config.setOutputLocation(baseDir);
Config.setPublicDir(path.join(baseDir, "assets"));
```

**Step 0.5 — 更新 .gitignore**

Repo 根目錄 `.gitignore` 新增：

```gitignore
# Remotion 影片專案
video/node_modules/
video/out/
video/dist/
video/.remotion/
```

**Step 0.6 — 驗證安裝**

```bash
cd <REPO_ROOT>/video && npm run dev
```

若 Remotion Studio 成功啟動，表示安裝完成。按 `Ctrl+C` 關閉。

---

### Step 1 — 素材準備

1. 確認教師提供的素材（音檔、照片、影片片段）
2. 建立素材子目錄（若不存在）並複製素材：

**macOS / Linux：**
```bash
mkdir -p ~/Videos/TeacherOS/assets/audio
mkdir -p ~/Videos/TeacherOS/assets/photos
cp "來源路徑" ~/Videos/TeacherOS/assets/audio/
```

**Windows（PowerShell）：**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Videos\TeacherOS\assets\audio"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Videos\TeacherOS\assets\photos"
Copy-Item "來源路徑" "$env:USERPROFILE\Videos\TeacherOS\assets\audio\"
```

3. 程式碼中一律使用 `staticFile("audio/xxx.mp3")` 引用，不寫絕對路徑

### Step 2 — 撰寫 Composition

1. 在 `video/src/` 建立新的 `.tsx` 檔案（以影片主題命名，PascalCase）
2. 在 `video/src/Root.tsx` 註冊新的 `<Composition>`，設定：
   - `id`：影片名稱
   - `durationInFrames`：總秒數 × fps
   - `fps`：30（預設）
   - `width` / `height`：1920 × 1080（預設）
3. 參考既有的 `FarmInternship.tsx` 作為結構範本

### Step 3 — 啟動 Studio 預覽

```bash
cd <REPO_ROOT>/video && npm run dev
```

Remotion Studio 會在 `http://localhost:3000` 啟動。

**AI 必須：**
1. 在背景啟動 dev server
2. 告知教師：「Studio 已啟動，請在瀏覽器打開 http://localhost:3000，選擇 [Composition 名稱] 預覽。」
3. 等教師看完給回饋

> **重要：Studio 有 HMR（Hot Module Replacement）。AI 修改程式碼後，瀏覽器會即時更新，不需重新啟動。**

### Step 4 — 教師預覽與修改循環

教師在 Studio 中可以：
- 拖曳時間軸逐幀檢視
- 調整播放速度
- 檢查每個場景的時間分配

**修改循環：**
1. 教師提出修改意見（例：「這段太長」「字太小」「順序要調」）
2. AI 修改 `.tsx` 程式碼
3. Studio 自動 HMR 更新
4. 教師再次預覽
5. 重複直到教師確認

**AI 不主動渲染。** 必須等教師明確說「可以了」「渲染」「輸出」才進入 Step 5。

### Step 5 — 渲染輸出

教師確認後，執行渲染：

**macOS / Linux：**
```bash
cd <REPO_ROOT>/video && npx remotion render src/index.ts <CompositionId> --output ~/Videos/TeacherOS/<中文檔名>.mp4
```

**Windows（PowerShell）：**
```powershell
Set-Location "<REPO_ROOT>\video"
npx remotion render src/index.ts <CompositionId> --output "$env:USERPROFILE\Videos\TeacherOS\<中文檔名>.mp4"
```

**檔名規則：** 使用繁體中文（中文在前），與教師的檔案命名習慣一致。

渲染完成後：
1. 回報檔案位置、大小、時長
2. 若教師要求，複製到桌面下載資料夾：

**macOS / Linux：**
```bash
cp ~/Videos/TeacherOS/<中文檔名>.mp4 ~/Desktop/Downloads/
```

**Windows（PowerShell）：**
```powershell
Copy-Item "$env:USERPROFILE\Videos\TeacherOS\<中文檔名>.mp4" "$env:USERPROFILE\Desktop\Downloads\"
```

### Step 6 — 關閉 Studio

渲染完成且教師不再需要修改時，終止背景的 dev server 程序。

AI 應使用啟動時記錄的 process ID 來關閉：

**macOS / Linux：**
```bash
kill <PID>
```

**Windows（PowerShell）：**
```powershell
Stop-Process -Id <PID>
```

或在教師收工時自動關閉。

## 跨平台注意

| 項目 | macOS / Linux | Windows（PowerShell） |
|------|---------------|----------------------|
| 素材目錄 | `~/Videos/TeacherOS/assets/` | `$env:USERPROFILE\Videos\TeacherOS\assets\` |
| 輸出目錄 | `~/Videos/TeacherOS/` | `$env:USERPROFILE\Videos\TeacherOS\` |
| 建立目錄 | `mkdir -p` | `New-Item -ItemType Directory -Force` |
| 複製檔案 | `cp` | `Copy-Item` |
| 關閉程序 | `kill <PID>` | `Stop-Process -Id <PID>` |
| 啟動 Studio | `npm run dev` | `npm run dev` |
| 渲染 | `npx remotion render ...` | `npx remotion render ...` |

## AI 工作協議

- **先預覽，後渲染**：絕對不跳過 Studio 預覽直接渲染，除非教師明確要求
- **素材用 `staticFile()`**：不寫絕對路徑
- **不刪除素材**：由教師決定何時清理
- **中文檔名**：輸出的 MP4 使用繁體中文命名
- **背景渲染**：渲染過程在背景執行，不阻擋對話

## 注意事項

- 影片程式碼在 Repo 內（進 Git），素材和輸出在 Repo 外（不進 Git）
- 每個影片是一個獨立的 Composition，共用 utility components 可抽到 `video/src/` 的共用檔案
- Remotion 支援 TailwindCSS，已在 `remotion.config.ts` 中啟用
