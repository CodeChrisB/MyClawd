"""Four limit sets: context too high, 5h limit reached, 7d limit reached, API cost limit reached.

python limit_sets.py  ->  ../mine/{context,limit-5h,limit-7d,limit-cost}/
Seam pose = the gauge / hourglass / calendar / jar at rest with Clawd awake.
"""
import math

from props import *
from PIL import ImageDraw


def finish(name, frame, loops):
    enter, leave = seam_slides(frame)
    save_set(name, enter, loops, leave)


GLASS = (150, 154, 168)
EMPTY = (36, 40, 52)
LINES = [LIGHT_BLUE, PINK, AMBER, GREEN, PURPLE]


# ---------------------------------------------------------------- context: the gauge fills up, Clawd compacts
GREY_BAR = (46, 50, 62)
N_BARS = 10


def warn_tri(draw, cx, y, color):
    """Small warning triangle, 7 rows, with a notch for the exclamation mark."""
    for r in range(7):
        w = 1 + 2 * r
        R(draw, cx - w // 2, y + r, w, 1, color)
    R(draw, cx, y + 2, 1, 3, DARK)
    R(draw, cx, y + 5, 1, 1, DARK)


def bars_for(h):
    """How many of the 10 bars sit at or below a gauge fill of h px (bars are 4 px apart from the floor)."""
    return 0 if h < 4 else min(N_BARS, (h - 4) // 4 + 1)


def draw_bars(draw, x0, colored, shimmer=None):
    """Ten bars on the right. Those level with the gauge fill are coloured, the ones above it grey."""
    for i in range(N_BARS):
        w = 22 + (i * 7) % 22
        color = LINES[i % len(LINES)] if i < colored else GREY_BAR
        if shimmer is not None and colored and i == shimmer % colored:
            color = tuple(min(255, c + 70) for c in color)
        R(draw, x0 + 38, 50 - i * 4, w if i < colored else 8, 3, color)  # unused bars stay short and grey


def draw_gauge(draw, x0, segs_h, color, shake=0):
    """Gauge on the left with 6 px segments. segs_h = fill height in px."""
    gx = x0 + 8 + shake
    R(draw, gx - 1, 9, 18, 46, EMPTY)
    R(draw, gx, 10, 16, 44, DARK)
    R(draw, gx, 54 - segs_h, 16, segs_h, color)
    for y in range(54 - 6, 10, -6):
        R(draw, gx, y, 16, 1, DARK)


def ctx_frame(level=0.0, lines=None, summary=0, warn=0, shake=0, tickmark=False, sweat_f=None, key=False, look=(2, 1),
              blink=False, bob=0, slide=0):
    """The context gauge on the left, ten bars on the right. Bars level with the gauge are coloured, the others grey."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    h = round(44 * level)
    color = GREEN if level < 0.5 else AMBER if level < 0.8 else RED
    draw_gauge(draw, x0, h, color, shake)
    draw_bars(draw, x0, bars_for(h) if lines is None else lines)
    if summary:
        R(draw, x0 + 38, 50, 12, 3 + summary, AMBER)
    if warn:
        warn_tri(draw, x0 + 75, 7, RED if warn == 2 else AMBER)
    if tickmark:
        tick(draw, x0 + 58, 20, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def ctx_gauge():
    frames = [ctx_frame()] * 4 + [ctx_frame(blink=True)] + [ctx_frame()] * 2
    for i in range(18):
        lv = (i + 1) / 18
        frames.append(ctx_frame(lv, warn=(1 + (i // 2) % 2) if lv > 0.85 else 0, sweat_f=i if lv > 0.7 else None,
                                look=(2, 0 if lv > 0.5 else 1)))
    frames += [ctx_frame(1.0, warn=1 + k % 2, shake=(-1, 1)[k % 2], sweat_f=k, bob=k % 2) for k in range(5)]
    frames += [ctx_frame(1.0, warn=2, key=True, bob=1 - k % 2, look=(2, 2)) for k in range(4)]
    for k in range(6):
        frames.append(ctx_frame(1.0 - 0.8 * ease((k + 1) / 6), look=(2, 1)))
    frames += [ctx_frame(0.2, tickmark=True)] * 6
    frames += [ctx_frame(0.1, tickmark=True), ctx_frame(0.0, tickmark=True, blink=True)]
    return frames + [ctx_frame()]


def ctx_pile():
    frames = [ctx_frame()] * 3 + [ctx_frame(blink=True)] + [ctx_frame()] * 2
    for n in range(1, 11):
        lv = n / 10
        frames += [ctx_frame(lv, lines=n, warn=(1 + n % 2) if lv > 0.8 else 0, sweat_f=n if lv > 0.7 else None,
                             look=(2, min(2, max(0, 2 - n // 4))))] * 2
    frames += [ctx_frame(1.0, lines=10, warn=2, key=True, bob=k % 2, look=(2, 2)) for k in range(4)]
    for k in range(5):                                                       # lines squash into one summary block
        n = max(0, 10 - 2 * (k + 1))
        frames.append(ctx_frame(max(0.2, n / 10), lines=n, summary=1 + k // 2, look=(2, 1)))
    frames += [ctx_frame(0.2, summary=2, tickmark=True)] * 6
    frames += [ctx_frame(0.1, summary=1, tickmark=True), ctx_frame(0.0, summary=0, tickmark=True, blink=True)]
    return frames + [ctx_frame()]


# ---------------------------------------------------------------- 5h limit: hourglass
HG_X = 10


def hourglass(draw, x0, a, flash=False):
    cx = x0 + HG_X + 9
    R(draw, cx - 11, 11, 22, 3, GLASS)
    R(draw, cx - 11, 46, 22, 3, GLASS)
    for r in range(14):
        w = 18 - round(r * 16 / 13)
        for yy, rr in ((14 + r, r), (45 - r, r)):
            R(draw, cx - w // 2 - 1, yy, 1, 1, GLASS)
            R(draw, cx + w // 2 + (w % 2), yy, 1, 1, GLASS)
    top, bot = round(14 * a), round(14 * (1 - a))
    for r in range(14):
        w = 18 - round(r * 16 / 13)
        if r >= 14 - top:
            R(draw, cx - w // 2, 14 + r, w + w % 2, 1, AMBER)
        rb = 13 - r                                                          # bottom bulb row
        wb = 18 - round(rb * 16 / 13)
        if r >= 14 - bot:
            R(draw, cx - wb // 2, 45 - rb, wb + wb % 2, 1, AMBER)
    if 0 < a < 1:
        R(draw, cx, 28, 1, 15, YELLOW)
    if flash:
        R(draw, cx - 1, 29, 3, 2, WHITE)


def lim_frame(label, a=1.0, hot=False, lid=0.0, zf=None, look=(2, 1), blink=False, bob=0, slide=0, marks=0, extra=None):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    if label == "5":
        hourglass(draw, x0, a)
    else:
        calendar(draw, x0, marks)
    text(draw, x0 + 52, 22, label + ("H" if label == "5" else "D"), (235, 90, 90) if hot else (110, 50, 50), 3)
    clawd(draw, look=look, blink=blink, lid=lid, bob=bob)
    if zf is not None:
        zzz(draw, zf)
    return img


def hg_run(label_unused=None):
    f = lambda **k: lim_frame("5", **k)
    frames = [f()] * 4 + [f(blink=True)] + [f()] * 2
    n = 30
    for i in range(n):
        a = 1 - (i + 1) / n
        lid = max(0.0, min(0.85, (i - 8) / 14))
        frames.append(f(a=a, lid=lid, zf=i if lid > 0.5 else None, look=(2, 1 if lid < 0.4 else 2), bob=1 if lid > 0.7 and i % 6 > 2 else 0))
    for k in range(5):
        frames.append(f(a=0, hot=k % 2 == 0, lid=0.85, zf=k + 40, bob=0))
    frames += [f(a=0, hot=True, lid=0.0, look=(0, 0), bob=1), f(a=0, hot=True, lid=0.0, look=(0, 0)),
               f(a=1.0, hot=False, blink=True)]
    return frames + [f()]


def hg_nap():
    f = lambda **k: lim_frame("5", **k)
    frames = [f()] * 3 + [f(blink=True)] + [f()] * 2
    for i in range(10):
        frames.append(f(a=1 - i * 0.01, lid=0.9 * ease((i + 1) / 10), look=(2, 2)))
    for i in range(20):
        frames.append(f(a=0.9 - i * 0.004, lid=0.9, zf=i, bob=1 if i % 8 > 3 else 0, look=(2, 2)))
    frames += [f(a=0.82, hot=True, lid=0.0, look=(0, 0), bob=1), f(a=0.82, hot=False, lid=0.0, look=(0, 0)),
               f(a=0.82, lid=0.0, look=(1, 1), blink=True)] + [f(a=0.82, look=(2, 1))] * 3
    return frames + [f()]


# ---------------------------------------------------------------- 7d limit: calendar
def calendar(draw, x0, marks):
    R(draw, x0 + 4, 14, 42, 38, (230, 232, 238))
    R(draw, x0 + 4, 14, 42, 8, RED)
    R(draw, x0 + 12, 11, 3, 6, DARK)
    R(draw, x0 + 35, 11, 3, 6, DARK)
    for d in range(21):
        cx, cy = x0 + 8 + (d % 7) * 5, 26 + (d // 7) * 8
        R(draw, cx, cy, 4, 6, RED if d < marks else (190, 194, 205))


def cal_days():
    f = lambda **k: lim_frame("7", **k)
    frames = [f()] * 4 + [f(blink=True)] + [f()] * 2
    for d in range(1, 8):
        lid = min(0.85, d * 0.12)
        frames += [f(marks=d, lid=lid, look=(2, 2 if d > 3 else 1), zf=d * 3 if lid > 0.5 else None)] * 3
    for k in range(5):
        frames.append(f(marks=7, hot=k % 2 == 0, lid=0.85, zf=30 + k))
    frames += [f(marks=7, hot=True, lid=0.0, look=(0, 0), bob=1), f(marks=0, hot=False, lid=0.0, look=(0, 0), bob=1),
               f(marks=0, blink=True)]
    return frames + [f()]


def cal_count():
    f = lambda **k: lim_frame("7", **k)
    frames = [f()] * 3 + [f(blink=True)] + [f()] * 2
    for d in range(1, 8):
        frames += [f(marks=d, look=(0 + (d % 3), 1 + (d // 4)))] * 2
    frames += [f(marks=7, hot=True, look=(2, 2), bob=1)] * 3 + [f(marks=7, lid=0.4, look=(2, 2))] * 4
    for d in range(6, -1, -1):                                               # rewinds, one day per frame
        frames.append(f(marks=d, look=(2, 1), lid=0.0))
    frames += [f(blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- API cost limit: a $ coin feeds a meter that hits the limit
DOLLAR = ["01110", "10101", "10100", "01110", "00101", "10101", "01110"]
COIN_RIM = (200, 140, 30)
METER_X, METER_Y, METER_W, LIMIT_X = 6, 40, 76, 72


def circle(draw, cx, cy, r, color, inner=0.0):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = math.hypot(xx - cx + 0.5, yy - cy + 0.5)
            if inner <= d <= r:
                R(draw, xx, yy, 1, 1, color)


def big_coin(draw, cx, cy):
    circle(draw, cx, cy, 9, COIN_RIM)
    circle(draw, cx, cy, 8, YELLOW)
    for r, row in enumerate(DOLLAR):
        for c, v in enumerate(row):
            if v == "1":
                R(draw, cx - 2 + c, cy - 3 + r, 1, 1, (120, 70, 40))


def no_sign(draw, cx, cy, color=RED):
    circle(draw, cx, cy, 13, color, inner=10.5)
    for i in range(-9, 10):                                                  # slash from top-left to bottom-right
        R(draw, cx + i - 1, cy + i, 3, 1, color)


def cost_frame(level=0.0, flyer=None, hit=0, sweat_f=None, look=(2, 1), blink=False, bob=0, slide=0):
    """hit: 0 none, 1 meter red + coin blocked, 2 same with the meter flashing off."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    big_coin(draw, x0 + 17, 22)
    R(draw, x0 + METER_X, METER_Y, METER_W, 11, EMPTY)
    R(draw, x0 + METER_X + 1, METER_Y + 1, METER_W - 2, 9, DARK)
    fw = round((LIMIT_X - METER_X - 2) * level)
    color = RED if hit else GREEN if level < 0.6 else AMBER if level < 0.85 else RED
    if hit != 2:
        R(draw, x0 + METER_X + 1, METER_Y + 1, fw, 9, color)
    R(draw, x0 + LIMIT_X, METER_Y - 5, 2, 21, WHITE)                           # limit line with a flag
    R(draw, x0 + LIMIT_X + 2, METER_Y - 5, 4, 3, RED)
    if hit:
        no_sign(draw, x0 + 17, 22)
    if flyer:
        fx, fy = flyer
        R(draw, x0 + fx, fy, 7, 4, YELLOW)
        R(draw, x0 + fx, fy + 3, 7, 1, COIN_RIM)
    clawd(draw, look=look, blink=blink, bob=bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def cost_run(steps, stall=None):
    """steps: coin drops; stall: index after which Clawd hesitates before the last drop."""
    frames = [cost_frame()] * 4 + [cost_frame(blink=True)] + [cost_frame()] * 2
    level = 0.0
    for i in range(steps):
        new = (i + 1) / steps
        endx = METER_X + 1 + round((LIMIT_X - METER_X - 2) * new)
        for k in range(5):                                                   # coin drops from the big coin into the meter
            t = (k + 1) / 5
            frames.append(cost_frame(level, flyer=(round(14 + (endx - 14) * t), round(34 + 5 * t - 6 * math.sin(t * math.pi))),
                                     look=(2, 1 + (k > 2)), sweat_f=k if new > 0.7 else None))
        level = new
        frames += [cost_frame(level, look=(2, 2), sweat_f=i if level > 0.7 else None)] * 2
        if stall is not None and i == stall:
            frames += [cost_frame(level, look=(2, 2), sweat_f=k, bob=k % 2) for k in range(6)]
    for k in range(6):                                                       # limit reached: meter flashes red, coin blocked
        frames.append(cost_frame(1.0, hit=1 + k % 2, sweat_f=k, look=(2, 2), bob=k % 2))
    frames += [cost_frame(1.0, hit=1, sweat_f=k, look=(1, 2)) for k in range(8)]
    frames += [cost_frame(1.0, hit=1, blink=True)]
    for k in range(1, 6):                                                    # meter drains again
        frames.append(cost_frame(1.0 - ease(k / 5), look=(2, 1)))
    return frames + [cost_frame()]


# ---------------------------------------------------------------- limit-empty/quarter/half/three-quarters: the gauge level is only approximate
LEVELS = {  # name: (fill colour, filled segments of 7). Empty still shows one line: it has started.
    "empty": (GREEN, 1), "quarter": (GREEN, 2), "half": ((190, 200, 60), 4), "three-quarters": (AMBER, 5),
}


def pct_frame(kind, spark=None, warn=False, sweat_f=None, key=False, glow=None, look=(2, 1), blink=False, bob=0,
              slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    color, segs = LEVELS[kind]
    h = segs * 6
    draw_gauge(draw, x0, 0, color)
    for s in range(7):                                                       # filled segments get a 1 px gap on top
        R(draw, x0 + 8, 54 - (s + 1) * 6 + 1, 16, 5, color if s < segs else (22, 26, 36))
    draw_bars(draw, x0, bars_for(h), shimmer=glow)
    if spark is not None:                                                    # fresh-start sparkles
        for k, (sx, sy) in enumerate(((30, 12), (34, 44), (28, 28))):
            if (spark + k * 3) % 8 < 4:
                R(draw, x0 + sx, sy, 1, 3, WHITE)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, WHITE)
    if warn:
        warn_tri(draw, x0 + 75, 7, AMBER)
    clawd(draw, look=look, blink=blink, bob=bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def pct_loop_a(kind):
    f = lambda **k: pct_frame(kind, **k)
    busy, nervous = kind in ("half", "three-quarters"), kind == "three-quarters"
    frames = [f()] * 4 + [f(blink=True)] + [f()] * 2
    for n in range(3):                                                       # three tokens flow into the context
        for k in range(8):
            frames.append(f(spark=k + n * 8 if kind == "empty" else None, glow=k,
                            look=(2, 1 + (k > 3)), key=busy and k % 3 == 0, bob=1 if busy and k % 3 == 0 else 0,
                            sweat_f=k + n if nervous else None, warn=nervous and k % 4 < 2))
        frames += [f(look=(2, 2), sweat_f=n if nervous else None)] * 2
    return frames + [f(blink=True)] + [f()]


def pct_loop_b(kind):
    f = lambda **k: pct_frame(kind, **k)
    busy, nervous = kind in ("half", "three-quarters"), kind == "three-quarters"
    frames = [f()] * 3 + [f(blink=True)] + [f()] * 2
    for n in range(2):
        for look in ((2, 0), (2, 0), (0, 1), (0, 1), (2, 1), (2, 2), (2, 2), (2, 1)):  # glances up at the gauge and around
            i = len(frames)
            frames += [f(look=look, spark=i if kind == "empty" else None, glow=i,
                         sweat_f=i if nervous else None, warn=nervous and i % 6 < 3,
                         key=busy and i % 4 == 0, bob=1 if busy and i % 4 == 0 else 0)] * 2
    return frames + [f(blink=True)] + [f()]


if __name__ == "__main__":
    finish("context", ctx_frame, [ctx_gauge, ctx_pile])
    finish("limit-5h", lambda **k: lim_frame("5", **k), [hg_run, hg_nap])
    finish("limit-7d", lambda **k: lim_frame("7", **k), [cal_days, cal_count])
    for kind in LEVELS:
        finish(f"context-{kind}", lambda p=kind, **k: pct_frame(p, **k), [lambda p=kind: pct_loop_a(p), lambda p=kind: pct_loop_b(p)])
    finish("limit-api-cost", cost_frame, [lambda: cost_run(6), lambda: cost_run(3, stall=1)])
