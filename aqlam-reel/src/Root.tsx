import React from "react";
import { parseMedia } from "@remotion/media-parser";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import {
  AqlamReel,
  AqlamReelProps,
  BASE_SCENE_FRAMES,
  SCENE_KEYS,
  SceneKey,
  voFile,
} from "./AqlamReel";
import { hasStaticFile } from "./components/Logo";
import { VIDEO, VOICEOVER } from "./config";

/**
 * Detects optional media in public/ and stretches any scene whose
 * voice-over clip is longer than the scene.
 */
const calculateMetadata: CalculateMetadataFunction<AqlamReelProps> = async ({
  props,
}) => {
  const sceneFrames = { ...BASE_SCENE_FRAMES };
  const voScenes: SceneKey[] = [];

  for (const key of SCENE_KEYS) {
    if (!hasStaticFile(voFile(key))) continue;
    voScenes.push(key);
    const { durationInSeconds } = await parseMedia({
      src: staticFile(voFile(key)),
      fields: { durationInSeconds: true },
      acknowledgeRemotionLicense: true,
    });
    const needed = Math.ceil(
      ((durationInSeconds ?? 0) +
        VOICEOVER.leadInSeconds +
        VOICEOVER.tailSeconds) *
        VIDEO.fps,
    );
    sceneFrames[key] = Math.max(sceneFrames[key], needed);
  }

  const durationInFrames = SCENE_KEYS.reduce((s, k) => s + sceneFrames[k], 0);
  return {
    durationInFrames,
    props: {
      ...props,
      sceneFrames,
      voScenes,
      hasMusic: hasStaticFile("music.mp3"),
    },
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="AqlamReel"
      component={AqlamReel}
      durationInFrames={SCENE_KEYS.reduce(
        (s, k) => s + BASE_SCENE_FRAMES[k],
        0,
      )}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
      defaultProps={{ showSafeZone: false } satisfies AqlamReelProps}
      calculateMetadata={calculateMetadata}
    />
  );
};
