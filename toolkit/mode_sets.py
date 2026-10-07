"""Mode sets: mode-plan (blueprint + route / checklist), mode-edit (accepted edits in a file), mode-auto (conveyor belt, auto approved).

python mode_sets.py  ->  ../mine/{mode-plan,mode-edit,mode-auto}/
"""
from props import *

BLUEPRINT, BP_LINE = (24, 52, 100), (44, 80, 140)


# ---------------------------------------------------------------- plan mode
ROUTE = [(12, 44), (30, 44), (30, 28), (58, 28), (58, 16), (76, 16)]       # waypoints on the blueprint
LIST_ROWS = [(9, 30), (9, 24), (9, 34), (9, 20)]


def route_points(upto):
    """Pixels of the dotted route up to length `upto` (0..1)."""
    pts, total = [], 0
    segs = []
    for (ax, ay), (bx, by) in zip(ROUTE, ROUTE[1:]):
        n = max(abs(bx - ax), abs(by - ay))
        segs.append((ax, ay, bx, by, n))
        total += n
    limit = upto * total
    done = 0
    for ax, ay, bx, by, n in segs:
        for i in range(n):
            if done + i > limit:
                return pts
            pts.append((round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n)))
        done += n
    return pts


def plan_frame(route=0.0, checks=0, clip=False, flag=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0, key=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, BLUEPRINT)
    for gx in range(0, 89, 8):                                               # blueprint grid
        R(draw, x0 + gx, 8, 1, 50, BP_LINE)
    for gy in range(8, 58, 8):
        R(draw, x0, gy, 89, 1, BP_LINE)
    ax, ay = ROUTE[0]
    dot(draw, x0 + ax, ay, 3, (170, 200, 240))                              # start marker
    if not clip:
        for i, (px, py) in enumerate(route_points(route)):
            if i % 4 < 2:
                R(draw, x0 + px, py, 2, 2, WHITE)
        for wx, wy in ROUTE[1:-1]:
            if route > 0 and any(abs(px - wx) < 2 and abs(py - wy) < 2 for px, py in route_points(route)):
                dot(draw, x0 + wx, wy, 2, AMBER)
        gx, gy = ROUTE[-1]
        R(draw, x0 + gx, gy - 8, 1, 12, (200, 210, 230))                    # goal flag pole
        if flag:
            R(draw, x0 + gx + 1, gy - 8, round(7 * flag), 4, RED)
    else:                                                                    # take B: a checklist
        R(draw, x0 + 22, 10, 44, 46, WHITE)
        R(draw, x0 + 36, 7, 16, 5, (150, 154, 168))
        for i in range(4):
            if i < checks:
                R(draw, x0 + 27, 18 + i * 9, 4, 4, GREEN)
                R(draw, x0 + 34, 19 + i * 9, LIST_ROWS[i][1], 2, (100, 106, 124))
            else:
                R(draw, x0 + 27, 18 + i * 9, 4, 4, (210, 214, 224))
    if tickmark:
        tick(draw, x0 + 62, 36, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def plan_route():
    f = plan_frame
    frames = intro(f)
    for k in range(20):                                                      # the route is drawn, Clawd's eyes follow it
        r = (k + 1) / 20
        look = (2, 2 if r < 0.3 else 1 if r < 0.6 else 0)
        frames.append(f(route=r, look=look, key=k % 3 == 0, bob=1 if k % 3 == 0 else 0))
    for k in range(5):
        frames.append(f(route=1.0, flag=(k + 1) / 5, look=(2, 0)))
    frames += [f(route=1.0, flag=1.0, tickmark=True, look=(2, 0), bob=-1 if k == 0 else 0) for k in range(7)]
    for k in range(5):                                                       # wiped again
        frames.append(f(route=1.0 - (k + 1) / 5, flag=max(0, 1 - (k + 1) / 2), look=(2, 1)))
    return frames + [f(blink=True), f()]


def plan_list():
    f = plan_frame
    frames = intro(f)
    for k in range(3):                                                       # the checklist sheet slides in
        frames.append(f(clip=True, look=(2, 1), bob=0))
    for n in range(1, 5):
        frames += [f(clip=True, checks=n, look=(2, 1 + n % 2), key=k == 0, bob=1 if k == 0 else 0) for k in range(4)]
    frames += [f(clip=True, checks=4, tickmark=False, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(7)]
    for n in (2, 0):
        frames.append(f(clip=True, checks=n))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- edit mode
CODE = [(0, 14, KEYWORD := (198, 120, 221)), (8, 26, (152, 195, 121)), (8, 18, LIGHT_BLUE), (8, 30, (229, 192, 123)),
        (0, 12, KEYWORD)]
ROW_Y = (16, 24, 32, 40, 48)


def edit_frame(state=(0, 0, 0), cursor=None, look=(2, 1), blink=False, bob=0, slide=0, key=False, tabmark=False):
    """state per edited row (rows 1, 2, 4): 0 untouched, 1 old text struck red, 2 new text green + tick."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, (24, 26, 38))
    R(draw, x0, 6, 89, 6, (40, 44, 54))                                      # tab bar with a pencil
    R(draw, x0 + 6, 8, 18, 3, (110, 116, 130))
    if tabmark:
        R(draw, x0 + 70, 8, 8, 3, GREEN)
    edited = {1: state[0], 2: state[1], 3: state[2]}
    for i, (ind, w, c) in enumerate(CODE):
        y = ROW_Y[i]
        R(draw, x0 + 3, y, 2, 3, (70, 76, 92))                               # gutter
        st = edited.get(i, 0)
        if st == 0:
            R(draw, x0 + 10 + ind, y, w, 3, c)
        elif st == 1:
            R(draw, x0 + 10 + ind, y, w, 3, (200, 80, 80))
            R(draw, x0 + 10 + ind, y + 1, w, 1, WHITE)
        else:
            R(draw, x0 + 10 + ind, y, w + 8, 3, GREEN)
            tick(draw, x0 + 78, y - 1, GREEN, 1)
    if cursor is not None:
        R(draw, x0 + 10 + cursor[0], ROW_Y[cursor[1]] - 1, 1, 5, WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def edit_accept():
    f = edit_frame
    frames = intro(f)
    state = [0, 0, 0]
    for row in range(3):                                                     # each edit: struck out, replaced, accepted
        r = row + 1
        frames += [f(tuple(state), cursor=(CODE[r][1], r), look=(2, min(2, r)), blink=k == 2) for k in range(3)]
        state[row] = 1
        frames += [f(tuple(state), look=(2, min(2, r)), key=k % 2 == 0, bob=k % 2) for k in range(4)]
        state[row] = 2
        frames += [f(tuple(state), look=(2, min(2, r)), bob=-1 if k == 0 else 0) for k in range(3)]
    frames += [f(tuple(state), look=(2, 0), tabmark=True, blink=k == 6) for k in range(8)]
    for k in range(3):                                                       # everything folds back to the original text
        n = 2 - k
        frames.append(f(tuple(2 if i < n else 0 for i in range(3)), look=(2, 1)))
    return frames + [f(blink=True), f()]


def edit_quick():
    f = edit_frame
    frames = intro(f)
    for pair in ((1, 2), (3,)):                                              # several edits at once, accepted together
        for r in pair:
            frames += [f(tuple(1 if i == r - 1 or (i + 1 in pair and i + 1 <= r) else 0 for i in range(3)),
                         cursor=(CODE[r][1], r), look=(2, r))]
    frames += [f((1, 1, 1), look=(2, 2), key=k % 2 == 0, bob=k % 2) for k in range(5)]
    for k in range(3):
        frames += [f(tuple(2 if i <= k else 1 for i in range(3)), look=(2, 1), bob=-1 if i == 0 else 0) for i in range(2)]
    frames += [f((2, 2, 2), tabmark=True, look=(2, 0), blink=k == 6) for k in range(8)]
    frames += [f((2, 2, 1)), f((2, 1, 0)), f((1, 0, 0)), f(blink=True)]
    return frames + [f()]


# ---------------------------------------------------------------- auto mode: everything runs through the gate on its own
BELT_Y = 44
ITEM_C = [LIGHT_BLUE, PINK, AMBER, GREEN, PURPLE]
GATE_X = 40


def auto_frame(f=0, items=(), pass_at=None, look=(2, 1), blink=False, bob=0, slide=0, lid=0.0, smile=False):
    """items: list of (x, colour). The belt moves 3 px per frame (period 12). pass_at = frames since an item crossed the gate."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    off = (f * 3) % 12
    R(draw, x0, BELT_Y + 4, 89, 2, (46, 50, 62))

    def paint(d):
        for x in range(-12 + off, 89, 12):                                   # belt stripes, clipped to the panel
            R(d, x0 + x, BELT_Y, 6, 4, (70, 76, 92))
        for x, c in items:
            R(d, x0 + x, BELT_Y - 9, 9, 9, c)
            R(d, x0 + x + 1, BELT_Y - 8, 3, 2, tuple(min(255, v + 60) for v in c))
        R(d, x0 + GATE_X, 18, 3, 27, GLASS_C)                                 # gate: two posts and a bar
        R(d, x0 + GATE_X + 18, 18, 3, 27, GLASS_C)
        R(d, x0 + GATE_X, 16, 21, 3, GLASS_C)
        if pass_at is not None:
            R(d, x0 + GATE_X + 3, 17, 15, 1, GREEN)
            tick(d, x0 + GATE_X + 7, 6, GREEN, 2)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob, lid=lid)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


GLASS_C = (150, 154, 168)


def auto_run(speed_items, gap):
    """A queue of items rolls through the gate. Everything is waved through, Clawd stays relaxed."""
    n = len(speed_items)
    total_travel = 100 + gap * (n - 1)
    frames_n = (total_travel // 3) + 1
    frames_n += (-frames_n) % 4                                              # belt phase must close
    out = []
    for fr in range(frames_n):
        items, passed = [], None
        for k in range(n):
            x = -10 + fr * 3 - k * gap
            if -10 <= x <= 90:
                items.append((x, speed_items[k]))
            if GATE_X <= x + 4 <= GATE_X + 18:
                passed = True
        out.append(auto_frame(fr, items, passed, look=(2, 1 if fr % 12 < 8 else 2), lid=0.3,
                              smile=fr > 6, blink=fr % 24 == 20, bob=1 if (fr % 24) in (10, 11) else 0))
    return out


def auto_loop_a():
    f = auto_frame
    return intro(f, 3) + auto_run(ITEM_C[:3], 26) + [f(blink=True), f()]


def auto_loop_b():
    f = auto_frame
    return intro(f, 3) + auto_run(ITEM_C[::-1], 20) + [f(blink=True), f()]


if __name__ == "__main__":
    finish("mode-plan", plan_frame, [plan_route, plan_list])
    finish("mode-edit", edit_frame, [edit_accept, edit_quick])
    finish("mode-auto", auto_frame, [auto_loop_a, auto_loop_b])
