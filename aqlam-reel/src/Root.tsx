import React from "react";
import { Composition } from "remotion";
import { AqlamReel, AqlamReelProps, TOTAL_FRAMES } from "./AqlamReel";
import { VIDEO } from "./config";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="AqlamReel"
      component={AqlamReel}
      durationInFrames={TOTAL_FRAMES}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
      defaultProps={{ showSafeZone: false } satisfies AqlamReelProps}
    />
  );
};
