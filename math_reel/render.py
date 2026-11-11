#!/usr/bin/env python3
"""Aqlam math-awareness reel: "When will I ever use math?"  1080x1920 @ 30fps.

Content-first motion graphics; stickers are small, corner-only accents.
Usage: python3 render.py [--preview]
"""
import math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
AUD = os.path.join(HERE, "audio")
W, H, FPS = 1080, 1920, 30

GREEN = (62, 142, 47)
GREEN_D = (38, 98, 30)
GREEN_L = (226, 240, 220)
ACCENT = (245, 166, 35)
RED = (214, 64, 52)
INK = (30, 42, 30)
GREY = (150, 160, 150)
BG = (251, 252, 248)
GRID = (226, 233, 222)

FB = os.path.join(HERE, "fonts", "Cairo-900.ttf")
FM = os.path.join(HERE, "fonts", "Cairo-700.ttf")
FSYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# scene boundaries (seconds) and voice start times
SC = [0.0, 3.9, 8.5, 15.5, 20.4, 25.0, 31.6, 37.6]
DURATION = SC[-1]
VOICE = [(f"v{i + 1}.wav", SC[i] + 0.25) for i in range(7)]
# (file, scene index, time within scene, volume) -- synced to the voice's word timings
_SFX = [
    ("typing.mp3", 0, 0.3, 0.5), ("pop.mp3", 0, 0.6, 0.7),
    ("whoosh.mp3", 1, -0.05, 0.6), ("ticks.mp3", 1, 0.35, 0.5), ("ding.mp3", 1, 1.5, 0.6),
    ("whoosh.mp3", 2, -0.05, 0.6), ("pop.mp3", 2, 0.15, 0.6), ("stamp.mp3", 2, 1.0, 1.0),
    ("ticks.mp3", 2, 2.8, 0.5), ("ding.mp3", 2, 4.2, 0.5), ("pop.mp3", 2, 5.2, 0.6),
    ("whoosh.mp3", 3, -0.05, 0.6), ("whoosh.mp3", 3, 1.0, 0.35), ("pop.mp3", 3, 3.0, 0.6), ("ding.mp3", 3, 3.7, 0.5),
    ("whoosh.mp3", 4, -0.05, 0.6), ("digital.mp3", 4, 0.4, 0.45), ("pop.mp3", 4, 1.75, 0.5),
    ("pop.mp3", 4, 2.05, 0.5), ("pop.mp3", 4, 2.35, 0.5), ("ding.mp3", 4, 3.0, 0.5),
    ("whoosh.mp3", 5, -0.05, 0.6), ("ding.mp3", 5, 3.05, 0.6),
    ("whoosh.mp3", 6, -0.05, 0.6), ("pop.mp3", 6, 1.4, 0.6), ("ding.mp3", 6, 2.2, 0.4),
]
SFX = [(f, SC[i] + at, v) for f, i, at, v in _SFX]

_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


# ------------------------------------------------------------- easing
def cl(x):
    return min(max(x, 0.0), 1.0)


def back(x, s=1.9):
    x = cl(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def out3(x):
    return 1 - (1 - cl(x)) ** 3


def prog(t, a, d):
    return cl((t - a) / d)


# ------------------------------------------------------------- text
_tc = {}


def text_img(s, size, color, f=FB, rtl=True):
    k = (s, size, color, f, rtl)
    if k in _tc:
        return _tc[k]
    fo = font(f, size)
    kw = dict(direction="rtl", language="ar") if rtl else {}
    l, t, r, b = fo.getbbox(s, anchor="ls", **kw)
    im = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), s, font=fo, fill=color, anchor="ls", **kw)
    _tc[k] = im
    return im


def pill(s, size, fg=(255, 255, 255), bg=GREEN, shade=GREEN_D, px=None, py=None):
    k = ("pill", s, size, fg, bg)
    if k in _tc:
        return _tc[k]
    t = text_img(s, size, fg)
    px = px or int(size * 0.42)
    py = py or int(size * 0.22)
    im = Image.new("RGBA", (t.width + 2 * px, t.height + 2 * py + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rr = min(40, im.height // 2)
    if shade:
        d.rounded_rectangle((0, 12, im.width - 1, im.height - 1), rr, fill=shade)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 13), rr, fill=bg)
    im.alpha_composite(t, (px, py))
    _tc[k] = im
    return im


def put(canvas, im, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if abs(scale - 1) > 0.003:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    if x >= 0 and y >= 0 and x + im.width <= canvas.width and y + im.height <= canvas.height:
        canvas.alpha_composite(im, (x, y))
    else:
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(im, (x, y), im)
        canvas.alpha_composite(layer)


def pop(canvas, im, cx, cy, t, at, dur=0.4, rot0=6.0):
    k = back((t - at) / dur)
    if t < at:
        return
    put(canvas, im, cx, cy, 0.2 + 0.8 * k if k < 1 else k, rot=(1 - cl(k)) * rot0)


# ------------------------------------------------------------- icons
def icon_tag(s, color=GREEN):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(s * .18, s * .18), (s * .55, s * .18), (s * .88, s * .52), (s * .52, s * .88), (s * .18, s * .55)],
              fill=color)
    d.ellipse((s * .3, s * .3, s * .42, s * .42), fill=(255, 255, 255))
    return im


def icon_clock(s, color=GREEN, ang=0):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(4, s // 12)
    d.ellipse((s * .1, s * .1, s * .9, s * .9), outline=color, width=w)
    c = s / 2
    for a, L in ((ang, .3), (ang / 12 + 1.0, .2)):
        d.line((c, c, c + s * L * math.sin(a), c - s * L * math.cos(a)), fill=color, width=w)
    d.ellipse((c - w, c - w, c + w, c + w), fill=color)
    return im


def icon_phone(s, color=GREEN):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(4, s // 12)
    d.rounded_rectangle((s * .3, s * .1, s * .7, s * .9), s // 10, outline=color, width=w)
    d.line((s * .44, s * .8, s * .56, s * .8), fill=color, width=w)
    return im


def icon_camera(s, color=GREEN):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((s * .12, s * .3, s * .88, s * .8), s // 10, fill=color)
    d.rectangle((s * .36, s * .2, s * .6, s * .32), fill=color)
    d.ellipse((s * .34, s * .38, s * .66, s * .7), fill=(255, 255, 255))
    d.ellipse((s * .42, s * .46, s * .58, s * .62), fill=color)
    return im


def icon_pin(s, color=RED):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((s * .22, s * .1, s * .78, s * .66), fill=color)
    d.polygon([(s * .27, s * .5), (s * .73, s * .5), (s * .5, s * .92)], fill=color)
    d.ellipse((s * .4, s * .28, s * .6, s * .48), fill=(255, 255, 255))
    return im


def icon_game(s, color=ACCENT):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((s * .1, s * .3, s * .9, s * .72), s // 5, fill=color)
    d.rectangle((s * .22, s * .47, s * .4, s * .55), fill=(255, 255, 255))
    d.rectangle((s * .27, s * .42, s * .35, s * .6), fill=(255, 255, 255))
    d.ellipse((s * .62, s * .4, s * .7, s * .48), fill=(255, 255, 255))
    d.ellipse((s * .7, s * .52, s * .78, s * .6), fill=(255, 255, 255))
    return im


def icon_bulb(s, color=ACCENT):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((s * .25, s * .1, s * .75, s * .6), fill=color)
    d.polygon([(s * .33, s * .5), (s * .67, s * .5), (s * .6, s * .7), (s * .4, s * .7)], fill=color)
    d.rounded_rectangle((s * .38, s * .72, s * .62, s * .86), s // 25, fill=INK)
    return im


def badge(icon, s, ring=GREEN):
    im = Image.new("RGBA", (s + 30, s + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((15, 25, s + 15, s + 25 + 10), fill=(0, 0, 0, 30))
    d.ellipse((15, 15, s + 15, s + 15), fill=(255, 255, 255), outline=ring, width=8)
    ic = icon.resize((int(s * .62), int(s * .62)), Image.LANCZOS)
    im.alpha_composite(ic, (15 + (s - ic.width) // 2, 15 + (s - ic.height) // 2))
    return im


# ------------------------------------------------------------- stickers
def load_sticker(name, width):
    im = Image.open(os.path.join(HERE, "stickers", name + ".png")).convert("RGBA")
    im = im.crop((0, 0, im.width, im.height - 14))
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    pad = 24
    sh = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", im.size, (20, 40, 20, 60)), (pad, pad + 10), im.getchannel("A"))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    sh.alpha_composite(im, (pad, pad))
    return sh


# ------------------------------------------------------------- background
def make_bg():
    bg = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(bg)
    for x in range(0, W, 54):
        d.line((x, 0, x, H), fill=GRID, width=2)
    for y in range(0, H, 54):
        d.line((0, y, W, y), fill=GRID, width=2)
    d.line((96, 0, 96, H), fill=(240, 196, 190), width=3)  # notebook margin
    return bg


random.seed(3)
EQS = ["x² + 5x = 14", "a² + b² = c²", "√49 = 7", "y = mx + b", "π ≈ 3.14", "¾ + ⅛ = ?",
       "2(x − 3) = 10", "Σ n", "√2 ≈ 1.41", "x ÷ 4 = 9", "7 × 8 = ?"]
def _eq_pos():
    out = []
    while len(out) < len(EQS):
        x, y = random.uniform(170, 910), random.uniform(290, 1640)
        if 40 < x < 1040 and 360 < y < 1010:      # question card
            continue
        if x < 420 and y > 1260:                  # sticker corner
            continue
        tries = getattr(_eq_pos, "n", 0) + 1
        _eq_pos.n = tries
        if tries < 20000 and any(abs(x - a) < 260 and abs(y - b) < 80 for a, b, *_ in out):
            continue
        out.append((x, y, random.uniform(-14, 14), random.uniform(0, 6.28), random.choice([46, 54, 62])))
    return out


EQ_POS = _eq_pos()


def draw_equations(c, t, lt, fall):
    for (x, y, r, ph, sz), e in zip(EQ_POS, EQS):
        shake = 2 + 6 * cl(lt / 4.0)
        dx = shake * math.sin(t * 31 + ph)
        dy = shake * math.cos(t * 27 + ph) + fall * fall * 2200 * (0.6 + 0.4 * math.sin(ph))
        im = text_img(e, sz, (120, 150, 115, 150), FSYM, rtl=False)
        put(c, im, x + dx, y + dy, rot=r + fall * 60 * math.sin(ph))


# ------------------------------------------------------------- scenes
def scene1(c, t, lt, A):  # hook
    draw_equations(c, t, lt, 0)
    put(c, A["card"], 540, 690, 1, 0, cl(lt / 0.25))
    pop(c, text_img("متى بستخدم", 104, INK), 540, 520, lt, 0.35)
    pop(c, pill("الرياضيات", 120), 540, 700, lt, 1.8)
    pop(c, text_img("في حياتي؟", 104, INK), 540, 865, lt, 2.6)
    # small sticker, corner only
    k = back((lt - 0.6) / 0.4)
    if lt > 0.6:
        put(c, A["M2"], 205, 1490 + 6 * math.sin(t * 3.4), 0.3 + 0.7 * k if k < 1 else 1)


def scene2(c, t, lt, A):  # twist: every day
    if lt < 1.0:
        draw_equations(c, t, lt + 4.7, out3(lt / 1.0))
    # counter 0 -> 365
    k = out3((lt - 0.35) / 1.0)
    n = int(round(365 * k))
    digits = "".join("٠١٢٣٤٥٦٧٨٩"[int(ch)] for ch in str(n))
    if lt > 0.3:
        put(c, text_img(digits, 300, GREEN), 540, 640, back((lt - 0.3) / 0.35))
        pop(c, text_img("يوم في السنة", 70, GREY), 540, 860, lt, 0.5)
    pop(c, pill("الجواب: كل يوم!", 104, bg=ACCENT, shade=(196, 126, 20)), 540, 1110, lt, 1.5, 0.45, -8)
    pop(c, text_img("…وبدون ما تنتبه", 72, INK), 540, 1290, lt, 2.6)


def label(c, s, lt):
    pop(c, pill(s, 58, fg=GREEN_D, bg=GREEN_L, shade=None), 540, 330, lt, 0.05)


def scene3(c, t, lt, A):  # shopping
    label(c, "التسوق", lt)
    # price tag (swinging)
    tag = A["tag"].copy()
    td = ImageDraw.Draw(tag)
    swing = 4 * math.sin(t * 2.2)
    # strike + new price
    strike = out3((lt - 2.8) / 0.35)
    if strike > 0:
        x0, x1 = 120, 120 + (tag.width - 240) * strike
        td.line((x0, 205, x1, 175), fill=RED, width=16)
    k = back(lt / 0.45)
    if lt > 0:
        put(c, tag, 540, 760, 0.3 + 0.7 * k if k < 1 else 1, rot=-5 + swing + (1 - cl(k)) * 20)
    # stamp
    if lt > 1.0:
        ks = out3((lt - 1.0) / 0.18)
        sc = 2.4 - 1.4 * ks
        sh = (1 - cl((lt - 1.18) / 0.25)) * 10 if lt > 1.18 else 0
        put(c, A["stamp"], 760 + sh * math.sin(t * 90), 560, sc, rot=14, alpha=0.4 + 0.6 * ks)
    # new price counter
    if lt > 2.8:
        v = 200 - int(round(60 * out3((lt - 2.8) / 1.4)))
        s = "".join("٠١٢٣٤٥٦٧٨٩"[int(ch)] for ch in str(v)) + " ريال"
        put(c, pill(s, 110, bg=GREEN), 540, 1080, back((lt - 2.8) / 0.4))
    pop(c, text_img("٢٠٠ − ٣٠٪ = ١٤٠", 92, INK), 540, 1290, lt, 4.2)
    pop(c, pill("نسبة مئوية ٪", 76, bg=ACCENT, shade=(196, 126, 20)), 540, 1460, lt, 5.2)


ROUTE = [(200, 1080), (260, 820), (520, 900), (620, 700), (860, 640), (880, 470)]


def bez(pts, u):
    p = list(pts)
    while len(p) > 1:
        p = [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u) for a, b in zip(p, p[1:])]
    return p[0]


def scene4(c, t, lt, A):  # time & speed
    label(c, "الوقت", lt)
    d = ImageDraw.Draw(c)
    k = out3(lt / 0.6)
    pts = [bez(ROUTE, i / 80) for i in range(int(80 * k) + 1)]
    if len(pts) > 1:
        d.line(pts, fill=(205, 212, 200), width=56, joint="curve")
        for i in range(0, len(pts) - 1, 4):
            d.line(pts[i:i + 2], fill=(255, 255, 255), width=6)
    pop(c, A["pin_g"], 200, 1040, lt, 0.1)
    pop(c, A["pin_r"], 880, 395, lt, 0.4)
    pop(c, text_img("١٢٠ كم", 64, INK), 330, 690, lt, 0.7)
    # car
    u = out3((lt - 0.3) / 2.5) if lt > 0.3 else 0
    x, y = bez(ROUTE, u)
    x2, y2 = bez(ROUTE, min(1, u + 0.01))
    ang = -math.degrees(math.atan2(y2 - y, x2 - x))
    if lt > 0.2:
        put(c, A["car"], x, y, back((lt - 0.2) / 0.3), rot=ang)
    # clock
    clk = icon_clock(220, INK, ang=t * 6)
    pop(c, clk, 860, 1000, lt, 0.5)
    pop(c, text_img("١٢٠ كم ÷ ٨٠ كم/س", 88, INK), 540, 1260, lt, 3.0)
    pop(c, pill("= ساعة ونص", 100), 540, 1420, lt, 3.7)
    pop(c, pill("قسمة وسرعة", 64, bg=ACCENT, shade=(196, 126, 20)), 540, 1570, lt, 3.3)


random.seed(11)
BIN_COLS = [(random.uniform(0, 1), random.uniform(160, 380), [random.choice("01") for _ in range(30)])
            for _ in range(9)]


def scene5(c, t, lt, A):  # phone / apps
    label(c, "التقنية", lt)
    k = back(lt / 0.45)
    if lt <= 0:
        return
    ph = Image.new("RGBA", (480, 880), (0, 0, 0, 0))
    d = ImageDraw.Draw(ph)
    d.rounded_rectangle((0, 0, 479, 879), 70, fill=INK)
    d.rounded_rectangle((22, 22, 457, 857), 52, fill=(18, 34, 20))
    d.rounded_rectangle((190, 40, 290, 62), 11, fill=INK)
    f = font(FSYM, 34)
    for i, (off, speed, chars) in enumerate(BIN_COLS):
        x = 50 + i * 46
        y0 = ((lt * speed + off * 900) % 900) - 300
        for j, ch in enumerate(chars[:22]):
            y = y0 + j * 40
            if 70 < y < 830:
                a = int(255 * (1 - j / 22))
                d.text((x, y), ch, font=f, fill=(110, 210, 90, a))
    put(c, ph, 540, 860, 0.3 + 0.7 * k if k < 1 else 1)
    for i, (key, x, y) in enumerate([("cam", 200, 560), ("pin", 880, 720), ("game", 210, 1150)]):
        at = 1.75 + i * 0.3
        if lt > at:
            u = out3((lt - at) / 0.45)
            put(c, A[key], 540 + (x - 540) * u, 860 + (y - 860) * u, 0.3 + 0.7 * back((lt - at) / 0.45),
                rot=4 * math.sin(t * 2 + i))
    pop(c, pill("كل تطبيق = رياضيات", 96), 540, 1470, lt, 3.0)


def scene6(c, t, lt, A):  # way of thinking
    pop(c, text_img("الرياضيات مو بس مادة…", 88, INK), 540, 420, lt, 0.15)
    center = (540, 900)
    nodes = [(250, 700, "b_tag"), (830, 700, "b_clock"), (540, 1210, "b_phone")]
    d = ImageDraw.Draw(c)
    for i, (x, y, key) in enumerate(nodes):
        u = out3((lt - 2.9 - i * 0.15) / 0.5)
        if u > 0:
            ex, ey = x + (center[0] - x) * u, y + (center[1] - y) * u
            d.line((x, y, ex, ey), fill=GREEN, width=10)
    for i, (x, y, key) in enumerate(nodes):
        pop(c, A[key], x, y + 6 * math.sin(t * 2 + i), lt, 0.5 + i * 0.25)
    if lt > 3.0:
        glow = 1 + 0.05 * math.sin(lt * 6)
        put(c, A["b_bulb"], center[0], center[1], back((lt - 3.0) / 0.45) * glow)
    pop(c, pill("هي طريقة تفكير", 110), 540, 1440, lt, 3.05, 0.45, -6)
    pop(c, text_img("تساعدك تحل أي مشكلة", 66, GREY), 540, 1590, lt, 4.0)


def scene7(c, t, lt, A):  # CTA
    pop(c, text_img("تابعوا", 96, INK), 540, 520, lt, 0.15)
    k = back((lt - 0.4) / 0.5)
    if lt > 0.4:
        put(c, text_img("أقلام", 260, GREEN), 540, 720, k)
        u = out3((lt - 0.8) / 0.5)
        d = ImageDraw.Draw(c)
        d.line((540 - 230 * u, 900, 540 + 230 * u, 900), fill=ACCENT, width=14)
    pop(c, text_img("ونخلي الرياضيات أسهل وأقرب لك", 62, INK), 540, 1010, lt, 1.4)
    if lt > 1.6:
        pulse = 1 + 0.05 * math.sin((lt - 1.6) * 2 * math.pi / 0.9)
        put(c, pill("+ تابعنا", 84, bg=INK, shade=(0, 0, 0)), 690, 1300, back((lt - 1.6) / 0.4) * pulse)
    # small sticker pointing at the follow button
    if lt > 1.4:
        kk = back((lt - 1.4) / 0.4)
        put(c, A["W5"], 250, 1420 + 6 * math.sin(t * 3), 0.3 + 0.7 * kk if kk < 1 else 1)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]


# ------------------------------------------------------------- assets
def build_assets():
    A = {"M2": load_sticker("M2", 250), "W5": load_sticker("W5", 300)}
    card = Image.new("RGBA", (900, 600), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, 899, 599), 48, fill=(255, 255, 255, 235),
                                           outline=GRID, width=4)
    A["card"] = card
    # price tag
    tag = Image.new("RGBA", (780, 380), (0, 0, 0, 0))
    d = ImageDraw.Draw(tag)
    d.rounded_rectangle((90, 20, 770, 360), 44, fill=(255, 255, 255), outline=INK, width=10)
    d.polygon([(10, 190), (100, 30), (100, 350)], fill=(255, 255, 255))
    d.line([(100, 26), (12, 190), (100, 354)], fill=INK, width=10, joint="curve")
    d.ellipse((70, 170, 110, 210), outline=INK, width=8)
    t = text_img("٢٠٠ ريال", 140, INK)
    tag.alpha_composite(t, (440 - t.width // 2, 190 - t.height // 2))
    A["tag"] = tag
    st = Image.new("RGBA", (500, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle((6, 6, 493, 183), 26, outline=RED, width=12)
    s = text_img("خصم ٣٠٪", 92, RED)
    st.alpha_composite(s, (250 - s.width // 2, 95 - s.height // 2))
    A["stamp"] = st
    A["pin_g"] = icon_pin(110, GREEN)
    A["pin_r"] = icon_pin(130, RED)
    car = Image.new("RGBA", (130, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(car)
    d.rounded_rectangle((0, 8, 129, 72), 22, fill=ACCENT, outline=INK, width=5)
    d.rounded_rectangle((70, 18, 108, 62), 10, fill=(200, 230, 245))
    A["car"] = car
    A["cam"] = badge(icon_camera(200), 190)
    A["pin"] = badge(icon_pin(200), 190, RED)
    A["game"] = badge(icon_game(200), 190, ACCENT)
    A["b_tag"] = badge(icon_tag(200), 200)
    A["b_clock"] = badge(icon_clock(200, GREEN, 2.0), 200)
    A["b_phone"] = badge(icon_phone(200), 200)
    A["b_bulb"] = badge(icon_bulb(240), 260, ACCENT)
    tag_im = pill("أقلام", 44)
    A["brand"] = tag_im
    return A


def frame(t, A, bg):
    c = bg.copy()
    i = max(j for j in range(len(SCENES)) if SC[j] <= t)
    lt = t - SC[i]
    dur = SC[i + 1] - SC[i]
    last = i == len(SCENES) - 1
    out_k = 0 if last else cl((lt - (dur - 0.22)) / 0.22)
    if out_k > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        SCENES[i](layer, t, lt, A)
        put(c, layer, W / 2, H / 2 - 60 * out_k, 1 - 0.08 * out_k, alpha=1 - out_k)
    else:
        SCENES[i](c, t, lt, A)
    put(c, A["brand"], 540, 175)
    if t > DURATION - 0.5:
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * cl((t - DURATION + 0.5) / 0.5)))))
    return c.convert("RGB")


def mix_audio(path):
    ins, fl, lb = [], [], []
    clips = [(f, a, 1.7) for f, a in VOICE] + list(SFX)
    for i, (f, a, v) in enumerate(clips):
        ins += ["-i", os.path.join(AUD, f)]
        ms = int(a * 1000)
        fl.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[a{i}]")
        lb.append(f"[a{i}]")
    n = len(clips)
    ins += ["-i", os.path.join(AUD, "music.mp3")]
    fl.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.2,atrim=0:{DURATION},"
              f"afade=t=in:d=0.5,afade=t=out:st={DURATION - 2}:d=2[m]")
    lb.append("[m]")
    fl.append("".join(lb) + f"amix=inputs={n + 1}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fl),
                    "-map", "[out]", "-t", str(DURATION), "-c:a", "aac", "-b:a", "192k", path], check=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    A, bg = build_assets(), make_bg()
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[2:]] or [3.5, 6.8, 11.0, 15.0, 21.8, 27.5, 33.0, 38.5]
        for t in ts:
            frame(t, A, bg).save(os.path.join(OUT, f"preview_{t:05.2f}.jpg"), quality=88)
        return
    audio = os.path.join(OUT, "_audio.m4a")
    mix_audio(audio)
    video = os.path.join(OUT, "math_reel.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264",
                          "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy",
                          "-shortest", "-movflags", "+faststart", video], stdin=subprocess.PIPE)
    for i in range(int(DURATION * FPS)):
        p.stdin.write(frame(i / FPS, A, bg).tobytes())
    p.stdin.close()
    p.wait()
    os.remove(audio)
    print("wrote", video)


if __name__ == "__main__":
    main()
