"""celebrate: two Clawds with party hats and a cake in the middle. No panel, the whole canvas is the scene.

python party_sets.py  ->  ../mine/celebrate/
Seam pose = both standing, hats on, three candles lit. Loop 1 blows the candles out, confetti, the candles relight themselves
(trick candles). Loop 2 is a little dance with music notes.
"""
import random

from props import *

GROUND = 56
CAKE_X = 94
FX, FY, FG = 118, GROUND - 40, 5      # the friend: head left, head top, grid size
HAT_A, HAT_B = YELLOW, LIGHT_BLUE
CONFETTI = [RED, YELLOW, GREEN, LIGHT_BLUE, PINK, PURPLE, ORANGE]
SMOKE = (190, 196, 210)


def arms_up(draw, ox, oy, g, left=True, right=True, flap=0):
    for on, x0 in ((left, ox - 2 * g), (right, ox + 8 * g)):
        if on:
            draw.rectangle([x0, oy + 2 * g, x0 + 2 * g - 1, oy + 4 * g - 1], fill=TRANS)
            draw.rectangle([x0, oy + g - 4 * flap, x0 + 2 * g - 1, oy + 3 * g - 1 - 4 * flap], fill=CORAL)


def friend(draw, bob=0, look=(-2, 1), blink=False, walk=None, dx=0):
    x, y, g = FX + dx, FY + bob, FG
    for bx, by, w, h in ((0, 0, 8, 2), (-2, 2, 12, 2), (0, 4, 8, 2)):
        draw.rectangle([x + bx * g, y + by * g, x + (bx + w) * g - 1, y + (by + h) * g - 1], fill=CORAL)
    for col in (0, 2, 5, 7):
        lifted = walk is not None and (col in (0, 5)) == (walk == 0)
        draw.rectangle([x + col * g, y + 6 * g, x + (col + 1) * g - 1, y + (7 if lifted else 8) * g - 1], fill=CORAL)
    for ex in (x + g, x + 6 * g):
        if blink:
            draw.rectangle([ex, y + g + 2, ex + g - 1, y + g + 3], fill=BLACK)
        else:
            lx = max(0, min(2, look[0] + 1)) - 1
            draw.rectangle([ex + lx, y + g + look[1], ex + lx + g - 2, y + 2 * g - 2 + look[1]], fill=BLACK)


def smile5(draw, bob=0, dx=0):
    mx, my = FX + dx + 4 * FG, FY + bob + 2 * FG + 1
    draw.rectangle([mx - 4, my, mx - 3, my + 1], fill=BLACK)
    draw.rectangle([mx - 2, my + 2, mx + 1, my + 3], fill=BLACK)
    draw.rectangle([mx + 2, my, mx + 3, my + 1], fill=BLACK)


def hat(draw, x, y, w, h, color):
    draw.polygon([(x, y), (x + w, y), (x + w // 2, y - h)], fill=color)
    R(draw, x + w // 2 - 1, y - h - 1, 3, 3, RED)
    R(draw, x + 2, y - 2, max(1, w - 4), 1, WHITE)


def cake(draw, dy=0, flames=(1, 1, 1), f=0, sparkle=False):
    R(draw, CAKE_X - 12, 46 + dy, 24, 2, (150, 104, 66))
    R(draw, CAKE_X - 2, 48 + dy, 4, GROUND - 48, (150, 104, 66))
    R(draw, CAKE_X - 10, 38 + dy, 20, 8, (235, 150, 170))
    R(draw, CAKE_X - 10, 38 + dy, 20, 2, WHITE)
    R(draw, CAKE_X - 6, 31 + dy, 12, 7, (250, 200, 210))
    R(draw, CAKE_X - 6, 31 + dy, 12, 2, WHITE)
    for i, c in enumerate((LIGHT_BLUE, YELLOW, GREEN)):
        x = CAKE_X - 4 + i * 4
        R(draw, x, 26 + dy, 2, 5, c)
        if flames[i]:
            R(draw, x, 23 + dy - (f + i) % 2, 2, 3, ORANGE)
            R(draw, x, 24 + dy - (f + i) % 2, 2, 1, YELLOW)
        elif flames[i] is None:
            R(draw, x, 21 + dy - (f * 2 + i) % 4, 1, 2, SMOKE)
    if sparkle:
        R(draw, CAKE_X - 1, 18 + dy, 3, 1, WHITE)
        R(draw, CAKE_X, 17 + dy, 1, 3, WHITE)


def note(draw, x, y, color):
    R(draw, x, y + 4, 3, 2, color)
    R(draw, x + 2, y, 1, 5, color)
    R(draw, x + 2, y, 3, 1, color)


def party_frame(f=0, bob=0, fbob=0, look=(2, 1), flook=(-2, 1), blink=False, fblink=False, flames=(1, 1, 1), cake_dy=0, hats=True,
                a_main=(False, False), a_friend=(False, False), flap=0, grin=True, confetti=None, puffs=(), notes=(), friend_dx=0, walk=None,
                sparkle=False, slide=0):
    img, draw = new_frame()
    if cake_dy is not None:
        cake(draw, cake_dy, flames, f, sparkle)
    if confetti is not None:
        rng = random.Random(11)
        for i in range(34):
            vx, vy = rng.uniform(-5.5, 5.5), rng.uniform(-7.5, -2.5)
            x, y = CAKE_X + vx * confetti, 24 + vy * confetti + 0.45 * confetti ** 2
            if 0 <= x < W - 1 and y < H:
                R(draw, round(x), round(y), 2, 2, CONFETTI[i % len(CONFETTI)])
    clawd(draw, look=look, blink=blink, bob=bob, walk=walk)
    arms_up(draw, OX, OY + bob, G, *a_main, flap=flap)
    friend(draw, fbob, flook, fblink, walk=walk, dx=friend_dx)
    arms_up(draw, FX + friend_dx, FY + fbob, FG, *a_friend, flap=flap)
    if hats:
        hat(draw, OX + 15, OY + bob + 2, 18, 8, HAT_A)
        hat(draw, FX + friend_dx + 10, FY + fbob, 15, 8, HAT_B)
    if grin:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
        smile5(draw, fbob, friend_dx)
    for px, py in puffs:
        R(draw, px, py, 2, 1, WHITE)
        R(draw, px + 1, py + 1, 1, 1, SMOKE)
    for nx, ny, c in notes:
        note(draw, nx, ny, c)
    return img


def rest(f=0):
    return party_frame(f)


def enter():
    fr = []
    for i, dx in enumerate([74, 48, 26, 10, 0]):
        fr.append(party_frame(0, look=(2, 0), friend_dx=dx, walk=i % 2 if dx else None,
                              cake_dy=None if i < 2 else (-34 if i == 2 else -12 if i == 3 else 0),
                              hats=False, grin=False, flook=(-1, 0)))
    fr.append(rest(0))
    return fr


def leave():
    fr = [rest(0)]
    for i, dx in enumerate([0, 10, 26, 48, 74]):
        fr.append(party_frame(0, look=(2, 0), friend_dx=dx, walk=i % 2 if dx else None,
                              cake_dy=None if i > 2 else (0 if i == 0 else -12 if i == 1 else -34),
                              hats=False, grin=False, flook=(-1, 0)))
    return fr


def blow():
    fr = [rest(0), rest(1)]
    for i in range(4):  # a happy wobble
        fr.append(party_frame(i, bob=-1 if i in (1, 2) else 0, fbob=-1 if i in (2, 3) else 0))
    for i in range(3):  # look at the cake, breathe in
        fr.append(party_frame(i, look=(2, 1), flook=(-2, 1), bob=-1 if i == 2 else 0, fbob=-1 if i == 2 else 0, grin=False))
    for i in range(6):  # blow
        pf = [(OX + 4 * G + 8 + k * 6 + i * 4, 24 + (k + i) % 2) for k in range(3) if OX + 4 * G + 8 + k * 6 + i * 4 < CAKE_X - 8]
        pf += [(FX + 4 * FG - 8 - k * 6 - i * 4, 28 + (k + i) % 2) for k in range(3) if FX + 4 * FG - 8 - k * 6 - i * 4 > CAKE_X + 8]
        fl = (1, 1, 1) if i < 3 else ((None, 1, None) if i == 3 else (None, None, None))
        fr.append(party_frame(i, look=(2, 1), flook=(-2, 1), flames=fl, puffs=pf, grin=False))
    for i in range(6):  # smoke, then the burst
        fr.append(party_frame(i, flames=(None, None, None) if i < 3 else (0, 0, 0), a_main=(True, True), a_friend=(True, True), flap=i % 2,
                              bob=-3 if i in (1, 2) else 0, fbob=-3 if i in (1, 2) else 0, confetti=i + 1 if i > 0 else None,
                              look=(2, -1), flook=(-2, -1)))
    for i in range(14):  # confetti falls, the trick candles light again
        up = i < 9
        fr.append(party_frame(i, flames=(0, 0, 0) if i < 7 else (1, 1, 1), a_main=(up, up), a_friend=(up, up), flap=i % 2,
                              confetti=7 + i, bob=-2 if i % 4 == 0 else 0, fbob=-2 if i % 4 == 2 else 0, sparkle=i == 7,
                              look=(2, -1 if up else 1), flook=(-2, -1 if up else 1)))
    fr += [party_frame(1, blink=True, fblink=True), rest(0)]
    return fr


def dance():
    fr = [rest(0), rest(1)]
    ncol = (PINK, LIGHT_BLUE, YELLOW)
    for i in range(32):
        m = i % 8 < 4
        notes = [(CAKE_X - 20 + ((i * 2 + k * 12) % 40), 16 - ((i + k * 5) % 14), ncol[k]) for k in range(3)]
        fr.append(party_frame(i, bob=-2 if (i // 2) % 2 == 0 and m else 0, fbob=-2 if (i // 2) % 2 == 0 and not m else 0,
                              a_main=(m, not m), a_friend=(not m, m), flap=(i // 2) % 2, notes=notes,
                              look=(2, 0 if m else 1), flook=(-2, 0 if not m else 1), blink=i == 20))
    fr += [party_frame(1, look=(2, 1)), rest(0)]
    return fr


if __name__ == "__main__":
    save_set("celebrate", enter, [blow, dance], leave)
