import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../config";
import { COPY } from "../copy";
import { FONT_STACK } from "../fonts";

const W = 400;
const H = 800;

/** CSS-drawn phone with a fake Aqlam app screen. */
export const PhoneMockup: React.FC<{ scale?: number }> = ({ scale = 1 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const c = COPY.solution;

  const cardIn = spring({ frame: frame - 12, fps, config: { damping: 14 } });
  const badgeIn = spring({ frame: frame - 22, fps, config: { damping: 9 } });
  const dot = 0.55 + 0.45 * Math.abs(Math.sin(frame / 7));
  const typed = interpolate(frame, [30, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: W,
        height: H,
        transform: `scale(${scale})`,
        borderRadius: 64,
        background: COLORS.phoneBody,
        padding: 14,
        boxShadow: `0 40px 80px rgba(0,0,0,0.45), 0 0 0 3px ${COLORS.backgroundGlow}`,
        position: "relative",
        flexShrink: 0,
      }}
    >
      <div
        dir="rtl"
        lang="ar"
        style={{
          width: "100%",
          height: "100%",
          borderRadius: 52,
          background: COLORS.phoneScreen,
          overflow: "hidden",
          fontFamily: FONT_STACK,
          color: COLORS.background,
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        {/* notch */}
        <div
          style={{
            position: "absolute",
            top: 12,
            left: "50%",
            transform: "translateX(-50%)",
            width: 120,
            height: 32,
            borderRadius: 20,
            background: COLORS.phoneBody,
          }}
        />
        {/* header */}
        <div
          style={{
            background: COLORS.background,
            color: COLORS.text,
            padding: "64px 28px 22px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ fontWeight: 800, fontSize: 30 }}>{c.screenHeader}</div>
          <div style={{ fontWeight: 900, fontSize: 30, color: COLORS.accent }}>
            {COPY.brandName}
          </div>
        </div>

        {/* tutor card */}
        <div
          style={{
            margin: "26px 22px 0",
            background: "#fff",
            borderRadius: 28,
            padding: 22,
            boxShadow: "0 10px 30px rgba(11,31,58,0.12)",
            transform: `translateY(${(1 - cardIn) * 80}px)`,
            opacity: cardIn,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 76,
                height: 76,
                borderRadius: 38,
                background: COLORS.accent,
                color: COLORS.onAccent,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
                fontSize: 38,
                flexShrink: 0,
              }}
            >
              أ
            </div>
            <div style={{ display: "flex", flexDirection: "column" }}>
              <div style={{ fontWeight: 900, fontSize: 30, lineHeight: 1.3 }}>
                {c.tutorName}
              </div>
              <div
                style={{
                  fontWeight: 700,
                  fontSize: 21,
                  lineHeight: 1.4,
                  color: "#4B5B73",
                }}
              >
                {c.tutorTitle}
              </div>
            </div>
          </div>
          <div
            style={{
              marginTop: 18,
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              background: COLORS.live,
              color: "#fff",
              borderRadius: 999,
              padding: "6px 18px",
              fontWeight: 800,
              fontSize: 22,
              transform: `scale(${badgeIn})`,
              transformOrigin: "right center",
            }}
          >
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: 6,
                background: "#fff",
                opacity: dot,
              }}
            />
            {c.liveBadge}
          </div>
        </div>

        {/* fake video / whiteboard */}
        <div
          style={{
            margin: "22px 22px 0",
            height: 250,
            borderRadius: 28,
            background: COLORS.background,
            position: "relative",
            overflow: "hidden",
            opacity: cardIn,
          }}
        >
          <div
            dir="rtl"
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: COLORS.text,
              fontWeight: 800,
              fontSize: 56,
              clipPath: `inset(0 0 0 ${(1 - typed) * 100}%)`,
            }}
          >
            ٣ × ٤ ={" "}
            <span style={{ color: COLORS.accent, marginRight: 14 }}>١٢</span>
          </div>
          <div
            style={{
              position: "absolute",
              bottom: 14,
              left: 14,
              width: 84,
              height: 84,
              borderRadius: 20,
              background: COLORS.backgroundGlow,
              border: `3px solid ${COLORS.accent}`,
            }}
          />
        </div>

        {/* join button */}
        <div
          style={{
            margin: "24px 22px 0",
            background: COLORS.accent,
            color: COLORS.onAccent,
            borderRadius: 22,
            padding: "14px 0",
            textAlign: "center",
            fontWeight: 900,
            fontSize: 30,
            opacity: cardIn,
          }}
        >
          {c.joinButton}
        </div>
      </div>
    </div>
  );
};
