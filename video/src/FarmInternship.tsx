import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Img,
  staticFile,
} from "remotion";

// --- Photo paths ---
const photos = {
  chalkboard: staticFile("photos/S__103301155.jpg"),
  exhibitA: staticFile("photos/S__103301156.jpg"),
  exhibitB: staticFile("photos/S__103301158.jpg"),
  exhibitC: staticFile("photos/S__103301160.jpg"),
  sisyphusSlide: staticFile("photos/S__103301162.jpg"),
  presentA: staticFile("photos/S__103301163.jpg"),
  presentB: staticFile("photos/S__103301167.jpg"),
  presentC: staticFile("photos/S__103301170.jpg"),
  presentD: staticFile("photos/S__103301174.jpg"),
  presentE: staticFile("photos/S__103301179.jpg"),
};

// --- Utility ---

/** Full-bleed background image with dark overlay */
const PhotoBg: React.FC<{
  src: string;
  overlayOpacity?: number;
}> = ({ src, overlayOpacity = 0.55 }) => {
  return (
    <>
      <Img
        src={src}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: `rgba(28, 25, 23, ${overlayOpacity})`,
        }}
      />
    </>
  );
};

/** Ken Burns slow zoom on a photo */
const KenBurns: React.FC<{
  src: string;
  overlayOpacity?: number;
  zoomStart?: number;
  zoomEnd?: number;
}> = ({ src, overlayOpacity = 0.5, zoomStart = 1.0, zoomEnd = 1.12 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], [zoomStart, zoomEnd], {
    extrapolateRight: "clamp",
  });
  return (
    <>
      <Img
        src={src}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: `rgba(28, 25, 23, ${overlayOpacity})`,
        }}
      />
    </>
  );
};

/** Crossfade between two photos */
const PhotoCrossfade: React.FC<{
  sources: string[];
  interval?: number;
  fadeDuration?: number;
  overlayOpacity?: number;
}> = ({ sources, interval = 90, fadeDuration = 20, overlayOpacity = 0.45 }) => {
  const frame = useCurrentFrame();
  const idx = Math.floor(frame / interval) % sources.length;
  const nextIdx = (idx + 1) % sources.length;
  const progress = (frame % interval);
  const fadeIn = progress < fadeDuration
    ? interpolate(progress, [0, fadeDuration], [0, 1], { extrapolateRight: "clamp" })
    : 1;

  return (
    <>
      <Img
        src={sources[nextIdx]}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
      <Img
        src={sources[idx]}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: fadeIn,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: `rgba(28, 25, 23, ${overlayOpacity})`,
        }}
      />
    </>
  );
};

// --- Scenes ---

/** 0-5s: Title over chalkboard */
const TitleScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = spring({ frame, fps, config: { damping: 12 } });
  const subtitleOpacity = interpolate(frame, [40, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <KenBurns src={photos.chalkboard} overlayOpacity={0.5} />
      <div className="relative z-10 flex flex-col items-center justify-center h-full">
        <div
          style={{ transform: `scale(${titleScale})` }}
          className="text-white text-8xl font-bold tracking-widest drop-shadow-lg"
        >
          農場實習
        </div>
        <div
          style={{ opacity: subtitleOpacity }}
          className="text-stone-300 text-3xl mt-8 tracking-wider drop-shadow"
        >
          九年級 ── 114 學年
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** 5-12s: Day 1 */
const Day1Scene: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [5, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const detailOpacity = interpolate(frame, [40, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const detail2Opacity = interpolate(frame, [80, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <PhotoCrossfade
        sources={[photos.exhibitA, photos.exhibitB]}
        interval={105}
        overlayOpacity={0.55}
      />
      <div className="relative z-10 flex flex-col items-start justify-center h-full px-24">
        <div
          style={{ opacity: titleOpacity }}
          className="text-amber-400 text-3xl tracking-widest mb-4"
        >
          3/11 ── 回校第一天
        </div>
        <div
          style={{ opacity: titleOpacity }}
          className="text-white text-6xl font-bold mb-10"
        >
          沉澱與重新看見
        </div>
        <div
          style={{ opacity: detailOpacity }}
          className="text-stone-300 text-2xl leading-relaxed"
        >
          混班分組 · 兩場深度討論
        </div>
        <div
          style={{ opacity: detail2Opacity }}
          className="text-stone-400 text-2xl mt-4"
        >
          發表會準備啟動
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Poem interlude A: 石頭 → 走下山 */
const PoemA: React.FC = () => {
  const frame = useCurrentFrame();

  const lines = [
    { text: "石頭是眾神給的。", delay: 10 },
    { text: "山坡是眾神選的。", delay: 35 },
    { text: "那永遠滾落的結局，也是眾神寫好的。", delay: 60 },
    { text: "", delay: 0 },
    { text: "但走下山的那段路，是他自己的。", delay: 110 },
  ];

  return (
    <AbsoluteFill className="bg-stone-900 flex items-center justify-center px-20">
      <div className="text-stone-200 text-4xl leading-loose space-y-2 max-w-5xl">
        {lines.map((line, i) => {
          if (line.text === "") return <div key={i} className="h-6" />;
          const opacity = interpolate(frame - line.delay, [0, 20], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const translateY = interpolate(frame - line.delay, [0, 20], [15, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <div
              key={i}
              style={{ opacity, transform: `translateY(${translateY}px)` }}
              className={
                line.text.includes("他自己的")
                  ? "text-amber-400 font-normal"
                  : "font-light"
              }
            >
              {line.text}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** 17-24s: Day 2 */
const Day2Scene: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [5, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const detailOpacity = interpolate(frame, [40, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const detail2Opacity = interpolate(frame, [80, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <PhotoCrossfade
        sources={[photos.exhibitC, photos.sisyphusSlide]}
        interval={105}
        overlayOpacity={0.55}
      />
      <div className="relative z-10 flex flex-col items-start justify-center h-full px-24">
        <div
          style={{ opacity: titleOpacity }}
          className="text-amber-400 text-3xl tracking-widest mb-4"
        >
          3/12 ── 回校第二天
        </div>
        <div
          style={{ opacity: titleOpacity }}
          className="text-white text-6xl font-bold mb-10"
        >
          打磨與彩排
        </div>
        <div
          style={{ opacity: detailOpacity }}
          className="text-stone-300 text-2xl leading-relaxed"
        >
          更深層反思 · 個人的轉變
        </div>
        <div
          style={{ opacity: detail2Opacity }}
          className="text-stone-400 text-2xl mt-4"
        >
          場布統籌 · 技術走位 · 講綱定稿
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Poem interlude B: 徒勞裡的節奏 */
const PoemB: React.FC = () => {
  const frame = useCurrentFrame();

  const lines = [
    { text: "人會在徒勞裡找到節奏，", delay: 10 },
    { text: "節奏裡長出意願，", delay: 40 },
    { text: "意願裡，長出微笑。", delay: 65 },
    { text: "", delay: 0 },
    { text: "薛西弗斯從未抵達終點。", delay: 100 },
    { text: "但每一次轉身的時刻，他比眾神自由。", delay: 130 },
  ];

  return (
    <AbsoluteFill>
      <PhotoBg src={photos.sisyphusSlide} overlayOpacity={0.7} />
      <div className="relative z-10 flex items-center justify-center h-full px-20">
        <div className="text-stone-200 text-4xl leading-loose space-y-2 max-w-5xl">
          {lines.map((line, i) => {
            if (line.text === "") return <div key={i} className="h-6" />;
            const opacity = interpolate(frame - line.delay, [0, 20], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const translateY = interpolate(frame - line.delay, [0, 20], [15, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={i}
                style={{ opacity, transform: `translateY(${translateY}px)` }}
                className={
                  line.text.includes("他比眾神自由")
                    ? "text-amber-400 font-normal"
                    : "font-light"
                }
              >
                {line.text}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** 29-42s: Day 3 — presentation photos cycling */
const Day3Scene: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [5, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const subtitleOpacity = interpolate(frame, [40, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const statsOpacity = interpolate(frame, [80, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <PhotoCrossfade
        sources={[
          photos.presentA,
          photos.presentB,
          photos.presentC,
          photos.presentD,
          photos.presentE,
        ]}
        interval={75}
        overlayOpacity={0.45}
      />
      <div className="relative z-10 flex flex-col items-start justify-center h-full px-24">
        <div
          style={{ opacity: titleOpacity }}
          className="text-amber-400 text-3xl tracking-widest mb-4"
        >
          3/13 ── 成果發表會
        </div>
        <div
          style={{ opacity: titleOpacity }}
          className="text-white text-6xl font-bold mb-10"
        >
          十九座農場的故事
        </div>
        <div
          style={{ opacity: subtitleOpacity }}
          className="text-stone-300 text-2xl leading-relaxed"
        >
          書面展 · 上午十組報告 · 下午九組報告
        </div>
        <div
          style={{ opacity: statsOpacity }}
          className="text-stone-400 text-2xl mt-4"
        >
          89 位學生 · 全台八縣市 · 10 天實習
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** 42-52s: Reflection — the spine remembers */
const ReflectionScene: React.FC = () => {
  const frame = useCurrentFrame();

  const line1 = interpolate(frame, [15, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const line2 = interpolate(frame, [60, 85], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const line3 = interpolate(frame, [130, 160], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className="bg-stone-900 flex flex-col items-center justify-center px-20 gap-12">
      <div
        style={{ opacity: line1 }}
        className="text-stone-300 text-4xl leading-relaxed text-center"
      >
        手上什麼也沒帶回來。
      </div>
      <div
        style={{ opacity: line2 }}
        className="text-stone-200 text-4xl leading-relaxed text-center"
      >
        但脊椎記得一個
        <br />
        沒有人命令過的彎度。
      </div>
      <div
        style={{ opacity: line3 }}
        className="text-amber-400 text-4xl tracking-wider"
      >
        那是你的。
      </div>
    </AbsoluteFill>
  );
};

/** 52-60s: End card */
const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, delay: 10, config: { damping: 15 } });
  const fadeOut = interpolate(frame, [180, 240], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      <PhotoBg src={photos.chalkboard} overlayOpacity={0.7} />
      <div
        className="relative z-10 flex flex-col items-center justify-center h-full"
        style={{ transform: `scale(${scale})` }}
      >
        <div className="text-white text-5xl tracking-widest drop-shadow">
          九年級農場實習
        </div>
        <div className="text-stone-400 text-2xl mt-6">
          114 學年 · 成果發表會
        </div>
        <div className="text-stone-500 text-xl mt-10">
          教師：林信宏（David）
        </div>
      </div>
    </AbsoluteFill>
  );
};

// --- Main Composition ---
// 60s @ 30fps = 1800 frames

export const FarmInternship: React.FC = () => {
  return (
    <AbsoluteFill className="bg-stone-900">
      {/* 0-5s: Title */}
      <Sequence from={0} durationInFrames={150}>
        <TitleScene />
      </Sequence>

      {/* 5-12s: Day 1 */}
      <Sequence from={150} durationInFrames={210}>
        <Day1Scene />
      </Sequence>

      {/* 12-17s: Poem A */}
      <Sequence from={360} durationInFrames={180}>
        <PoemA />
      </Sequence>

      {/* 17-24s: Day 2 */}
      <Sequence from={540} durationInFrames={210}>
        <Day2Scene />
      </Sequence>

      {/* 24-30s: Poem B */}
      <Sequence from={750} durationInFrames={180}>
        <PoemB />
      </Sequence>

      {/* 30-43s: Day 3 */}
      <Sequence from={930} durationInFrames={390}>
        <Day3Scene />
      </Sequence>

      {/* 43-53s: Reflection */}
      <Sequence from={1320} durationInFrames={300}>
        <ReflectionScene />
      </Sequence>

      {/* 53-60s: End card */}
      <Sequence from={1620} durationInFrames={180}>
        <EndCard />
      </Sequence>
    </AbsoluteFill>
  );
};
