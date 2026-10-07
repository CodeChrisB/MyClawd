"""legal: a legal page that is stamped FREE, and the no-data, no-money, just-for-fun badges (the GIF on the site's Legal tab).

python legal_sets.py  ->  ../mine/legal/
Seam = a plain legal page on the panel. Loop 1 stamps FREE on it and swaps in a fresh page; loop 2 shows three badges.
"""
import math

from props import *

DOCX, DOCY, DOCW, DOCH = 8, 10, 38, 42
HEART = ("0110110", "1111111", "1111111", "0111110", "0011100", "0001000")


def heart(draw, x, y, s, color):
    for r, row in enumerate(HEART):
        for c, v in enumerate(row):
            if v == "1":
                R(draw, x + c * s, y + r * s, s, s, color)


def legal_frame(page_dx=0, stamp=None, free=0, thud=0, badges=0, shown=(), spark=None, tickmark=False, look=(2, 1), blink=False,
                bob=0, slide=0, smile=False):
    """stamp = (x, y) of the rubber stamp's base (panel coordinates) or None. free: 0..1 how much of the FREE mark is visible.
    badges: how many of the three badges have popped in (0..3)."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        px, py = x0 + DOCX + page_dx, DOCY + thud
        R(d, px, py, DOCW, DOCH, (238, 238, 244))
        R(d, px, py, DOCW, DOCH, (238, 238, 244))
        R(d, px + 4, py + 4, 22, 3, (90, 96, 118))                           # the title
        for i, w in enumerate((30, 26, 30, 22, 28)):                         # legal text
            R(d, px + 4, py + 11 + i * 4, w, 1, (150, 154, 170))
        R(d, px + 4, py + 37, 16, 1, (90, 96, 118))                          # signature line
        R(d, px + 6, py + 34, 3, 2, (90, 96, 118))
        R(d, px + 9, py + 35, 4, 1, (90, 96, 118))
        if free:                                                             # the stamp prints FREE in one thud
            text(d, px + 3, py + 22, "FREE", (40, 170, 90), 2)
        if stamp:
            sx, sy = x0 + stamp[0], stamp[1]
            R(d, sx + 4, sy - 14, 6, 6, (180, 60, 60))                       # the knob
            R(d, sx + 6, sy - 9, 2, 5, (150, 80, 60))
            R(d, sx, sy - 5, 14, 5, (210, 80, 80))
            R(d, sx + 1, sy, 12, 1, (110, 40, 40))
        if badges:
            for i in range(badges):
                cx, cy = x0 + 66, 18 + i * 16
                r = 7 if i < badges - 1 or not spark else 8
                dot(d, cx, cy, r, (36, 40, 52))
                dot(d, cx, cy, r - 1, (24, 28, 40))
                if i == 0:                                                   # no data: a cloud with a slash
                    R(d, cx - 4, cy - 1, 8, 3, (190, 194, 208))
                    R(d, cx - 2, cy - 3, 4, 3, (190, 194, 208))
                elif i == 1:                                                 # no money: a coin with a slash
                    dot(d, cx, cy, 4, YELLOW)
                    dot(d, cx, cy, 2, (200, 140, 30))
                else:                                                        # just for fun: a heart
                    heart(d, cx - 3, cy - 3, 1, (240, 90, 120)) if False else heart(d, cx - 7, cy - 6, 2, (240, 90, 120))
                if i < 2:
                    for k in range(-5, 6):
                        R(d, cx + k, cy + k, 2, 2, RED)
                else:
                    tick(d, cx + 4, cy + 3, GREEN, 1)
        if tickmark:
            tick(d, x0 + 54, 8, GREEN, 2)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    if spark is not None:
        for k, (sx, sy) in enumerate(((50, 14), (80, 40), (14, 8))):
            if (spark + k * 2) % 6 < 3:
                R(draw, x0 + sx, sy, 1, 3, YELLOW)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def legal_stamp():
    f = legal_frame
    frames = intro(f)
    for k in range(4):                                                       # the stamp comes down onto the page
        frames.append(f(stamp=(16, round(lerp(8, 40, ease((k + 1) / 4)))), look=(2, 0 if k < 3 else 1), bob=1 if k == 3 else 0))
    frames += [f(stamp=(16, 40), thud=1, free=1.0, look=(2, 1), bob=1)]      # thud: FREE is printed
    for k in range(3):
        frames.append(f(stamp=(16, round(lerp(40, 8, ease((k + 1) / 3)))), free=1.0, look=(2, 1)))
    frames += [f(free=1.0, spark=k, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in range(5):                                                       # a fresh page slides in
        t = ease((k + 1) / 5)
        frames.append(f(page_dx=-round(t * 52), free=1.0 if t < 0.6 else 0, look=(2, 1)))
    return frames + [f(blink=True), f()]


def legal_badges():
    f = legal_frame
    frames = intro(f)
    for n in range(1, 4):                                                    # no data, no money, just for fun
        for k in range(3):
            frames.append(f(badges=n, spark=k if n == 3 else None, look=(2, 0 if n < 3 else 1), bob=1 if k == 0 else 0, smile=n == 3))
        frames += [f(badges=n, look=(2, 1), blink=k == 1 and n == 2) for k in range(3)]
    frames += [f(badges=3, spark=k, smile=True, tickmark=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for n in (2, 1, 0):
        frames.append(f(badges=n, look=(2, 1)))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("legal", legal_frame, [legal_stamp, legal_badges])
