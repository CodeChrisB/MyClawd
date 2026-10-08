"""Six sets for everyday dev work: debug, merge-conflict, lint, security, benchmark, api-request.

python dev_sets.py  ->  ../mine/{debug,merge-conflict,lint,security,benchmark,api-request}/
Seam pose = the panel at rest (a calm code file, a stopwatch at 12, an idle server rack), see clawd.md.
"""
import math

from props import *

KEY, FUNC, STR, PUNCT, LB = (198, 120, 221), (229, 192, 123), (152, 195, 121), (171, 178, 191), LIGHT_BLUE
PANEL_BG = (24, 26, 38)
CODE = [
    [(0, 12, KEY), (16, 18, FUNC)],
    [(6, 20, LB), (30, 24, STR)],
    [(6, 14, KEY), (24, 26, PUNCT), (56, 10, LB)],
    [(6, 30, FUNC), (40, 16, STR)],
    [(0, 8, PUNCT)],
]
PITCH, TOP = 9, 12
HOT_BG, OK_BG, STEP_BG = (70, 32, 40), (30, 60, 44), (44, 50, 74)


def base(slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide)
    return img, draw, x0


def rows(draw, x0, lines=CODE, bg=None, off=None, fade=None, top=TOP, pitch=PITCH):
    """Code lines on the panel. bg = {row: colour}, off = {row: dx px}, fade = {row: 0..1 towards the panel colour}."""
    for i, line in enumerate(lines):
        y = top + i * pitch
        if bg and i in bg:
            R(draw, x0 + 1, y - 2, 87, pitch - 1, bg[i])
        R(draw, x0 + 3, y + 1, 2, 2, mix(COMMENT, PANEL_BG, 0.4))
        for indent, w, color in line:
            c = mix(color, PANEL_BG, fade[i]) if fade and i in fade else color
            R(draw, x0 + 10 + indent + (off or {}).get(i, 0), y, w, 4, c)


def puff(draw, cx, cy, r, color=WHITE):
    for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)):
        R(draw, cx + round(ax * r), cy + round(ay * r), 2, 2, color)


def smile(draw, bob=0):
    draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)


def hold(frame, n, **kw):
    return [frame(**kw) for _ in range(n)]


# ---------------------------------------------------------------- debug: a bug on line 3, magnifier, fix; or step through


def bug(draw, x, y, phase=0, up=False):
    body = (210, 70, 70)
    R(draw, x + 1, y + 1, 7, 4, body)
    R(draw, x + 4, y + 1, 1, 4, DARK)
    R(draw, x + 8, y + 2, 2, 2, (240, 240, 245))
    R(draw, x + 9, y, 1, 1, WHITE)
    for i in (2, 4, 6):
        r = (phase + i // 2) % 2
        R(draw, x + i, y - 1 - r if up else y + 5, 1, 1 + r if up else 1 + r, (200, 204, 214))


def debug_frame(bug_at=None, phase=0, up=False, flag=None, fixed=None, ring=None, bp=None, step=None, val=None, pf=None,
                look=(2, 1), blink=False, bob=0, grin=False, slide=0):
    img, draw, x0 = base(slide)
    bg = {}
    for r, c in ((flag, HOT_BG), (fixed, OK_BG), (step, STEP_BG)):
        if r is not None:
            bg[r] = c
    rows(draw, x0, bg=bg)
    if bp is not None:
        dot(draw, x0 + 4, TOP + bp * PITCH + 2, 2, RED)
    if step is not None:
        y = TOP + step * PITCH
        R(draw, x0 + 2, y, 1, 5, YELLOW)
        R(draw, x0 + 3, y + 1, 1, 3, YELLOW)
        R(draw, x0 + 4, y + 2, 1, 1, YELLOW)
    if fixed is not None:
        tick(draw, x0 + 78, TOP + fixed * PITCH - 1, GREEN)
    if val is not None:
        y = TOP + val * PITCH
        R(draw, x0 + 62, y - 3, 20, 10, (60, 70, 100))
        text(draw, x0 + 64, y - 1, "5", WHITE, 1)
        R(draw, x0 + 69, y + 2, 10, 1, (190, 196, 210))
    if bug_at is not None:
        bug(draw, x0 + bug_at, TOP + 2 * PITCH - 1, phase, up)
    if ring is not None:
        cx, cy = x0 + ring, TOP + 2 * PITCH + 2
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=WHITE, width=2)
        for k in range(4):
            R(draw, cx + 6 + k, cy + 6 + k, 2, 2, (190, 196, 210))
    if pf:
        puff(draw, x0 + 38, TOP + 2 * PITCH + 2, pf, WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    if grin:
        smile(draw, bob)
    return img


def debug_hunt():
    f = debug_frame
    frames = hold(f, 3)
    for i in range(14):
        frames.append(f(bug_at=2 + i * 3, phase=i, look=(2, 1 + (i > 6))))
    frames += [f(bug_at=44, phase=i, flag=2, look=(2, 2)) for i in range(2)]
    for i in range(4):
        frames.append(f(bug_at=44, phase=i, flag=2, ring=84 - i * 10, look=(2, 2)))
    for i in range(5):
        frames.append(f(bug_at=44, phase=i, flag=2, ring=54, look=(2, 2), bob=-1 if i == 0 else 0))
    frames += [f(bug_at=44, up=True, phase=i, flag=2, look=(2, 2)) for i in range(2)]
    frames += [f(flag=2, pf=3, look=(2, 2)), f(fixed=2, pf=7, look=(2, 1))]
    frames += [f(fixed=2, grin=True, bob=-1 if i == 0 else 0) for i in range(5)]
    return frames + [f(blink=True)] + hold(f, 1)


def debug_step():
    f = debug_frame
    frames = hold(f, 3)
    frames += [f(bp=3), f(bp=3, look=(2, 2)), f(bp=3)]
    for s in range(4):
        frames += hold(f, 3, bp=3, step=s, look=(2, (0, 1, 1, 2)[s]))
    frames += hold(f, 6, bp=3, step=3, val=3, look=(2, 2))
    frames += [f(bp=3, step=3, val=3, look=(2, 2), bob=-1), f(bp=3, step=4, look=(2, 2)), f(bp=3, step=4, look=(2, 2))]
    frames += [f(bp=3, look=(2, 1)), f(look=(2, 1), blink=True)] + hold(f, 1)
    return frames


# ---------------------------------------------------------------- merge-conflict


SEAM6 = CODE + [[(0, 16, KEY), (20, 14, FUNC)]]
THEIRS = [(6, 12, LB), (22, 30, STR)]
BAND, DIV = (140, 48, 60), (80, 84, 96)
MY, TY = 12, 8   # first row y, pitch


def merge_frame(c=0.0, r=0.0, pick=None, chip=None, cur=None, tweak=0.0, look=(2, 1), blink=False, bob=0, slide=0, key=False):
    """c: conflict markers fade in, r: resolve progress, pick: 'ours' or 'theirs'."""
    img, draw, x0 = base(slide)

    def row(i, y=None):
        return (MY + i * TY) if y is None else y

    def segs(y, line, color_fade=0.0, w=1.0):
        for indent, wd, col in line:
            R(draw, x0 + 10 + round(indent * w), y, max(1, round(wd * w)), 4, mix(col, PANEL_BG, color_fade))

    R(draw, x0 + 3, MY + 1, 2, 2, mix(COMMENT, PANEL_BG, .4))
    segs(MY, SEAM6[0])
    if c == 0 and r == 0:  # at rest: the plain file
        for i in range(1, 6):
            R(draw, x0 + 3, row(i) + 1, 2, 2, mix(COMMENT, PANEL_BG, .4))
            segs(row(i), SEAM6[i])
    else:
        shown = min(c, 1.0)
        keep = 1 - r
        mixbg = lambda col, k: mix(PANEL_BG, col, k)
        for i, col in ((1, BAND), (3, DIV), (5, BAND)):
            if keep > 0:
                R(draw, x0 + 1, row(i) - 1, round(87 * keep), 6, mixbg(col, shown))
                if shown >= .5:
                    for k in range(3):
                        R(draw, x0 + 5 + k * 3, row(i) + 1, 2, 2, (235, 190, 195))
        ours_y = row(2) - round((row(2) - row(1)) * r) if pick == 'ours' else row(2)
        theirs_y = row(4) - round((row(4) - row(1)) * r) if pick == 'theirs' else row(4)
        if pick != 'theirs' or keep > .4:
            R(draw, x0 + 1, ours_y - 1, 87 if pick != 'theirs' else round(87 * keep), 6, mixbg((28, 48, 92), shown if pick != 'ours' else 1))
            segs(ours_y, SEAM6[1], 0.0 if shown >= .5 else 1.0, keep if pick == 'theirs' else 1.0)
        if pick != 'ours' or keep > .4:
            R(draw, x0 + 1, theirs_y - 1, 87 if pick != 'ours' else round(87 * keep), 6, mixbg((88, 52, 28), shown if pick != 'theirs' else 1 - tweak))
            if pick == 'theirs' and tweak:
                segs(theirs_y, [(a, mix_i(b, w2, tweak), mix(col, col2, tweak)) for (a, b, col), (_, w2, col2) in zip(THEIRS, SEAM6[1][:2])] if False else THEIRS)
                segs(theirs_y, SEAM6[1], 1 - tweak)
            else:
                segs(theirs_y, THEIRS, 0.0 if shown >= .5 else 1.0, keep if pick == 'ours' else 1.0)
        for i in range(2, 6):
            if r:
                R(draw, x0 + 3, row(i) + 1, 2, 2, mix(COMMENT, PANEL_BG, .4 + .6 * (1 - r)))
                segs(row(i), SEAM6[i], 1 - r)
    if chip is not None:
        for k, col in enumerate(((60, 110, 200), (200, 120, 50))):
            lit = chip == k
            R(draw, x0 + 38 + k * 25, 7, 22, 5, mix(col, WHITE, .5) if lit else col)
            R(draw, x0 + 41 + k * 25, 9, 14, 1, WHITE)
    if cur is not None:
        cursor(draw, x0 + cur[0], cur[1])
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def merge_take(pick):
    f = merge_frame
    k = 0 if pick == 'ours' else 1
    frames = hold(f, 3)
    frames += [f(c=.4, look=(2, 0)), f(c=.7, look=(2, 0), bob=-1), f(c=1.0, look=(2, 0))]
    for i in range(8):  # compares the two sides
        frames.append(f(c=1.0, look=(2, 1 + (i // 2) % 2 * (1 if i < 4 else 0) if i < 4 else 2 - (i // 2) % 2)))
    frames += [f(c=1.0, chip=k, look=(2, 0))] * 2
    for i in range(5):  # cursor to the chip
        t = ease((i + 1) / 5)
        frames.append(f(c=1.0, chip=k, cur=(round(44 + (30 + k * 25 - 44) * t), round(40 - 29 * t)), look=(2, 0)))
    frames += [f(c=1.0, chip=k, cur=(30 + k * 25, 11), look=(2, 0), bob=1)] * 2
    steps = 4
    for i in range(steps):
        r = ease((i + 1) / steps)
        frames.append(f(c=1.0, r=r, pick=pick, look=(2, 1)))
    if pick == 'theirs':
        for i in range(3):  # fixes the last bits by hand
            frames.append(f(c=1.0, r=1.0, pick=pick, tweak=(i + 1) / 3, key=i % 2 == 0, bob=1 if i % 2 == 0 else 0, look=(2, 2)))
    frames += [f(look=(2, 1), blink=True)] + hold(f, 1)
    return frames


# ---------------------------------------------------------------- lint: format a messy file, or clear the warnings


def squiggle(draw, x, y, w, color):
    for i in range(0, w, 2):
        R(draw, x + i, y + (i // 2) % 2, 2, 1, color)


def badge(draw, x0, n, ok=False):
    R(draw, x0 + 74, 6, 13, 9, GREEN if ok else RED)
    if ok:
        tick(draw, x0 + 77, 8, WHITE)
    else:
        text(draw, x0 + 79, 8, str(n), WHITE, 1)


def lint_frame(off=None, squig=(), count=None, ok=False, sweep=None, look=(2, 1), blink=False, bob=0, grin=False, slide=0, key=False):
    img, draw, x0 = base(slide)
    rows(draw, x0, off=off)
    for r, color in squig:
        y = TOP + r * PITCH
        squiggle(draw, x0 + 10, y + 5, sum(w for _, w, _ in CODE[r]) // 2 + 14 + (CODE[r][-1][0] // 2), color)
    if count is not None:
        badge(draw, x0, count, ok)
    if sweep is not None:
        R(draw, x0 + 1, sweep, 87, 2, (150, 200, 250))
        R(draw, x0 + 1, sweep - 3, 87, 3, (60, 90, 130))
    clawd(draw, look=look, blink=blink, bob=bob)
    if grin:
        smile(draw, bob)
    if key:
        key_press(draw, bob)
    return img


MESS = {0: 0, 1: 7, 2: 3, 3: 10, 4: 5}


def lint_format():
    f = lint_frame
    frames = hold(f, 3)
    frames += [f(off={k: v // 2 for k, v in MESS.items()}, look=(2, 0)), f(off=MESS, look=(2, 0), bob=-1)]
    frames += hold(f, 3, off=MESS, look=(2, 2))
    for i in range(10):
        sy = 8 + i * 5
        off = {k: (0 if TOP + k * PITCH + 2 < sy else v) for k, v in MESS.items()}
        frames.append(f(off=off, sweep=sy if sy < 56 else None, look=(2, min(2, i // 3)), bob=1 if i % 2 else 0))
    frames += [f(count=0, ok=True, grin=True, bob=-1 if i == 0 else 0) for i in range(5)]
    return frames + [f(blink=True)] + hold(f, 1)


def lint_clear():
    f = lint_frame
    marks = [(1, RED), (2, YELLOW), (3, RED)]
    frames = hold(f, 3)
    for n in range(1, 4):
        frames += hold(f, 2, squig=marks[:n], count=n, look=(2, n - 1 if n < 3 else 2))
    frames += hold(f, 3, squig=marks, count=3, look=(2, 1))
    for n in (3, 2, 1):
        left = marks[:n - 1] if n == 3 else marks[: n - 1]
        left = [m for m in marks if m[0] != (3, 2, 1)[3 - n]] if False else marks[: n - 1]
        frames += [f(squig=marks[:n], count=n, key=True, bob=1, look=(2, n - 1 if n < 3 else 2))] + hold(f, 2, squig=left, count=n - 1, look=(2, 1))
    frames += [f(count=0, ok=True, grin=True, bob=-1)] + hold(f, 4, count=0, ok=True, grin=True)
    return frames + [f(blink=True)] + hold(f, 1)


# ---------------------------------------------------------------- security: scan for a leaked key, audit the packages


def shield(draw, x, y, state):
    fill = {'idle': (36, 40, 52), 'alert': RED, 'ok': GREEN}[state]
    for i, w in enumerate((13, 13, 13, 13, 11, 9, 7, 5, 3)):
        R(draw, x + (13 - w) // 2, y + i, w, 1, fill)
    R(draw, x, y, 13, 1, COMMENT if state == 'idle' else WHITE)
    if state == 'ok':
        tick(draw, x + 4, y + 3, WHITE)
    if state == 'alert':
        R(draw, x + 6, y + 2, 1, 4, WHITE)
        R(draw, x + 6, y + 7, 1, 1, WHITE)


def sec_frame(beam=None, secret=False, mask=0.0, sh='idle', dots=None, flag=False, look=(2, 1), blink=False, bob=0, slide=0, grin=False):
    img, draw, x0 = base(slide)
    lines = [list(l) for l in CODE]
    if secret:
        lines[2] = [lines[2][0], (24, 50, YELLOW)]
    rows(draw, x0, lines, bg={2: HOT_BG} if flag else None)
    if mask:
        R(draw, x0 + 10 + 24, TOP + 2 * PITCH - 1, 50, 6, HOT_BG if flag else PANEL_BG)
        for k in range(round(9 * mask)):
            R(draw, x0 + 10 + 26 + k * 5, TOP + 2 * PITCH + 1, 3, 3, COMMENT)
    if dots:
        for i, c in enumerate(dots):
            if c:
                dot(draw, x0 + 4, TOP + i * PITCH + 2, 2, c)
    if beam is not None:
        R(draw, x0 + beam - 5, 8, 5, 48, (36, 60, 90))
        R(draw, x0 + beam, 8, 2, 48, (120, 200, 255))
    shield(draw, x0 + 73, 42, sh)
    clawd(draw, look=look, blink=blink, bob=bob)
    if grin:
        smile(draw, bob)
    return img


def sec_scan():
    f = sec_frame
    frames = hold(f, 3)
    for i in range(15):
        bx = 4 + i * 5
        hit = bx >= 56
        frames.append(f(beam=bx, secret=hit, flag=hit, sh='alert' if hit else 'idle', look=(2, min(2, i // 5)), bob=-1 if i == 11 else 0))
    frames += hold(f, 3, secret=True, flag=True, sh='alert', look=(2, 2))
    for i in range(4):
        frames.append(f(secret=True, flag=i < 2, mask=(i + 1) / 4, sh='alert' if i < 3 else 'ok', look=(2, 2)))
    frames += hold(f, 4, mask=1.0, sh='ok', grin=True, look=(2, 1))
    frames += [f(sh='ok', grin=True)] + [f(sh='idle')] + [f(blink=True)] + hold(f, 1)
    return frames


def sec_audit():
    f = sec_frame
    frames = hold(f, 3)
    state = [None] * 5
    for i in range(5):
        for j in range(2):
            d = list(state)
            d[i] = GREY if j == 0 else (AMBER if i == 3 else GREEN)
            frames.append(f(dots=d, look=(2, min(2, i // 2))))
        state[i] = AMBER if i == 3 else GREEN
        if i == 3:  # one package is outdated and gets updated
            frames += hold(f, 2, dots=list(state), look=(2, 2), bob=-1)
            state[3] = GREEN
            frames += hold(f, 2, dots=list(state), look=(2, 2), bob=1)
    frames += hold(f, 4, dots=state, sh='ok', grin=True)
    frames += [f(sh='ok', grin=True, dots=[None] * 5), f(sh='idle'), f(blink=True)] + hold(f, 1)
    return frames


# ---------------------------------------------------------------- benchmark: stopwatch + bars, flame graph


SW = (20, 34)
TRACK = (36, 40, 52)
FLAME_BASE = 54


def stopwatch(draw, x0, deg):
    cx, cy = x0 + SW[0], SW[1]
    dot(draw, cx, cy, 13, (150, 154, 168))
    dot(draw, cx, cy, 11, (30, 34, 46))
    R(draw, cx - 2, cy - 17, 5, 3, (150, 154, 168))
    for k in range(12):
        a = math.radians(k * 30)
        R(draw, cx + round(math.sin(a) * 10), cy - round(math.cos(a) * 10), 1, 1, COMMENT)
    a = math.radians(deg)
    for s in range(1, 10):
        R(draw, cx + round(math.sin(a) * s), cy - round(math.cos(a) * s), 1, 1, WHITE)
    R(draw, cx, cy, 2, 2, RED)


def bench_frame(deg=0, bars=(0, 0), flame=(0, 0, 0), hot=None, ok=False, look=(2, 1), blink=False, bob=0, slide=0, grin=False):
    img, draw, x0 = base(slide)
    stopwatch(draw, x0, deg)
    for i, (n, col) in enumerate(zip(bars, (ORANGE, GREEN))):
        y = 20 + i * 12
        R(draw, x0 + 40, y, 44, 6, TRACK)
        R(draw, x0 + 40, y, round(n), 6, col)
    if any(flame):
        w1, w2, w3 = flame
        if w1:
            R(draw, x0 + 40, FLAME_BASE - 6, round(44 * w1), 6, (200, 110, 70))
        if w2:
            R(draw, x0 + 40, FLAME_BASE - 14, round(20 * w2), 6, (220, 150, 70))
            hot_c = (GREEN if ok else (RED if hot else (220, 130, 60)))
            R(draw, x0 + 62, FLAME_BASE - 14, round((22 if not ok else 10) * w2), 6, hot_c)
        if w3:
            R(draw, x0 + 40, FLAME_BASE - 22, round(10 * w3), 6, (230, 190, 80))
            R(draw, x0 + 52, FLAME_BASE - 22, round(6 * w3), 6, (230, 170, 70))
            R(draw, x0 + 62, FLAME_BASE - 22, round((14 if not ok else 6) * w3), 6, (240, 90, 80) if hot and not ok else ((GREEN) if ok else (230, 190, 80)))
    if ok:
        tick(draw, x0 + 74, 8, GREEN, 2)
    clawd(draw, look=look, blink=blink, bob=bob)
    if grin:
        smile(draw, bob)
    return img


def bench_compare():
    f = bench_frame
    frames = hold(f, 3)
    for i in range(18):
        frames.append(f(deg=(i + 1) * 20 % 360, bars=((i + 1) / 18 * 40, 0), look=(2, 1)))
    frames += hold(f, 2, bars=(40, 0), look=(2, 2), bob=0)
    for i in range(9):
        frames.append(f(deg=(i + 1) * 40 % 360, bars=(40, (i + 1) / 9 * 18), look=(2, 2 if i < 6 else 1)))
    frames += hold(f, 5, bars=(40, 18), grin=True, look=(2, 1), bob=0)
    frames += [f(bars=(40, 18), grin=True, bob=-1)] + hold(f, 2, bars=(20, 9), look=(2, 1))
    return frames + [f(blink=True)] + hold(f, 1)


def bench_flame():
    f = bench_frame
    frames = hold(f, 3)
    for k in range(3):
        for j in range(2):
            fl = [1.0 if i < k else (0.5 if i == k and j == 0 else (1.0 if i == k else 0)) for i in range(3)]
            frames.append(f(flame=tuple(fl), look=(2, 2 - k)))
    for i in range(6):
        frames.append(f(flame=(1, 1, 1), hot=i % 2 == 0, look=(2, 1 + (i % 2))))
    frames += hold(f, 2, flame=(1, 1, 1), hot=True, look=(2, 1), bob=-1)
    frames += hold(f, 4, flame=(1, 1, 1), ok=True, grin=True)
    for k in (2, 1, 0):
        fl = [1.0 if i < k else 0 for i in range(3)]
        frames.append(f(flame=tuple(fl), ok=True, grin=k > 0))
    return frames + [f(blink=True)] + hold(f, 1)


# ---------------------------------------------------------------- api-request: 200, 404, 500


def envelope(draw, x, y, color):
    R(draw, x, y, 9, 6, color)
    R(draw, x + 1, y + 1, 1, 1, DARK)
    R(draw, x + 2, y + 2, 1, 1, DARK)
    R(draw, x + 3, y + 3, 3, 1, DARK)
    R(draw, x + 6, y + 2, 1, 1, DARK)
    R(draw, x + 7, y + 1, 1, 1, DARK)


def api_frame(req=None, res=None, rcolor=GREEN, led=GREY, chip=None, smoke=0, shake=0, q=False, look=(2, 1), blink=False, bob=0,
              slide=0, grin=False, sweating=False, f=0):
    img, draw, x0 = base(slide)
    R(draw, x0 + 6, 33, 58, 1, GREY)                                          # the line between client and server
    R(draw, x0 + 66, 14, 18, 40, (90, 94, 108))                                # server rack
    for i in range(3):
        R(draw, x0 + 68, 17 + i * 12, 14, 9, (60, 64, 78))
        R(draw, x0 + 79, 20 + i * 12, 2, 2, led if i == 0 else GREY)
    if req is not None:
        envelope(draw, x0 + req, 29, YELLOW)
    if res is not None:
        envelope(draw, x0 + res, 29, rcolor)
    for k in range(smoke):
        R(draw, x0 + 70 + k * 3, 10 - k * 2 - (f % 3), 4 + k % 2, 3, (170, 174, 186))
    if chip:
        label, col = chip
        cx = x0 + 12 + shake
        R(draw, cx, 38, 30, 14, col)
        text(draw, cx + 3, 41, label, WHITE, 2)
    clawd(draw, look=look, blink=blink, bob=bob)
    if grin:
        smile(draw, bob)
    if q:
        text(draw, OX + 8 * G + 6, 6, "?", YELLOW, 2)
    if sweating:
        sweat(draw, bob, f)
    return img


def api_take(code):
    f = api_frame
    col, label = {200: (GREEN, "200"), 404: (AMBER, "404"), 500: (RED, "500")}[code]
    frames = hold(f, 3)
    for i in range(7):
        frames.append(f(req=8 + round(ease((i + 1) / 7) * 48), look=(2, 1), bob=1 if i == 0 else 0))
    led = col
    frames += [f(led=led, look=(2, 1)), f(led=GREY, look=(2, 1)), f(led=led, look=(2, 1))]
    for i in range(7):
        frames.append(f(res=56 - round(ease((i + 1) / 7) * 48), rcolor=col, led=led, smoke=2 if code == 500 else 0, f=i))
    for i in range(10):
        extra = {}
        if code == 200:
            extra = dict(grin=True, bob=-1 if i < 2 else 0, look=(2, 1))
        elif code == 404:
            extra = dict(q=i > 1, look=(1 - (i // 2) % 2 * 2 + 1, 1), bob=0)
        else:
            extra = dict(smoke=3 + i % 2, sweating=True, shake=1 if i % 2 else -1, look=(2, 0), bob=0)
        frames.append(f(chip=(label, col), led=led, f=i, **extra))
    frames += [f(chip=(label, col), led=led, look=(2, 1))] if code != 200 else []
    frames += [f(led=GREY, blink=True)] + hold(f, 1)
    return frames


if __name__ == "__main__":
    finish("debug", debug_frame, [debug_hunt, debug_step])
    finish("merge-conflict", merge_frame, [lambda: merge_take('ours'), lambda: merge_take('theirs')])
    finish("lint", lint_frame, [lint_format, lint_clear])
    finish("security", sec_frame, [sec_scan, sec_audit])
    finish("benchmark", bench_frame, [bench_compare, bench_flame])
    finish("api-request", api_frame, [lambda: api_take(200), lambda: api_take(404), lambda: api_take(500)])
