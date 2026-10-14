import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { COLORS } from "../config";

/**
 * Wall clock that ticks from 8:45 to 9:00, then gives a little "alarm" wobble.
 */
export const Clock: React.FC<{
  size?: number;
  /** Frame when ticking starts */
  start?: number;
  /** Number of minute ticks (8:45 -> 9:00 = 15) */
  ticks?: number;
  /** Frames per tick */
  framesPerTick?: number;
}> = ({ size = 300, start = 0, ticks = 15, framesPerTick = 3 }) => {
  const frame = useCurrentFrame();
  const t = Math.max(0, frame - start);
  const idx = Math.min(ticks, Math.floor(t / framesPerTick));
  const within =
    idx >= ticks
      ? 0
      : interpolate(t % framesPerTick, [0, framesPerTick - 1], [0, 1], {
          easing: Easing.out(Easing.back(3)),
          extrapolateRight: "clamp",
        });
  const minutesDone = Math.min(ticks, idx + within);
  const minuteAngle = 360 - ticks * 6 + minutesDone * 6;
  const hourAngle = 270 - (ticks / 60) * 30 + (minutesDone / 60) * 30;

  const endFrame = start + ticks * framesPerTick;
  const since = frame - endFrame;
  const wobble =
    since > 0 ? Math.sin(since * 1.6) * 9 * Math.exp(-since / 10) : 0;

  const intro = interpolate(frame, [0, 10], [0.6, 1], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(2)),
  });

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      style={{ transform: `rotate(${wobble}deg) scale(${intro})` }}
    >
      {/* bells */}
      <circle cx="45" cy="38" r="18" fill={COLORS.accent} />
      <circle cx="155" cy="38" r="18" fill={COLORS.accent} />
      <circle
        cx="100"
        cy="108"
        r="80"
        fill={COLORS.text}
        stroke={COLORS.accent}
        strokeWidth="10"
      />
      {Array.from({ length: 12 }).map((_, i) => {
        const a = (i * 30 * Math.PI) / 180;
        const r1 = i % 3 === 0 ? 58 : 63;
        return (
          <line
            key={i}
            x1={100 + Math.sin(a) * r1}
            y1={108 - Math.cos(a) * r1}
            x2={100 + Math.sin(a) * 70}
            y2={108 - Math.cos(a) * 70}
            stroke={COLORS.background}
            strokeWidth={i % 3 === 0 ? 6 : 3}
            strokeLinecap="round"
          />
        );
      })}
      <line
        x1="100"
        y1="108"
        x2="100"
        y2="70"
        stroke={COLORS.background}
        strokeWidth="9"
        strokeLinecap="round"
        transform={`rotate(${hourAngle} 100 108)`}
      />
      <line
        x1="100"
        y1="108"
        x2="100"
        y2="50"
        stroke={COLORS.accent}
        strokeWidth="6"
        strokeLinecap="round"
        transform={`rotate(${minuteAngle} 100 108)`}
      />
      <circle cx="100" cy="108" r="8" fill={COLORS.background} />
    </svg>
  );
};
