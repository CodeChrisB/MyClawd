"""Everything needed to draw Clawd status-bar GIFs: colours, Clawd himself, frame helpers, seam check, export.

Size 192x64, 100 ms per frame, transparent background. One grid block = G = 6 px.
Output goes to ../mine/<set>/ (enter.gif, loop.gif, loop-2.gif ..., exit.gif, full.gif + a PNG sheet per loop).
"""
from pathlib import Path

from PIL import Image, ImageDraw

# Colours
CORAL, BLACK, WHITE = (212, 132, 90), (0, 0, 0), (255, 255, 255)
YELLOW, RED, GREEN, LIGHT_BLUE = (240, 200, 80), (220, 80, 80), (80, 180, 100), (160, 200, 240)
PINK, PURPLE, ORANGE = (240, 160, 180), (160, 100, 200), (240, 160, 60)
COMMENT = (110, 116, 130)       # dim grey for secondary things
PANEL_EDGE = (52, 54, 64)       # border of the panel on the right
TRANS = (0, 0, 0, 0)
EXPORT_KEY_RGB = (255, 0, 255)  # magenta key, becomes palette index 255 = transparent

# Canvas and Clawd's place on it
W, H = 192, 64
G = 6                                  # one block in px; Clawd is 8 blocks tall, 8 wide (+2 arm blocks each side)
OX, OY = 2 * G + 4, (H - 8 * G) // 2   # top-left of Clawd's head
PX0, PY0, PX1, PY1 = 98, 6, 186, 58    # the panel/activity area on the right
FRAME_MS = 100
ENTER = EXIT = 6                       # frames of enter / exit (0.6 s)

OUT_DIR = Path(__file__).resolve().parent.parent / "mine"


def ease(t):
    return t * t * (3 - 2 * t)


def new_frame():
    img = Image.new("RGBA", (W, H), TRANS)
    return img, ImageDraw.Draw(img)


def frames_of(n, painter):
    """n frames; painter(draw, i) draws frame i."""
    out = []
    for i in range(n):
        img, draw = new_frame()
        painter(draw, i)
        out.append(img)
    return out


def _block(draw, x, y, w, h, color):
    draw.rectangle([x, y, x + w * G - 1, y + h * G - 1], fill=color)


def clawd(draw, look=(0, 0), blink=False, lid=0.0, bob=0, dx=0, walk=None, color=CORAL):
    """Draw Clawd. look = eye shift in px (keep it within about 2), lid 0..1 half closes the eyes,
    bob = vertical px, dx = horizontal px (can leave the canvas), walk = 0/1 lifts one leg pair,
    color = body colour (a second agent)."""
    ox, oy = OX + dx, OY + bob
    _block(draw, ox, oy, 8, 2, color)                   # head
    _block(draw, ox - 2 * G, oy + 2 * G, 12, 2, color)  # body + arms
    _block(draw, ox, oy + 4 * G, 8, 2, color)           # lower body
    for col in (0, 2, 5, 7):                            # legs, one pair shorter while walking
        lifted = walk is not None and (col in (0, 5)) == (walk == 0)
        _block(draw, ox + col * G, oy + 6 * G, 1, 1 if lifted else 2, color)
    for ex in (ox + G, ox + 6 * G):
        if blink:
            y = oy + G + G // 2
            draw.rectangle([ex, y, ex + G - 1, y + 2], fill=BLACK)
        else:
            cover = min(G - 1, round(G * lid))
            x, y = ex + look[0], oy + G + look[1]
            draw.rectangle([x, y + cover, x + G - 1, y + G - 1], fill=BLACK)


def draw_smile(draw, mx, my):
    draw.rectangle([mx - 5, my, mx - 4, my + 1], fill=BLACK)
    draw.rectangle([mx - 3, my + 2, mx + 2, my + 3], fill=BLACK)
    draw.rectangle([mx + 3, my, mx + 4, my + 1], fill=BLACK)


def draw_panel(draw, slide=0, fill=(24, 26, 38)):
    """The dark panel on the right. slide shifts it right (off screen) for enter/exit."""
    x0, x1 = PX0 + slide, PX1 + slide
    draw.rectangle([x0 - 2, PY0 - 2, x1 + 2, PY1 + 2], fill=PANEL_EDGE)
    draw.rectangle([x0, PY0, x1, PY1], fill=fill)
    return x0, x1


def slide_frames(make, n, reverse):
    """Enter/exit by sliding the panel. make(look, slide) returns one frame; t=1 is the seam pose."""
    out = []
    for i in range(n):
        t = ease((i + 1) / n) if not reverse else 1 - ease(i / (n - 1))
        out.append(make((round(2 * t), round(t)), round((1 - t) * (W - PX0 + 4))))
    return out


# Export

def save_strip(frames, path, repeat):
    """Transparent GIF with one shared palette. Enter/exit play once, loops repeat."""
    rgbs = [Image.alpha_composite(Image.new("RGBA", (W, H), EXPORT_KEY_RGB + (255,)), f).convert("RGB") for f in frames]
    sheet = Image.new("RGB", (W, H * len(rgbs)))
    for i, rgb in enumerate(rgbs):
        sheet.paste(rgb, (0, i * H))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT).getpalette()[:255 * 3] + list(EXPORT_KEY_RGB)
    pal = Image.new("P", (1, 1))
    pal.putpalette(palette)
    out = []
    for frame, rgb in zip(frames, rgbs):
        p = rgb.quantize(palette=pal, dither=Image.Dither.NONE)
        p.paste(255, mask=frame.getchannel("A").point(lambda a: 255 if a == 0 else 0))
        out.append(p)
    out[0].save(path, save_all=True, append_images=out[1:], duration=FRAME_MS, disposal=2, transparency=255,
                optimize=False, **({"loop": 0} if repeat else {}))


def contact_sheet(frames, path, pick=12, cols=4, bg=(60, 60, 64)):
    """PNG with `pick` evenly spaced frames at 2x on a grey background. Read this to judge an animation."""
    pick = min(pick, len(frames))
    idx = [round(i * (len(frames) - 1) / max(1, pick - 1)) for i in range(pick)]
    rows = (pick + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W * 2, rows * H * 2), bg)
    for k, i in enumerate(idx):
        f = frames[i].resize((W * 2, H * 2), Image.NEAREST)
        b = Image.new("RGBA", f.size, bg + (255,))
        b.alpha_composite(f)
        sheet.paste(b.convert("RGB"), ((k % cols) * W * 2, (k // cols) * H * 2))
    sheet.save(path)


def same(a, b):
    return a.tobytes() == b.tobytes()


def check_seams(enter, loops, leave):
    """The contract: enter ends on the seam pose, every loop starts and ends on it, exit starts on it."""
    seam = enter[-1]
    assert same(leave[0], seam), "exit must start on the seam pose (= last frame of enter)"
    for i, fr in enumerate(loops, 1):
        assert same(fr[0], seam), f"loop {i} must start on the seam pose"
        assert same(fr[-1], seam), f"loop {i} must end on the seam pose"


def save_set(name, enter_fn, loop_fns, exit_fn):
    """Build, check the seams, write the GIFs and one PNG sheet per loop into mine/<name>/."""
    enter, loops, leave = enter_fn(), [fn() for fn in loop_fns], exit_fn()
    check_seams(enter, loops, leave)
    out = OUT_DIR / name
    out.mkdir(parents=True, exist_ok=True)
    save_strip(enter, out / "enter.gif", repeat=False)
    for i, fr in enumerate(loops, 1):
        save_strip(fr, out / ("loop.gif" if i == 1 else f"loop-{i}.gif"), repeat=True)
        contact_sheet(fr, out / f"sheet-loop{i}.png")
    save_strip(leave, out / "exit.gif", repeat=False)
    contact_sheet(enter, out / "sheet-enter.png", pick=6, cols=3)
    save_strip(enter + [f for fr in loops for f in fr] + leave, out / "full.gif", repeat=True)
    print(f"seams ok, wrote {out}")
    return out
