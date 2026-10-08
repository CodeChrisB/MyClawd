"""Speech: Clawd says the things Claude always says. Seven sets with two phrases each.

python speech_sets.py  ->  ../mine/{right,lets-look,tests-pass,sorry,great-question,proceed,thinking-aloud}/
No panel: a big speech bubble beside Clawd. It is always as wide as the canvas allows and top aligned,
only its height changes (it grows by one line whenever the text wraps). Text is the 3x5 font at scale 2.
Seam pose = Clawd alone, nothing said. Each loop: the bubble opens, the text is typed while Clawd talks, a reaction, the bubble closes.
"""
from props import *
from font3 import say

INK_T = (30, 34, 46)
BX0, BX1, BY0 = 84, 189, 2          # the bubble: full width, top aligned
LINE_H, PAD = 12, 6                 # scale 2 text: 10 px glyph rows + 2 px gap
MAX_CHARS = 12                      # (105 - 2 * 5 padding) / 8 px per character
SETS = {
    # name: (mood, icon, phrase A, phrase B)
    "right": ("happy", None, ["YOU'RE", "ABSOLUTELY", "RIGHT!"], ["GREAT", "CATCH!", "THANK YOU."]),
    "lets-look": ("think", None, ["LET ME TAKE", "A LOOK AT", "THAT."], ["I'LL START", "BY READING", "THE FILE."]),
    "tests-pass": ("happy", "tick", ["ALL TESTS", "PASS!"], ["DONE! READY", "TO COMMIT?"]),
    "sorry": ("sorry", None, ["I APOLOGIZE", "FOR THE", "CONFUSION."], ["YOU'RE", "RIGHT, MY", "MISTAKE."]),
    "great-question": ("happy", None, ["GREAT", "QUESTION!"], ["HERE'S WHAT", "I FOUND."]),
    "proceed": ("ask", None, ["SHOULD I", "PROCEED?"], ["WANT ME TO", "CONTINUE?"]),
    "thinking-aloud": ("think", None, ["HMM, LET ME", "THINK..."], ["ACTUALLY,", "WAIT."]),
}
for _, (_, _, a, b) in SETS.items():
    assert all(len(l) <= MAX_CHARS for l in a + b), (a, b)


def bubble(draw, lines_shown, pop=1.0):
    h = lines_shown * LINE_H + PAD
    w = max(6, round((BX1 - BX0 + 1) * pop))
    R(draw, BX0, BY0, w, h, WHITE)
    for cx, cy in ((BX0, BY0), (BX0 + w - 1, BY0), (BX0, BY0 + h - 1), (BX0 + w - 1, BY0 + h - 1)):
        R(draw, cx, cy, 1, 1, TRANS)
    ty = BY0 + min(h - 8, 24)                      # tail towards Clawd's face
    for i, tw in enumerate((6, 5, 4, 3, 2, 1)):
        R(draw, BX0 - tw, ty + i, tw, 1, WHITE)
    return h


def smile(draw, bob=0):
    draw_smile(draw, OX + 4 * G, OY + 2 * G + 1 + bob)


def speech_frame(lines=None, n=0, pop=0.0, mood="happy", icon=None, talk=False, react=0, look=(2, 1), blink=False, bob=0, f=0):
    img, draw = new_frame()
    if lines and pop > 0:
        typed, shown, left = [], 0, n
        for line in lines:
            typed.append(line[:max(0, left)])
            if left > 0:
                shown += 1
            left -= len(line)
        h = bubble(draw, max(1, shown), pop)
        if pop >= 1:
            for i, t in enumerate(typed):
                say(draw, BX0 + 5, BY0 + 4 + i * LINE_H, t, INK_T, 2)
            if icon == "tick" and n >= sum(len(l) for l in lines):
                tick(draw, BX1 - 14, BY0 + h - 12, GREEN, 2)
    clawd(draw, look=look, blink=blink, bob=bob)
    if talk:
        draw.rectangle([OX + 4 * G - 3, OY + 2 * G + 1 + bob, OX + 4 * G + 2, OY + 2 * G + 4 + bob], fill=BLACK)
    if react and mood in ("happy", "ask"):
        smile(draw, bob)
    if react and mood == "sorry":
        sweat(draw, bob, f)
    if mood == "ask" and react:
        draw.rectangle([OX + 8 * G, OY + 2 * G, OX + 10 * G - 1, OY + 4 * G - 1], fill=TRANS)
        draw.rectangle([OX + 8 * G, OY - 3, OX + 9 * G - 1, OY + 3 * G - 1], fill=CORAL)
    return img


def enter():
    looks = [(0, 0), (0, 0), (1, 0), (1, 1), (2, 1), (2, 1)]
    return [speech_frame(look=lk, bob=-1 if i == 3 else 0, blink=i == 1) for i, lk in enumerate(looks)]


def leave():
    looks = [(2, 1), (2, 1), (1, 1), (1, 0), (0, 0), (0, 0)]
    return [speech_frame(look=lk, bob=-1 if i == 2 else 0) for i, lk in enumerate(looks)]


def take(mood, icon, lines):
    f = speech_frame
    total = sum(len(l) for l in lines)
    looks = {"happy": (2, 1), "think": (2, -2), "sorry": (2, 2), "ask": (2, 1)}
    lk = looks[mood]
    frames = [f() for _ in range(3)]
    frames += [f(lines, pop=.4, mood=mood, look=lk), f(lines, pop=.75, mood=mood, look=lk),
               f(lines, pop=1.0, mood=mood, look=lk, bob=-1 if mood == "happy" else 0)]
    for k in range(1, total + 1):
        look = lk if mood != "think" else ((2, -2), (1, -2), (2, -1))[(k // 5) % 3]
        frames.append(f(lines, n=k, pop=1.0, mood=mood, icon=icon, talk=k % 2 == 1, look=look, bob=1 if k % 5 == 0 else 0))
    for i in range(10):
        frames.append(f(lines, n=total, pop=1.0, mood=mood, icon=icon, react=1, look=lk, f=i,
                        bob=-1 if (mood == "happy" and i == 0) else 0, blink=i == 7))
    frames += [f(lines, n=total, pop=.6, mood=mood, icon=icon, look=(2, 1)), f(look=(2, 1), blink=True), f()]
    return frames


if __name__ == "__main__":
    for name, (mood, icon, a, b) in SETS.items():
        save_set(name, enter, [lambda m=mood, i=icon, l=a: take(m, i, l), lambda m=mood, i=icon, l=b: take(m, i, l)], leave)
