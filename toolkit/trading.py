"""Worked example, a bigger set: Clawd watches candles, buys the dip, sells the top and counts coins.

Run: python trading.py  -> ../mine/trading/
Seam = the panel with an empty chart. Every take fills it and empties it again.
"""
import random

from clawd_core import *

TPANEL = (14, 18, 26)
TBAR = (40, 44, 54)
GRID_C = (30, 35, 47)
GREEN_DIM = (22, 62, 42)
COIN_IN = (200, 140, 30)

CH = 36  # chart height in px
CX0_OFF, CY1 = 4, 53  # chart left inset from the panel, bottom y
STEP = 6  # candle pitch
N = 13  # candles per chart


def series(rng, n, start, drift, vol):
    """Random walk of (open, close, high, low) heights above the chart floor."""
    out, p = [], start
    for _ in range(n):
        c = max(2, min(CH - 4, p + drift + rng.uniform(-vol, vol)))
        out.append((p, c, min(CH - 1, max(p, c) + rng.randint(0, 3)), max(0, min(p, c) - rng.randint(0, 3))))
        p = c
    return out


def coin(draw, x, y):
    draw.rectangle([x + 1, y, x + 4, y + 5], fill=YELLOW)
    draw.rectangle([x, y + 1, x + 5, y + 4], fill=YELLOW)
    draw.rectangle([x + 2, y + 2, x + 3, y + 3], fill=COIN_IN)


def draw_panel(draw, x0, x1, up):
    draw.rectangle([x0 - 2, PY0 - 2, x1 + 2, PY1 + 2], fill=PANEL_EDGE)
    draw.rectangle([x0, PY0, x1, PY1], fill=TPANEL)
    draw.rectangle([x0, PY0, x1, PY0 + 7], fill=TBAR)
    draw.rectangle([x0 + 3, PY0 + 2, x0 + 6, PY0 + 5], fill=YELLOW)  # ticker coin
    draw.rectangle([x0 + 9, PY0 + 3, x0 + 18, PY0 + 4], fill=COMMENT)
    draw.rectangle([x0 + 21, PY0 + 3, x0 + 26, PY0 + 4], fill=COMMENT)
    color = COMMENT if up is None else GREEN if up else RED
    draw.rectangle([x1 - 16, PY0 + 2, x1 - 3, PY0 + 5], fill=color)  # price
    for gy in (CY1 - 12, CY1 - 24, CY1 - 36):
        draw.rectangle([x0 + 2, gy, x1 - 2, gy], fill=GRID_C)


def candle_x(x0, i):
    return x0 + CX0_OFF + i * STEP


def draw_candles(draw, x0, candles):
    for i, (o, c, hi, lo) in enumerate(candles):
        x = candle_x(x0, i)
        color = GREEN if c >= o else RED
        draw.rectangle([x + 1, CY1 - hi, x + 1, CY1 - lo], fill=color)
        top, bot = CY1 - round(max(o, c)), CY1 - round(min(o, c))
        draw.rectangle([x, top, x + 2, max(top, bot)], fill=color)


def draw_mark(draw, x0, candles, i, kind):
    x = candle_x(x0, i) + 1
    hi, lo = candles[i][2], candles[i][3]
    if kind == "buy":  # green arrow under the low
        y = CY1 - lo + 2
        draw.rectangle([x, y, x, y], fill=GREEN)
        draw.rectangle([x - 1, y + 1, x + 1, y + 1], fill=GREEN)
        draw.rectangle([x - 2, y + 2, x + 2, y + 2], fill=GREEN)
    else:  # red arrow over the high
        y = CY1 - hi - 4
        draw.rectangle([x - 2, y, x + 2, y], fill=RED)
        draw.rectangle([x - 1, y + 1, x + 1, y + 1], fill=RED)
        draw.rectangle([x, y + 2, x, y + 2], fill=RED)


def draw_line(draw, x0, pts):
    prev = None
    for i, v in enumerate(pts):
        x, y = candle_x(x0, i) + 1, CY1 - round(v)
        draw.rectangle([x, y, x, CY1], fill=GREEN_DIM)
        if prev:  # connect with a vertical run so the line stays solid
            lo, hi = sorted((prev[1], y))
            for xx in range(prev[0] + 1, x + 1):
                t = (xx - prev[0]) / (x - prev[0])
                yy = round(prev[1] + (y - prev[1]) * t)
                draw.rectangle([xx, yy, xx, CY1], fill=GREEN_DIM)
                draw.rectangle([xx, yy, xx, yy], fill=GREEN)
        prev = (x, y)


def draw_stack(draw, n):
    for k in range(n):
        y = OY + 8 * G - 3 - k * 3
        draw.rectangle([80, y, 88, y + 2], fill=YELLOW)
        draw.rectangle([80, y + 2, 88, y + 2], fill=COIN_IN)


def eye_y(v):
    return 0 if v > 24 else 1 if v > 14 else 2


def tframe(candles=(), marks=(), line=None, floater=None, stack=0, look=(2, 1), bob=0, key=False, blink=False, slide=0):
    img, draw = new_frame()
    x0, x1 = PX0 + slide, PX1 + slide
    shown = list(candles)
    up = None
    if shown:
        up = shown[-1][1] >= shown[0][0]
    elif line:
        up = True
    draw_panel(draw, x0, x1, up)
    if line:
        draw_line(draw, x0, line)
    draw_candles(draw, x0, shown)
    for i, kind in marks:
        if i < len(shown):
            draw_mark(draw, x0, shown, i, kind)
    if stack:
        draw_stack(draw, stack)
    if floater:
        coin(draw, *floater)
    clawd(draw, look=look, bob=bob, blink=blink)
    if key:
        hx, hy = OX + 10 * G + 2, OY + 2 * G + bob
        draw.rectangle([hx, hy - 3, hx + 1, hy - 2], fill=YELLOW)
        draw.rectangle([hx + 3, hy + 1, hx + 4, hy + 2], fill=YELLOW)
    return img


def idle(n):
    return [tframe(blink=f == n - 2 and n > 4) for f in range(n)]


def build(cs, per=2, marks=(), pause=None, **kw):
    """Candles appear one by one. pause = {index: frames} presses a key after that candle."""
    frames = []
    for i in range(1, len(cs) + 1):
        look = (2, eye_y(cs[i - 1][1]))
        frames += [tframe(cs[:i], marks, look=look, **kw)] * per
        for f in range((pause or {}).get(i - 1, 0)):
            frames.append(tframe(cs[:i], marks, look=look, bob=f % 2, key=f % 2 == 0, **kw))
    return frames


def clear(cs, marks=(), steps=4):
    """Wipes the chart right to left and ends on the empty seam frame."""
    frames = []
    for k in range(1, steps + 1):
        frames.append(tframe(cs[:max(0, len(cs) - round(len(cs) * k / steps))], marks, look=(2, 1)))
    return frames


def trade_rise():
    cs = series(random.Random(5), N, 8, 1.9, 3.2)
    frames = idle(4) + build(cs)
    frames += [tframe(cs, look=(2, 0), blink=f == 4) for f in range(8)]
    return frames + clear(cs)


def trade_buy():
    rng = random.Random(11)
    cs = series(rng, 7, 26, -3.0, 2.0) + series(rng, 6, 7, 3.4, 2.2)
    cs[7] = (cs[6][1], cs[7][1], cs[7][2], cs[7][3])
    marks = [(6, "buy")]
    frames = idle(3) + build(cs[:7], 2, pause={6: 4})
    frames += build_from(cs, 7, marks)
    frames += [tframe(cs, marks, look=(2, 0), blink=f == 5) for f in range(7)]
    return frames + clear(cs, marks)


def build_from(cs, start, marks):
    frames = []
    for i in range(start + 1, len(cs) + 1):
        frames += [tframe(cs[:i], marks, look=(2, eye_y(cs[i - 1][1])))] * 2
    return frames


def trade_sell():
    rng = random.Random(21)
    cs = series(rng, 8, 6, 3.4, 2.0) + series(rng, 5, 30, -2.6, 2.0)
    marks = [(7, "sell")]
    frames = idle(3) + build(cs[:8], 2, pause={7: 4})
    pos = lambda f: (80, round(44 - 28 * ease(min(1, f / 12))))  # coin floats up beside Clawd
    for i in range(9, len(cs) + 1):
        for f in range(2):
            n = len(frames)
            frames.append(tframe(cs[:i], marks, look=(2, eye_y(cs[i - 1][1])), floater=pos((i - 9) * 2 + f)))
    for f in range(8):
        frames.append(tframe(cs, marks, look=(2, 2), floater=pos(10 + f), blink=f == 6))
    return frames + clear(cs, marks)


def trade_portfolio():
    rng = random.Random(33)
    pts, v = [], 5
    for i in range(N):
        v = min(CH - 5, v + rng.uniform(-1.5, 4.2))
        pts.append(v)
    pts[-1] = max(pts[-1], pts[-2] + 2)
    frames = idle(3)
    for i in range(1, N + 1):
        stack = i * 4 // N
        frames += [tframe(line=pts[:i], stack=stack, look=(2, eye_y(pts[i - 1])))] * 2
    frames += [tframe(line=pts, stack=4, look=(2, 0), blink=f == 5, bob=0) for f in range(8)]
    for k in range(1, 5):  # chart empties, then the coins drop away
        keep = max(0, N - round(N * k / 4))
        frames.append(tframe(line=pts[:keep] or None, stack=4 if k < 3 else 4 - (k - 2) * 2, look=(2, 1)))
    return frames


def slide(n, reverse):
    out = []
    for i in range(n):
        t = ease((i + 1) / n) if not reverse else 1 - ease(i / (n - 1))
        out.append(tframe(look=(round(2 * t), round(t)), slide=round((1 - t) * (W - PX0 + 4))))
    return out


TAKES = [trade_rise, trade_buy, trade_sell, trade_portfolio]


if __name__ == "__main__":
    save_set("trading", lambda: slide(ENTER, False), TAKES, lambda: slide(EXIT, True))
