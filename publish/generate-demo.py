import base64

REPO = '/Users/Dave/Desktop/WaldorfTeacherOS-Repo'

with open(f'{REPO}/setup/assets/waldorf-bg.jpg', 'rb') as f:
    BG_B64 = base64.b64encode(f.read()).decode()
with open(f'{REPO}/setup/assets/logo-ready.png', 'rb') as f:
    LOGO_B64 = base64.b64encode(f.read()).decode()

html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TeacherOS — 系統功能說明</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif;
    min-height: 100vh;
    background-color: #fdf8f0;
    background-image: url("data:image/jpeg;base64,{BG_B64}");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    color: #3a2e22;
  }}

  .overlay {{
    min-height: 100vh;
    background: rgba(253, 248, 240, 0.82);
    padding: 0 0 60px 0;
  }}

  /* ── Header ── */
  header {{
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(180,150,100,0.2);
    padding: 18px 40px;
    display: flex;
    align-items: center;
    gap: 18px;
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  header img {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
  }}
  header .title-block h1 {{
    font-size: 1.4rem;
    font-weight: 700;
    color: #4a3520;
    letter-spacing: 0.02em;
  }}
  header .title-block p {{
    font-size: 0.82rem;
    color: #8a6e4e;
    margin-top: 2px;
  }}

  /* ── Tabs ── */
  .tab-bar {{
    display: flex;
    gap: 0;
    padding: 28px 40px 0;
    border-bottom: 2px solid rgba(180,150,100,0.25);
    flex-wrap: wrap;
  }}
  .tab-btn {{
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    padding: 10px 22px 12px;
    font-size: 0.95rem;
    font-weight: 600;
    color: #8a6e4e;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    margin-bottom: -2px;
  }}
  .tab-btn:hover {{ color: #5a3e1e; }}
  .tab-btn.active {{
    color: #5a3e1e;
    border-bottom: 3px solid #c17f3a;
    background: rgba(255,255,255,0.5);
  }}
  .tab-btn .role-badge {{
    font-size: 0.68rem;
    background: rgba(193,127,58,0.15);
    color: #8a5a1e;
    border-radius: 4px;
    padding: 1px 6px;
    margin-left: 6px;
    font-weight: 500;
  }}

  /* ── Tab Panels ── */
  .tab-panel {{ display: none; padding: 32px 40px; }}
  .tab-panel.active {{ display: block; }}

  .panel-intro {{
    background: rgba(255,255,255,0.65);
    border-left: 4px solid #c17f3a;
    border-radius: 0 8px 8px 0;
    padding: 14px 20px;
    margin-bottom: 28px;
    font-size: 0.9rem;
    color: #5a4030;
    line-height: 1.7;
  }}
  .panel-intro strong {{ color: #4a2e10; }}

  /* ── Workflow Steps ── */
  .workflow {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 18px;
  }}

  .step-card {{
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(180,150,100,0.25);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(100,70,30,0.08);
    transition: box-shadow 0.2s, transform 0.2s;
  }}
  .step-card:hover {{
    box-shadow: 0 6px 20px rgba(100,70,30,0.14);
    transform: translateY(-2px);
  }}

  .card-header {{
    padding: 14px 18px 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid rgba(180,150,100,0.18);
    cursor: pointer;
    user-select: none;
  }}
  .step-num {{
    width: 30px; height: 30px;
    border-radius: 50%;
    background: #c17f3a;
    color: white;
    font-size: 0.8rem;
    font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }}
  .step-num.blue {{ background: #5b8fa8; }}
  .step-num.green {{ background: #6a9a6e; }}
  .step-num.purple {{ background: #8a6aaa; }}

  .card-title {{
    flex: 1;
  }}
  .card-title .cmd {{
    font-family: "SF Mono", "Fira Code", monospace;
    font-size: 0.78rem;
    background: rgba(193,127,58,0.12);
    color: #8a4a10;
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 4px;
  }}
  .card-title h3 {{
    font-size: 0.95rem;
    font-weight: 600;
    color: #3a2e22;
    line-height: 1.3;
  }}
  .expand-icon {{
    color: #b09070;
    font-size: 0.8rem;
    transition: transform 0.2s;
    flex-shrink: 0;
  }}
  .step-card.expanded .expand-icon {{ transform: rotate(180deg); }}

  .card-body {{
    display: none;
    padding: 0 18px 16px;
  }}
  .step-card.expanded .card-body {{ display: block; }}

  .you-say {{
    margin-top: 14px;
    background: rgba(91,143,168,0.08);
    border-left: 3px solid #5b8fa8;
    border-radius: 0 6px 6px 0;
    padding: 10px 14px;
  }}
  .you-say .label {{
    font-size: 0.72rem;
    font-weight: 600;
    color: #5b8fa8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 5px;
  }}
  .you-say p {{
    font-size: 0.88rem;
    color: #3a4a58;
    line-height: 1.6;
  }}
  .you-say .voice-note {{
    font-size: 0.76rem;
    color: #7a8a98;
    margin-top: 4px;
    font-style: italic;
  }}

  .ai-reply {{
    margin-top: 10px;
    background: rgba(106,154,110,0.08);
    border-left: 3px solid #6a9a6e;
    border-radius: 0 6px 6px 0;
    padding: 10px 14px;
  }}
  .ai-reply .label {{
    font-size: 0.72rem;
    font-weight: 600;
    color: #4a8a4e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 5px;
  }}
  .ai-reply p {{
    font-size: 0.88rem;
    color: #2a4a2e;
    line-height: 1.6;
  }}

  .note-box {{
    margin-top: 10px;
    background: rgba(255,240,210,0.6);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 0.8rem;
    color: #6a4a1e;
    line-height: 1.5;
  }}
  .note-box::before {{
    content: "說明　";
    font-weight: 600;
    color: #8a5a1e;
  }}

  /* ── Status badges ── */
  .status-badge {{
    display: inline-block;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 8px;
    font-weight: 500;
  }}
  .badge-done {{ background: #d4edda; color: #2a6a30; }}
  .badge-active {{ background: #fff3cd; color: #7a5a00; }}
  .badge-pending {{ background: #f0e0f0; color: #6a3a7a; }}

  /* ── Architect special section ── */
  .arch-section {{
    margin-bottom: 28px;
  }}
  .arch-section h2 {{
    font-size: 1.05rem;
    font-weight: 700;
    color: #4a3520;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px dashed rgba(180,150,100,0.3);
  }}

  .flow-connector {{
    text-align: center;
    color: #b09070;
    font-size: 1.2rem;
    margin: 4px 0;
  }}

  /* ── Footer ── */
  footer {{
    text-align: center;
    padding: 24px 40px;
    font-size: 0.78rem;
    color: #a08060;
    border-top: 1px solid rgba(180,150,100,0.2);
    margin-top: 40px;
  }}

  @media (max-width: 700px) {{
    .tab-bar, .tab-panel {{ padding-left: 16px; padding-right: 16px; }}
    header {{ padding: 14px 16px; }}
    .workflow {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="overlay">

<!-- Header -->
<header>
  <img src="data:image/png;base64,{LOGO_B64}" alt="TeacherOS Logo">
  <div class="title-block">
    <h1>TeacherOS &nbsp;×&nbsp; 功能說明介面</h1>
    <p>AI 時代的教師工作作業系統　·　設計者：David　·　2026 春季</p>
  </div>
</header>

<!-- Tab Bar -->
<div class="tab-bar">
  <button class="tab-btn active" onclick="switchTab('english', this)">
    英文老師 <span class="role-badge">Block 1–4</span>
  </button>
  <button class="tab-btn" onclick="switchTab('homeroom', this)">
    導師 <span class="role-badge">HM Block 1–4</span>
  </button>
  <button class="tab-btn" onclick="switchTab('mainlesson', this)">
    主課程老師 <span class="role-badge">規劃中</span>
  </button>
  <button class="tab-btn" onclick="switchTab('architect', this)">
    架構師・新手老師 <span class="role-badge">系統建置</span>
  </button>
</div>

<!-- ══════════════════════════════════════════════
     TAB 1: 英文老師
══════════════════════════════════════════════ -->
<div id="tab-english" class="tab-panel active">
  <div class="panel-intro">
    <strong>英文老師工作流（Block 1 → 4）</strong><br>
    四個區塊形成完整閉環：學季規劃 → 課堂設計 → 歷程紀錄 → 期末結案。每次對話 AI 自動從進度錨點定位，不需重新解釋背景。語音輸入完全支援。
  </div>

  <div class="workflow">

    <!-- /load -->
    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num">0</div>
        <div class="card-title">
          <div class="cmd">/load</div>
          <h3>載入系統・確認當前位置</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「我要繼續 9C 英文課工作。」</p>
          <p class="voice-note">語音輸入可以，說「繼續上次」也可以</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>「已載入系統。9C 英文目前在 Block 二，下一步：設計第 1–2 週 45 分鐘課堂流程（小說研讀 + 語言工坊）。是否直接開始？」</p>
        </div>
        <div class="note-box">AI 自動從進度錨點（english-session.yaml）讀出現況。若有跨科目協調事項，會一併提醒（例如：班親會在第 3 週，課程節奏需留意）。</div>
      </div>
    </div>

    <!-- Block 1 -->
    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num">1</div>
        <div class="card-title">
          <div class="cmd">/syllabus</div>
          <h3>Block 1　學季整體規劃 <span class="status-badge badge-done">9C 已完成</span></h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「我要開始 9C 英文課學季大綱。」（並提供文本研究文件）</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>AI 讀取你的研究資料，設計三軸架構（小說 The House on Mango Street + 語言工坊 + 108 課綱），確認評量比例，產出完整教學大綱 .md 檔。</p>
        </div>
        <div class="note-box">這份大綱是整學期的基準文件，必須先完成才能進入 Block 2。完成後 AI 詢問是否輸出至 Google Drive（自動套用 Logo 與華德福水彩背景）。</div>
      </div>
    </div>

    <!-- Block 2 -->
    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num">2</div>
        <div class="card-title">
          <div class="cmd">/lesson</div>
          <h3>Block 2　45 分鐘課堂設計 <span class="status-badge badge-active">進行中</span></h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「幫我設計第一單元（第 1–2 週）的課堂流程。」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>產出 2-A 課堂流程（暖身 10 分 → 主活動 25 分 → 差異化任務 → 收尾 5 分）+ 2-B 差異化任務（A/B/C/D 四類學生各有不同任務與驗收機制）。</p>
        </div>
        <div class="note-box">AI 在設計前自動查閱 Block 3 最近三筆歷程紀錄，確保設計符合學生最新樣態。差異化任務每條策略都有具體課堂畫面感，可直接帶入教室。</div>
      </div>
    </div>

    <!-- Block 3 -->
    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num">3</div>
        <div class="card-title">
          <div class="cmd">隨時可用</div>
          <h3>Block 3　教學歷程紀錄</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說（語音口述）</div>
          <p>「今天 S03 和 S11 的討論很投入，但 S07 一直分心，我覺得是因為上週的任務對她太難了...」</p>
          <p class="voice-note">不需要整理格式，直接說就好</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>已解構並分流：S03、S11 紀錄寫入個別學生 log；S07 的任務難度觀察寫入 unit-logs.md；教師主觀反思寫入 teacher-reflections.md。所有紀錄自動附上日期標籤。</p>
        </div>
        <div class="note-box">可在 Block 2 課堂後隨時獨立插入，不需等待固定時間點。紀錄越豐富，Block 2 下一單元的差異化設計越精準。</div>
      </div>
    </div>

    <!-- Block 4 -->
    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num">4</div>
        <div class="card-title">
          <div class="cmd">期末啟動</div>
          <h3>Block 4　學習評量結案</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「學期結束了，幫我產出評量總表。」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>整合三維紀錄庫（學生 log + 班級進度 + 教學反思）與學季大綱核心任務，產出 student-assessments-YYYYMMDD.md，包含全班 200 字歷程摘要 + 每位學生的質性描述、大綱檢核、分數。</p>
        </div>
        <div class="note-box">AI 在此步驟才自動還原學生真實姓名（平時用 ID 保護隱私）。此結案檔案受本機 .gitignore 保護，不會上傳 GitHub。</div>
      </div>
    </div>

    <!-- /di-check -->
    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num blue">✓</div>
        <div class="card-title">
          <div class="cmd">/di-check</div>
          <h3>DI 雙軸合規檢查</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「幫我確認這個單元設計是否符合差異化教學要求。」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>依據能力 × 動機雙軸矩陣逐條檢查：A/B/C/D 四類皆有對應策略、每條策略有具體課堂畫面、無「鷹架支持」等抽象標籤。給出通過/警示/需修正的結構化回饋。</p>
        </div>
        <div class="note-box">任何時候都可以用 /di-check 驗證產出品質，確保差異化設計不流於表面。</div>
      </div>
    </div>

    <!-- /session-end -->
    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num blue">⟳</div>
        <div class="card-title">
          <div class="cmd">/session-end</div>
          <h3>對話收尾・進度同步</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「今天先到這裡。」或直接說「結束」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>條列今天確認的決定 → 更新進度錨點 → 更新系統狀態快照 → 說明下次工作起點是什麼。</p>
        </div>
        <div class="note-box">進度錨點（english-session.yaml）自動更新，下次對話開始時 AI 直接報告現況，無縫銜接。</div>
      </div>
    </div>

  </div><!-- /workflow -->
</div><!-- /tab-english -->


<!-- ══════════════════════════════════════════════
     TAB 2: 導師
══════════════════════════════════════════════ -->
<div id="tab-homeroom" class="tab-panel">
  <div class="panel-intro">
    <strong>導師工作流（HM Block 1–4）</strong><br>
    班級經營、行事曆管理、親師溝通、學生狀態追蹤，四個區塊覆蓋導師業務全週期。Google Calendar 直寫支援，文件輸出自動套用華德福視覺風格。
  </div>

  <div class="workflow">

    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num green">1</div>
        <div class="card-title">
          <div class="cmd">HM Block 1</div>
          <h3>學季行事規劃・時間軸建立</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「幫我規劃本學期 9C 導師工作的整體時間軸。」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>確認學季起訖、工作週數、重要節點（農場實習、戲劇、班親會），建立 calendar.md 班級行事曆，自動對齊英文課進度，標記需要跨科目協調的週次。</p>
        </div>
        <div class="note-box">導師行事曆與英文課進度錨點的 cross_module_notes 自動連動，跨線衝突即時提醒。</div>
      </div>
    </div>

    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num green">2</div>
        <div class="card-title">
          <div class="cmd">HM Block 2</div>
          <h3>Google Calendar 直寫</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「把春季班親會（3/21）寫進 Google Calendar，地點教室，提醒前兩天。」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>「已透過 gcal-write.py 將活動直接寫入你的 Google Calendar：春季班親會，2026-03-21 18:30，地點：教室，提醒設定：2 天前。」</p>
        </div>
        <div class="note-box">OAuth2 授權一次性設定，之後免操作。活動同時寫入本機 calendar.md 作為備份快照。</div>
      </div>
    </div>

    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num green">3</div>
        <div class="card-title">
          <div class="cmd">HM Block 3</div>
          <h3>親師溝通文件起草</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「幫我起草春季班親會通知，語氣溫暖，提到農場實習結束後的班親會意義。」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>產出通知草稿 .md 檔，語氣有人味，華德福精神自然融入但不堆砌術語。詢問是否輸出至 Google Drive，輸出後自動套用 Logo 與華德福水彩背景。</p>
        </div>
        <div class="note-box">已完成範例：9C 春季班親會通知（2026-03-01），存於 homeroom/content/comms/。輸出路徑：Google Drive /九年級C班/導師/親師溝通/。</div>
      </div>
    </div>

    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num green">4</div>
        <div class="card-title">
          <div class="cmd">HM Block 4</div>
          <h3>學生觀察・學期末整合</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說（語音口述）</div>
          <p>「S05 這週在農場很主動，完全不像他在課堂的樣子，我覺得他需要更多體力勞動的任務...」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>紀錄寫入學生觀察日誌，標記日期與情境（農場實習週），並提示：此觀察是否需要同步給英文老師或主課程老師？（跨科目協作提醒）</p>
        </div>
        <div class="note-box">導師視角的學生觀察與英文課的 di-profile 保持獨立，但可透過 cross_module_notes 進行跨線協調。</div>
      </div>
    </div>

  </div>
</div><!-- /tab-homeroom -->


<!-- ══════════════════════════════════════════════
     TAB 3: 主課程老師
══════════════════════════════════════════════ -->
<div id="tab-mainlesson" class="tab-panel">
  <div class="panel-intro">
    <strong>主課程工作流（規劃中）</strong><span class="status-badge badge-pending">模板建立中</span><br>
    主課程採連續三週（約 15 堂）的弧線敘事結構，每天 2 小時，與英文專科課截然不同。目前框架設計中，預計完成後即可啟動 9C 主課程 Block 1。
  </div>

  <div class="workflow">

    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num purple">★</div>
        <div class="card-title">
          <div class="cmd">主課程特色</div>
          <h3>15 堂連續弧線設計</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">主課程與英文課的不同</div>
          <p>主課程連續 3 週，每天同一個主題深耕，有完整敘事弧線（起點 → 現象探索 → 深化 → 收尾）。需要設計「有頭有尾」的主題旅程，而非分散的單元。</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 設計邏輯</div>
          <p>AI 協助設計 15 堂的完整弧線：起點故事（喚起）→ 現象學觀察 → 概念提煉 → 藝術整合 → 末日總結（統整印象）。差異化任務融入每個環節而非獨立切割。</p>
        </div>
        <div class="note-box">九年級主課程方向：當代歷史與現代世界形成、板塊構造、熱力學、黑白素描——對應九年級存在焦慮與尋找絕對真理的發展樣態。</div>
      </div>
    </div>

    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num purple">1</div>
        <div class="card-title">
          <div class="cmd">啟動方式</div>
          <h3>如何啟動主課程工作線</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">你說</div>
          <p>「我要開始 9C 主課程設計。」</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 回覆</div>
          <p>AI 先建立 main-lesson-di-template.md（若尚未存在），然後引導 Block 1：確認主題、15 堂弧線架構、與英文課及導師業務的跨線協調點。</p>
        </div>
        <div class="note-box">目前等待 main-lesson-di-template.md 完成後即可啟動。預計是 9C 英文 Block 2 完成後的下一個優先工作。</div>
      </div>
    </div>

    <div class="step-card" onclick="toggleCard(this)">
      <div class="card-header">
        <div class="step-num purple">→</div>
        <div class="card-title">
          <div class="cmd">跨線整合</div>
          <h3>主課程 × 英文課 × 導師 協作</h3>
        </div>
        <div class="expand-icon">▼</div>
      </div>
      <div class="card-body">
        <div class="you-say">
          <div class="label">場景</div>
          <p>主課程做黑白素描（藝術 × 光影極端對比），英文課同時在讀 The House on Mango Street（社群邊緣的敘事）。</p>
        </div>
        <div class="ai-reply">
          <div class="label">AI 協調提醒</div>
          <p>發現跨線共鳴：黑白素描的「光影過渡」與 Cisneros 文字中「邊界地帶」的意象高度呼應。建議在英文 vignette 寫作任務中加入「用文字描繪光影」的視覺化引導。</p>
        </div>
        <div class="note-box">跨線整合紀錄自動寫入 class-9c/project.yaml 的 cross_module_notes.active，兩個工作線的 AI 都能看見。</div>
      </div>
    </div>

  </div>
</div><!-- /tab-mainlesson -->


<!-- ══════════════════════════════════════════════
     TAB 4: 架構師・新手老師
══════════════════════════════════════════════ -->
<div id="tab-architect" class="tab-panel">
  <div class="panel-intro">
    <strong>你不只是使用者，你是架構師。</strong><br>
    每一位 Clone 這個 Repo 的老師，都在建立一套屬於自己的教師工作系統。TeacherOS 是一個可移植的框架，你用自己的身份、哲學與班級改寫它，AI 就認識你。這一頁說明如何「接手並建構你自己的 TeacherOS」。
  </div>

  <div class="arch-section">
    <h2>Phase 1　取得框架</h2>
    <div class="workflow">

      <div class="step-card" onclick="toggleCard(this)">
        <div class="card-header">
          <div class="step-num">A</div>
          <div class="card-title">
            <div class="cmd">git clone</div>
            <h3>下載完整系統框架</h3>
          </div>
          <div class="expand-icon">▼</div>
        </div>
        <div class="card-body">
          <div class="you-say">
            <div class="label">終端機執行</div>
            <p>git clone https://github.com/elliot200852-lab/waldorf-teacher-os.git</p>
          </div>
          <div class="ai-reply">
            <div class="label">你得到什麼</div>
            <p>完整的三層記憶系統框架：teacheros.yaml（身份層）+ project.yaml（專案層）+ working/*.yaml（工作線層）+ 所有 Block 1–4 模板 + 輸出腳本 build.sh。</p>
          </div>
          <div class="note-box">這個框架目前是 David 的版本。接下來你要把它改寫成你的版本。</div>
        </div>
      </div>

      <div class="step-card" onclick="toggleCard(this)">
        <div class="card-header">
          <div class="step-num">B</div>
          <div class="card-title">
            <div class="cmd">environment.env</div>
            <h3>建立個人設定檔</h3>
          </div>
          <div class="expand-icon">▼</div>
        </div>
        <div class="card-body">
          <div class="you-say">
            <div class="label">你做</div>
            <p>複製 setup/environment.env.example → 改名 environment.env，填入你的姓名、Google 帳號、Drive 資料夾路徑。</p>
          </div>
          <div class="ai-reply">
            <div class="label">效果</div>
            <p>build.sh 自動讀取你的帳號，輸出至你的 Google Drive，不需要手動輸入任何路徑。</p>
          </div>
          <div class="note-box">environment.env 已列入 .gitignore，不會上傳，不會洩漏個人資訊。</div>
        </div>
      </div>

    </div>
  </div>

  <div class="arch-section">
    <h2>Phase 2　寫入你的身份</h2>
    <div class="workflow">

      <div class="step-card" onclick="toggleCard(this)">
        <div class="card-header">
          <div class="step-num">C</div>
          <div class="card-title">
            <div class="cmd">teacheros.yaml</div>
            <h3>改寫教師身份層（Layer 1）</h3>
          </div>
          <div class="expand-icon">▼</div>
        </div>
        <div class="card-body">
          <div class="you-say">
            <div class="label">你改寫</div>
            <p>打開 ai-core/teacheros.yaml，填入你的姓名、任教年級與科目、教學哲學、工作偏好（語音輸入？文字輸入？偏好哪種 AI 工具？）</p>
          </div>
          <div class="ai-reply">
            <div class="label">效果</div>
            <p>任何 AI 讀取這份檔案後，立刻知道「你是誰、你教什麼、你想要什麼樣的協作風格」，不需要每次重新介紹自己。</p>
          </div>
          <div class="note-box">這是整個系統最重要的一份文件。改寫後，AI 就認識你了。</div>
        </div>
      </div>

      <div class="step-card" onclick="toggleCard(this)">
        <div class="card-header">
          <div class="step-num">D</div>
          <div class="card-title">
            <div class="cmd">project.yaml</div>
            <h3>建立你的班級結構（Layer 2）</h3>
          </div>
          <div class="expand-icon">▼</div>
        </div>
        <div class="card-body">
          <div class="you-say">
            <div class="label">你做</div>
            <p>複製 projects/class-8a/ 資料夾，改名為你的班級代碼（如 class-10b），修改 project.yaml 中的班級代碼、年級、科目。</p>
          </div>
          <div class="ai-reply">
            <div class="label">效果</div>
            <p>AI 讀取班級的 project.yaml 後，知道這個班的工作重點、目前狀態、跨科目協調事項，每次對話自動定位到正確的工作線。</p>
          </div>
          <div class="note-box">新班級的 status 預設為 dormant（休眠），對 AI 說「我要開始 {{班級}} 英文課」即可自動啟動。</div>
        </div>
      </div>

    </div>
  </div>

  <div class="arch-section">
    <h2>Phase 3　啟動第一次工作</h2>
    <div class="workflow">

      <div class="step-card" onclick="toggleCard(this)">
        <div class="card-header">
          <div class="step-num">E</div>
          <div class="card-title">
            <div class="cmd">第一次對話</div>
            <h3>Block 1 — 學季大綱設計</h3>
          </div>
          <div class="expand-icon">▼</div>
        </div>
        <div class="card-body">
          <div class="you-say">
            <div class="label">你說</div>
            <p>「我要開始 {{班級代碼}} 英文課學季大綱。」（並準備你的文本研究或教學構想）</p>
          </div>
          <div class="ai-reply">
            <div class="label">AI 回覆</div>
            <p>載入你的 teacheros.yaml，讀取班級 project.yaml，引導你完成 Block 1：課程主題確認 → 學期規劃 → 差異化策略設計 → 評量比例定案 → 輸出教學大綱到 Google Drive。</p>
          </div>
          <div class="note-box">整個流程 AI 主導，你只需要提供靈魂與素材：你對這班學生的了解、你想教什麼、你覺得什麼對他們最重要。</div>
        </div>
      </div>

      <div class="step-card" onclick="toggleCard(this)">
        <div class="card-header">
          <div class="step-num">F</div>
          <div class="card-title">
            <div class="cmd">新增班級/科目</div>
            <h3>擴充你的系統版圖</h3>
          </div>
          <div class="expand-icon">▼</div>
        </div>
        <div class="card-body">
          <div class="you-say">
            <div class="label">你說</div>
            <p>「我要新增一個班級科目：8B，科目是英文。」</p>
          </div>
          <div class="ai-reply">
            <div class="label">AI 回覆</div>
            <p>引導你複製班級結構 → 修改 project.yaml → 更新 system-status.yaml → 說明下一步如何填入學生 DI 資料（students.yaml）並啟動 Block 1。</p>
          </div>
          <div class="note-box">完整 SOP 在 setup/teacher-guide.md 第十節。任何新老師接手後，依照這個 SOP 就能建立自己的系統。</div>
        </div>
      </div>

    </div>
  </div>

  <div class="arch-section">
    <h2>三層記憶模型　系統核心</h2>
    <div style="background:rgba(255,255,255,0.7);border-radius:12px;padding:20px 24px;border:1px solid rgba(180,150,100,0.2);">
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;text-align:center;">
        <div style="background:rgba(193,127,58,0.1);border-radius:8px;padding:16px;">
          <div style="font-size:0.75rem;font-weight:700;color:#8a5a1e;letter-spacing:0.1em;margin-bottom:8px;">LAYER 1</div>
          <div style="font-size:1rem;font-weight:700;color:#4a2e10;margin-bottom:6px;">教師身份層</div>
          <div style="font-size:0.78rem;color:#7a5a2e;line-height:1.5;">teacheros.yaml<br>你是誰・你的哲學<br>長期穩定・不常改</div>
        </div>
        <div style="background:rgba(91,143,168,0.1);border-radius:8px;padding:16px;">
          <div style="font-size:0.75rem;font-weight:700;color:#3a6a88;letter-spacing:0.1em;margin-bottom:8px;">LAYER 2</div>
          <div style="font-size:1rem;font-weight:700;color:#1a3a4a;margin-bottom:6px;">專案記憶層</div>
          <div style="font-size:0.78rem;color:#3a5a6a;line-height:1.5;">project.yaml<br>班級脈絡・當前焦點<br>每班一份</div>
        </div>
        <div style="background:rgba(106,154,110,0.1);border-radius:8px;padding:16px;">
          <div style="font-size:0.75rem;font-weight:700;color:#2a6a3a;letter-spacing:0.1em;margin-bottom:8px;">LAYER 3</div>
          <div style="font-size:1rem;font-weight:700;color:#0a3a1a;margin-bottom:6px;">工作線記憶層</div>
          <div style="font-size:0.78rem;color:#2a5a3a;line-height:1.5;">working/*.yaml<br>Block/Step・下一步<br>每次對話更新</div>
        </div>
      </div>
    </div>
  </div>

</div><!-- /tab-architect -->

<footer>
  TeacherOS — AI 時代的教師工作作業系統　·　設計者：David（台灣華德福教師）<br>
  github.com/elliot200852-lab/waldorf-teacher-os　·　2026 春季展示版
</footer>

</div><!-- /overlay -->

<script>
  function switchTab(name, btn) {{
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    btn.classList.add('active');
  }}

  function toggleCard(card) {{
    card.classList.toggle('expanded');
  }}

  // Auto-expand first card in each tab for demo readiness
  document.addEventListener('DOMContentLoaded', () => {{
    document.querySelectorAll('.tab-panel').forEach(panel => {{
      const first = panel.querySelector('.step-card');
      if (first) first.classList.add('expanded');
    }});
  }});
</script>
</body>
</html>'''

output_path = f'{REPO}/publish/teacheros-demo.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = len(html.encode('utf-8')) // 1024
print(f"Generated: {output_path}")
print(f"File size: {size_kb} KB")
