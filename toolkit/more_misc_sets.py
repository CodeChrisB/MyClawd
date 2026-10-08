"""Three more scenes: overworked (Misc), friday-deploy (Dev work), this-is-fine (Memes).

python more_misc_sets.py  ->  ../mine/{overworked,friday-deploy,this-is-fine}/
Seam pose: an empty panel / a Friday the 13th calendar next to a red button / Clawd on a chair, the room on fire (flames at phase 0).
"""
import math

from props import *
from dev_sets import base, hold, smile
from font3 import say
from fun_sets import arm

BROWN, BROWN_D = (140, 98, 62), (104, 70, 44)
NOTE_C = [YELLOW, PINK, LIGHT_BLUE, GREEN, ORANGE, PURPLE]


# ---------------------------------------------------------------- overworked: tickets pile up, the coffee runs out


def mug(draw, x, y, fill=0.0):
    R(draw, x, y, 7, 8, WHITE)
    R(draw, x + 7, y + 2, 2, 4, WHITE)
    R(draw, x + 1, y + 1, 5, 1, (110, 70, 40) if fill else (200, 204, 216))
    if fill:
        R(draw, x + 1, y + 1, 5, round(5 * fill), (110, 70, 40))


def ow_frame(notes=0, drop=None, mugs=0, clock=None, lid=0.0, shake=0, steam=0, sweating=False, look=(2, 1), blink=False, bob=0, f=0, slide=0):
    img, draw, x0 = base(slide)
    for i in range(notes):  # tickets piled in rows of five
        col, row = i % 5, i // 5
        R(draw, x0 + 4 + col * 17, 46 - row * 10, 14, 9, NOTE_C[i % 6])
        R(draw, x0 + 6 + col * 17, 48 - row * 10, 9, 1, DARK)
        R(draw, x0 + 6 + col * 17, 51 - row * 10, 6, 1, DARK)
    if drop is not None:
        i, y = drop
        col, row = i % 5, i // 5
        R(draw, x0 + 4 + col * 17, y, 14, 9, NOTE_C[i % 6])
        R(draw, x0 + 6 + col * 17, y + 2, 9, 1, DARK)
    for k in range(mugs):
        mug(draw, x0 + 4 + k * 13, 46, 0.0 if k < mugs - 1 else 1.0)
    if clock is not None:
        cx, cy = x0 + 74, 16
        dot(draw, cx, cy, 8, (200, 204, 216))
        dot(draw, cx, cy, 6, (30, 34, 56))
        for s in range(1, 6):
            a = math.radians(clock * 6)
            R(draw, cx + round(math.sin(a) * s), cy - round(math.cos(a) * s), 1, 1, WHITE)
        for s in range(1, 4):
            a = math.radians(clock * 0.5)
            R(draw, cx + round(math.sin(a) * s), cy - round(math.cos(a) * s), 1, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob, dx=shake, lid=lid)
    if sweating:
        sweat(draw, bob, f)
    for k in range(steam):  # steam from the head
        R(draw, OX + 14 + k * 11 + shake, 5 - (f + k * 2) % 6 // 2, 3, 3, (190, 196, 210))
    return img


def ow_pile():
    f = ow_frame
    fr = hold(f, 3)
    for i in range(12):
        row, ty = i // 5, 46 - (i // 5) * 10
        for k in range(3):
            fr.append(f(notes=i, drop=(i, -10 + round((ty + 10) * ease((k + 1) / 3))), lid=min(.7, i * .06), look=(2, 0 if k < 2 else 1),
                        sweating=i > 5, f=i * 3 + k, steam=1 if i > 7 else 0))
        fr.append(f(notes=i + 1, lid=min(.8, (i + 1) * .06), look=(2, 2), sweating=i > 5, f=i * 3 + 3, steam=2 if i > 8 else 1 if i > 6 else 0,
                    bob=1 if i % 2 else 0))
    fr += hold(f, 4, notes=12, lid=.85, look=(2, 2), sweating=True, steam=2, bob=1)
    for i in range(3):
        fr.append(f(notes=12 - 4 * (i + 1) if i < 2 else 0, lid=.5, look=(2, 1)))
    return fr + [f(blink=True)] + hold(f, 1)


def ow_coffee():
    f = ow_frame
    fr = hold(f, 3)
    for n in range(1, 7):
        for k in range(3):
            fr.append(f(mugs=n, clock=(n * 40 + k * 14) % 360, lid=max(0, .5 - n * .1), shake=1 if (n * 3 + k) % 2 else 0, look=(2, 0)))
    for i in range(14):  # wired: everything vibrates
        fr.append(f(mugs=6, clock=(i * 70) % 360, shake=1 if i % 2 else -1, look=(2 if i % 4 < 2 else 1, 0 if i % 3 else 1), bob=-1 if i % 2 else 0,
                    steam=1 if i % 3 == 0 else 0, f=i, sweating=i > 6))
    for i in range(3):
        fr.append(f(mugs=6 - 3 * (i + 1) if i < 1 else 0, clock=(i * 120) % 360 if i < 2 else None, lid=.4, look=(2, 1)))
    return fr + [f(blink=True)] + hold(f, 1)


# ---------------------------------------------------------------- friday-deploy: the button on Friday the 13th


def calendar(draw, x0, band=RED, label="FRI", date="13", flip=0.0):
    R(draw, x0 + 4, 14, 32, 34, WHITE)
    R(draw, x0 + 4, 14, 32, 9, band)
    say(draw, x0 + 12, 16, label, WHITE)
    for k, ch in enumerate(date):
        say(draw, x0 + 9 + k * 12, 28, ch, DARK, 3)
    R(draw, x0 + 10, 11, 2, 5, (150, 154, 168))
    R(draw, x0 + 28, 11, 2, 5, (150, 154, 168))


def big_button(draw, x0, pressed=False, glow=False):
    R(draw, x0 + 48, 46, 34, 7, (70, 74, 90))
    y = 40 if pressed else 36
    R(draw, x0 + 51, y, 28, 46 - y + 2, (150, 40, 44))
    dot(draw, x0 + 65, y - 1, 11, RED if not glow else (255, 110, 100))
    say(draw, x0 + 56, y - 4, "GO", WHITE)


def fd_frame(cur=None, pressed=False, glow=False, band=RED, label="FRI", date="13", rocket=None, alarm=False, look=(2, 1), blink=False, bob=0, f=0, sweating=False,
             bang=False, grin=False, slide=0):
    img, draw, x0 = base(slide)
    if alarm and f % 2 == 0:
        draw.rectangle([x0 - 2, PY0 - 2, x0 + 88 + 2, PY1 + 2], outline=RED, width=2)
    calendar(draw, x0, band, label, date)
    big_button(draw, x0, pressed, glow)
    if rocket is not None:
        def paint(d):
            R(d, x0 + 62, rocket, 6, 12, WHITE)
            R(d, x0 + 62, rocket + 12, 6, 2, RED)
            R(d, x0 + 59, rocket + 8, 3, 6, RED)
            R(d, x0 + 68, rocket + 8, 3, 6, RED)
            R(d, x0 + 63, rocket + 3, 4, 3, LIGHT_BLUE)
            R(d, x0 + 63, rocket + 14, 4, 5 + f % 2 * 2, ORANGE)
        clipped(img, x0, paint)
    if cur is not None:
        cursor(ImageDraw.Draw(img), x0 + cur[0], cur[1])
    d2 = ImageDraw.Draw(img)
    clawd(d2, look=look, blink=blink, bob=bob)
    if sweating:
        sweat(d2, bob, f)
    if bang:
        for k, y in enumerate((4, 10)):
            R(d2, OX + 9 * G + 2 + k * 5, 2, 2, 7, YELLOW)
            R(d2, OX + 9 * G + 2 + k * 5, 11, 2, 2, YELLOW)
    if grin:
        smile(d2, bob)
    return img


def fd_yolo():
    f = fd_frame
    fr = hold(f, 3)
    path = [(8, 54), (30, 52), (56, 46), (64, 40)]
    for i in range(8):
        t = ease((i + 1) / 8) * 3
        a = int(min(2, t))
        p0, p1 = path[a], path[a + 1]
        u = t - a
        fr.append(f(cur=(round(p0[0] + (p1[0] - p0[0]) * u), round(p0[1] + (p1[1] - p0[1]) * u)), look=(2, 2 if i > 3 else 1), f=i))
    fr += [f(cur=(64, 40), look=(2, 2), sweating=True, f=i) for i in range(5)]
    fr += [f(cur=(64, 40), look=(2, 0), sweating=True, f=i, bob=-1) for i in range(2)]
    fr += [f(cur=(64, 42), pressed=True, glow=True, look=(2, 2), bang=False, f=0), f(cur=(64, 42), pressed=True, glow=True, look=(2, 2), f=1)]
    for i in range(10):
        fr.append(f(cur=(64, 42), glow=True, rocket=40 - i * 7, alarm=True, look=(2, -1), f=i, bang=i > 4, bob=-1 if i in (3, 4) else 0))
    for i in range(6):
        fr.append(f(alarm=i < 4, look=(2, 1), f=i, sweating=True, bang=i < 2))
    return fr + [f(blink=True)] + hold(f, 1)


def fd_monday():
    f = fd_frame
    fr = hold(f, 3)
    for i in range(6):
        fr.append(f(cur=(8 + i * 8, 54 - i), look=(2, 1), f=i))
    for i in range(6):
        fr.append(f(cur=(56, 46), look=(2, 2), sweating=True, f=i))
    for i in range(6):  # looks at the calendar and shakes the head
        fr.append(f(cur=(56, 46), look=(2 if i % 4 < 2 else 0, 1), f=i))
    for i in range(6):  # the cursor drifts off to the calendar
        fr.append(f(cur=(56 - i * 8, 46 - i * 2), look=(2 - (i > 2), 1), f=i))
    for i in range(4):  # the calendar flips to Monday
        fr.append(f(cur=(12, 34), band=BLUE_C if i > 1 else RED, label="MON" if i > 1 else "FRI", date="16" if i > 1 else "13", look=(2, 0), f=i))
    fr += [f(band=BLUE_C, label="MON", date="16", grin=True, look=(2, 1), bob=-1 if i == 0 else 0, f=i) for i in range(6)]
    for i in range(2):
        fr.append(f(look=(2, 1)))
    return fr + [f(blink=True)] + hold(f, 1)


BLUE_C = (60, 120, 210)


# ---------------------------------------------------------------- this-is-fine


GROUND = 56
FIRE_R, FIRE_O, FIRE_Y = (200, 50, 30), (240, 130, 40), (255, 210, 70)
SEAT = (130, 90, 60)


def fire(draw, t, grow=1.0, front=False):
    p = 2 * math.pi * t / 8
    for x in range(0, W, 3):
        if front:
            h = 3 + 2 * math.sin(x * 1.3 + p) + math.sin(x * 2.1 - 2 * p)
        else:
            h = 9 + 4 * math.sin(x * 0.35) + 4 * math.sin(x * 0.9 + p) + 2.5 * math.sin(x * 1.7 - 2 * p)
            if x >= 150:
                h += 16 + 7 * math.sin(x * 0.5 + p)
            if x < 6:
                h += 12 + 4 * math.sin(x + p)
        h = max(2, round(h * grow))
        R(draw, x, GROUND - h, 3, h, FIRE_R)
        R(draw, x, GROUND - round(h * .7), 3, round(h * .7), FIRE_O)
        R(draw, x, GROUND - round(h * .4), 3, round(h * .4), FIRE_Y)


def smoke_and_ceiling(draw, t, grow):
    p = 2 * math.pi * t / 8
    for k in range(5):
        x = 6 + k * 38 + round(3 * math.sin(p + k))
        R(draw, x, 0, 18, 4 + round(2 * grow * (1 + math.sin(p + k * 2))), (58, 60, 70))
    for x in range(0, W, 6):
        c = round(grow * (3 + 3 * abs(math.sin(x * 0.8 + p))))
        R(draw, x, 4, 6, c, (220, 90, 30))
    for k in range(7):  # sparks
        sx = 30 + k * 22 + round(3 * math.sin(p + k))
        sy = GROUND - 6 - (t * 6 + k * 9) % 48
        if grow > .4:
            R(draw, sx, sy, 1, 2, YELLOW)


def room(draw, mug_at=(82, 32), steam_f=0, plank=None, bubble=None):
    R(draw, OX - 10, 24, 5, 28, BROWN_D)           # chair back and seat
    R(draw, OX + 53, 24, 5, 28, BROWN_D)
    R(draw, OX - 10, 24, 68, 4, BROWN_D)
    R(draw, 76, 40, 44, 3, BROWN)                    # side table
    R(draw, 80, 43, 3, GROUND - 43, BROWN_D)
    R(draw, 112, 43, 3, GROUND - 43, BROWN_D)
    mug(draw, *mug_at)
    for k in range(2):
        R(draw, mug_at[0] + 1 + k * 3 + (steam_f // 2 + k) % 2, mug_at[1] - 3 - (steam_f + k * 3) % 5, 1, 1, (190, 196, 210))


def seat_front(draw):
    R(draw, OX - 8, 46, 62, 6, SEAT)
    R(draw, OX - 8, 52, 3, GROUND - 52, BROWN_D)
    R(draw, OX + 49, 52, 3, GROUND - 52, BROWN_D)


def fine_frame(t=0, grow=1.0, mug_at=(82, 32), arm_level=0, blink=False, lid=0.0, plank=None, bubble=0, look=(2, 0), sip=False, slide=0):
    img, draw = new_frame()
    smoke_and_ceiling(draw, t, grow)
    fire(draw, t, grow)
    room(draw, mug_at, t)
    if plank is not None:
        px, py, sparks = plank
        R(draw, px, py, 30, 4, (110, 66, 36))
        R(draw, px, py, 30, 1, (230, 120, 40))
        for k in range(sparks):
            R(draw, px + 4 + k * 5, py - 3 - (k * 3) % 5, 1, 1, YELLOW)
    clawd(draw, look=look, blink=blink, lid=lid)
    arm(draw, arm_level)
    draw_smile(draw, OX + 4 * G, OY + 2 * G + 1)
    seat_front(draw)
    fire(draw, t + 3, grow, front=True)
    if bubble:
        w, h, bx = 4 * 13 + 9, 12, 116
        R(draw, bx, 6, round(w * min(1.0, bubble)), h, WHITE)
        R(draw, bx - 3, 12, 3, 3, WHITE)
        if bubble >= 1:
            say(draw, bx + 5, 9, "THIS IS FINE.", (30, 34, 46))
    return img


def fine_rest(t=0):
    return fine_frame(t)


def fine_enter():
    return [fine_frame(i, grow=g) for i, g in enumerate((0.0, .25, .5, .75, .9))] + [fine_frame(0)]


def fine_leave():
    return [fine_frame(0)] + [fine_frame(i + 1, grow=g) for i, g in enumerate((.9, .7, .45, .2, 0.0))]


def fine_sip():
    fr = [fine_rest(t) for t in range(8)]
    n = len(fr)
    path = [(82, 32), (80, 24), (74, 16), (64, 16), (52, 20)]
    for i in range(5):  # the mug floats up to the hand
        fr.append(fine_frame(n + i, mug_at=path[i], arm_level=1 if i > 0 else 0))
    for i in range(8):  # sip, calm as ever
        fr.append(fine_frame(n + 5 + i, mug_at=path[4], arm_level=1, lid=.6 if 2 <= i < 6 else 0.0, blink=i == 3))
    for i in range(5):
        fr.append(fine_frame(n + 13 + i, mug_at=path[3 - i] if i < 4 else (82, 32), arm_level=1 if i < 3 else 0))
    while len(fr) % 8:
        fr.append(fine_rest(len(fr)))
    return fr + [fine_rest(0)]


def fine_plank():
    fr = [fine_rest(t) for t in range(8)]
    n = len(fr)
    for i in range(6):
        fr.append(fine_frame(n + i, bubble=min(1.0, (i + 1) / 3), look=(2, 0)))
    for i in range(8):  # a burning plank drops in front of the table, Clawd stays calm
        py = round(-6 + 52 * ease(min(1.0, (i + 1) / 6)))
        fr.append(fine_frame(n + 6 + i, bubble=1.0, plank=(78, py, 0 if i < 5 else 4), blink=i == 6))
    for i in range(10):
        fr.append(fine_frame(n + 14 + i, bubble=1.0, plank=(78, 46, 4 - i // 3), blink=i == 5))
    for i in range(2):
        fr.append(fine_frame(n + 24 + i, bubble=1.0))
    while len(fr) % 8:
        fr.append(fine_rest(len(fr)))
    return fr + [fine_rest(0)]


if __name__ == "__main__":
    finish("overworked", ow_frame, [ow_pile, ow_coffee])
    finish("friday-deploy", fd_frame, [fd_yolo, fd_monday])
    save_set("this-is-fine", fine_enter, [fine_sip, fine_plank], fine_leave)
