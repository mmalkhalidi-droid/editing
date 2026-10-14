import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { KineticLine } from "../components/KineticLine";
import { Logo } from "../components/Logo";
import { SafeArea } from "../components/SafeArea";
import { COLORS } from "../config";
import { COPY } from "../copy";

export const Turn: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Gold panel wipes in from the right (RTL reading start).
  const wipe = interpolate(frame, [0, 9], [100, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const logoIn = spring({ frame: frame - 8, fps, config: { damping: 10 } });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      <AbsoluteFill
        style={{
          backgroundColor: COLORS.accent,
          transform: `translateX(${wipe}%)`,
        }}
      />
      <SafeArea gap={30}>
        <div style={{ transform: `scale(${logoIn})`, opacity: logoIn }}>
          <Logo size={200} color={COLORS.onAccent} />
        </div>
        <KineticLine
          text={COPY.turn.line}
          delay={14}
          stagger={4}
          fontSize={118}
          color={COLORS.onAccent}
        />
      </SafeArea>
    </AbsoluteFill>
  );
};
