"""Git sets: git-commit, git-push, git-pr. The commit chain scrolls one node to the left at the end, which equals the seam.

python git_sets.py  ->  ../mine/{git-commit,git-push,git-pr}/
"""
from props import *

NODE_X = (16, 36, 56)                    # commit nodes in the seam, 20 px apart
LINE_Y = 44
COMMIT = LIGHT_BLUE
PENDING = AMBER
PURPLE_PR = (150, 110, 220)


def chain(draw, x0, shift=0, new=None, colors=None, y=LINE_Y, line=True):
    """Commit chain on a horizontal line. shift scrolls it left. new = (colour, radius) adds a fourth node on the right."""
    if line:
        R(draw, x0 + 4, y, 80, 1, (70, 76, 92))
    xs = [x + shift * -1 for x in NODE_X]
    for i, x in enumerate(xs):
        c = colors[i] if colors else COMMIT
        dot(draw, x0 + x, y, 3, c)
    if new:
        dot(draw, x0 + 76 - shift, y, new[1], new[0])
    if shift:                                                                # the node scrolling out on the left
        dot(draw, x0 + 16 - shift, y, 3, COMMIT)


def git_frame(shift=0, new=None, colors=None, files=(), msg=0, stars=None, look=(2, 1), blink=False, bob=0, key=False, slide=0,
              tickmark=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        chain(d, x0, shift, new, colors)
        for fx, fy in files:                                                 # file icons flying to the new commit
            R(d, x0 + fx, fy, 6, 8, WHITE)
            R(d, x0 + fx + 1, fy + 2, 4, 1, (150, 154, 168))
            R(d, x0 + fx + 1, fy + 5, 3, 1, (150, 154, 168))
        if msg:
            R(d, x0 + 8, 20, msg, 3, (225, 228, 235))
        if tickmark:
            tick(d, x0 + 62, 24, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if key:
        key_press(draw, bob)
    return img


def scroll_out(f, color=GREEN, **kw):
    """The new node settles and the whole chain moves left by one node: ends on the seam."""
    out = []
    for k in range(6):
        t = ease((k + 1) / 6)
        out.append(f(shift=round(20 * t), new=(mix(color, COMMIT, t), 3), look=(2, 1), **kw))
    return out


def commit_files():
    f = git_frame
    frames = intro(f)
    for n in range(3):                                                       # three files fly into the next commit
        for k in range(5):
            t = (k + 1) / 5
            fx, fy = round(lerp(8 + n * 12, 74, t)), round(lerp(14, 40, t) + (-6 * math.sin(t * math.pi)))
            frames.append(f(files=[(fx, fy)], new=(PENDING, 1 + n) if n else None, look=(2, 0 + (k > 2)), bob=k % 2))
        frames += [f(new=(PENDING, 2 + n), bob=1, look=(2, 2))]
    frames += [f(new=(GREEN, 3), tickmark=True, look=(2, 0), bob=-1)] * 4
    return frames + scroll_out(f, GREEN) + [f(blink=True), f()]


def commit_msg():
    f = git_frame
    frames = intro(f)
    for k in range(14):                                                      # writes the commit message
        frames.append(f(msg=round(70 * (k + 1) / 14), key=k % 2 == 0, bob=k % 2, look=(2, 1 - (k % 6 > 2))))
    frames += [f(msg=70, look=(2, 1), blink=True)]
    for k, r in enumerate((1, 2, 3)):                                        # Enter: the node pops
        frames.append(f(msg=70, new=(PENDING, r), look=(2, 2)))
    frames += [f(msg=0, new=(GREEN, 3), tickmark=True, look=(2, 0), bob=-1 if k < 2 else 0) for k in range(5)]
    return frames + scroll_out(f, GREEN) + [f(blink=True), f()]


# ---------------------------------------------------------------- push: local nodes fly up to a cloud
def cloud_icon(draw, x, y, color):
    R(draw, x + 2, y + 6, 20, 6, color)
    R(draw, x + 5, y + 3, 8, 5, color)
    R(draw, x + 10, y, 9, 8, color)
    R(draw, x + 15, y + 3, 7, 6, color)


def push_frame(sent=0, flying=None, cloud=GREY, bars=0, prog=None, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0,
               sweat_f=None):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 4, LINE_Y, 80, 1, (70, 76, 92))
    for i, x in enumerate(NODE_X):
        dot(draw, x0 + x, LINE_Y, 3, GREEN if i < sent else PENDING)
    cloud_icon(draw, x0 + 56, 10, cloud)
    for i in range(bars):
        R(draw, x0 + 60 + i * 5, 14, 3, 3, WHITE)
    if flying:
        dot(draw, x0 + flying[0], flying[1], 2, WHITE)
    if prog is not None:
        R(draw, x0 + 6, 52, 76, 3, (36, 40, 52))
        R(draw, x0 + 6, 52, round(76 * prog), 3, LIGHT_BLUE)
    if tickmark:
        tick(draw, x0 + 62, 28, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def push_nodes():
    f = push_frame
    frames = intro(f)
    for n in range(3):
        sx = NODE_X[n]
        for k in range(6):
            t = (k + 1) / 6
            frames.append(f(sent=n, flying=(round(lerp(sx, 70, t)), round(lerp(LINE_Y, 22, t) - 6 * math.sin(t * math.pi))),
                            look=(2, 1 - (k > 2)), bob=1 if k == 0 else 0, cloud=GREY if k < 5 else WHITE))
        frames += [f(sent=n + 1, bars=n + 1, cloud=LIGHT_BLUE, look=(2, 0))] * 2
    frames += [f(sent=3, bars=3, cloud=GREEN, tickmark=True, look=(2, 0), bob=-1 if k < 2 else 0) for k in range(7)]
    frames += [f(sent=2, bars=2, cloud=LIGHT_BLUE), f(sent=1, bars=1, cloud=GREY), f(blink=True)]
    return frames + [f()]


def push_progress():
    f = push_frame
    frames = intro(f)
    for k in range(16):                                                      # one go: progress bar, nodes fill the cloud
        p = (k + 1) / 16
        frames.append(f(sent=int(p * 3), prog=p, bars=int(p * 3), cloud=LIGHT_BLUE, look=(2, 1 + (k % 6 > 2)),
                        flying=(round(lerp(20, 70, (k % 4) / 4)), round(lerp(40, 22, (k % 4) / 4))), sweat_f=None))
    frames += [f(sent=3, prog=1.0, bars=3, cloud=GREEN, tickmark=True, look=(2, 0), bob=-1 if k < 2 else 0) for k in range(7)]
    for k in (0.6, 0.3):
        frames.append(f(sent=1, prog=k, bars=1, cloud=GREY))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- pull request: a branch grows, gets reviewed, merges
def branch(draw, x0, grow, nodes, badge=None, bubbles=0, merge=None):
    """Feature branch leaving the main line at node 2 (x=36), going up-right. grow 0..1 draws the diagonal."""
    sx, sy, ex, ey = x0 + 36, LINE_Y, x0 + 72, 24
    for i in range(int(36 * grow) + 1):
        t = i / 36
        R(draw, round(sx + (ex - sx) * t), round(sy + (ey - sy) * t), 2, 2, (110, 116, 140))
    for k in range(nodes):
        t = (k + 1) / 3
        dot(draw, round(sx + (ex - sx) * t), round(sy + (ey - sy) * t), 3, LIGHT_BLUE if merge is None else PURPLE_PR)
    if badge:
        bx, by = x0 + 74, 16
        dot(draw, bx, by, 6, PURPLE_PR if badge == 1 else GREEN)
        if badge == 1:                                                       # merge icon: two dots and a line
            R(draw, bx - 3, by - 3, 2, 2, WHITE)
            R(draw, bx + 1, by + 1, 2, 2, WHITE)
            R(draw, bx - 3, by - 1, 1, 4, WHITE)
        else:
            tick(draw, bx - 3, by - 2, WHITE, 1)
    for k in range(bubbles):
        bx, by = x0 + 40 + k * 18, 8 + k * 2
        R(draw, bx, by, 16, 10, WHITE)
        R(draw, bx + 12, by + 10, 3, 3, WHITE)
        R(draw, bx + 2, by + 2, 11, 1, (110, 116, 130))
        R(draw, bx + 2, by + 5, 8, 1, (110, 116, 130))


def pr_frame(grow=0.0, nodes=0, badge=None, bubbles=0, merge=0.0, shift=0, new=None, look=(2, 1), blink=False, bob=0, slide=0,
             tickmark=False):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)

    def paint(d):
        chain(d, x0, shift, new)
        if grow and not merge:
            branch(d, x0, grow, nodes, badge, bubbles)
        elif merge:                                                          # nodes slide down the diagonal into main
            sx, sy, ex, ey = x0 + 36, LINE_Y, x0 + 72, 24
            for k in range(3):
                t = ((k + 1) / 3) * (1 - merge)
                dot(d, round(sx + (ex - sx) * t), round(sy + (ey - sy) * t), 3, PURPLE_PR)
            for i in range(int(36 * (1 - merge)) + 1):
                tt = i / 36
                R(d, round(sx + (ex - sx) * tt), round(sy + (ey - sy) * tt), 2, 2, (110, 116, 140))
        if tickmark:
            tick(d, x0 + 62, 30, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def merge_end(f):
    frames = []
    for k in range(5):                                                       # branch folds back into main, a merge node appears
        t = ease((k + 1) / 5)
        frames.append(f(grow=1.0, nodes=3, merge=t, new=(PURPLE_PR, round(3 * t)), look=(2, 1)))
    frames += [f(new=(GREEN, 3), tickmark=True, look=(2, 0), bob=-1 if k < 2 else 0) for k in range(5)]
    return frames + scroll_out(f, GREEN)


def pr_open():
    f = pr_frame
    frames = intro(f)
    for k in range(8):
        frames.append(f(grow=(k + 1) / 8, nodes=min(3, k // 2), look=(2, 1 - (k > 3)), bob=k % 2, ))
    frames += [f(grow=1.0, nodes=3, badge=1, look=(2, 0), bob=-1 if k == 0 else 0) for k in range(8)]
    return frames + merge_end(f) + [f(blink=True), f()]


def pr_review():
    f = pr_frame
    frames = intro(f)
    for k in range(6):
        frames.append(f(grow=(k + 1) / 6, nodes=min(3, k // 2), look=(2, 1)))
    frames += [f(grow=1.0, nodes=3, badge=1, look=(2, 0))] * 3
    for b in (1, 2):                                                         # review comments pop up
        frames += [f(grow=1.0, nodes=3, badge=1, bubbles=b, look=(2, 0 if b == 1 else 1), blink=b == 2 and k == 2)
                   for k in range(3)]
    frames += [f(grow=1.0, nodes=3, badge=2, bubbles=0, look=(2, 0), bob=-1 if k == 0 else 0) for k in range(5)]
    return frames + merge_end(f) + [f(blink=True), f()]


if __name__ == "__main__":
    finish("git-commit", git_frame, [commit_files, commit_msg])
    finish("git-push", push_frame, [push_nodes, push_progress])
    finish("git-pr", pr_frame, [pr_open, pr_review])
