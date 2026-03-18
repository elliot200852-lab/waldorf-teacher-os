---
name: teach-animation
description: 用 Revideo（Motion Canvas fork）快速生成教學動畫。概念解說、時間線、流程圖、標題動畫。輕量快速，與 Remotion 影片製作互補。
triggers:
  - 教學動畫
  - 做動畫
  - 做一段動畫
  - 概念動畫
  - 解說動畫
  - 概念視覺化
  - timeline 動畫
  - 流程圖動畫
  - animate
  - teach animation
  - 做一段教學影片給學生看
  - 視覺化這個概念
requires_args: false
---

# skill: teach-animation — 教學動畫生成（Revideo）

用 Revideo（Motion Canvas fork，支援 headless CLI 渲染）快速生成教學動畫。
適用場景：概念解說、歷史時間線、流程圖、因果關係圖、課堂標題動畫。

> **與 video skill 的分工：**
> - `video`（Remotion）= 完整影片製作工作室。有 Studio 預覽、HMR 修改循環、React 元件架構。適合農場紀錄片、學期回顧等複雜作品。
> - `teach-animation`（Revideo）= 快速動畫生成器。TypeScript generator function + `yield*`，輕量流程。適合概念視覺化、課堂素材。
>
> **簡單判斷：** 需要預覽循環與複雜剪輯 → video。需要快速生成概念動畫 → teach-animation。
> **不觸發的詞：** 「做影片」「製作影片」「video」→ 歸 video skill。

## 前置需求

- Node.js >= 16
- FFmpeg

確認安裝：

**macOS / Linux：**
```bash
command -v node && command -v ffmpeg
```

**Windows（PowerShell）：**
```powershell
Get-Command node; Get-Command ffmpeg
```

若 FFmpeg 未安裝：

**macOS：**
```bash
brew install ffmpeg
```

**Windows（PowerShell）：**
```powershell
winget install Gyan.FFmpeg
# 或
choco install ffmpeg
```

## 根目錄

以 Repo 根目錄為基準。AI 自動偵測：`git rev-parse --show-toplevel`。

## 執行步驟

### Step 1 — 解析請求

從教師輸入中解析：

- **影片類型**：concept（概念解說動畫）/ material（課堂素材影片）/ custom（自訂）
- **主題與內容**：要視覺化的概念、流程、時間線、文字
- **語言**：預設繁體中文，英文素材保留英文
- **時長偏好**：若未指定，概念動畫 60-90 秒，素材影片 15-45 秒
- **背景音樂**：若教師提供音檔，複製到 `public/audio/` 並在場景中加入 `<Audio>`

### Step 2 — 確認或初始化專案

Revideo 工作目錄位於 Repo 外部（不進 Git）。

> **重要：** `npm init @revideo@latest` 在某些環境有 interactive prompt 問題。
> AI 應優先使用手動初始化流程（見下方），確保可靠性。

**macOS / Linux：**
```bash
REVIDEO_DIR="$HOME/revideo-workspace/revideo-project"

if [ ! -d "$REVIDEO_DIR" ]; then
  mkdir -p "$REVIDEO_DIR/src/scenes" "$REVIDEO_DIR/public/audio"
  cd "$REVIDEO_DIR"
  npm init -y
  # 修改 package.json 的 type 為 module
  npm pkg set type=module
  npm pkg set scripts.start=vite
  npm pkg set scripts.render="tsx src/render.ts"
  npm install @revideo/2d @revideo/core @revideo/renderer @revideo/vite-plugin @revideo/ui
  npm install -D tsx vite
fi
```

**Windows（PowerShell）：**
```powershell
$REVIDEO_DIR = "$env:USERPROFILE\revideo-workspace\revideo-project"

if (-not (Test-Path $REVIDEO_DIR)) {
  New-Item -ItemType Directory -Force -Path "$REVIDEO_DIR\src\scenes"
  New-Item -ItemType Directory -Force -Path "$REVIDEO_DIR\public\audio"
  Set-Location $REVIDEO_DIR
  npm init -y
  npm pkg set type=module
  npm pkg set scripts.start=vite
  npm pkg set scripts.render="tsx src/render.ts"
  npm install @revideo/2d @revideo/core @revideo/renderer @revideo/vite-plugin @revideo/ui
  npm install -D tsx vite
}
```

**初始化後，AI 必須建立以下設定檔（使用 Write tool）：**

`vite.config.ts`：
```tsx
// @ts-nocheck
import {defineConfig} from 'vite';
import pkg from '@revideo/vite-plugin';

const motionCanvas = pkg.default ?? pkg;

export default defineConfig({
  plugins: [motionCanvas({project: './src/project.ts'})],
});
```

`tsconfig.json`：
```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "jsxImportSource": "@revideo/2d/lib",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": true
  },
  "include": ["src"]
}
```

`src/project.meta`（必須存在，否則 Revideo 無法讀取場景名稱）：
```json
{
  "version": 1,
  "name": "teach-animation",
  "fps": 30,
  "resolution": {"x": 1920, "y": 1080},
  "background": "#1a1a2e"
}
```

`src/render.ts`：
```tsx
import {renderVideo} from '@revideo/renderer';

async function render() {
  console.log('Rendering video...');
  const file = await renderVideo({
    projectFile: './src/project.ts',
    settings: {logProgress: true},
  });
  console.log(`Rendered video to ${file}`);
}

render();
```

若專案已存在（`$REVIDEO_DIR/package.json` 存在），跳過初始化直接進入 Step 3。

### Step 3 — 生成場景檔案

在 `src/scenes/` 下建立新的 `.tsx` 場景檔案。命名規則：`{日期}-{主題簡稱}.tsx`

**關鍵 API 注意（Revideo v0.10+）：**

```tsx
// 所有 import 來自 @revideo，不是 @motion-canvas
import {Txt, Rect, Circle, Line, Img, Audio, makeScene2D} from '@revideo/2d';
import {
  all, chain, sequence, waitFor, createRef, createSignal,
  easeInOutCubic, easeOutBack, easeOutElastic, easeOutCubic, useScene
} from '@revideo/core';

// ⚠️ v0.10 的 makeScene2D 需要兩個參數：name + runner
// 第一個參數是場景名稱字串（必填），第二個是 generator function
export default makeScene2D('scene-name', function* (view) {
  // animation logic here
});
```

> **常見錯誤：** `makeScene2D(function* (view) {...})` 只傳一個參數會導致
> `Cannot read properties of undefined (reading 'name')` 錯誤。
> v0.10 的簽名是 `makeScene2D(name: string, runner: GeneratorFunction)`。

**華德福動畫設計原則：**

1. **節奏感**：動畫的出現與消失要有呼吸節奏，避免突然出現/消失。每個元素至少 0.3 秒過渡
2. **色彩豐富**：使用溫暖、自然但鮮明的色調。每個概念用不同色系區分。推薦色板：
   - 背景：場景切換時變換底色（`#0f0e1a` → `#141428` → `#1a1020` → `#0a0f1e`）
   - 主色：`#ff6b6b`（珊瑚紅）、`#2dd4a8`（翡翠綠）、`#5b7cfa`（皇家藍）
   - 強調：`#ffd93d`（金黃）、`#f4a261`（琥珀）、`#a78bfa`（薰衣草紫）
   - 卡片：`#1e1e3a`（深卡片底）+ 各概念色的 2px 描邊
3. **文字**：中文使用 `fontFamily: 'Noto Sans TC, sans-serif'`。標題 ≥ 72px，內文 ≥ 28px
4. **彈跳進場**：使用 `easeOutBack` 或 `easeOutElastic` 搭配 `scale(0→1)` 實現 pop-out 效果
5. **場景切換**：不同主題段落使用不同背景色的全螢幕 `<Rect>` 淡入淡出
6. **資訊圖表**：善用橫條圖（`<Rect>` width 動畫）、圓點 + 光暈（`<Circle>` 雙層）、圖示 emoji
7. **空間**：留白充足，一個畫面最多 3-4 個視覺元素
8. **流向**：資訊從左到右、從上到下，符合閱讀直覺

**常用動畫模式：**

```tsx
// pop-out 彈跳進場（推薦用於標題與卡片）
yield* all(
  element().opacity(1, 0.5),
  element().scale(0.3).scale(1, 0.6, easeOutBack),
);

// elastic 彈跳（用於圓點、icon）
yield* all(
  dot().opacity(1, 0.3),
  dot().scale(0).scale(1, 0.5, easeOutElastic),
);

// 逐一出現（每個間隔 0.15 秒，比 0.2 更緊湊）
yield* sequence(0.15,
  icon().opacity(1, 0.3),
  label().opacity(1, 0.3),
  desc().opacity(1, 0.3),
);

// 橫條圖動畫（資訊圖表用）
yield* bar().width(400, 1.0, easeOutCubic);

// 場景切換（背景色轉場）
yield* all(
  oldBg().opacity(0, 0.8),
  /* ...淡出所有舊元素... */
);
yield* newBg().opacity(1, 0.8);
```

**背景音樂（若教師提供）：**

將音檔複製到 `public/audio/` 後，在場景開頭加入：

```tsx
// Audio 元件不需要 ref（v0.10 的 Audio 不支援 volume signal animation）
view.add(
  <Audio src={'audio/bg-music.mp3'} play={true} volume={0.4} />,
);
```

> **已知限制：** Revideo v0.10 的 `<Audio>` volume 不支援 signal-based animation（`volume(0, 2.0)` 會報錯）。
> 音量淡出需用 FFmpeg 後製，或接受固定音量。

### Step 4 — 更新專案設定

更新 `src/project.ts` 指向新場景：

```tsx
import {makeProject} from '@revideo/core';
import scene from './scenes/{scene-filename}?scene';

export default makeProject({
  scenes: [scene],
});
```

若需要更換場景名稱或解析度，同步更新 `src/project.meta`。

### Step 5 — 預覽（可選但建議）

**macOS / Linux / Windows（通用）：**
```bash
cd <REVIDEO_DIR> && npm start
```

Revideo Studio 會在 `http://localhost:9000/` 啟動（port 被佔用時自動遞增）。

**AI 必須：**
1. 在背景啟動 dev server
2. 告知教師瀏覽器 URL
3. 等教師確認後進入修改循環或渲染

> Studio 有 HMR。AI 修改 `.tsx` 後瀏覽器即時更新。
> 首次啟動或清 cache 後需重新整理瀏覽器。

### Step 6 — 渲染

教師確認後（或跳過預覽時），執行 headless 渲染：

**macOS / Linux / Windows（通用）：**
```bash
cd <REVIDEO_DIR> && npx tsx src/render.ts
```

> **注意：** 渲染時 Revideo 會啟動自己的 vite server + puppeteer。
> 若 dev server 仍在運行，渲染會自動使用下一個可用 port，不衝突。
> 但建議先關閉 dev server 以減少資源佔用。

輸出檔案預設在 `./output/video.mp4`。

### Step 7 — 交付

將輸出的 .mp4 複製到教師桌面，使用繁體中文命名：

**macOS / Linux：**
```bash
cp ./output/video.mp4 ~/Desktop/<中文檔名>.mp4
```

**Windows（PowerShell）：**
```powershell
Copy-Item .\output\video.mp4 "$env:USERPROFILE\Desktop\<中文檔名>.mp4"
```

告知教師：檔案位置、解析度、時長、檔案大小。

若教師要上傳 Google Drive，使用 gws CLI 或銜接 drive 技能。

## 影片類型模板

### 概念解說動畫（concept）

適用：歷史時間線、抽象概念視覺化、因果關係圖、比較分析

典型結構（60-90 秒）：
1. 標題 pop-out 進場 + 裝飾線（3-5 秒）
2. 背景轉場 → 核心概念逐步展開，每段用不同色系卡片（主體 30-50 秒）
3. 背景轉場 → 資訊圖表總結（橫條圖 / 對比表）（10-15 秒）
4. 背景轉場 → 金句收尾 + 署名（8-12 秒）

### 課堂素材影片（material）

適用：課堂開場標題、活動轉場、重點提示卡、每日金句

典型結構（15-45 秒）：
1. 背景色淡入
2. 主文字 pop-out 進場
3. 副文字或裝飾元素
4. 停留展示（3-5 秒）
5. 淡出

## 參數化影片（差異化教學用）

Revideo 支援透過 variables 傳入動態內容，適合批次生成：

```tsx
// scene 中讀取參數
const studentName = useScene().variables.get('name', '同學')();
const topic = useScene().variables.get('topic', '今日主題')();
```

```tsx
// render.ts 中傳入參數
await renderVideo({
  projectFile: './src/project.ts',
  variables: {name: '小明', topic: '台灣戰後史'},
  settings: {logProgress: true},
});
```

## 注意事項

- **import 路徑**：`@revideo/2d` 和 `@revideo/core`，**不是** `@motion-canvas`
- **makeScene2D 簽名**：v0.10 需要 `makeScene2D('name', function* (view) {...})`，兩個參數
- **project.meta 必須存在**：否則 Revideo 無法讀取專案名稱，預覽和渲染都會失敗
- **vite-plugin 匯出**：v0.10 需要 `pkg.default ?? pkg` 取得正確的 function
- **中文字型**：需確認系統已安裝 Noto Sans TC 或其他中文字型
- **Audio volume**：v0.10 不支援 signal animation，音量只能設定固定值
- 本機渲染速度通常快於即時（1 分鐘影片渲染不到 1 分鐘）
- 影片預設解析度 1920x1080，30fps
- 不處理影片剪輯或轉檔——那是 FFmpeg 的工作

## 除錯

| 症狀 | 原因 | 解法 |
|------|------|------|
| `Cannot read properties of undefined (reading 'name')` | `makeScene2D` 缺少第一個 name 參數 | 改為 `makeScene2D('scene-name', function* ...)` |
| `Cannot find module '@revideo/ui'` | 未安裝 UI 套件 | `npm install @revideo/ui` |
| `motionCanvas is not a function` | vite-plugin 匯出格式 | 使用 `pkg.default ?? pkg` |
| 預覽黑屏 | vite cache 過期 | 刪除 `node_modules/.vite` 並重啟 |
| `volume is not a function` | Audio 不支援 signal animation | 移除 `bgMusic().volume(...)` 動畫 |
| 中文不顯示 | 缺字型 | macOS: `fc-list \| grep -i noto`；Windows: `Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' \| Select-String 'Noto'` |
| 渲染卡住 | 場景有無限迴圈或缺少 `yield*` | 先跑 `npm start` 在瀏覽器確認動畫正確 |

## 跨平台對照表

| Step | 有終端指令？ | macOS / Linux | Windows（PowerShell） | 狀態 |
|------|-----------|--------------|---------------------|------|
| 前置需求（FFmpeg 確認） | 有 | `command -v ffmpeg` | `Get-Command ffmpeg` | OK |
| 前置需求（FFmpeg 安裝） | 有 | `brew install ffmpeg` | `winget install Gyan.FFmpeg` | OK |
| Step 2（專案初始化） | 有 | `mkdir -p` + `npm init -y` + `npm install` | `New-Item` + `npm init -y` + `npm install` | OK |
| Step 2（設定檔） | 無 | AI Write tool | AI Write tool | OK |
| Step 3（場景檔寫入） | 無 | AI Write tool | AI Write tool | OK |
| Step 4（設定更新） | 無 | AI Edit tool | AI Edit tool | OK |
| Step 5（預覽） | 有 | `npm start` | `npm start` | OK（通用） |
| Step 6（渲染） | 有 | `npx tsx src/render.ts` | `npx tsx src/render.ts` | OK（通用） |
| Step 7（交付複製） | 有 | `cp` | `Copy-Item` | OK |
| 除錯（字型檢查） | 有 | `fc-list \| grep noto` | `Get-ItemProperty ... \| Select-String` | OK |
| 除錯（清 cache） | 有 | `rm -rf node_modules/.vite` | `Remove-Item -Recurse node_modules\.vite` | OK |
