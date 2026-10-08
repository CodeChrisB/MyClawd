"""Saving for sets that must loop without a hitch: the loop is exactly one period long (no duplicate seam frame at the end),
the enter starts on the base pose (Clawd alone) and ends on the frame right before loop frame 0, the exit starts on loop frame 0
and ends on the base pose. save_flow checks what can be checked pixel-exact and writes the usual files."""
from clawd_core import *


def base_pose():
    img, draw = new_frame()
    clawd(draw)
    return img


def save_flow(name, enter, loops, leave):
    base = base_pose()
    assert same(enter[0], base), "enter must start on the base pose (Clawd alone, eyes centred, nothing else visible)"
    assert same(leave[-1], base), "exit must end on the base pose"
    for i, fr in enumerate(loops, 1):
        assert same(leave[0], fr[0]), f"exit must start on loop {i} frame 0"
        assert not same(fr[0], fr[-1]), f"loop {i} repeats its first frame at the end, that is a visible hitch"
        assert not same(enter[-1], fr[0]), f"enter repeats loop {i} frame 0"
    out = OUT_DIR / name
    out.mkdir(parents=True, exist_ok=True)
    save_strip(enter, out / "enter.gif", repeat=False)
    for i, fr in enumerate(loops, 1):
        save_strip(fr, out / ("loop.gif" if i == 1 else f"loop-{i}.gif"), repeat=True)
        contact_sheet(fr, out / f"sheet-loop{i}.png")
    save_strip(leave, out / "exit.gif", repeat=False)
    contact_sheet(enter, out / "sheet-enter.png", pick=min(12, len(enter)), cols=4)
    contact_sheet(leave, out / "sheet-exit.png", pick=min(12, len(leave)), cols=4)
    save_strip(enter + [f for fr in loops for f in fr] + leave, out / "full.gif", repeat=True)
    print(f"flow ok, wrote {out}")
