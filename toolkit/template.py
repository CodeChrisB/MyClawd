"""Smallest complete set: Clawd waits while a chat bubble types three dots. Copy this file and change the loop.

python template.py  ->  ../mine/template/
Seam pose = panel on screen with no dots. Enter slides it in, each loop adds dots and returns to the seam, exit slides it out.
"""
from clawd_core import *


def frame(dots=0, look=(2, 1), blink=False, bob=0, slide=0):
    img, draw = new_frame()
    x0, x1 = draw_panel(draw, slide)
    for i in range(dots):  # dots in the panel centre
        cx = (x0 + x1) // 2 - 12 + i * 12
        draw.rectangle([cx, 28, cx + 5, 33], fill=WHITE)
    clawd(draw, look=look, blink=blink, bob=bob)
    return img


def enter():
    return slide_frames(lambda look, slide: frame(look=look, slide=slide), ENTER, reverse=False)


def leave():
    return slide_frames(lambda look, slide: frame(look=look, slide=slide), EXIT, reverse=True)


def loop():
    frames = [frame()] * 3  # first frame = seam
    for _ in range(2):
        for d in (1, 2, 3):
            frames += [frame(dots=d, bob=d % 2)] * 3
        frames += [frame(dots=3)] * 3
    frames += [frame(dots=3, blink=True), frame(dots=2), frame(dots=1)]
    return frames + [frame()]  # last frame = seam


if __name__ == "__main__":
    save_set("template", enter, [loop], leave)
