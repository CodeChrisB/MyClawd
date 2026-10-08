"""Weather: sunny, partly-cloudy, cloudy, rain, snow, thunder, hurricane. Two loops each.

python weather_sets.py  ->  ../mine/{sunny,partly-cloudy,cloudy,rain,snow,thunder,hurricane}/
No panel: the weather fills the right of the canvas (rain, snow and wind everywhere) and Clawd reacts at the left.
Seam pose = the weather at rest (loop time t = 0) with Clawd's accessory on. Enter brings the weather in (presence k 0 to 1),
exit takes it away again. Loops are N frames of t, then the seam frame again. Everything periodic (rays, drops, flakes, streaks)
travels a whole number of periods in N frames, so the loops join without a jump.
"""
import math
import random

from props import *
from font3 import say
from seamless import save_flow

SUN_Y = (255, 214, 70)
CLOUD_W, CLOUD_S = (240, 242, 250), (186, 194, 214)
CLOUD_G, CLOUD_GS = (150, 156, 174), (110, 116, 136)
CLOUD_D, CLOUD_DS = (96, 100, 120), (66, 70, 88)
RAIN_C, SNOW_C = (150, 190, 240), (245, 248, 255)


def cloud(draw, x, y, w=36, col=CLOUD_W, shade=CLOUD_S):
    h = max(6, w // 3)
    draw.ellipse([x, y + h // 3, x + w, y + h + h // 3], fill=col)
    draw.ellipse([x + w // 6, y, x + w // 6 + w // 2, y + h], fill=col)
    draw.ellipse([x + w // 2, y + h // 4, x + w - 2, y + h + 2], fill=col)
    R(draw, x + 3, y + h + h // 3 - 2, w - 6, 2, shade)


def sun(draw, cx, cy, r, t, n, dim=0.0, rays=True):
    col = mix(SUN_Y, (190, 190, 200), dim)
    if rays:
        for j in range(12):
            a = 2 * math.pi * (j / 12 + t / (12 * n))
            for rr in range(r + 3, r + 9, 2):
                R(draw, cx + round(math.cos(a) * rr) - 1, cy + round(math.sin(a) * rr) - 1, 2, 2, col)
    dot(draw, cx, cy, r, col)
    dot(draw, cx - 2, cy - 2, max(2, r - 5), mix(col, WHITE, .4))


def shades(draw, bob=0, glint=None):
    """Sunglasses whose lenses are joined by a bridge and whose temples run to the sides of the head."""
    oy = OY + G + bob
    left, right = OX + G - 2, OX + 6 * G - 2                  # lens x, 10 px wide each
    ink = (14, 14, 20)
    R(draw, left, oy - 1, 10, 7, ink)
    R(draw, right, oy - 1, 10, 7, ink)
    R(draw, left + 10, oy, right - left - 10, 2, ink)           # bridge, touches both lenses
    R(draw, OX, oy, left - OX, 2, ink)                          # temples
    R(draw, right + 10, oy, OX + 8 * G - right - 10, 2, ink)
    R(draw, left + 1, oy, 3, 1, (70, 74, 96))
    R(draw, right + 1, oy, 3, 1, (70, 74, 96))
    if glint is not None:
        R(draw, left + 1 + glint % 6, oy + 2, 2, 1, WHITE)


def scarf(draw, bob=0):
    R(draw, OX + 2, OY + 4 * G - 2 + bob, 8 * G - 4, 5, (200, 50, 60))
    R(draw, OX + 2, OY + 4 * G - 2 + bob, 8 * G - 4, 1, (230, 90, 96))
    R(draw, OX + 8 * G - 14, OY + 4 * G + 2 + bob, 6, 11, (200, 50, 60))
    R(draw, OX + 8 * G - 14, OY + 4 * G + 6 + bob, 6, 1, (230, 190, 190))


def umbrella(draw, open_=1.0, tilt=0):
    w = round(46 * open_)
    if w < 8:
        return
    cx = 50 + tilt
    draw.pieslice([cx - w // 2, -2, cx + w // 2, 18], 180, 360, fill=(214, 52, 60))
    for k in (-1, 0, 1):
        R(draw, cx + k * w // 4, 1, 1, 7, (160, 30, 40))
    R(draw, 72 + tilt // 2, 8, 1, round(24 * open_), (190, 196, 210))


def drops(draw, t, n, count=30, speed=8, slant=0.25, skip=None, color=RAIN_C):
    for i in range(count):
        x0, y0 = (i * 37) % 192, (i * 23) % 64
        y = (y0 + speed * t) % 64
        x = round((x0 + slant * y) % 192)
        if skip and skip(x, y):
            continue
        R(draw, x, y, 1, 3, color)


def flakes(draw, t, n, count=34, color=SNOW_C):
    for i in range(count):
        x0, y0, s = (i * 41) % 192, (i * 17) % 64, 2 if i % 3 else 4
        y = (y0 + s * t * (64 // (s * n) if False else 1)) % 64
        x = x0 + round(3 * math.sin(2 * math.pi * (t / n) * (1 + i % 2) + i))
        sz = 2 if s == 4 else 1
        R(draw, x, y, sz, sz, color if sz == 2 else mix(color, LIGHT_BLUE, .4))


def smile(draw, bob=0):
    draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)


def arm(draw, level, bob=0):
    ox, oy = OX, OY + bob
    if not level:
        return
    draw.rectangle([ox + 8 * G, oy + 2 * G, ox + 10 * G - 1, oy + 4 * G - 1], fill=TRANS)
    if level == 1:
        draw.rectangle([ox + 8 * G, oy + G + 3, ox + 9 * G + 2, oy + 3 * G - 1], fill=CORAL)
        draw.rectangle([ox + 9 * G - 1, oy + 4, ox + 10 * G - 2, oy + 2 * G - 1], fill=CORAL)
    else:
        draw.rectangle([ox + 8 * G, oy - 3, ox + 9 * G - 1, oy + 3 * G - 1], fill=CORAL)


def blend(look, k):
    return (round(look[0] * k), round(look[1] * k))


def make(frame, n):
    """enter (from the base pose: Clawd alone), leave (back to it) and a loop builder for a frame(t, k, ...) function.
    The enter runs on the loop's own time ending right before t = 0, the leave starts on t = 0, loops are exactly n frames."""
    def enter():
        return [frame((i - 6) % n, ease(i / 5)) for i in range(6)]

    def leave():
        return [frame(i, 1 - ease(i / 5)) for i in range(6)]

    def loop(fn):
        return lambda: [frame(0, 1.0)] + [fn(t) for t in range(1, n)]
    return enter, leave, loop


# ---------------------------------------------------------------- sunny

N_SUN = 36


def sunny_frame(t=0, k=1.0, look=(2, -1), bob=0, blink=False, lid=0.15, wave=0, glint=None, sweat_=False, size=0):
    img, draw = new_frame()
    sun(draw, 148, 26 + round((1 - k) * 70), 11 + size, t, N_SUN, rays=k > .3)
    clawd(draw, look=blend(look, k), blink=blink, lid=lid * k, bob=bob)
    arm(draw, wave, bob)
    if k > .6:
        shades(draw, bob, glint)
        smile(draw, bob)
    if sweat_:
        sweat(draw, bob, t)
    return img


def sunny_a(t):
    g = (t // 2) % 14 if 6 <= t < 20 else None
    return sunny_frame(t, glint=g, bob=-1 if t % 18 in (0, 1) else 0, blink=t == 30)


def sunny_b(t):
    return sunny_frame(t, wave=2 if (t // 3) % 2 and 6 <= t < 30 else 1 if 6 <= t < 30 else 0, size=1 if 10 <= t < 22 else 0,
                       glint=(t // 3) % 12 if t < 18 else None)


# ---------------------------------------------------------------- partly cloudy

N_PC = 48


def pc_frame(t=0, k=1.0, look=(2, -1), bob=0, blink=False):
    img, draw = new_frame()
    cx, cy = 148, 24
    c1 = (190 - (t * 4) % 192) if False else 200 - (t * 5) % 240 + 40          # drifts left, wraps after 240 px
    c2 = 230 - (t * 3 + 90) % 240 + 20
    covered = 0.0
    for cxx, w in ((c1, 40), (c2, 30)):
        if abs(cxx + w / 2 - cx) < 14:
            covered = max(covered, 1 - abs(cxx + w / 2 - cx) / 14)
    sun(draw, cx, cy + round((1 - k) * 80), 9, t, N_PC, dim=covered * .6, rays=covered < .5 and k > .3)
    cloud(draw, round(c1 + (1 - k) * 260), 12, 40)
    cloud(draw, round(c2 + (1 - k) * 260), 30, 30, CLOUD_W, CLOUD_S)
    clawd(draw, look=blend(look, k), blink=blink, lid=(0.35 - .3 * covered if covered < .5 else 0.0) * k, bob=bob)
    if covered > .6:
        smile(draw, bob)
    return img


def pc_a(t):
    return pc_frame(t, blink=t == 40)


def pc_b(t):
    return pc_frame(t, look=(2, -2) if 14 < t < 34 else (2, 0), bob=-1 if t in (20, 21) else 0, blink=t == 8)


# ---------------------------------------------------------------- cloudy

N_CL = 40


def cl_frame(t=0, k=1.0, look=(2, -2), yawn=0, bob=0, blink=False, sweat_=False):
    img, draw = new_frame()
    off = round((1 - k) * 110)
    sway = round(4 * math.sin(2 * math.pi * t / N_CL))
    cloud(draw, 96 + sway + off, 4, 46, CLOUD_G, CLOUD_GS)
    cloud(draw, 138 - sway + off, 10, 52, CLOUD_G, CLOUD_GS)
    cloud(draw, 112 + round(2 * math.sin(2 * math.pi * t / N_CL + 1)) + off, 22, 44, CLOUD_D, CLOUD_DS)
    cloud(draw, 150 + sway + off, 26, 36, CLOUD_G, CLOUD_GS)
    clawd(draw, look=blend(look, k), blink=blink, lid=0.25 * k, bob=bob)
    mx, my = OX + 4 * G, OY + 2 * G + 2 + bob
    if yawn:
        draw.rectangle([mx - 4, my - 1, mx + 3, my + 4], fill=BLACK)
    elif k > .6:
        R(draw, mx - 3, my + 1, 6, 2, BLACK)                  # the flat "meh" mouth
    return img


def cl_a(t):
    return cl_frame(t, look=(2, -2) if t < 30 else (2, 0), blink=t == 34)


def cl_b(t):
    y = 1 if 12 <= t < 24 else 0
    return cl_frame(t, yawn=y, look=(2, -1), bob=-1 if y and t in (14, 15) else 0, blink=t == 28)


# ---------------------------------------------------------------- rain

N_RAIN = 32


def rain_frame(t=0, k=1.0, look=(2, -1), bob=0, blink=False, lift=0, splash=False, tilt=0):
    img, draw = new_frame()
    off = round((1 - k) * 130)
    cloud(draw, 110 + off, 2, 50, CLOUD_G, CLOUD_GS)
    cloud(draw, 150 + off, 6, 40, CLOUD_D, CLOUD_DS)
    cloud(draw, 84 + off, 8, 32, CLOUD_D, CLOUD_DS)
    if k > .25:
        under = lambda x, y: k > .6 and 28 < x < 74 and y < 10
        drops(draw, t, N_RAIN, count=round(34 * min(1.0, k * 1.5)), speed=8, skip=under)
    if splash:
        for gx in (96, 126, 156):                               # puddle ripples
            r = 1 + (t // 2 + gx) % 4
            R(draw, gx - r * 2, 57, r * 4, 1, RAIN_C)
    clawd(draw, look=blend(look, k), blink=blink, bob=bob - lift)
    if k > .6:
        umbrella(draw, min(1.0, (k - .6) / .3), tilt)
    return img


def rain_a(t):
    return rain_frame(t, blink=t == 20, look=(2, -2) if 8 < t < 22 else (2, 0))


def rain_b(t):
    hop = -2 if t % 16 in (6, 7) else -1 if t % 16 in (5, 8) else 0
    return rain_frame(t, splash=True, lift=-hop if False else 0, bob=hop, look=(2, 2), tilt=0)


# ---------------------------------------------------------------- snow

N_SNOW = 32


def snow_frame(t=0, k=1.0, look=(2, 0), shiver=0, bob=0, blink=False, man=0, poof=0):
    img, draw = new_frame()
    off = round((1 - k) * 110)
    cloud(draw, 100 + off, 0, 50, (214, 220, 232), (170, 178, 198))
    cloud(draw, 148 + off, 2, 40, (214, 220, 232), (170, 178, 198))
    flakes(draw, t, N_SNOW, count=round(36 * min(1.0, k * 1.4)))
    if k > .3:
        R(draw, 192 - round(108 * min(1.0, (k - .3) / .5)), 56, round(108 * min(1.0, (k - .3) / .5)), 2, (240, 244, 250))   # snow on the ground
    if man >= 1:
        dot(draw, 138, 50, 6, SNOW_C)
    if man >= 2:
        dot(draw, 138, 40, 5, SNOW_C)
    if man >= 3:
        dot(draw, 138, 32, 4, SNOW_C)
        R(draw, 136, 31, 1, 1, BLACK)
        R(draw, 140, 31, 1, 1, BLACK)
        R(draw, 138, 33, 5, 1, (240, 130, 40))
    if man >= 4:
        R(draw, 134, 24, 9, 5, (30, 30, 36))
        R(draw, 131, 28, 15, 1, (30, 30, 36))
    if poof:
        puff(draw, 138, 40, 4 + poof * 3)
    clawd(draw, look=blend(look, k), blink=blink, lid=0.25 * k, bob=bob, dx=shiver)
    if k > .6:
        scarf(draw, bob)
    return img


def puff(draw, cx, cy, r):
    for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)):
        R(draw, cx + round(ax * r), cy + round(ay * r), 2, 2, WHITE)


def snow_a(t):
    sh = 1 if 6 < t < 26 and t % 2 else 0
    return snow_frame(t, shiver=sh, look=(2, -1) if 10 < t < 22 else (2, 0), blink=t == 28)


SNOWMAN = [(2, 1), (4, 2), (6, 3), (8, 4)]


def snow_b(t):
    man = 0
    for a, m in SNOWMAN:
        if t >= a:
            man = m
    poof = 0
    if t >= 24:
        man, poof = (man if t < 26 else 0), max(0, 1 + (t - 26) // 2) if t >= 26 else 1
        if poof > 4:
            poof = 0
    return snow_frame(t, man=man, poof=poof, look=(2, 0 if t < 14 else 1), shiver=1 if 12 < t < 24 and t % 2 else 0)


# ---------------------------------------------------------------- thunder

N_TH = 40
FLASH = {8: 1.0, 9: .5, 26: 1.0, 27: .6, 29: .8}
BOOM = range(13, 20)


def bolt(draw, x, top=12):
    pts = [(x + 2, top), (x - 5, top + 14), (x + 4, top + 16), (x - 4, top + 34), (x + 5, top + 38)]
    draw.line(pts, fill=(255, 220, 90), width=3)
    draw.line(pts, fill=WHITE, width=1)


def th_frame(t=0, k=1.0, look=(2, -1), bob=0, blink=False, flash=0.0, boom=False, sweat_=False, hop=0):
    img, draw = new_frame()
    off = round((1 - k) * 110)
    if flash:
        R(draw, 84, 0, 108, 64, mix((70, 80, 120), (225, 232, 255), flash))
    cloud(draw, 98 + off, 0, 54, CLOUD_D, CLOUD_DS)
    cloud(draw, 146 + off, 2, 44, CLOUD_D, CLOUD_DS)
    if k > .25:
        drops(draw, t, N_TH, count=round(18 * min(1.0, k * 1.5)), speed=8, slant=0.2)
    if flash:
        bolt(draw, 148)
    if boom:
        say(draw, 100, 40, "BOOM", YELLOW, 3)
    clawd(draw, look=blend(look, k), blink=blink, bob=bob - hop, lid=0.0)
    if sweat_:
        sweat(draw, bob, t)
    return img


def th_a(t):
    fl = FLASH.get(t, 0.0)
    return th_frame(t, flash=fl if t < 20 else 0.0, boom=t in BOOM, hop=3 if t in (10, 11) else 1 if t in (9, 12) else 0,
                    look=(0, 0) if 8 <= t < 16 else (2, -1), sweat_=14 < t < 30, blink=t == 34)


def th_b(t):
    fl = FLASH.get(t, 0.0)
    return th_frame(t, flash=fl if t >= 24 or t == 8 or t == 9 else 0.0, boom=t in range(30, 37), hop=3 if t in (28, 29) else 1 if t in (27, 30) else 0,
                    look=(2, 0) if t < 26 else (0, 0), sweat_=30 < t, blink=t == 4)


# ---------------------------------------------------------------- hurricane

N_HU = 32


def hurricane_frame(t=0, k=1.0, look=(2, 0), bob=0, blink=False, lean=0, arm_up=0):
    img, draw = new_frame()
    cx, cy = 150, 32 + round((1 - k) * 70)
    rot = t / N_HU * 2 * math.pi / 3                                   # 3 arms: a third of a turn per loop joins up
    if k > .15:
        for arm_i in range(3):
            for s in range(44):
                r = 4 + s * 0.62 * max(0.3, k)
                a = arm_i * 2 * math.pi / 3 + s * 0.17 + rot
                px, py = cx + round(math.cos(a) * r * 1.5), cy + round(math.sin(a) * r * .95)
                sz = 6 - s // 9
                R(draw, px - sz // 2, py - sz // 2, sz, sz, mix(CLOUD_W, CLOUD_DS, s / 44))
        dot(draw, cx, cy, 4, (24, 26, 40))
    if k > .3:
        for i in range(10):                                            # wind streaks, 6 px a frame over 192 px
            x = (i * 53 + 6 * t) % 192
            y = 4 + (i * 29) % 52
            R(draw, x, y, 10, 1, (200, 208, 224))
        for i in range(5):                                             # debris: leaves and a plank
            x = (i * 71 + 6 * t) % 192
            y = 10 + (i * 37) % 40 + round(5 * math.sin(2 * math.pi * (t / N_HU) * 2 + i))
            if i % 2:
                R(draw, x, y, 4, 2, (80, 160, 90))
            else:
                R(draw, x, y, 8, 2, (150, 104, 66))
    clawd(draw, look=blend(look, k), blink=blink, bob=bob, dx=round(lean * k), lid=0.0)
    arm(draw, arm_up, bob)
    if k > .5:
        sweat(draw, bob, t)
    return img


def hu_a(t):
    return hurricane_frame(t, lean=2 if t % 4 < 2 else 3, bob=-1 if t % 8 in (3, 4) else 0, look=(2, 0), blink=t == 20)


def hu_b(t):
    return hurricane_frame(t, lean=3 if t % 2 else 2, look=(2, -1 if t % 8 < 4 else 1), arm_up=2 if 8 < t < 24 else 0, bob=1 if t % 6 < 3 else 0)


if __name__ == "__main__":
    for name, fr, n, a, b in (("sunny", sunny_frame, N_SUN, sunny_a, sunny_b), ("partly-cloudy", pc_frame, N_PC, pc_a, pc_b),
                              ("cloudy", cl_frame, N_CL, cl_a, cl_b), ("rain", rain_frame, N_RAIN, rain_a, rain_b),
                              ("snow", snow_frame, N_SNOW, snow_a, snow_b), ("thunder", th_frame, N_TH, th_a, th_b),
                              ("hurricane", hurricane_frame, N_HU, hu_a, hu_b)):
        enter, leave, loop = make(fr, n)
        save_flow(name, enter(), [loop(a)(), loop(b)()], leave())
