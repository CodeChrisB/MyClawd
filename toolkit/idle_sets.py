"""Two more idle sets with variants: idle-coffee (sip, steam gazing, wake up) and idle-book (reading, a funny page, a nap).

python idle_sets.py  ->  ../mine/{idle-coffee,idle-book}/
No panel: Clawd alone with a prop that rises in during the enter and sinks away in the exit.
"""
import math

from props import *

SEAM = (0, 1)
MUG, COFFEE, HANDLE = (236, 236, 242), (96, 58, 34), (200, 200, 210)
STEAM = (205, 210, 222)
PAGE, PAGE_D, SPINE, COVER = (240, 236, 224), (205, 200, 186), (130, 84, 52), (160, 108, 64)


def slide_idle(frame, n, reverse):
    """Enter/exit: the prop rises from below the canvas (or sinks back). First exit frame = seam."""
    out = []
    for i in range(n):
        t = ease((i + 1) / n) if not reverse else 1 - ease(i / (n - 1))
        out.append(frame(off=round((1 - t) * 34), look=(0, round(t))))
    return out


def finish_idle(name, frame, loops):
    save_set(name, lambda: slide_idle(frame, ENTER, False), loops, lambda: slide_idle(frame, EXIT, True))


def face(draw, bob, smile=False, wide=False):
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)


# ---------------------------------------------------------------- coffee
def mug(draw, x, y):
    R(draw, x, y, 10, 10, MUG)
    R(draw, x + 1, y + 1, 8, 2, COFFEE)
    R(draw, x + 10, y + 2, 3, 6, HANDLE)
    R(draw, x + 11, y + 4, 1, 2, (26, 30, 42))
    R(draw, x, y + 9, 10, 1, (170, 170, 184))


def steam(draw, x, y, f, strong=1):
    for k in range(3):
        t = ((f * 1.0 + k * 3) % 10) / 10
        sx = x + 1 + k * 3 + round(math.sin((f + k * 2) * 0.7) * 1.2)
        sy = y - 3 - round(t * (9 + 4 * strong))
        if t < 0.9:
            R(draw, sx, sy, 2, 2 if t < 0.5 else 1, STEAM)


def coffee_frame(off=0, lift=0.0, f=0, steam_on=True, look=SEAM, blink=False, lid=0.0, bob=0, smile=False, spark=False, strong=1,
                 sway=0):
    img, draw = new_frame()
    clawd(draw, look=look, blink=blink, lid=lid, bob=bob, dx=sway)
    face(draw, bob, smile)
    mx, my = 68 - round(14 * lift) + sway, 24 - round(10 * lift) + bob + off
    mug(draw, mx, my)
    if steam_on and off == 0:
        steam(draw, mx, my, f, strong)
    if spark:
        for k, (sx, sy) in enumerate(((10, 6), (60, 3), (70, 12))):
            if (f + k * 2) % 6 < 3:
                R(draw, sx, sy, 1, 3, YELLOW)
                R(draw, sx - 1, sy + 1, 3, 1, YELLOW)
    return img


def coffee_sip():
    f = coffee_frame
    frames = [f(f=k) for k in range(6)] + [f(f=6, blink=True)] + [f(f=7)]
    for k in range(5):                                                       # lifts the mug to his face
        frames.append(f(lift=ease((k + 1) / 5), f=8 + k, look=(0, 1), bob=0))
    for k in range(4):                                                       # sips, eyes closed
        frames.append(f(lift=1.0, f=13 + k, blink=True, bob=1 if k == 1 else 0))
    for k in range(5):
        frames.append(f(lift=1.0 - ease((k + 1) / 5), f=17 + k, smile=k > 1, look=(0, 1)))
    frames += [f(f=22 + k, smile=True, look=(0, 0 if k < 4 else 1), blink=k == 5) for k in range(8)]
    return frames + [f(f=30, smile=True, blink=True), f()]


def coffee_gaze():
    f = coffee_frame
    frames = [f(f=k) for k in range(5)]
    for k in range(18):                                                      # watches the steam curl up, content
        frames.append(f(f=5 + k, strong=2, look=(0, -1 if k % 8 < 5 else 0), sway=(0, 1, 1, 0, -1, -1, 0, 0)[k % 8] if k > 3 else 0,
                        smile=k > 4, blink=k == 12))
    frames += [f(f=23 + k, look=(0, 1), smile=k < 2) for k in range(4)]
    return frames + [f(f=27, blink=True), f()]


def coffee_wake():
    f = coffee_frame
    frames = [f(), f(f=1)] + [f(f=k + 2, lid=min(0.7, 0.2 * (k + 1)), look=(0, 2), bob=1 if k % 4 == 3 else 0) for k in range(6)]
    for k in range(4):                                                       # sleepy, then the mug comes up
        frames.append(f(lift=ease((k + 1) / 4), f=6 + k, lid=0.7, look=(0, 2)))
    for k in range(3):
        frames.append(f(lift=1.0, f=10 + k, blink=True, lid=0.0))
    for k in range(5):                                                       # eyes wide, a jolt: the mug stays in his hand
        frames.append(f(lift=1.0, f=13 + k, look=(0, 0), bob=-3 if k < 2 else -1, spark=True, strong=2, smile=k > 2))
    for k in range(6):                                                       # then he lowers it slowly, happy
        frames.append(f(lift=1.0 - ease((k + 1) / 6), f=18 + k, look=(0, 1 if k > 2 else 0), spark=k < 3, smile=True))
    frames += [f(f=24 + k, smile=True, look=(0, 1), blink=k == 5) for k in range(6)]
    return frames + [f(f=26, blink=True), f()]


# ---------------------------------------------------------------- book
def book(draw, x, y, flip=None, scan=0):
    """Open book, 40 x 14, cover edge in brown, a red bookmark at the spine. scan lights one text line."""
    R(draw, x - 1, y - 1, 42, 16, COVER)
    R(draw, x, y, 19, 13, PAGE)
    R(draw, x + 21, y, 19, 13, PAGE)
    R(draw, x + 19, y, 2, 13, SPINE)
    R(draw, x + 20, y + 13, 2, 4, RED)
    for side in (0, 21):
        for i in range(4):
            R(draw, x + 3 + side, y + 2 + i * 3, 13 - (i == 3) * 5, 1, PAGE_D)
    if scan:
        line = (scan - 1) % 4
        side = 21 if scan > 4 else 0
        R(draw, x + 3 + side, y + 2 + line * 3, 13, 1, AMBER)
    if flip is not None:                                                     # the right page turns over to the left
        w = abs(round(19 * math.cos(flip * math.pi)))
        R(draw, x + 20 - (w if flip > 0.5 else 0), y, max(1, w), 13, (252, 248, 238))


def book_frame(off=0, flip=None, scan=0, look=SEAM, blink=False, lid=0.0, bob=0, smile=False, zf=None, tilt=0, f=0):
    img, draw = new_frame()
    clawd(draw, look=look, blink=blink, lid=lid, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    bx, by = 20, 24 + bob + off + tilt
    book(draw, bx, by, flip, scan)
    if off == 0:                                                             # both hands hold the book
        R(draw, bx - 5, by + 6, 6, 7, CORAL)
        R(draw, bx + 39, by + 6, 6, 7, CORAL)
        R(draw, bx - 3, by + 11, 4, 2, CORAL)
        R(draw, bx + 39, by + 11, 4, 2, CORAL)
    if zf is not None:
        zzz(draw, zf, 66, 22, 3)
    return img


def book_read():
    f = book_frame
    frames = [f()] * 3 + [f(blink=True)] + [f()] * 2
    for page in range(2):                                                    # reads two pages, line by line
        for line in range(1, 7):
            frames += [f(scan=line, look=(0 if line % 3 else 2, 2 - (line % 3 == 0)))] * 2
        for k in range(5):                                                   # turns the page
            frames.append(f(flip=(k + 1) / 6, look=(2, 2)))
        frames += [f(look=(0, 2)), f(blink=True, look=(0, 2))]
    return frames + [f(look=(0, 1)), f(blink=True), f()]


def book_funny():
    f = book_frame
    frames = [f()] * 3
    for line in range(1, 5):
        frames += [f(scan=line, look=(2 if line % 2 else 0, 2))] * 2
    frames += [f(scan=4, look=(2, 2))]
    for k in range(10):                                                      # something funny: shakes with silent laughter
        frames.append(f(scan=4, look=(1, 2), bob=(0, -1)[k % 2], tilt=(0, 1)[k % 2], smile=True, blink=k in (3, 4, 8)))
    frames += [f(look=(0, 1), smile=True, blink=k == 3) for k in range(4)]
    return frames + [f(blink=True), f()]


def book_nap():
    f = book_frame
    frames = [f()] * 2
    for line in range(1, 4):
        frames += [f(scan=line, look=(0 if line % 2 else 2, 2), lid=0.3 * line)] * 2
    for k in range(4):                                                       # eyes close, head sinks
        frames.append(f(lid=0.85, look=(0, 2), bob=k // 2, tilt=0))
    for k in range(14):
        frames.append(f(lid=0.85, look=(0, 2), bob=1 if k % 8 < 4 else 0, zf=k))
    for k in range(3):                                                       # a jolt awake
        frames.append(f(lid=0.0, look=(0, 0), bob=-2 if k == 0 else 0))
    frames += [f(scan=1, look=(2, 2)), f(look=(0, 1))]
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish_idle("idle-coffee", coffee_frame, [coffee_sip, coffee_gaze, coffee_wake])
    finish_idle("idle-book", book_frame, [book_read, book_funny, book_nap])
