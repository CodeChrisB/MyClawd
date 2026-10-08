"""Speech: Clawd says the things Claude always says. Seven sets with two phrases each.

python speech_sets.py  ->  ../mine/{right,lets-look,tests-pass,sorry,great-question,proceed,thinking-aloud}/
Seam pose = the empty panel. Each loop: the bubble pops open, the text is typed while Clawd talks, a short reaction, the bubble closes.
"""
from props import *
from dev_sets import base, hold, smile
from font3 import say

INK_T = (30, 34, 46)
SETS = {
    # name: (mood, icon, phrase A, phrase B)
    "right": ("happy", None, ["You're absolutely", "right!"], ["Great catch!", "Thank you."]),
    "lets-look": ("think", None, ["Let me take a", "look at that."], ["I'll start by", "reading the file."]),
    "tests-pass": ("happy", "tick", ["All tests pass!"], ["Done! Ready to", "commit?"]),
    "sorry": ("sorry", None, ["I apologize for", "the confusion."], ["You're right,", "my mistake."]),
    "great-question": ("happy", None, ["Great question!"], ["Here's what", "I found."]),
    "proceed": ("ask", None, ["Should I", "proceed?"], ["Want me to", "continue?"]),
    "thinking-aloud": ("think", None, ["Hmm, let me", "think..."], ["Actually,", "wait."]),
}


def box(lines):
    return 4 * max(len(l) for l in lines) + 9, 7 * len(lines) + 5


def speech_frame(lines=None, n=0, pop=0.0, mood="happy", icon=None, talk=False, react=0, look=(2, 1), blink=False, bob=0, f=0, slide=0):
    img, draw, x0 = base(slide)
    if lines and pop > 0:
        w, h = box(lines)
        cx, cy = x0 + 46, 31
        ww, hh = max(3, round(w * pop)), max(3, round(h * pop))
        bx, by = cx - ww // 2 + 3, cy - hh // 2
        R(draw, bx, by, ww, hh, WHITE)
        R(draw, bx - 4, cy + 1, 4, 3, WHITE)
        R(draw, bx - 2, cy + 4, 2, 2, WHITE)
        if pop >= 1:
            left = n
            for i, line in enumerate(lines):
                shown = line[:max(0, left)]
                left -= len(line)
                say(draw, bx + 5, by + 3 + i * 7, shown, INK_T)
            if icon == "tick" and n >= sum(len(l) for l in lines):
                tick(draw, bx + ww - 8, by + hh - 7, GREEN)
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


def take(mood, icon, lines):
    f = speech_frame
    total = sum(len(l) for l in lines)
    looks = {"happy": (2, 1), "think": (2, -2), "sorry": (2, 2), "ask": (2, 1)}
    lk = looks[mood]
    frames = hold(f, 3)
    frames += [f(lines, pop=.5, mood=mood, look=lk), f(lines, pop=1.0, mood=mood, look=lk, bob=-1 if mood == "happy" else 0)]
    for k in range(1, total + 1):
        look = lk if mood != "think" else ((2, -2), (1, -2), (2, -1))[(k // 5) % 3]
        frames.append(f(lines, n=k, pop=1.0, mood=mood, icon=icon, talk=k % 2 == 1, look=look, bob=1 if k % 5 == 0 else 0))
    for i in range(9):
        frames.append(f(lines, n=total, pop=1.0, mood=mood, icon=icon, react=1, look=lk, f=i, bob=-1 if (mood == "happy" and i == 0) else 0,
                        blink=i == 6))
    frames += [f(lines, n=total, pop=.5, mood=mood, icon=icon, look=(2, 1)), f(look=(2, 1), blink=True)] + hold(f, 1)
    return frames


if __name__ == "__main__":
    for name, (mood, icon, a, b) in SETS.items():
        finish(name, speech_frame, [lambda m=mood, i=icon, l=a: take(m, i, l), lambda m=mood, i=icon, l=b: take(m, i, l)])
