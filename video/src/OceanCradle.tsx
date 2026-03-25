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
  chalkboard: staticFile("photos/A005/chalkboard.png"),
  kuroshioTemp: staticFile("photos/A005/kuroshio-temp.png"),
  oceanGyres: staticFile("photos/A005/ocean-gyres.png"),
  coral: staticFile("photos/A005/coral.jpg"),
  fishSchool: staticFile("photos/A005/fish-school.jpg"),
  taiwanSatellite: staticFile("photos/A005/taiwan-strait-satellite.jpg"),
  taiwanDetail: staticFile("photos/A005/taiwan-strait-detail.jpg"),
  deepOcean: staticFile("photos/A005/deep-ocean.jpg"),
};

// --- Utility Components ---

const KenBurns: React.FC<{
  src: string;
  overlayOpacity?: number;
  zoomStart?: number;
  zoomEnd?: number;
  panX?: number;
}> = ({ src, overlayOpacity = 0.5, zoomStart = 1.0, zoomEnd = 1.12, panX = 0 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], [zoomStart, zoomEnd], {
    extrapolateRight: "clamp",
  });
  const tx = interpolate(frame, [0, durationInFrames], [0, panX], {
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
          transform: `scale(${scale}) translateX(${tx}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: `rgba(10, 25, 50, ${overlayOpacity})`,
        }}
      />
    </>
  );
};

const CrossfadeBg: React.FC<{
  src1: string;
  src2: string;
  crossfadeStart?: number;
  crossfadeEnd?: number;
  overlayOpacity?: number;
}> = ({ src1, src2, crossfadeStart = 0.4, crossfadeEnd = 0.6, overlayOpacity = 0.5 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const mix = interpolate(
    frame,
    [durationInFrames * crossfadeStart, durationInFrames * crossfadeEnd],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const scale1 = interpolate(frame, [0, durationInFrames], [1.0, 1.1], {
    extrapolateRight: "clamp",
  });
  const scale2 = interpolate(frame, [0, durationInFrames], [1.05, 1.15], {
    extrapolateRight: "clamp",
  });
  return (
    <>
      <Img
        src={src1}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 1 - mix,
          transform: `scale(${scale1})`,
        }}
      />
      <Img
        src={src2}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: mix,
          transform: `scale(${scale2})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: `rgba(10, 25, 50, ${overlayOpacity})`,
        }}
      />
    </>
  );
};

const FadeText: React.FC<{
  text: string;
  delay: number;
  className?: string;
  style?: React.CSSProperties;
  speed?: number;
}> = ({ text, delay, className = "", style = {}, speed = 20 }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, speed], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(frame - delay, [0, speed], [15, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{ opacity, transform: `translateY(${translateY}px)`, ...style }}
      className={className}
    >
      {text}
    </div>
  );
};

// --- Scenes ---

/** Scene 1: Title over chalkboard (7s = 210 frames) */
const TitleScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleScale = spring({ frame, fps, config: { damping: 12 } });
  const subtitleOpacity = interpolate(frame, [40, 65], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const seriesOpacity = interpolate(frame, [75, 95], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <KenBurns src={photos.chalkboard} overlayOpacity={0.45} zoomEnd={1.08} />
      <div className="relative z-10 flex flex-col items-center justify-center h-full">
        <div
          style={{ opacity: seriesOpacity }}
          className="text-sky-300 text-2xl tracking-[0.5em] mb-6"
        >
          臺灣的故事 · A005
        </div>
        <div
          style={{ transform: `scale(${titleScale})` }}
          className="text-white text-8xl font-bold tracking-widest drop-shadow-lg"
        >
          海的搖籃
        </div>
        <div
          style={{ opacity: subtitleOpacity }}
          className="text-sky-200 text-3xl mt-8 tracking-wider drop-shadow"
        >
          黑潮與臺灣
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 2: The Ocean River (11s = 330 frames) — kuroshioTemp → taiwanSatellite crossfade */
const OceanRiverScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <CrossfadeBg
        src1={photos.kuroshioTemp}
        src2={photos.taiwanSatellite}
        crossfadeStart={0.55}
        crossfadeEnd={0.75}
        overlayOpacity={0.5}
      />
      <div className="relative z-10 flex flex-col items-start justify-center h-full px-24">
        <FadeText
          text="臺灣四面環海"
          delay={8}
          className="text-sky-300 text-3xl tracking-widest mb-4"
        />
        <FadeText
          text="海裡有一條看不見的河"
          delay={35}
          className="text-white text-6xl font-bold mb-10"
        />
        <FadeText
          text="它叫做——黑潮"
          delay={75}
          className="text-sky-200 text-5xl font-bold"
        />
        <FadeText
          text="從菲律賓出發，沿著臺灣東岸往北奔跑"
          delay={120}
          className="text-stone-300 text-2xl mt-8"
        />
        <FadeText
          text="一百到兩百公里寬 · 深達千公尺"
          delay={170}
          className="text-stone-400 text-2xl mt-4"
        />
        <FadeText
          text="每秒鐘都在流動"
          delay={220}
          className="text-sky-400 text-2xl mt-4"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 3: The Kuroshio's Path (9s = 270 frames) — oceanGyres with pan */
const KuroshioPathScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <KenBurns src={photos.oceanGyres} overlayOpacity={0.45} zoomEnd={1.18} panX={-30} />
      <div className="relative z-10 flex flex-col items-end justify-center h-full px-24">
        <FadeText
          text="黑潮從哪裡來？"
          delay={8}
          className="text-amber-400 text-3xl tracking-widest mb-4"
        />
        <FadeText
          text="北赤道洋流撞上菲律賓群島"
          delay={45}
          className="text-white text-4xl font-bold mb-4 text-right"
        />
        <FadeText
          text="分成兩股——往北的那一股"
          delay={90}
          className="text-stone-200 text-3xl text-right"
        />
        <FadeText
          text="就是黑潮"
          delay={130}
          className="text-sky-300 text-5xl font-bold mt-6 text-right"
        />
        <FadeText
          text="全世界第二大洋流"
          delay={175}
          className="text-stone-400 text-2xl mt-4 text-right"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 4: Why Black (10s = 300 frames) — deepOcean → taiwanDetail crossfade */
const WhyBlackScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <CrossfadeBg
        src1={photos.deepOcean}
        src2={photos.taiwanDetail}
        crossfadeStart={0.6}
        crossfadeEnd={0.8}
        overlayOpacity={0.6}
      />
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-20 gap-5">
        <FadeText
          text="為什麼叫「黑潮」？"
          delay={8}
          className="text-stone-300 text-3xl text-center leading-relaxed"
        />
        <FadeText
          text="因為它的水太乾淨了"
          delay={45}
          className="text-stone-200 text-3xl text-center leading-relaxed"
        />
        <FadeText
          text="陽光一照進去，一直往深處穿"
          delay={90}
          className="text-stone-200 text-3xl text-center leading-relaxed"
        />
        <FadeText
          text="沒有東西把光彈回來"
          delay={130}
          className="text-stone-300 text-3xl text-center leading-relaxed"
        />
        <FadeText
          text="深到幾乎像墨水一樣"
          delay={185}
          className="text-sky-300 text-4xl text-center tracking-wider mt-4"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 5: The Gift — Warmth (12s = 360 frames) — coral with KenBurns */
const WarmthScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <KenBurns src={photos.coral} overlayOpacity={0.45} zoomEnd={1.15} />
      <div className="relative z-10 flex flex-col items-start justify-center h-full px-24">
        <FadeText
          text="黑潮最大的禮物"
          delay={8}
          className="text-sky-300 text-3xl tracking-widest mb-4"
        />
        <FadeText
          text="溫暖"
          delay={40}
          className="text-white text-7xl font-bold mb-10"
        />
        <FadeText
          text="攝氏二十四到二十八度的海水"
          delay={85}
          className="text-stone-200 text-2xl"
        />
        <FadeText
          text="從南方帶來了熱帶的生命力"
          delay={130}
          className="text-stone-300 text-2xl mt-4"
        />
        <FadeText
          text="臺灣珊瑚種類佔全世界三分之一"
          delay={185}
          className="text-amber-300 text-3xl mt-6 font-bold"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 6: Marine Life (11s = 330 frames) — coral → fish crossfade */
const MarineLifeScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <CrossfadeBg
        src1={photos.coral}
        src2={photos.fishSchool}
        crossfadeStart={0.25}
        crossfadeEnd={0.45}
        overlayOpacity={0.45}
      />
      <div className="relative z-10 flex flex-col items-start justify-end h-full px-24 pb-28">
        <FadeText
          text="珊瑚礁是「海中的熱帶雨林」"
          delay={8}
          className="text-sky-200 text-3xl tracking-wider mb-4"
        />
        <FadeText
          text="魚、蝦、海龜、章魚、海星"
          delay={55}
          className="text-white text-4xl font-bold mb-6"
        />
        <FadeText
          text="上千種生物在這裡吃飯、睡覺、養小孩"
          delay={105}
          className="text-stone-300 text-2xl"
        />
        <FadeText
          text="全部因為一條從南方流來的溫暖的河"
          delay={165}
          className="text-stone-400 text-2xl mt-4"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 7: Paradox (12s = 360 frames) — oceanGyres → deepOcean crossfade */
const ParadoxScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <CrossfadeBg
        src1={photos.oceanGyres}
        src2={photos.deepOcean}
        crossfadeStart={0.5}
        crossfadeEnd={0.7}
        overlayOpacity={0.6}
      />
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-20 gap-6">
        <FadeText
          text="黑潮悖論"
          delay={8}
          className="text-amber-400 text-4xl tracking-widest"
        />
        <FadeText
          text="水這麼乾淨，養分這麼少"
          delay={45}
          className="text-stone-300 text-3xl text-center"
        />
        <FadeText
          text="魚群卻特別多、特別肥"
          delay={85}
          className="text-white text-4xl font-bold text-center"
        />
        <FadeText
          text="因為黑潮會把海底的養分翻攪上來"
          delay={135}
          className="text-stone-300 text-3xl text-center"
        />
        <FadeText
          text="就像用湯匙攪一碗湯"
          delay={185}
          className="text-sky-300 text-3xl text-center"
        />
        <FadeText
          text="底下沉的東西就浮上來了"
          delay={230}
          className="text-stone-400 text-2xl text-center"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 8: Taiwan from the Sea (11s = 330 frames) — taiwanSatellite → taiwanDetail */
const TaiwanFromSeaScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <CrossfadeBg
        src1={photos.taiwanSatellite}
        src2={photos.kuroshioTemp}
        crossfadeStart={0.45}
        crossfadeEnd={0.65}
        overlayOpacity={0.55}
      />
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-20 gap-6">
        <FadeText
          text="這座島嶼並不孤單"
          delay={8}
          className="text-sky-300 text-4xl tracking-wider"
        />
        <FadeText
          text="海不是阻隔，是連結"
          delay={60}
          className="text-white text-5xl font-bold text-center"
        />
        <FadeText
          text="黑潮帶來溫暖、帶來生命"
          delay={120}
          className="text-stone-300 text-3xl text-center"
        />
        <FadeText
          text="也帶來了故事"
          delay={175}
          className="text-stone-300 text-3xl text-center"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 9: Pull quote (14s = 420 frames) */
const PullQuoteScene: React.FC = () => {
  const frame = useCurrentFrame();

  const line1 = interpolate(frame, [15, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const line2 = interpolate(frame, [60, 85], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const line3 = interpolate(frame, [120, 150], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const line4 = interpolate(frame, [210, 250], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className="bg-[#0a1932] flex flex-col items-center justify-center px-20 gap-6">
      <div style={{ opacity: line1 }} className="text-stone-300 text-3xl text-center leading-relaxed">
        你腳下的土地，是板塊推上來的
      </div>
      <div style={{ opacity: line2 }} className="text-stone-300 text-3xl text-center leading-relaxed">
        你喝的水，是河流帶下來的
      </div>
      <div style={{ opacity: line3 }} className="text-stone-300 text-3xl text-center leading-relaxed">
        你泡的溫泉，是火山燒出來的
      </div>
      <div style={{ opacity: line4 }} className="text-sky-300 text-4xl text-center tracking-wider mt-6 leading-relaxed">
        而你吃的魚、你看到的珊瑚、你感受到的溫暖
        <br />
        那是海，從很遠很遠的南方
        <br />
        一路送過來給你的
      </div>
    </AbsoluteFill>
  );
};

/** Scene 10: Next Story Teaser (9s = 270 frames) */
const NextStoryScene: React.FC = () => {
  return (
    <AbsoluteFill>
      <KenBurns src={photos.deepOcean} overlayOpacity={0.7} zoomEnd={1.06} />
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-20 gap-6">
        <FadeText
          text="下一次"
          delay={15}
          className="text-stone-400 text-3xl tracking-widest"
        />
        <FadeText
          text="我們要去認識一群很早很早"
          delay={55}
          className="text-stone-200 text-3xl text-center"
        />
        <FadeText
          text="就在臺灣生活的人"
          delay={95}
          className="text-stone-200 text-3xl text-center"
        />
        <FadeText
          text="他們划著獨木舟"
          delay={140}
          className="text-sky-300 text-4xl text-center mt-4"
        />
        <FadeText
          text="在太平洋上來去自如"
          delay={180}
          className="text-sky-300 text-4xl text-center font-bold"
        />
      </div>
    </AbsoluteFill>
  );
};

/** Scene 11: End card (9s = 270 frames) */
const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, delay: 10, config: { damping: 15 } });
  const fadeOut = interpolate(frame, [200, 270], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      <KenBurns src={photos.chalkboard} overlayOpacity={0.65} zoomEnd={1.04} />
      <div
        className="relative z-10 flex flex-col items-center justify-center h-full"
        style={{ transform: `scale(${scale})` }}
      >
        <div className="text-sky-300 text-2xl tracking-[0.3em] mb-6">
          臺灣的故事
        </div>
        <div className="text-white text-5xl tracking-widest drop-shadow">
          海的搖籃
        </div>
        <div className="text-stone-400 text-2xl mt-6">
          黑潮與臺灣
        </div>
        <div className="text-stone-500 text-xl mt-10">
          教師：林信宏（David）
        </div>
        <div className="text-stone-600 text-lg mt-4">
          慈心華德福學校
        </div>
      </div>
    </AbsoluteFill>
  );
};

// --- Main Composition ---
// 2 min = 120s @ 30fps = 3600 frames
// 11 scenes, faster rhythm, more image crossfades

export const OceanCradle: React.FC = () => {
  return (
    <AbsoluteFill className="bg-[#0a1932]">
      {/* 1. Title (0-7s, 210f) */}
      <Sequence from={0} durationInFrames={210}>
        <TitleScene />
      </Sequence>

      {/* 2. Ocean River (7-18s, 330f) — kuroshioTemp → taiwanSatellite */}
      <Sequence from={210} durationInFrames={330}>
        <OceanRiverScene />
      </Sequence>

      {/* 3. Kuroshio Path (18-27s, 270f) — oceanGyres with pan */}
      <Sequence from={540} durationInFrames={270}>
        <KuroshioPathScene />
      </Sequence>

      {/* 4. Why Black (27-37s, 300f) — deepOcean → taiwanDetail */}
      <Sequence from={810} durationInFrames={300}>
        <WhyBlackScene />
      </Sequence>

      {/* 5. Warmth (37-49s, 360f) — coral KenBurns */}
      <Sequence from={1110} durationInFrames={360}>
        <WarmthScene />
      </Sequence>

      {/* 6. Marine Life (49-60s, 330f) — coral → fish crossfade */}
      <Sequence from={1470} durationInFrames={330}>
        <MarineLifeScene />
      </Sequence>

      {/* 7. Paradox (60-72s, 360f) — oceanGyres → deepOcean */}
      <Sequence from={1800} durationInFrames={360}>
        <ParadoxScene />
      </Sequence>

      {/* 8. Taiwan from the Sea (72-83s, 330f) — taiwanSatellite → kuroshioTemp */}
      <Sequence from={2160} durationInFrames={330}>
        <TaiwanFromSeaScene />
      </Sequence>

      {/* 9. Pull Quote (83-97s, 420f) */}
      <Sequence from={2490} durationInFrames={420}>
        <PullQuoteScene />
      </Sequence>

      {/* 10. Next Story Teaser (97-106s, 270f) */}
      <Sequence from={2910} durationInFrames={270}>
        <NextStoryScene />
      </Sequence>

      {/* 11. End Card (106-115s, 270f) */}
      <Sequence from={3180} durationInFrames={270}>
        <EndCard />
      </Sequence>
    </AbsoluteFill>
  );
};
