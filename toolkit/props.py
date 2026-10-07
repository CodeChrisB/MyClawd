"""Small shared drawing helpers for set files: rectangles, ticks, a tiny 3x5 font, zzz, sweat, cursor."""
import math

from PIL import Image, ImageDraw

from clawd_core import *

BLUE = (100, 160, 220)
GREY = (70, 74, 86)
DARK = (14, 18, 26)
AMBER = (240, 170, 60)
INK = (225, 228, 235)


def R(draw, x, y, w, h, color):
    """Filled rectangle by position and size in px."""
    if w > 0 and h > 0:
        draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def tick(draw, x, y, color=GREEN, s=1):
    """Check mark, 5x4 blocks of s px, top-left at x,y."""
    for dx, dy in ((0, 2), (1, 3), (2, 2), (3, 1), (4, 0)):
        R(draw, x + dx * s, y + dy * s, s, s, color)


def cross(draw, x, y, color=RED, s=1):
    """X, 5x5 blocks of s px."""
    for i in range(5):
        R(draw, (x + i * s), y + i * s, s, s, color)
        R(draw, x + (4 - i) * s, y + i * s, s, s, color)


GLYPHS = {
    "5": ["###", "#..", "###", "..#", "###"], "7": ["###", "..#", ".#.", ".#.", ".#."],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"], "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "Z": ["###", "..#", ".#.", "#..", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"], "2": ["###", "..#", "###", "#..", "###"],
    "%": ["#.#", "..#", ".#.", "#..", "#.#"],
    "?": ["###", "..#", ".##", "...", ".#."], "9": ["###", "#.#", "###", "..#", "###"], "4": ["#.#", "#.#", "###", "..#", "..#"],
    "E": ["###", "#..", "##.", "#..", "###"], "S": ["###", "#..", "###", "..#", "###"], "C": ["###", "#..", "#..", "#..", "###"],
}


def text(draw, x, y, s, color, scale=2):
    """Tiny 3x5 font (digits 0 2 5 7, H, D, Z, %). Each char is 3*scale wide with 1*scale gap."""
    for ch in s:
        for r, row in enumerate(GLYPHS[ch]):
            for c, v in enumerate(row):
                if v == "#":
                    R(draw, x + c * scale, y + r * scale, scale, scale, color)
        x += 4 * scale
    return x


def zzz(draw, f, x=80, y=34, n=3, color=LIGHT_BLUE):
    """n small z letters floating up and to the right; f is the frame counter (period 24)."""
    for k in range(n):
        t = ((f + k * 8) % 24) / 24
        zx, zy = round(x + t * 10 + k * 2), round(y - t * 24)
        if 6 <= zy <= PY1 - 4 and t < 0.9:
            R(draw, zx, zy, 3, 1, color)
            R(draw, zx + 1, zy + 1, 1, 1, color)
            R(draw, zx, zy + 2, 3, 1, color)


def sweat(draw, bob=0, f=0):
    """Sweat drop beside Clawd's head that slides down."""
    x, y = OX + 8 * G + 3, OY + 4 + bob + (f % 6)
    R(draw, x, y, 2, 1, BLUE)
    R(draw, x - 1, y + 1, 4, 2, BLUE)


def cursor(draw, x, y):
    """White mouse arrow, tip at x,y."""
    for i, w in enumerate((1, 2, 3, 4, 5, 4, 3, 2)):
        R(draw, x, y + i, w, 1, WHITE)
    R(draw, x + 1, y + 8, 2, 2, WHITE)


def key_press(draw, bob):
    """Two yellow blocks near Clawd's right hand while he taps."""
    hx, hy = OX + 10 * G + 2, OY + 2 * G + bob
    R(draw, hx, hy - 3, 2, 2, YELLOW)
    R(draw, hx + 3, hy + 1, 2, 2, YELLOW)


def seam_slides(frame):
    """Enter and exit for sets whose frame() takes look= and slide=."""
    return (lambda: slide_frames(lambda look, slide: frame(look=look, slide=slide), ENTER, False),
            lambda: slide_frames(lambda look, slide: frame(look=look, slide=slide), EXIT, True))


def clipped(img, x0, painter):
    """Draw with painter(draw) on a layer and keep only what falls inside the panel (things can enter from outside)."""
    layer, ld = new_frame()
    painter(ld)
    img.alpha_composite(layer.crop((x0, PY0, x0 + 89, PY1 + 1)), (x0, PY0))


def dot(draw, cx, cy, r, color):
    """Filled circle by centre and radius, pixel by pixel (no anti-aliasing)."""
    for yy in range(cy - r, cy + r + 1):
        w = round(math.sqrt(max(0, r * r + 0.5 - (yy - cy) ** 2)))
        R(draw, cx - w, yy, 2 * w + 1, 1, color)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(round(lerp(a, b, t)) for a, b in zip(c1, c2))


def intro(frame, n=4):
    return [frame()] * n + [frame(blink=True)] + [frame()] * 2


def finish(name, frame, loops):
    enter, leave = seam_slides(frame)
    save_set(name, enter, loops, leave)
