"""Effort levels: effort-low, -medium, -high, -xhigh, -max. A dial shows the level, Clawd shows how hard he works.

python effort_sets.py  ->  ../mine/effort-*/
Seam = needle resting on the level, Clawd calm for that level. Loop 1 works steadily, loop 2 bursts one level higher and settles.
"""
import math

from props import *

CX, CY, RO, RI = 44, 54, 34, 27                    # dial centre (relative to the panel) and ring radii
ZONES = [GREEN, (160, 206, 80), YELLOW, ORANGE, RED]
NAMES = ["low", "medium", "high", "xhigh", "max"]
LID = [0.45, 0.1, 0.0, 0.0, 0.0]                  # how open Clawd's eyes are at rest
GREY_ARC = (46, 50, 62)


def dial(draw, x0, level, needle, shake=0):
    """Half circle split into five zones, the zone of the current level lit. Needle at `needle` (0..4 as a float)."""
    for deg in range(0, 181, 1):
        zone = min(4, deg // 36)
        a = math.radians(180 - deg)
        for r in range(RI, RO + 1, 1):
            if deg % 36 in (0, 35) and r < RO - 1:                           # thin gaps between zones
                continue
            c = ZONES[zone] if zone == level else mix(ZONES[zone], (20, 24, 34), 0.72)
            R(draw, round(x0 + CX + math.cos(a) * r) + shake, round(CY - math.sin(a) * r), 1, 1, c)
    ang = math.radians(180 - (18 + 36 * needle))
    for r in range(0, RI - 3):
        R(draw, round(x0 + CX + math.cos(ang) * r) + shake, round(CY - math.sin(ang) * r), 2, 2, WHITE)
    dot(draw, x0 + CX + shake, CY, 3, (200, 204, 215))


def flames(draw, x0, f):
    for k in range(4):
        h = 4 + (f * 2 + k * 3) % 6
        x = x0 + CX - 12 + k * 8
        R(draw, x, CY - RI - h - 1, 3, h, ORANGE)
        R(draw, x + 1, CY - RI - h + 1, 1, max(1, h - 2), YELLOW)


def steam(draw, f, strong):
    for k in range(3 if strong else 2):
        t = ((f + k * 3) % 9) / 9
        x = OX + 10 + k * 14 + (k % 2) * 3
        y = 7 - round(t * 7)
        if t < 0.85:
            R(draw, x, y, 3, 2, (225, 228, 238))
            R(draw, x + 1, y - 1, 1, 1, (225, 228, 238))


def effort_frame(level, needle=None, f=0, shake=0, sweat_on=False, steam_on=False, flame=False, key=False, spark=False,
                 look=(2, 1), blink=False, bob=0, slide=0, lid=None, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    dial(draw, x0, level, level if needle is None else needle, shake)
    if flame:
        flames(draw, x0, f)
    if spark:
        for k, (sx, sy) in enumerate(((10, 14), (78, 18), (60, 10), (22, 30))):
            if (f + k * 2) % 5 < 2:
                R(draw, x0 + sx, sy, 1, 3, YELLOW)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob, lid=LID[level] if lid is None else lid, dx=shake)
    if smile:
        draw_smile(draw, OX + 4 * G + shake, OY + 2 * G + 1 + bob)
    if steam_on:
        steam(draw, f, level >= 4)
    if sweat_on:
        sweat(draw, bob, f)
    if key:
        key_press(draw, bob)
    return img


def make_level(level):
    """Loops for one effort level: (steady work, burst)."""
    def fr(**kw):
        return effort_frame(level, **kw)

    busy = level >= 1
    fast = level >= 2

    def steady():
        frames = [fr()] * 4 + [fr(blink=True)] + [fr()] * 2
        n = 26
        for i in range(n):
            wob = math.sin(i * (0.5 + 0.2 * level)) * (0.1 + 0.07 * level)
            key = busy and (i % 2 == 0 if level < 3 else True)
            frames.append(fr(needle=level + wob, f=i, key=key, bob=1 if key and i % 2 == 0 else (1 if level == 0 and i % 8 < 3 else 0),
                             sweat_on=level >= 2 and (i % 12 < 8 if level == 2 else True), steam_on=level >= 3,
                             flame=level == 4, shake=(-1, 1)[i % 2] if level == 4 else 0, spark=level == 4,
                             look=(2, 1 + (i % 10 > 6)), smile=level == 0, blink=i == 12 and level < 3))
        return frames + [fr(blink=True), fr()]

    def burst():
        frames = [fr()] * 3 + [fr(blink=True)] + [fr()] * 2
        top = min(4, level + 1)
        for i in range(5):                                                   # the needle swings up
            t = ease((i + 1) / 5)
            frames.append(fr(needle=lerp(level, top, t) + (0.08 if level == 4 else 0), f=i, look=(2, 0), lid=0.0,
                             bob=-1 if i == 4 else 0, shake=(-1, 1)[i % 2] if level == 4 else 0, spark=level == 4))
        for i in range(14):                                                  # works flat out
            n_level = top if level < 4 else 4
            frames.append(fr(needle=n_level + 0.15 * math.sin(i * 1.4), f=i, key=True, bob=i % 2, lid=0.0,
                             sweat_on=True, steam_on=level >= 2, flame=top >= 4, shake=(-1, 1)[i % 2] if top >= 4 else 0,
                             spark=top >= 4, look=(2, 1 + (i % 6 > 3))))
        for i in range(5):                                                   # and settles back
            t = ease((i + 1) / 5)
            frames.append(fr(needle=lerp(top, level, t), f=i, look=(2, 1), sweat_on=i < 3, steam_on=level >= 3 and i < 3,
                             flame=level == 4 and i < 3, shake=(-1, 1)[i % 2] if level == 4 and i < 3 else 0))
        return frames + [fr(blink=True), fr()]

    return steady, burst


if __name__ == "__main__":
    for lv, name in enumerate(NAMES):
        steady, burst = make_level(lv)
        finish(f"effort-{name}", lambda lv=lv, **k: effort_frame(lv, **k), [steady, burst])
