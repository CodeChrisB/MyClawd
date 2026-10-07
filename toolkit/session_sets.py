"""Five session sets: prompt (your message arrives), cwd (directory changed), done (turn finished),
session-start (boot / sunrise), stop-failure (API error).

python session_sets.py  ->  ../mine/{prompt,cwd,done,session-start,stop-failure}/
"""
import math

from props import *

SEAM_LOOK = (2, 1)
COIN_RIM = (200, 140, 30)


def finish(name, frame, loops):
    enter, leave = seam_slides(frame)
    save_set(name, enter, loops, leave)


def intro(frame, n=4):
    return [frame()] * n + [frame(blink=True)] + [frame()] * 2


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(round(lerp(a, b, t)) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- prompt: your message arrives
PAPER = (230, 232, 238)


def envelope(draw, x, y, opened):
    R(draw, x, y, 28, 18, PAPER)
    if opened:
        for r in range(8):
            R(draw, x + r, y - 1 - r, 28 - 2 * r, 1, (200, 204, 215))
    else:
        for r in range(9):
            R(draw, x + r, y + r, 28 - 2 * r, 1, (200, 204, 215))


def page(draw, x, y, hl, lines=3):
    R(draw, x, y, 22, 26, WHITE)
    for i in range(lines):
        R(draw, x + 3, y + 4 + i * 6, 16 - (i == 2) * 6, 2, AMBER if i < hl else (150, 154, 168))


def prompt_frame(env=None, pg=None, bubble=None, bang=False, look=SEAM_LOOK, blink=False, bob=0, slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        if env:
            ex, ey, opened = env
            envelope(d, x0 + ex, ey, opened)
        if pg:
            px, py, hl = pg
            page(d, x0 + px, py, hl)
        if bubble:
            n, size = bubble
            bw, bh = round(46 * size), round(28 * size)
            bx, by = x0 + 34, 18
            R(d, bx, by, bw, bh, WHITE)
            R(d, bx - 4, by + bh - 6, 5, 4, WHITE)                          # tail towards Clawd
            for i in range(min(n, 3)):
                R(d, bx + 4, by + 5 + i * 7, round((34 - i * 8) * size), 2, (110, 116, 130))
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if bang:
        R(draw, OX + 24, 0, 3, 5, AMBER)
        R(draw, OX + 24, 6, 3, 2, AMBER)
    return img


def prompt_letter():
    f = prompt_frame
    frames = intro(f)
    for k in range(6):                                                       # the envelope drops in
        t = ease((k + 1) / 6)
        frames.append(f(env=(30, round(lerp(-24, 28, t)), False), look=(2, 0 if k < 3 else 1)))
    frames += [f(env=(30, 28, False))] * 2 + [f(env=(30, 28, True))] * 2
    for k in range(4):                                                       # the page slides out
        frames.append(f(env=(30, 28, True), pg=(33, round(lerp(34, 12, ease((k + 1) / 4))), 0), look=(2, 0)))
    for k in range(12):                                                      # Clawd reads it line by line
        line = k // 4
        frames.append(f(env=(30, 28, True), pg=(33, 12, line + 1), look=(2, line), bob=1 if k % 4 == 3 else 0))
    frames += [f(env=(30, 28, True), pg=(33, 12, 3), look=(2, 0), bob=k % 2) for k in range(3)]
    for k in range(4):
        frames.append(f(env=(30, 28, True), pg=(33, round(lerp(12, 34, ease((k + 1) / 4))), 3)))
    frames += [f(env=(30, 28, True)), f(env=(30, 28, False))]
    for k in range(4):
        frames.append(f(env=(round(lerp(30, 100, ease((k + 1) / 4))), 28, False)))
    return frames + [f()]


def prompt_bubble():
    f = prompt_frame
    frames = intro(f)
    for k in range(4):                                                       # speech bubble pops
        frames.append(f(bubble=(0, ease((k + 1) / 4)), look=(2, 1)))
    for n in range(1, 4):                                                    # the text types in
        frames += [f(bubble=(n, 1.0), look=(2, n - 1), bang=n == 1, bob=-2 if n == 1 else 0)] * 3
    frames += [f(bubble=(3, 1.0), bang=True, look=(2, 0), bob=-1 * (k % 2)) for k in range(4)]
    frames += [f(bubble=(3, 1.0), look=(2, 1), blink=True)] + [f(bubble=(3, 1.0))] * 2
    for k in range(4):
        frames.append(f(bubble=(3, 1.0 - 0.9 * ease((k + 1) / 4))))
    return frames + [f()]


# ---------------------------------------------------------------- cwd: Clawd moves into another directory
def folder(draw, x, y, color):
    R(draw, x, y, 12, 4, color)
    R(draw, x, y + 3, 32, 22, color)
    R(draw, x, y + 7, 32, 1, tuple(max(0, c - 50) for c in color))
    R(draw, x + 4, y + 13, 22, 2, tuple(max(0, c - 70) for c in color))


def crumbs(draw, x0, n, flash):
    for i in range(n):
        R(draw, x0 + 5 + i * 17, 11, 12, 4, AMBER if (flash and i == n - 1) else (110, 116, 130))
        if i:
            R(draw, x0 + 2 + i * 17, 12, 2, 2, (80, 84, 98))


FOLDERS = [AMBER, LIGHT_BLUE, GREEN, PINK]


def cwd_frame(fx=0, fcolor=0, other=None, n=2, flash=False, look=SEAM_LOOK, blink=False, bob=0, slide=0):
    """other = (offset, colour index) for a second folder sliding past."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    crumbs(draw, x0, n, flash)

    def paint(d):
        folder(d, x0 + 28 + fx, 26, FOLDERS[fcolor])
        if other:
            folder(d, x0 + 28 + other[0], 26, FOLDERS[other[1]])
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def cwd_swap(to, n_to, back=True):
    f = cwd_frame
    frames = intro(f)
    for k in range(6):                                                       # cd into: old folder leaves left, new one arrives
        t = ease((k + 1) / 6)
        frames.append(f(fx=round(-80 * t), fcolor=0, other=(round(lerp(90, 0, t)), to), n=2, look=(2, 1), bob=k % 2 if k < 5 else 0))
    frames += [f(fx=0, fcolor=to, n=n_to, flash=k < 3, look=(2, 0 + (k > 3))) for k in range(8)]
    frames += [f(fx=0, fcolor=to, n=n_to, blink=True)]
    for k in range(6):                                                       # cd ..: back to the first one
        t = ease((k + 1) / 6)
        frames.append(f(fx=round(90 * t), fcolor=to, other=(round(lerp(-80, 0, t)), 0), n=n_to if k < 3 else 2, look=(2, 1)))
    return frames + [f()]


def cwd_walk():
    f = cwd_frame
    frames = intro(f)
    for step in (1, 2):                                                      # cd one level deeper, twice, then all the way up
        for k in range(5):
            t = ease((k + 1) / 5)
            frames.append(f(fx=round(-80 * t), fcolor=step - 1, other=(round(lerp(90, 0, t)), step), n=2 + step - 1, look=(2, 1)))
        frames += [f(fcolor=step, n=2 + step, flash=k < 2, look=(2, 1 + k % 2)) for k in range(4)]
    frames += [f(fcolor=2, n=4, look=(2, 0), blink=True)] * 2
    for k in range(7):                                                       # cd ~: the path shrinks back at once
        t = ease((k + 1) / 7)
        frames.append(f(fx=round(90 * t), fcolor=2, other=(round(lerp(-80, 0, t)), 0), n=max(2, 4 - k // 2), look=(2, 1)))
    return frames + [f()]


# ---------------------------------------------------------------- done: turn finished
CONFETTI = [(12, 1.2, PINK), (22, 0.9, YELLOW), (30, 1.4, LIGHT_BLUE), (40, 1.0, GREEN), (50, 1.3, PURPLE),
            (58, 0.8, AMBER), (66, 1.1, PINK), (74, 1.5, YELLOW), (18, 0.7, GREEN), (46, 1.6, LIGHT_BLUE),
            (62, 0.95, RED), (34, 1.15, PURPLE)]


def done_frame(badge=0.0, confetti=None, bell=None, smile=False, look=SEAM_LOOK, blink=False, bob=0, slide=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        if badge:
            r = max(1, round(14 * badge))
            cx, cy = x0 + 44, 33
            for yy in range(cy - r, cy + r + 1):
                w = round(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
                R(d, cx - w, yy, 2 * w, 1, GREEN)
            if badge > 0.8:
                tick(d, cx - 10, cy - 7, WHITE, 4)
        if bell is not None:
            swing, rings = bell
            bx = x0 + 44
            for r in range(16):                                              # bell body, swinging from the top
                w = 4 + round(r * 0.9) + (r > 13) * 3
                R(d, bx - w // 2 + round(swing * r / 16), 14 + r, w, 1, YELLOW if r < 15 else COIN_RIM)
            R(d, bx - 2 + round(swing * 1.2), 31, 4, 4, COIN_RIM)             # clapper
            if rings:
                for s in (-1, 1):
                    for k in range(3):
                        R(d, bx + s * (16 + k * 5), 22 - k * 3, 2, 8 + k * 6, (230, 200, 120))
        for i, (cx, speed, col) in enumerate(confetti or []):
            cy = round((confetti_t[0] * speed * 3 + i * 9) % 52) + 4
            R(d, x0 + cx, cy, 3, 3, col)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


confetti_t = [0]


def done_badge():
    f = done_frame
    frames = intro(f)
    for k, s in enumerate((0.3, 0.7, 1.15, 1.0)):                            # pop
        frames.append(f(badge=s, look=(2, 0), bob=-2 if k == 2 else 0))
    for k in range(18):                                                      # confetti falls, Clawd smiles and hops twice
        confetti_t[0] = k
        frames.append(f(badge=1.0, confetti=CONFETTI, smile=True, look=(2, 0), bob=-2 if k in (1, 2, 8, 9) else 0,
                        blink=k == 14))
    confetti_t[0] = 0
    frames += [f(badge=1.0, smile=True, look=(2, 1))] * 3
    for s in (0.6, 0.3):
        frames.append(f(badge=s, smile=True))
    return frames + [f(blink=True), f()]


def done_bell():
    f = done_frame
    frames = intro(f)
    for ring in range(3):
        for k, sw in enumerate((0, 3, 5, 3, 0, -3, -5, -3)):
            frames.append(f(bell=(sw, abs(sw) >= 5), smile=True, look=(2, 0), bob=-1 if abs(sw) == 5 else 0))
        if ring < 2:
            frames += [f(bell=(0, False), smile=True)] * 2
    frames += [f(bell=(0, False), smile=True, blink=True)] + [f(bell=(0, False), smile=True)] * 2
    return frames + [f()]


# ---------------------------------------------------------------- session-start: the Claude welcome box appears, both Clawds hop
TERM, TERM_BAR = (12, 14, 18), (40, 44, 54)
MG = 2                                   # grid of the small Clawd inside the box


def mini(draw, ox, oy, blink=False, smile=False):
    g = MG
    R(draw, ox, oy, 8 * g, 2 * g, CORAL)
    R(draw, ox - 2 * g, oy + 2 * g, 12 * g, 2 * g, CORAL)
    R(draw, ox, oy + 4 * g, 8 * g, 2 * g, CORAL)
    for lc in (0, 2, 5, 7):
        R(draw, ox + lc * g, oy + 6 * g, g, 2 * g, CORAL)
    for ex in (1, 6):
        if blink:
            R(draw, ox + ex * g, oy + g + 1, g, 1, BLACK)
        else:
            R(draw, ox + ex * g, oy + g, g, g, BLACK)
    if smile:
        R(draw, ox + 3 * g, oy + 2 * g + 1, 1, 1, BLACK)
        R(draw, ox + 3 * g + 1, oy + 2 * g + 2, 4, 1, BLACK)
        R(draw, ox + 3 * g + 5, oy + 2 * g + 1, 1, 1, BLACK)


def start_frame(show=False, hop=0, bob=0, smile=False, spark=None, look=SEAM_LOOK, blink=False, mini_blink=False, slide=0,
                typed=0, key=False):
    """Terminal window. Seam: empty prompt with the cursor. show: only the Claude welcome box (orange border, small Clawd
    and the text lines) and nothing else. hop = how far the small Clawd is lifted (px), bob = the big Clawd's offset."""
    img, draw = new_frame()
    x0, x1 = PX0 + slide, PX1 + slide
    draw.rectangle([x0 - 2, PY0 - 2, x1 + 2, PY1 + 2], fill=PANEL_EDGE)
    draw.rectangle([x0, PY0, x1, PY1], fill=TERM)
    draw.rectangle([x0, PY0, x0 + 88, PY0 + 7], fill=TERM_BAR)
    for i, c in enumerate((RED, YELLOW, GREEN)):
        draw.rectangle([x0 + 4 + i * 5, PY0 + 3, x0 + 5 + i * 5, PY0 + 4], fill=c)
    if show:
        draw.rectangle([x0 + 5, 17, x0 + 83, 54], outline=CORAL)
        mini(draw, x0 + 14, 28 - hop, mini_blink, smile)
        R(draw, x0 + 42, 26, 28, 3, WHITE)                                   # the welcome text, like the real banner
        R(draw, x0 + 42, 33, 36, 2, (110, 116, 130))
        R(draw, x0 + 42, 38, 26, 2, (110, 116, 130))
        R(draw, x0 + 42, 43, 32, 2, (110, 116, 130))
        if spark is not None:
            for k, (sx, sy) in enumerate(((10, 20), (36, 20), (78, 20), (12, 50))):
                if (spark + k * 2) % 6 < 3:
                    R(draw, x0 + sx, sy, 1, 3, YELLOW)
                    R(draw, x0 + sx - 1, sy + 1, 3, 1, YELLOW)
    else:
        R(draw, x0 + 6, 19, 2, 2, GREEN)
        R(draw, x0 + 8, 21, 2, 2, GREEN)
        R(draw, x0 + 6, 23, 2, 2, GREEN)
        if typed:
            R(draw, x0 + 13, 20, typed, 4, WHITE)                            # the typed command
        R(draw, x0 + 13 + typed + (1 if typed else 0), 19, 4, 6, WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


HOP = (0, 2, 4, 5, 4, 2)                 # how high the big Clawd is lifted per frame of a hop
MHOP = (0, 1, 2, 3, 2, 1)                # and the small one, in step with it


def hops(n, smile=True, spark=False):
    """n hops, both Clawds in the same frame of the same hop."""
    f = start_frame
    out = []
    for h in range(n):
        for k in range(6):
            out.append(f(show=True, hop=MHOP[k], bob=-HOP[k], smile=smile, look=(2, 0),
                         spark=len(out) if spark else None))
    return out


def typing(f):
    """Clawd types "claude" into the console and presses Enter."""
    out = [f(typed=round(26 * (k + 1) / 12), look=(2, 2), bob=k % 2, key=k % 2 == 0) for k in range(12)]
    return out + [f(typed=26, look=(2, 1), blink=k == 1) for k in range(3)]


def start_claude():
    f = start_frame
    frames = intro(f) + typing(f)
    frames += hops(2) + [f(show=True, smile=True, look=(2, 0))] * 4
    frames += [f(show=True, smile=True, mini_blink=True, blink=True)] + [f(show=True, smile=True)] * 3
    return frames + [f(blink=True), f()]


def start_party():
    f = start_frame
    frames = intro(f) + typing(f)
    frames += hops(1, spark=True)
    frames += [f(show=True, smile=True, bob=1 if k % 2 else 0, spark=k, look=(2, 0 if k % 4 < 2 else 1)) for k in range(6)]
    frames += hops(2, spark=True)
    frames += [f(show=True, smile=True, spark=k, mini_blink=k == 3, blink=k == 3) for k in range(5)]
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- stop-failure: the API call failed
def cloud(draw, x, y, color):
    R(draw, x + 2, y + 10, 32, 10, color)
    R(draw, x + 6, y + 6, 12, 8, color)
    R(draw, x + 14, y + 1, 14, 14, color)
    R(draw, x + 24, y + 6, 10, 10, color)


def bolt(draw, x, y):
    for i, (dx, w) in enumerate(((2, 4), (0, 4), (3, 4), (1, 4), (4, 4), (2, 3))):
        R(draw, x + dx, y + i * 4, w, 4, YELLOW)


def fail_frame(color=GREY, code=False, spin=None, bolt_on=False, mark=None, shake=0, look=SEAM_LOOK, blink=False, bob=0,
               slide=0, sweat_f=None, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    cloud(draw, x0 + 26 + shake, 12, color)
    if bolt_on:
        bolt(draw, x0 + 36, 0 + 6 + 6)
    if mark == "ok":
        tick(draw, x0 + 34, 18, WHITE, 3)
    elif mark == "x":
        cross(draw, x0 + 36, 17, WHITE, 3)
    if code:
        text(draw, x0 + 31, 40, "500", RED, 3)
    if spin is not None:
        for i in range(8):
            ang = i * math.pi / 4
            lit = (i - spin) % 8
            c = mix((50, 54, 66), WHITE, max(0, 1 - lit / 5)) if lit < 5 else (50, 54, 66)
            R(draw, round(x0 + 43 + math.cos(ang) * 9), round(48 + math.sin(ang) * 9), 3, 3, c)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def fail_start(f):
    frames = intro(f)
    frames += [f(bolt_on=True, look=(2, 0))] * 2
    for k in range(8):                                                       # cloud turns red and shakes, the code blinks
        frames.append(f(color=RED, code=k % 4 < 3, shake=(-1, 1)[k % 2] if k < 6 else 0, sweat_f=k, look=(1, 0),
                        bob=k % 2))
    frames += [f(color=RED, code=True, sweat_f=k, look=(1, 1)) for k in range(3)]
    return frames


def fail_retry(f, n=12, color=RED):
    return [f(color=color, spin=k % 8, look=(2, 1 + (k % 6 > 2)), sweat_f=k) for k in range(n)]


def fail_loop():
    f = fail_frame
    frames = fail_start(f) + fail_retry(f)
    frames += [f(color=RED, mark="x", sweat_f=k, look=(2, 2)) for k in range(6)]
    for k in range(3):
        frames.append(f(color=mix(RED, GREY, (k + 1) / 3)))
    return frames + [f(blink=True), f()]


def recover_loop():
    f = fail_frame
    frames = fail_start(f) + fail_retry(f, 14)
    frames += [f(color=GREEN, mark="ok", look=(2, 0), smile=True, bob=-2 if k == 0 else 0) for k in range(7)]
    for k in range(3):
        frames.append(f(color=mix(GREEN, GREY, (k + 1) / 3), smile=k < 2))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("prompt", prompt_frame, [prompt_letter, prompt_bubble])
    finish("cwd", cwd_frame, [lambda: cwd_swap(1, 3), cwd_walk])
    finish("done", done_frame, [done_badge, done_bell])
    finish("session-start", start_frame, [start_claude, start_party])
    finish("stop-failure", fail_frame, [fail_loop, recover_loop])
