"""Eight more sets: tool-failure, todo-list, session-end, teammate-idle, rewind, skills, scheduled-task, ide-connected.

python event_sets.py  ->  ../mine/<set>/
"""
import math

from props import *
from misc_sets import accessory, sibling, bolt_poly

RED_D = (120, 50, 54)
EMPTY = (36, 40, 52)


# ---------------------------------------------------------------- tool failure: red cross, error log, retry, success
def wrench(draw, x, y, color):
    dot(draw, x + 5, y + 5, 5, color)
    dot(draw, x + 5, y + 5, 2, EMPTY)
    R(draw, x + 3, y + 1, 4, 3, EMPTY)                                       # the jaw opening
    for i in range(11):
        R(draw, x + 8 + i, y + 8 + i, 3, 3, color)


def fail_frame(state="idle", spin=None, log=0, fixed=0, shake=0, look=(2, 1), blink=False, bob=0, slide=0, sweat_f=None,
               q=False, key=False, smile=False):
    """state: idle, fail, ok. log = how many error lines are shown, fixed = how many of them turned green."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    col = {"idle": (90, 96, 116), "fail": RED, "ok": GREEN}[state]
    R(draw, x0 + 9 + shake, 20, 28, 28, EMPTY)
    R(draw, x0 + 10 + shake, 21, 26, 26, (20, 24, 34) if state == "idle" else mix((20, 24, 34), col, 0.25))
    wrench(draw, x0 + 14 + shake, 25, col)
    if state == "fail":
        cross(draw, x0 + 26 + shake, 38, WHITE, 2)
    if state == "ok":
        tick(draw, x0 + 24, 38, WHITE, 2)
    if spin is not None:
        for i in range(8):
            ang = i * math.pi / 4
            lit = (i - spin) % 8
            c = mix((50, 54, 66), AMBER, max(0, 1 - lit / 5)) if lit < 5 else (50, 54, 66)
            R(draw, round(x0 + 23 + math.cos(ang) * 17) - 1, round(34 + math.sin(ang) * 17) - 1, 3, 3, c)
    for i in range(log):
        c = GREEN if i < fixed else (220, 90, 90) if i % 2 == 0 else (230, 150, 80)
        R(draw, x0 + 46, 22 + i * 8, (34, 26, 30)[i], 3, c)
    clawd(draw, look=look, blink=blink, bob=bob)
    if q:
        for r_, row in enumerate(("###", "..#", ".##", "...", ".#.")):
            for c_, v in enumerate(row):
                if v == "#":
                    R(draw, OX + 22 + c_ * 2, r_, 2, 1, AMBER)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def tool_fail_retry():
    f = fail_frame
    frames = intro(f)
    frames += [f(spin=k, look=(2, 1)) for k in range(6)]
    for k in range(6):                                                       # it fails
        frames.append(f("fail", shake=(-1, 1)[k % 2], log=min(3, k // 2 + 1), sweat_f=k, q=k > 2, look=(1, 1), bob=k % 2))
    for k in range(6):                                                       # Clawd reads the log
        frames.append(f("fail", log=3, sweat_f=k, look=(2, k // 2), q=k < 3))
    frames += [f("fail", log=3, spin=k, look=(2, 2)) for k in range(8)]       # retry
    frames += [f("ok", log=3 - k // 3 if k > 3 else 3, look=(2, 0), smile=True, bob=-2 if k == 0 else 0) for k in range(8)]
    for k in range(3):
        frames.append(f("ok" if k < 1 else "idle", log=0, look=(2, 1)))
    return frames + [f(blink=True), f()]


def tool_fail_fix():
    f = fail_frame
    frames = intro(f)
    frames += [f(spin=k) for k in range(5)]
    for k in range(5):
        frames.append(f("fail", shake=(-1, 1)[k % 2], log=3, sweat_f=k, look=(1, 1), bob=k % 2))
    for n in range(1, 4):                                                    # Clawd fixes the lines one by one
        frames += [f("fail", log=3, fixed=n - 1, key=k % 2 == 0, bob=k % 2, look=(2, n - 1), sweat_f=k) for k in range(4)]
        frames.append(f("fail", log=3, fixed=n, look=(2, n - 1)))
    frames += [f("fail", log=3, fixed=3, spin=k, look=(2, 1)) for k in range(6)]
    frames += [f("ok", log=3, fixed=3, look=(2, 0), smile=True, bob=-2 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in range(3):
        frames.append(f("idle", look=(2, 1)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- todo list
TODO_W = (36, 28, 40, 24, 32)
TODO_C = (LIGHT_BLUE, PINK, AMBER, GREEN, PURPLE)


def todo_frame(rows=(), pulse=0, count=0, spark=None, look=(2, 1), blink=False, bob=0, slide=0, key=False, smile=False):
    """rows: list of states 1 pending, 2 active, 3 done, 0 hidden."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 6, 9, 76, 1, (60, 66, 82))
    R(draw, x0 + 8, 11, 22, 3, (150, 156, 176))
    for i, st in enumerate(rows):
        y = 18 + i * 7
        if st == 0:
            continue
        bx = x0 + 9
        if st == 1:
            R(draw, bx, y, 5, 5, (70, 76, 92))
            R(draw, bx + 1, y + 1, 3, 3, (24, 28, 38))
            R(draw, x0 + 18, y + 1, TODO_W[i], 3, (130, 136, 156))
        elif st == 2:
            R(draw, bx, y, 5, 5, AMBER if pulse % 2 == 0 else (160, 110, 40))
            R(draw, x0 + 18, y + 1, TODO_W[i], 3, TODO_C[i])
            R(draw, x0 + 18 + TODO_W[i] + 3, y + 1, 4, 3, AMBER)
        else:
            R(draw, bx, y, 5, 5, GREEN)
            tick(draw, bx, y, WHITE, 1)
            R(draw, x0 + 18, y + 1, TODO_W[i], 3, (70, 76, 92))
            R(draw, x0 + 18, y + 2, TODO_W[i], 1, (150, 156, 176))           # struck through
    for i in range(5):
        R(draw, x0 + 8 + i * 6, 54, 4, 2, GREEN if i < count else (46, 50, 62))
    if spark is not None:
        for k, (sx, sy) in enumerate(((70, 12), (78, 40), (60, 50))):
            if (spark + k * 2) % 6 < 3:
                R(draw, x0 + sx, sy, 1, 3, YELLOW)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def todo_run():
    f = todo_frame
    frames = intro(f)
    rows = []
    for i in range(5):                                                       # the list is created
        rows = rows + [1]
        frames += [f(tuple(rows), look=(2, min(2, i // 2)), key=True, bob=1)] + [f(tuple(rows), look=(2, min(2, i // 2)))]
    done = 0
    for i in range(5):                                                       # worked off one by one
        for k in range(4):
            r = [3] * i + [2] + [1] * (4 - i)
            frames.append(f(tuple(r), pulse=k, count=i, key=k % 2 == 0, bob=k % 2, look=(2, min(2, i // 2 + (k > 1)))))
        done = i + 1
        frames.append(f(tuple([3] * done + [1] * (5 - done)), count=done, bob=-1, look=(2, min(2, i // 2))))
    frames += [f((3,) * 5, count=5, spark=k, smile=True, look=(2, 0), blink=k == 7) for k in range(9)]
    for i in range(4, -1, -1):
        frames.append(f(tuple([3] * i), count=i))
    return frames + [f(blink=True), f()]


def todo_add():
    f = todo_frame
    frames = intro(f)
    rows = [1, 1, 1]
    frames += [f(tuple(rows[:k + 1]), key=True, bob=1) for k in range(3)] + [f(tuple(rows))] * 2
    for i in range(3):
        for k in range(3):
            frames.append(f(tuple([3] * i + [2] + [1] * (2 - i)), pulse=k, count=i, key=k % 2 == 0, bob=k % 2, look=(2, i)))
        frames.append(f(tuple([3] * (i + 1) + [1] * (2 - i)), count=i + 1, bob=-1))
        if i == 1:                                                           # a new item shows up in the middle of the work
            frames += [f((3, 3, 1, 1), count=2, key=True, bob=1, look=(2, 2), blink=False)] * 2
            rows = [3, 3, 1, 1]
            for k in range(3):
                frames.append(f(tuple(rows[:3]) + (1,) * (k > 0) + (1, 1)[:0], count=2, look=(2, 2)))
            frames += [f((3, 3, 1, 1), count=2)] * 2
            for k in range(3):
                frames.append(f((3, 3, 2, 1), pulse=k, count=2, key=k % 2 == 0, bob=k % 2, look=(2, 2)))
            frames.append(f((3, 3, 3, 1), count=3, bob=-1))
            for k in range(3):
                frames.append(f((3, 3, 3, 2), pulse=k, count=3, key=k % 2 == 0, bob=k % 2, look=(2, 2)))
            frames.append(f((3, 3, 3, 3), count=4, bob=-1))
            break
    frames += [f((3, 3, 3, 3), count=4, spark=k, smile=True, look=(2, 0)) for k in range(7)]
    for i in range(3, -1, -1):
        frames.append(f(tuple([3] * i), count=i))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- session end: exit, a wave, the screen switches off
def term_frame(typed=0, summary=0, wave=None, crt=None, led=0, cursor=True, look=(2, 1), blink=False, bob=0, slide=0, smile=False,
               lid=0.0, key=False):
    img, draw = new_frame()
    x0, x1 = PX0 + slide, PX1 + slide
    draw.rectangle([x0 - 2, PY0 - 2, x1 + 2, PY1 + 2], fill=PANEL_EDGE)
    draw.rectangle([x0, PY0, x1, PY1], fill=(12, 14, 18))
    draw.rectangle([x0, PY0, x1, PY0 + 7], fill=(40, 44, 54))
    for i, c in enumerate((RED, YELLOW, GREEN)):
        draw.rectangle([x0 + 4 + i * 5, PY0 + 3, x0 + 5 + i * 5, PY0 + 4], fill=c)
    R(draw, x0 + 6, 19, 2, 2, GREEN)
    R(draw, x0 + 8, 21, 2, 2, GREEN)
    R(draw, x0 + 6, 23, 2, 2, GREEN)
    if typed:
        R(draw, x0 + 13, 20, typed, 4, (225, 228, 235))
    if cursor:
        R(draw, x0 + 13 + typed + (1 if typed else 0), 19, 4, 6, WHITE)
    if summary:                                                              # a small session summary
        for i, (w, c) in enumerate(((46, LIGHT_BLUE), (34, PINK), (40, AMBER))):
            if i < summary:
                R(draw, x0 + 8, 30 + i * 6, w, 3, c)
                tick(draw, x0 + 58, 29 + i * 6, GREEN, 1)
    if crt is not None:                                                      # the screen switches off like an old TV
        h = max(1, round(53 * crt))
        R(draw, x0, 6, 89, 53, (4, 4, 6))
        if crt > 0.05:
            R(draw, x0 + 2, 32 - h // 2, 85, h, (12, 14, 18))
        else:
            R(draw, x0 + 36, 31, 16, 2, WHITE)
        R(draw, x0 + 82, 53, 3, 3, RED if led else (50, 20, 22))
    clawd(draw, look=look, blink=blink, bob=bob, lid=lid)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if wave is not None:                                                     # a little waving hand beside Clawd
        wx = 82 + (4 if wave % 2 else 0)
        dot(draw, wx, 26, 3, YELLOW)
        for k in range(3):
            R(draw, wx - 3 + k * 3, 21, 2, 3, YELLOW)
    if key:
        key_press(draw, bob)
    return img


def end_exit():
    f = term_frame
    frames = intro(f)
    for k in range(5):                                                       # types "exit"
        frames.append(f(typed=round(14 * (k + 1) / 5), key=k % 2 == 0, bob=k % 2, look=(2, 2)))
    frames += [f(typed=14, look=(2, 1), blink=True)]
    for k in range(8):                                                       # waves goodbye
        frames.append(f(typed=14, cursor=False, wave=k, smile=True, look=(2, 1), bob=-1 if k % 4 == 1 else 0))
    for k, c in enumerate((0.6, 0.25, 0.04, 0.0)):                           # screen off
        frames.append(f(typed=14, cursor=False, crt=c, led=1, smile=k < 2, look=(2, 1), lid=0.3 * (k + 1) / 4))
    frames += [f(crt=0.0, led=k % 2, look=(2, 2), lid=0.85) for k in range(3)]
    frames += [f(crt=0.0, led=0, look=(2, 1), lid=0.4), f(look=(2, 1), lid=0.2)]
    return frames + [f(blink=True), f()]


def end_summary():
    f = term_frame
    frames = intro(f)
    for k in range(4):
        frames.append(f(typed=round(14 * (k + 1) / 4), key=k % 2 == 0, bob=k % 2, look=(2, 2)))
    for n in (1, 2, 3):                                                      # what was done this session
        frames += [f(typed=14, cursor=False, summary=n, look=(2, n - 1))] * 3
    frames += [f(typed=14, cursor=False, summary=3, wave=k, smile=True, look=(2, 0), bob=-1 if k % 4 == 1 else 0) for k in range(8)]
    for k, c in enumerate((0.6, 0.25, 0.04, 0.0)):
        frames.append(f(typed=14, cursor=False, summary=3 if k < 2 else 0, crt=c, led=1, smile=k < 2, look=(2, 1), lid=0.3 * (k + 1) / 4))
    frames += [f(crt=0.0, led=k % 2, look=(2, 2), lid=0.85) for k in range(3)]
    frames += [f(look=(2, 1), lid=0.3), f(blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- teammate idle: three agents wait for work
MATES = ((16, CORAL), (44, (150, 172, 232)), (72, (152, 204, 142)))


def mates_frame(blinks=(), sleepy=None, ping=None, hop=0, card=False, looks=(0, 0, 0), look=(2, 1), blink=False, bob=0, slide=0,
                z=None, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 4, 58, 80, 1, (70, 76, 92))
    for i, (cx, c) in enumerate(MATES):
        sibling(draw, x0 + cx, c and 2, c, True, hop if ping == i else 0, ping == i and smile, i in blinks, None, looks[i])
    if z is not None:
        zzz(draw, z, x0 + MATES[sleepy][0] - 4 if sleepy is not None else x0 + 40, 30, 2)
    if ping is not None and not card:
        bx = x0 + MATES[ping][0] - 3
        R(draw, bx, 12, 7, 9, AMBER)
        R(draw, bx + 3, 14, 1, 3, DARK)
        R(draw, bx + 3, 18, 1, 1, DARK)
    if card and ping is not None:
        cx = x0 + MATES[ping][0]
        R(draw, cx - 4, 28, 8, 10, WHITE)
        R(draw, cx - 3, 30, 6, 1, (140, 146, 166))
        R(draw, cx - 3, 33, 4, 1, (140, 146, 166))
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def mates_wait():
    f = mates_frame
    frames = intro(f)
    for k in range(18):                                                      # they blink in turn, one dozes off
        who = (k // 3) % 3
        frames.append(f(blinks=(who,) if k % 3 == 2 else (), sleepy=1, z=k if k > 5 else None, look=(2, 1 + (who == 1)),
                        blink=k == 14))
    for k in range(4):
        frames.append(f(look=(2, 1)))
    return frames + [f(blink=True), f()]


def mates_ping():
    f = mates_frame
    frames = intro(f)
    for k in range(4):
        frames.append(f(look=(2, 1), looks=(0, 0, 0)))
    for k in range(4):                                                       # a new task pings the middle agent
        frames.append(f(ping=1, hop=(0, 2, 3, 2)[k], smile=True, looks=(1, 0, -1), look=(2, 0), bob=-1 if k == 1 else 0))
    for k in range(6):
        frames.append(f(ping=1, card=True, hop=(0, 2, 3, 2, 0, 0)[k], smile=True, looks=(1, 0, -1), look=(2, 0)))
    frames += [f(ping=1, card=True, looks=(1, 0, -1), look=(2, 1), blink=k == 3) for k in range(5)]
    for k in range(3):
        frames.append(f(look=(2, 1), looks=(0, 0, 0)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- rewind: scrub the timeline back and replay
MSG_C = (LIGHT_BLUE, PINK, LIGHT_BLUE, AMBER, LIGHT_BLUE, GREEN)
MSG_W = (30, 36, 26, 38, 32, 28)


def rewind_frame(handle=1.0, branch=0, hot=False, look=(2, 1), blink=False, bob=0, slide=0, key=False, sweat_f=None):
    """handle 0..1 along the timeline; chat lines at or before the handle are shown, `branch` a new green line."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    shown = int(handle * 6 + 0.001)
    for i in range(6):
        if i < shown:
            x = x0 + 8 + (30 if i % 2 else 0)
            R(draw, x, 12 + i * 6, MSG_W[i], 3, MSG_C[i])
    if branch:
        R(draw, x0 + 38, 12 + shown * 6, 6 + 5 * branch, 3, (110, 220, 140))
    R(draw, x0 + 8, 52, 72, 2, (50, 54, 66))
    for i in range(6):
        R(draw, x0 + 8 + round(72 * (i + 1) / 6) - 1, 50, 1, 6, (90, 96, 116))
    hx = x0 + 8 + round(72 * handle)
    R(draw, hx - 2, 48, 5, 9, WHITE if hot else (200, 204, 215))
    c = AMBER if hot else (70, 76, 92)
    for k in range(2):                                                       # the "<<" rewind symbol
        for r_ in range(5):
            R(draw, x0 + 72 + k * 5 + abs(r_ - 2) // 1 * 0 + (2 - abs(r_ - 2)), 8 + r_ - 6 + 6, 1, 1, c) if False else None
    for k in range(2):
        for r_ in range(5):
            w = 3 - abs(r_ - 2)
            R(draw, x0 + 70 + k * 5 + (3 - w), 4 + r_, w, 1, c)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def rewind_branch():
    f = rewind_frame
    frames = intro(f)
    for k in range(10):                                                      # the handle is dragged back to message 3
        h = lerp(1.0, 0.5, ease((k + 1) / 10))
        frames.append(f(h, hot=True, look=(2, 1 + (k % 4 > 1)), bob=1 if k % 5 == 0 else 0))
    frames += [f(0.5, hot=True, look=(2, 1))] * 2
    for k in range(5):                                                       # a different answer is typed from there
        frames.append(f(0.5, branch=k + 1, key=k % 2 == 0, bob=k % 2, look=(2, 1)))
    frames += [f(0.5, branch=5, look=(2, 0), blink=True)] * 2
    for k in range(10):                                                      # and the timeline plays forward again
        h = lerp(0.5, 1.0, ease((k + 1) / 10))
        frames.append(f(h, hot=k < 9, branch=max(0, 5 - k) if h < 0.7 else 0, look=(2, 1)))
    return frames + [f(blink=True), f()]


def rewind_scrub():
    f = rewind_frame
    frames = intro(f)
    for target in (0.3, 0.8, 0.15):                                          # scrubbing back and forth
        cur = frames and 1.0
        for k in range(7):
            pass
    pos = 1.0
    for target in (0.3, 0.8, 0.15, 1.0):
        n = 7
        for k in range(n):
            h = lerp(pos, target, ease((k + 1) / n))
            frames.append(f(h, hot=True, look=(2, 0 if target > pos else 2), bob=1 if k == 0 else 0, sweat_f=None))
        pos = target
        frames += [f(pos, hot=pos < 1.0, look=(2, 1))] * 2
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- skills: a cartridge gives Clawd a new skill
SKILLS = ((PURPLE, 1), (GREEN, 0))                                            # cartridge colour, accessory index


def star(draw, cx, cy, color):
    R(draw, cx - 1, cy - 4, 3, 9, color)
    R(draw, cx - 4, cy - 1, 9, 3, color)
    R(draw, cx - 3, cy - 3, 2, 2, color)
    R(draw, cx + 2, cy - 3, 2, 2, color)
    R(draw, cx - 3, cy + 2, 2, 2, color)
    R(draw, cx + 2, cy + 2, 2, 2, color)


def skills_frame(cart=None, cart_x=60, skill=None, power=0, look=(2, 1), blink=False, bob=0, slide=0, sparkle=None, key=False,
                 hat=None):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 50, 18, 30, 28, (36, 40, 52))                               # the slot
    R(draw, x0 + 52, 20, 26, 24, (14, 16, 22))
    R(draw, x0 + 8, 16, 34, 30, (30, 34, 46))                                # the little screen
    R(draw, x0 + 10, 18, 30, 26, (14, 20, 30) if skill is None else mix((14, 20, 30), SKILLS[skill][0], 0.3))

    def paint(d):
        if cart is not None:
            c = SKILLS[cart][0]
            R(d, x0 + cart_x, 20, 20, 24, c)
            R(d, x0 + cart_x, 20, 20, 4, mix(c, BLACK, 0.35))
            R(d, x0 + cart_x + 3, 26, 14, 10, mix(c, WHITE, 0.55))
            R(d, x0 + cart_x + 3, 38, 14, 2, mix(c, BLACK, 0.35))
        if skill is not None and power:
            cx, cy = x0 + 25, 31
            if skill == 0:
                star(d, cx, cy, YELLOW)
            else:
                bolt_poly(d, cx, cy, YELLOW)
            if power > 1:
                for k in range(6):
                    a = k * math.pi / 3 + power * 0.3
                    R(d, round(cx + math.cos(a) * 15), round(cy + math.sin(a) * 12), 2, 2, WHITE)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if hat is not None:
        accessory(draw, OX, OY + bob, 8 * G, SKILLS[hat][1], 2, True, lift=slide // 8)
    if key:
        key_press(draw, bob)
    return img


def skills_load(i):
    f = skills_frame
    frames = intro(f)
    for k in range(7):                                                       # the cartridge slides into the slot
        frames.append(f(cart=i, cart_x=round(lerp(92, 58, ease((k + 1) / 7))), look=(2, 1), bob=1 if k == 0 else 0))
    frames += [f(cart=i, cart_x=58, bob=1, look=(2, 1))]
    for k in range(3):                                                       # the screen powers up
        frames.append(f(cart=i, cart_x=58, skill=i, power=k, look=(2, 0)))
    for k in range(10):                                                      # Clawd gets the skill (an accessory) at once
        frames.append(f(cart=i, cart_x=58, skill=i, power=1 + k % 3, hat=i, look=(2, 0 if k < 6 else 1), sparkle=k,
                        bob=-2 if k in (0, 1) else 0, blink=k == 8))
    for k in range(3):
        frames.append(f(cart=i, cart_x=58, skill=i, power=1, hat=i, look=(2, 1)))
    for k in range(6):                                                       # eject: the cartridge slides out and the skill is put away
        frames.append(f(cart=i, cart_x=round(lerp(58, 92, ease((k + 1) / 6))), skill=i if k < 3 else None, power=1 if k < 3 else 0,
                        hat=i if k < 4 else None, look=(2, 1)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- scheduled task: the clock rings, the task runs, again and again
CLOCK = (30, 32, 16)                                                          # centre x (panel relative), y, radius


def hand(draw, cx, cy, deg, length, color, w=2):
    a = math.radians(deg - 90)
    for r in range(0, length):
        R(draw, round(cx + math.cos(a) * r) - w // 2, round(cy + math.sin(a) * r) - w // 2, w, w, color)


def clock_frame(minute=60.0, ring=None, bell=0, bar=0.0, tickmark=False, lid=0.0, zf=None, look=(2, 1), blink=False, bob=0,
                slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    cx, cy, r = x0 + CLOCK[0], CLOCK[1], CLOCK[2]
    dot(draw, cx, cy, r, (200, 204, 215))
    dot(draw, cx, cy, r - 2, (20, 24, 34))
    for k in range(12):
        a = math.radians(k * 30)
        R(draw, round(cx + math.sin(a) * (r - 4)), round(cy - math.cos(a) * (r - 4)), 2, 2, (130, 136, 156))
    hand(draw, cx, cy, 300, 7, (220, 224, 235), 3)                           # the hour hand stays put
    hand(draw, cx, cy, minute, 11, AMBER, 2)
    dot(draw, cx, cy, 2, WHITE)
    if ring is not None:                                                     # the repeat arrow: a lit spot runs around
        for i in range(24):
            a = math.radians(i * 15 - 90)
            lit = (i - ring) % 24
            c = mix((40, 44, 58), LIGHT_BLUE, max(0, 1 - lit / 8)) if lit < 8 else (40, 44, 58)
            R(draw, round(cx + math.cos(a) * (r + 5)) - 1, round(cy + math.sin(a) * (r + 5)) - 1, 2, 2, c)
    if bell:                                                                 # the bell on top rings
        bx = x0 + 30 + (-1, 1)[bell % 2] * 2
        R(draw, bx - 4, 8, 8, 4, YELLOW)
        R(draw, bx - 2, 6, 4, 2, YELLOW)
        R(draw, bx - 1, 12, 2, 2, YELLOW)
    R(draw, x0 + 56, 20, 24, 24, (36, 40, 52))
    R(draw, x0 + 57, 21, 22, 22, (22, 26, 36))
    R(draw, x0 + 59, 24, 14, 2, (110, 116, 140))
    R(draw, x0 + 59, 29, 18, 2, (110, 116, 140))
    R(draw, x0 + 59, 38, 18, 3, (36, 40, 52))
    R(draw, x0 + 59, 38, round(18 * bar), 3, GREEN)
    if tickmark:
        tick(draw, x0 + 62, 31, GREEN, 2)
    clawd(draw, look=look, blink=blink, bob=bob, lid=lid)
    if zf is not None:
        zzz(draw, zf, 80, 34, 3)
    return img


def clock_run():
    f = clock_frame
    frames = intro(f)
    for k in range(20):                                                      # time passes, Clawd dozes off
        lid = min(0.85, max(0.0, (k - 3) / 12))
        frames.append(f(60.0 + 18 * (k + 1), lid=lid, zf=k if lid > 0.5 else None, look=(2, 2 if lid > 0.3 else 1)))
    for k in range(8):                                                       # the bell rings, he wakes
        frames.append(f(60.0, bell=k + 1, lid=0.85 * (1 - ease((k + 1) / 8)), look=(2, 0), bob=-1 if k == 4 else 0))
    for k in range(8):
        frames.append(f(60.0, bell=k % 2 + 1 if k < 4 else 0, bar=(k + 1) / 8, look=(2, 1), bob=k % 2))
    frames += [f(60.0, bar=1.0, tickmark=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(7)]
    frames += [f(60.0, bar=0.5), f(60.0, bar=0.0, blink=True)]
    return frames + [f()]


def clock_repeat():
    f = clock_frame
    frames = intro(f)
    for rnd in range(2):                                                     # two runs of the recurring task
        for k in range(12):
            frames.append(f(60.0 + 30 * (k + 1), ring=k * 2 + rnd * 4, lid=0.5 if k > 5 else 0.0, zf=k if k > 8 else None,
                            look=(2, 1)))
        for k in range(6):
            frames.append(f(60.0 + 30 * 12, ring=k * 2, bell=k % 2 + 1, bar=(k + 1) / 6, lid=0.0, look=(2, 0), bob=k % 2))
        frames += [f(60.0, ring=rnd, bar=1.0, tickmark=True, look=(2, 0), bob=-1 if k == 0 else 0) for k in range(4)]
        frames.append(f(60.0, bar=0.4, look=(2, 1)))
    frames += [f(60.0, bar=0.0, ring=None, blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- IDE connected: terminal and editor link up
def ide_frame(cable=0.0, linked=False, sel=False, chip=False, diff=0, ok=False, look=(2, 1), blink=False, bob=0, slide=0, key=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (22, 24, 34))
    R(draw, x0 + 3, 12, 34, 38, (12, 14, 18))                                # terminal window
    R(draw, x0 + 3, 12, 34, 5, (40, 44, 54))
    R(draw, x0 + 5, 14, 2, 2, GREEN if linked else (90, 96, 116))
    R(draw, x0 + 6, 21, 2, 2, GREEN)
    R(draw, x0 + 8, 23, 2, 2, GREEN)
    R(draw, x0 + 6, 25, 2, 2, GREEN)
    R(draw, x0 + 12, 22, 14, 3, (140, 146, 166))
    if chip:
        R(draw, x0 + 8, 32, 24, 6, (60, 80, 140))
        R(draw, x0 + 10, 34, 14, 2, WHITE)
        tick(draw, x0 + 26, 33, GREEN, 1)
    R(draw, x0 + 46, 8, 38, 46, (30, 34, 48))                                # editor window
    R(draw, x0 + 46, 8, 38, 5, (50, 56, 80))
    R(draw, x0 + 48, 10, 2, 2, GREEN if linked else (90, 96, 116))
    R(draw, x0 + 46, 13, 7, 41, (24, 28, 40))
    rows = ((24, (198, 120, 221)), (20, (152, 195, 121)), (28, LIGHT_BLUE), (16, (229, 192, 123)), (22, (152, 195, 121)), (12, (198, 120, 221)))
    for i, (w, c) in enumerate(rows):
        y = 18 + i * 6
        if sel and i == 2:
            R(draw, x0 + 53, y - 1, 30, 5, (60, 80, 140))
        if diff and i >= 3:
            R(draw, x0 + 53, y - 1, 30, 5, (30, 80, 52) if i % 2 else (90, 40, 44))
        R(draw, x0 + 55, y, w, 3, c)
        if ok and i >= 3:
            tick(draw, x0 + 78, y - 1, GREEN, 1)
    if cable:
        x_end = round(lerp(34, 48, cable))
        R(draw, x0 + 36, 44, max(1, x_end - 36), 2, (170, 174, 190))
        R(draw, x0 + x_end - 2, 42, 4, 6, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def ide_link():
    f = ide_frame
    frames = intro(f)
    for k in range(6):                                                       # the plug travels across and clicks in
        frames.append(f(cable=(k + 1) / 6, look=(2, 1), bob=1 if k == 0 else 0))
    frames += [f(cable=1.0, linked=True, look=(2, 0), bob=-1)] + [f(cable=1.0, linked=True, look=(2, 0))] * 2
    frames += [f(cable=1.0, linked=True, sel=True, look=(2, 1), key=k == 0, bob=1 if k == 0 else 0) for k in range(4)]
    for k in range(3):                                                       # the selected line shows up in the terminal
        frames.append(f(cable=1.0, linked=True, sel=True, chip=k > 0, look=(2, 1)))
    frames += [f(cable=1.0, linked=True, sel=True, chip=True, look=(2, 0), blink=k == 4, bob=-1 if k == 0 else 0) for k in range(7)]
    frames += [f(cable=1.0, linked=True, sel=False, chip=False)]
    for k in range(5):
        frames.append(f(cable=1.0 - (k + 1) / 5, linked=k < 2))
    return frames + [f(blink=True), f()]


def ide_diff():
    f = ide_frame
    frames = intro(f)
    for k in range(5):
        frames.append(f(cable=(k + 1) / 5, look=(2, 1)))
    frames += [f(cable=1.0, linked=True, look=(2, 0), bob=-1)] * 3
    for k in range(6):                                                       # Clawd edits, the diff appears in the IDE
        frames.append(f(cable=1.0, linked=True, diff=1, look=(2, 1 + (k % 4 > 1)), key=k % 2 == 0, bob=k % 2))
    frames += [f(cable=1.0, linked=True, diff=1, ok=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(7)]
    frames += [f(cable=1.0, linked=True)]
    for k in range(5):
        frames.append(f(cable=1.0 - (k + 1) / 5, linked=k < 2))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("tool-failure", fail_frame, [tool_fail_retry, tool_fail_fix])
    finish("todo-list", todo_frame, [todo_run, todo_add])
    finish("session-end", term_frame, [end_exit, end_summary])
    finish("teammate-idle", mates_frame, [mates_wait, mates_ping])
    finish("rewind", rewind_frame, [rewind_branch, rewind_scrub])
    finish("skills", skills_frame, [lambda: skills_load(0), lambda: skills_load(1)])
    finish("scheduled-task", clock_frame, [clock_run, clock_repeat])
    finish("ide-connected", ide_frame, [ide_link, ide_diff])
