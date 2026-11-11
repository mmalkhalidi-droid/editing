#!/usr/bin/env python3
"""Render the Aqlam motion reel (1080x1920, 30fps) from the sticker PNGs.

Usage: python3 render.py            -> writes out/aqlam_reel.mp4
       python3 render.py --preview  -> writes a few still frames to out/
"""
import math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
W, H, FPS = 1080, 1920, 30

GREEN = (62, 142, 47)
GREEN_D = (38, 98, 30)
INK = (28, 40, 26)
BG = (247, 249, 243)

FONT_B = os.path.join(HERE, "fonts", "cairo-arabic-900-normal.woff")
FONT_M = os.path.join(HERE, "fonts", "cairo-arabic-700-normal.woff")

# ---------------------------------------------------------------- timeline
# Each scene: start, end, stickers [(name, cx, bottom, width)], caption lines
# [(text, style)], voice clips [(file, at)], sfx [(file, at)], extra effect.
SCENES = [
    dict(t=(0.00, 3.60), st=[("M2", 540, 1580, 760)],
         cap=[("عندك", "ink"), ("سؤال؟", "pill")], fx="qmarks"),
    dict(t=(3.60, 7.25), st=[("W2", 540, 1580, 760)],
         cap=[("من وين", "ink"), ("أبدأ؟", "pill")], fx="qmarks"),
    dict(t=(7.25, 9.20), st=[("M4", 540, 1580, 760)],
         cap=[("لا تحتار", "pill")], fx="rays"),
    dict(t=(9.20, 12.75), st=[("W3", 540, 1580, 760)],
         cap=[("في أقلام", "pill"), ("نبسّط لك الفكرة", "ink")]),
    dict(t=(12.75, 15.40), st=[("M3", 540, 1580, 760)],
         cap=[("خطوة", "ink"), ("بخطوة", "pill")], fx="steps"),
    dict(t=(15.40, 18.15), st=[("W4", 540, 1580, 760)],
         cap=[("سهلة", "pill"), ("وممتعة", "ink")], fx="rays"),
    dict(t=(18.15, 20.60), st=[("M1", 300, 1470, 620), ("W1", 790, 1490, 620)],
         cap=[("سهلة، صح؟", "pill")], fx="confetti"),
    dict(t=(20.60, 26.50), st=[("M5", 300, 1440, 620), ("W5", 785, 1460, 660)],
         cap=[("تابعوا", "ink"), ("أقلام", "pill")], fx="cta"),
]
VOICE = [("1.mp3", 0.35), ("2.mp3", 3.85), ("3.mp3", 7.45), ("4.mp3", 9.40),
         ("5.mp3", 12.95), ("6.mp3", 15.60), ("7m.mp3", 18.40), ("7w.mp3", 18.45),
         ("8.mp3", 20.85)]
SFX = [("pop.mp3", 0.00, 0.9)] + [("pop.mp3", s["t"][0], 0.9) for s in SCENES[1:]] + [
    ("whoosh.mp3", 3.45, 0.6), ("whoosh.mp3", 12.6, 0.6), ("ding.mp3", 7.3, 0.8),
    ("ding.mp3", 15.45, 0.5), ("confetti.mp3", 18.2, 0.8), ("pop.mp3", 18.45, 0.8),
    ("whoosh.mp3", 20.45, 0.6), ("ding.mp3", 22.0, 0.6)]
DURATION = SCENES[-1]["t"][1]


# ---------------------------------------------------------------- helpers
def ease_out_back(x, s=1.9):
    x = min(max(x, 0.0), 1.0) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_in(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x


def ar_text(text, size, color, font=FONT_B):
    """Render Arabic text. The Cairo Arabic subset has no space glyph, so lay
    out words right-to-left ourselves."""
    f = ImageFont.truetype(font, size)
    words = []
    for w in text.split(" "):
        l, t, r, b = f.getbbox(w, direction="rtl", language="ar", anchor="ls")
        im = Image.new("RGBA", (r - l + 4, int(size * 1.9)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((2 - l, int(size * 1.35)), w, font=f, fill=color,
                                direction="rtl", language="ar", anchor="ls")
        words.append(im)
    gap = int(size * 0.28)
    tw = sum(i.width for i in words) + gap * (len(words) - 1)
    out = Image.new("RGBA", (tw, words[0].height), (0, 0, 0, 0))
    x = tw
    for i in words:  # first word on the right
        x -= i.width
        out.alpha_composite(i, (x, 0))
        x -= gap
    return out.crop(out.getbbox())


def caption_line(text, style):
    size = 118
    if style == "pill":
        t = ar_text(text, size, (255, 255, 255))
        px, py = 46, 30
        im = Image.new("RGBA", (t.width + 2 * px, t.height + 2 * py + 14), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 14, im.width - 1, im.height - 1), 40, fill=GREEN_D)
        d.rounded_rectangle((0, 0, im.width - 1, im.height - 15), 40, fill=GREEN)
        im.alpha_composite(t, (px, py))
        return im
    t = ar_text(text, size, INK)
    return t


def with_shadow(st):
    pad = 40
    a = st.getchannel("A")
    sh = Image.new("RGBA", (st.width + 2 * pad, st.height + 2 * pad), (0, 0, 0, 0))
    blk = Image.new("RGBA", st.size, (20, 40, 20, 70))
    sh.paste(blk, (pad, pad + 16), a)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh.alpha_composite(st, (pad, pad))
    return sh


def paste_center(canvas, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0:
        return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                       Image.BILINEAR)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BILINEAR, expand=True)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    if x >= 0 and y >= 0 and x + im.width <= W and y + im.height <= H:
        canvas.alpha_composite(im, (x, y))
    else:
        _safe_paste(canvas, im, x, y)


def _safe_paste(canvas, im, x, y):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(im, (x, y), im)
    canvas.alpha_composite(layer)


# ---------------------------------------------------------------- assets
def load_assets():
    st = {}
    for s in SCENES:
        for name, cx, bottom, width in s["st"]:
            key = (name, width)
            if key in st:
                continue
            im = Image.open(os.path.join(HERE, "stickers", name + ".png")).convert("RGBA")
            # trim the last few px (tiny overlap leftovers from the sheet)
            im = im.crop((0, 0, im.width, im.height - 14))
            sc = width / im.width
            im = im.resize((width, int(im.height * sc)), Image.LANCZOS)
            st[key] = with_shadow(im)
    caps = {}
    for i, s in enumerate(SCENES):
        caps[i] = [caption_line(t, sty) for t, sty in s["cap"]]
    return st, caps


def make_background():
    bg = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(bg)
    for y in range(60, H, 64):  # subtle dot grid
        for x in range(30 + (y // 64 % 2) * 32, W, 64):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(222, 230, 214, 255))
    return bg


BLOBS = [(160, 260, 260, 0.0), (930, 700, 320, 1.7), (120, 1350, 300, 3.1), (980, 1700, 260, 4.2)]


def draw_blobs(canvas, t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, r, ph in BLOBS:
        x += 40 * math.sin(t * 0.5 + ph)
        y += 30 * math.cos(t * 0.4 + ph)
        d.ellipse((x - r, y - r, x + r, y + r), fill=GREEN + (26,))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(30)))


def brand_tag():
    t = ar_text("أقلام", 52, (255, 255, 255))
    im = Image.new("RGBA", (t.width + 60, t.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2,
                                         fill=GREEN)
    im.alpha_composite(t, (30, 15))
    return im


random.seed(7)
CONFETTI = [dict(x=random.uniform(0, W), y=random.uniform(-400, -20), vx=random.uniform(-120, 120),
                 vy=random.uniform(250, 650), r=random.uniform(0, 360), vr=random.uniform(-400, 400),
                 c=random.choice([GREEN, (250, 196, 0), (255, 255, 255), (90, 180, 70), GREEN_D]),
                 s=random.uniform(14, 26)) for _ in range(140)]


def draw_fx(canvas, fx, lt, dur):
    d = ImageDraw.Draw(canvas)
    if fx == "rays":
        cx, cy = 540, 1000
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        k = min(1, lt / 0.4)
        for i in range(16):
            a = math.radians(i * 22.5 + lt * 18)
            r0, r1 = 330 * k, 900 * k
            a2 = a + math.radians(6)
            ld.polygon([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                        (cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                        (cx + r1 * math.cos(a2), cy + r1 * math.sin(a2))], fill=GREEN + (34,))
        canvas.alpha_composite(layer)
    elif fx == "qmarks":
        for i, (x, y, ph) in enumerate([(130, 820, 0), (950, 1180, 1.3), (900, 760, 2.4)]):
            k = ease_out_back((lt - 0.4 - i * 0.18) / 0.4)
            if k <= 0:
                continue
            q = ar_text("؟", int(110 * k) + 1, GREEN + (200,))
            paste_center(canvas, q, x, y + 14 * math.sin(lt * 3 + ph), rot=12 * math.sin(lt * 2 + ph))
    elif fx == "steps":
        for i in range(3):
            k = ease_out_back((lt - 0.3 - i * 0.35) / 0.35)
            if k <= 0:
                continue
            x = 820 - i * 300
            r = 52 * k
            d.ellipse((x - r, 1720 - r, x + r, 1720 + r), fill=GREEN)
            n = ar_text("١٢٣"[i], int(64 * k) + 1, (255, 255, 255))
            paste_center(canvas, n, x, 1720)
            if i < 2 and k >= 1:
                d.line((x - 70, 1720, x - 230, 1720), fill=GREEN + (160,), width=8)
    elif fx == "confetti":
        for p in CONFETTI:
            tt = lt
            x = p["x"] + p["vx"] * tt
            y = p["y"] + p["vy"] * tt + 300 * tt * tt
            if y > H + 40:
                continue
            rot = math.radians(p["r"] + p["vr"] * tt)
            s = p["s"]
            w = s * abs(math.cos(rot * 1.7)) + 4
            pts = [(-w / 2, -s / 3), (w / 2, -s / 3), (w / 2, s / 3), (-w / 2, s / 3)]
            pts = [(x + px * math.cos(rot) - py * math.sin(rot), y + px * math.sin(rot) + py * math.cos(rot))
                   for px, py in pts]
            d.polygon(pts, fill=p["c"])


def cta_button(lt):
    t = ar_text("انتظروا الجديد", 64, (255, 255, 255))
    im = Image.new("RGBA", (t.width + 120, t.height + 56), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2, fill=INK)
    im.alpha_composite(t, (60, 28))
    return im


# ---------------------------------------------------------------- frame
def render_frame(t, assets, bg, tag, btn):
    st_assets, caps = assets
    canvas = bg.copy()
    draw_blobs(canvas, t)
    si = max(i for i, s in enumerate(SCENES) if s["t"][0] <= t)
    s = SCENES[si]
    t0, t1 = s["t"]
    lt, dur = t - t0, t1 - t0
    last = si == len(SCENES) - 1
    out_k = 0 if last else ease_in((lt - (dur - 0.22)) / 0.22)  # exit progress

    if s.get("fx") in ("rays",):
        draw_fx(canvas, s["fx"], lt, dur)

    # stickers
    for j, (name, cx, bottom, width) in enumerate(s["st"]):
        im = st_assets[(name, width)]
        k = ease_out_back((lt - j * 0.12) / 0.42)
        sc = (0.25 + 0.75 * k) * (1 - out_k)
        if (lt - j * 0.12) < 0:
            continue
        bob = 9 * math.sin((t + j) * 2 * math.pi / 1.7)
        rot = (1 - min(k, 1)) * (-10 if j == 0 else 10) + 1.6 * math.sin((t + j * 0.7) * 2.1)
        cy = bottom - im.height / 2 + 40 + bob + (1 - min(k, 1)) * 120
        paste_center(canvas, im, cx, cy, sc, rot)

    if s.get("fx") in ("qmarks", "steps", "confetti"):
        draw_fx(canvas, s["fx"], lt, dur)

    # caption lines
    lines = caps[si]
    y = 430 - (sum(l.height for l in lines) + 18 * (len(lines) - 1)) / 2
    for j, l in enumerate(lines):
        k = ease_out_back((lt - 0.15 - j * 0.14) / 0.38)
        cy = y + l.height / 2
        if k > 0:
            paste_center(canvas, l, 540, cy + 4 * math.sin(t * 2.4 + j), k * (1 - out_k),
                         rot=(1 - min(k, 1)) * 8)
        y += l.height + 18

    # CTA button
    if s.get("fx") == "cta":
        k = ease_out_back((lt - 1.2) / 0.45)
        if k > 0:
            pulse = 1 + 0.04 * math.sin(max(0, lt - 1.6) * 2 * math.pi / 0.9)
            paste_center(canvas, btn, 540, 1640, k * pulse)

    # persistent brand tag (top, inside the safe zone)
    paste_center(canvas, tag, 540, 175)

    # white flash on the "idea" scene
    if s.get("fx") == "rays" and lt < 0.3:
        a = int(200 * (1 - lt / 0.3))
        canvas.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
    # fade to white at the very end
    if t > DURATION - 0.5:
        a = int(255 * (t - (DURATION - 0.5)) / 0.5)
        canvas.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, min(255, a))))
    return canvas.convert("RGB")


def mix_audio(path):
    a = os.path.join(HERE, "audio")
    inputs, filters, labels = [], [], []
    clips = [(f, at, 1.6) for f, at in VOICE] + [(f, at, v) for f, at, v in SFX]
    for i, (f, at, vol) in enumerate(clips):
        inputs += ["-i", os.path.join(a, f)]
        ms = int(at * 1000)
        filters.append(f"[{i}:a]aresample=44100,volume={vol},adelay={ms}|{ms}[a{i}]")
        labels.append(f"[a{i}]")
    n = len(clips)
    inputs += ["-i", os.path.join(a, "music.mp3")]
    filters.append(f"[{n}:a]aresample=44100,volume=0.22,atrim=0:{DURATION},"
                   f"afade=t=in:d=0.4,afade=t=out:st={DURATION - 1.5}:d=1.5[m]")
    labels.append("[m]")
    filters.append("".join(labels) + f"amix=inputs={n + 1}:normalize=0,alimiter=limit=0.95[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
                    ";".join(filters), "-map", "[out]", "-t", str(DURATION), "-c:a", "aac",
                    "-b:a", "192k", path], check=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    assets = load_assets()
    bg, tag, btn = make_background(), brand_tag(), cta_button(0)
    if "--preview" in sys.argv:
        for t in [1.5, 5.0, 7.5, 10.5, 14.0, 16.5, 18.7, 19.5, 23.0]:
            render_frame(t, assets, bg, tag, btn).save(os.path.join(OUT, f"preview_{t:05.2f}.jpg"),
                                                       quality=88)
        return
    audio = os.path.join(OUT, "_audio.m4a")
    mix_audio(audio)
    video = os.path.join(OUT, "aqlam_reel.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio,
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-c:a", "copy", "-shortest", "-movflags", "+faststart", video],
                         stdin=subprocess.PIPE)
    n = int(DURATION * FPS)
    for i in range(n):
        p.stdin.write(render_frame(i / FPS, assets, bg, tag, btn).tobytes())
    p.stdin.close()
    p.wait()
    os.remove(audio)
    print("wrote", video)


if __name__ == "__main__":
    main()
