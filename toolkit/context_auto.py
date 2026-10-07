"""auto-compact: the context fills up to the 90% line, a bell warns, then it compacts by itself.

python context_auto.py  ->  ../mine/auto-compact/
Seam = a lightly filled gauge (2 segments) with the 90% marker; a loop climbs to the marker and compacts back to the seam level.
"""
import math

from props import *
from limit_sets import draw_gauge, draw_bars, bars_for, warn_tri, LINES

SEAM_LEVEL = 0.2
THRESH = 0.9


def bell(draw, x, y, rattle):
    c = YELLOW if rattle else (120, 126, 146)
    sx = x + (-1, 1)[rattle % 2] if rattle else x
    R(draw, sx + 4, y, 2, 1, c)                                              # knob
    R(draw, sx + 3, y + 1, 4, 1, c)
    R(draw, sx + 2, y + 2, 6, 1, c)
    R(draw, sx + 1, y + 3, 8, 2, c)                                          # a rounder body
    R(draw, sx, y + 5, 10, 1, c)                                             # the lip
    R(draw, sx + 4, y + 6, 2, 1, c)                                          # clapper
    if rattle:                                                               # sound arcs
        for dx in (-5, 11):
            R(draw, sx + dx, y + 1, 1, 4, YELLOW)


def auto_frame(level=SEAM_LEVEL, colored=None, summary=0, doc=0, ring=None, rattle=0, warn=0, tickmark=False, chip=None, glow=None,
               sweat_f=None, key=False, look=(2, 1), blink=False, bob=0, slide=0, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    h = round(44 * level)
    color = GREEN if level < 0.5 else AMBER if level < 0.8 else RED
    draw_gauge(draw, x0, h, color)
    for i in range(0, 16, 4):                                                # the 90% marker across the gauge
        R(draw, x0 + 7 + i, 54 - round(44 * THRESH), 3, 1, WHITE)
    R(draw, x0 + 25, 54 - round(44 * THRESH) - 1, 3, 3, WHITE)
    draw_bars(draw, x0, bars_for(h) if colored is None else colored, shimmer=glow)
    if summary:
        R(draw, x0 + 38, 47, summary, 5, AMBER)
        R(draw, x0 + 38, 51, summary, 1, (190, 130, 40))
    if doc:                                                                  # the summary page is written line by line
        R(draw, x0 + 60, 24, 20, 26, (232, 234, 240))
        for i in range(min(doc, 4)):
            R(draw, x0 + 63, 28 + i * 5, 14, 2, AMBER)
    bell(draw, x0 + 54, 7, rattle)
    if ring is not None:                                                     # the "auto" ring turns while it compacts
        for k in range(14):
            a = k * 2 * math.pi / 14
            lit = (k - ring) % 14
            c = mix((60, 66, 82), AMBER, max(0, 1 - lit / 6)) if lit < 6 else (60, 66, 82)
            R(draw, round(x0 + 76 + math.cos(a) * 4), round(10 + math.sin(a) * 4), 1, 1, c)
    if warn:
        warn_tri(draw, x0 + 70, 7, RED if warn == 2 else AMBER)
    if chip:
        R(draw, x0 + chip[0], chip[1], 4, 3, LIGHT_BLUE)
    if tickmark:
        tick(draw, x0 + 62, 20, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def compact_phase(f, start, doc=False):
    """The bars fold into one summary block, the gauge falls back to the seam level, nobody pressed anything."""
    frames = []
    n = 12
    for k in range(n):
        t = ease((k + 1) / n)
        lvl = lerp(start, SEAM_LEVEL, t)
        left = max(0, round(10 * (1 - t)))
        frames.append(f(lvl, colored=left, summary=round(14 * t), doc=min(4, 1 + k // 3) if doc else 0, ring=k, look=(2, 1),
                        sweat_f=k if k < 6 else None, bob=1 if k % 4 == 0 else 0))
    return frames


def auto_climb():
    f = auto_frame
    frames = intro(f)
    for i in range(20):                                                      # work piles up towards the marker
        lvl = lerp(SEAM_LEVEL, THRESH, ease((i + 1) / 20))
        frames.append(f(lvl, key=i % 2 == 0, bob=i % 2, glow=i, sweat_f=i if lvl > 0.7 else None,
                        warn=(1 + (i // 2) % 2) if lvl > 0.84 else 0, look=(2, 1 if lvl < 0.6 else 0)))
    for k in range(10):                                                      # the bell rings
        frames.append(f(THRESH, rattle=k + 1, warn=1 + k % 2, sweat_f=k, look=(2, 0), bob=-1 if k % 5 == 1 else 0))
    frames += compact_phase(f, THRESH)
    frames += [f(SEAM_LEVEL, summary=14, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(6)]
    for k in range(3):
        frames.append(f(SEAM_LEVEL, summary=round(14 * (1 - (k + 1) / 3))))
    return frames + [f(blink=True), f()]


def auto_chips():
    f = auto_frame
    frames = intro(f)
    levels = [SEAM_LEVEL + (THRESH - SEAM_LEVEL) * i / 7 for i in range(8)]
    for i in range(7):                                                       # tokens fly in one by one and raise the level
        for k in range(4):
            t = (k + 1) / 4
            y = 54 - round(44 * levels[i]) - 3
            frames.append(f(levels[i], chip=(round(lerp(86, 26, t)), y), look=(2, 1 if i < 4 else 0), key=k == 0, bob=1 if k == 0 else 0,
                            sweat_f=k if levels[i] > 0.7 else None, warn=(1 + k % 2) if levels[i] > 0.8 else 0))
        frames.append(f(levels[i + 1], look=(2, 1)))
    for k in range(6):
        frames.append(f(THRESH, rattle=k + 1, warn=1 + k % 2, sweat_f=k, look=(2, 0)))
    frames += compact_phase(f, THRESH, doc=True)                              # compaction writes a summary page
    frames += [f(SEAM_LEVEL, doc=4, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(7)]
    for k in range(3):
        frames.append(f(SEAM_LEVEL, doc=max(0, 3 - 2 * k)))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("auto-compact", auto_frame, [auto_climb, auto_chips])
