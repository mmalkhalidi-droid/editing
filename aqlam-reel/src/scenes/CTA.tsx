import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Background } from "../components/Background";
import { ChatIcon } from "../components/Icons";
import { KineticLine } from "../components/KineticLine";
import { Logo } from "../components/Logo";
import { SafeArea } from "../components/SafeArea";
import { COLORS } from "../config";
import { COPY } from "../copy";
import { FONT_STACK } from "../fonts";

/** Frames at the end of the scene where everything holds still. */
const HOLD_FRAMES = 30;

export const CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const logoIn = spring({ frame, fps, config: { damping: 11 } });
  const storeIn = spring({ frame: frame - 18, fps, config: { damping: 14 } });
  const btnIn = spring({ frame: frame - 24, fps, config: { damping: 10 } });

  // Subtle pulse that eases out before the final hold.
  const pulseEnd = durationInFrames - HOLD_FRAMES;
  const pulseAmp = interpolate(
    frame,
    [30, 36, pulseEnd - 8, pulseEnd],
    [0, 1, 1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );
  const phase = Math.max(0, frame - 30) / 9;
  const pulse = 1 + 0.045 * Math.sin(phase) * pulseAmp;
  const ring = (Math.max(0, frame - 30) % 24) / 24;

  return (
    <AbsoluteFill>
      <Background />
      <SafeArea gap={34}>
        <div style={{ transform: `scale(${logoIn})`, opacity: logoIn }}>
          <Logo size={190} />
        </div>
        <KineticLine
          text={COPY.cta.main}
          delay={6}
          stagger={4}
          fontSize={100}
        />
        <div
          dir="rtl"
          lang="ar"
          style={{
            fontFamily: FONT_STACK,
            fontWeight: 700,
            fontSize: 44,
            color: COLORS.muted,
            opacity: storeIn,
            transform: `translateY(${(1 - storeIn) * 30}px)`,
          }}
        >
          {COPY.cta.store}
        </div>
        <div
          style={{
            position: "relative",
            marginTop: 20,
            transform: `scale(${btnIn * pulse})`,
          }}
        >
          {/* expanding ring behind the button */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: 999,
              border: `4px solid ${COLORS.whatsapp}`,
              transform: `scale(${1 + ring * 0.25})`,
              opacity: (1 - ring) * 0.7 * pulseAmp,
            }}
          />
          <div
            dir="rtl"
            lang="ar"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 20,
              background: COLORS.whatsapp,
              color: "#fff",
              borderRadius: 999,
              padding: "26px 60px",
              fontFamily: FONT_STACK,
              fontWeight: 900,
              fontSize: 62,
              lineHeight: 1.3,
              boxShadow: "0 18px 40px rgba(37,211,102,0.35)",
            }}
          >
            <ChatIcon size={66} />
            {COPY.cta.whatsapp}
          </div>
        </div>
      </SafeArea>
    </AbsoluteFill>
  );
};
