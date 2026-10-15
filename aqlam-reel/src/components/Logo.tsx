import React from "react";
import { getStaticFiles, Img, staticFile } from "remotion";
import { COLORS } from "../config";
import { COPY } from "../copy";
import { FONT_STACK } from "../fonts";

export const hasStaticFile = (name: string) =>
  getStaticFiles().some((f) => f.name === name);

/**
 * Uses public/logo.png when present, otherwise an Arabic wordmark.
 * `size` is the logo height in px.
 */
export const Logo: React.FC<{
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ size = 160, color = COLORS.accent, style }) => {
  if (hasStaticFile("logo.png")) {
    return (
      <Img
        src={staticFile("logo.png")}
        style={{ height: size, width: "auto", objectFit: "contain", ...style }}
      />
    );
  }
  return (
    <div
      dir="rtl"
      lang="ar"
      style={{
        fontFamily: FONT_STACK,
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1.2,
        color,
        ...style,
      }}
    >
      {COPY.brandName}
    </div>
  );
};
