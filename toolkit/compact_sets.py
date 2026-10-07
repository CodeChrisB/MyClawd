"""Two sets: compacting (4 loops: press, fold, double press, summary) and handoff (Clawd writes, a second agent takes over).

python compact_sets.py  ->  ../mine/{compacting,handoff}/
"""
import math

from props import *
from PIL import ImageDraw
from limit_sets import LINES, GREY_BAR, draw_gauge, GLASS, COIN_RIM

def lerp(a, b, t):
    return a + (b - a) * t


LW = [34, 28, 40, 24, 36, 30, 42, 26, 38, 32]


def finish(name, frame, loops):
    enter, leave = seam_slides(frame)
    save_set(name, enter, loops, leave)


# ---------------------------------------------------------------- compacting: a press, a fold, two presses, a written summary
def cp_frame(lines=(), level=0.0, plate=8, summary=None, doc=None, wall=None, tickmark=False, sweat_f=None, key=False,
             look=(2, 1), blink=False, bob=0, slide=0):
    """Gauge left; compactor right (floor, a plate that can come down, a pile of lines, a summary block or doc)."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    color = GREEN if level < 0.5 else AMBER if level < 0.8 else RED
    draw_gauge(draw, x0, round(44 * level), color)
    R(draw, x0 + 36, 52, 48, 2, (70, 74, 86))
    R(draw, x0 + 36, 8, 2, 44, GRID_RAIL)
    R(draw, x0 + 82, 8, 2, 44, GRID_RAIL)
    limit = 59 if doc else (wall - 1 if wall else 999)                       # the page / the wall cuts lines off
    for x, y, w, c in lines:
        R(draw, x0 + x, y, min(w, limit - x), 3, c)
    if summary:
        sx, sy, sw, sh = summary
        R(draw, x0 + sx, sy, sw, sh, AMBER)
        R(draw, x0 + sx, sy + sh - 1, sw, 1, COIN_RIM)
    if doc:                                                                  # page with n written lines
        n, w = doc
        R(draw, x0 + 60, 28, 22, 24, (230, 232, 238))
        for i in range(n):
            R(draw, x0 + 63, 32 + i * 5, min(16, w if i == n - 1 else 16), 2, AMBER)
    R(draw, x0 + 52, 6, 16, 4, (90, 94, 108))                                # piston housing with a lamp
    R(draw, x0 + 54, 7, 2, 2, AMBER if (plate is not None and plate > 9) or wall else GREY)
    if plate is not None:
        R(draw, x0 + 58, 10, 4, max(0, plate - 10), (120, 124, 140))        # the rod that holds the plate
        R(draw, x0 + 38, plate, 44, 3, GLASS)
    if wall:                                                                 # side ram: housing on the right, rod, wall
        R(draw, x0 + 84, 28, 4, 8, (90, 94, 108))
        R(draw, x0 + wall + 3, 31, 84 - wall - 3, 2, (120, 124, 140))
        R(draw, x0 + wall, 12, 3, 40, GLASS)
    if tickmark:
        tick(draw, x0 + 62, 16, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


GRID_RAIL = (48, 52, 64)


def pile(n, c=1.0):
    return [(38, round(49 - 4 * i * c), LW[i % 10], LINES[i % 5]) for i in range(n)]


def intro():
    return [cp_frame()] * 4 + [cp_frame(blink=True)] + [cp_frame()] * 2


def grow(n, per=2):
    frames = []
    for k in range(1, n + 1):
        frames += [cp_frame(pile(k), k / 10, sweat_f=k if k > 6 else None, look=(2, 2 - k // 4))] * per
    return frames


def finale(summary, level, n=0):
    """Summary block shows with a check, then shrinks away. Ends on the seam."""
    frames = [cp_frame(summary=summary, level=level, tickmark=True, look=(2, 0))] * 6
    sx, sy, sw, sh = summary
    for k in (3, 2, 1):
        frames.append(cp_frame(summary=(sx, sy, sw * k // 4, sh), level=level * k / 5, tickmark=k > 1))
    frames.append(cp_frame(blink=True))
    return frames + [cp_frame()]


def press():
    frames = intro() + grow(10)
    top = lambda c: round(49 - 36 * c) - 4
    frames += [cp_frame(pile(10), 1.0, plate=8, key=True, bob=k % 2, look=(2, 2), sweat_f=k) for k in range(3)]
    for k in range(7):
        c = 1.0 - 0.88 * ease((k + 1) / 7)
        frames.append(cp_frame(pile(10, c), c, plate=top(c), key=k % 2 == 0, bob=k % 2 if k < 6 else 0, look=(2, 2)))
    summary = (50, 46, 14, 5)
    for k in range(5):
        frames.append(cp_frame(summary=summary, level=0.15, plate=top(0.12) - round(k * (top(0.12) - 8) / 4)))
    return frames + finale(summary, 0.15)


def fold():
    """A wall rams in from the right and squeezes the pile narrower, then the pile turns into one block."""
    frames = intro() + grow(10)
    frames += [cp_frame(pile(10), 1.0, key=True, bob=k % 2, look=(2, 2), sweat_f=k) for k in range(3)]
    for k in range(8):
        t = ease((k + 1) / 8)
        wall = round(lerp(84, 48, t))
        frames.append(cp_frame(pile(10), 1.0 - 0.7 * t, wall=wall, key=k % 2 == 0, bob=k % 2 if k < 7 else 0, look=(2, 2)))
    summary = (50, 46, 14, 5)
    for k in range(5):
        frames.append(cp_frame(summary=summary, level=0.15, wall=round(lerp(48, 84, ease((k + 1) / 5)))))
    return frames + finale(summary, 0.15)


def double_press():
    frames = intro() + grow(10)
    top = lambda c: round(49 - 36 * c) - 4
    for k in range(5):                                                       # first press, only partly
        c = 1.0 - 0.45 * ease((k + 1) / 5)
        frames.append(cp_frame(pile(10, c), c, plate=top(c), key=k % 2 == 0, bob=k % 2, look=(2, 2)))
    frames += [cp_frame(pile(10, 0.55), 0.55, plate=top(0.55), look=(2, 0), blink=k == 2) for k in range(3)]
    for k in range(3):                                                       # plate lifts, pile springs back a bit
        c = 0.55 + 0.15 * ease((k + 1) / 3)
        frames.append(cp_frame(pile(10, c), c, plate=top(c) - 3 * (k + 1), look=(2, 1), sweat_f=k))
    for k in range(6):                                                       # second press, all the way
        c = 0.7 - 0.58 * ease((k + 1) / 6)
        frames.append(cp_frame(pile(10, c), c, plate=top(c), key=k % 2 == 0, bob=k % 2, look=(2, 2)))
    summary = (50, 46, 14, 5)
    for k in range(4):
        frames.append(cp_frame(summary=summary, level=0.15, plate=top(0.12) - round(k * (top(0.12) - 8) / 3)))
    return frames + finale(summary, 0.15)


def summarize():
    """Clawd types a summary page; the lines slide into it one pair at a time."""
    frames = intro()
    base = [(38, 49 - 4 * i, 12 + (i * 5) % 9, LINES[i % 5]) for i in range(10)]
    for k in range(1, 11):
        frames += [cp_frame(base[:k], k / 10, sweat_f=k if k > 6 else None, look=(2, 2 - k // 4))] * 2
    gone = set()
    for rnd in range(5):
        pair = (9 - 2 * rnd, 8 - 2 * rnd)
        for k in range(5):
            lines = []
            for i, (x, y, w, c) in enumerate(base):
                if i in gone:
                    continue
                lines.append((x + (round(24 * ease((k + 1) / 5)) if i in pair else 0), y, w, c))
            n_left = 10 - len(gone) - (2 if k == 4 else 0)
            frames.append(cp_frame(lines, n_left / 10, doc=(min(rnd + 1, 4), 4 + k * 3), key=k % 2 == 0, bob=k % 2,
                                   look=(2, 1 + (k > 2))))
        gone |= set(pair)
    frames += [cp_frame(level=0.0, doc=(4, 16), tickmark=True, look=(2, 0))] * 6
    frames += [cp_frame(doc=(2, 16)), cp_frame(blink=True)]
    return frames + [cp_frame()]


# ---------------------------------------------------------------- handoff: Clawd writes, another agent takes over
def handoff_frame(lect=0, text=0, cdx=0, cwalk=None, adx=None, awalk=None, poof=0, pen=0, look=(2, 1),
                  alook=(0, 1), blink=False, bob=0, abob=0, hl=0, check=False):
    img, draw = new_frame()
    lx = 80 + lect
    R(draw, lx, 38, 24, 18, (120, 70, 40))                                   # lectern
    R(draw, lx - 2, 36, 28, 3, (150, 90, 50))
    R(draw, lx + 3, 22, 18, 14, WHITE)                                       # sheet
    for i in range(3):                                                       # handwriting: text counts 0..24 characters
        w = max(0, min(12, text - i * 8))
        R(draw, lx + 5, 25 + i * 4, w, 1, AMBER if i < hl else (70, 74, 90))  # the line being read lights up
        if i < hl:
            R(draw, lx + 5, 26 + i * 4, w, 1, AMBER)
    if check:
        tick(draw, lx + 8, 10, GREEN, 2)
    if pen:
        R(draw, lx - 6, 28 - pen % 2, 7, 2, (60, 40, 20))
    clawd(draw, look=look, blink=blink, bob=bob, dx=cdx, walk=cwalk)
    if adx is not None:
        clawd(draw, look=alook, dx=adx, walk=awalk, bob=abob)
    if poof:
        for k in range(8):
            ang = k * math.pi / 4
            r = 4 + poof * 5
            R(draw, round(OX + 36 + math.cos(ang) * r * 1.6), round(OY + 24 + math.sin(ang) * r), 3, 3, (210, 214, 226))
    return img



def enter_handoff():
    return [handoff_frame(lect=round((1 - ease((i + 1) / ENTER)) * 120), look=(round(2 * ease((i + 1) / ENTER)), round(ease((i + 1) / ENTER))))
            for i in range(ENTER)]


def leave_handoff():
    out = []
    for i in range(EXIT):
        t = 1 - ease(i / (EXIT - 1))                                          # first frame = seam, last = lectern gone
        out.append(handoff_frame(lect=round((1 - t) * 120), look=(round(2 * t), round(t))))
    return out


def handoff_loop():
    f = handoff_frame
    frames = [f()] * 3 + [f(blink=True)] + [f()] * 2
    for k in range(18):                                                      # Clawd writes
        frames.append(f(text=k * 24 // 17, pen=1 + k % 2, bob=k % 2 if k % 3 == 0 else 0, look=(2, 2 if k % 6 < 3 else 1)))
    frames += [f(text=24)] * 2
    start, stop = 176, 118
    for k in range(10):                                                      # the other agent walks in
        x = round(start + (stop - start) * (k + 1) / 10)
        frames.append(f(text=24, adx=x, awalk=k % 2, look=(2, 1 if k < 6 else 0)))
    for k in range(12):                                                      # the agent reads the page, line by line
        line = k // 4
        frames.append(f(text=24, adx=stop, hl=line + 1, alook=(0, line), abob=1 if k % 4 == 3 else 0, look=(2, 1)))
    frames += [f(text=24, adx=stop, hl=3, check=True, abob=k % 2, alook=(0, 2), look=(2, 0)) for k in range(4)]
    for k in range(12):                                                      # Clawd walks away to the left
        x = -round(88 * ease((k + 1) / 12))
        frames.append(f(text=24, cdx=x, cwalk=k % 2, adx=stop, look=(0, 1), alook=(0, 1), check=k < 3))
    frames += [f(text=24, cdx=-88, adx=stop)] * 2
    for k in range(14):                                                      # the agent takes Clawd's place
        x = round(stop - stop * ease((k + 1) / 14))
        frames.append(f(text=24, cdx=-88, adx=x, awalk=k % 2, alook=(0, 1) if k < 12 else (2, 1)))
    for k in range(9):                                                       # at Clawd's place, reads it once more, then continues
        line = k // 3
        frames.append(f(text=24, adx=0, hl=line + 1, alook=(2, line), abob=1 if k % 3 == 2 else 0))
    frames += [f(text=24, adx=0, hl=3, check=True, abob=k % 2, alook=(2, 1)) for k in range(3)]
    for k in range(1, 4):                                                    # a puff, and a fresh sheet
        frames.append(f(text=24 if k < 2 else 0, adx=0, poof=k, alook=(2, 1)))
    return frames + [f()]


if __name__ == "__main__":
    finish("compacting", cp_frame, [press, fold, double_press, summarize])
    save_set("handoff", enter_handoff, [handoff_loop], leave_handoff)
