"""More agents: agent-spawn (a portal), agent-report (a mini agent hands over a report), agent-merge (results join).

python more_agents.py  ->  ../mine/<set>/
"""
import math

from props import *

BOX = (36, 40, 52)
BLUE_A, GREEN_A = (150, 172, 232), (152, 204, 142)
FLOOR_Y = 50


def agent(draw, cx, floor, g, color, look=0, blink=False, smile=False, hop=0, clipy=None):
    """A small agent (grid g), feet on `floor`. look shifts the eyes."""
    ox, oy = cx - 4 * g, floor - 8 * g - hop
    R(draw, ox, oy, 8 * g, 2 * g, color)
    R(draw, ox - 2 * g, oy + 2 * g, 12 * g, 2 * g, color)
    R(draw, ox, oy + 4 * g, 8 * g, 2 * g, color)
    for lc in (0, 2, 5, 7):
        R(draw, ox + lc * g, oy + 6 * g, g, 2 * g, color)
    for ex in (1, 6):
        if blink:
            R(draw, ox + ex * g, oy + g + g // 2, g, 1, BLACK)
        else:
            R(draw, ox + ex * g + look, oy + g, g, g, BLACK)
    if smile and g > 1:
        R(draw, ox + 3 * g, oy + 2 * g + 1, 1, 1, BLACK)
        R(draw, ox + 3 * g + 1, oy + 2 * g + 2, 2, 1, BLACK)
        R(draw, ox + 5 * g - 1, oy + 2 * g + 1, 1, 1, BLACK)


def poof(draw, cx, cy, r, color=(225, 228, 238)):
    for k in range(8):
        a = k * math.pi / 4
        R(draw, round(cx + math.cos(a) * r) - 1, round(cy + math.sin(a) * r * 0.7) - 1, 3, 3, color)


# ---------------------------------------------------------------- spawn: a portal opens and an agent steps out
def portal(draw, cx, y, spin, power):
    """A flat ring of dots. power 0 dim .. 1 bright. spin rotates the dots."""
    n = 18
    for i in range(n):
        a = i * 2 * math.pi / n + spin * 0.25
        c = mix((60, 66, 90), (190, 150, 255), power * (0.4 + 0.6 * ((i + spin) % 3) / 2))
        R(draw, round(cx + math.cos(a) * 16) - 1, round(y + math.sin(a) * 4) - 1, 3, 2, c)
    if power > 0.4:
        R(draw, cx - 12, y - 1, 25, 3, mix((20, 24, 34), (120, 80, 200), power))


def spawn_frame(agents=(), spin=0, power=0.0, puff=None, look=(2, 1), blink=False, bob=0, slide=0, key=False, smile=False):
    """agents: list of (cx, rise 0..1, colour, hop, smile). rise < 1 means still coming out of the portal."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 4, FLOOR_Y + 1, 80, 1, (60, 66, 82))
    portal(draw, x0 + 44, 46, spin, power)
    layer, ld = new_frame()
    for cx, rise, color, hop, sm in agents:
        floor = FLOOR_Y + round((1 - rise) * 18)
        agent(ld, x0 + cx, floor, 2, color, hop=hop, smile=sm)
    img.alpha_composite(layer.crop((0, 0, W, 47 if any(a[1] < 1 for a in agents) else H)).convert("RGBA"), (0, 0))
    draw = ImageDraw.Draw(img)
    if puff:
        poof(draw, x0 + puff[0], puff[1], puff[2])
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if key:
        key_press(draw, bob)
    return img


def spawn_one():
    f = spawn_frame
    frames = intro(f)
    for k in range(4):                                                       # the portal opens
        frames.append(f(spin=k, power=(k + 1) / 4, look=(2, 1), key=k == 3, bob=1 if k == 3 else 0))
    for k in range(6):                                                       # an agent steps up out of it
        frames.append(f(((44, ease((k + 1) / 6), CORAL, 0, False),), spin=k + 4, power=1.0, look=(2, 1)))
    frames += [f(((44, 1.0, CORAL, 0, False),), spin=10, power=1.0, puff=(44, 40, 7), look=(2, 0))]
    for k in range(6):                                                       # it hops and waves hello
        frames.append(f(((44, 1.0, CORAL, (0, 3, 4, 3, 0, 0)[k], True),), spin=11 + k, power=0.7, look=(2, 0), smile=True,
                        bob=-(0, 2, 3, 2, 0, 0)[k]))
    frames += [f(((44, 1.0, CORAL, 0, True),), spin=17 + k, power=0.5, look=(2, 1), blink=k == 3, smile=True) for k in range(5)]
    for k in range(6):                                                       # back into the portal
        frames.append(f(((44, 1.0 - ease((k + 1) / 6), CORAL, 0, False),), spin=22 + k, power=0.7 - 0.1 * k, look=(2, 1)))
    for k in range(3):
        frames.append(f(spin=28 + k, power=max(0.0, 0.3 - 0.1 * k)))
    return frames + [f(blink=True), f()]


def spawn_team():
    f = spawn_frame
    frames = intro(f)
    spots = ((18, CORAL), (44, BLUE_A), (70, GREEN_A))
    done = []
    for i, (sx, col) in enumerate((spots[1], spots[0], spots[2])):           # three agents come out one after another
        for k in range(4):
            frames.append(f(tuple(done) + ((44, ease((k + 1) / 4), col, 0, False),), spin=len(frames), power=1.0, look=(2, 1),
                            key=k == 0, bob=1 if k == 0 else 0))
        if sx != 44:                                                         # it steps aside
            for k in range(4):
                frames.append(f(tuple(done) + ((round(lerp(44, sx, ease((k + 1) / 4))), 1.0, col, (0, 2, 2, 0)[k], False),),
                                spin=len(frames), power=1.0, look=(2, 1)))
        done.append((sx, 1.0, col, 0, False))
    frames += [f(tuple(done), spin=k, power=0.8, look=(2, 0)) for k in range(2)]
    for k in range(8):                                                       # the whole team hops together
        hp = (0, 3, 4, 3, 0, 3, 4, 0)[k]
        frames.append(f(tuple((cx, 1.0, col, hp, True) for cx, _, col, _, _ in done), spin=k, power=0.6, look=(2, 0), smile=True,
                        bob=-(hp // 2)))
    for i, (cx, _, col, _, _) in enumerate(reversed(done)):                  # and they leave through the portal one by one
        keep = tuple((c, 1.0, cl, 0, False) for c, _, cl, _, _ in done[:len(done) - 1 - i])
        for k in range(3):
            frames.append(f(keep + ((cx, 1.0 - ease((k + 1) / 3), col, 0, False),), spin=k, power=0.6, look=(2, 1)))
    for k in range(3):
        frames.append(f(spin=k, power=max(0.0, 0.3 - 0.1 * k)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- report: a mini agent hands in its report
def report_card(draw, x, y, w, h, mark, lines=0, ok=True):
    R(draw, x, y, w, h, WHITE)
    col = GREEN if ok else AMBER
    R(draw, x, y, w, 5, col if mark else (170, 174, 190))
    if mark:
        if ok:
            tick(draw, x + 2, y, WHITE, 1)
        else:
            R(draw, x + 3, y + 1, 1, 2, DARK)
            R(draw, x + 3, y + 4, 1, 1, DARK)
    for i in range(lines):
        R(draw, x + 3, y + 8 + i * 4, w - 7 - (i % 2) * 5, 1, (150, 154, 168) if i % 2 == 0 else (120, 126, 146))


def report_frame(mini_x=None, walk=0, card=None, big=0, ok=True, hl=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0,
                 sweat_f=None, smile=False, mini_hop=0, mini_smile=False, mini_back=False):
    """mini_x = centre x of the mini agent (panel coords, can be off the right edge). card = (x, y) of the small report."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    R(draw, x0 + 4, FLOOR_Y + 1, 80, 1, (60, 66, 82))

    def paint(d):
        if mini_x is not None:
            agent(d, x0 + mini_x, FLOOR_Y, 2, BLUE_A, hop=(1 if walk % 2 else 0) + mini_hop, smile=mini_smile,
                  look=-1 if mini_back else 0)
        if card:
            report_card(d, x0 + card[0], card[1], 10, 13, True, 2, ok)
        if big:
            h = round(34 * min(1.0, big))
            report_card(d, x0 + 8, 46 - h, 30, h, big >= 1, 5 if big >= 1 else 0, ok)
            if big >= 1:
                for i in range(hl):
                    R(d, x0 + 11, 54 - 34 + 8 + i * 4 - 8, 20, 1, AMBER)
        if tickmark:
            tick(d, x0 + 46, 14, GREEN, 3)
    clipped(img, x0, paint)
    draw = ImageDraw.Draw(img)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    return img


def report_walk_in(f, ok=True, extra=None):
    frames = []
    for k in range(9):                                                       # the agent walks in with its report
        x = round(lerp(100, 62, (k + 1) / 9))
        frames.append(f(mini_x=x, walk=k, card=(x - 5, 28), ok=ok, look=(2, 1), mini_back=True))
    frames += [f(mini_x=62, card=(57, 28), ok=ok, look=(2, 1), mini_hop=1), f(mini_x=62, card=(57, 28), ok=ok, look=(2, 1))]
    for k in range(5):                                                       # the report goes across to Clawd and opens up
        t = ease((k + 1) / 5)
        frames.append(f(mini_x=62, card=(round(lerp(57, 20, t)), round(lerp(28, 24, t))), ok=ok, look=(2, 1)))
    for k in range(4):
        frames.append(f(mini_x=62, big=(k + 1) / 4, ok=ok, look=(2, 1)))
    return frames


def report_ok():
    f = report_frame
    frames = intro(f)
    frames += report_walk_in(f, True)
    for k in range(8):                                                       # Clawd reads it line by line
        frames.append(f(mini_x=62, big=1.0, ok=True, look=(2, 0 + k // 3), mini_smile=False, blink=k == 7))
    frames += [f(mini_x=62, big=1.0, ok=True, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0,
                 mini_hop=(0, 2, 3, 2, 0, 0, 0)[k], mini_smile=True) for k in range(7)]
    for k in range(4):                                                       # the report closes, the agent leaves
        frames.append(f(mini_x=62, big=max(0.0, 1.0 - (k + 1) / 4) if k < 3 else 0, ok=True, mini_smile=True))
    for k in range(9):
        x = round(lerp(62, 100, (k + 1) / 9))
        frames.append(f(mini_x=x, walk=k, look=(2, 1)))
    return frames + [f(blink=True), f()]


def report_retry():
    f = report_frame
    frames = intro(f)
    frames += report_walk_in(f, False)
    frames += [f(mini_x=62, big=1.0, ok=False, look=(2, 1 + k // 3), sweat_f=k, bob=k % 2) for k in range(6)]          # something is off
    for k in range(4):                                                       # sent back
        frames.append(f(mini_x=62, big=max(0.0, 1.0 - (k + 1) / 4) if k < 3 else 0, ok=False, look=(1, 1), sweat_f=k))
    for k in range(8):
        x = round(lerp(62, 100, (k + 1) / 8))
        frames.append(f(mini_x=x, walk=k, look=(2, 1)))
    frames += [f(look=(2, 2), bob=k % 2) for k in range(4)]
    frames += report_walk_in(f, True)                                        # it comes back with a good one
    frames += [f(mini_x=62, big=1.0, ok=True, tickmark=True, smile=True, look=(2, 0), bob=-1 if k == 0 else 0,
                 mini_hop=(0, 2, 3, 2, 0, 0)[k], mini_smile=True) for k in range(6)]
    for k in range(4):
        frames.append(f(mini_x=62, big=max(0.0, 1.0 - (k + 1) / 4) if k < 3 else 0, ok=True, mini_smile=True))
    for k in range(9):
        x = round(lerp(62, 100, (k + 1) / 9))
        frames.append(f(mini_x=x, walk=k, look=(2, 1)))
    return frames + [f(blink=True), f()]


# ---------------------------------------------------------------- merge results: three results join into one
LANES = ((22, LIGHT_BLUE), (36, PINK), (50, AMBER))
MERGE = (64, 32)


def merge_frame(blocks=(), big=0.0, conflict=0, ring=0, tickmark=False, look=(2, 1), blink=False, bob=0, slide=0, sweat_f=None,
                key=False, smile=False, hops=(0, 0, 0)):
    """blocks: list of (x, y, colour) result blocks in flight."""
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, DARK)
    for i, (fl, c) in enumerate(LANES):                                      # three small agents on the left
        agent(draw, x0 + 12, fl, 1, (CORAL, BLUE_A, GREEN_A)[i], hop=hops[i], look=0)
    for deg in range(0, 360, 20):                                            # the merge point
        a = math.radians(deg)
        R(draw, round(x0 + MERGE[0] + math.cos(a) * 9), round(MERGE[1] + math.sin(a) * 9), 1, 1, mix((70, 76, 92), WHITE, ring))
    for bx, by, c in blocks:
        R(draw, x0 + bx, by, 6, 6, c)
        R(draw, x0 + bx, by, 6, 1, mix(c, WHITE, 0.5))
    if big:
        s = round(14 * big)
        cx, cy = x0 + MERGE[0], MERGE[1]
        for i, (fl, c) in enumerate(LANES):
            R(draw, cx - s // 2, cy - s // 2 + i * s // 3, s, max(1, s // 3 + (1 if i == 2 else 0)), c)
    if conflict:
        cx, cy = x0 + MERGE[0], MERGE[1]
        for k in range(6):
            a = k * math.pi / 3 + conflict * 0.6
            R(draw, round(cx + math.cos(a) * (6 + conflict % 3)), round(cy + math.sin(a) * (6 + conflict % 3)), 2, 2, RED)
        cross(draw, cx - 3, cy - 3, RED, 1)
    if tickmark:
        tick(draw, x0 + 56, 10, GREEN, 3)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    if sweat_f is not None:
        sweat(draw, bob, sweat_f)
    if key:
        key_press(draw, bob)
    return img


def fly(i, t, stop=0.0):
    """Block of lane i at time t (0..1) between the agent and the merge point."""
    fl, c = LANES[i]
    sx, sy = 22, fl - 6
    ex, ey = MERGE[0] - 3 - stop * 4, MERGE[1] - 3 + (i - 1) * 3 * (1 - t) * 0
    return (round(lerp(sx, ex, t)), round(lerp(sy, ey, t)), c)


def merge_simple():
    f = merge_frame
    frames = intro(f)
    for k in range(3):
        frames.append(f(hops=(0, 0, 0), look=(2, 1)))
    for k in range(7):                                                       # the three blocks fly in together
        t = ease((k + 1) / 7)
        frames.append(f(blocks=[fly(i, t) for i in range(3)], ring=0.0, hops=(1 if k < 2 else 0,) * 3, look=(2, 1)))
    for k in range(3):                                                       # flash, and they become one
        frames.append(f(ring=1.0, big=0.5 + 0.25 * k, look=(2, 0), bob=-1 if k == 0 else 0))
    frames += [f(ring=0.6, big=1.0, tickmark=True, smile=True, look=(2, 0), blink=k == 5, bob=-1 if k == 0 else 0) for k in range(7)]
    for k in range(3):
        frames.append(f(big=max(0.0, 1.0 - 0.4 * (k + 1)), ring=0.3))
    return frames + [f(blink=True), f()]


def merge_conflict():
    f = merge_frame
    frames = intro(f)
    for k in range(7):                                                       # two blocks collide on the way
        t = ease((k + 1) / 7)
        frames.append(f(blocks=[fly(0, t), fly(1, t), fly(2, min(1.0, t * 0.6))], look=(2, 1), hops=(1, 1, 0) if k < 2 else (0, 0, 0)))
    for k in range(6):                                                       # a conflict spark
        frames.append(f(blocks=[fly(0, 1.0), fly(1, 1.0), fly(2, 0.6)], conflict=k + 1, ring=0.5, sweat_f=k, look=(1, 1), bob=k % 2))
    for k in range(6):                                                       # Clawd sorts it out
        frames.append(f(blocks=[fly(0, 1.0), fly(1, 1.0), fly(2, 0.6)], conflict=max(0, 3 - k // 2), ring=0.5, key=k % 2 == 0,
                        bob=k % 2, look=(2, 2), sweat_f=k))
    for k in range(4):                                                       # the third block joins
        t = lerp(0.6, 1.0, ease((k + 1) / 4))
        frames.append(f(blocks=[fly(0, 1.0), fly(1, 1.0), fly(2, t)], ring=0.5, look=(2, 1)))
    for k in range(3):
        frames.append(f(ring=1.0, big=0.5 + 0.25 * k, look=(2, 0), bob=-1 if k == 0 else 0))
    frames += [f(ring=0.6, big=1.0, tickmark=True, smile=True, look=(2, 0), blink=k == 5) for k in range(6)]
    for k in range(3):
        frames.append(f(big=max(0.0, 1.0 - 0.4 * (k + 1)), ring=0.3))
    return frames + [f(blink=True), f()]


if __name__ == "__main__":
    finish("agent-spawn", spawn_frame, [spawn_one, spawn_team])
    finish("agent-report", report_frame, [report_ok, report_retry])
    finish("agent-merge", merge_frame, [merge_simple, merge_conflict])
