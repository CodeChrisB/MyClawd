"""Four small misc sets: celebrate, night-owl, new-mail, hello.

python fun_sets.py  ->  ../mine/{celebrate,night-owl,new-mail,hello}/
Seam pose = the panel at rest (a party popper, a night sky, an empty inbox, a plain panel), see clawd.md.
"""
import math
import random

from props import *
from dev_sets import base, hold, puff, smile

GLYPHS["I"] = ["###", ".#.", ".#.", ".#.", "###"]
NIGHT = (14, 18, 40)
CONFETTI = [RED, YELLOW, GREEN, LIGHT_BLUE, PINK, PURPLE, ORANGE]


def arm(draw, level, bob=0):
    """Right arm half raised (1) or straight up (2)."""
    ox, oy = OX, OY + bob
    if not level:
        return
    draw.rectangle([ox + 8 * G, oy + 2 * G, ox + 10 * G - 1, oy + 4 * G - 1], fill=TRANS)
    if level == 1:
        draw.rectangle([ox + 8 * G, oy + G + 3, ox + 9 * G + 2, oy + 3 * G - 1], fill=CORAL)
        draw.rectangle([ox + 9 * G - 1, oy + 4, ox + 10 * G - 2, oy + 2 * G - 1], fill=CORAL)
    else:
        draw.rectangle([ox + 8 * G, oy - 3, ox + 9 * G - 1, oy + 3 * G - 1], fill=CORAL)


def me(draw, look=(2, 1), blink=False, bob=0, lid=0.0, grin=False, arm_level=0):
    clawd(draw, look=look, blink=blink, bob=bob, lid=lid)
    arm(draw, arm_level, bob)
    if grin:
        smile(draw, bob)


# ---------------------------------------------------------------- celebrate: popper, balloons, fireworks

POP = (30, 36)   # mouth of the popper, relative to the panel corner


def popper(draw, x0, flash=False):
    draw.polygon([(x0 + 6, 56), (x0 + 24, 56), (x0 + 19, POP[1]), (x0 + 11, POP[1])], fill=(230, 110, 150))
    for k in range(3):
        R(draw, x0 + 9 + k * 0, 44 + k * 4, 12 - k * 0, 1, YELLOW)
    R(draw, x0 + 11, POP[1] - 1, 8, 2, (60, 30, 40))
    if flash:
        R(draw, x0 + 12, POP[1] - 5, 6, 5, WHITE)
        R(draw, x0 + 14, POP[1] - 8, 2, 3, YELLOW)


def party_frame(k=None, balloons=(), shots=(), flash=False, look=(2, 1), blink=False, bob=0, grin=False, arm_level=0, slide=0):
    img, draw, x0 = base(slide)
    layer, ld = new_frame()
    popper(ld, x0, flash)
    if k is not None:  # confetti burst, k frames after the bang
        rng = random.Random(7)
        for i in range(22):
            vx, vy = rng.uniform(1.0, 4.4), rng.uniform(-5.6, -1.6)
            x, y = x0 + POP[0] - 12 + vx * k, POP[1] - 4 + vy * k + 0.35 * k * k
            R(ld, round(x), round(y), 2, 2, CONFETTI[i % len(CONFETTI)])
    for bx, t, c in balloons:  # balloons rise, t = frames since launch
        y = 66 - round(t * 2.2)
        x = x0 + bx + round(2 * math.sin(t / 3))
        dot(ld, x, y, 5, c)
        R(ld, x - 2, y - 3, 1, 2, WHITE)
        R(ld, x, y + 5, 1, 12, (190, 196, 210))
    for sx, sy, age, c in shots:  # fireworks, age 0..: rocket first, then a burst
        if age < 3:
            R(ld, x0 + sx, sy + 10 - age * 3 + 20 - 20, 1, 3, YELLOW)
        else:
            r = 2 + (age - 3) * 2
            for a in range(0, 360, 45):
                px, py = x0 + sx + round(math.cos(math.radians(a)) * r), sy + round(math.sin(math.radians(a)) * r)
                R(ld, px, py, 2, 2, c if age < 8 else mix(c, NIGHT, .5))
    img.alpha_composite(layer.crop((x0, PY0, x0 + 89, PY1 + 1)), (x0, PY0))
    me(draw, look, blink, bob, grin=grin, arm_level=arm_level)
    return img


def party_pop():
    f = party_frame
    frames = hold(f, 3)
    frames += [f(look=(2, 2), bob=1), f(look=(2, 2)), f(look=(2, 2), bob=1)]
    frames += [f(k=0, flash=True, look=(2, 1), bob=-2, grin=True, arm_level=2)]
    for k in range(1, 15):
        frames.append(f(k=k, look=(2, min(2, k // 4)), bob=-3 if k == 1 else (-1 if k < 4 else 0), grin=True, arm_level=2 if k < 8 else 0))
    frames += [f(blink=True)] + hold(f, 1)
    return frames


def party_balloons():
    f = party_frame
    frames = hold(f, 3)
    cols = (RED, YELLOW, LIGHT_BLUE)
    for t in range(40):
        balls = [(34 + i * 18, t - i * 8, cols[i]) for i in range(3) if t - i * 8 >= 0 and t - i * 8 < 36]
        frames.append(f(balloons=balls, look=(2, 0 if t % 16 < 8 else 1), grin=t > 4, bob=-1 if t in (3, 4) else 0))
    return frames + [f(blink=True)] + hold(f, 1)


def party_fireworks():
    f = party_frame
    frames = hold(f, 3)
    plan = [(0, 40, 22, PINK), (8, 62, 18, YELLOW), (16, 52, 32, LIGHT_BLUE)]
    for t in range(40):
        shots = [(x, y, t - s, c) for s, x, y, c in plan if 0 <= t - s < 14]
        frames.append(f(shots=shots, look=(2, -1), grin=t > 5, bob=-1 if t in (4, 12, 20) else 0))
    return frames + [f(blink=True)] + hold(f, 1)


# ---------------------------------------------------------------- night-owl


STARS = [(10, 12), (24, 26), (44, 10), (58, 30), (76, 22), (36, 44)]


def night_frame(twinkle=(), shoot=None, clock=None, cup=0, yawn=0, lid=0.45, look=(2, 1), blink=False, bob=0, slide=0, f=0):
    img, draw = new_frame()
    x0, _ = draw_panel(draw, slide, NIGHT)
    for i, (sx, sy) in enumerate(STARS):
        R(draw, x0 + sx, sy, 1, 1, WHITE)
        if i in twinkle:
            R(draw, x0 + sx - 1, sy, 3, 1, WHITE)
            R(draw, x0 + sx, sy - 1, 1, 3, WHITE)
    dot(draw, x0 + 68, 16, 7, (240, 232, 190))
    dot(draw, x0 + 71, 14, 6, NIGHT)
    if shoot is not None:
        for k in range(6):
            R(draw, x0 + 4 + shoot * 4 - k * 2, 8 + shoot * 2 - k, 2 - (k > 2), 1, mix(WHITE, NIGHT, k / 6))
    if clock is not None:
        r, mins = clock
        cx, cy = x0 + 36, 36
        dot(draw, cx, cy, r, (200, 204, 216))
        dot(draw, cx, cy, r - 2, (30, 34, 56))
        if r >= 10:
            for s in range(1, 8):
                a = math.radians(mins * 6)
                R(draw, cx + round(math.sin(a) * s), cy - round(math.cos(a) * s), 1, 1, WHITE)
            for s in range(1, 5):
                a = math.radians(mins / 12 * 6 * 2 + 300)
                R(draw, cx + round(math.sin(a) * s), cy - round(math.cos(a) * s), 1, 1, YELLOW)
    clawd(draw, look=look, blink=blink, bob=bob, lid=lid)
    if yawn:
        draw.rectangle([OX + 4 * G - 3, OY + 2 * G - 1 + bob, OX + 4 * G + 2, OY + 2 * G + 3 + bob], fill=BLACK)
    if cup:
        arm(draw, 1, bob)
        mx, my = OX + 10 * G - 1, OY + 1 + bob
        R(draw, mx, my, 6, 7, WHITE)
        R(draw, mx + 6, my + 1, 2, 4, WHITE)
        R(draw, mx + 1, my + 1, 4, 1, (110, 70, 40))
        for k in range(2):
            R(draw, mx + 1 + k * 3 + ((f // 2 + k) % 2), my - 2 - ((f + k * 3) % 5), 1, 1, COMMENT)
    return img


# a night-owl frame at rest has lid 0.45 and looks at the sky, that is the seam
def night_frame_seam(**kw):
    return night_frame(**kw)


def night_stars():
    f = night_frame
    frames = hold(f, 3)
    for t in range(32):
        tw = {(t // 3) % 6, (t // 3 + 3) % 6} if t % 3 else set()
        frames.append(f(twinkle=tw, shoot=t - 14 if 14 <= t < 24 else None, look=(2, 0 if t < 14 else 0 if t < 24 else 1),
                        blink=t == 28, bob=0))
    return frames + hold(f, 1)


def night_clock():
    f = night_frame
    frames = hold(f, 3)
    for i, r in enumerate((3, 7, 11)):
        frames.append(f(clock=(r, 0), look=(2, 1)))
    for i in range(14):
        frames.append(f(clock=(11, i * 14), lid=0.45 + 0.04 * i, look=(2, 1)))
    frames += [f(clock=(11, 196 + i * 4), lid=0.85, yawn=1, bob=-1 if i == 0 else 0) for i in range(4)]
    frames += [f(clock=(11, 212), lid=0.6, cup=1, f=i, bob=0) for i in range(8)]
    frames += [f(clock=(11, 212), lid=0.2, cup=1, f=i) for i in range(4)]
    for r in (7, 3):
        frames.append(f(clock=(r, 212), lid=0.45))
    return frames + hold(f, 2)


# ---------------------------------------------------------------- new-mail: envelope into the inbox, open it, toss spam


def envelope(draw, x, y, color=WHITE, bang=False, open_=0.0):
    R(draw, x, y, 14, 10, color)
    ink = (120, 126, 150)
    for k in range(6):
        R(draw, x + 1 + k, y + 1 + k // 2 * 1, 1, 1, ink)
        R(draw, x + 12 - k, y + 1 + k // 2 * 1, 1, 1, ink)
    if bang:
        R(draw, x + 6, y + 2, 2, 5, RED)
        R(draw, x + 6, y + 8, 2, 1, RED)


def mail_frame(env=None, bell=0, count=0, letter=None, bin_x=None, bin_lid=0, junk=None, look=(2, 1), blink=False, bob=0, slide=0, grin=False):
    img, draw, x0 = base(slide)
    layer, ld = new_frame()
    if env is not None:
        envelope(ld, x0 + env[0], env[1], env[2] if len(env) > 2 else WHITE)
    if letter is not None:
        R(ld, x0 + 26, letter, 26, 20, WHITE)
        for k in range(4):
            R(ld, x0 + 29, letter + 3 + k * 4, 20 - k * 2, 1, COMMENT)
    if junk is not None:
        envelope(ld, x0 + junk[0], junk[1], (200, 130, 130), bang=True)
    R(ld, x0 + 22, 40, 44, 14, (96, 100, 116))            # inbox tray, the front wall hides what drops in
    R(ld, x0 + 22, 40, 44, 2, (150, 154, 168))
    R(ld, x0 + 22, 52, 44, 2, (70, 74, 90))
    bx = x0 + 70 + round(2 * math.sin(bell * 2)) if bell else x0 + 70
    col = YELLOW if bell else (60, 64, 78)
    R(ld, bx, 8, 8, 7, col)
    R(ld, bx + 1, 6, 6, 2, col)
    R(ld, bx + 3, 15, 2, 2, col)
    if bell and bell % 2:
        R(ld, bx - 3, 7, 1, 4, YELLOW)
        R(ld, bx + 10, 7, 1, 4, YELLOW)
    if count:
        R(ld, bx + 6, 5, 7, 7, RED)
        text(ld, bx + 8, 6, str(count), WHITE, 1)
    if bin_x is not None:
        R(ld, x0 + bin_x, 36, 14, 18, (120, 126, 142))
        R(ld, x0 + bin_x - 1, 34 - bin_lid, 16, 2, (150, 154, 168))
        for k in range(3):
            R(ld, x0 + bin_x + 3 + k * 4, 39, 1, 12, (80, 84, 100))
    img.alpha_composite(layer.crop((x0, PY0, x0 + 89, PY1 + 1)), (x0, PY0))
    d = ImageDraw.Draw(img)
    clawd(d, look=look, blink=blink, bob=bob)
    if grin:
        smile(d, bob)
    return img


def mail_ding():
    f = mail_frame
    frames = hold(f, 3)
    for i in range(6):
        y = round(-12 + (46 - -12) * ease((i + 1) / 6)) if i < 5 else 46
        frames.append(f(env=(37, y), look=(2, 0 if i < 3 else 1)))
    for i in range(8):
        frames.append(f(env=(37, 46), bell=i + 1, count=1, look=(2, 0), grin=i > 1, bob=-1 if i == 0 else 0))
    frames += hold(f, 2, bell=0, count=1, look=(2, 1), grin=True)
    return frames + [f(blink=True)] + hold(f, 1)


def mail_open():
    f = mail_frame
    frames = hold(f, 3)
    for i in range(5):
        frames.append(f(env=(37, 46 - round(i * 5)), look=(2, 1)))
    for i in range(6):
        frames.append(f(env=(37, 22), letter=30 - round(10 * ease((i + 1) / 6)) if i >= 0 else None, look=(2, 1 + i // 3)))
    for i in range(8):
        frames.append(f(env=(37, 22), letter=18, look=(2, 0 if i < 4 else 1) if i % 2 else (2, 2), grin=i > 5))
    for i in range(5):
        frames.append(f(env=(37, 22), letter=18 + round(8 * ease((i + 1) / 5)) if i < 4 else None, look=(2, 1)))
    for i in range(5):
        frames.append(f(env=(37, 22 + round(i * 6)) if i < 4 else None, look=(2, 1)))
    return frames + [f(blink=True)] + hold(f, 1)


def mail_spam():
    f = mail_frame
    frames = hold(f, 3)
    for i in range(6):
        frames.append(f(junk=(37, round(-12 + 58 * ease((i + 1) / 6))), look=(2, 1)))
    frames += hold(f, 3, junk=(37, 46), look=(2, 2), bob=0)
    for i in range(6):  # the bin slides in from the right
        frames.append(f(junk=(37, 46), bin_x=round(92 - 28 * ease((i + 1) / 6)), look=(2, 2)))
    for i in range(7):  # flicked into the bin in an arc
        t = (i + 1) / 7
        frames.append(f(junk=(round(37 + 28 * t), round(46 - 22 * math.sin(math.pi * t) + 4 * t)), bin_x=64, bin_lid=4 if i > 3 else 0, look=(2, 0), bob=1 if i == 0 else 0))
    frames += hold(f, 3, bin_x=64, bin_lid=0, look=(2, 1), grin=True)
    for i in range(6):
        frames.append(f(bin_x=round(64 + 28 * ease((i + 1) / 6)) if i < 5 else None, look=(2, 1)))
    return frames + [f(blink=True)] + hold(f, 1)


# ---------------------------------------------------------------- hello


def hello_frame(bubble=0.0, word="HI", heart=False, arm_level=0, look=(2, 1), blink=False, bob=0, grin=False, slide=0, lean=0):
    img, draw, x0 = base(slide)
    if bubble:
        w, h = round(46 * bubble), round(26 * bubble)
        cx, cy = x0 + 44, 32
        R(draw, cx - w // 2, cy - h // 2, w, h, WHITE)
        R(draw, cx - w // 2 - 4, cy + 2, 4, 3, WHITE)
        R(draw, cx - w // 2 - 2, cy + 5, 2, 2, WHITE)
        if bubble >= 1:
            if heart:
                for r_, row_ in enumerate((".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X...")):
                    for c_, ch in enumerate(row_):
                        if ch == "X":
                            R(draw, cx - 7 + c_ * 2, cy - 6 + r_ * 2, 2, 2, RED)
            else:
                text(draw, cx - 10, cy - 5, word, CORAL, 3)
    clawd(draw, look=look, blink=blink, bob=bob + lean)
    arm(draw, arm_level, bob + lean)
    if grin:
        smile(draw, bob + lean)
    return img


def hello_wave():
    f = hello_frame
    frames = hold(f, 3)
    for i in range(3):
        frames.append(f(bubble=(i + 1) / 3, arm_level=1, look=(2, 0), bob=-1 if i == 1 else 0))
    for i in range(14):
        frames.append(f(bubble=1.0, arm_level=2 if (i // 2) % 2 == 0 else 1, grin=True, look=(2, 0), bob=0))
    for i in range(3):
        frames.append(f(bubble=1 - (i + 1) / 3 if i < 2 else 0, arm_level=1, grin=True))
    return frames + [f(blink=True)] + hold(f, 1)


def hello_bow():
    f = hello_frame
    frames = hold(f, 3)
    for i in range(3):
        frames.append(f(bubble=(i + 1) / 3, look=(2, 1)))
    for sink in (1, 2, 3, 3, 3, 3, 2, 1):
        frames.append(f(bubble=1.0, heart=True, lean=sink, look=(2, 2), grin=sink >= 2))
    frames += hold(f, 3, bubble=1.0, heart=True, grin=True, arm_level=1)
    for i in range(3):
        frames.append(f(bubble=1 - (i + 1) / 3 if i < 2 else 0, grin=True))
    return frames + [f(blink=True)] + hold(f, 1)


if __name__ == "__main__":
    finish("celebrate", party_frame, [party_pop, party_balloons, party_fireworks])
    finish("night-owl", night_frame, [night_stars, night_clock])
    finish("new-mail", mail_frame, [mail_ding, mail_open, mail_spam])
    finish("hello", hello_frame, [hello_wave, hello_bow])
