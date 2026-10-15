import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Background } from "../components/Background";
import { KineticLine } from "../components/KineticLine";
import { SafeArea } from "../components/SafeArea";
import { COLORS } from "../config";
import { COPY } from "../copy";

export const Offer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const burst = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });
  const underline = spring({
    frame: frame - 22,
    fps,
    config: { damping: 18 },
  });

  return (
    <AbsoluteFill>
      <Background />
      {/* soft gold halo behind the price */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 44%, ${COLORS.accent}33 0%, transparent ${45 * burst}%)`,
        }}
      />
      <SafeArea gap={24}>
        <KineticLine
          text={COPY.offer.main}
          delay={0}
          stagger={4}
          fontSize={100}
          highlight={["٧٠٠", "درهم"]}
          style={{ lineHeight: 1.25 }}
        />
        <div
          style={{
            width: 420 * underline,
            height: 10,
            borderRadius: 5,
            background: COLORS.accent,
          }}
        />
        <KineticLine
          text={COPY.offer.sub}
          delay={28}
          stagger={3}
          fontSize={64}
          fontWeight={700}
          color={COLORS.muted}
        />
      </SafeArea>
    </AbsoluteFill>
  );
};
