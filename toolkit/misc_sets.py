"""Eight more sets: testing, code-review, fast-mode, update-available, memory-write, interrupt, model-switch, background-task.

python misc_sets.py  ->  ../mine/<set>/
"""
from props import *

ROW_C = (60, 64, 78)


# ---------------------------------------------------------------- testing: rows run, pass or fail
TEST_Y = (14, 22, 30, 38, 46)
TEST_W = (34, 26, 40, 30, 22)


def testing_frame(status=(0, 0, 0, 0, 0), pulse=0, done=0.0, look=(2, 1), blink=False, bob=0, slide=0, sweat_f=None, key=False,
                  shake=0, smile=False):
    """status per row: 0 pending, 1 running, 2 pass, 3 fail."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    for i, st in enumerate(status):
        y = TEST_Y[i]
        sx = x0 + 6 + (shake if st == 3 else 0)
        col = [ROW_C, AMBER if pulse % 2 == 0 else (150, 110, 40), GREEN, RED][st]
        R(draw, sx, y, 7, 6, col)
        if st == 2:
            tick(draw, sx + 1, y + 1, WHITE, 1)
        elif st == 3:
            cross(draw, sx + 1, y + 1, WHITE, 1)
        R(draw, x0 + 18, y + 2, TEST_W[i], 2, (110, 116, 130) if st < 3 else (200, 90, 90))
    R(draw, x0 + 6, 54, 76, 2, (36, 40, 52))
    R(draw, x0 + 6, 54, round(76 * done), 2, GREEN)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def run_rows(f, start, status, fail=None, per=3):
    out, st = [], list(status)
    for i in range(start, 5):
        for k in range(per):
            s = list(st)
            s[i] = 1
            out.append(f(tuple(s), pulse=k, done=sum(1 for v in st if v == 2) / 5, look=(2, min(2, i // 2 + (k > 1)))))
        st[i] = 3 if i == fail else 2
        out.append(f(tuple(st), done=sum(1 for v in st if v == 2) / 5, look=(2, min(2, i // 2)),
                     bob=1 if st[i] == 2 else 0))
        if st[i] == 3:
            return out, st
    return out, st


def reset_rows(f, st):
    out = []
    for i in range(4, -1, -1):
        st[i] = 0
        out.append(f(tuple(st), done=sum(1 for v in st if v == 2) / 5))
    return out


def testing_pass():
    f = testing_frame
    frames = intro(f)
    run, st = run_rows(f, 0, [0] * 5)
    frames += run
    frames += [f(tuple(st), done=1.0, look=(2, 0), smile=True, bob=-2 if k == 0 else 0, blink=k == 6) for k in range(8)]
    return frames + reset_rows(f, st) + [f(blink=True), f()]


def testing_fail():
    f = testing_frame
    frames = intro(f)
    run, st = run_rows(f, 0, [0] * 5, fail=2)
    frames += run
    frames += [f(tuple(st), done=0.4, shake=(-1, 1)[k % 2], sweat_f=k, look=(1, 1), bob=k % 2) for k in range(6)]
    frames += [f(tuple(st), done=0.4, sweat_f=k, look=(2, 2), key=k % 2 == 0, bob=k % 2) for k in range(6)]   # fixes the code
    st[2] = 0
    for k in range(3):
        s = list(st)
        s[2] = 1
        frames.append(f(tuple(s), pulse=k, done=0.4, look=(2, 1)))
    st[2] = 2
    frames.append(f(tuple(st), done=0.6, bob=1))
    run, st = run_rows(f, 3, st)
    frames += run
    frames += [f(tuple(st), done=1.0, look=(2, 0), smile=True, bob=-2 if k == 0 else 0) for k in range(6)]
    return frames + reset_rows(f, st) + [f(blink=True), f()]


# ---------------------------------------------------------------- code review: a magnifier checks the diff
DIFF = (("=", 36), ("+", 30), ("+", 38), ("-", 24), ("=", 32), ("+", 28))
DIFF_Y = (13, 21, 29, 37, 45, 53)


def glass(draw, cx, cy):
    for yy in range(-6, 7):
        for xx in range(-6, 7):
            d = math.hypot(xx, yy)
            if 4.2 <= d <= 6.2:
                R(draw, cx + xx, cy + yy, 1, 1, WHITE)
    for k in range(5):
        R(draw, cx + 4 + k, cy + 4 + k, 2, 2, (200, 204, 215))


def review_frame(mag=None, checked=0, flag=None, fixed=False, approve=0, look=(2, 1), blink=False, bob=0, slide=0, sweat_f=None,
                 key=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (22, 24, 34))
    for i, (kind, w) in enumerate(DIFF):
        y = DIFF_Y[i] - 2
        if kind == "+":
            R(draw, x0 + 4, y - 1, 80, 6, (24, 56, 40))
        elif kind == "-" and not (fixed and flag == i):
            R(draw, x0 + 4, y - 1, 80, 6, (66, 30, 34))
        sign = {"=": None, "+": GREEN, "-": RED}[kind]
        if kind == "-" and fixed and flag == i:
            sign = GREEN
        if sign:
            R(draw, x0 + 6, y + 2, 3, 1, sign)
            if kind == "+" or (fixed and flag == i):
                R(draw, x0 + 7, y + 1, 1, 3, sign)
        R(draw, x0 + 14, y + 1, w, 3, (130, 136, 156) if kind == "=" else (190, 196, 214))
        if i < checked:
            tick(draw, x0 + 76, y, GREEN, 1)
        if flag == i and not fixed:
            R(draw, x0 + 74, y - 1, 8, 7, AMBER)
            R(draw, x0 + 77, y, 2, 3, DARK)
            R(draw, x0 + 77, y + 4, 2, 1, DARK)
    if mag is not None:
        glass(draw, x0 + mag[0], mag[1])
    if approve:
        dot(draw, x0 + 44, 33, round(14 * approve), GREEN)
        if approve >= 1:
            tick(draw, x0 + 34, 28, WHITE, 4)
    clawd(draw, look=look, blink=blink, bob=bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def review_scan(issue=None):
    f = review_frame
    frames = intro(f)
    checked, fixed = 0, False
    for i in range(6):
        for k in range(3):
            frames.append(f(mag=(30 + i * 2 + k, DIFF_Y[i] + 2), checked=checked, flag=issue if (issue is not None and i > issue) else None,
                            look=(2, min(2, i // 2)), fixed=fixed))
        if issue == i:
            frames += [f(mag=(40, DIFF_Y[i] + 2), checked=checked, flag=i, sweat_f=k, look=(2, 2), bob=k % 2) for k in range(5)]
            frames += [f(mag=None, checked=checked, flag=i, look=(2, 2), key=k % 2 == 0, bob=k % 2) for k in range(5)]
            fixed = True
            frames += [f(mag=None, checked=checked, flag=i, fixed=True, bob=-1 if k == 0 else 0) for k in range(3)]
        checked = i + 1
        frames.append(f(mag=(40, DIFF_Y[i] + 2), checked=checked, flag=issue, fixed=fixed, look=(2, min(2, i // 2)), bob=1))
    for k, a in enumerate((0.4, 0.8, 1.15, 1.0)):
        frames.append(f(checked=6, flag=issue, fixed=fixed, approve=a, look=(2, 0), bob=-1 if k == 2 else 0))
    frames += [f(checked=6, flag=issue, fixed=fixed, approve=1.0, look=(2, 0), blink=k == 5) for k in range(6)]
    for k in range(3):
        frames.append(f(checked=6 - 2 * (k + 1) if k < 3 else 0, flag=issue, fixed=fixed))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- fast mode: the bolt, speed lines, a race
BOLT = [(6, 0), (0, 14), (7, 14), (3, 26), (16, 9), (9, 9), (14, 0)]


def bolt_poly(draw, cx, cy, color):
    draw.polygon([(cx - 8 + x, cy - 13 + y) for x, y in BOLT], fill=color)


def fast_frame(charge=0.0, streak=None, race=None, look=(2, 1), blink=False, bob=0, slide=0, wind=False, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        if race is None:
            col = mix((70, 76, 92), YELLOW, charge)
            bolt_poly(d, x0 + 44, 32, col)
            if charge > 0.6:
                for k in range(6):
                    a = k * math.pi / 3 + math.pi / 6
                    R(d, round(x0 + 44 + math.cos(a) * 22), round(32 + math.sin(a) * 22), 2, 2, YELLOW)
        if streak is not None:
            for i, (y, ln, sp) in enumerate(((14, 18, 5), (22, 26, 7), (30, 14, 6), (38, 22, 8), (46, 16, 5), (52, 24, 7))):
                x = round(88 - ((streak * sp + i * 17) % 110))
                R(d, x0 + x, y, ln, 1, (255, 224, 120) if i % 2 == 0 else (200, 210, 235))
        if race is not None:
            slow, fast = race
            R(d, x0 + 6, 20, 76, 7, (36, 40, 52))
            R(d, x0 + 6, 20, round(76 * slow), 7, (130, 136, 156))
            R(d, x0 + 6, 36, 76, 7, (36, 40, 52))
            R(d, x0 + 6, 36, round(76 * fast), 7, YELLOW)
            bolt_poly(d, x0 + 6 + round(70 * fast), 39, WHITE) if False else None
            if fast >= 1.0:
                tick(d, x0 + 40, 48, GREEN, 2)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if wind:
        for k, (y, ln) in enumerate(((16, 8), (26, 12), (36, 6), (46, 10))):
            R(draw, 4 + (k * 3) % 5, OY + y - 8, ln, 1, (200, 210, 235))
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def fast_bolt():
    f = fast_frame
    frames = intro(f)
    for k in range(4):
        frames.append(f(charge=(k + 1) / 4, look=(2, 0), bob=1 if k == 3 else 0))
    for k in range(18):                                                      # speed lines rush through, eyes dart, wind blows back
        frames.append(f(charge=1.0, streak=k, look=(2 if k % 2 == 0 else 0, 1), wind=True, bob=-1 if k % 6 == 0 else 0))
    for k in range(4):
        frames.append(f(charge=1.0 - (k + 1) / 4, streak=18 + k if k < 2 else None, look=(2, 1)))
    return frames + [f(blink=True), f()]


def fast_race():
    f = fast_frame
    frames = intro(f)
    for k in range(18):                                                      # the fast bar wins the race
        fast = min(1.0, (k + 1) / 10)
        slow = min(1.0, (k + 1) / 30)
        frames.append(f(race=(slow, fast), look=(2, 1 + (k % 4 > 1)), wind=k > 2 and k < 10, bob=1 if k % 6 == 0 else 0))
    frames += [f(race=(0.6, 1.0), look=(2, 0), smile=True, bob=-2 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in range(3):
        frames.append(f(race=(0.6 - 0.2 * k, 1.0 - 0.45 * (k + 1)), look=(2, 1)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- update available: a gift, an up arrow
def gift(draw, cx, y, bow=True):
    R(draw, cx - 10, y + 6, 20, 14, AMBER)
    R(draw, cx - 11, y + 3, 22, 5, (250, 190, 90))
    R(draw, cx - 2, y + 3, 4, 17, PINK)
    if bow:
        R(draw, cx - 6, y, 5, 4, PINK)
        R(draw, cx + 1, y, 5, 4, PINK)


def up_badge(draw, cx, cy, s):
    r = max(1, round(8 * s))
    dot(draw, cx, cy, r, GREEN)
    if s >= 0.9:
        R(draw, cx - 1, cy - 3, 3, 7, WHITE)
        for k, w in enumerate((1, 3, 5)):
            R(draw, cx - w // 2, cy - 5 + k, w, 1, WHITE)


def update_frame(gy=None, badge=0.0, bar=None, sparkle=None, look=(2, 1), blink=False, bob=0, slide=0, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 6, 52, 76, 1, (70, 76, 92))

    def paint(d):
        if gy is not None:
            gift(d, x0 + 38, gy)
        if badge:
            up_badge(d, x0 + 56, round((gy if gy is not None else 28) + 4), badge)
        if bar is not None:
            R(d, x0 + 8, 52, 72, 3, (36, 40, 52))
            R(d, x0 + 8, 52, round(72 * bar), 3, GREEN)
        if sparkle is not None:
            for k, (sx, sy) in enumerate(((22, 20), (62, 16), (70, 34), (14, 36))):
                if (sparkle + k * 2) % 6 < 3:
                    R(d, x0 + sx, sy, 1, 3, YELLOW)
                    R(d, x0 + sx - 1, sy + 1, 3, 1, YELLOW)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def update_gift():
    f = update_frame
    frames = intro(f)
    for k, y in enumerate((-22, -8, 10, 22, 18, 22, 21, 22)):                # the gift drops in and bounces
        frames.append(f(gy=y, look=(2, 0 if k < 4 else 1), bob=1 if k == 3 else 0))
    for k, s in enumerate((0.4, 0.9, 1.2, 1.0)):
        frames.append(f(gy=22, badge=s, look=(2, 0), smile=k > 1, bob=-2 if k == 2 else 0))
    frames += [f(gy=22, badge=1.0, look=(2, 0), smile=True, blink=k == 5, sparkle=k) for k in range(9)]
    for k in range(3):
        frames.append(f(gy=22 + 14 * (k + 1), badge=max(0, 1 - 0.4 * (k + 1)), look=(2, 1)))
    return frames + [f(blink=True), f()]


def update_install():
    f = update_frame
    frames = intro(f)
    frames += [f(gy=22, look=(2, 1))] * 3
    for k in range(14):                                                      # installing
        frames.append(f(gy=22, bar=(k + 1) / 14, look=(2, 1 + (k % 6 > 2)), bob=1 if k % 5 == 0 else 0))
    for k, s in enumerate((0.5, 1.0, 1.2, 1.0)):
        frames.append(f(gy=22, bar=1.0, badge=s, look=(2, 0), smile=True, bob=-2 if k == 2 else 0))
    frames += [f(gy=22, bar=1.0, badge=1.0, look=(2, 0), smile=True, sparkle=k) for k in range(8)]
    for k in range(3):
        frames.append(f(gy=22 + 14 * (k + 1), bar=max(0, 1 - 0.4 * (k + 1)), badge=max(0, 1 - 0.4 * (k + 1))))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- memory write: a note is pinned to the board
BOARD, NOTE_Y, NOTE_P, NOTE_B = (130, 92, 58), (250, 224, 120), (240, 170, 190), (160, 210, 240)


def note(draw, x, y, w, h, color, lines=0):
    R(draw, x, y, w, h, color)
    for i in range(lines):
        R(draw, x + 2, y + 3 + i * 4, max(2, (w - 5) - (i == 2) * (w // 3)), 1, (110, 90, 60))


def pin(draw, x, y):
    R(draw, x, y, 2, 2, RED)


def memory_frame(new=None, lines=0, pinned=False, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0, key=False, sparkle=None):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 3, 8, 83, 46, BOARD)
    R(draw, x0 + 3, 8, 83, 1, (100, 66, 40))

    def paint(d):
        note(d, x0 + 8, 14, 20, 18, NOTE_Y, 3)
        pin(d, x0 + 17, 14)
        note(d, x0 + 36, 22, 18, 16, NOTE_P, 2)
        pin(d, x0 + 44, 22)
        if pinned:
            note(d, x0 + 62, 12, 20, 18, NOTE_B, 3)
            pin(d, x0 + 71, 12)
        if new:
            nx, ny, nw, nh = new
            note(d, x0 + nx, ny, nw, nh, NOTE_B, lines)
        if tickmark:
            tick(d, x0 + 64, 36, GREEN, 3)
        if sparkle is not None:
            for k, (sx, sy) in enumerate(((60, 10), (84, 18), (70, 32))):
                if (sparkle + k * 2) % 6 < 3:
                    R(d, x0 + sx, sy, 1, 3, WHITE)
                    R(d, x0 + sx - 1, sy + 1, 3, 1, WHITE)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def memory_type():
    f = memory_frame
    frames = intro(f)
    for k in range(3):                                                       # a blank note appears, big, in the middle
        frames.append(f(new=(30, 18, round(20 + 6 * (k + 1) / 3 * 1), round(18 + 6 * (k + 1) / 3)), look=(2, 1)))
    for n in range(1, 4):                                                    # Clawd writes on it, line by line
        frames += [f(new=(30, 18, 26, 24), lines=n, key=k % 2 == 0, bob=k % 2, look=(2, 1 + (n > 1))) for k in range(4)]
    for k in range(5):                                                       # it flies to the free spot and is pinned
        t = ease((k + 1) / 5)
        frames.append(f(new=(round(lerp(30, 62, t)), round(lerp(18, 12, t)), round(lerp(26, 20, t)), round(lerp(24, 18, t))),
                        lines=3, look=(2, 0)))
    frames += [f(pinned=True, tickmark=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in range(2):
        frames.append(f(pinned=True, look=(2, 1)))
    return frames + [f(blink=True), f()]


def memory_toss():
    f = memory_frame
    frames = intro(f)
    for k in range(4):
        frames.append(f(new=(66, 34, 14, 12), lines=1 + k // 2, key=k % 2 == 0, bob=k % 2, look=(2, 2)))   # a note leaves his hand
    for k in range(6):                                                       # arcs to the board
        t = (k + 1) / 6
        frames.append(f(new=(round(lerp(66, 62, t)), round(lerp(34, 12, t) - 8 * math.sin(t * math.pi)), round(lerp(14, 20, t)),
                             round(lerp(12, 18, t))), lines=3, look=(2, 0)))
    frames += [f(pinned=True, sparkle=k, tickmark=k > 1, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 7) for k in range(9)]
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- interrupt: Esc stops everything
def interrupt_frame(lines=(0, 0, 0), stopped=0, esc=0, look=(2, 1), blink=False, bob=0, slide=0, key=False, cursor=True):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (24, 26, 38))
    for i, (w, c) in enumerate(((30, LIGHT_BLUE), (22, PINK), (36, AMBER))):
        y = 16 + i * 10
        R(draw, x0 + 8, y, round(w * lines[i] / 100), 3, c)
    if cursor and not stopped:
        R(draw, x0 + 8 + round(30 * lines[0] / 100), 15, 1, 5, WHITE)
    if stopped:                                                              # everything dims, a stop sign flashes
        layer = Image.new("RGBA", (W, H), TRANS)
        ImageDraw.Draw(layer).rectangle([x0, PY0, x0 + 88, PY1], fill=(10, 10, 14, 150))
        img.alpha_composite(layer)
        draw = ImageDraw.Draw(img)
        if stopped == 1 or stopped % 2 == 1:
            dot(draw, x0 + 44, 38, 9, RED)
            R(draw, x0 + 38, 36, 12, 4, WHITE)
    if esc:
        kx, ky = x0 + 28, 8 + round((1 - esc) * -14)
        R(draw, kx, ky, 32, 16, (206, 207, 214))
        R(draw, kx, ky + 13, 32, 3, (140, 142, 154))
        text(draw, kx + 6, ky + 3, "ESC", (50, 54, 66), 2)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def interrupt_loop():
    f = interrupt_frame
    frames = intro(f)
    for k in range(14):                                                      # busy typing
        lines = (min(100, 12 + k * 7), max(0, min(100, k * 8 - 20)), max(0, min(100, k * 6 - 50)))
        frames.append(f(lines, key=k % 2 == 0, bob=k % 2, look=(2, 1 + (k % 8 > 4)), cursor=k % 4 < 3))
    full = (100, 100, 40)
    for k in range(3):                                                       # the Esc key drops in
        frames.append(f(full, esc=(k + 1) / 3, look=(2, 0), bob=-2 if k == 2 else 0))
    for k in range(8):                                                       # all stops: dimmed, stop sign flashes, Clawd freezes
        frames.append(f(full, stopped=1 + k % 2 * 2, esc=1.0 if k < 4 else 0.0, look=(0, 0), bob=0))
    for k in range(5):                                                       # then he turns to you
        frames.append(f(full, stopped=1, look=(-2, 1), blink=k == 3))
    for k in range(4):
        frames.append(f(tuple(round(v * (1 - (k + 1) / 4)) for v in full), look=(1, 1)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- model switch: small, medium and big Clawd, a selector between them
MODELS = ((11, 1, (244, 176, 140)), (33, 2, CORAL), (66, 3, (186, 98, 62)))   # centre x, grid size, body colour
FLOOR = 50
ACCESSORIES = [                                                              # one per model: bitmap rows, colour
    (["..#.#..", ".##.##.", "..###..", "...#..."], GREEN),                   # small model: a sprout
    (["....##....", "..######..", "##########"], (160, 108, 220)),         # medium model: a beret
    (["#...##...#", "##.####.##", "##########", "##########"], YELLOW),      # big model: a crown
]


def accessory(draw, head_x, head_y, head_w, kind, scale, bright=True, lift=0):
    rows, color = ACCESSORIES[kind]
    c = color if bright else mix(color, (30, 34, 46), 0.62)
    w, h = len(rows[0]) * scale, len(rows) * scale
    x, y = head_x + (head_w - w) // 2, head_y - h - lift
    for r, row in enumerate(rows):
        for col, ch in enumerate(row):
            if ch == "#":
                R(draw, x + col * scale, y + r * scale, scale, scale, c)


def sibling(draw, cx, g, color, bright, hop=0, smile=False, blink=False, kind=0):
    c = color if bright else mix(color, (30, 34, 46), 0.62)
    ox, oy = cx - 4 * g, FLOOR - 8 * g - hop
    R(draw, ox, oy, 8 * g, 2 * g, c)
    R(draw, ox - 2 * g, oy + 2 * g, 12 * g, 2 * g, c)
    R(draw, ox, oy + 4 * g, 8 * g, 2 * g, c)
    for lc in (0, 2, 5, 7):
        R(draw, ox + lc * g, oy + 6 * g, g, 2 * g, c)
    eye = BLACK if bright else (20, 22, 30)
    for ex in (1, 6):
        if blink:
            R(draw, ox + ex * g, oy + g + g // 2, g, 1, eye)
        else:
            R(draw, ox + ex * g, oy + g, g, g, eye)
    if smile and g > 1:
        R(draw, ox + 3 * g, oy + 2 * g + 1, 1, 1, eye)
        R(draw, ox + 3 * g + 1, oy + 2 * g + 2, 2 * g - 2 if g > 2 else 2, 1, eye)
        R(draw, ox + 5 * g - 1, oy + 2 * g + 1, 1, 1, eye)
    accessory(draw, ox, oy, 8 * g, kind, 1, bright)


def model_frame(sel=1, pos=None, hop=0, sparkle=None, look=(2, 1), blink=False, bob=0, slide=0, smile=False, mblink=False):
    """sel: which sibling is bright and gets the hop; pos = selector centre x while it hops between them."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 4, FLOOR + 8, 80, 1, (70, 76, 92))
    for i, (cx, g, c) in enumerate(MODELS):
        sibling(draw, x0 + cx, g, c, i == sel, hop if i == sel else 0, smile and i == sel, mblink and i == sel, kind=i)
    cx, g, _ = MODELS[sel]
    sx = x0 + (cx if pos is None else pos)
    hw, hh = 6 * g + 3, 4 * g + 3
    cy = FLOOR - 4 * g - hop
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):                      # bracket corners
        px, py = sx + dx * hw, cy + dy * hh
        R(draw, px - (3 if dx > 0 else 0), py, 4, 1, WHITE)
        R(draw, px, py - (3 if dy > 0 else 0), 1, 4, WHITE)
    if sparkle is not None:
        for k, (px, py) in enumerate(((cx - 10, 12), (cx + 10, 10), (cx, 6))):
            if (sparkle + k * 2) % 6 < 3:
                R(draw, x0 + px, py, 1, 3, YELLOW)
                R(draw, x0 + px - 1, py + 1, 3, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob)
    accessory(draw, OX, OY + bob, 8 * G, sel, 2, True, lift=slide // 8)          # Clawd wears the selected model's accessory at once;
    if smile:                                                                # it drops on during the enter and lifts off in the exit
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


HOPS = (0, 2, 3, 2, 0)


def model_hop():
    f = model_frame
    frames = intro(f)
    cur = 1
    for target in (0, 2, 1):
        a, b = MODELS[cur][0], MODELS[target][0]
        for k in range(5):                                                   # the selector moves across
            frames.append(f(sel=cur if k < 3 else target, pos=round(lerp(a, b, ease((k + 1) / 5))), look=(2, 0 if b > a else 2)))
        for k in range(5):                                                   # the chosen one hops, both Clawds happy
            frames.append(f(sel=target, hop=HOPS[k], smile=True, bob=-HOPS[k] // 2, look=(2, 1)))
        frames += [f(sel=target, smile=True, mblink=k == 2, blink=k == 2) for k in range(3)]
        cur = target
    return frames + [f(blink=True), f()]


def model_pick():
    f = model_frame
    frames = intro(f)
    for k in range(4):                                                       # eyes flick between the three, then choose the big one
        frames.append(f(sel=1, look=(2, (0, 1, 2, 1)[k]), blink=k == 3))
    for k in range(5):
        frames.append(f(sel=2, pos=round(lerp(33, 66, ease((k + 1) / 5))), look=(2, 0)))
    for h in range(2):                                                       # two big happy hops with sparkles
        for k in range(5):
            frames.append(f(sel=2, hop=HOPS[k] + 1, smile=True, bob=-HOPS[k] // 2, sparkle=k + h * 5, look=(2, 0)))
    frames += [f(sel=2, smile=True, sparkle=k, mblink=k == 3, blink=k == 3) for k in range(5)]
    for k in range(5):
        frames.append(f(sel=2 if k < 2 else 1, pos=round(lerp(66, 33, ease((k + 1) / 5))), look=(2, 1)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- background task: Clawd works while a widget runs
def widget(draw, x, y, state, spin=0, prog=0.0):
    R(draw, x, y, 24, 24, (36, 40, 52))
    R(draw, x + 1, y + 1, 22, 22, (24, 28, 38))
    if state == "run":
        for i in range(8):
            ang = i * math.pi / 4
            lit = (i - spin) % 8
            c = mix((50, 54, 66), WHITE, max(0, 1 - lit / 5)) if lit < 5 else (50, 54, 66)
            R(draw, round(x + 12 + math.cos(ang) * 7) - 1, round(y + 10 + math.sin(ang) * 7), 3, 3, c)
        R(draw, x + 3, y + 20, round(18 * prog), 2, LIGHT_BLUE)
    elif state == "done":
        tick(draw, x + 5, y + 6, GREEN, 3)


def bg_frame(lines=0, widget_x=0, state="idle", spin=0, prog=0.0, dotflash=False, toast=False, look=(2, 1), blink=False,
             bob=0, slide=0, key=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (24, 26, 38))
    R(draw, x0, 6, 89, 6, (40, 44, 54))

    def paint(d):
        for i, (w, c) in enumerate(((36, LIGHT_BLUE), (28, PINK), (40, AMBER), (22, GREEN))):
            R(d, x0 + 5, 16 + i * 8, round(w * min(1.0, max(0.0, lines - i * 0.25) * 4 if lines else 0) * 0.5 + (0 if lines else 0)), 3, c)
        if state != "idle" or widget_x:
            widget(d, x0 + 62 + widget_x, 16, state, spin, prog)
        if dotflash:
            dot(d, x0 + 84 + widget_x, 14, 2, AMBER)
        if toast:
            R(d, x0 + 48, 44, 38, 10, WHITE)
            tick(d, x0 + 50, 46, GREEN, 1)
            R(d, x0 + 58, 48, 24, 2, (110, 116, 130))
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def bg_run():
    f = bg_frame
    frames = intro(f)
    for k in range(4):                                                       # the widget slides in
        frames.append(f(widget_x=round(30 * (1 - ease((k + 1) / 4))), state="run", spin=k, look=(2, 0)))
    for k in range(18):                                                      # Clawd keeps typing while it runs
        frames.append(f(lines=(k + 1) / 18, state="run", spin=k, prog=(k + 1) / 18, key=k % 2 == 0, bob=k % 2,
                        look=(2, 1 + (k % 8 > 5))))
    for k in range(3):
        frames.append(f(lines=1.0, state="done", dotflash=k % 2 == 0, look=(2, 0), bob=-1 if k == 0 else 0))
    frames += [f(lines=1.0, state="done", toast=k > 0, look=(2, 0), blink=k == 5) for k in range(7)]
    for k in range(4):
        frames.append(f(lines=1.0 - (k + 1) / 4, widget_x=round(30 * ease((k + 1) / 4)), state="done"))
    return frames + [f(blink=True), f()]


def bg_notify():
    f = bg_frame
    frames = intro(f)
    for k in range(4):
        frames.append(f(widget_x=round(30 * (1 - ease((k + 1) / 4))), state="run", spin=k))
    for k in range(10):
        frames.append(f(lines=(k + 1) / 10 * 0.6, state="run", spin=k, prog=(k + 1) / 20, key=k % 2 == 0, bob=k % 2,
                        look=(2, 2)))
    for k in range(6):                                                       # the widget finishes mid-work: a glance, then on
        frames.append(f(lines=0.6, state="done", dotflash=k % 2 == 0, toast=k > 1, look=(2, 0 if k < 4 else 1), bob=-1 if k == 0 else 0))
    for k in range(8):
        frames.append(f(lines=0.6 + (k + 1) / 8 * 0.4, state="done", toast=k < 4, key=k % 2 == 0, bob=k % 2, look=(2, 2)))
    for k in range(4):
        frames.append(f(lines=1.0 - (k + 1) / 4, widget_x=round(30 * ease((k + 1) / 4)), state="done"))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("testing", testing_frame, [testing_pass, testing_fail])
    finish("code-review", review_frame, [lambda: review_scan(None), lambda: review_scan(3)])
    finish("fast-mode", fast_frame, [fast_bolt, fast_race])
    finish("update-available", update_frame, [update_gift, update_install])
    finish("memory-write", memory_frame, [memory_type, memory_toss])
    finish("interrupt", interrupt_frame, [interrupt_loop])
    finish("model-switch", model_frame, [model_hop, model_pick])
    finish("background-task", bg_frame, [bg_run, bg_notify])
