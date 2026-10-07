"""Session command sets: login (a key opens the lock), resume (a bookmarked book opens), clear (the panel is wiped).

python cmd_sets.py  ->  ../mine/{login,resume,clear}/
"""
import math

from props import *
from tool_sets import lock


# ---------------------------------------------------------------- login: key, lock, an avatar appears
def key(draw, x, y, turn=0):
    dot(draw, x + 3, y + 3, 3, YELLOW)
    R(draw, x + 2, y + 2, 2, 2, DARK)
    R(draw, x + 6, y + 2, 14, 2, YELLOW)
    R(draw, x + 15, y + 4, 2, 3, YELLOW)
    R(draw, x + 19, y + 4, 2, 4, YELLOW)


def avatar(draw, cx, cy):
    dot(draw, cx, cy - 4, 4, (150, 170, 220))
    R(draw, cx - 8, cy + 2, 17, 8, (150, 170, 220))
    R(draw, cx - 8, cy + 8, 17, 2, (110, 126, 176))


def login_frame(state="closed", key_x=None, key_turn=0, user=0.0, cursor=None, hot=False, flash=False, tickmark=False,
                look=(2, 1), blink=False, bob=0, slide=0, shake=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    lock(draw, x0 + 16, 30, state, shake)

    def paint(d):
        if key_x is not None:
            key(d, x0 + key_x, 33 + (key_turn % 2))
        if user:
            avatar(d, x0 + 58, 26)
        if tickmark:
            tick(d, x0 + 52, 40, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    if cursor:
        R(draw, x0 + 46, 20, 28, 11, WHITE if flash else (90, 200, 120) if hot else (45, 110, 65))
        text(draw, x0 + 50, 22, "5", WHITE, 1) if False else tick(draw, x0 + 57, 23, DARK if flash else WHITE)
        cursor_arrow(draw, *cursor)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def cursor_arrow(draw, x, y):
    cursor(draw, x, y)


def login_key():
    f = login_frame
    frames = intro(f)
    for k in range(7):                                                       # the key travels from Clawd to the lock
        t = ease((k + 1) / 7)
        frames.append(f(key_x=round(lerp(68, 30, t)), look=(2, 1), bob=1 if k == 0 else 0))
    for k in range(4):                                                       # turns
        frames.append(f(key_x=30, key_turn=k, look=(2, 1), bob=k % 2))
    for k in range(3):
        frames.append(f("open", key_x=30, look=(2, 0), bob=-1 if k == 0 else 0))
    for k in range(6):                                                       # the user appears and a check
        frames.append(f("open", user=min(1.0, (k + 1) / 3), tickmark=k > 1, look=(2, 0), blink=k == 5))
    frames += [f("open", user=1.0, tickmark=True, look=(2, 0))] * 3
    frames += [f("closed", user=0.0, look=(2, 1), blink=True)]
    return frames + [f()]


def login_browser():
    f = login_frame
    frames = intro(f)
    for k in range(3):                                                       # a browser asks to log in
        frames.append(f(cursor=(0, 0) if False else None, look=(2, 1)))
    start, target = (84, 54), (62, 27)
    for k in range(8):
        t = ease((k + 1) / 8)
        frames.append(f(cursor=(round(lerp(start[0], target[0], t)) + PX0, round(lerp(start[1], target[1], t))), hot=k > 5,
                        look=(2, 0 if k > 3 else 1)))
    frames += [f(cursor=(target[0] + PX0, target[1]), flash=True, bob=1)] * 2
    for k in range(4):
        frames.append(f("open", cursor=(target[0] + PX0 + k * 3, target[1] + k * 3), user=0.5 * (k > 1), look=(2, 0)))
    for k in range(6):
        frames.append(f("open", user=1.0, tickmark=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5))
    frames += [f("closed", look=(2, 1), blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- resume: a bookmarked conversation opens where it stopped
COVER, COVER_D, PAGE = (96, 70, 170), (64, 46, 120), (236, 232, 220)
BOOK_LINES = ((LIGHT_BLUE, 18), (PINK, 14), (LIGHT_BLUE, 20), (AMBER, 12), (PINK, 16))


def book(draw, x0, openness, ribbon=0, lines=0, hl=False, typed=0):
    """openness 0 closed .. 1 open. ribbon = how far the bookmark is pulled out (px)."""
    if openness <= 0:
        R(draw, x0 + 26, 14, 36, 34, COVER)
        R(draw, x0 + 26, 14, 4, 34, COVER_D)
        R(draw, x0 + 36, 22, 18, 3, (150, 124, 220))
        R(draw, x0 + 36, 28, 12, 2, (150, 124, 220))
        R(draw, x0 + 40, 48, 3, 6 + ribbon, RED)
    else:
        w = round(30 * openness)
        R(draw, x0 + 14, 12, 60, 38, COVER_D)
        R(draw, x0 + 44 - w, 14, w, 34, PAGE)
        R(draw, x0 + 44, 14, w, 34, PAGE)
        R(draw, x0 + 43, 14, 2, 34, (190, 184, 170))
        if openness >= 1:
            for i in range(lines):
                c, ln = BOOK_LINES[i]
                R(draw, x0 + 50, 18 + i * 6, ln + 6, 2, c)
                R(draw, x0 + 19, 18 + i * 6, ln, 2, (170, 164, 150))
            if hl:
                R(draw, x0 + 47, 17 + (lines - 1) * 6, 3, 4, RED)
            if typed:
                R(draw, x0 + 50, 18 + lines * 6, typed, 2, (110, 116, 140))
                R(draw, x0 + 50 + typed, 17 + lines * 6, 1, 4, DARK)


def resume_frame(openness=0.0, ribbon=0, lines=0, hl=False, typed=0, look=(2, 1), blink=False, bob=0, slide=0, key=False,
                 flip=None):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (26, 28, 40))
    book(draw, x0, openness, ribbon, lines, hl, typed)
    if flip is not None:                                                     # a page turning: a narrow page between the two halves
        w = abs(round(24 * math.cos(flip * math.pi)))
        R(draw, x0 + 44 - (w if flip > 0.5 else 0), 14, max(1, w), 34, (250, 246, 236))
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def resume_open():
    f = resume_frame
    frames = intro(f)
    for k in range(3):                                                       # the ribbon is pulled
        frames.append(f(ribbon=3 * (k + 1), look=(2, 2), bob=k % 2))
    frames += [f(ribbon=9, look=(2, 1))]
    for o in (0.3, 0.7, 1.0):
        frames.append(f(openness=o, look=(2, 1)))
    for n in range(1, 5):                                                    # the old conversation shows
        frames += [f(openness=1.0, lines=n, look=(2, min(2, n // 2)))] * 2
    frames += [f(openness=1.0, lines=4, hl=True, look=(2, 2), bob=-1 if k == 0 else 0) for k in range(4)]
    for k in range(6):                                                       # continues with a new line
        frames.append(f(openness=1.0, lines=4, hl=True, typed=4 + k * 3, key=k % 2 == 0, bob=k % 2, look=(2, 2)))
    frames += [f(openness=1.0, lines=4, hl=True, typed=19, look=(2, 1), blink=True)]
    for o in (0.7, 0.3):
        frames.append(f(openness=o, look=(2, 1)))
    frames += [f(ribbon=3), f(blink=True)]
    return frames + [f()]


def resume_flip():
    f = resume_frame
    frames = intro(f)
    for o in (0.4, 1.0):
        frames.append(f(openness=o, look=(2, 1)))
    for p in range(3):                                                       # pages flip until the marked one
        for k in range(4):
            frames.append(f(openness=1.0, flip=(k + 1) / 5, lines=1 + p, look=(2, 1)))
    frames += [f(openness=1.0, lines=5, hl=True, look=(2, 2), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    frames += [f(openness=0.5), f(openness=0.0, ribbon=3), f(blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- clear: a squeegee wipes the panel clean
CLEAR_LINES = ((LIGHT_BLUE, 38), (PINK, 28), (AMBER, 42), (GREEN, 30), (LIGHT_BLUE, 36), (PURPLE, 24))


def clear_frame(lines=0, wipe=None, flash=0, typed=0, sparkle=None, look=(2, 1), blink=False, bob=0, slide=0, key=False):
    """wipe: y of the squeegee blade (lines below it are already gone), None = not wiping."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (24, 26, 38))
    for i in range(lines):
        y = 14 + i * 7
        if wipe is None or y > wipe:
            c, w = CLEAR_LINES[i]
            R(draw, x0 + 8, y, w, 3, c)
    if wipe is not None:
        R(draw, x0 + 3, wipe - 1, 83, 3, WHITE)
        R(draw, x0 + 3, wipe - 5, 83, 1, (200, 210, 235))
        R(draw, x0 + 40, wipe - 12, 4, 8, (150, 154, 168))
    if typed:
        R(draw, x0 + 8, 52, typed, 3, (225, 228, 235))
    if flash:
        layer = Image.new("RGBA", (W, H), TRANS)
        ImageDraw.Draw(layer).rectangle([x0, PY0, x0 + 88, PY1], fill=(255, 255, 255, flash))
        img.alpha_composite(layer)
    draw = ImageDraw.Draw(img)
    if sparkle is not None:
        for k, (sx, sy) in enumerate(((14, 20), (70, 16), (44, 36), (62, 46), (20, 46))):
            if (sparkle + k * 2) % 6 < 3:
                R(draw, x0 + sx, sy, 1, 3, WHITE)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def clear_wipe():
    f = clear_frame
    frames = intro(f)
    for n in range(1, 7):                                                    # a conversation piles up
        frames += [f(lines=n, look=(2, min(2, n // 3)))] * 2
    frames += [f(lines=6, look=(2, 1), blink=True)]
    for k in range(9):                                                       # the squeegee sweeps down
        y = round(lerp(8, 58, (k + 1) / 9))
        frames.append(f(lines=6, wipe=y, look=(2, min(2, k // 3)), key=k % 2 == 0, bob=k % 2))
    frames += [f(sparkle=k, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    return frames + [f(blink=True), f()]


def clear_command():
    f = clear_frame
    frames = intro(f)
    for n in range(1, 7):
        frames += [f(lines=n, look=(2, min(2, n // 3)))] * 2
    for k in range(7):                                                       # types the command
        frames.append(f(lines=6, typed=round(20 * (k + 1) / 7), key=k % 2 == 0, bob=k % 2, look=(2, 2)))
    frames += [f(lines=6, typed=20, look=(2, 1), blink=True)]
    for k, a in enumerate((220, 120, 50)):                                   # Enter: a white flash and everything is gone
        frames.append(f(lines=6 if k == 0 else 0, flash=a, look=(1, 0), bob=-2 if k == 0 else 0))
    frames += [f(sparkle=k, look=(2, 0), blink=k == 5) for k in range(7)]
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("login", login_frame, [login_key, login_browser])
    finish("resume", resume_frame, [resume_open, resume_flip])
    finish("clear", clear_frame, [clear_wipe, clear_command])
