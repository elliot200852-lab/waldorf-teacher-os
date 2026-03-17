import {
  AbsoluteFill,
  Audio,
  useCurrentFrame,
  interpolate,
  spring,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";

const bgMusic = staticFile("audio/tears-in-heaven.mp3");

// ── Utility Components ──

const FadeInText: React.FC<{
  children: React.ReactNode;
  delay?: number;
  className?: string;
  style?: React.CSSProperties;
}> = ({ children, delay = 0, className, style }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(frame - delay, [0, 25], [18, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{ opacity, transform: `translateY(${translateY}px)`, ...style }}
      className={className}
    >
      {children}
    </div>
  );
};

// ── Scenes ──

/** Title card */
const TitleScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 14 } });
  const subOpacity = interpolate(frame, [50, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center">
      <div style={{ transform: `scale(${scale})` }} className="text-center">
        <div className="text-[#b4a082] text-6xl tracking-wider leading-tight">
          從 Prompt Engineering
        </div>
        <div className="text-[#b4a082] text-6xl tracking-wider leading-tight mt-4">
          到 Context Engineering
        </div>
      </div>
      <div
        style={{ opacity: subOpacity }}
        className="text-[#e1ded7] text-3xl mt-12 tracking-wide"
      >
        AI 時代真正該學的事
      </div>
      <div
        style={{ opacity: subOpacity * 0.5 }}
        className="text-[#78736c] text-xl mt-8"
      >
        David — TeacherOS 建造日誌
      </div>
    </AbsoluteFill>
  );
};

/** Opening hook: AI forgot me */
const HookScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-start justify-center px-28">
      <FadeInText delay={5} className="text-[#e1ded7] text-[36px] leading-relaxed">
        上週四下午，我跟 AI 連續工作了大概三小時。
      </FadeInText>
      <FadeInText delay={30} className="text-[#e1ded7] text-[36px] leading-relaxed mt-6">
        前半段它的語氣完全對——
      </FadeInText>
      <FadeInText delay={45} className="text-[#e1ded7] text-[36px] leading-relaxed">
        知道我是誰、知道我的學生在什麼狀態。
      </FadeInText>
      <FadeInText delay={80} className="text-[#b4a082] text-[36px] leading-relaxed mt-10">
        後半段，它開始叫我「您」，
      </FadeInText>
      <FadeInText delay={100} className="text-[#b4a082] text-[36px] leading-relaxed">
        建議我「可以考慮融入多元評量策略
      </FadeInText>
      <FadeInText delay={110} className="text-[#b4a082] text-[36px] leading-relaxed">
        以提升學習成效」。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** It forgot me */
const ForgotScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleScale = spring({ frame, fps, delay: 5, config: { damping: 12 } });

  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center px-28">
      <div
        style={{ transform: `scale(${titleScale})` }}
        className="text-[#e1ded7] text-7xl mb-14"
      >
        它忘了我是誰。
      </div>
      <FadeInText delay={40} className="text-[#78736c] text-[32px] leading-relaxed text-center">
        不是重開對話那種忘，
      </FadeInText>
      <FadeInText delay={55} className="text-[#78736c] text-[32px] leading-relaxed text-center">
        是對話還在，但腦子裡最早裝進去的
      </FadeInText>
      <FadeInText delay={65} className="text-[#78736c] text-[32px] leading-relaxed text-center">
        東西被悄悄擠掉了。
      </FadeInText>
      <FadeInText delay={100} className="text-[#e1ded7] text-[32px] leading-relaxed text-center mt-10">
        就像一個同事跟你開會開到第三個小時，
      </FadeInText>
      <FadeInText delay={115} className="text-[#e1ded7] text-[32px] leading-relaxed text-center">
        眼神開始飄，回答變成安全的官話。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Paradigm shift */
const ParadigmScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center px-24">
      <FadeInText delay={10} className="text-[#78736c] text-[30px] mb-10">
        技術上這叫 context compaction。
      </FadeInText>
      <FadeInText delay={50} className="text-[#e1ded7] text-[38px] leading-relaxed text-center">
        但它真正讓我看懂的，不是技術問題，
      </FadeInText>
      <FadeInText delay={70} className="text-[#b4a082] text-[44px] mt-4">
        是一整個產業正在經歷的典範轉移。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Prompt Engineering era */
const PromptEraScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-start justify-center px-28">
      <FadeInText delay={5} className="text-[#e1ded7] text-[34px] leading-relaxed">
        2023 年，全世界在學 Prompt Engineering
      </FadeInText>
      <FadeInText delay={20} className="text-[#e1ded7] text-[34px] leading-relaxed">
        ——怎麼跟 AI 講話才能得到好答案。
      </FadeInText>
      <FadeInText delay={40} className="text-[#78736c] text-[30px] mt-4">
        角色扮演、思維鏈、Few-shot，一堆公式。
      </FadeInText>
      <FadeInText delay={75} className="text-[#e1ded7] text-[34px] mt-10 leading-relaxed">
        到了 2025 年中，Karpathy 公開說：
      </FadeInText>
      <FadeInText delay={95} className="text-[#b4a082] text-[38px] mt-4">
        別再叫它 prompt engineering 了，
      </FadeInText>
      <FadeInText delay={110} className="text-[#b4a082] text-[38px]">
        叫 Context Engineering。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** The Karpathy quote */
const QuoteScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center px-20">
      <FadeInText delay={10} className="text-[#b4a082] text-5xl leading-snug text-center italic">
        "the delicate art of filling
      </FadeInText>
      <FadeInText delay={25} className="text-[#b4a082] text-5xl leading-snug text-center italic">
        the context window
      </FadeInText>
      <FadeInText delay={40} className="text-[#b4a082] text-5xl leading-snug text-center italic">
        with just the right information
      </FadeInText>
      <FadeInText delay={55} className="text-[#b4a082] text-5xl leading-snug text-center italic">
        for the next step"
      </FadeInText>
      <FadeInText delay={80} className="text-[#78736c] text-2xl mt-10">
        — Karpathy
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Translation */
const TranslationScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center px-24">
      <FadeInText delay={10} className="text-[#78736c] text-[28px] mb-8">
        翻成白話：
      </FadeInText>
      <FadeInText delay={35} className="text-[#e1ded7] text-5xl leading-tight text-center">
        你不需要學怎麼「問」，
      </FadeInText>
      <FadeInText delay={55} className="text-[#e1ded7] text-5xl leading-tight text-center mt-4">
        你需要學怎麼
      </FadeInText>
      <FadeInText delay={70} className="text-[#b4a082] text-5xl leading-tight text-center mt-4">
        「讓 AI 在回答之前
      </FadeInText>
      <FadeInText delay={80} className="text-[#b4a082] text-5xl leading-tight text-center">
        腦袋裡裝對東西」。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Skill Engineering */
const SkillScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-start justify-center px-28">
      <FadeInText delay={5} className="text-[#e1ded7] text-[36px]">
        然後是 Skill Engineering。
      </FadeInText>
      <FadeInText delay={30} className="text-[#e1ded7] text-[32px] mt-6 leading-relaxed">
        把你反覆在做的事打包成一份規格書，
      </FadeInText>
      <FadeInText delay={45} className="text-[#e1ded7] text-[32px] leading-relaxed">
        AI 照著跑。
      </FadeInText>
      <FadeInText delay={75} className="text-[#b4a082] text-[36px] mt-10">
        我說了一句「設計一堂課」，四個字。
      </FadeInText>
      <FadeInText delay={100} className="text-[#b4a082] text-[36px] mt-4">
        四個字換來四十五分鐘的完整教學設計。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Three stages comparison */
const ThreeStagesScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center px-24 gap-10">
      <FadeInText delay={5} className="text-[#78736c] text-[30px]">
        Prompt Engineering
      </FadeInText>
      <FadeInText delay={15} className="text-[#78736c] text-[22px] -mt-6">
        寫一句好的問題——AI 自己做得比大多數人好
      </FadeInText>

      <FadeInText delay={40} className="text-[#e1ded7] text-[34px]">
        Context Engineering
      </FadeInText>
      <FadeInText delay={50} className="text-[#e1ded7] text-[24px] -mt-6">
        確保 AI 開口之前就知道你是誰
      </FadeInText>

      <FadeInText delay={70} className="text-[#b4a082] text-[34px]">
        Skill Engineering
      </FadeInText>
      <FadeInText delay={80} className="text-[#b4a082] text-[24px] -mt-6">
        確保 AI 在你說「開始」之後知道怎麼做
      </FadeInText>

      <FadeInText delay={110} className="text-[#e1ded7] text-5xl mt-6">
        後面兩個，只有人能做。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Mollick warning */
const WarningScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center px-28">
      <FadeInText delay={10} className="text-[#e1ded7] text-[34px] leading-relaxed text-center">
        能為 AI 組裝正確 context 的人，
      </FadeInText>
      <FadeInText delay={30} className="text-[#e1ded7] text-[34px] leading-relaxed text-center">
        跟只會打字聊天的人，
      </FadeInText>
      <FadeInText delay={50} className="text-[#e1ded7] text-[34px] leading-relaxed text-center">
        拿到的東西品質差距會越拉越大。
      </FadeInText>
      <FadeInText delay={85} className="text-[#b4a082] text-5xl mt-12">
        不是技術門檻，
      </FadeInText>
      <FadeInText delay={100} className="text-[#b4a082] text-5xl mt-2">
        是思考門檻。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Resolution: restart the conversation */
const ResolutionScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-start justify-center px-28">
      <FadeInText delay={5} className="text-[#e1ded7] text-[32px] leading-relaxed">
        AI 忘了我是誰之後，
      </FadeInText>
      <FadeInText delay={20} className="text-[#e1ded7] text-[32px] leading-relaxed">
        我做的第一件事不是重新貼一次設定，
      </FadeInText>
      <FadeInText delay={40} className="text-[#e1ded7] text-[32px] leading-relaxed">
        而是收工、開新對話、
      </FadeInText>
      <FadeInText delay={55} className="text-[#e1ded7] text-[32px] leading-relaxed">
        讓它重新載入完整的 context。
      </FadeInText>
      <FadeInText delay={80} className="text-[#b4a082] text-[38px] mt-8">
        三十秒，一切回來。
      </FadeInText>
      <FadeInText delay={110} className="text-[#78736c] text-[28px] mt-8 leading-relaxed">
        知道什麼時候該重開，
      </FadeInText>
      <FadeInText delay={125} className="text-[#78736c] text-[28px] leading-relaxed">
        也是 context engineering 的一部分。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** 40% capacity */
const CapacityScene: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center">
      <FadeInText delay={10} className="text-[#e1ded7] text-[34px]">
        當 AI 腦袋塞滿的時候，
      </FadeInText>
      <FadeInText delay={45} className="text-[#b4a082] text-7xl mt-8">
        它大概只剩四成的行為能力。
      </FadeInText>
    </AbsoluteFill>
  );
};

/** Closing / signature */
const ClosingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeOut = interpolate(frame, [200, 270], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className="bg-[#12121a] flex flex-col items-center justify-center" style={{ opacity: fadeOut }}>
      <FadeInText delay={10} className="text-[#78736c] text-[30px]">
        在 AI 時代，
      </FadeInText>
      <FadeInText delay={35} className="text-[#b4a082] text-6xl mt-6">
        「把自己說清楚」
      </FadeInText>
      <FadeInText delay={60} className="text-[#e1ded7] text-[34px] mt-6">
        可能比「會跟 AI 說話」
      </FadeInText>
      <FadeInText delay={75} className="text-[#e1ded7] text-[34px]">
        重要得多。
      </FadeInText>
      <FadeInText delay={110} className="text-[#78736c] text-2xl mt-16">
        — David，華德福教師
      </FadeInText>
    </AbsoluteFill>
  );
};

// ── Main Composition ──
// 120s @ 30fps = 3600 frames

export const ContextEngineering: React.FC = () => {
  const frame = useCurrentFrame();
  // Audio fade out in last 5 seconds (frames 3450-3600)
  const audioVolume = interpolate(frame, [0, 30, 3450, 3600], [0, 0.4, 0.4, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className="bg-[#12121a]">
      <Audio src={bgMusic} volume={audioVolume} />

      {/* 0-8s: Title */}
      <Sequence from={0} durationInFrames={240}>
        <TitleScene />
      </Sequence>

      {/* 8-18s: Opening hook */}
      <Sequence from={240} durationInFrames={300}>
        <HookScene />
      </Sequence>

      {/* 18-27s: It forgot me */}
      <Sequence from={540} durationInFrames={270}>
        <ForgotScene />
      </Sequence>

      {/* 27-33s: Paradigm shift */}
      <Sequence from={810} durationInFrames={180}>
        <ParadigmScene />
      </Sequence>

      {/* 33-43s: Prompt Engineering era */}
      <Sequence from={990} durationInFrames={300}>
        <PromptEraScene />
      </Sequence>

      {/* 43-50s: Karpathy quote */}
      <Sequence from={1290} durationInFrames={210}>
        <QuoteScene />
      </Sequence>

      {/* 50-57s: Translation */}
      <Sequence from={1500} durationInFrames={210}>
        <TranslationScene />
      </Sequence>

      {/* 57-66s: Skill Engineering */}
      <Sequence from={1710} durationInFrames={270}>
        <SkillScene />
      </Sequence>

      {/* 66-76s: Three stages */}
      <Sequence from={1980} durationInFrames={300}>
        <ThreeStagesScene />
      </Sequence>

      {/* 76-84s: Mollick warning */}
      <Sequence from={2280} durationInFrames={240}>
        <WarningScene />
      </Sequence>

      {/* 84-95s: Resolution */}
      <Sequence from={2520} durationInFrames={330}>
        <ResolutionScene />
      </Sequence>

      {/* 95-103s: 40% capacity */}
      <Sequence from={2850} durationInFrames={240}>
        <CapacityScene />
      </Sequence>

      {/* 103-120s: Closing */}
      <Sequence from={3090} durationInFrames={510}>
        <ClosingScene />
      </Sequence>
    </AbsoluteFill>
  );
};
