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
