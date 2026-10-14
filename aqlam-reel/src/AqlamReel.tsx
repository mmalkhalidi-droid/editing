import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile } from "remotion";
import { hasStaticFile } from "./components/Logo";
import { SafeZoneOverlay } from "./components/SafeArea";
import { COLORS, MUSIC, SCENE_SECONDS, VIDEO } from "./config";
import { FONT_STACK } from "./fonts";
import { CTA } from "./scenes/CTA";
import { Hook } from "./scenes/Hook";
import { Offer } from "./scenes/Offer";
import { Pain } from "./scenes/Pain";
import { Solution } from "./scenes/Solution";
import { Turn } from "./scenes/Turn";

const SCENES = [
  { key: "hook", Component: Hook },
  { key: "pain", Component: Pain },
  { key: "turn", Component: Turn },
  { key: "solution", Component: Solution },
  { key: "offer", Component: Offer },
  { key: "cta", Component: CTA },
] as const;

export const sceneFrames = (key: keyof typeof SCENE_SECONDS) =>
  Math.round(SCENE_SECONDS[key] * VIDEO.fps);

export const TOTAL_FRAMES = SCENES.reduce(
  (sum, s) => sum + sceneFrames(s.key),
  0,
);

/** Start frame of each scene, handy for rendering stills. */
export const SCENE_STARTS = SCENES.reduce<Record<string, number>>(
  (acc, s, i) => {
    acc[s.key] =
      i === 0 ? 0 : acc[SCENES[i - 1].key] + sceneFrames(SCENES[i - 1].key);
    return acc;
  },
  {},
);

export type AqlamReelProps = { showSafeZone: boolean };

export const AqlamReel: React.FC<AqlamReelProps> = ({ showSafeZone }) => {
  const hasMusic = hasStaticFile("music.mp3");
  const fadeIn = MUSIC.fadeInSeconds * VIDEO.fps;
  const fadeOut = MUSIC.fadeOutSeconds * VIDEO.fps;

  return (
    <AbsoluteFill
      dir="rtl"
      lang="ar"
      style={{ backgroundColor: COLORS.background, fontFamily: FONT_STACK }}
    >
      {SCENES.map(({ key, Component }) => (
        <Sequence
          key={key}
          name={key}
          from={SCENE_STARTS[key]}
          durationInFrames={sceneFrames(key)}
        >
          <Component />
        </Sequence>
      ))}

      {hasMusic ? (
        <Audio
          src={staticFile("music.mp3")}
          volume={(f) =>
            MUSIC.volume *
            interpolate(
              f,
              [0, fadeIn, TOTAL_FRAMES - fadeOut, TOTAL_FRAMES],
              [0, 1, 1, 0],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
            )
          }
        />
      ) : null}

      {showSafeZone ? <SafeZoneOverlay /> : null}
    </AbsoluteFill>
  );
};
