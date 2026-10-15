# Aqlam (أقلام) – 20s Instagram Reel

Remotion project for a 1080×1920, 30fps, 20-second H.264 reel.

## Where to edit

| What | File |
| --- | --- |
| All Arabic text | `src/copy.ts` |
| Brand colors, scene lengths, safe zone, music fade | `src/config.ts` |
| Each scene | `src/scenes/*.tsx` (Hook, Pain, Turn, Solution, Offer, CTA) |
| Shared pieces (kinetic text, phone mockup, clock, logo) | `src/components/` |

- **Logo:** drop a `public/logo.png` and it replaces the "أقلام" wordmark automatically.
- **Music:** drop a `public/music.mp3` and it's added with a fade in/out. Without it, the video is silent.

## Voice-over

The VO script is `VOICEOVER_LINES` in `src/copy.ts` (one line per scene). Put one clip per
scene in `public/vo/` — `hook.mp3`, `pain.mp3`, `turn.mp3`, `solution.mp3`, `offer.mp3`,
`cta.mp3` — and each plays at the start of its scene. Any subset works. If a clip is longer
than its scene, that scene stretches to fit, and music (if any) is ducked under the voice.
Levels and timing live in `VOICEOVER` / `MUSIC` in `src/config.ts`.

**Generate an AI Emirati voice (free):**

```bash
pip install edge-tts
npm run voiceover                            # ar-AE-HamdanNeural (male)
VOICE=ar-AE-FatimaNeural npm run voiceover   # female
npm run render
```

**Or record it yourself:** read each line into your phone's voice memo app, export as MP3,
name the files as above and drop them in `public/vo/`.

## Preview & tweak (Remotion Studio)

```bash
npm install
npm run dev        # opens http://localhost:3000
```

Pick the **AqlamReel** composition. Scrub the timeline, and use the props panel on the
right to turn on `showSafeZone` (red bands show where Instagram's UI covers the video).
Changes to `copy.ts` / `config.ts` hot-reload instantly.

## Render

```bash
npm run render     # -> out/aqlam-reel.mp4
npm run stills     # one PNG per scene (with the safe-zone overlay) -> out/stills/
```
