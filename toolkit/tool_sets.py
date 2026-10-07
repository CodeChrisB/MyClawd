"""Five tool sets: tools (plug in), permission, deploy, database, download.

python tool_sets.py  ->  ../mine/{tools,permission,deploy,database,download}/
Every set's seam pose = its panel at rest (nothing in progress), see clawd.md.
"""
import random

from props import *
from PIL import ImageDraw


def finish(name, frame, loops):
    enter, leave = seam_slides(frame)
    save_set(name, enter, loops, leave)


def eyes(y):
    return (2, y)


# ---------------------------------------------------------------- tools: Clawd plugs a cable into the tool socket
TILES = [LIGHT_BLUE, PINK, AMBER]


def tools_frame(cable=None, tiles=(0, 0, 0), led=False, spark=None, look=(2, 1), blink=False, bob=0, slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 4, 10, 5, 5, GREEN if led else GREY)                       # status light
    R(draw, x0 + 2, 24, 8, 12, (90, 94, 108))                               # socket
    R(draw, x0 + 4, 27, 2, 2, DARK)
    R(draw, x0 + 4, 32, 2, 2, DARK)
    R(draw, x0 + 10, 29, 70, 1, GREY)                                       # bus line
    for i, c in enumerate(TILES):
        tx = x0 + 22 + i * 21
        R(draw, tx + 6, 30, 2, 4, GREY)                                     # stem
        level = tiles[i]
        R(draw, tx, 34, 14, 14, c if level else (36, 40, 52))
        if level:
            R(draw, tx + 4, 38, 6, 6, WHITE if level == 2 else DARK)
    if cable is not None:                                                  # cable from Clawd's hand to the socket
        R(draw, OX + 10 * G, OY + 3 * G + 1, max(0, cable - (OX + 10 * G)), 2, (150, 154, 168))
        R(draw, cable - 2, OY + 3 * G - 1, 4, 6, YELLOW)
    if spark is not None:
        R(draw, spark, 28, 3, 3, WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def tools_connect(calls):
    sock = PX0 + 1
    frames = [tools_frame()] * 3
    for i in range(9):                                                      # cable reaches out
        x = round(OX + 10 * G + (sock - OX - 10 * G) * ease((i + 1) / 9))
        frames.append(tools_frame(cable=x, bob=i % 2))
    frames += [tools_frame(cable=sock, led=True, spark=PX0 + 6)] + [tools_frame(cable=sock, led=True)] * 2
    for t in range(3):
        frames += [tools_frame(cable=sock, led=True, tiles=tuple(1 if j <= t else 0 for j in range(3)))] * 3
    for _ in range(calls):                                                  # a call travels along the bus to a tile
        for t in range(3):
            tx = PX0 + 29 + t * 21
            for k in range(4):
                sx = round(PX0 + 12 + (tx - PX0 - 12) * (k + 1) / 4)
                tiles = [1, 1, 1]
                frames.append(tools_frame(cable=sock, led=True, tiles=tuple(tiles), spark=sx, look=(2, 1 + k % 2)))
            tiles = [1, 1, 1]
            tiles[t] = 2
            frames += [tools_frame(cable=sock, led=True, tiles=tuple(tiles), look=(2, 2))] * 2
    frames += [tools_frame(cable=sock, led=True, tiles=(1, 1, 1), blink=True)]
    for t in (2, 1, 0):
        frames += [tools_frame(cable=sock, led=True, tiles=tuple(1 if j < t else 0 for j in range(3)))] * 2
    frames += [tools_frame(cable=sock, led=False)]
    for i in range(9):                                                      # cable winds back
        x = round(sock - (sock - OX - 10 * G) * ease((i + 1) / 9))
        frames.append(tools_frame(cable=x if i < 8 else None, bob=i % 2 if i < 8 else 0))
    return frames + [tools_frame()]


# ---------------------------------------------------------------- permission: waiting for an Allow click
def lock(draw, x, y, state, dx=0):
    """state: closed, open, denied. Body 16x12 with a shackle above. Open: the shackle lifts, its long leg stays in the body,
    only the other leg comes out."""
    body = {"closed": AMBER, "open": GREEN, "denied": RED}[state]
    sx = x + dx
    up = 4 if state == "open" else 0
    steel = (190, 194, 205)
    R(draw, sx + 3, y - 8 - up, 2, 8 + up, steel)                            # the leg that stays in the body
    R(draw, sx + 11, y - 8 - up, 2, 8, steel)                                # the free leg: lifted clear of the body when open
    R(draw, sx + 3, y - 10 - up, 10, 2, steel)
    R(draw, sx, y, 16, 12, body)
    R(draw, sx + 7, y + 3, 2, 4, DARK)


def perm_frame(state="closed", cur=None, hot=None, flash=None, shake=0, mark=None, look=(2, 1), blink=False, bob=0, slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    lock(draw, x0 + 12, 30, state, shake)
    ya, yd = 22, 38
    R(draw, x0 + 50, ya, 28, 11, WHITE if flash == "allow" else (90, 200, 120) if hot == "allow" else (45, 110, 65))
    tick(draw, x0 + 61, ya + 3, DARK if flash == "allow" else WHITE)
    R(draw, x0 + 50, yd, 28, 11, WHITE if flash == "deny" else (235, 100, 100) if hot == "deny" else (125, 55, 55))
    cross(draw, x0 + 61, yd + 3, DARK if flash == "deny" else WHITE)
    if mark == "ok":
        tick(draw, x0 + 13, 4, GREEN, 2)
    elif mark == "no":
        cross(draw, x0 + 13, 4, RED, 2)
    if cur:
        cursor(draw, *cur)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def perm_take(choice):
    x0 = PX0
    ty = 27 if choice == "allow" else 43
    target = (x0 + 64, ty)
    start = (x0 + 84, 54)
    look = (2, 0) if choice == "allow" else (2, 2)
    frames = [perm_frame()] * 4 + [perm_frame(blink=True), perm_frame()] + [perm_frame()] * 2
    for i in range(9):
        t = ease((i + 1) / 9)
        pos = (round(start[0] + (target[0] - start[0]) * t), round(start[1] + (target[1] - start[1]) * t))
        frames.append(perm_frame(cur=pos, look=(2, 1 if i < 5 else look[1])))
    frames += [perm_frame(cur=target, hot=choice, look=look)] * 3
    frames += [perm_frame(cur=target, flash=choice, look=look, bob=1)] * 2
    if choice == "allow":
        for k, st in enumerate(("closed", "open", "open", "open", "open", "open", "open")):
            frames.append(perm_frame(st, cur=target, hot=choice, mark="ok" if k > 0 else None, look=(2, 1)))
        for i in range(6):
            frames.append(perm_frame("open", cur=(target[0] + i * 4, target[1] + i * 3), mark="ok" if i < 3 else None))
        frames += [perm_frame("closed", look=(2, 1), blink=True)]
    else:
        for k in range(8):
            frames.append(perm_frame("denied", cur=target, hot=choice, shake=(-1, 1)[k % 2] if k < 6 else 0,
                                     mark="no" if k > 1 else None, look=(1, 1)))
        for i in range(6):
            frames.append(perm_frame("denied", cur=(target[0] + i * 4, target[1] - i * 3), mark="no" if i < 3 else None))
        frames += [perm_frame("closed", look=(2, 1), blink=True)]
    return frames + [perm_frame()]


# ---------------------------------------------------------------- deploy: bar fills, rocket lifts off, new rocket arrives
def rocket(draw, cx, top):
    R(draw, cx - 4, top + 6, 8, 18, (225, 228, 235))
    for i, w in enumerate((2, 4, 6, 8)):
        R(draw, cx - w // 2, top + 2 + i, w, 1, RED)
    R(draw, cx - 4, top + 6, 8, 1, RED)
    R(draw, cx - 1, top + 11, 3, 3, BLUE)
    R(draw, cx - 7, top + 18, 3, 6, RED)
    R(draw, cx + 4, top + 18, 3, 6, RED)


def deploy_frame(bar=0, rocket_y=0, smoke=(), check=False, dots=None, shake=0, ground_cover=True, look=(2, 1),
                 blink=False, bob=0, slide=0, flame=False, no_rocket=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    cx = x0 + 44
    R(draw, x0 + 6, 10, 76, 5, (36, 40, 52))
    if dots is None:
        R(draw, x0 + 7, 11, round(74 * bar), 3, GREEN)
    else:                                                                    # countdown lights
        for i in range(3):
            lit = i < dots
            R(draw, x0 + 30 + i * 12, 9, 6, 6, (GREEN if i == 2 else AMBER) if lit else (36, 40, 52))
    layer, ld = new_frame()                                                  # rocket and smoke, clipped to the panel
    for sx, sy, r in smoke:
        R(ld, cx + sx - r, sy - r, 2 * r, 2 * r, (150, 154, 166))
    if not no_rocket:
        top = 27 + rocket_y
        rocket(ld, cx + shake, top)
        if flame:
            R(ld, cx - 2 + shake, top + 24, 4, 5, ORANGE)
            R(ld, cx - 1 + shake, top + 29, 2, 3, YELLOW)
    img.alpha_composite(layer.crop((x0, PY0, x0 + 89, PY1 + 1)), (x0, PY0))
    draw = ImageDraw.Draw(img)
    R(draw, x0 + 2, 52, 85, 6, (40, 44, 54))                                  # ground covers the rocket's base
    if check:
        tick(draw, cx - 8, 24, GREEN, 4)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def deploy_end():
    """Check shows, then a new rocket rises out of the ground. Ends on the seam."""
    frames = [deploy_frame(no_rocket=True, check=True, look=(2, 0))] * 6 + [deploy_frame(no_rocket=True, blink=True)]
    for k in range(6):
        frames.append(deploy_frame(rocket_y=round(22 * (1 - ease((k + 1) / 6)))))
    return frames


def deploy_launch(bar_frames, dots):
    frames = [deploy_frame()] * 3
    if dots is None:
        for i in range(bar_frames):
            frames += [deploy_frame(bar=ease((i + 1) / bar_frames), look=(2, 1 + (i // 3) % 2))]
    else:
        for d in range(1, 4):
            frames += [deploy_frame(dots=d, look=(2, 1))] * 4
    frames += [deploy_frame(bar=1.0, dots=None if dots is None else 3, shake=(-1) ** k, flame=True, bob=k % 2,
                            smoke=[(-10, 54, 2), (10, 54, 2)]) for k in range(4)]
    for k in range(10):
        t = ease((k + 1) / 10)
        y = round(-48 * t - 8 * (k > 4))
        smoke = [(-8 - j, 54 - j * 3, 2 + j // 2) for j in range(3)] + [(8 + j, 54 - j * 3, 2 + j // 2) for j in range(3)]
        frames.append(deploy_frame(bar=1.0, dots=None if dots is None else 3, rocket_y=y, flame=True, smoke=smoke,
                                   look=(2, 0)))
    return frames + deploy_end()


# ---------------------------------------------------------------- database: records fly out of / into the cylinder
REC = [LIGHT_BLUE, PINK, AMBER, GREEN]


def cylinder(draw, x, y, pulse=None, flash=None):
    for k in range(3):
        base = (70, 110, 180) if flash != k else (90, 200, 120)
        if pulse == k:
            base = (110, 150, 220)
        yy = y + k * 10
        R(draw, x, yy, 18, 9, base)
        R(draw, x, yy, 18, 1, (130, 170, 235))
        R(draw, x, yy + 8, 18, 1, (45, 75, 130))
        R(draw, x + 13, yy + 3, 3, 2, (45, 75, 130))


def slot_y(i):
    return 14 + i * 10


def db_frame(slots=(), flying=None, pulse=None, flash=None, look=(2, 1), blink=False, bob=0, slide=0, mark=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    cylinder(draw, x0 + 8, 18, pulse, flash)
    for i in range(4):
        R(draw, x0 + 38, slot_y(i), 44, 7, (36, 40, 52))
        R(draw, x0 + 39, slot_y(i) + 1, 42, 5, DARK)
    for i, w in slots:
        R(draw, x0 + 39, slot_y(i) + 1, w, 5, REC[i])
    if flying:
        fx, fy, c = flying
        R(draw, x0 + fx, fy, 12, 5, c)
    if mark:
        tick(draw, x0 + 12, 6, GREEN, 2)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


WIDTHS = [30, 22, 36, 26]


def db_query():
    frames = [db_frame()] * 4 + [db_frame(blink=True)] + [db_frame()] * 2
    done = []
    for i in range(4):
        for k in range(4):
            t = (k + 1) / 4
            fy = round(26 + (slot_y(i) + 1 - 26) * t)
            frames.append(db_frame(done, (round(26 + 13 * t), fy, REC[i]), pulse=i % 3 if k < 2 else None,
                                   look=(2, min(2, max(0, (fy - 14) // 12)))))
        done = done + [(i, WIDTHS[i])]
        frames += [db_frame(done, look=(2, min(2, i)))]
    frames += [db_frame(done, mark=True)] * 6
    for i in (3, 2, 1, 0):
        done = [d for d in done if d[0] != i]
        frames += [db_frame(done)] * 2
    return frames + [db_frame()]


def db_insert():
    frames = [db_frame()] * 3 + [db_frame(blink=True)] + [db_frame()] * 2
    shown = []
    for i in range(3):
        shown = shown + [(i, WIDTHS[i])]
        frames += [db_frame(shown, look=(2, min(2, i)))] * 3
    frames += [db_frame(shown, look=(2, 1))] * 2
    for i in (0, 1, 2):
        shown = [s for s in shown if s[0] != i]
        for k in range(4):
            t = (k + 1) / 4
            frames.append(db_frame(shown, (round(26 + 13 * (1 - t)), round(slot_y(i) + 1 + (26 - slot_y(i) - 1) * t), REC[i]),
                                   look=(2, 1)))
        frames += [db_frame(shown, flash=i, bob=1)] * 2
    frames += [db_frame(mark=True)] * 6
    return frames + [db_frame()]


# ---------------------------------------------------------------- download: bar + packages falling into a tray
def tray(draw, x, packages):
    R(draw, x, 46, 34, 2, (150, 154, 168))
    R(draw, x, 38, 2, 10, (150, 154, 168))
    R(draw, x + 32, 38, 2, 10, (150, 154, 168))
    for k in range(packages):
        R(draw, x + 3 + (k % 3) * 10, 41 - (k // 3) * 6 + 1, 8, 5, AMBER)
        R(draw, x + 3 + (k % 3) * 10, 41 - (k // 3) * 6 + 1, 8, 1, YELLOW)


def file_icon(draw, x, y):
    R(draw, x, y, 7, 9, WHITE)
    R(draw, x + 4, y, 3, 3, (170, 174, 186))
    R(draw, x + 1, y + 4, 5, 1, (150, 154, 168))
    R(draw, x + 1, y + 6, 4, 1, (150, 154, 168))


def dl_frame(bar=0.0, arrow=0, packages=0, falling=None, files=(), dots=0, tickmark=False, look=(2, 1), blink=False,
             bob=0, slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 6, 10, 76, 6, (36, 40, 52))
    R(draw, x0 + 7, 11, round(74 * bar), 4, GREEN if bar >= 1 else LIGHT_BLUE)
    c = LIGHT_BLUE if (bar > 0 or files or dots) else GREY
    if tickmark:                                                             # the arrow turns into a big check
        tick(draw, x0 + 7, 27, GREEN, 4)
    else:
        R(draw, x0 + 10, 24 + arrow, 7, 10, c)                               # arrow shaft
        for i, w in enumerate((15, 13, 11, 9, 7, 5, 3, 1)):
            R(draw, x0 + 13 - w // 2, 34 + arrow + i, w, 1, c)
    tray(draw, x0 + 44, packages)
    if falling:
        fx, fy = falling
        R(draw, x0 + fx, fy, 8, 5, AMBER)
    for fx, fy in files:
        file_icon(draw, x0 + fx, fy)
    for i in range(3):
        R(draw, x0 + 30 + i * 8, 20, 5, 3, GREEN if i < dots else (36, 40, 52))
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def dl_bar():
    frames = [dl_frame()] * 4 + [dl_frame(blink=True)] + [dl_frame()] * 2
    pk = 0
    for i in range(18):
        bar = (i + 1) / 18
        arrow = (i % 4 > 1) * 2
        fall = None
        if i % 6 in (1, 2, 3, 4):
            fall = (62, 22 + ((i % 6) - 1) * 6)
        if i % 6 == 5 and pk < 5:
            pk += 1
        frames.append(dl_frame(bar, arrow, pk, fall, look=(2, 1 + (i % 6 > 2))))
    frames += [dl_frame(1.0, 0, pk, tickmark=True, look=(2, 0))] * 8
    for k in (4, 2, 0):
        frames += [dl_frame(max(0, k / 5), 0, min(pk, k))] * 2
    return frames + [dl_frame()]


def dl_files():
    frames = [dl_frame()] * 3 + [dl_frame(blink=True)] + [dl_frame()] * 2
    landed = 0
    for n in range(3):
        for k in range(6):
            t = (k + 1) / 6
            frames.append(dl_frame(0.1, (k % 2) * 2, landed, files=[(60 + n * 8, round(18 + 24 * ease(t)))], dots=n,
                                   look=(2, 1 + (k > 2))))
        landed = (n + 1) * 2
        frames += [dl_frame(0.1, 0, landed, dots=n + 1, bob=1)] * 2
    frames += [dl_frame(1.0, 0, landed, dots=3, tickmark=True, look=(2, 0))] * 7
    frames += [dl_frame(0.5, 0, 2, dots=1)] * 2 + [dl_frame(0.0, 0, 0)]
    return frames + [dl_frame()]


if __name__ == "__main__":
    finish("tools", tools_frame, [lambda: tools_connect(1), lambda: tools_connect(2)])
    finish("permission", perm_frame, [lambda: perm_take("allow"), lambda: perm_take("deny")])
    finish("deploy", deploy_frame, [lambda: deploy_launch(14, None), lambda: deploy_launch(0, 3)])
    finish("database", db_frame, [db_query, db_insert])
    finish("download", dl_frame, [dl_bar, dl_files])
