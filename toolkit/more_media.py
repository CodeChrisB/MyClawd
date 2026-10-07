"""More multimodal: video (watch, pick key frames, transcript) and multitasking (a terminal, an editor and a browser at once).

python more_media.py  ->  ../mine/{video,multitasking}/
"""
import math

from props import *

BOX = (36, 40, 52)
GREYT = (130, 136, 156)


# ---------------------------------------------------------------- video
def scene(draw, x, y, w, h, t):
    """A tiny road scene with a car that drives across as t goes 0..1."""
    R(draw, x, y, w, h, (110, 170, 230))
    dot(draw, x + w - 8, y + 5, 3, YELLOW)
    R(draw, x, y + h - 6, w, 6, (70, 150, 80))
    R(draw, x, y + h - 4, w, 2, (70, 76, 92))
    cx = x + 2 + round(t * (w - 14))
    R(draw, cx, y + h - 8, 10, 4, RED)
    R(draw, cx + 2, y + h - 10, 6, 2, RED)
    R(draw, cx + 3, y + h - 10, 2, 2, (200, 230, 255))
    R(draw, cx + 1, y + h - 5, 3, 3, BLACK)
    R(draw, cx + 6, y + h - 5, 3, 3, BLACK)


def video_frame(t=0.0, playing=False, picks=0, flash=False, caption=0, summary=0, tickmark=False, cursor_xy=None, look=(2, 1),
                blink=False, bob=0, slide=0, smile=False, scrub=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 5, 9, 52, 30, (70, 76, 92))
    scene(draw, x0 + 7, 11, 48, 18, t)
    if flash:
        for xx in range(x0 + 6, x0 + 56):
            R(draw, xx, 10, 1, 1, AMBER)
            R(draw, xx, 29, 1, 1, AMBER)
        R(draw, x0 + 6, 10, 1, 20, AMBER)
        R(draw, x0 + 55, 10, 1, 20, AMBER)
    if not playing:                                                          # big play button over the paused picture
        dot(draw, x0 + 31, 20, 6, (20, 24, 34))
        for r in range(5):
            R(draw, x0 + 29 + r, 17 + r, 1, 7 - 2 * r if r < 4 else 1, WHITE)
        R(draw, x0 + 29, 17, 1, 7, WHITE)
        for r in range(1, 4):
            R(draw, x0 + 29 + r, 17 + r, 1, max(1, 7 - 2 * r), WHITE)
    R(draw, x0 + 7, 32, 48, 6, (36, 40, 52))
    if playing:
        R(draw, x0 + 9, 33, 2, 4, WHITE)
        R(draw, x0 + 12, 33, 2, 4, WHITE)
    else:
        for r in range(3):
            R(draw, x0 + 9 + r, 33 + r, 1, 4 - 2 * r if r < 2 else 1, WHITE)
        R(draw, x0 + 9, 33, 1, 4, WHITE)
    R(draw, x0 + 17, 34, 36, 2, (70, 76, 92))
    R(draw, x0 + 17, 34, round(36 * t), 2, LIGHT_BLUE)
    dot(draw, x0 + 17 + round(36 * t), 35, 2, WHITE if not scrub else AMBER)
    for i in range(5):                                                       # picked key frames
        sx = x0 + 6 + i * 11
        R(draw, sx, 43, 10, 11, (50, 56, 74))
        if i < picks:
            R(draw, sx + 1, 44, 8, 9, (110, 170, 230))                       # a tiny snapshot of the scene at that moment
            R(draw, sx + 1, 50, 8, 3, (70, 150, 80))
            dot(draw, sx + 7, 46, 1, YELLOW)
            R(draw, sx + 1 + round((0.1, 0.3, 0.5, 0.7, 0.9)[i] * 5), 48, 3, 2, RED)
            R(draw, sx + 7, 52, 2, 1, GREEN)
    for i in range(summary):
        R(draw, x0 + 62, 12 + i * 7, (22, 18, 20)[i], 3, (225, 228, 235) if i == 0 else GREYT)
    for i in range(caption):                                                 # live captions
        R(draw, x0 + 62, 12 + i * 5, (20, 14, 22, 12, 18)[i % 5], 2, (200, 204, 215))
    if tickmark:
        tick(draw, x0 + 68, 40, GREEN, 3)
    if cursor_xy:
        cursor(draw, *cursor_xy)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def video_watch():
    f = video_frame
    frames = intro(f)
    frames += [f(look=(2, 1), bob=1), f(playing=True, look=(2, 1))]
    picks = 0
    for k in range(24):                                                      # plays, the car drives, key frames are picked
        t = (k + 1) / 24
        pick_now = k in (5, 12, 19)
        if pick_now:
            picks += 1
        frames.append(f(t * 0.9, True, picks, flash=pick_now, look=(2, 1 - (k % 10 > 6)), bob=1 if pick_now else 0))
    for n in range(1, 4):                                                    # then a summary appears
        frames += [f(0.9, False, picks, summary=n, look=(2, 1))] * 2
    frames += [f(0.9, False, picks, summary=3, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5)
               for k in range(6)]
    for k in range(4):                                                       # rewinds and clears
        frames.append(f(0.9 * (1 - (k + 1) / 4), False, max(0, picks - k - 1) if k < 3 else 0, summary=max(0, 3 - k - 1)))
    return frames + [f(blink=True), f()]


def video_scrub():
    f = video_frame
    frames = intro(f)
    start = (PX0 + 50, 52)
    for k in range(6):                                                       # drags the playhead along the timeline
        t = ease((k + 1) / 6) * 0.6
        frames.append(f(t, False, scrub=True, cursor_xy=(PX0 + 17 + round(36 * t), 36 + (6 - k)), look=(2, 1 + (k > 3))))
    picks = 0
    for k, jump in enumerate((0.6, 0.25, 0.8)):                              # jumps to moments and grabs a frame at each
        for j in range(3):
            frames.append(f(lerp(0.6 if k == 0 else (0.6, 0.25)[k - 1], jump, ease((j + 1) / 3)), False, picks, scrub=True,
                            cursor_xy=(PX0 + 17 + round(36 * jump), 36), look=(2, 0 + j % 2)))
        picks += 1
        frames += [f(jump, False, picks, flash=True, scrub=True, caption=picks * 2, look=(2, 0), bob=1)]
        frames += [f(jump, False, picks, scrub=True, caption=picks * 2, look=(2, 1))] * 2
    frames += [f(0.8, False, 3, caption=5, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0, blink=k == 5) for k in range(6)]
    for k in range(4):
        frames.append(f(0.8 * (1 - (k + 1) / 4), False, max(0, 2 - k), caption=max(0, 5 - 2 * (k + 1))))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- multitasking: three programs, switching between them
WINS = {"term": (3, 9, 34, 22), "edit": (40, 9, 45, 22), "web": (10, 34, 68, 21)}
CODE_ROWS = (((198, 120, 221), 14), ((152, 195, 121), 22), (LIGHT_BLUE, 16), ((229, 192, 123), 24))


def window(draw, x0, name, focus, dim, **st):
    wx, wy, ww, wh = WINS[name]
    x, y = x0 + wx, wy
    edge = CORAL if focus else (70, 76, 92)
    bg = {"term": (12, 14, 18), "edit": (30, 34, 48), "web": (236, 238, 244)}[name]
    bar = {"term": (50, 54, 66), "edit": (60, 76, 130), "web": (210, 212, 224)}[name]
    if dim:
        bg, bar = mix(bg, (14, 18, 26), 0.45), mix(bar, (14, 18, 26), 0.45)
    R(draw, x - 1, y - 1, ww + 2, wh + 2, edge)
    R(draw, x, y, ww, wh, bg)
    R(draw, x, y, ww, 4, bar)
    R(draw, x + 2, y + 1, 2, 2, {"term": GREEN, "edit": LIGHT_BLUE, "web": ORANGE}[name])
    if name == "term":
        lines = st.get("lines", 0)
        for i in range(lines):
            c = GREEN if i % 2 == 0 else (150, 156, 176)
            R(draw, x + 4, y + 7 + i * 4, 8 + (i * 5) % 14, 1, c)
        if st.get("cursor"):
            R(draw, x + 4 + 8 + (max(0, lines - 1) * 5) % 14 + 2, y + 6 + max(0, lines - 1) * 4, 2, 3, WHITE)
        if st.get("done"):
            tick(draw, x + 24, y + 12, GREEN, 1)
    elif name == "edit":
        marks = st.get("marks", 0)
        for i, (c, w) in enumerate(CODE_ROWS):
            c = mix(c, (14, 18, 26), 0.45) if dim else c
            R(draw, x + 4, y + 7 + i * 4, w, 2, c)
            if i < marks:
                R(draw, x + 4 + w + 2, y + 7 + i * 4, 8, 2, GREEN)
        if st.get("sel"):
            R(draw, x + 3, y + 10, 30, 4, (60, 80, 140))
            R(draw, x + 4, y + 11, CODE_ROWS[1][1], 2, CODE_ROWS[1][0])
    else:
        load = st.get("load", 0.0)
        hero = st.get("hero", 0)
        if load:
            R(draw, x, y + 4, round(ww * load), 1, ORANGE)
        R(draw, x + 4, y + 7, 24 + (hero % 2) * 8, 8, [(110, 170, 230), (240, 170, 90), (150, 200, 140)][hero % 3])
        R(draw, x + 32 + (hero % 2) * 8, y + 7, 24, 2, (150, 154, 170))
        R(draw, x + 32 + (hero % 2) * 8, y + 11, 18, 2, (170, 174, 190))
        R(draw, x + 4, y + 17, 50, 1, (190, 194, 206))


def multi_frame(focus=None, term=None, edit=None, web=None, packet=None, switcher=None, tickmark=False, look=(2, 1), blink=False,
                bob=0, slide=0, key=False, smile=False, sweat_f=None):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    for name, st in (("term", term or {}), ("edit", edit or {}), ("web", web or {})):
        window(draw, x0, name, focus == name, focus is not None and focus != name, **st)
    if packet:
        px, py, c = packet
        R(draw, x0 + px - 1, py - 1, 5, 5, WHITE)
        R(draw, x0 + px, py, 3, 3, c)
    if switcher is not None:                                                 # the alt-tab overlay
        R(draw, x0 + 22, 20, 44, 22, (150, 154, 168))
        R(draw, x0 + 23, 21, 42, 20, (22, 26, 38))
        for i, (c, nm) in enumerate(((GREEN, "term"), (LIGHT_BLUE, "edit"), ((236, 238, 244), "web"))):
            tx = x0 + 26 + i * 13
            R(draw, tx, 25, 10, 12, mix(c, DARK, 0.35) if switcher != i else c)
            if switcher == i:
                R(draw, tx - 1, 24, 12, 1, WHITE)
                R(draw, tx - 1, 37, 12, 1, WHITE)
                R(draw, tx - 1, 24, 1, 14, WHITE)
                R(draw, tx + 10, 24, 1, 14, WHITE)
    if tickmark:
        tick(draw, x0 + 76, 38, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


LOOK = {"term": (2, 0), "edit": (2, 0), "web": (2, 2)}
SW = {"term": 0, "edit": 1, "web": 2}


def alt_tab(f, a, b, state_a, state_b, hold=2):
    """Switcher overlay hops from app a to app b."""
    frames = [f(focus=a, switcher=SW[a], look=LOOK[a], **state_a)] * 2
    frames += [f(focus=a, switcher=SW[b], look=LOOK[b], **state_a)] * hold
    return frames


def multi_alt():
    f = multi_frame
    frames = intro(f)
    term = {}
    for k in range(6):                                                       # in the terminal: a command, its output
        term = {"lines": 1 + k // 2, "cursor": k % 2 == 0}
        frames.append(f("term", term=term, look=LOOK["term"], key=k % 2 == 0, bob=k % 2))
    term = {"lines": 3, "done": True}
    frames += [f("term", term=term, look=(2, 0))] * 2
    for k in (0, 1):                                                         # alt-tab to the editor
        frames.append(f("term", term=term, switcher=SW["term"] if k == 0 else SW["edit"], look=LOOK["edit"]))
    frames.append(f("term", term=term, switcher=SW["edit"], look=LOOK["edit"]))
    for m in range(1, 5):                                                    # edits four lines
        frames += [f("edit", term=term, edit={"marks": m, "sel": m == 1}, look=(2, 0), key=True, bob=1),
                   f("edit", term=term, edit={"marks": m}, look=(2, 0))]
    edit = {"marks": 4}
    for k in (0, 1):                                                         # alt-tab to the browser
        frames.append(f("edit", term=term, edit=edit, switcher=SW["edit"] if k == 0 else SW["web"], look=LOOK["web"]))
    frames.append(f("edit", term=term, edit=edit, switcher=SW["web"], look=LOOK["web"]))
    for k in range(8):                                                       # the page reloads with the change
        frames.append(f("web", term=term, edit=edit, web={"load": (k + 1) / 8, "hero": 1 if k > 4 else 0}, look=(2, 2)))
    frames += [f("web", term=term, edit=edit, web={"hero": 1}, tickmark=True, smile=True, look=(2, 1), bob=-1 if k == 0 else 0,
                 blink=k == 5) for k in range(6)]
    for k in range(3):                                                       # everything is put away
        frames.append(f(None, term={"lines": 3 - k} if k < 2 else None, edit={"marks": max(0, 4 - 2 * k)}, web={"hero": 1 if k < 2 else 0}))
    return frames + [f(blink=True), f()]


def multi_flow():
    f = multi_frame
    frames = intro(f)
    route = (("web", "edit", (36, 44), (50, 24), LIGHT_BLUE), ("edit", "term", (46, 24), (20, 20), AMBER),
             ("term", "web", (20, 26), (40, 44), GREEN))
    state = {"term": {}, "edit": {}, "web": {}}
    for i, (src, dst, p0, p1, col) in enumerate(route):                      # a snippet travels from window to window
        for k in range(3):
            frames.append(f(src, term=state["term"], edit=state["edit"], web=state["web"], look=LOOK[src], blink=False))
        for k in range(6):
            t = ease((k + 1) / 6)
            frames.append(f(src, term=state["term"], edit=state["edit"], web=state["web"],
                            packet=(round(lerp(p0[0], p1[0], t)), round(lerp(p0[1], p1[1], t)), col), look=LOOK[dst if k > 2 else src]))
        if dst == "edit":
            state["edit"] = {"marks": 1, "sel": True}
        elif dst == "term":
            state["term"] = {"lines": 2, "cursor": True}
        else:
            state["web"] = {"hero": 1}
        for k in range(4):
            if dst == "term":
                state["term"] = {"lines": 2 + k // 2, "done": k > 2}
            frames.append(f(dst, term=state["term"], edit=state["edit"], web=state["web"], look=LOOK[dst],
                            key=dst == "term" and k % 2 == 0, bob=k % 2 if dst == "term" else 0))
    frames += [f("web", term=state["term"], edit=state["edit"], web=state["web"], tickmark=True, smile=True, look=(2, 1),
                 bob=-1 if k == 0 else 0, blink=k == 5) for k in range(6)]
    for k in range(3):
        frames.append(f(None, term=state["term"] if k < 1 else None, edit=state["edit"] if k < 2 else None,
                        web={"hero": 1} if k < 2 else {}))
    return frames + [f(blink=True), f()]


def multi_parallel():
    f = multi_frame
    frames = intro(f)
    order = ("term", "edit", "web")
    for k in range(30):                                                      # all three work at once, Clawd's attention cycles
        who = order[(k // 5) % 3]
        term = {"lines": min(4, 1 + k // 5), "cursor": k % 4 < 2, "done": k > 24}
        edit = {"marks": min(4, k // 6)}
        web = {"load": min(1.0, (k + 1) / 24), "hero": 1 if k > 22 else 0}
        frames.append(f(who, term=term, edit=edit, web=web, look=LOOK[who], key=who != "web" and k % 2 == 0,
                        bob=1 if who != "web" and k % 2 == 0 else 0, sweat_f=k if 12 < k < 20 else None))
    term = {"lines": 4, "done": True}
    edit = {"marks": 4}
    web = {"hero": 1}
    frames += [f(None, term=term, edit=edit, web=web, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0,
                 blink=k == 6) for k in range(7)]
    for k in range(3):
        frames.append(f(None, term={"lines": 2 - k} if k < 2 else None, edit={"marks": max(0, 2 - k)}, web={"hero": 1} if k < 1 else {}))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("video", video_frame, [video_watch, video_scrub])
    finish("multitasking", multi_frame, [multi_alt, multi_flow, multi_parallel])
