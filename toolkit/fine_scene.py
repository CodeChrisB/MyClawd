"""this-is-fine: Clawd walks into a burning room, sits on a chair next to a table with a mug and says it is fine.

python fine_scene.py  ->  ../mine/this-is-fine/
Seamless: the enter starts on the base pose (Clawd alone, no house) and the house is uncovered while he walks right.
Everything that moves in the room (flames, smoke, sparks, ash, steam) repeats every 8 frames, the loops are 40 and 48 frames
(no extra seam frame at the end), the enter ends on the frame right before loop frame 0 and the exit starts on loop frame 0.
"""
import math

from props import *
from font3 import say
from fun_sets import arm
from seamless import save_flow, base_pose

GROUND = 58
SEAT_DX = 72                       # Clawd's x shift when he sits on the chair
F_RED, F_ORANGE, F_YELLOW = (214, 52, 32), (246, 134, 36), (255, 214, 80)
WALL_TOP, WALL_BOT = (52, 36, 42), (104, 62, 48)
FLOOR, FLOOR_D = (96, 64, 44), (74, 48, 34)
SEAT, WOOD = (150, 104, 66), (118, 80, 50)
# floor flames, wall flames, ceiling flames: (centre x, base y, height, width, sway, phase)
FLOOR_F = [(cx, GROUND, 7 + (cx * 7) % 8, 9, 1.5, cx * 0.4) for cx in range(4, 190, 12)]
WALL_F = [(14, GROUND, 34, 18, 3, 0.3), (32, GROUND, 40, 20, 3, 1.4), (52, GROUND, 30, 16, 3, 2.2), (186, GROUND, 24, 12, 2, 0.9),
          (100, 52, 12, 8, 1.5, 0.2), (150, 52, 14, 8, 2, 3.4), (172, 52, 18, 10, 2, 2.6)]
CEIL_F = [(cx, 1, 8 + (cx * 5) % 6, 11, 2, cx * 0.3) for cx in range(14, 192, 28)]
WALK_PATH = [0, 5, 13, 23, 34, 45, 56, 65, 72]
MUG_PATH = [(156, 32), (152, 24), (146, 16), (136, 16), (124, 20)]


def flame(draw, cx, base, h, w, sway=0.0, down=False, dim=0.0):
    for i in range(h):
        t = i / h
        ww = max(1, round(w * (1 - t) ** 0.8))
        off = round(sway * t)
        y = base + i if down else base - i
        for frac, col, lim in ((1.0, F_RED, 1.0), (.62, F_ORANGE, .85), (.3, F_YELLOW, .55)):
            if t < lim:
                w2 = max(1, round(ww * frac))
                R(draw, cx - w2 // 2 + off, y, w2, 1, mix(col, WALL_TOP, dim) if dim else col)


def flames(draw, specs, t, down=False, dim=0.0, scale=1.0):
    p = 2 * math.pi * t / 8
    for cx, base, h, w, sway, ph in specs:
        hh = round(h * scale * (0.88 + 0.12 * math.sin(p + ph) + 0.06 * math.sin(2 * p + ph * 2)))
        if hh >= 2:
            flame(draw, cx, base, hh, w, sway * math.sin(p + ph), down, dim)


def backdrop(draw, t):
    for y in range(64):
        R(draw, 1, y, 190, 1, mix(WALL_TOP, WALL_BOT, min(1.0, max(0.0, (y - 4) / 50))))
    R(draw, 1, 52, 190, 11, FLOOR)
    for x in range(1, 190, 24):
        R(draw, x, 52, 1, 11, FLOOR_D)
    R(draw, 1, 51, 190, 2, FLOOR_D)
    for x in range(1, 110):                                   # firelight on the left wall
        k = min(1.0, (110 - x) / 110) * .38
        for y in range(2, 51):
            if (x + y) % 2 == 0:
                R(draw, x, y, 1, 1, mix(mix(WALL_TOP, WALL_BOT, min(1.0, max(0.0, (y - 4) / 50))), (210, 96, 40), k))
    R(draw, 22, 6, 30, 28, WOOD)                              # window with curtains, the garden is on fire too
    for i in range(24):
        R(draw, 25, 9 + i, 24, 1, mix((250, 190, 70), (190, 60, 34), i / 24))
    R(draw, 36, 9, 2, 24, WOOD)
    R(draw, 25, 20, 24, 2, WOOD)
    R(draw, 20, 4, 5, 32, (170, 60, 60))
    R(draw, 49, 4, 5, 32, (170, 60, 60))
    R(draw, 66, 12, 17, 14, SEAT)                             # picture frame
    R(draw, 68, 14, 13, 10, (126, 150, 176))
    R(draw, 70, 19, 9, 5, (92, 130, 96))
    p = 2 * math.pi * t / 8                                   # smoke under the ceiling
    for k in range(6):
        x = 4 + k * 32 + round(3 * math.sin(p + k))
        h = 2 + round(4 * (1 + math.sin(p + k * 1.7)) / 2)
        R(draw, x, 1, 28, h, (40, 34, 40))
        R(draw, x + 6, 1 + h, 16, max(1, h // 2), (52, 44, 50))


def mug_at(draw, x, y, t):
    R(draw, x, y, 8, 8, WHITE)
    R(draw, x + 8, y + 2, 2, 4, WHITE)
    R(draw, x + 1, y + 1, 6, 2, (110, 70, 40))
    for k in range(2):
        R(draw, x + 1 + k * 3 + (t // 2 + k) % 2, y - 3 - (t + k * 3) % 4, 1, 1, (210, 214, 224))   # steam: periods 4 and 2 divide 8


def furniture(draw, mug, t):
    R(draw, 84, 22, 5, 30, WOOD)                              # chair back behind Clawd
    R(draw, 135, 22, 5, 30, WOOD)
    R(draw, 84, 22, 56, 4, WOOD)
    R(draw, 152, 40, 38, 3, SEAT)                             # side table
    R(draw, 155, 43, 3, GROUND - 43, WOOD)
    R(draw, 185, 43, 3, GROUND - 43, WOOD)
    mug_at(draw, mug[0], mug[1], t)


def seat_front(draw):
    R(draw, 82, 46, 60, 5, SEAT)
    R(draw, 82, 46, 60, 1, (186, 140, 96))
    R(draw, 84, 51, 4, GROUND - 51, WOOD)
    R(draw, 136, 51, 4, GROUND - 51, WOOD)


def sparks_ash(draw, t):
    for k in range(8):
        sx = 24 + k * 20 + round(3 * math.sin(2 * math.pi * t / 8 + k))
        R(draw, sx, 50 - (t * 6 + k * 7) % 48, 1, 2, F_YELLOW)
    for k in range(9):
        ax = 14 + k * 21 + round(2 * math.sin(2 * math.pi * t / 8 + k * 2))
        R(draw, ax, 4 + (k * 9 + t * 6) % 48, 1, 1, (150, 146, 150))


def paint_room(draw, t, mug, plank, bubble, me_fn, sitting):
    backdrop(draw, t)
    flames(draw, WALL_F[:4], t)
    flames(draw, WALL_F[4:], t, dim=.35)
    flames(draw, CEIL_F, t, down=True)
    flames(draw, FLOOR_F[::2], t + 2, dim=.3)
    furniture(draw, mug, t)
    if plank is not None:
        px, py, sp = plank
        R(draw, px, py, 30, 4, (110, 66, 36))
        R(draw, px, py, 30, 1, F_ORANGE)
        for k in range(sp):
            R(draw, px + 4 + k * 5, py - 3 - (k * 3) % 5, 1, 1, F_YELLOW)
    if sitting and me_fn:
        me_fn(draw)
    seat_front(draw)
    flames(draw, FLOOR_F[1::2], t, scale=.75)
    sparks_ash(draw, t)
    if bubble:
        bx, by, w, h = 8, 4, 7 * 8 + 10, 2 * 12 + 6               # the bubble sits left of Clawd, tail towards him
        R(draw, bx, by, round(w * min(1.0, bubble)), h, WHITE)
        if bubble >= 1:
            for k, wd in enumerate((5, 4, 3, 2, 1)):
                R(draw, bx + w, by + h - 8 + k, wd, 1, WHITE)
            say(draw, bx + 5, by + 4, "THIS IS", (30, 34, 46), 2)
            say(draw, bx + 5, by + 16, "FINE.", (30, 34, 46), 2)


def hat_on(draw, head_top, dx):
    R(draw, OX + 13 + dx, head_top - 6, 22, 6, (30, 30, 36))
    R(draw, OX + 7 + dx, head_top, 34, 2, (30, 30, 36))
    R(draw, OX + 13 + dx, head_top - 2, 22, 1, (150, 40, 44))
    R(draw, OX + 15 + dx, head_top - 5, 6, 1, (78, 78, 90))


def fine_frame(t=0, mug=MUG_PATH[0], arm_level=0, blink=False, lid=0.3, plank=None, bubble=0, look=(0, 0), dx=SEAT_DX, walk=None,
               sitting=True, bob=0, hat=True, grin=True, reveal=None):
    """reveal: only the part of the house left of this x is shown (enter and exit), None shows all of it."""
    img, draw = new_frame()

    def me(d):
        b = -2 if sitting else bob
        clawd(d, look=look, blink=blink, lid=lid, bob=b, dx=dx, walk=walk)
        if arm_level and dx == SEAT_DX:
            arm_shift(d, arm_level, b)
        if grin:
            draw_smile(d, OX + 4 * G + dx, OY + 2 * G + 1 + b)
        if hat:
            hat_on(d, OY + b, dx)

    if reveal is None:
        paint_room(draw, t, mug, plank, bubble, me, sitting)
        if not sitting:
            me(draw)
        return img
    layer, ld = new_frame()
    paint_room(ld, t, mug, plank, bubble, None, False)
    r = max(0, min(192, reveal))
    if r:
        img.alpha_composite(layer.crop((0, 0, r, 64)), (0, 0))
    me(draw)
    return img


def arm_shift(draw, level, bob):
    """The raised right arm of a seated Clawd (he is shifted right by SEAT_DX)."""
    ox, oy = OX + SEAT_DX, OY + bob
    draw.rectangle([ox + 8 * G, oy + 2 * G, ox + 10 * G - 1, oy + 4 * G - 1], fill=TRANS)
    draw.rectangle([ox + 8 * G, oy + G + 3, ox + 9 * G + 2, oy + 3 * G - 1], fill=CORAL)
    draw.rectangle([ox + 9 * G - 1, oy + 4, ox + 10 * G - 2, oy + 2 * G - 1], fill=CORAL)


def rest(t=0):
    return fine_frame(t)


def enter():
    n = 14
    fr = [base_pose()]
    for i in range(1, 9):
        fr.append(fine_frame(i - n, dx=WALK_PATH[i], walk=i % 2, sitting=False, look=(1 if i < 3 else 2, 0), hat=i >= 3, grin=i >= 5, lid=0.3 * i / 8,
                             reveal=24 + i * 22 if i < 8 else 192))
    fr.append(fine_frame(9 - n, dx=SEAT_DX, sitting=False, reveal=192))
    fr.append(fine_frame(10 - n, dx=SEAT_DX, sitting=False, bob=-5, reveal=192))
    fr.append(fine_frame(11 - n, dx=SEAT_DX, sitting=False, bob=-3, reveal=192))
    fr.append(fine_frame(12 - n, dx=SEAT_DX, sitting=False, bob=-2, reveal=192))
    fr.append(fine_frame(13 - n))                                  # = frame t = -1 = 7, loop frame 0 comes next
    return fr


def leave():
    fr = [rest(0), fine_frame(1, sitting=False, bob=-3), fine_frame(2, sitting=False, bob=-5), fine_frame(3, sitting=False, bob=-1)]
    t = 4
    for i, dx in enumerate(reversed(WALK_PATH[1:])):
        j = len(WALK_PATH) - 1 - i
        fr.append(fine_frame(t, dx=dx, walk=j % 2, sitting=False, look=(-2 if i > 2 else 0, 0), hat=j >= 3, grin=j >= 5,
                             lid=0.3 * j / 8, reveal=192 if i < 1 else (24 + j * 22 if j < 8 else 192)))
        t += 1
    fr.append(base_pose())
    return fr


def sip(t):
    if t < 8 or t >= 26:
        return fine_frame(t)
    if t < 13:
        i = t - 8
        return fine_frame(t, mug=MUG_PATH[i], arm_level=1 if i > 0 else 0)
    if t < 21:
        i = t - 13
        return fine_frame(t, mug=MUG_PATH[4], arm_level=1, lid=.7 if 2 <= i < 6 else 0.3, blink=i == 3)
    i = t - 21
    return fine_frame(t, mug=MUG_PATH[3 - i] if i < 4 else MUG_PATH[0], arm_level=1 if i < 3 else 0)


def plank(t):
    pop = 0.0
    if 8 <= t < 14:
        pop = min(1.0, (t - 7) / 3)
    elif 14 <= t < 38:
        pop = 1.0
    elif 38 <= t < 42:
        pop = max(0.0, 1 - (t - 37) / 4)
    pk = None
    if 14 <= t < 22:
        pk = (156, round(-6 + 42 * ease(min(1.0, (t - 13) / 6))), 0 if t < 19 else 4)
    elif 22 <= t < 38:
        pk = (156, 36, max(0, 4 - (t - 22) // 4))
    return fine_frame(t, bubble=pop, plank=pk, blink=t in (28, 34))


if __name__ == "__main__":
    save_flow("this-is-fine", enter(), [[sip(t) for t in range(40)], [plank(t) for t in range(48)]], leave())
