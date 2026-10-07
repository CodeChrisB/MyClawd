"""Build and CI, docs and learning: ci-pipeline, build, container, docs-read, tutorial, learned.

python build_sets.py  ->  ../mine/<set>/
"""
import math

from props import *

BOX = (36, 40, 52)


# ---------------------------------------------------------------- CI pipeline: stages light up one after another
STAGE_X = (6, 26, 46, 66)
STAGE_NAMES = ("lint", "test", "build", "ship")


def stage_icon(draw, x, y, i, col):
    if i == 0:                                                               # lint: three lines
        for k in range(3):
            R(draw, x + 3, y + 3 + k * 3, 10 - k * 2, 1, col)
    elif i == 1:                                                             # test: a flask
        R(draw, x + 6, y + 2, 4, 4, col)
        R(draw, x + 4, y + 6, 8, 6, col)
    elif i == 2:                                                             # build: a brick
        R(draw, x + 3, y + 4, 10, 7, col)
        R(draw, x + 5, y + 6, 2, 1, BOX)
        R(draw, x + 9, y + 8, 2, 1, BOX)
    else:                                                                    # ship: an arrow up
        R(draw, x + 7, y + 3, 2, 8, col)
        R(draw, x + 5, y + 5, 6, 1, col)
        R(draw, x + 6, y + 4, 4, 1, col)


def ci_frame(status=(0, 0, 0, 0), pulse=0, flow=None, banner=None, look=(2, 1), blink=False, bob=0, slide=0, sweat_f=None,
             key=False, smile=False):
    """status per stage: 0 pending, 1 running, 2 pass, 3 fail. flow = stage index a data dot is travelling to."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    for i, x in enumerate(STAGE_X):
        st = status[i]
        col = [(90, 96, 116), AMBER if pulse % 2 == 0 else (170, 120, 40), GREEN, RED][st]
        R(draw, x0 + x, 24, 18, 18, col if st else BOX)
        R(draw, x0 + x + 1, 25, 16, 16, (20, 24, 34) if st < 2 else mix((20, 24, 34), col, 0.35))
        stage_icon(draw, x0 + x + 1, 25, i, col if st != 1 else WHITE)
        if st == 2:
            tick(draw, x0 + x + 6, 35, WHITE, 1)
        if st == 3:
            cross(draw, x0 + x + 6, 35, WHITE, 1)
        if i < 3:
            R(draw, x0 + x + 19, 32, 1, 2, (70, 76, 92))
            R(draw, x0 + x + 20 - 1, 32, 2, 2, (70, 76, 92))
    if flow is not None:
        fx = x0 + STAGE_X[flow] - 4 + 0
        R(draw, fx - 1, 31, 4, 4, WHITE)
    if banner:
        R(draw, x0 + 6, 48, 76, 4, BOX)
        R(draw, x0 + 7, 49, round(74 * banner[0]), 2, banner[1])
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def ci_run(fail=None):
    f = ci_frame
    frames = intro(f)
    st = [0, 0, 0, 0]
    i = 0
    while i < 4:
        for k in range(4):                                                   # a stage runs
            s = list(st)
            s[i] = 1
            frames.append(f(tuple(s), pulse=k, flow=i if k < 1 else None, banner=(sum(1 for v in st if v == 2) / 4 + k / 16, AMBER),
                            look=(2, 1 + (k > 1))))
        if fail is not None and i == fail:
            st[i] = 3
            frames += [f(tuple(st), banner=(i / 4, RED), sweat_f=k, look=(1, 1), bob=k % 2) for k in range(6)]
            frames += [f(tuple(st), banner=(i / 4, RED), key=k % 2 == 0, bob=k % 2, look=(2, 2), sweat_f=k) for k in range(5)]
            st[i] = 0
            fail = None
            continue
        st[i] = 2
        frames.append(f(tuple(st), banner=((i + 1) / 4, GREEN), bob=1, look=(2, 1)))
        i += 1
    frames += [f((2, 2, 2, 2), banner=(1.0, GREEN), smile=True, look=(2, 0), bob=-2 if k == 0 else 0, blink=k == 6) for k in range(8)]
    for k in range(4):
        frames.append(f(tuple(2 if j < 3 - k else 0 for j in range(4)), banner=(max(0, 0.75 - 0.25 * k), GREEN)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- build: sources go in, a package comes out
def build_frame(files=0, moving=None, gear=0, bar=0.0, out=0.0, warn=False, tickmark=False, shake=0, look=(2, 1), blink=False,
                bob=0, slide=0, key=False, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        for i in range(files):                                               # source files waiting on the left
            R(d, x0 + 6, 14 + i * 12, 10, 10, WHITE)
            R(d, x0 + 8, 17 + i * 12, 6, 1, (140, 146, 166))
            R(d, x0 + 8, 20 + i * 12, 4, 1, (140, 146, 166))
        if moving:
            mx, my = moving
            R(d, x0 + mx, my, 10, 10, WHITE)
            R(d, x0 + mx + 2, my + 3, 6, 1, (140, 146, 166))
        R(d, x0 + 28 + shake, 18, 28, 28, (70, 76, 92))                       # the machine
        R(d, x0 + 30 + shake, 20, 24, 14, (20, 24, 34))
        cx, cy = x0 + 42 + shake, 27
        if gear % 2 == 0:
            R(d, cx - 5, cy - 1, 11, 3, AMBER)
            R(d, cx - 1, cy - 5, 3, 11, AMBER)
        else:
            for k in range(-4, 5):
                R(d, cx + k, cy + k, 2, 2, AMBER)
                R(d, cx + k, cy - k, 2, 2, AMBER)
        dot(d, cx, cy, 2, (20, 24, 34))
        R(d, x0 + 32 + shake, 38, 20, 4, (36, 40, 52))
        R(d, x0 + 32 + shake, 38, round(20 * bar), 4, AMBER if warn else GREEN)
        R(d, x0 + 60, 36, 24, 2, (90, 96, 116))                               # output belt and the package
        if out:
            px = round(lerp(54, 66, min(1.0, out)))
            R(d, x0 + px, 28, 14, 10, (200, 160, 90))
            R(d, x0 + px, 28, 14, 2, (230, 190, 120))
            R(d, x0 + px + 6, 28, 2, 10, RED)
        if tickmark:
            tick(d, x0 + 66, 16, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def build_make(warn=False):
    f = build_frame
    frames = intro(f)
    for i in range(3):                                                       # three files, one by one, into the machine
        left = 3 - i
        for k in range(4):
            t = (k + 1) / 4
            frames.append(f(files=left - 1, moving=(round(lerp(6, 34, t)), round(lerp(14 + i * 12 + (left - 1 - i) * 0, 22, t))),
                            gear=k, bar=i / 3, look=(2, 1)))
        for k in range(3):
            frames.append(f(files=left - 1, gear=k + i, bar=(i + (k + 1) / 3) / 3, shake=(-1, 1)[k % 2] if k < 2 else 0,
                            look=(2, 2), bob=k % 2, key=k == 0))
    for k in range(2):
        frames.append(f(gear=k, bar=1.0, warn=warn, look=(2, 1)))
    for k in range(6):                                                       # the package comes out
        frames.append(f(gear=k, bar=1.0, out=(k + 1) / 6, warn=warn and k % 2 == 0, look=(2, 1)))
    frames += [f(bar=1.0, out=1.0, tickmark=True, smile=True, look=(2, 0), bob=-2 if k == 0 else 0, blink=k == 5) for k in range(7)]
    for k in range(3):
        frames.append(f(bar=1.0 - 0.4 * (k + 1), out=max(0.0, 1.0 - 0.5 * (k + 1))))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- container build: layers stack up, the container is sealed
LAYER_C = ((90, 150, 230), (160, 110, 220), (80, 190, 170), (240, 170, 60), (230, 124, 90))


def container_frame(layers=0, sliding=None, cached=(), sealed=0.0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0,
                    key=False, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 12, 52, 64, 3, (90, 96, 116))
    cx0 = x0 + 20

    def paint(d):
        for i in range(layers):
            R(d, cx0, 47 - i * 6, 48, 5, LAYER_C[i])
            R(d, cx0, 47 - i * 6, 48, 1, mix(LAYER_C[i], WHITE, 0.4))
            if i in cached:
                for sx in range(4, 44, 8):
                    R(d, cx0 + sx, 49 - i * 6, 3, 2, YELLOW)
        if sliding:
            i, sx = sliding
            R(d, x0 + sx, 47 - i * 6, 48, 5, LAYER_C[i])
        if sealed:
            h = round(32 * sealed)
            R(d, cx0 - 2, 51 - h, 52, 2, (220, 224, 235))
            R(d, cx0 - 2, 51 - h, 2, h, (220, 224, 235))
            R(d, cx0 + 48, 51 - h, 2, h, (220, 224, 235))
            if sealed >= 1:
                R(d, cx0 - 2, 19, 52, 2, (220, 224, 235))
        if tickmark:
            tick(d, x0 + 66, 12, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def container_build(cache=()):
    f = container_frame
    frames = intro(f)
    for i in range(5):                                                       # layers slide in and stack
        for k in range(3):
            frames.append(f(layers=i, sliding=(i, round(lerp(-52, 20, ease((k + 1) / 3)))) if i not in cache else None,
                            cached=cache, look=(2, 2 - i // 2), key=k == 1, bob=1 if k == 1 else 0))
        frames.append(f(layers=i + 1, cached=cache, look=(2, 2 - i // 2)))
    for k in range(5):                                                       # the container is sealed around it
        frames.append(f(layers=5, cached=cache, sealed=(k + 1) / 5, look=(2, 1)))
    frames += [f(layers=5, cached=cache, sealed=1.0, tickmark=True, smile=True, look=(2, 0), bob=-2 if k == 0 else 0,
                 blink=k == 6) for k in range(8)]
    for k in range(4, -1, -1):
        frames.append(f(layers=k + 1 if k else 1, cached=cache, sealed=max(0.0, k / 5)))
    frames += [f(layers=0)]
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- docs: reading documentation
def docs_frame(nav=0, page=0, query=0, hit=0, flip=None, look=(2, 1), blink=False, bob=0, slide=0, key=False, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (30, 34, 46))
    R(draw, x0, 6, 89, 7, (46, 50, 66))
    R(draw, x0 + 30, 8, 50, 3, (24, 28, 38))
    if query:
        R(draw, x0 + 32, 9, query, 1, WHITE)
    for i in range(4):                                                       # sidebar
        c = AMBER if i == nav else (110, 116, 140)
        R(draw, x0 + 4, 17 + i * 8, 18, 3, c)
        if i == nav:
            R(draw, x0 + 2, 17 + i * 8 - 1, 1, 5, AMBER)
    R(draw, x0 + 26, 14, 1, 42, (50, 56, 74))
    layouts = (((30, WHITE), (46, (130, 136, 156)), (40, (130, 136, 156)), (46, (130, 136, 156)), (30, (130, 136, 156)), (42, (130, 136, 156))),
               ((24, WHITE), (50, (130, 136, 156)), (34, (130, 136, 156)), (46, (130, 136, 156)), (40, (130, 136, 156)), (28, (130, 136, 156))),
               ((36, WHITE), (44, (130, 136, 156)), (48, (130, 136, 156)), (30, (130, 136, 156)), (42, (130, 136, 156)), (36, (130, 136, 156))),
               ((28, WHITE), (48, (130, 136, 156)), (36, (130, 136, 156)), (44, (130, 136, 156)), (28, (130, 136, 156)), (46, (130, 136, 156))))
    lines = layouts[page % 4]
    w_all = 0
    for i, (w, c) in enumerate(lines):
        y = 18 + i * 6
        wd = w if flip is None else round(w * abs(math.cos(flip * math.pi)))
        R(draw, x0 + 32, y, wd, 3 if i == 0 else 2, c)
        if hit and i == 3:
            R(draw, x0 + 31, y - 1, 12, 4, AMBER)
            R(draw, x0 + 32, y, wd, 2, (40, 30, 10))
    if hit and hit > 1:
        tick(draw, x0 + 78, 33, GREEN, 1)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def docs_browse():
    f = docs_frame
    frames = intro(f)
    for target in (1, 2, 3, 0):                                              # clicks through the sections, reads each page
        for k in range(3):
            frames.append(f(nav=target, page=target - 1 if k == 0 else target, look=(2, 1 if k == 0 else 2)))
        for k in range(4):
            frames.append(f(nav=target, page=target, look=(2, 1 + (k > 1))))
        frames += [f(nav=target, page=target, look=(2, 2), blink=target == 2)] * 2
    return frames[:-2] + [f(nav=0, page=0, blink=True), f()]


def docs_search():
    f = docs_frame
    frames = intro(f)
    for k in range(8):                                                       # types a query in the search box
        frames.append(f(query=round(18 * (k + 1) / 8), key=k % 2 == 0, bob=k % 2, look=(2, 0)))
    for k in range(5):                                                       # the match lights up
        frames.append(f(query=18, hit=1, look=(2, 1 + (k > 2))))
    frames += [f(query=18, hit=2, look=(2, 2), smile=True, bob=-1 if k == 0 else 0, blink=k == 5) for k in range(7)]
    for k in range(3):
        frames.append(f(query=round(18 * (1 - (k + 1) / 3))))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- tutorial: follow the steps, build the result
def tutorial_frame(done=0, active=None, pulse=0, built=0, spark=None, look=(2, 1), blink=False, bob=0, slide=0, key=False, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    for i in range(3):
        y = 12 + i * 15
        cx, cy = x0 + 12, y + 6
        if i < done:
            dot(draw, cx, cy, 6, GREEN)
            tick(draw, cx - 3, cy - 2, WHITE, 1)
        elif active == i:
            dot(draw, cx, cy, 6, AMBER if pulse % 2 == 0 else (170, 120, 40))
            text(draw, cx - 1, cy - 2, "123"[i], DARK, 1)
        else:
            dot(draw, cx, cy, 6, (60, 66, 82))
            text(draw, cx - 1, cy - 2, "123"[i], (150, 156, 176), 1)
        R(draw, x0 + 22, y + 3, (22, 28, 20)[i], 2, (150, 156, 176) if i >= done else (80, 86, 104))
        R(draw, x0 + 22, y + 7, (14, 18, 12)[i], 2, (110, 116, 140) if i >= done else (70, 76, 92))
        if i < 2:
            R(draw, cx, y + 12, 1, 3, (60, 66, 82))
    bx, by = x0 + 54, 20                                                     # the little house that is being built
    if built >= 1:
        R(draw, bx, by + 14, 24, 14, (230, 190, 130))
    if built >= 2:
        for r in range(8):
            R(draw, bx - 2 + r, by + 13 - r, 28 - 2 * r, 1, RED)
    if built >= 3:
        R(draw, bx + 9, by + 19, 6, 9, (120, 80, 50))
        R(draw, bx + 3, by + 18, 4, 4, LIGHT_BLUE)
        R(draw, bx + 17, by + 18, 4, 4, LIGHT_BLUE)
    if spark is not None:
        for k, (sx, sy) in enumerate(((50, 14), (80, 18), (84, 40))):
            if (spark + k * 2) % 6 < 3:
                R(draw, x0 + sx, sy, 1, 3, YELLOW)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def tutorial_run(build=True):
    f = tutorial_frame
    frames = intro(f)
    for i in range(3):
        for k in range(5):
            frames.append(f(done=i, active=i, pulse=k, built=i if build else 0, key=k % 2 == 0, bob=k % 2, look=(2, i)))
        frames.append(f(done=i + 1, built=i + 1 if build else 0, bob=-1, look=(2, i)))
    frames += [f(done=3, built=3 if build else 0, spark=k, smile=True, look=(2, 0), blink=k == 7) for k in range(9)]
    for k in range(3, 0, -1):
        frames.append(f(done=k - 1, built=k - 1 if build else 0))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- learned something: a book, a bulb, an XP bar
def learn_frame(book=0.0, bulb=0, xp=0.0, star=0, spark=None, look=(2, 1), blink=False, bob=0, slide=0, smile=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    bx, by = x0 + 14, 26
    if book <= 0:
        R(draw, bx, by, 26, 22, (96, 70, 170))
        R(draw, bx, by, 3, 22, (64, 46, 120))
        R(draw, bx + 7, by + 5, 14, 2, (150, 124, 220))
    else:
        w = round(13 * min(1, book))
        R(draw, bx - 1, by - 1, 28, 24, (96, 70, 170))
        R(draw, bx + 13 - w, by, w, 22, (240, 236, 224))
        R(draw, bx + 13, by, w, 22, (240, 236, 224))
        if book >= 1:
            for i in range(4):
                R(draw, bx + 2, by + 3 + i * 4, 9, 1, (200, 196, 182))
                R(draw, bx + 15, by + 3 + i * 4, 9, 1, (200, 196, 182))
            if bulb:
                for k in range(5):                                           # light rays rising out of the book
                    R(draw, bx + 4 + k * 4, by - 4 - (bulb + k) % 4 * 2, 1, 3, YELLOW)
    if bulb:
        cx, cy = x0 + 62, 20
        dot(draw, cx, cy, 6, (255, 218, 96))
        R(draw, cx - 3, cy + 6, 6, 3, (120, 126, 150))
        for k in range(8):
            a = k * math.pi / 4
            R(draw, round(cx + math.cos(a) * 10), round(cy + math.sin(a) * 10), 2, 2, YELLOW)
    R(draw, x0 + 44, 46, 38, 5, (36, 40, 52))
    R(draw, x0 + 45, 47, round(36 * xp), 3, GREEN)
    if star:
        cx, cy = x0 + 74, 36                                                 # a plus-shaped star that pops in
        sz = (1, 2, 3, 2)[min(3, star - 1)]
        R(draw, cx - sz, cy - 4, 2 * sz + 1, 9, YELLOW) if sz >= 2 else None
        R(draw, cx - 1, cy - 4, 3, 9, YELLOW)
        R(draw, cx - 4, cy - 1, 9, 3, YELLOW)
        R(draw, cx - 3, cy - 3, 2, 2, YELLOW)
        R(draw, cx + 2, cy - 3, 2, 2, YELLOW)
        R(draw, cx - 3, cy + 2, 2, 2, YELLOW)
        R(draw, cx + 2, cy + 2, 2, 2, YELLOW)
    if spark is not None:
        for k, (sx, sy) in enumerate(((44, 14), (80, 24), (10, 22), (60, 40))):
            if (spark + k * 2) % 6 < 3:
                R(draw, x0 + sx, sy, 1, 3, WHITE)
                R(draw, x0 + sx - 1, sy + 1, 3, 1, WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def learn_book():
    f = learn_frame
    frames = intro(f)
    for k in range(3):
        frames.append(f(book=(k + 1) / 3, look=(2, 1)))
    for k in range(6):                                                       # reads, the xp bar fills a bit
        frames.append(f(book=1.0, xp=0.1 + k * 0.1, look=(2, 1 + (k % 4 > 1))))
    for k in range(6):                                                       # aha: a bulb
        frames.append(f(book=1.0, bulb=k + 1, xp=0.7, look=(2, 0), bob=-2 if k == 0 else 0, smile=k > 1))
    for k in range(4):
        frames.append(f(book=1.0, bulb=1 + k, xp=min(1.0, 0.7 + 0.1 * (k + 1)), star=k + 1, spark=k, look=(2, 0), smile=True))
    frames += [f(book=1.0, bulb=1, xp=1.0, star=4, spark=k, look=(2, 0), smile=True, blink=k == 5) for k in range(6)]
    for k in range(3):
        frames.append(f(book=1.0 - (k + 1) / 3 if k < 2 else 0.0, xp=max(0.0, 1.0 - 0.4 * (k + 1))))
    return frames + [f(blink=True), f()]


def learn_quiz():
    f = learn_frame
    frames = intro(f)
    frames += [f(book=0.5), f(book=1.0)]
    for k in range(8):
        frames.append(f(book=1.0, xp=0.05 * (k + 1), look=(2, 1 + (k % 4 > 1))))
    for k in range(6):                                                       # tries it, gets it right
        frames.append(f(book=1.0, xp=0.4 + k * 0.1, bulb=1 if k > 3 else 0, look=(2, 1), bob=-1 if k == 5 else 0, smile=k > 4))
    frames += [f(book=1.0, bulb=1, xp=1.0, star=1 + k // 2, spark=k, smile=True, look=(2, 0)) for k in range(8)]
    for k in range(3):
        frames.append(f(book=0.5 if k < 2 else 0.0, xp=max(0.0, 1.0 - 0.4 * (k + 1))))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("ci-pipeline", ci_frame, [lambda: ci_run(None), lambda: ci_run(1)])
    finish("build", build_frame, [lambda: build_make(False), lambda: build_make(True)])
    finish("container", container_frame, [lambda: container_build(()), lambda: container_build((0, 1))])
    finish("docs-read", docs_frame, [docs_browse, docs_search])
    finish("tutorial", tutorial_frame, [lambda: tutorial_run(False), lambda: tutorial_run(True)])
    finish("learned", learn_frame, [learn_book, learn_quiz])
