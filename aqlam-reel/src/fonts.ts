import { loadFont } from "@remotion/google-fonts/Cairo";

export const { fontFamily } = loadFont("normal", {
  weights: ["600", "700", "800", "900"],
  subsets: ["arabic", "latin"],
});

/** Cairo first, system color emoji as fallback for emoji glyphs. */
export const FONT_STACK = `${fontFamily}, "Noto Color Emoji", "Apple Color Emoji", sans-serif`;
