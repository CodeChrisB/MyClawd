"""Thinking, redrawn smooth: a thought cloud with three hopping dots, drawn at 4x and scaled down (anti-aliased).

python thinking_sets.py  ->  ../mine/thinking/
Seam = dots at phase 0 inside the cloud. Every loop hops the dots, plays its own idea, and the dots pop back at phase 0.
The cloud has no panel: the edge alpha is thresholded so no anti-aliased fringe appears on the transparent canvas.
"""
import math

from props import *

SS = 4                                   # supersampling factor
CLOUD = (228, 232, 242)
CLOUD_EDGE = (150, 156, 178)
STEEL, CORAL_G, GOLD = (92, 102, 132), (226, 122, 88), (238, 178, 62)
CIRCLES = [(15, 31, 12), (29, 21, 13), (47, 16, 15), (64, 22, 13), (74, 33, 10), (54, 39, 13), (32, 39, 12)]
DELTA_A = 72.0                           # one loop of spinning = 2 tooth pitches of gear A (36 deg each) = whole teeth for all gears
GEARS = None
GS = 1.12                                # gear cluster size relative to the layout below


def gear_layout():
    """Meshing gears A (10 teeth), B (8), C (6): centres and phases so that teeth fall into gaps."""
    A = dict(cx=30, cy=33, Ro=12, Rr=10, n=10, color=STEEL)
    phi = math.radians(-50)
    B = dict(cx=A["cx"] + 19 * math.cos(phi), cy=A["cy"] + 19 * math.sin(phi), Ro=9, Rr=7, n=8, color=CORAL_G)
    b0 = phi + math.pi + math.pi / B["n"]
    psi = b0 - 3 * 2 * math.pi / B["n"]                                    # direction of a B tooth, C meshes there
    C = dict(cx=B["cx"] + 13.4 * math.cos(psi), cy=B["cy"] + 13.4 * math.sin(psi), Ro=6, Rr=4.4, n=6, color=GOLD)
    c0 = psi + math.pi + math.pi / C["n"]
    A["a0"], B["a0"], C["a0"] = phi, b0, c0
    return A, B, C


GEARS = gear_layout()


def gear(d, ox, g, theta, scale=1.0):
    """theta = rotation of gear A in radians; B turns the other way, C like A."""
    k = {0: 1.0, 1: -GEARS[0]["n"] / GEARS[1]["n"], 2: GEARS[0]["n"] / GEARS[2]["n"]}[GEARS.index(g)]
    ang = g["a0"] + theta * k
    cx, cy = (ox + 44 + (g["cx"] - 39.5) * GS * scale) * SS, (28.5 + (g["cy"] - 27) * GS * scale) * SS   # cluster centred in the cloud
    Ro, Rr, n = g["Ro"] * SS * scale * GS, g["Rr"] * SS * scale * GS, g["n"]
    p, pts = 2 * math.pi / n, []
    for i in range(n):
        a = ang + i * p
        for r, da in ((Rr, -0.30), (Ro, -0.14), (Ro, 0.14), (Rr, 0.30)):
            pts.append((cx + math.cos(a + da * p) * r, cy + math.sin(a + da * p) * r))
    body = g["color"]
    dark = tuple(round(c * 0.72) for c in body)
    d.polygon(pts, fill=body)
    d.ellipse([cx - Rr * 0.72, cy - Rr * 0.72, cx + Rr * 0.72, cy + Rr * 0.72], fill=dark)
    d.ellipse([cx - Rr * 0.5, cy - Rr * 0.5, cx + Rr * 0.5, cy + Rr * 0.5], fill=body)
    d.ellipse([cx - Rr * 0.2, cy - Rr * 0.2, cx + Rr * 0.2, cy + Rr * 0.2], fill=CLOUD)


def hop_dots(d, ox, theta, scale=1.0):
    """Three dots hop one after another; theta 72 = one hop cycle, so theta 0 is the seam."""
    for i in range(3):
        h = max(0.0, math.sin(math.radians(theta * 5) - i * 1.9))
        cx, cy, r = (ox + 34 + i * 10) * SS, (32 - 7 * h * scale) * SS, 4 * SS * scale
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CORAL_G if i == 1 else STEEL)


def cloud(d, ox):
    for pad, color in ((1.2, CLOUD_EDGE), (0, CLOUD)):
        for cx, cy, r in CIRCLES:
            d.ellipse([(ox + cx - r - pad) * SS, (cy - r - pad) * SS, (ox + cx + r + pad) * SS, (cy + r + pad) * SS], fill=color)
        d.rectangle([(ox + 15 - pad) * SS, (31 - pad) * SS, (ox + 74 + pad) * SS, (44 + pad) * SS], fill=color)


def bulb(d, ox, scale, glow):
    cx, cy = (ox + 44) * SS, 27 * SS
    if glow:
        for k in range(12):
            a = k * math.pi / 6
            r0, r1 = (13 + glow * 0.5) * SS * scale, (16 + glow * 2.2) * SS * scale
            d.line([cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * r1, cy + math.sin(a) * r1],
                   fill=(255, 196, 64), width=round(1.4 * SS))
    r = 9 * SS * scale
    d.ellipse([cx - r, cy - r * 1.05, cx + r, cy + r * 0.95], fill=(255, 218, 96))
    d.ellipse([cx - r * 0.55, cy - r * 0.75, cx - r * 0.15, cy - r * 0.35], fill=(255, 245, 190))
    d.rectangle([cx - r * 0.45, cy + r * 0.85, cx + r * 0.45, cy + r * 1.3], fill=(120, 126, 150))
    d.rectangle([cx - r * 0.3, cy + r * 1.3, cx + r * 0.3, cy + r * 1.5], fill=(90, 96, 118))


def dots(d, ox, f):
    for i in range(3):
        y = 30 - 5 * max(0, math.sin((f - i * 2) * 0.55)) if f - i * 2 >= 0 else 30
        cx = (ox + 34 + i * 10) * SS
        d.ellipse([cx - 3 * SS, (y - 3) * SS, cx + 3 * SS, (y + 3) * SS], fill=(110, 118, 144))


def check(d, ox, scale):
    s = SS * scale
    pts = [(ox + 32, 30), (ox + 40, 38), (ox + 56, 20)]
    d.line([(x * SS + (1 - scale) * 40 * SS * 0, y * SS) for x, y in pts], fill=(70, 180, 100), width=round(5 * s), joint="curve")


def thinking_frame(theta=0.0, gscale=1.0, bulb_s=0.0, glow=0, dots_f=None, check_s=0.0, look=(2, -2), blink=False, bob=0,
                   slide=0, smile=False, trail=3):
    img, draw = new_frame()
    x0 = PX0 + slide                                                          # no panel: the cloud sits on the transparent canvas
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    cloud(d, x0)
    if gscale > 0:
        hop_dots(d, x0, theta, gscale)
    if bulb_s > 0:
        bulb(d, x0, bulb_s, glow)
    if dots_f is not None:
        dots(d, x0, dots_f)
    if check_s > 0:
        check(d, x0, check_s)
    small = big.resize((W, H), Image.BOX)
    alpha = small.getchannel("A").point(lambda a: 255 if a >= 110 else 0)    # hard edge: anti-aliased edge pixels would turn pink
    small.putalpha(alpha)
    img.alpha_composite(small)
    draw = ImageDraw.Draw(img)
    for cx, cy, r in ((70, 11, 2), (79, 9, 3), (89, 10, 4))[:trail]:          # thought trail, plain pixels outside the panel
        draw.ellipse([cx - r - 1, cy - r - 1 + slide * 0, cx + r + 1, cy + r + 1], fill=CLOUD_EDGE)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CLOUD)
    clawd(draw, look=look, blink=blink, bob=bob)
    if smile:
        draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)
    return img


def intro(f):
    return [f()] * 3 + [f(blink=True)] + [f()] * 2


def spin(frames_n, start=0.0, step=3.0, **kw):
    return [thinking_frame(theta=start + step * i, bob=1 if 6 <= i < 16 else 0, **kw) for i in range(frames_n)]


def gears_loop():
    f = thinking_frame
    frames = intro(f)
    for i in range(24):                                                      # 72 degrees: whole teeth, so the last frame is the seam
        frames.append(f(theta=3.0 * (i + 1) if i < 23 else 0.0, look=(2, -2 - (i // 8 % 2)), bob=1 if 8 <= i < 16 else 0))
    for i in range(24):
        frames.append(f(theta=3.0 * (i + 1) if i < 23 else 0.0, look=(1 + i // 12, -2), blink=i == 10))
    return frames + [f()]


def idea_loop():
    f = thinking_frame
    frames = intro(f) + spin(10, 0.0, 3.0)
    for k in range(4):                                                       # gears shrink away
        frames.append(f(theta=30 + 3.0 * k, gscale=1 - (k + 1) / 4, look=(2, -3)))
    for k, s in enumerate((0.4, 0.9, 1.15, 1.0)):                            # the bulb pops
        frames.append(f(gscale=0, bulb_s=s, glow=k, look=(2, -3), bob=-2 if k == 2 else 0, smile=k > 1))
    for k in range(8):
        frames.append(f(gscale=0, bulb_s=1.0, glow=2 + k % 3, look=(2, -3), smile=True, bob=-1 if k in (1, 2) else 0))
    for k in range(3):
        frames.append(f(gscale=0, bulb_s=1.0 - (k + 1) / 3, glow=0, look=(2, -2), smile=k < 1))
    for k in range(4):                                                       # gears come back, still, at angle 0
        frames.append(f(theta=0.0, gscale=(k + 1) / 4, look=(2, -2)))
    return frames + [f()]


def dots_loop():
    f = thinking_frame
    frames = intro(f) + spin(8, 0.0, 3.0)
    for k in range(4):
        frames.append(f(theta=24 + 3.0 * k, gscale=1 - (k + 1) / 4, look=(1, -2)))
    for k in range(18):                                                      # "hmm...": three dots bounce, Clawd looks around
        frames.append(f(gscale=0, dots_f=k, look=(2 if k % 12 < 6 else 0, -2 + (k % 12 > 8)), blink=k == 13))
    for k in range(4):
        frames.append(f(theta=0.0, gscale=(k + 1) / 4, look=(2, -2)))
    return frames + [f()]


def found_loop():
    f = thinking_frame
    frames = intro(f) + spin(10, 0.0, 3.0)
    for k in range(4):
        frames.append(f(theta=30 + 3.0 * k, gscale=1 - (k + 1) / 4, look=(2, -2)))
    for k, s in enumerate((0.5, 1.0, 1.1, 1.0)):                             # got it: a check mark
        frames.append(f(gscale=0, check_s=s, look=(2, 0), smile=True, bob=-1 if k == 2 else 0))
    frames += [f(gscale=0, check_s=1.0, look=(2, 0), smile=True, blink=k == 5) for k in range(8)]
    for k in range(4):
        frames.append(f(theta=0.0, gscale=(k + 1) / 4, look=(2, -2)))
    return frames + [f()]


def slide(n, reverse):
    out = []
    for i in range(n):
        t = ease((i + 1) / n) if not reverse else 1 - ease(i / (n - 1))
        out.append(thinking_frame(look=(round(2 * t), -round(2 * t)), slide=round((1 - t) * (W - PX0 + 4)), trail=3 if t > 0.99 else 0))
    return out


if __name__ == "__main__":
    save_set("thinking", lambda: slide(ENTER, False), [gears_loop, idea_loop, found_loop], lambda: slide(EXIT, True))
