import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Background } from "../components/Background";
import { CheckIcon } from "../components/Icons";
import { PhoneMockup } from "../components/PhoneMockup";
import { SafeArea } from "../components/SafeArea";
import { COLORS } from "../config";
import { COPY } from "../copy";
import { FONT_STACK } from "../fonts";

const FIRST_BENEFIT = 40;
const BENEFIT_STEP = 38;

const Benefit: React.FC<{ text: string; delay: number }> = ({
  text,
  delay,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 160 },
  });
  const check = interpolate(frame - delay, [4, 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      dir="rtl"
      lang="ar"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 22,
        width: "100%",
        opacity: Math.min(1, s * 2),
        transform: `translateX(${(1 - s) * 160}px)`,
      }}
    >
      <div style={{ transform: `scale(${s})`, flexShrink: 0, display: "flex" }}>
        <CheckIcon size={68} progress={check} />
      </div>
      <div
        style={{
          fontFamily: FONT_STACK,
          fontWeight: 800,
          fontSize: 48,
          lineHeight: 1.3,
          color: COLORS.text,
        }}
      >
        {text}
      </div>
    </div>
  );
};

export const Solution: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Gold from the previous scene wipes away to the left.
  const wipe = interpolate(frame, [0, 9], [0, -100], {
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });
  const phoneIn = spring({ frame: frame - 2, fps, config: { damping: 13 } });
  const float = Math.sin(frame / 18) * 6;

  return (
    <AbsoluteFill>
      <Background />
      <SafeArea gap={44}>
        <div
          style={{
            transform: `translateY(${(1 - phoneIn) * 500 + float}px) rotate(${(1 - phoneIn) * -8}deg)`,
          }}
        >
          <PhoneMockup scale={0.92} />
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 18,
            width: 940,
            marginTop: -40,
          }}
        >
          {COPY.solution.benefits.map((b, i) => (
            <Benefit
              key={i}
              text={b}
              delay={FIRST_BENEFIT + i * BENEFIT_STEP}
            />
          ))}
        </div>
      </SafeArea>
      <AbsoluteFill
        style={{
          backgroundColor: COLORS.accent,
          transform: `translateX(${wipe}%)`,
        }}
      />
    </AbsoluteFill>
  );
};
