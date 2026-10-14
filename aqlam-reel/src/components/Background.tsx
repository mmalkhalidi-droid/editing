import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLORS } from "../config";

/** Navy background with a slowly drifting soft glow. */
export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const x = 50 + Math.sin(frame / 60) * 18;
  const y = 42 + Math.cos(frame / 75) * 10;
  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        backgroundImage: `radial-gradient(circle at ${x}% ${y}%, ${COLORS.backgroundGlow} 0%, ${COLORS.background} 60%)`,
      }}
    />
  );
};
