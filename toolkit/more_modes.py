"""More modes and effort: mode-default, mode-sandbox, effort-ultrathink, effort-adaptive.

python more_modes.py  ->  ../mine/<set>/
"""
import math

from props import *
from effort_sets import effort_frame, dial, steam as steam_puffs, ZONES, LID

BOX = (36, 40, 52)
GREYT = (130, 136, 156)


# ---------------------------------------------------------------- default mode: every step is asked first
def act_icon(draw, x, y, kind, col):
    if kind == 0:                                                            # read: an eye
        R(draw, x, y + 3, 10, 4, col)
        R(draw, x + 2, y + 2, 6, 6, col)
        R(draw, x + 4, y + 3, 2, 4, (14, 18, 26))
    elif kind == 1:                                                          # edit: a pencil
        for i in range(8):
            R(draw, x + 1 + i, y + 8 - i, 2, 2, col)
        R(draw, x, y + 8, 2, 2, col)
    else:                                                                    # run: a terminal prompt
        R(draw, x, y + 1, 11, 1, col)
        R(draw, x, y + 9, 11, 1, col)
        R(draw, x, y + 1, 1, 9, col)
        R(draw, x + 10, y + 1, 1, 9, col)
        R(draw, x + 2, y + 3, 2, 2, col)
        R(draw, x + 4, y + 5, 2, 2, col)
        R(draw, x + 2, y + 7, 2, 1, col)
        R(draw, x + 6, y + 7, 3, 1, col)


ROW_Y = (16, 28, 40)
ROW_W = (30, 36, 26)


def default_frame(rows=(0, 0, 0), pulse=0, ask=None, hot=None, flash=None, cursor_xy=None, look=(2, 1), blink=False, bob=0,
                  slide=0, sweat_f=None, key=False, smile=False):
    """rows: 0 pending, 1 asking, 2 allowed, 3 denied. ask = row index whose dialog is open."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 68, 7, 16, 7, AMBER)                                        # mode badge: "?"
    text(draw, x0 + 74, 8, "?", DARK, 1)
    for i, st in enumerate(rows):
        y = ROW_Y[i]
        col = [(90, 96, 116), AMBER if pulse % 2 == 0 else (170, 120, 40), GREEN, RED][st]
        R(draw, x0 + 6, y - 2, 12, 12, BOX)
        R(draw, x0 + 7, y - 1, 10, 10, (20, 24, 34))
        act_icon(draw, x0 + 7, y - 1, i, col if st != 0 else (110, 116, 136))
        R(draw, x0 + 22, y + 2, ROW_W[i], 3, (150, 156, 176) if st < 2 else (80, 86, 104))
        R(draw, x0 + 22, y + 6, ROW_W[i] - 10, 2, (100, 106, 126) if st < 2 else (64, 70, 88))
        if st == 2:
            tick(draw, x0 + 68, y + 1, GREEN, 2)
        if st == 3:
            cross(draw, x0 + 68, y + 1, RED, 2)
    if ask is not None:                                                      # the permission dialog
        R(draw, x0 + 12, 19, 62, 30, (150, 154, 168))
        R(draw, x0 + 13, 20, 60, 28, (30, 34, 46))
        act_icon(draw, x0 + 17, 23, ask, AMBER)
        R(draw, x0 + 32, 24, 34, 2, (225, 228, 235))
        R(draw, x0 + 32, 29, 24, 2, GREYT)
        R(draw, x0 + 20, 38, 22, 8, WHITE if flash == "allow" else (90, 200, 120) if hot == "allow" else (45, 110, 65))
        tick(draw, x0 + 28, 39, DARK if flash == "allow" else WHITE)
        R(draw, x0 + 46, 38, 22, 8, WHITE if flash == "deny" else (235, 100, 100) if hot == "deny" else (125, 55, 55))
        cross(draw, x0 + 54, 39, DARK if flash == "deny" else WHITE)
    if cursor_xy:
        cursor(draw, *cursor_xy)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def ask_step(f, rows, i, choice="allow", look_dy=1):
    """One asked step: dialog opens, the cursor goes to the button and clicks. Returns frames and the new rows."""
    frames = []
    r = list(rows)
    r[i] = 1
    x0 = PX0
    target = (x0 + (30 if choice == "allow" else 56), 40)
    for k in range(2):
        frames.append(f(tuple(r), pulse=k, ask=i, look=(2, look_dy)))
    for k in range(5):
        t = ease((k + 1) / 5)
        frames.append(f(tuple(r), ask=i, cursor_xy=(round(lerp(x0 + 80, target[0], t)), round(lerp(54, target[1], t))),
                        hot=choice if k > 3 else None, look=(2, 2 if k > 1 else look_dy)))
    frames += [f(tuple(r), ask=i, cursor_xy=target, flash=choice, look=(2, 2), bob=1)] * 2
    r[i] = 2 if choice == "allow" else 3
    frames.append(f(tuple(r), look=(2, look_dy)))
    return frames, r


def default_allow():
    f = default_frame
    frames = intro(f)
    rows = [0, 0, 0]
    for i in range(3):
        fr, rows = ask_step(f, rows, i, "allow", i)
        frames += fr
        frames += [f(tuple(rows), look=(2, i), bob=-1 if k == 0 else 0, key=k > 1 and k < 4) for k in range(3)]
    frames += [f((2, 2, 2), smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in range(3):
        frames.append(f(tuple(2 if j < 2 - k else 0 for j in range(3))))
    return frames + [f(blink=True), f()]


def default_deny():
    f = default_frame
    frames = intro(f)
    rows = [0, 0, 0]
    fr, rows = ask_step(f, rows, 0, "allow", 0)
    frames += fr
    fr, rows = ask_step(f, rows, 1, "deny", 1)                              # the second step is refused
    frames += fr
    frames += [f(tuple(rows), sweat_f=k, look=(1, 1), bob=k % 2) for k in range(4)]
    frames += [f(tuple(rows), sweat_f=k, look=(2, 2), key=k % 2 == 0, bob=k % 2) for k in range(6)]   # he rethinks the step
    rows[1] = 0
    fr, rows = ask_step(f, rows, 1, "allow", 1)                              # and asks again, differently
    frames += fr
    fr, rows = ask_step(f, rows, 2, "allow", 2)
    frames += fr
    frames += [f(tuple(rows), smile=True, look=(2, 0), bob=-1 if k == 0 else 0) for k in range(6)]
    for k in range(3):
        frames.append(f(tuple(2 if j < 2 - k else 0 for j in range(3))))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- sandbox mode: free to play inside, the walls hold
SAND = (214, 190, 130)
FILE_X = (14, 28, 42)


def sandbox_frame(packet=None, ticks=(), gate=0, blocked=None, globe=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0,
                  smile=False, shake=0):
    """gate 0 closed, 1 open. blocked = (x, y) spot on the wall where something just bounced (red flash)."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    bx, by, bw, bh = x0 + 8, 12, 52, 40
    for x in range(bx, bx + bw, 4):                                          # dashed wall
        for y in (by, by + bh - 1):
            R(draw, x + shake, y, 2, 1, (110, 170, 230))
    for y in range(by, by + bh, 4):
        R(draw, bx + shake, y, 1, 2, (110, 170, 230))
        if not (28 <= y <= 38):
            R(draw, bx + bw - 1 + shake, y, 1, 2, (110, 170, 230))
    R(draw, bx + 1, 46, bw - 2, 5, SAND)                                     # sand at the bottom
    for k in range(5):
        R(draw, bx + 4 + k * 9, 45, 3, 1, SAND)
    for i, fx in enumerate(FILE_X):                                          # files in the box
        R(draw, x0 + fx, 32, 9, 12, WHITE)
        R(draw, x0 + fx + 2, 35, 5, 1, (150, 156, 176))
        R(draw, x0 + fx + 2, 38, 4, 1, (150, 156, 176))
        if i in ticks:
            tick(draw, x0 + fx + 2, 26, GREEN, 1)
    R(draw, bx + bw - 2, 28, 4, 11, GREEN if gate else RED)                  # the gate in the wall
    cx, cy = x0 + 71, 34                                                     # the outside world
    dot(draw, cx, cy, 8, (80, 190, 130) if globe else (70, 76, 92))
    R(draw, cx - 8, cy, 17, 1, (30, 34, 46))
    R(draw, cx, cy - 8, 1, 17, (30, 34, 46))
    if globe and tickmark:
        tick(draw, cx - 3, cy - 14, GREEN, 2)
    if packet:
        dot(draw, x0 + packet[0], packet[1], 2, WHITE)
    if blocked:
        R(draw, x0 + blocked[0] - 1, blocked[1] - 3, 3, 7, RED)
        cross(draw, x0 + blocked[0] + 3, blocked[1] - 3, RED, 1)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def sandbox_inside():
    f = sandbox_frame
    frames = intro(f)
    ticks = []
    for i, fx in enumerate(FILE_X):                                          # works on the files inside: all fine
        for k in range(4):
            t = (k + 1) / 4
            sx = FILE_X[i - 1] + 4 if i else 12
            frames.append(f(packet=(round(lerp(sx, fx + 4, t)), round(26 - 5 * math.sin(t * math.pi))), ticks=tuple(ticks),
                            look=(2, 1 + (k > 1))))
        ticks.append(i)
        frames += [f(ticks=tuple(ticks), bob=1, look=(2, 2))]
    frames += [f(ticks=tuple(ticks), smile=True, look=(2, 1)) for k in range(3)]
    for k in range(5):                                                       # then it reaches for the outside: bounced
        t = (k + 1) / 5
        frames.append(f(packet=(round(lerp(46, 56, t)), 34), ticks=tuple(ticks), look=(2, 1), shake=0))
    for k in range(4):
        frames.append(f(packet=(round(lerp(56, 40, (k + 1) / 4)), 34), ticks=tuple(ticks), blocked=(58, 34), shake=(-1, 1)[k % 2],
                        look=(1, 1), bob=1 if k == 0 else 0))
    frames += [f(ticks=tuple(ticks), smile=True, look=(2, 1), blink=k == 3) for k in range(5)]
    for k in range(3):
        frames.append(f(ticks=tuple(ticks[:2 - k]) if k < 2 else ()))
    return frames + [f(blink=True), f()]


def sandbox_gate():
    f = sandbox_frame
    frames = intro(f)
    for k in range(3):
        frames.append(f(gate=1, look=(2, 1)))
    for k in range(7):                                                       # an allowed host: the gate opens and a packet goes out
        t = (k + 1) / 7
        frames.append(f(gate=1, packet=(round(lerp(40, 71, t)), 34), globe=1 if k > 4 else 0, look=(2, 1)))
    frames += [f(gate=1, globe=1, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0) for k in range(5)]
    for k in range(3):
        frames.append(f(gate=1 if k < 2 else 0, globe=1 if k < 1 else 0))
    for k in range(4):                                                       # a different route is closed
        t = (k + 1) / 4
        frames.append(f(packet=(round(lerp(40, 56, t)), round(lerp(34, 18, t))), look=(2, 0)))
    for k in range(4):
        frames.append(f(packet=(round(lerp(56, 40, (k + 1) / 4)), 18), blocked=(58, 18), shake=(-1, 1)[k % 2], look=(1, 1)))
    frames += [f(smile=True, look=(2, 1), blink=k == 2) for k in range(4)]
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- ultrathink: past max
ZONES6 = ZONES + [(170, 110, 240)]
RAINBOW = (RED, ORANGE, YELLOW, GREEN, (80, 200, 200), LIGHT_BLUE, PURPLE, PINK)


def dial6(draw, x0, needle, shake=0, hot=False):
    cx, cy, ro, ri = 44, 54, 34, 27
    lit = min(5, int(needle + 0.5))
    for deg in range(0, 181):
        zone = min(5, deg // 30)
        a = math.radians(180 - deg)
        for r in range(ri, ro + 1):
            if deg % 30 in (0, 29) and r < ro - 1:
                continue
            c = ZONES6[zone] if zone == lit else mix(ZONES6[zone], (20, 24, 34), 0.72)
            R(draw, round(x0 + cx + math.cos(a) * r) + shake, round(cy - math.sin(a) * r), 1, 1, c)
    ang = math.radians(180 - (15 + 30 * needle))
    for r in range(0, ri - 3):
        R(draw, round(x0 + cx + math.cos(ang) * r) + shake, round(cy - math.sin(ang) * r), 2, 2, WHITE)
    dot(draw, x0 + cx + shake, cy, 3, (200, 204, 215))


def ultra_frame(needle=2.0, word=0, shift=0, rings=0, rays=False, f=0, shake=0, steam_on=False, sweat_on=False, spark=False,
                key=False, look=(2, 1), blink=False, bob=0, slide=0, lid=0.0, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    dial6(draw, x0, needle, shake)
    for i in range(word):                                                    # the keyword, in rainbow colours
        R(draw, x0 + 8 + i * 8, 8, 6, 8, RAINBOW[(i + shift) % 8])
    if rays:
        for k in range(10):
            a = k * math.pi / 5 + f * 0.15
            r0, r1 = 36, 44 + (f + k) % 4 * 2
            R(draw, round(x0 + 44 + math.cos(a) * r1), round(54 - abs(math.sin(a)) * r1), 2, 2, (200, 170, 255))
    for k in range(rings):                                                   # shock rings from the dial hub
        rr = 6 + k * 9 + (f % 3) * 2
        for deg in range(0, 181, 3):
            a = math.radians(deg)
            R(draw, round(x0 + 44 + math.cos(a) * rr), round(54 - math.sin(a) * rr), 1, 1, mix((170, 110, 240), WHITE, 0.4))
    if spark:
        for k, (sx, sy) in enumerate(((10, 24), (78, 26), (60, 18), (26, 20))):
            if (f + k * 2) % 5 < 2:
                R(draw, x0 + sx, sy, 1, 3, YELLOW)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob, lid=lid, dx=shake)
    if smile:
        draw_smile(draw, OX + 4 * G + shake, OY + 2 * G + 1 + bob)
    if steam_on:
        steam_puffs(draw, f, True)
    if sweat_on:
        sweat(draw, bob, f)
    if key:
        key_press(draw, bob)
    return img


def ultra_burst():
    f = ultra_frame
    frames = intro(f)
    for k in range(8):                                                       # the keyword is typed
        frames.append(f(word=k + 1, shift=k, key=k % 2 == 0, bob=k % 2, look=(2, 0)))
    for k in range(6):                                                       # the needle swings past max into the purple
        frames.append(f(needle=lerp(2.0, 5.0, ease((k + 1) / 6)), word=8, shift=k, f=k, look=(2, 0), bob=-1 if k == 5 else 0,
                        shake=(-1, 1)[k % 2] if k > 3 else 0))
    for k in range(10):                                                      # holds, everything glows
        frames.append(f(needle=5.0 + 0.15 * math.sin(k * 1.6), word=8, shift=k, f=k, rays=True, steam_on=True, sweat_on=True,
                        spark=True, shake=(-1, 1)[k % 2], key=k % 2 == 0, bob=k % 2, look=(2, 1 + (k % 6 > 3))))
    for k in range(6):                                                       # and comes back down
        frames.append(f(needle=lerp(5.0, 2.0, ease((k + 1) / 6)), word=max(0, 8 - 2 * k), shift=k, f=k, steam_on=k < 3,
                        sweat_on=k < 4, look=(2, 1)))
    return frames + [f(blink=True), f()]


def ultra_pulse():
    f = ultra_frame
    frames = intro(f)
    for k in range(4):
        frames.append(f(word=8, shift=k, look=(2, 0), key=k % 2 == 0, bob=k % 2))
    for rnd in range(2):                                                     # two surges, each with a shock ring
        for k in range(4):
            frames.append(f(needle=lerp(2.0, 5.0, ease((k + 1) / 4)), word=8, shift=k + rnd * 3, f=k, rings=1 + k // 2, spark=True,
                            shake=(-1, 1)[k % 2], steam_on=True, look=(2, 0)))
        for k in range(4):
            frames.append(f(needle=5.0 - 0.1 * k, word=8, shift=k, f=k + 4, rings=3, rays=True, steam_on=True, sweat_on=True,
                            shake=(-1, 1)[k % 2], look=(2, 1)))
        for k in range(3):
            frames.append(f(needle=lerp(5.0, 3.0, ease((k + 1) / 3)), word=8, shift=k, f=k, steam_on=True, sweat_on=True, look=(2, 2)))
    for k in range(6):
        frames.append(f(needle=lerp(3.0, 2.0, ease((k + 1) / 6)), word=max(0, 8 - k * 2), look=(2, 1)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- adaptive effort: the needle follows the task
def adaptive_frame(needle=1.0, task=None, thinking=False, f=0, look=(2, 1), blink=False, bob=0, slide=0, smile=False, key=False):
    """The dial follows the difficulty of the task on its own. task = number of blocks in the difficulty strip."""
    n = task if task is not None else 1 + round(needle * 1.25)
    level = max(0, min(4, int(needle + 0.5)))
    lid = max(0.0, 0.45 * (1 - needle))
    img = effort_frame(level, needle=needle, f=f, sweat_on=needle > 2.2, steam_on=needle > 3.2, flame=needle > 3.6,
                       key=key or needle > 0.8, shake=(-1, 1)[f % 2] if needle > 3.8 else 0, spark=needle > 3.8, look=look,
                       blink=blink, bob=bob if bob else (1 if needle > 0.8 and f % 2 == 0 else 0), slide=slide, lid=lid, smile=smile)
    draw = ImageDraw.Draw(img)
    x0 = PX0 + slide
    for i in range(7):                                                       # the difficulty strip
        c = ZONES[min(4, i * 5 // 7)] if i < n else (46, 50, 62)
        R(draw, x0 + 8 + i * 7, 8, 5, 6, c)
    ax, ay = x0 + 76, 10                                                     # the "auto" ring with an arrow
    for deg in range(0, 360, 20):
        a = math.radians(deg)
        R(draw, round(ax + math.cos(a) * 4), round(ay + math.sin(a) * 4), 1, 1, AMBER if thinking else (80, 86, 104))
    R(draw, ax + 3, ay - 5, 3, 1, AMBER if thinking else (80, 86, 104))
    return img


def adaptive_run(order):
    f = adaptive_frame
    frames = intro(f)
    needle = 1.0
    fcount = 0
    for target in order:
        for k in range(7):                                                   # the needle decides and moves in steps
            needle_k = lerp(needle, target, ease((k + 1) / 7))
            frames.append(f(needle_k, task=None, thinking=True, f=fcount, look=(2, 1 - (target > needle) + (target < needle))))
            fcount += 1
        needle = target
        for k in range(8):                                                   # works at that level for a moment
            frames.append(f(needle + 0.08 * math.sin(k * 1.3), f=fcount, look=(2, 1 + (k % 6 > 3)), blink=k == 7 and needle < 2))
            fcount += 1
    for k in range(7):
        frames.append(f(lerp(needle, 1.0, ease((k + 1) / 7)), thinking=True, f=fcount))
        fcount += 1
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("mode-default", default_frame, [default_allow, default_deny])
    finish("mode-sandbox", sandbox_frame, [sandbox_inside, sandbox_gate])
    finish("effort-ultrathink", ultra_frame, [ultra_burst, ultra_pulse])
    finish("effort-adaptive", adaptive_frame, [lambda: adaptive_run((0.3, 3.6, 2.0)), lambda: adaptive_run((3.0, 0.2, 4.0))])
