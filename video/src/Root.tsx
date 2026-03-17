import "./index.css";
import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { FarmInternship } from "./FarmInternship";
import { ContextEngineering } from "./ContextEngineering";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyComp"
        component={MyComposition}
        durationInFrames={60}
        fps={30}
        width={1280}
        height={720}
      />
      <Composition
        id="FarmInternship"
        component={FarmInternship}
        durationInFrames={1800}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="ContextEngineering"
        component={ContextEngineering}
        durationInFrames={3600}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
