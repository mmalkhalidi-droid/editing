import React from "react";
import { AbsoluteFill } from "remotion";
import { SAFE_ZONE } from "../config";

/** Centers children inside Instagram's safe zone. */
export const SafeArea: React.FC<{
  children: React.ReactNode;
  gap?: number;
  style?: React.CSSProperties;
}> = ({ children, gap = 40, style }) => (
  <AbsoluteFill
    dir="rtl"
    style={{
      paddingTop: SAFE_ZONE.top,
      paddingBottom: SAFE_ZONE.bottom,
      paddingLeft: SAFE_ZONE.side,
      paddingRight: SAFE_ZONE.side,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);

/** Debug overlay showing the unsafe areas (toggle via the showSafeZone prop). */
export const SafeZoneOverlay: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: SAFE_ZONE.top,
        background: "rgba(255,0,0,0.25)",
      }}
    />
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: SAFE_ZONE.bottom,
        background: "rgba(255,0,0,0.25)",
      }}
    />
  </AbsoluteFill>
);
