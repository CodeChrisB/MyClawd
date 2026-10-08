"""Weather in one shared world: sunny, partly-cloudy, cloudy, rain, snow, thunder, hurricane. Two loops each.

python weather_world.py  ->  ../mine/{sunny,partly-cloudy,cloudy,rain,snow,thunder,hurricane}/
Every set has the same stage: Clawd stands on a ground strip that spans the canvas, a tree and a house are on the right.
The weather changes the world and Clawd himself: green grass, dull grass, wet ground with puddles, white snow; a wet roof, snow on
roof and tree, lit windows, a bending tree and grass in the wind. Clawd turns darker and drips when it rains, snow piles up on his
head and shoulders, he shakes it off.
Seamless like seamless.py asks: the enter starts on the base pose (Clawd alone) and uncovers ground, tree, house and weather
(presence k 0 to 1, everything is off canvas at k = 0); the exit goes back. Loops are exactly one period of t, no duplicate end frame.
"""
import math
import random

from props import *
from font3 import say
from seamless import save_flow
from weather_sets import cloud, sun, shades, scarf, blend, CLOUD_W, CLOUD_S, CLOUD_G, CLOUD_GS, CLOUD_D, CLOUD_DS, RAIN_C, SNOW_C

GY = 56                                   # top of the ground, Clawd's feet stand on it
GRASS, GRASS_D = (84, 168, 92), (58, 128, 70)
DULL, DULL_D = (88, 138, 90), (66, 104, 74)
WET, WET_D = (50, 100, 72), (36, 76, 56)
SNOW_G, SNOW_D = (244, 247, 252), (196, 210, 232)
WALL, ROOF, WOOD_D = (206, 176, 128), (160, 62, 52), (110, 70, 44)
COLORS = [RED, YELLOW, PINK, LIGHT_BLUE]


def tint(c, to, a):
    return mix(c, to, max(0.0, min(1.0, a)))


# ---------------------------------------------------------------- the world


def ground(draw, mode, t, k, wind=0.0, puddles=False):
    top = GY + round((1 - k) * 12)
    main, dark = {"grass": (GRASS, GRASS_D), "dull": (DULL, DULL_D), "wet": (WET, WET_D), "snow": (SNOW_G, SNOW_D)}[mode]
    R(draw, 0, top, 192, 64 - top, main)
    R(draw, 0, top + 4, 192, 64 - top - 4, dark)
    if mode == "snow":
        for x in range(0, 192, 3):                                    # soft drifts
            R(draw, x, top - (1 if (x * 5) % 7 < 2 else 0), 3, 1, SNOW_G)
        return
    if top > GY + 3:
        return
    for x in range(1, 192, 5):                                        # blades, they bend in the wind
        h = 3 + (x * 7) % 3
        bend = round(wind * 2 * math.sin(2 * math.pi * t / 8 + x))
        R(draw, x, top - h, 1, h, dark if mode == "wet" else main)
        R(draw, x + bend, top - h - 1, 1, 1, dark if mode == "wet" else main)
    if puddles:
        for px, w in ((98, 16), (150, 22), (22, 14)):
            R(draw, px, top + 1, w, 2, (92, 120, 168))
            r = 1 + (t // 2 + px) % 4
            R(draw, px + w // 2 - r * 2, top + 1, r * 4, 1, (150, 176, 220))


def house(draw, dx=0, snow=0.0, wet=0.0, lit=False, flash=0.0, t=0, wind=0.0, k=1.0):
    x0 = 128 + dx + round((1 - k) * 120) + (round(wind * math.sin(t * 2.4)) if wind else 0)
    wall = tint(WALL, (120, 110, 130), wet * .25)
    roof = tint(ROOF, (96, 50, 56), wet * .4)
    R(draw, x0, 34, 56, 22, wall)
    R(draw, x0 + 40, 14, 7, 20, tint((150, 80, 70), (100, 60, 64), wet * .4))        # chimney
    draw.polygon([(x0 - 5, 35), (x0 + 61, 35), (x0 + 28, 14)], fill=roof)
    if snow > 0:
        draw.polygon([(x0 - 1, 33), (x0 + 57, 33), (x0 + 28, 14 + round((1 - snow) * 12))], fill=SNOW_G)
        R(draw, x0 - 5, 34, 66, round(2 * snow), SNOW_G)
        R(draw, x0 + 40, 13, 7, round(2 * snow), SNOW_G)
    R(draw, x0 + 8, 40, 14, 11, WOOD_D)                                               # window
    light = (250, 214, 110) if lit else (150, 190, 226)
    if flash:
        light = tint(light, WHITE, flash)
    R(draw, x0 + 9, 41, 12, 9, light)
    R(draw, x0 + 14, 41, 2, 9, WOOD_D)
    R(draw, x0 + 9, 45, 12, 1, WOOD_D)
    R(draw, x0 + 36, 42, 11, 14, WOOD_D)                                              # door
    R(draw, x0 + 44, 49, 1, 2, YELLOW)
    for i in range(3):                                                                # chimney smoke
        age = (t * 3 + i * 8) % 24
        R(draw, x0 + 41 + round(wind * age / 2) + (i % 2), 11 - age // 2 - (i % 2), 4, 3, tint((220, 222, 230), (110, 114, 130), wet * .3))
    return x0


def tree(draw, x, t, k, wind=0.0, snow=0.0, wet=0.0, dark=0.0):
    x += round((1 - k) * 120)
    sway = round(wind * 3 * math.sin(2 * math.pi * t / 8))
    R(draw, x - 2, 38, 5, 18, tint(WOOD_D, (60, 40, 30), wet * .3))
    leaf = tint((84, 160, 92), (54, 96, 66), max(wet * .5, dark * .4))
    leaf_d = tint((58, 122, 70), (40, 72, 54), max(wet * .5, dark * .4))
    for ox_, oy_, r in ((-6, 0, 9), (6, 1, 9), (0, -7, 10)):
        dot(draw, x + ox_ + sway, 30 + oy_, r, leaf_d)
        dot(draw, x + ox_ + sway - 1, 29 + oy_, r - 2, leaf)
    if snow > 0:
        R(draw, x - 8 + sway, 20 + round((1 - snow) * 4), 17, round(3 * snow), SNOW_G)
        R(draw, x - 12 + sway, 28, 5, round(2 * snow), SNOW_G)
        R(draw, x + 8 + sway, 29, 5, round(2 * snow), SNOW_G)


def rain_drops(draw, t, count, front, wind=0.0, splash=True):
    for i in range(count):
        x0, y0 = (i * 37 + (11 if front else 0)) % 192, (i * 23) % 64
        y = (y0 + 8 * t) % 64
        x = round((x0 + (0.25 + wind * .5) * y) % 192)
        if y < GY - 3:
            R(draw, x, y, 1, 3, RAIN_C)
        elif y < GY and splash:
            R(draw, x - 1, GY - 1, 3, 1, (190, 210, 245))


def flakes(draw, t, n, count):
    for i in range(count):
        x0, y0, s = (i * 41) % 192, (i * 17) % 64, 2 if i % 3 else 4
        y = (y0 + s * t * 64 // (s * n)) % 64 if False else (y0 + s * t) % 64
        x = x0 + round(3 * math.sin(2 * math.pi * (t / n) * (1 + i % 2) + i))
        if y < GY:
            R(draw, x, y, 2 if s == 4 else 1, 2 if s == 4 else 1, SNOW_C if s == 4 else tint(SNOW_C, LIGHT_BLUE, .4))


# ---------------------------------------------------------------- Clawd and what the weather does to him

HEAD_X = list(range(0, 48, 2))
random.Random(5).shuffle(HEAD_X)
ARM_X = [(-12 + i, 0) for i in range(0, 12, 2)] + [(48 + i, 0) for i in range(0, 12, 2)]
random.Random(9).shuffle(ARM_X)


def clawd_fx(img, draw, look=(0, 0), lid=0.0, bob=0, dx=0, blink=False, wet=0.0, snow=0.0, t=0, mouth=None, rainy=False):
    clawd(draw, look=look, blink=blink, lid=lid, bob=bob, dx=dx)
    if wet > 0.02:                                                    # wet fur is darker and bluish
        px = img.load()
        for x in range(max(0, OX + dx - 14), min(192, OX + dx + 62)):
            for y in range(max(0, OY + bob - 2), min(64, OY + bob + 50)):
                if px[x, y][:4] == CORAL + (255,):
                    px[x, y] = tint(CORAL, (104, 112, 160), wet * .38) + (255,)
        for j, ax in enumerate((OX - 8, OX - 3, OX + 51, OX + 57)):   # drips from the arms, and from the chin
            age = (t + j * 3) % 8
            if age < 6:
                R(draw, ax + dx, OY + 4 * G + bob + age * 2, 1, 2, (150, 190, 240))
        age = (t + 2) % 8
        if age < 6:
            R(draw, OX + 3 * G + dx, OY + 4 * G + 12 + bob + age * 2 - 8, 1, 2, (150, 190, 240)) if False else None
        if rainy:                                                     # raindrops splashing on his head
            for j in range(3):
                sx = OX + dx + 4 + (t * 13 + j * 17) % 40
                if (t + j) % 3 == 0:
                    R(draw, sx, OY + bob - 2, 3, 1, (190, 210, 245))
    if snow > 0.02:
        n_head = round(len(HEAD_X) * snow)
        for x in HEAD_X[:n_head]:
            R(draw, OX + dx + x, OY + bob - 1, 2, 1, SNOW_C)
            if x % 4 == 0:
                R(draw, OX + dx + x, OY + bob, 2, 1, SNOW_C)
        n_arm = round(len(ARM_X) * snow)
        for ax, _ in ARM_X[:n_arm]:
            R(draw, OX + dx + ax, OY + 2 * G + bob - 1, 2, 1, SNOW_C)
    if mouth == "smile":
        draw_smile(draw, OX + 4 * G + dx, OY + 2 * G + 1 + bob)
    elif mouth == "flat":
        R(draw, OX + 4 * G - 3 + dx, OY + 2 * G + 3 + bob, 6, 2, BLACK)
    elif mouth == "yawn":
        draw.rectangle([OX + 4 * G - 4 + dx, OY + 2 * G + bob, OX + 4 * G + 3 + dx, OY + 2 * G + 5 + bob], fill=BLACK)


COAT, COAT_D = (252, 210, 58), (214, 164, 28)


def raincoat(draw, dx=0, bob=0):
    """A cute yellow raincoat: hood with a brim, buttoned coat, sleeves with cuffs. The face and legs stay free."""
    ox, oy = OX + dx, OY + bob
    R(draw, ox - 2, oy - 4, 52, 9, COAT)                      # hood
    R(draw, ox - 2, oy + 4, 5, 10, COAT)
    R(draw, ox + 45, oy + 4, 5, 10, COAT)
    R(draw, ox + 5, oy + 4, 38, 2, COAT_D)                    # brim
    R(draw, ox + 3, oy - 3, 6, 1, (255, 238, 150))
    R(draw, ox + 5, oy + 2 * G + 4, 38, 3, COAT)              # collar, below the mouth
    R(draw, ox - 12, oy + 2 * G + 5, 72, 12, COAT)            # coat and sleeves
    R(draw, ox, oy + 4 * G + 5, 48, 12, COAT)                 # skirt of the coat
    R(draw, ox - 12, oy + 4 * G - 2, 12, 2, COAT_D)           # cuffs
    R(draw, ox + 48, oy + 4 * G - 2, 12, 2, COAT_D)
    R(draw, ox, oy + 4 * G + 15, 48, 2, COAT_D)               # hem
    R(draw, ox + 23, oy + 2 * G + 7, 2, 22, COAT_D)           # placket
    for by in (oy + 2 * G + 10, oy + 4 * G + 2, oy + 4 * G + 10):
        R(draw, ox + 21, by, 2, 2, (60, 40, 20))
        R(draw, ox + 25, by, 2, 2, (60, 40, 20))
    R(draw, ox + 6, oy + 4 * G + 6, 10, 5, COAT_D)            # pocket


def shadow(draw, k, dx=0, a=1.0):
    if k > .3 and a > 0:
        R(draw, OX + 4 + dx, GY, 40, 2, tint(GRASS_D, (30, 80, 50), a))


# ---------------------------------------------------------------- the scenes


def scene(kind, t=0, k=1.0, n=32, look=(0, 0), lid=0.0, bob=0, dx=0, blink=False, mouth=None, extra=None, **kw):
    img, draw = new_frame()
    cfg = dict(sun=False, clouds=(), drops=0, flakes=0, mode="grass", lit=False, wind=0.0, wet=0.0, snow=0.0, swirl=False, dull=0.0, tornado=False, tree=True,
               flash=0.0, puddles=False, accessory=None, shadow=True, stormy=False)
    cfg.update(KINDS[kind])
    cfg.update(kw)
    off = round((1 - k) * 280)
    if cfg["flash"]:
        R(draw, 84, 0, 108, GY, tint((70, 80, 120), (225, 232, 255), cfg["flash"]))
    if cfg["tornado"] and k > .15:
        tornado(draw, t, n, k)
    if cfg["sun"]:
        sun(draw, 84, 12 + round((1 - k) * 80), 8, t, n, dim=cfg.get("sun_dim", 0.0), rays=k > .3 and cfg.get("sun_dim", 0) < .5)
    for cx, cy, w, c, s_ in cfg["clouds"]:
        cloud(draw, round(cx(t, n) if callable(cx) else cx) + off, cy, w, c, s_)
    if cfg["drops"] and k > .25:
        rain_drops(draw, t, round(cfg["drops"] * .6 * min(1.0, k * 1.5)), False, cfg["wind"])
    x_house = house(draw, 0, cfg["snow"] * k, cfg["wet"] * k, cfg["lit"] or cfg["dull"] > 0, cfg["flash"], t, cfg["wind"], k)
    if cfg["tree"]:
        tree(draw, 108, t, k, cfg["wind"], cfg["snow"] * k, cfg["wet"] * k, cfg["dull"])
    ground(draw, cfg["mode"], t, k, cfg["wind"], cfg["puddles"])
    if cfg["shadow"] and cfg["mode"] == "grass":
        shadow(draw, k, dx, 1.0 - cfg.get("sun_dim", 0.0))
    if cfg["flakes"] and k > .25:
        flakes(draw, t, n, round(cfg["flakes"] * min(1.0, k * 1.5)))
    clawd_fx(img, draw, look=blend(look, k), lid=lid * k, bob=bob, dx=round(dx * k), blink=blink, wet=cfg["wet"] * k, snow=cfg["snow"] * k, t=t,
             mouth=mouth if k > .6 else None, rainy=cfg["drops"] > 0)
    if cfg["accessory"] == "shades" and k > .6:
        shades(draw, bob, kw.get("glint"))
    if cfg["accessory"] == "raincoat" and k > .6:
        raincoat(draw, round(dx * k), bob)
    if cfg["accessory"] == "scarf" and k > .6:
        scarf(draw, bob)
    if cfg["drops"] and k > .25:
        rain_drops(draw, t, round(cfg["drops"] * .4 * min(1.0, k * 1.5)), True, cfg["wind"])
    if cfg["wind"] and k > .3:
        for i in range(8):
            x = (i * 53 + 6 * t) % 192
            R(draw, x, 4 + (i * 29) % 46, 10, 1, (206, 214, 228))
        for i in range(4):
            x = (i * 71 + 6 * t) % 192
            y = 12 + (i * 37) % 34 + round(5 * math.sin(2 * math.pi * (t / n) * 2 + i))
            R(draw, x, y, 8 if i % 2 == 0 else 4, 2, (150, 104, 66) if i % 2 == 0 else (80, 160, 90))
    if extra:
        extra(draw)
    return img


TOR_X, TOR_TOP = 100, 4


def tornado(draw, t, n, k):
    """A funnel: wide at the top, narrowing to the ground. Bands run around it, rows at different speeds make it spin."""
    h = GY - TOR_TOP
    cloud(draw, TOR_X - 40 + round((1 - k) * 130), -4, 80, CLOUD_D, CLOUD_DS)
    for y in range(TOR_TOP + 6, GY):
        f = (GY - y) / h
        w = round((5 + 36 * f ** 1.5) * max(.4, k))
        shift = (4 * t if y % 4 < 2 else -4 * t) + round(3 * math.sin(y / 4.0))
        for x in range(TOR_X - w // 2, TOR_X - w // 2 + w):
            band = ((x - shift) // 6) % 2
            edge = min(x - (TOR_X - w // 2), (TOR_X - w // 2 + w - 1) - x)
            col = (176, 182, 198) if band else (104, 110, 130)
            if edge < 2:
                col = (66, 70, 88)
            R(draw, x, y, 1, 1, col)
    for i in range(8):                                                   # dust at the foot of the funnel
        a = 2 * math.pi * (i / 8 + 2 * t / n)
        R(draw, TOR_X + round(math.cos(a) * 14) - 1, GY - 3 + round(math.sin(a) * 2), 3, 2, (150, 130, 100))
    for i in range(6):                                                   # debris circling the funnel
        a = 2 * math.pi * (i / 6 + 2 * t / n)
        yy = 14 + i * 7
        f = (GY - yy) / h
        r = (5 + 36 * f ** 1.5) / 2 + 5
        R(draw, TOR_X + round(math.cos(a) * r), yy + round(math.sin(a) * 2), 4 if i % 2 else 3, 2, (150, 104, 66) if i % 2 else (84, 160, 94))


def drift(speed, x0, period=240):
    return lambda t, n: (x0 - t * speed) % period - 40


KINDS = {
    "sunny": dict(sun=True, mode="grass", accessory="shades"),
    "partly": dict(sun=True, mode="grass", clouds=((drift(5, 240), 6, 40, CLOUD_W, CLOUD_S), (drift(3, 130), 26, 30, CLOUD_W, CLOUD_S))),
    "cloudy": dict(mode="dull", dull=1.0, clouds=((90, 2, 46, CLOUD_G, CLOUD_GS), (136, 6, 52, CLOUD_G, CLOUD_GS), (110, 18, 44, CLOUD_D, CLOUD_DS),
                                                (160, 20, 36, CLOUD_G, CLOUD_GS)), shadow=False),
    "rain": dict(mode="wet", wet=1.0, lit=True, drops=34, puddles=True, shadow=False, accessory="raincoat",
                 clouds=((88, 0, 50, CLOUD_G, CLOUD_GS), (130, 2, 56, CLOUD_D, CLOUD_DS), (164, 4, 40, CLOUD_D, CLOUD_DS))),
    "snow": dict(mode="snow", snow=1.0, lit=True, flakes=38, accessory="scarf", shadow=False,
                 clouds=((88, 0, 50, (222, 228, 240), (176, 186, 206)), (132, 2, 56, (222, 228, 240), (176, 186, 206)), (170, 4, 36, (222, 228, 240), (176, 186, 206)))),
    "thunder": dict(mode="wet", wet=1.0, lit=True, drops=26, puddles=True, shadow=False, stormy=True, accessory="raincoat",
                    clouds=((86, 0, 56, CLOUD_D, CLOUD_DS), (132, 2, 56, CLOUD_D, CLOUD_DS), (166, 0, 40, CLOUD_D, CLOUD_DS))),
    "hurricane": dict(mode="wet", wet=1.0, lit=True, drops=26, wind=1.0, tornado=True, tree=False, shadow=False, accessory="raincoat"),
}


def bolt(draw, x=158, top=2):
    pts = [(x + 2, top), (x - 5, top + 14), (x + 4, top + 16), (x - 4, top + 34), (x + 5, top + 38)]
    draw.line(pts, fill=(255, 220, 90), width=3)
    draw.line(pts, fill=WHITE, width=1)


# loops: variant(t) -> kwargs for scene(), t = 0 is always the seam (no overrides)

N = {"sunny": 36, "partly": 48, "cloudy": 40, "rain": 32, "snow": 32, "thunder": 40, "hurricane": 32}


def sunny_a(t):
    return dict(look=(2, -1), mouth="smile", glint=(t // 2) % 14 if 6 <= t < 20 else None, blink=t == 30, bob=-1 if t in (18, 19) else 0)


def sunny_b(t):
    return dict(look=(2, -1), mouth="smile", glint=(t // 3) % 12 if t < 18 else None,
                extra=(lambda d, t=t: butterfly(d, t)) if 4 <= t < 32 else None)


def butterfly(draw, t):
    x = 80 + round(26 * math.sin(2 * math.pi * (t - 4) / 28 * 1.0)) + (t - 4) * 2
    y = 36 + round(8 * math.sin(t / 1.6))
    R(draw, x, y - 1, 2, 4, (70, 56, 70))
    f = t % 2
    for sx in (-1, 1):
        wx = x + (2 if sx > 0 else -4)
        R(draw, wx, y - 2 + f * 2, 4, 3 - f, (240, 150, 60))
        R(draw, wx, y + 1, 3, 2, (230, 110, 150))


def partly_a(t):
    return dict(look=(2, -1), blink=t == 40, lid=0.2, sun_dim=cover(t))


def partly_b(t):
    return dict(look=(2, -2) if 14 < t < 34 else (2, 0), bob=-1 if t in (20, 21) else 0, blink=t == 8, lid=0.2, sun_dim=cover(t))


def cover(t):
    best = 0.0
    for sp, x0, w in ((5, 240, 40), (3, 130, 30)):
        c = (x0 - t * sp) % 240 - 40 + w / 2
        best = max(best, 1 - abs(c - 84) / 18)
    return max(0.0, min(1.0, best)) * .7


def cloudy_a(t):
    return dict(look=(2, -2) if t < 30 else (2, 0), mouth="flat", lid=.25, blink=t == 34)


def cloudy_b(t):
    y = 12 <= t < 24
    return dict(look=(2, -1), mouth="yawn" if y else "flat", lid=.25, bob=-1 if t in (14, 15) else 0, blink=t == 28)


def rain_a(t):
    return dict(look=(2, -2) if 8 < t < 22 else (2, 0), blink=t == 20, mouth="flat" if 10 < t < 26 else None, lid=.2)


def rain_b(t):
    """Shakes the water off: his body jitters and drops fly out."""
    sh = 10 <= t < 20
    def fling(d):
        for i in range(10):
            a = i / 10 * 2 * math.pi
            age = t - 10
            R(d, OX + 24 + round(math.cos(a) * (14 + age * 3)), OY + 24 + round(math.sin(a) * (10 + age * 2.4)), 2, 2, (150, 190, 240))
    return dict(dx=(2 if t % 2 else -2) if sh else 0, look=(2, 1) if sh else (2, 0), extra=fling if sh else None, blink=t == 24, lid=.3 if sh else .2)


def snow_a(t):
    sh = 1 if 6 < t < 26 and t % 2 else 0
    def breath(d):
        if 18 < t < 62 and t % 8 < 4:
            R(d, OX + 8 * G + 2 + (t % 8), OY + 3 * G - (t % 8), 2, 1, WHITE)
    return dict(dx=sh, look=(2, -1) if 10 < t < 22 else (2, 0), lid=.35 if 6 < t < 26 else .2, blink=t == 28, extra=breath)


def snow_b(t):
    """Shakes the snow off, then it slowly piles up again."""
    shake = 8 <= t < 14
    s = 1.0 if t < 8 else 0.0 if t < 15 else min(1.0, (t - 14) / 16)
    def puff_(d):
        if shake:
            for i in range(10):
                a = i / 10 * 2 * math.pi
                R(d, OX + 24 + round(math.cos(a) * (16 + (t - 8) * 4)), OY + 6 + round(math.sin(a) * (8 + (t - 8) * 2)), 2, 2, SNOW_C)
    return dict(dx=(2 if t % 2 else -2) if shake else 0, snow=s, look=(2, 0), lid=.3 if shake else .2, extra=puff_, blink=t == 28)


FLASH = {8: 1.0, 9: .5, 26: 1.0, 27: .6, 29: .8}


def thunder_a(t):
    f = FLASH.get(t, 0.0) if t < 20 else 0.0
    def draw_(d):
        if f:
            bolt(d)
        if 13 <= t < 20:
            say(d, 100, 40, "BOOM", YELLOW, 3)
    return dict(flash=f, extra=draw_, bob=-3 if t in (10, 11) else -1 if t in (9, 12) else 0, look=(0, 0) if 8 <= t < 16 else (2, -1),
                blink=t == 34, lid=0.0)


def thunder_b(t):
    f = FLASH.get(t, 0.0) if (t >= 24 or t in (8, 9)) else 0.0
    def draw_(d):
        if f:
            bolt(d, 140)
        if 30 <= t < 37:
            say(d, 100, 40, "BOOM", YELLOW, 3)
    return dict(flash=f, extra=draw_, bob=-3 if t in (28, 29) else -1 if t in (27, 30) else 0, look=(2, 0) if t < 26 else (0, 0),
                blink=t == 4, lid=0.0)


def hurricane_a(t):
    return dict(dx=2 if t % 4 < 2 else 3, bob=-1 if t % 8 in (3, 4) else 0, look=(2, 0), blink=t == 20)


def hurricane_b(t):
    return dict(dx=3 if t % 2 else 2, look=(2, -1 if t % 8 < 4 else 1), bob=1 if t % 6 < 3 else 0)


SETS = [("sunny", "sunny", sunny_a, sunny_b), ("partly-cloudy", "partly", partly_a, partly_b), ("cloudy", "cloudy", cloudy_a, cloudy_b),
        ("rain", "rain", rain_a, rain_b), ("snow", "snow", snow_a, snow_b), ("thunder", "thunder", thunder_a, thunder_b),
        ("hurricane", "hurricane", hurricane_a, hurricane_b)]


def build(name, kind, a, b):
    n = N[kind]
    base_kw = {"sunny": dict(look=(2, -1), mouth="smile"), "partly": dict(look=(2, -1), lid=.2), "cloudy": dict(look=(2, -2), mouth="flat", lid=.25),
               "rain": dict(look=(2, 0), lid=.2), "snow": dict(look=(2, 0), lid=.2), "thunder": dict(look=(2, -1), lid=0.0),
               "hurricane": dict(look=(2, 0), dx=2)}[kind]

    def at_rest(t):
        return scene(kind, t, 1.0, n, **base_kw)

    enter = [scene(kind, (i - 6) % n, ease(i / 5), n, **base_kw) for i in range(6)]
    leave = [scene(kind, i, 1 - ease(i / 5), n, **base_kw) for i in range(6)]

    def loop(variant):
        return [at_rest(0)] + [scene(kind, t, 1.0, n, **{**base_kw, **variant(t)}) for t in range(1, n)]
    return enter, [loop(a), loop(b)], leave


if __name__ == "__main__":
    for name, kind, a, b in SETS:
        enter, loops, leave = build(name, kind, a, b)
        save_flow(name, enter, loops, leave)
