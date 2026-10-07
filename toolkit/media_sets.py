"""Multimodal sets: paste-image, voice-input, screenshot, pdf, excel, powerpoint.

python media_sets.py  ->  ../mine/<set>/
Colours only hint at the file types (red pdf, green sheet, orange slides); no logos.
"""
import math
import random

from props import *

BOX = (36, 40, 52)
GREYT = (130, 136, 156)


def picture(draw, x, y, w=22, h=16, sun=True):
    """A tiny landscape: sky, sun, hill."""
    R(draw, x, y, w, h, (110, 170, 230))
    if sun:
        dot(draw, x + w - 6, y + 5, 3, YELLOW)
    R(draw, x, y + h - 5, w, 5, (70, 150, 80))
    for r in range(5):
        R(draw, x + 3 + r, y + h - 6 - r, 12 - 2 * r, 1, (90, 110, 120))


# ---------------------------------------------------------------- paste image
def keycap(draw, x, y, label, down):
    off = 1 if down else 0
    R(draw, x, y + 7, len(label) * 4 + 5, 3, (90, 94, 108))
    R(draw, x, y + off, len(label) * 4 + 5, 8, (225, 228, 238) if down else (186, 190, 204))
    text(draw, x + 3, y + 1 + off, label, (50, 54, 66), 1)


def paste_frame(down=0, card=None, chip=0, tickmark=False, cursor_xy=None, look=(2, 1), blink=False, bob=0, slide=0, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    keycap(draw, x0 + 6, 12, "CTRL", down > 0)
    keycap(draw, x0 + 36, 12, "V", down > 1)
    R(draw, x0 + 6, 42, 76, 13, BOX)                                         # the prompt box
    R(draw, x0 + 7, 43, 74, 11, (20, 24, 34))

    def paint(d):
        if chip:
            picture(d, x0 + 9, 44, 14, 9, chip > 1)
        if card:
            cx, cy = card
            picture(d, x0 + cx, cy)
        if tickmark:
            tick(d, x0 + 68, 20, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    if not chip:
        R(draw, x0 + 10, 46, 1, 6, WHITE)
    if cursor_xy:
        cursor(draw, *cursor_xy)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def paste_keys():
    f = paste_frame
    frames = intro(f)
    frames += [f(down=1, look=(2, 1), bob=1), f(down=2, look=(2, 1), bob=1)]
    for k in range(5):                                                       # the image drops into the box
        frames.append(f(down=2, card=(round(lerp(58, 9, ease((k + 1) / 5))), round(lerp(-18, 36, ease((k + 1) / 5)))),
                        look=(2, 0 if k < 3 else 2)))
    frames += [f(down=1, chip=1, look=(2, 2))] + [f(chip=1, look=(2, 1))]
    frames += [f(chip=2, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(7)]
    frames += [f(chip=1), f(chip=0), f(blink=True)]
    return frames + [f()]


def paste_drag():
    f = paste_frame
    frames = intro(f)
    start, end = (PX0 + 74, 22), (PX0 + 14, 46)
    for k in range(7):                                                       # an image is dragged over from the side
        t = ease((k + 1) / 7)
        pos = (round(lerp(start[0], end[0], t)), round(lerp(start[1], end[1], t)))
        frames.append(f(card=(pos[0] - PX0 - 4, pos[1] - 6), cursor_xy=pos, look=(2, 1 + (k > 3))))
    frames += [f(card=(10, 41), cursor_xy=end, look=(2, 2))] * 2
    frames += [f(chip=1, cursor_xy=(end[0] + k * 3, end[1] - k * 2), look=(2, 1)) for k in range(3)]
    frames += [f(chip=2, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(7)]
    frames += [f(chip=1), f(chip=0), f(blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- voice input
def voice_frame(rec=False, wave=None, text=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0, smile=False, glow=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    mx = x0 + 18
    R(draw, mx - 4, 16, 9, 16, (150, 156, 176))                              # the microphone
    R(draw, mx - 3, 17, 7, 14, (96, 102, 122))
    for k in range(3):
        R(draw, mx - 3, 20 + k * 3, 7, 1, (150, 156, 176))
    R(draw, mx - 7, 28, 2, 6, (120, 126, 146))
    R(draw, mx + 6, 28, 2, 6, (120, 126, 146))
    R(draw, mx - 7, 34, 15, 2, (120, 126, 146))
    R(draw, mx, 36, 1, 6, (120, 126, 146))
    R(draw, mx - 5, 42, 11, 2, (120, 126, 146))
    if rec:
        dot(draw, mx + 12, 18, 2, RED)
    if wave is not None:                                                     # the level meter
        rng = random.Random(wave)
        for k in range(9):
            h = 2 + rng.randint(1, 10)
            R(draw, x0 + 34 + k * 5, 24 - h // 2, 3, h, (110, 170, 230))
    R(draw, x0 + 34, 38, 50, 16, BOX)
    R(draw, x0 + 35, 39, 48, 14, (20, 24, 34))
    for i in range(3):
        n = max(0, min(text - i * 10, 10)) if text else 0
        R(draw, x0 + 38, 42 + i * 4, round(n * (4.2, 3.4, 2.4)[i]), 2, (225, 228, 235))
    if tickmark:
        tick(draw, x0 + 70, 28, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def voice_dictate(long=False):
    f = voice_frame
    frames = intro(f)
    frames += [f(rec=True, look=(2, 1))] * 2
    total = 30 if long else 22
    for k in range(total):                                                   # speaks, the level meter dances, words appear
        frames.append(f(rec=k % 6 < 4, wave=k + 5, text=round(30 * (k + 1) / total), glow=1 + k % 3 if k % 5 < 3 else 0,
                        look=(2, 1 if k % 8 < 5 else 2), bob=1 if k % 7 == 0 else 0))
    frames += [f(rec=False, text=30, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in (20, 10, 0):
        frames.append(f(text=k))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- screenshot: capture, then read it
def ui_shot(draw, x, y, w=32, h=24, boxes=0):
    R(draw, x, y, w, h, (236, 238, 244))
    R(draw, x, y, w, 4, (110, 120, 150))
    R(draw, x + 2, y + 1, 2, 2, RED)
    R(draw, x + 3, y + 6, 12, 8, (110, 170, 230))
    R(draw, x + 17, y + 6, w - 20, 2, (150, 156, 176))
    R(draw, x + 17, y + 10, w - 24, 2, (150, 156, 176))
    R(draw, x + 3, y + 16, 9, 5, GREEN)
    R(draw, x + 14, y + 16, w - 17, 5, (200, 204, 215))
    marks = ((x + 2, y + 5, 14, 10, AMBER), (x + 16, y + 5, w - 18, 9, LIGHT_BLUE), (x + 2, y + 15, 11, 7, PINK), (x + 13, y + 15, w - 15, 7, (160, 110, 220)))
    for bx, by, bw, bh, c in marks[:boxes]:
        R(draw, bx, by, bw, 1, c)
        R(draw, bx, by + bh - 1, bw, 1, c)
        R(draw, bx, by, 1, bh, c)
        R(draw, bx + bw - 1, by, 1, bh, c)


def shot_frame(sel=(1.0,), flash=0, shot=None, boxes=0, desc=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0,
               smile=False, cursor_xy=None):
    """sel = size of the viewfinder rectangle (1.0 big .. 0.55 small). shot = (x, y) of the captured thumbnail."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    if shot is None:
        s = sel[0]
        w, h = round(76 * s), round(44 * s)
        cx, cy = x0 + 44, 32
        L, T = cx - w // 2, cy - h // 2
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            px, py = L + dx * (w - 1), T + dy * (h - 1)
            R(draw, px - (4 if dx else 0), py, 5, 1, WHITE)
            R(draw, px, py - (4 if dy else 0), 1, 5, WHITE)
    else:
        ui_shot(draw, x0 + shot[0], shot[1], boxes=boxes)
    for i in range(desc):
        R(draw, x0 + 50, 18 + i * 6, (30, 24, 28)[i], 2, (225, 228, 235) if i == 0 else GREYT)
    if tickmark:
        tick(draw, x0 + 66, 40, GREEN, 3)
    if cursor_xy:
        cursor(draw, *cursor_xy)
    if flash:
        layer = Image.new("RGBA", (W, H), TRANS)
        ImageDraw.Draw(layer).rectangle([x0, PY0, x0 + 88, PY1], fill=(255, 255, 255, flash))
        img.alpha_composite(layer)
        draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def shot_read():
    f = shot_frame
    frames = intro(f)
    for k in range(4):                                                       # the viewfinder tightens
        frames.append(f((1.0 - 0.1 * (k + 1),), look=(2, 1), bob=1 if k == 3 else 0))
    for fl in (230, 120, 40):                                                # flash
        frames.append(f((0.6,), flash=fl, look=(2, 0), bob=-1 if fl == 230 else 0))
    for k in range(4):                                                       # the screenshot lands on the left
        frames.append(f(shot=(round(lerp(60, 8, ease((k + 1) / 4))), 18), look=(2, 1)))
    for n in range(1, 5):                                                    # Clawd finds the elements one by one
        frames += [f(shot=(8, 18), boxes=n, look=(2, 1 + n % 2))] * 2
    for n in range(1, 4):                                                    # and describes them
        frames += [f(shot=(8, 18), boxes=4, desc=n, look=(2, 1))] * 2
    frames += [f(shot=(8, 18), boxes=4, desc=3, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5)
               for k in range(7)]
    frames += [f(shot=(round(lerp(8, -40, ease((k + 1) / 4))), 18), desc=3 if k < 2 else 0) for k in range(4)]
    return frames + [f(blink=True), f()]


def shot_crop():
    f = shot_frame
    frames = intro(f)
    pos = (PX0 + 74, 52)
    for k in range(8):                                                       # drags a selection
        s = 1.0 - 0.06 * (k + 1)
        frames.append(f((s,), cursor_xy=(PX0 + 8 + round(70 * s), 8 + round(48 * s)), look=(2, 1 + (k > 3))))
    frames += [f((0.52,), cursor_xy=(PX0 + 44, 38), look=(2, 2), bob=1)] * 2
    for fl in (230, 120, 40):
        frames.append(f((0.52,), flash=fl, look=(2, 0)))
    for k in range(3):
        frames.append(f(shot=(8, 18), boxes=0, look=(2, 1)))
    for n in range(1, 5):
        frames += [f(shot=(8, 18), boxes=n, desc=min(3, n - 1), look=(2, 1))] * 2
    frames += [f(shot=(8, 18), boxes=4, desc=3, tickmark=True, smile=True, look=(2, 0), blink=k == 5) for k in range(6)]
    frames += [f(shot=(round(lerp(8, -40, ease((k + 1) / 4))), 18)) for k in range(4)]
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- pdf
def pdf_frame(page=0, flip=None, hl=0, out=0, table=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    for k in (2, 1):                                                         # pages behind
        R(draw, x0 + 8 + k * 3, 10 - k * 0 + k * 2, 28, 38, (170, 174, 190))
    px = x0 + 8

    def paint(d):
        R(d, px, 10, 28, 38, WHITE)
        R(d, px, 10, 28, 7, (200, 60, 60))
        text(d, px + 3, 11, "PDF", WHITE, 1)
        wflip = 28 if flip is None else round(28 * abs(math.cos(flip * math.pi)))
        for i in range(6):
            y = 21 + i * 4
            c = AMBER if i < hl else (170, 174, 190)
            R(d, px + 3, y, min(22, wflip) - (i % 3) * 3 if wflip > 4 else 0, 2, c)
        if table:
            for r_ in range(table):
                R(d, px + 3, 24 + r_ * 6, 22, 1, (110, 116, 140))
            R(d, px + 12, 24, 1, 6 * table - 0, (110, 116, 140))
        for i in range(out):                                                 # extracted lines on the right
            R(d, x0 + 46, 14 + i * 6, (30, 24, 34, 26)[i % 4], 3, (225, 228, 235) if i % 2 == 0 else LIGHT_BLUE)
        if tickmark:
            tick(d, x0 + 66, 42, GREEN, 3)
    clipped(img, x0, paint)
    for i in range(3):                                                       # page indicator
        R(img.__class__ and ImageDraw.Draw(img), x0 + 8 + i * 6, 52, 4, 2, WHITE if i == page else (60, 66, 82))
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def pdf_extract():
    f = pdf_frame
    frames = intro(f)
    for p in range(2):                                                       # reads two pages
        for k in range(5):
            frames.append(f(page=p, flip=None, hl=0, look=(2, 1 + (k > 2))))
        for k in range(6):                                                   # highlights flow into the summary
            frames.append(f(page=p, hl=min(6, k + 1), out=min(3, k // 2) + p, look=(2, 1)))
        for k in range(4):                                                   # next page turns
            frames.append(f(page=p, flip=(k + 1) / 5 if p == 0 else None, hl=6, out=3 if p == 0 else 4, look=(2, 1)))
    frames += [f(page=1, hl=6, out=4, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(7)]
    frames += [f(page=0, hl=3, out=2), f(page=0, hl=0, out=0), f(blink=True)]
    return frames + [f()]


def pdf_table():
    f = pdf_frame
    frames = intro(f)
    for k in range(5):
        frames.append(f(look=(2, 1)))
    for n in range(1, 5):                                                    # a table is spotted and read row by row
        frames += [f(table=n, look=(2, min(2, n // 2 + 1)))] * 2
    for n in range(1, 5):
        frames += [f(table=4, hl=n, out=n, look=(2, 2 - n // 3))] * 2
    frames += [f(table=4, hl=6, out=4, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(7)]
    frames += [f(table=2, hl=2, out=2), f(), f(blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- excel: a sheet, a formula, a chart
def sheet_frame(sel=None, formula=0, total=0, chart=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0, key=False, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (30, 34, 46))
    R(draw, x0, 6, 89, 7, (40, 130, 80))                                     # green title strip
    R(draw, x0 + 3, 8, 6, 3, WHITE)
    R(draw, x0 + 12, 8, 70, 3, (30, 90, 56))
    R(draw, x0 + 12, 8, formula, 3, WHITE)
    cw, ch = 11, 6
    gx, gy = x0 + 4, 16
    nums = ((6, 9, 4, 7), (8, 5, 9, 3), (4, 8, 6, 9), (9, 4, 7, 5), (5, 7, 3, 8))
    for r_ in range(6):
        for c_ in range(5 if not chart else 3):
            x, y = gx + c_ * (cw + 1), gy + r_ * (ch + 1)
            hdr = r_ == 0 or c_ == 0
            R(draw, x, y, cw, ch, (50, 56, 74) if hdr else (40, 44, 60))
            if r_ and c_:
                R(draw, x + 1, y + 2, nums[c_ - 1][min(r_ - 1, 3)] if r_ < 5 else 0, 2, (200, 204, 215))
    if total:
        x, y = gx + 1 * (cw + 1), gy + 5 * (ch + 1)
        R(draw, x, y, cw, ch, (40, 130, 80))
        R(draw, x + 1, y + 2, 9, 2, WHITE)
    if sel is not None:
        c_, r_, w_, h_ = sel
        x, y = gx + c_ * (cw + 1), gy + r_ * (ch + 1)
        ww, hh = w_ * (cw + 1) - 1, h_ * (ch + 1) - 1
        R(draw, x, y, ww, 1, WHITE)
        R(draw, x, y + hh - 1, ww, 1, WHITE)
        R(draw, x, y, 1, hh, WHITE)
        R(draw, x + ww - 1, y, 1, hh, WHITE)
    if chart:                                                                # a small bar chart appears
        R(draw, x0 + 46, 18, 38, 34, (24, 28, 40))
        for k in range(4):
            hgt = round((8, 14, 20, 12)[k] * min(1.0, chart))
            R(draw, x0 + 50 + k * 8, 48 - hgt, 5, hgt, (60, 180, 110))
    if tickmark:
        tick(draw, x0 + 62, 10, GREEN, 2) if False else tick(draw, x0 + 74, 14, WHITE, 1)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def sheet_sum():
    f = sheet_frame
    frames = intro(f)
    for k, sel in enumerate(((1, 1, 1, 1), (1, 1, 1, 2), (1, 1, 1, 3), (1, 1, 1, 4))):          # drags a selection down a column
        frames += [f(sel, look=(2, 1 + k // 2), key=True, bob=k % 2)] * 2
    for k in range(8):                                                       # types the formula
        frames.append(f((1, 1, 1, 4), formula=round(30 * (k + 1) / 8), key=k % 2 == 0, bob=k % 2, look=(2, 0)))
    frames += [f((1, 5, 1, 1), formula=30, total=1, look=(2, 2), bob=-1)] * 3
    frames += [f((1, 5, 1, 1), formula=30, total=1, tickmark=True, smile=True, look=(2, 1), blink=k == 5) for k in range(6)]
    for k in range(3):
        frames.append(f(None, formula=round(30 * (1 - (k + 1) / 3)), total=1 if k < 1 else 0))
    return frames + [f(blink=True), f()]


def sheet_chart():
    f = sheet_frame
    frames = intro(f)
    frames += [f((1, 1, 3, 4), look=(2, 1))] * 3
    for k in range(7):                                                       # a chart grows out of the data
        frames.append(f((1, 1, 3, 4), chart=(k + 1) / 7, look=(2, 1 - (k > 3)), bob=1 if k == 0 else 0))
    frames += [f((1, 1, 3, 4), chart=1.0, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in range(3):
        frames.append(f((1, 1, 3, 4) if k < 2 else None, chart=max(0.0, 1.0 - 0.45 * (k + 1))))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- powerpoint: slides
ORANGE_D = (220, 100, 50)


def slide_frame(cur=0, wipe=None, title=1.0, bullets=3, art=False, laser=None, play=False, look=(2, 1), blink=False, bob=0, slide=0,
                key=False, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (30, 32, 44))
    for i in range(3):                                                       # thumbnails
        y = 12 + i * 14
        R(draw, x0 + 4, y, 18, 11, WHITE if i != cur else (255, 244, 226))
        R(draw, x0 + 4, y, 2, 11, ORANGE_D)
        R(draw, x0 + 8, y + 2, 10 - i * 2, 1, (150, 156, 176))
        R(draw, x0 + 8, y + 5, 8, 1, (150, 156, 176))
        if i == cur:
            R(draw, x0 + 2, y - 1, 22, 1, ORANGE_D)
            R(draw, x0 + 2, y + 11, 22, 1, ORANGE_D)
            R(draw, x0 + 2, y - 1, 1, 13, ORANGE_D)
            R(draw, x0 + 23, y - 1, 1, 13, ORANGE_D)
    layer = [(26, 3), (20, 3), (30, 4)][cur % 3]
    sx, sy, sw, sh = x0 + 28, 14, 56, 34
    R(draw, sx, sy, sw, sh, WHITE)
    R(draw, sx, sy, 3, sh, ORANGE_D)
    R(draw, sx + 6, sy + 4, round(layer[0] * 1.4 * title), 3, (60, 66, 84))
    for i in range(bullets):
        R(draw, sx + 6, sy + 12 + i * 6, 2, 2, ORANGE_D)
        R(draw, sx + 11, sy + 12 + i * 6, (30, 24, 32)[i] - cur * 2, 2, (150, 156, 176))
    if art:
        picture(draw, sx + 32, sy + 12, 20, 16)
    if wipe is not None:                                                     # transition: a curtain wipes across the slide
        R(draw, sx + round(sw * wipe), sy, sw - round(sw * wipe), sh, (30, 32, 44))
    if laser:
        dot(draw, x0 + laser[0], laser[1], 2, RED)
    if play:
        for r in range(6):
            R(draw, x0 + 40 + r, 28 + r, 7 - 2 * r if False else max(1, 8 - 2 * r), 1, WHITE)
            R(draw, x0 + 40 + r, 28 - r, max(1, 8 - 2 * r), 1, WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def slides_present():
    f = slide_frame
    frames = intro(f)
    for target in (1, 2, 0):                                                 # steps through the deck with a laser pointer
        for k in range(3):
            frames.append(f(cur=target - 1 if target else 2, laser=(40 + k * 9, 20 + k * 4), look=(2, 1 + k % 2)))
        for k in range(4):
            frames.append(f(cur=target, wipe=(k + 1) / 4 if k < 3 else None, look=(2, 1), bob=1 if k == 0 else 0))
        frames += [f(cur=target, laser=(60 - target * 5, 30), look=(2, 2))] * 2
    return frames + [f(blink=True), f()]


def slides_build():
    f = slide_frame
    frames = intro(f)
    for k in range(6):                                                       # the title is typed
        frames.append(f(title=(k + 1) / 6, bullets=0, key=k % 2 == 0, bob=k % 2, look=(2, 0)))
    for n in range(1, 4):                                                    # the bullets pop in
        frames += [f(bullets=n, key=k == 0, bob=1 if k == 0 else 0, look=(2, 1 + n // 2)) for k in range(3)]
    frames += [f(art=True, look=(2, 0), bob=-1 if k == 0 else 0) for k in range(4)]     # a picture lands
    frames += [f(art=True, play=k > 1, smile=True, look=(2, 0), blink=k == 6) for k in range(8)]
    for k in range(3):
        frames.append(f(bullets=2 - k if k < 2 else 0, title=0.5, art=k < 1))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("paste-image", paste_frame, [paste_keys, paste_drag])
    finish("voice-input", voice_frame, [lambda: voice_dictate(False), lambda: voice_dictate(True)])
    finish("screenshot", shot_frame, [shot_read, shot_crop])
    finish("pdf", pdf_frame, [pdf_extract, pdf_table])
    finish("excel", sheet_frame, [sheet_sum, sheet_chart])
    finish("powerpoint", slide_frame, [slides_present, slides_build])
