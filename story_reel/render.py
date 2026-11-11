#!/usr/bin/env python3
"""Aqlam story reel: Sarah finds the right tutor with the Aqlam app.  1080x1920 @ 30fps.

The story and the app screens are the content; stickers appear only as a small
tutor photo and a small thumbs-up at the end.
Usage: python3 render.py [--preview [t ...]]
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
ACCENT_D = (196, 126, 20)
RED = (214, 64, 52)
INK = (30, 42, 30)
GREY = (140, 150, 140)
LINE = (225, 230, 222)
BG = (250, 251, 247)
WHITE = (255, 255, 255)

FB = os.path.join(HERE, "fonts", "Cairo-900.ttf")
FM = os.path.join(HERE, "fonts", "Cairo-700.ttf")

# scene boundaries; voice line i starts 0.25s into scene i
SC = [0.0, 7.6, 13.1, 15.6, 21.0, 25.2, 29.8, 33.8, 41.0]
DURATION = SC[-1]
VOICE = [(f"v{i + 1}.wav", SC[i] + 0.25) for i in range(8)]
_SFX = [
    ("pop.mp3", 0, 0.25, 0.6), ("pop.mp3", 0, 0.95, 0.5), ("ticks.mp3", 0, 1.9, 0.45),
    ("typing.mp3", 0, 5.6, 0.5),
    ("whoosh.mp3", 1, -0.05, 0.6), ("pop.mp3", 1, 0.3, 0.5), ("pop.mp3", 1, 1.0, 0.5),
    ("pop.mp3", 1, 1.7, 0.5), ("stamp.mp3", 1, 3.75, 0.5),
    ("whoosh.mp3", 2, -0.05, 0.6), ("digital.mp3", 2, 0.4, 0.5), ("ding.mp3", 2, 1.3, 0.6),
    ("pop.mp3", 3, 0.75, 0.6), ("whoosh.mp3", 3, 1.6, 0.45), ("ding.mp3", 3, 3.4, 0.5),
    ("pop.mp3", 4, 0.9, 0.6), ("pop.mp3", 4, 1.7, 0.6), ("ding.mp3", 4, 1.85, 0.7),
    ("whoosh.mp3", 5, -0.05, 0.6), ("typing.mp3", 5, 1.0, 0.5), ("ding.mp3", 5, 2.9, 0.5),
    ("whoosh.mp3", 6, -0.05, 0.6), ("stamp.mp3", 6, 2.35, 1.0), ("ding.mp3", 6, 2.45, 0.6),
    ("whoosh.mp3", 7, -0.05, 0.6), ("pop.mp3", 7, 1.5, 0.5), ("pop.mp3", 7, 3.4, 0.6),
]
SFX = [(f, SC[i] + at, v) for f, i, at, v in _SFX]

# ------------------------------------------------------------- basics
_fc, _tc = {}, {}


def font(path, size):
    if (path, size) not in _fc:
        _fc[(path, size)] = ImageFont.truetype(path, size)
    return _fc[(path, size)]


def cl(x):
    return min(max(x, 0.0), 1.0)


def back(x, s=1.9):
    x = cl(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def out3(x):
    return 1 - (1 - cl(x)) ** 3


def inout(x):
    x = cl(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def num(n):
    return "".join("٠١٢٣٤٥٦٧٨٩"[int(c)] if c.isdigit() else c for c in str(n))


def text_img(s, size, color, f=FB):
    k = (s, size, color, f)
    if k not in _tc:
        fo = font(f, size)
        l, t, r, b = fo.getbbox(s, anchor="ls", direction="rtl", language="ar")
        im = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4 - l, 4 - t), s, font=fo, fill=color, anchor="ls",
                                direction="rtl", language="ar")
        _tc[k] = im
    return _tc[k]


def pill(s, size, fg=WHITE, bg=GREEN, shade=GREEN_D, f=FB):
    k = ("pill", s, size, fg, bg, shade, f)
    if k not in _tc:
        t = text_img(s, size, fg, f)
        px, py = int(size * .45), int(size * .2)
        sh = 10 if shade else 0
        im = Image.new("RGBA", (t.width + 2 * px, t.height + 2 * py + sh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        rr = min(40, (im.height - sh) // 2)
        if shade:
            d.rounded_rectangle((0, sh, im.width - 1, im.height - 1), rr, fill=shade)
        d.rounded_rectangle((0, 0, im.width - 1, im.height - 1 - sh), rr, fill=bg)
        im.alpha_composite(t, (px, py))
        _tc[k] = im
    return _tc[k]


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


def pop(canvas, im, cx, cy, lt, at, dur=0.4, rot0=6.0):
    if lt < at:
        return
    k = back((lt - at) / dur)
    put(canvas, im, cx, cy, 0.2 + 0.8 * k if k < 1 else k, rot=(1 - cl(k)) * rot0)


def card(w, h, r=36, fill=WHITE, outline=LINE, shadow=True):
    pad = 24 if shadow else 0
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 10, pad + w, pad + h + 10), r, fill=(20, 40, 20, 45))
        im = sh.filter(ImageFilter.GaussianBlur(12))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w - 1, pad + h - 1), r, fill=fill,
                                         outline=outline, width=3 if outline else 0)
    return im, pad


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * .45
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def check(d, cx, cy, s, color, width):
    d.line([(cx - s * .5, cy), (cx - s * .12, cy + s * .38), (cx + s * .55, cy - s * .4)], fill=color,
           width=width, joint="curve")


def tap(canvas, x, y, lt, at):
    """finger-tap ripple"""
    if not (at <= lt < at + 0.5):
        return
    k = (lt - at) / 0.5
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = 20 + 60 * k
    d.ellipse((x - r, y - r, x + r, y + r), outline=GREEN + (int(220 * (1 - k)),), width=8)
    d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(30, 42, 30, int(120 * (1 - k))))
    canvas.alpha_composite(layer)


# ------------------------------------------------------------- assets
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


def avatar(size, ring=GREEN):
    src = Image.open(os.path.join(HERE, "stickers", "W3.png")).convert("RGBA")
    w, h = src.size
    s = int(w * .62)
    face = src.crop((int(w * .2), int(h * .03), int(w * .2) + s, int(h * .03) + s)).resize((size, size), Image.LANCZOS)
    bgc = Image.new("RGBA", (size, size), GREEN_L + (255,))
    bgc.alpha_composite(face)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size + 12, size + 12), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, size + 11, size + 11), fill=ring)
    out.paste(bgc, (6, 6), mask)
    return out


def person_icon(size, color=GREY):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, size - 1, size - 1), fill=(236, 239, 233))
    d.ellipse((size * .33, size * .2, size * .67, size * .54), fill=color)
    d.pieslice((size * .18, size * .58, size * .82, size * 1.15), 180, 360, fill=color)
    return im


def student_badge():
    """Sarah: a simple flat student icon (hijab silhouette + graduation cap)."""
    s = 300
    im = Image.new("RGBA", (s, s + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 20, s - 1, s + 19), fill=WHITE, outline=GREEN, width=10)
    # body / abaya
    d.pieslice((60, 200, 240, 380), 180, 360, fill=INK)
    # hijab
    d.ellipse((92, 88, 208, 216), fill=INK)
    d.ellipse((112, 112, 188, 200), fill=(236, 200, 170))
    # eyes + smile
    d.ellipse((133, 145, 143, 155), fill=INK)
    d.ellipse((157, 145, 167, 155), fill=INK)
    d.arc((136, 158, 164, 182), 20, 160, fill=INK, width=4)
    # cap
    d.polygon([(150, 48), (240, 84), (150, 118), (60, 84)], fill=GREEN)
    d.rectangle((112, 92, 188, 116), fill=GREEN_D)
    d.line((232, 86, 232, 140), fill=ACCENT, width=6)
    d.ellipse((224, 136, 240, 152), fill=ACCENT)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).ellipse((5, 25, s - 6, s + 14), fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    ImageDraw.Draw(out).ellipse((0, 20, s - 1, s + 19), outline=GREEN, width=10)
    # cap drawn again over the ring so it pokes out
    d2 = ImageDraw.Draw(out)
    d2.polygon([(150, 0), (250, 40), (150, 78), (50, 40)], fill=GREEN)
    d2.rectangle((108, 50, 192, 80), fill=GREEN_D)
    d2.line((242, 42, 242, 100), fill=ACCENT, width=6)
    d2.ellipse((234, 96, 250, 112), fill=ACCENT)
    return out


def make_bg():
    bg = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(bg)
    for y in range(40, H, 60):
        for x in range(30 + (y // 60 % 2) * 30, W, 60):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(222, 229, 216))
    return bg


# ------------------------------------------------------------- phone + app screens
PW, PH = 500, 980          # screen size
PX, PY = 540, 1010          # phone centre on canvas


def phone_frame():
    im = Image.new("RGBA", (PW + 44, PH + 44), (0, 0, 0, 0))
    sh = Image.new("RGBA", (PW + 104, PH + 104), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 44, PW + 74, PH + 88), 78, fill=(20, 40, 20, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, PW + 43, PH + 43), 76, fill=INK)
    return im, sh


def screen_base(title=None):
    s = Image.new("RGBA", (PW, PH), WHITE + (255,))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle((PW / 2 - 70, 14, PW / 2 + 70, 44), 15, fill=INK)  # notch
    if title:
        d.rectangle((0, 0, PW, 170), fill=GREEN)
        d.rounded_rectangle((PW / 2 - 70, 14, PW / 2 + 70, 44), 15, fill=INK)
        t = text_img(title, 46, WHITE)
        s.alpha_composite(t, (PW - 36 - t.width, 92))
    return s


SUBJECTS = [("رياضيات", "÷×"), ("فيزياء", "⚛"), ("كيمياء", "⚗"), ("إنجليزي", "Aa")]


def screen_subjects(lt, sel_at):
    s = screen_base("اختر المادة")
    d = ImageDraw.Draw(s)
    for i, (name, _) in enumerate(SUBJECTS):
        col, row = 1 - i % 2, i // 2      # RTL: first item top-right
        x0, y0 = 30 + col * 230, 210 + row * 250
        sel = i == 0 and lt >= sel_at
        d.rounded_rectangle((x0, y0, x0 + 210, y0 + 220), 30,
                            fill=GREEN if sel else (244, 247, 241), outline=GREEN if sel else LINE, width=4)
        t = text_img(name, 40, WHITE if sel else INK)
        s.alpha_composite(t, (int(x0 + 105 - t.width / 2), y0 + 140))
        # simple glyph icons
        cx, cy = x0 + 105, y0 + 80
        c = WHITE if sel else GREEN
        if i == 0:
            d.line((cx - 30, cy, cx + 30, cy), fill=c, width=8)
            d.ellipse((cx - 6, cy - 26, cx + 6, cy - 14), fill=c)
            d.ellipse((cx - 6, cy + 14, cx + 6, cy + 26), fill=c)
        elif i == 1:
            for a in (0, 60, 120):
                d.ellipse((cx - 36, cy - 14, cx + 36, cy + 14), outline=c, width=5) if a == 0 else None
            d.ellipse((cx - 14, cy - 36, cx + 14, cy + 36), outline=c, width=5)
            d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=c)
        elif i == 2:
            d.polygon([(cx - 12, cy - 34), (cx + 12, cy - 34), (cx + 12, cy - 6), (cx + 34, cy + 32),
                       (cx - 34, cy + 32), (cx - 12, cy - 6)], outline=c, width=5)
            d.rectangle((cx - 26, cy + 14, cx + 26, cy + 28), fill=c)
        else:
            t2 = font(FB, 52)
            d.text((cx, cy), "Aa", font=t2, fill=c, anchor="mm")
    t = text_img("أو ابحث عن مادة…", 34, GREY, FM)
    d.rounded_rectangle((30, 740, PW - 30, 830), 45, fill=(244, 247, 241), outline=LINE, width=3)
    s.alpha_composite(t, (PW - 70 - t.width, 762))
    return s


def screen_tutors(lt, A, best_at):
    s = screen_base("المدرّس الأنسب لك")
    d = ImageDraw.Draw(s)
    for i in range(3):
        y0 = 200 + i * 245
        k = out3((lt - i * 0.15) / 0.4)
        if k <= 0:
            continue
        dx = int((1 - k) * 300)
        best = i == 0
        d.rounded_rectangle((24 + dx, y0, PW - 24 + dx, y0 + 220), 28,
                            fill=(240, 248, 236) if best else (248, 249, 246),
                            outline=GREEN if best else LINE, width=5 if best else 3)
        if best:
            s.alpha_composite(A["avatar"], (PW - 24 - 20 - A["avatar"].width + dx, y0 + 22))
        else:
            s.alpha_composite(A["person"], (PW - 24 - 26 - A["person"].width + dx, y0 + 28))
        name = "معلمة رياضيات" if best else "مدرّس رياضيات"
        t = text_img(name, 38, INK if best else GREY)
        s.alpha_composite(t, (PW - 210 - t.width + dx, y0 + 34))
        n_st = 5 if best else 4
        for j in range(5):
            star(d, PW - 230 - j * 40 + dx, y0 + 122, 16, ACCENT if j < n_st else LINE)
        if best and lt >= best_at:
            kb = back((lt - best_at) / 0.35)
            b = pill("الأنسب لك", 30, bg=ACCENT, shade=None)
            b = b.resize((max(1, int(b.width * kb)), max(1, int(b.height * kb))))
            s.alpha_composite(b, (PW - 210 - b.width + dx, y0 + 150))
    return s


DAYS = ["سبت", "أحد", "إثنين", "ثلاثاء", "أربعاء"]
SLOTS = ["٤:٠٠ م", "٥:٠٠ م", "٧:٠٠ م", "٨:٠٠ م"]


def screen_booking(lt, A, slot_at, confirm_at):
    s = screen_base("احجز موعدك")
    d = ImageDraw.Draw(s)
    s.alpha_composite(A["avatar_s"], (PW - 30 - A["avatar_s"].width, 196))
    t = text_img("معلمة رياضيات", 34, INK)
    s.alpha_composite(t, (PW - 130 - t.width, 214))
    for i, day in enumerate(DAYS):
        x1 = PW - 24 - i * 92
        sel = i == 2
        d.rounded_rectangle((x1 - 84, 310, x1, 420), 24, fill=GREEN if sel else (244, 247, 241),
                            outline=GREEN if sel else LINE, width=3)
        tt = text_img(day, 24, WHITE if sel else GREY, FM)
        s.alpha_composite(tt, (int(x1 - 42 - tt.width / 2), 324))
        n = text_img(num(12 + i), 38, WHITE if sel else INK)
        s.alpha_composite(n, (int(x1 - 42 - n.width / 2), 362))
    tt = text_img("الأوقات المتاحة", 32, GREY, FM)
    s.alpha_composite(tt, (PW - 30 - tt.width, 450))
    for i, sl in enumerate(SLOTS):
        col, row = 1 - i % 2, i // 2
        x0, y0 = 30 + col * 230, 510 + row * 110
        sel = i == 2 and lt >= slot_at
        d.rounded_rectangle((x0, y0, x0 + 210, y0 + 90), 24, fill=GREEN if sel else WHITE,
                            outline=GREEN, width=4)
        t = text_img(sl, 36, WHITE if sel else GREEN_D)
        s.alpha_composite(t, (int(x0 + 105 - t.width / 2), int(y0 + 45 - t.height / 2)))
    pressed = confirm_at <= lt < confirm_at + 0.15
    d.rounded_rectangle((30, 790 + (4 if pressed else 0), PW - 30, 890), 44, fill=INK)
    t = text_img("تأكيد الحجز", 40, WHITE)
    s.alpha_composite(t, (int(PW / 2 - t.width / 2), 812))
    # success overlay
    if lt >= confirm_at + 0.15:
        k = back((lt - confirm_at - 0.15) / 0.4)
        ov = Image.new("RGBA", (PW, PH), (255, 255, 255, int(235 * cl(k))))
        od = ImageDraw.Draw(ov)
        r = 110 * k
        od.ellipse((PW / 2 - r, 380 - r, PW / 2 + r, 380 + r), fill=GREEN)
        if k > 0.6:
            check(od, PW / 2, 380, 120, WHITE, 18)
        tt = text_img("تم الحجز!", 56, GREEN_D)
        tt2 = text_img("الإثنين ١٤ • ٧:٠٠ م", 34, GREY, FM)
        if k > 0.3:
            ov.alpha_composite(tt, (int(PW / 2 - tt.width / 2), 540))
            ov.alpha_composite(tt2, (int(PW / 2 - tt2.width / 2), 630))
        s.alpha_composite(ov)
    return s


EQ_STEPS = ["٢س + ٤ = ١٠", "٢س = ٦", "س = ٣"]


def screen_call(lt, A):
    s = Image.new("RGBA", (PW, PH), (24, 30, 26, 255))
    d = ImageDraw.Draw(s)
    # tutor video (top)
    d.rounded_rectangle((16, 60, PW - 16, 470), 30, fill=(214, 228, 208))
    vid = A["tutor_vid"]
    bob = int(3 * math.sin(lt * 4))
    s.alpha_composite(vid, (int(PW / 2 - vid.width / 2), 470 - vid.height + bob if bob > 0 else 470 - vid.height))
    d.rectangle((16, 466, PW - 16, 480), fill=(24, 30, 26))
    live = pill("مباشر", 24, bg=RED, shade=None)
    s.alpha_composite(live, (PW - 40 - live.width, 80))
    # whiteboard (bottom)
    d.rounded_rectangle((16, 490, PW - 16, 900), 30, fill=WHITE)
    for i, eq in enumerate(EQ_STEPS):
        at = 0.6 + i * 0.75
        if lt < at:
            continue
        k = cl((lt - at) / 0.5)
        t = text_img(eq, 52, GREEN_D if i == 2 else INK)
        w = int(t.width * k)
        crop = t.crop((t.width - w, 0, t.width, t.height))  # write right-to-left
        s.alpha_composite(crop, (PW - 50 - w, 520 + i * 110))
    if lt > 2.9:
        k = back((lt - 2.9) / 0.35)
        r = 34 * k
        d.ellipse((70 - r, 780 - r, 70 + r, 780 + r), fill=GREEN)
        if k > .6:
            check(d, 70, 780, 36, WHITE, 7)
    # call controls
    for i, c in enumerate([(70, 70, 70), RED, (70, 70, 70)]):
        x = PW / 2 + (i - 1) * 110
        d.ellipse((x - 34, 920, x + 34, 980 - 4), fill=c)
    return s


def draw_phone(c, screen, scale=1.0, cy=PY, rot=0.0, alpha=1.0, A=None):
    frame, shadow = A["phone"], A["phone_sh"]
    ph = frame.copy()
    mask = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PW - 1, PH - 1), 58, fill=255)
    ph.paste(screen, (22, 22), mask)
    put(c, shadow, PX, cy + 20, scale, rot, alpha)
    put(c, ph, PX, cy, scale, rot, alpha)


def step_label(c, n, s, lt, at=0.05, y=250):
    im = pill(f"{num(n)}  {s}", 54, fg=GREEN_D, bg=GREEN_L, shade=None)
    pop(c, im, 540, y, lt, at)


# ------------------------------------------------------------- scenes
def scene1(c, t, lt, A):  # Sarah's problem
    pop(c, A["sarah"], 540, 420, lt, 0.15, 0.5)
    pop(c, pill("هذي سارة", 72), 540, 650, lt, 0.75)
    # calendar countdown
    if lt > 1.7:
        k = back((lt - 1.7) / 0.45)
        cal = A["cal"].copy()
        d = ImageDraw.Draw(cal)
        days = 7 if lt > 2.6 else max(7, 30 - int((lt - 1.7) / 0.9 * 23))
        n = text_img(num(days), 170, RED)
        cal.alpha_composite(n, (int(cal.width / 2 - n.width / 2), 150))
        put(c, cal, 300, 1060, 0.3 + 0.7 * k if k < 1 else 1, rot=-4 + (1 - cl(k)) * 10)
    pop(c, text_img("اختبار الرياضيات", 58, INK), 300, 1330, lt, 3.1)
    # notebook with question marks
    if lt > 4.6:
        k = back((lt - 4.6) / 0.45)
        put(c, A["notebook"], 790, 1090, 0.3 + 0.7 * k if k < 1 else 1, rot=5 + (1 - cl(k)) * -10)
        for i, (x, y) in enumerate([(700, 1010), (850, 1120), (760, 1230)]):
            at = 5.7 + i * 0.15
            if lt > at:
                q = text_img("؟", 110, RED)
                put(c, q, x, y + 8 * math.sin(t * 5 + i), back((lt - at) / 0.3), rot=15 * math.sin(t * 3 + i))
    pop(c, pill("ما فهمت الدرس!", 64, bg=RED, shade=(160, 40, 32)), 790, 1420, lt, 5.8)


CHAT = [("أحد يعرف مدرس رياضيات زين؟", True, 0.3), ("جربي واحد أعرفه…", False, 1.0),
        ("بس جدوله مليان هالأسبوع", False, 1.7)]


def scene2(c, t, lt, A):  # the search chaos
    for i, (msg, mine, at) in enumerate(CHAT):
        if lt < at:
            continue
        b = A[f"chat{i}"]
        x = 1040 - b.width / 2 if mine else 40 + b.width / 2
        k = back((lt - at) / 0.35)
        put(c, b, x, 420 + i * 170, 0.3 + 0.7 * k if k < 1 else 1)
    shake = 6 * math.sin(t * 40) if 3.3 < lt < 3.7 else 0
    pop(c, pill("منو الأنسب لها؟", 80, bg=ACCENT, shade=ACCENT_D), 540 + shake, 1000, lt, 2.1, 0.4, -6)
    # schedule with clashes
    if lt > 3.5:
        k = back((lt - 3.5) / 0.4)
        put(c, A["clash"], 540, 1340, 0.3 + 0.7 * k if k < 1 else 1)
        d = ImageDraw.Draw(c)
        for i in range(5):
            at = 3.75 + i * 0.07
            if lt > at and i != 4:
                x, y = 540 + (2 - i) * 170, 1360
                kk = cl((lt - at) / 0.15)
                d.line((x - 40 * kk, y - 40 * kk, x + 40 * kk, y + 40 * kk), fill=RED, width=12)
                d.line((x + 40 * kk, y - 40 * kk, x - 40 * kk, y + 40 * kk), fill=RED, width=12)
    pop(c, text_img("ومتى بيكون فاضي؟", 66, INK), 540, 1560, lt, 3.7)


def scene3(c, t, lt, A):  # downloads Aqlam
    k = back(lt / 0.5)
    scr = screen_base()
    d = ImageDraw.Draw(scr)
    d.rectangle((0, 0, PW, PH), fill=GREEN)
    d.rounded_rectangle((PW / 2 - 70, 14, PW / 2 + 70, 44), 15, fill=INK)
    if lt < 1.25:  # download progress
        p = out3((lt - 0.2) / 1.0)
        d.rounded_rectangle((90, PH / 2 + 80, PW - 90, PH / 2 + 104), 12, fill=GREEN_D)
        d.rounded_rectangle((PW - 90 - (PW - 180) * p, PH / 2 + 80, PW - 90, PH / 2 + 104), 12, fill=WHITE)
        tt = text_img("جاري التحميل…", 34, (210, 236, 200), FM)
        scr.alpha_composite(tt, (int(PW / 2 - tt.width / 2), int(PH / 2 + 120)))
    logo = text_img("أقلام", 140, WHITE)
    kl = back((lt - 1.25) / 0.45) if lt > 1.25 else 0.85
    lg = logo.resize((int(logo.width * kl), int(logo.height * kl)))
    scr.alpha_composite(lg, (int(PW / 2 - lg.width / 2), int(PH / 2 - 60 - lg.height / 2)))
    draw_phone(c, scr, 0.3 + 0.7 * k if k < 1 else 1, A=A)
    pop(c, pill("تطبيق أقلام", 70), 540, 290, lt, 1.25)


def scene4(c, t, lt, A):  # choose subject -> best tutor
    step_label(c, 1, "اختر المادة", lt, 0.0)
    if lt > 1.55:
        step_label(c, 2, "أنسب مدرّس لك", lt, 1.55, y=250)
    slide = inout((lt - 1.45) / 0.35)
    a = screen_subjects(lt, 0.8)
    if slide > 0:
        b = screen_tutors(lt - 1.7, A, 1.55)
        # RTL slide: new screen enters from the left
        lay = Image.new("RGBA", (PW * 2, PH))
        lay.paste(b, (0, 0))
        lay.paste(a, (PW, 0))
        scr = lay.crop((int(PW * (1 - slide)), 0, int(PW * (1 - slide)) + PW, PH))
    else:
        scr = a
    draw_phone(c, scr, A=A)
    # tap on maths card: card centre in canvas coords
    sx = PX - PW / 2 + 30 + 230 + 105
    sy = PY - PH / 2 + 210 + 110
    tap(c, sx, sy, lt, 0.65)
    if lt > 3.4:
        pop(c, A["tag_best"], 540, 1700, lt, 3.4)


def scene5(c, t, lt, A):  # book in one tap
    step_label(c, 3, "احجز بضغطة", lt, 0.0)
    draw_phone(c, screen_booking(lt, A, 0.9, 1.65), A=A)
    sx, sy = PX - PW / 2 + 30 + 105, PY - PH / 2 + 510 + 110 + 45
    tap(c, sx, sy, lt, 0.8)
    tap(c, PX, PY - PH / 2 + 840, lt, 1.55)


def scene6(c, t, lt, A):  # online lesson from home
    step_label(c, 4, "الدرس أونلاين", lt, 0.0)
    k = back(lt / 0.45)
    draw_phone(c, screen_call(lt, A), 0.3 + 0.7 * k if k < 1 else 1, A=A)
    pop(c, A["home"], 860, 1600, lt, 2.6)
    pop(c, pill("من البيت", 60, bg=ACCENT, shade=ACCENT_D), 600, 1620, lt, 2.75)


def scene7(c, t, lt, A):  # exam day: Sarah excels
    k = back(lt / 0.45)
    put(c, A["paper"], 540, 980, 0.3 + 0.7 * k if k < 1 else 1, rot=-3 + (1 - cl(k)) * 8)
    if lt > 2.3:
        ks = out3((lt - 2.3) / 0.18)
        put(c, A["stamp"], 650, 1250, 2.2 - 1.2 * ks, rot=-14, alpha=0.4 + 0.6 * ks)
    pop(c, pill("يوم الاختبار", 64, fg=GREEN_D, bg=GREEN_L, shade=None), 540, 300, lt, 0.1)
    pop(c, pill("سارة تفوّقت!", 90), 540, 1640, lt, 2.4, 0.45, -6)
    if lt > 2.4:
        d = ImageDraw.Draw(c)
        for p in CONFETTI:
            tt = lt - 2.4
            x = p["x"] + p["vx"] * tt
            y = p["y"] + p["vy"] * tt + 300 * tt * tt
            if y > H + 40:
                continue
            rot = math.radians(p["r"] + p["vr"] * tt)
            s = p["s"]
            w = s * abs(math.cos(rot * 1.7)) + 4
            pts = [(-w / 2, -s / 3), (w / 2, -s / 3), (w / 2, s / 3), (-w / 2, s / 3)]
            d.polygon([(x + a * math.cos(rot) - b * math.sin(rot), y + a * math.sin(rot) + b * math.cos(rot))
                       for a, b in pts], fill=p["c"])


def scene8(c, t, lt, A):  # CTA
    k = back((lt - 0.05) / 0.5)
    put(c, text_img("أقلام", 250, GREEN), 540, 560, k)
    if lt > 0.5:
        u = out3((lt - 0.5) / 0.5)
        ImageDraw.Draw(c).line((540 - 220 * u, 730, 540 + 220 * u, 730), fill=ACCENT, width=14)
    pop(c, text_img("نوصلك بأفضل مدرس لك", 70, INK), 540, 850, lt, 1.3)
    if lt > 3.4:
        pulse = 1 + 0.05 * math.sin((lt - 3.8) * 2 * math.pi / 0.9) if lt > 3.8 else 1
        put(c, A["cta"], 540, 1120, back((lt - 3.4) / 0.4) * pulse)
    pop(c, text_img("واحجز درسك اليوم", 60, GREY), 540, 1290, lt, 4.4)
    if lt > 1.5:
        kk = back((lt - 1.5) / 0.4)
        put(c, A["M1"], 830, 1530 + 6 * math.sin(t * 3), 0.3 + 0.7 * kk if kk < 1 else 1)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]

random.seed(7)
CONFETTI = [dict(x=random.uniform(0, W), y=random.uniform(-400, -20), vx=random.uniform(-120, 120),
                 vy=random.uniform(250, 650), r=random.uniform(0, 360), vr=random.uniform(-400, 400),
                 c=random.choice([GREEN, ACCENT, (90, 180, 70), GREEN_D, RED]), s=random.uniform(14, 26))
            for _ in range(150)]


def build_assets():
    A = {"M1": load_sticker("M1", 280), "sarah": student_badge(), "avatar": avatar(150),
         "avatar_s": avatar(80), "person": person_icon(140)}
    A["phone"], A["phone_sh"] = phone_frame()
    vid = load_sticker("W3", 330)
    A["tutor_vid"] = vid.crop((0, 0, vid.width, vid.height - 24))
    # calendar
    cal, pad = card(380, 400, 36)
    d = ImageDraw.Draw(cal)
    d.rounded_rectangle((pad, pad, pad + 379, pad + 110), 36, fill=RED)
    d.rectangle((pad, pad + 70, pad + 379, pad + 110), fill=RED)
    for x in (pad + 110, pad + 270):
        d.rounded_rectangle((x - 10, pad - 20, x + 10, pad + 30), 8, fill=INK)
    t = text_img("باقي", 50, WHITE)
    cal.alpha_composite(t, (int(cal.width / 2 - t.width / 2), pad + 22))
    t = text_img("أيام", 54, INK)
    cal.alpha_composite(t, (int(cal.width / 2 - t.width / 2), pad + 320))
    A["cal"] = cal
    # notebook
    nb, pad = card(420, 520, 24)
    d = ImageDraw.Draw(nb)
    for y in range(pad + 80, pad + 500, 56):
        d.line((pad + 20, y, pad + 400, y), fill=(200, 215, 235), width=3)
    d.line((pad + 360, pad, pad + 360, pad + 519), fill=(240, 170, 160), width=4)
    fo = font(FM, 40)
    for i, s in enumerate(["٣س − ٥ = ؟", "س² + ...", "…؟"]):
        d.text((pad + 340, pad + 60 + i * 112), s, font=fo, fill=GREY, anchor="rs", direction="rtl", language="ar")
    d.line((pad + 80, pad + 300, pad + 300, pad + 330), fill=(160, 160, 160), width=6)
    d.line((pad + 90, pad + 330, pad + 280, pad + 300), fill=(160, 160, 160), width=6)
    A["notebook"] = nb
    # chat bubbles
    for i, (msg, mine, _) in enumerate(CHAT):
        t = text_img(msg, 46, WHITE if mine else INK, FM)
        b = Image.new("RGBA", (t.width + 70, t.height + 50), (0, 0, 0, 0))
        ImageDraw.Draw(b).rounded_rectangle((0, 0, b.width - 1, b.height - 1), 36,
                                            fill=GREEN if mine else (234, 237, 230))
        b.alpha_composite(t, (35, 25))
        A[f"chat{i}"] = b
    # schedule clash strip
    cl_, pad = card(880, 200, 30)
    d = ImageDraw.Draw(cl_)
    for i in range(5):
        x = pad + 440 + (2 - i) * 170
        d.rounded_rectangle((x - 70, pad + 30, x + 70, pad + 170), 22, fill=(246, 246, 243), outline=LINE, width=3)
        tt = text_img(num(4 + i) + " م", 34, GREY, FM)
        cl_.alpha_composite(tt, (int(x - tt.width / 2), pad + 50))
    A["clash"] = cl_
    A["tag_best"] = pill("ترشيح حسب مستواك", 56, bg=ACCENT, shade=ACCENT_D)
    # home icon
    hm = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(hm)
    d.ellipse((0, 0, 149, 149), fill=WHITE, outline=GREEN, width=8)
    d.polygon([(75, 32), (122, 72), (28, 72)], fill=GREEN)
    d.rectangle((42, 70, 108, 118), fill=GREEN)
    d.rectangle((66, 88, 84, 118), fill=WHITE)
    A["home"] = hm
    # exam paper
    pp, pad = card(640, 860, 20)
    d = ImageDraw.Draw(pp)
    t = text_img("اختبار الرياضيات", 54, INK)
    pp.alpha_composite(t, (pad + 600 - t.width, pad + 40))
    t = text_img("الاسم: سارة", 40, GREY, FM)
    pp.alpha_composite(t, (pad + 600 - t.width, pad + 130))
    d.line((pad + 40, pad + 210, pad + 600, pad + 210), fill=LINE, width=4)
    for i in range(5):
        y = pad + 260 + i * 110
        d.line((pad + 150, y + 30, pad + 600, y + 30), fill=(215, 222, 212), width=4)
        check(d, pad + 80, y + 20, 50, GREEN, 9)
    A["paper"] = pp
    st = Image.new("RGBA", (420, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle((6, 6, 413, 193), 30, outline=GREEN, width=12)
    t = text_img("ممتاز", 110, GREEN)
    st.alpha_composite(t, (210 - t.width // 2, 100 - t.height // 2))
    A["stamp"] = st
    A["cta"] = pill("حمّل التطبيق", 92, bg=INK, shade=(0, 0, 0))
    A["brand"] = pill("أقلام", 44)
    return A


def frame(t, A, bg):
    c = bg.copy()
    i = max(j for j in range(len(SCENES)) if SC[j] <= t)
    lt, dur = t - SC[i], SC[i + 1] - SC[i]
    last = i == len(SCENES) - 1
    # phone scenes (3,4,5) flow into each other without the exit fade
    keep = i in (2, 3, 4)
    out_k = 0 if (last or keep) else cl((lt - (dur - 0.22)) / 0.22)
    if out_k > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        SCENES[i](layer, t, lt, A)
        put(c, layer, W / 2, H / 2 - 60 * out_k, 1 - 0.08 * out_k, alpha=1 - out_k)
    else:
        SCENES[i](c, t, lt, A)
    if i != len(SCENES) - 1:
        put(c, A["brand"], 540, 120)
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
        ts = [float(x) for x in sys.argv[2:]] or [6.5, 11.5, 14.9, 16.6, 19.8, 23.5, 28.5, 32.8, 39.0]
        for t in ts:
            frame(t, A, bg).save(os.path.join(OUT, f"preview_{t:05.2f}.jpg"), quality=88)
        return
    audio = os.path.join(OUT, "_audio.m4a")
    mix_audio(audio)
    video = os.path.join(OUT, "story_reel.mp4")
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
