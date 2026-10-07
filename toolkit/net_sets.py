"""Problem and network sets: offline, overloaded, crash, web-fetch.

python net_sets.py  ->  ../mine/{offline,overloaded,crash,web-fetch}/
"""
import math
import random

from props import *


# ---------------------------------------------------------------- offline: the Wi-Fi bars drop out and come back
def wifi(draw, cx, cy, arcs, color, lit_dot=True):
    dot(draw, cx, cy, 2, color if lit_dot else (60, 64, 78))
    for i in range(3):
        r = 8 + i * 8
        c = color if i < arcs else (44, 48, 60)
        for deg in range(-48, 49, 2):
            a = math.radians(deg)
            R(draw, round(cx + math.sin(a) * r) - 1, round(cy - math.cos(a) * r) - 1, 2, 2, c)


def offline_frame(arcs=3, color=LIGHT_BLUE, cross=False, q=False, dots=None, look=(2, 1), blink=False, bob=0, slide=0,
                  sweat_f=None, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    wifi(draw, x0 + 44, 46, arcs, color, arcs > 0 or cross is False)
    if cross:
        cross_x(draw, x0 + 56, 30)
    if dots is not None:
        for i in range(3):
            lit = (i - dots) % 3 == 0
            R(draw, x0 + 36 + i * 8, 53, 4, 4, AMBER if lit else (60, 64, 78))
    clawd(draw, look=look, blink=blink, bob=bob)
    if q:
        draw_q(draw, OX + 22, 0)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def cross_x(draw, x, y):
    for i in range(10):
        R(draw, x + i, y + i, 3, 2, RED)
        R(draw, x + 9 - i, y + i, 3, 2, RED)


def draw_q(draw, x, y):
    for r, row in enumerate(("###", "..#", ".##", "...", ".#.")):
        for c, v in enumerate(row):
            if v == "#":
                R(draw, x + c * 2, y + r, 2, 1, AMBER)


def offline_drop():
    f = offline_frame
    frames = intro(f)
    for arcs in (2, 1, 0):                                                   # the bars fall away one by one
        frames += [f(arcs=arcs, color=mix(LIGHT_BLUE, ORANGE, (3 - arcs) / 3), look=(2, 0))] * 3
    for k in range(10):                                                      # no signal: X, question mark, Clawd confused
        frames.append(f(arcs=0, color=RED, cross=True, q=k % 4 < 3, sweat_f=k, bob=k % 2 if k > 5 else 0,
                        look=((2, 1), (1, 1), (0, 1), (1, 1), (2, 1))[k % 5]))
    for arcs in (1, 2, 3):                                                   # and it comes back
        frames += [f(arcs=arcs, color=mix(AMBER, GREEN, arcs / 3), look=(2, 0))] * 3
    frames += [f(arcs=3, color=GREEN, smile=True, bob=-1 if k == 0 else 0, look=(2, 0)) for k in range(4)]
    for k in range(3):
        frames.append(f(arcs=3, color=mix(GREEN, LIGHT_BLUE, (k + 1) / 3)))
    return frames + [f(blink=True), f()]


def offline_flicker():
    f = offline_frame
    frames = intro(f)
    seq = (3, 2, 3, 1, 0, 2, 0, 1, 3, 0, 1, 0, 2, 1)
    for k, a in enumerate(seq):                                              # the signal flickers
        frames += [f(arcs=a, color=AMBER if a < 3 else LIGHT_BLUE, look=(2, 1 + (k % 3 == 0)), bob=1 if a == 0 else 0)]
    for k in range(12):                                                      # "reconnecting" with chasing dots
        frames.append(f(arcs=0, color=AMBER, dots=k, look=(2, 2 - k % 2), bob=1 if k % 4 == 0 else 0, sweat_f=k if k > 8 else None))
    for arcs in (1, 2, 3):
        frames += [f(arcs=arcs, color=GREEN, look=(2, 0))] * 2
    for k in range(3):
        frames.append(f(arcs=3, color=mix(GREEN, LIGHT_BLUE, (k + 1) / 3), smile=k < 2))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- overloaded (529): too many requests hit the cloud
def cloud_big(draw, cx, cy, color):
    R(draw, cx - 16, cy - 2, 32, 10, color)
    R(draw, cx - 12, cy - 8, 12, 8, color)
    R(draw, cx - 4, cy - 12, 14, 12, color)
    R(draw, cx + 6, cy - 6, 10, 8, color)


def over_frame(load=0.0, f=0, retry=None, look=(2, 1), blink=False, bob=0, slide=0, sweat_f=None, code=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        shake = (-1, 1)[f % 2] if load > 0.7 else 0
        cloud_big(d, x0 + 44 + shake, 26, mix((110, 116, 130), RED, load))
        n = round(load * 14)
        for k in range(n):                                                   # requests streaming in from all sides
            ang = k * 2.4 + 0.5
            t = ((f * (0.07 + 0.012 * (k % 5)) + k * 0.31) % 1)
            dist = (1 - t) * 48
            px, py = 44 + math.cos(ang) * dist, 26 + math.sin(ang) * dist * 0.8
            R(d, x0 + round(px), round(py), 3, 3, [LIGHT_BLUE, AMBER, PINK][k % 3])
        if code:
            text(d, x0 + 31, 42, "529", RED, 3)
        if retry is not None:
            for i in range(8):
                ang = i * math.pi / 4
                lit = (i - retry) % 8
                c = mix((50, 54, 66), WHITE, max(0, 1 - lit / 5)) if lit < 5 else (50, 54, 66)
                R(d, round(x0 + 44 + math.cos(ang) * 8) - 1, round(46 + math.sin(ang) * 8) - 1, 3, 3, c)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def over_flood():
    f = over_frame
    frames = intro(f)
    for k in range(18):                                                      # more and more requests
        load = (k + 1) / 18
        frames.append(f(load, f=k, look=(2, 1 - (k > 9)), sweat_f=k if load > 0.5 else None, bob=1 if k % 6 == 0 else 0))
    for k in range(8):
        frames.append(f(1.0, f=k, code=True, sweat_f=k, look=(2, 1), bob=k % 2))
    for k in range(6):                                                       # it cools down
        load = 1.0 - (k + 1) / 6
        frames.append(f(load, f=k, code=k < 2, look=(2, 1)))
    return frames + [f(blink=True), f()]


def over_retry():
    f = over_frame
    frames = intro(f)
    for k in range(10):
        frames.append(f(min(1.0, (k + 1) / 10), f=k, sweat_f=k if k > 4 else None, look=(2, 1)))
    frames += [f(1.0, f=k, code=True, sweat_f=k, bob=k % 2, look=(1, 1)) for k in range(5)]
    for k in range(12):                                                      # waits, retry spinner, load melts away
        load = max(0.0, 1.0 - k / 12)
        frames.append(f(load, f=k, retry=k % 8, sweat_f=k if k < 6 else None, look=(2, 2 if k % 6 < 3 else 1)))
    frames += [f(0.0, f=k, retry=k % 8, look=(2, 1)) for k in range(4)]
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- crash: glitch, black screen, reboot
CODE_LINES = ((36, LIGHT_BLUE), (28, PINK), (40, AMBER), (22, GREEN))


def crash_frame(lines=4, bar=None, glitch=0, noise=False, black=False, bsod=0, seed=0, look=(2, 1), blink=False, bob=0,
                slide=0, sweat_f=None, dx=0, led=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (24, 26, 38))
    if black:
        R(draw, x0, 6, 89, 53, (4, 4, 6))
        if led:
            R(draw, x0 + 82, 53, 3, 3, RED)
    elif bsod:
        R(draw, x0, 6, 89, 53, (28, 70, 170))
        R(draw, x0 + 10, 14, 4, 4, WHITE)
        R(draw, x0 + 10, 22, 4, 4, WHITE)
        R(draw, x0 + 22, 14, 3, 12, WHITE)
        R(draw, x0 + 24, 12, 8, 3, WHITE)
        R(draw, x0 + 24, 25, 8, 3, WHITE)
        R(draw, x0 + 10, 36, 50, 2, (200, 215, 255))
        R(draw, x0 + 10, 42, 36, 2, (200, 215, 255))
        R(draw, x0 + 10, 48, 44, 2, (200, 215, 255))
    else:
        for i in range(min(lines, 4)):
            w, c = CODE_LINES[i]
            R(draw, x0 + 8, 16 + i * 10, w, 3, c)
        if bar is not None:
            R(draw, x0 + 14, 32, 60, 5, (36, 40, 52))
            R(draw, x0 + 15, 33, round(58 * bar), 3, LIGHT_BLUE)
    if glitch or noise:                                                      # tear the picture into shifted bands, add static
        rng = random.Random(seed)
        box = (x0, 6, x0 + 89, 59)
        region = img.crop(box)
        out = region.copy()
        y = 0
        while y < 53:
            h = rng.randint(3, 8)
            shift = rng.randint(-glitch * 5, glitch * 5) if glitch and rng.random() < 0.5 + glitch * 0.1 else 0
            band = region.crop((0, y, 89, min(53, y + h)))
            out.paste(band, (shift, y))
            y += h
        if noise:
            for _ in range(500):
                out.putpixel((rng.randrange(89), rng.randrange(53)), (rng.choice((255, 120, 40)),) * 3 + (255,))
        img.paste(out, (x0, 6))
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob, dx=dx)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def reboot(f, bsod=False):
    frames = [f(black=True, led=k % 2 == 0, look=(2, 1)) for k in range(3)]
    for k in range(8):
        frames.append(f(bar=(k + 1) / 8, lines=0, look=(2, 1 + (k % 4 > 1)), sweat_f=k if k < 4 else None))
    for n in range(1, 5):
        frames += [f(lines=n, look=(2, 1), bob=-1 if n == 4 else 0)] * 2
    return frames


def crash_glitch():
    f = crash_frame
    frames = intro(f)
    for g in (1, 2, 3, 4):
        frames += [f(glitch=g, seed=g * 7 + k, look=(1, 1), sweat_f=g if g > 2 else None, bob=k % 2, dx=0) for k in range(2)]
    frames += [f(noise=True, glitch=4, seed=40 + k, look=(0, 0), bob=-2 if k == 0 else 0, dx=(-1, 1)[k % 2]) for k in range(2)]
    return frames + reboot(f) + [f(blink=True), f()]


def crash_bsod():
    f = crash_frame
    frames = intro(f)
    frames += [f(glitch=2, seed=3 + k, look=(1, 1)) for k in range(3)]
    frames += [f(bsod=1, look=(0, 1), sweat_f=k, bob=k % 2 if k > 4 else 0) for k in range(10)]
    return frames + reboot(f) + [f(blink=True), f()]


# ---------------------------------------------------------------- web fetch: a page is pulled down from the cloud
def small_cloud(draw, x, y, color):
    R(draw, x + 2, y + 6, 20, 6, color)
    R(draw, x + 5, y + 3, 8, 5, color)
    R(draw, x + 10, y, 9, 8, color)
    R(draw, x + 15, y + 3, 7, 6, color)


def page(draw, x, y, w, h, lines=3, hl=0):
    R(draw, x, y, w, h, WHITE)
    R(draw, x, y, w, 4, (110, 120, 150))
    R(draw, x + 2, y + 1, 2, 2, RED)
    for i in range(lines):
        R(draw, x + 3, y + 7 + i * 5, w - 8 - (i % 2) * 6, 2, AMBER if i < hl else (150, 154, 168))


def web_frame(url=0, packet=None, pg=None, hl=0, extract=None, cloud=GREY, tickmark=False, look=(2, 1), blink=False, bob=0,
              slide=0, key=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 5, 9, 58, 7, (40, 44, 54))
    R(draw, x0 + 6, 10, 56, 5, (24, 26, 38))
    if url:
        R(draw, x0 + 8, 11, round(46 * url), 3, LIGHT_BLUE)
    small_cloud(draw, x0 + 64, 8, cloud)

    def paint(d):
        if packet is not None:
            px, py = packet
            R(d, x0 + px, py, 3, 3, WHITE)
        if pg is not None:
            page(d, x0 + pg[0], pg[1], 30, 26, 3, hl)
        if extract:
            for ex, ey, c in extract:
                R(d, x0 + ex, ey, 10, 2, c)
        if tickmark:
            tick(d, x0 + 66, 36, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def web_fetch():
    f = web_frame
    frames = intro(f)
    for k in range(8):                                                       # the URL is typed
        frames.append(f(url=(k + 1) / 8, key=k % 2 == 0, bob=k % 2, look=(2, 0)))
    for k in range(5):                                                       # the request flies up to the cloud
        t = (k + 1) / 5
        frames.append(f(url=1.0, packet=(round(lerp(30, 74, t)), round(lerp(16, 12, t))), look=(2, 0), cloud=GREY))
    frames += [f(url=1.0, cloud=LIGHT_BLUE, look=(2, 0))] * 2
    for k in range(6):                                                       # the page comes down
        t = ease((k + 1) / 6)
        frames.append(f(url=1.0, pg=(round(lerp(60, 26, t)), round(lerp(12, 26, t))), cloud=LIGHT_BLUE, look=(2, 1 + (k > 3))))
    for hl in (1, 2, 3):                                                     # its text lines light up
        frames += [f(url=1.0, pg=(26, 26), hl=hl, cloud=LIGHT_BLUE, look=(2, 1 + hl // 2))] * 3
    for k in range(5):                                                       # and fly towards Clawd as a summary
        frames.append(f(url=1.0, pg=(26, 26), hl=3, cloud=LIGHT_BLUE, extract=[(round(lerp(30, 4, (k + 1) / 5)), 32 + i * 5, AMBER) for i in range(3)],
                        look=(1, 1)))
    frames += [f(url=1.0, tickmark=True, cloud=GREEN, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(7)]
    frames += [f(url=0.5), f(url=0.0, cloud=mix(GREEN, GREY, 0.6)), f(blink=True)]
    return frames + [f()]


def web_fetch_many():
    f = web_frame
    frames = intro(f)
    for k in range(5):
        frames.append(f(url=(k + 1) / 5, key=k % 2 == 0, bob=k % 2, look=(2, 0)))
    for n in range(3):                                                       # three pages in a row, each smaller summary line
        for k in range(4):
            t = (k + 1) / 4
            frames.append(f(url=1.0, packet=(round(lerp(30, 74, t)), round(lerp(16, 12, t))), cloud=LIGHT_BLUE, look=(2, 0)))
        for k in range(4):
            t = ease((k + 1) / 4)
            frames.append(f(url=1.0, pg=(round(lerp(60, 26, t)), round(lerp(12, 26, t))), cloud=LIGHT_BLUE, hl=0, look=(2, 1)))
        frames += [f(url=1.0, pg=(26, 26), hl=3, cloud=LIGHT_BLUE, look=(2, 2), bob=1)] * 2
        for k in range(3):
            frames.append(f(url=1.0, cloud=LIGHT_BLUE, extract=[(round(lerp(30, 4, (k + 1) / 3)), 34, AMBER)], look=(1, 1)))
    frames += [f(url=1.0, tickmark=True, cloud=GREEN, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 4) for k in range(6)]
    frames += [f(url=0.5), f(url=0.0, cloud=mix(GREEN, GREY, 0.6)), f(blink=True)]
    return frames + [f()]


if __name__ == "__main__":
    finish("offline", offline_frame, [offline_drop, offline_flicker])
    finish("overloaded", over_frame, [over_flood, over_retry])
    finish("crash", crash_frame, [crash_glitch, crash_bsod])
    finish("web-fetch", web_frame, [web_fetch, web_fetch_many])
