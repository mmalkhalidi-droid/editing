// Generates public/vo/<scene>.mp3 from VOICEOVER_LINES in src/copy.ts
// using Microsoft Edge neural voices (free, no API key).
//
//   pip install edge-tts
//   npm run voiceover                          # Emirati male voice
//   VOICE=ar-AE-FatimaNeural npm run voiceover # Emirati female voice
//   RATE=+15% npm run voiceover                # speak faster
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { VOICEOVER_LINES } from "../src/copy.ts";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const outDir = join(root, "public", "vo");
const voice = process.env.VOICE ?? "ar-AE-HamdanNeural";
const rate = process.env.RATE ?? "+8%";

mkdirSync(outDir, { recursive: true });
for (const [scene, text] of Object.entries(VOICEOVER_LINES)) {
  const out = join(outDir, `${scene}.mp3`);
  console.log(`${scene}: ${text}`);
  execFileSync(
    "edge-tts",
    ["--voice", voice, `--rate=${rate}`, "--text", text, "--write-media", out],
    { stdio: "inherit" },
  );
}
console.log(
  `\nWrote ${Object.keys(VOICEOVER_LINES).length} clips to public/vo/`,
);
