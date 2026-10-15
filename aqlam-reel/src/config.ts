/**
 * Brand + layout config. Swap the colors here to re-skin the whole reel.
 */
export const COLORS = {
  /** Main background */
  background: "#0B1F3A",
  /** Slightly lighter shade used for the background glow */
  backgroundGlow: "#17355F",
  /** Main text color */
  text: "#FFF8EE",
  /** Accent (highlights, wordmark, wipe) */
  accent: "#F5B700",
  /** Text drawn on top of the accent color */
  onAccent: "#0B1F3A",
  /** Muted text (secondary lines) */
  muted: "#C9D3E3",
  /** "Live" badge on the phone mockup */
  live: "#22C55E",
  /** WhatsApp button */
  whatsapp: "#25D366",
  /** Phone mockup body */
  phoneBody: "#050D1A",
  /** Phone mockup screen */
  phoneScreen: "#F7F4EE",
} as const;

export const VIDEO = {
  width: 1080,
  height: 1920,
  fps: 30,
} as const;

/** Instagram Reels UI covers the top ~220px and bottom ~380px. */
export const SAFE_ZONE = {
  top: 220,
  bottom: 380,
  side: 70,
} as const;

/** Scene lengths in seconds. Edit these to retime the reel. */
export const SCENE_SECONDS = {
  hook: 3,
  pain: 3,
  turn: 2,
  solution: 6,
  offer: 3,
  cta: 3,
} as const;

/** Music fade in/out (seconds), only used if public/music.mp3 exists. */
export const MUSIC = {
  fadeInSeconds: 0.5,
  fadeOutSeconds: 1.5,
  volume: 0.9,
  /** Music volume multiplier while voice-over is present. */
  duckedVolume: 0.25,
} as const;

/**
 * Voice-over, only used if public/vo/<scene>.mp3 files exist
 * (hook.mp3, pain.mp3, turn.mp3, solution.mp3, offer.mp3, cta.mp3).
 * A scene is stretched automatically if its clip is longer than the scene.
 */
export const VOICEOVER = {
  volume: 1,
  /** Delay after the scene starts before the clip plays (seconds). */
  leadInSeconds: 0.1,
  /** Breathing room kept after a clip before the next scene (seconds). */
  tailSeconds: 0.15,
} as const;
