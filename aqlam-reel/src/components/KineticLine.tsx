import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../config";
import { FONT_STACK } from "../fonts";

type Props = {
  text: string;
  /** Frame (relative to the parent Sequence) when the first word starts. */
  delay?: number;
  /** Frames between words. */
  stagger?: number;
  fontSize?: number;
  fontWeight?: number;
  color?: string;
  /** Words (exact match) to paint in the accent color. */
  highlight?: readonly string[];
  highlightColor?: string;
  /** "pop" scales up from small, "slide" slides in from the right (RTL start). */
  variant?: "pop" | "slide";
  style?: React.CSSProperties;
};

/**
 * Kinetic RTL line. Splits on spaces only, so Arabic letters inside a
 * word are never separated and keep their joining.
 */
export const KineticLine: React.FC<Props> = ({
  text,
  delay = 0,
  stagger = 4,
  fontSize = 96,
  fontWeight = 900,
  color = COLORS.text,
  highlight = [],
  highlightColor = COLORS.accent,
  variant = "pop",
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ").filter(Boolean);

  // "slide" moves the whole line as one block so words never overlap mid-flight.
  const lineS =
    variant === "slide"
      ? spring({
          frame: frame - delay,
          fps,
          config: { damping: 13, stiffness: 200, mass: 0.7 },
        })
      : 1;

  return (
    <div
      dir="rtl"
      lang="ar"
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        columnGap: "0.28em",
        fontFamily: FONT_STACK,
        fontSize,
        fontWeight,
        lineHeight: 1.35,
        color,
        textAlign: "center",
        opacity: Math.min(1, Math.max(0, lineS * 2)),
        transform: `translateX(${(1 - lineS) * 260}px)`,
        ...style,
      }}
    >
      {words.map((word, i) => {
        const s =
          variant === "slide"
            ? 1
            : spring({
                frame: frame - delay - i * stagger,
                fps,
                config: { damping: 11, stiffness: 170, mass: 0.7 },
              });
        const opacity = Math.min(1, Math.max(0, s * 2));
        const transform = `translateY(${(1 - s) * 70}px) scale(${0.4 + 0.6 * s})`;
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity,
              transform,
              color: highlight.includes(word) ? highlightColor : undefined,
              whiteSpace: "nowrap",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
