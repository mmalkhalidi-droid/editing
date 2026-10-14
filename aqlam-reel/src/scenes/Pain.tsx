import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Background } from "../components/Background";
import { KineticLine } from "../components/KineticLine";
import { SafeArea } from "../components/SafeArea";
import { COLORS } from "../config";
import { COPY } from "../copy";

/** Frames between each pain line. */
const STEP = 22;

export const Pain: React.FC = () => {
  const frame = useCurrentFrame();
  const lines = COPY.pain.lines;

  // A short, decaying shake each time a new line lands.
  let shakeX = 0;
  let shakeY = 0;
  lines.forEach((_, i) => {
    const since = frame - (i * STEP + 4);
    if (since >= 0 && since < 12) {
      const amp = 14 * (1 - since / 12);
      shakeX += Math.sin(since * 2.7) * amp;
      shakeY += Math.cos(since * 3.3) * amp * 0.5;
    }
  });

  return (
    <AbsoluteFill>
      <Background />
      <SafeArea
        gap={10}
        style={{ transform: `translate(${shakeX}px, ${shakeY}px)` }}
      >
        {lines.map((line, i) => (
          <KineticLine
            key={i}
            text={line}
            delay={i * STEP}
            stagger={2}
            fontSize={i === lines.length - 1 ? 84 : 112}
            color={i === lines.length - 1 ? COLORS.accent : COLORS.text}
            variant="slide"
          />
        ))}
      </SafeArea>
    </AbsoluteFill>
  );
};
