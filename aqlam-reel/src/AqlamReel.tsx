import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile } from "remotion";
import { SafeZoneOverlay } from "./components/SafeArea";
import { COLORS, MUSIC, SCENE_SECONDS, VIDEO, VOICEOVER } from "./config";
import { FONT_STACK } from "./fonts";
import { CTA } from "./scenes/CTA";
import { Hook } from "./scenes/Hook";
import { Offer } from "./scenes/Offer";
import { Pain } from "./scenes/Pain";
import { Solution } from "./scenes/Solution";
import { Turn } from "./scenes/Turn";

export type SceneKey = keyof typeof SCENE_SECONDS;

const SCENES: { key: SceneKey; Component: React.FC }[] = [
  { key: "hook", Component: Hook },
  { key: "pain", Component: Pain },
  { key: "turn", Component: Turn },
  { key: "solution", Component: Solution },
  { key: "offer", Component: Offer },
  { key: "cta", Component: CTA },
];

export const SCENE_KEYS = SCENES.map((s) => s.key);

/** Scene lengths from config.ts, before any voice-over stretching. */
export const BASE_SCENE_FRAMES = Object.fromEntries(
  SCENE_KEYS.map((k) => [k, Math.round(SCENE_SECONDS[k] * VIDEO.fps)]),
) as Record<SceneKey, number>;

export const voFile = (key: SceneKey) => `vo/${key}.mp3`;

export type AqlamReelProps = {
  showSafeZone: boolean;
  /** Filled in by calculateMetadata (Root.tsx). */
  sceneFrames?: Record<SceneKey, number>;
  voScenes?: SceneKey[];
  hasMusic?: boolean;
};

export const AqlamReel: React.FC<AqlamReelProps> = ({
  showSafeZone,
  sceneFrames = BASE_SCENE_FRAMES,
  voScenes = [],
  hasMusic = false,
}) => {
  let start = 0;
  const starts = {} as Record<SceneKey, number>;
  for (const key of SCENE_KEYS) {
    starts[key] = start;
    start += sceneFrames[key];
  }
  const total = start;

  const fadeIn = MUSIC.fadeInSeconds * VIDEO.fps;
  const fadeOut = MUSIC.fadeOutSeconds * VIDEO.fps;
  const musicLevel =
    MUSIC.volume * (voScenes.length > 0 ? MUSIC.duckedVolume : 1);

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
          from={starts[key]}
          durationInFrames={sceneFrames[key]}
        >
          <Component />
        </Sequence>
      ))}

      {voScenes.map((key) => (
        <Sequence
          key={`vo-${key}`}
          name={`vo: ${key}`}
          from={starts[key] + Math.round(VOICEOVER.leadInSeconds * VIDEO.fps)}
          layout="none"
        >
          <Audio src={staticFile(voFile(key))} volume={VOICEOVER.volume} />
        </Sequence>
      ))}

      {hasMusic ? (
        <Audio
          src={staticFile("music.mp3")}
          volume={(f) =>
            musicLevel *
            interpolate(f, [0, fadeIn, total - fadeOut, total], [0, 1, 1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      ) : null}

      {showSafeZone ? <SafeZoneOverlay /> : null}
    </AbsoluteFill>
  );
};
