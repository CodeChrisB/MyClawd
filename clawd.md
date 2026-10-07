# clawd.md — instructions for Claude

You are in the **MyClawd** repo. The user wants to create their own pixel-art GIF set of **Clawd** (the Claude Code mascot), in the same style as the 60+ sets on the site.
You draw every frame with Python and Pillow. There is no image model. Read this whole file, then follow the workflow.

## Workflow

0. **Setup.** If Pillow is missing, run `pip install -r requirements.txt`.
1. **Ask first.** Use the **AskUserQuestion** tool before writing any code. Do not guess what the GIF is about.
   Ask these in one call (up to 4 questions), each with 2-4 short options; the user can always pick "Other" and type:
   - *What should Clawd be doing in the GIF?* Options like: working on a task (typing, reading, searching) · using a tool or app (terminal, browser, finance, ...) · idle or relaxing (music, a hobby, napping) · reacting (happy, angry, confused, celebrating).
   - *What is next to Clawd?* Options like: a panel/screen on the right (chart, code, list) · a small prop he holds or sits at · a friend (a second Clawd) · nothing, just Clawd.
   - *How lively?* Calm (default, small slow movements) · medium · lively.
   - *How many loop variants?* 1 · 2-3 · 4 or more.
   If the answer to the first question is vague, ask one short follow-up for the concrete details (what exactly happens, what does it look like).
2. **Name it.** Short lowercase slug, for example `baking`. Output goes to `mine/<slug>/`.
3. **Read the code, then find a similar set.** Read `toolkit/clawd_core.py` and `toolkit/props.py` (both short). Then look at the catalog at the bottom of this file and open the one example file closest to what the user wants. Copy its structure, not the whole repo. `toolkit/template.py` is the smallest complete set.
4. **Write `toolkit/<slug>.py`.** Frame function first (`frame(**state)` returns one RGBA frame), then the loops, then `finish(...)` or `save_set(...)` at the bottom. One file per set, or several related sets in one file.
5. **Run it:** `python toolkit/<slug>.py`. `save_set` refuses to write if a seam is wrong; read the assertion message.
6. **Look at it.** Open `mine/<slug>/sheet-loop1.png` (and the other sheets, `sheet-enter.png`) with your image-reading tool. 12 evenly spaced frames, 2x. Judge pose, readability, contrast, clipping, anything floating. Fix and rerun until it looks right. You cannot see timing, so keep to the pace rules below. To compare several sets at once, paste the middle rows of their sheets into one PNG.
7. **Hand over.** Tell the user the folder and what is inside. `full.gif` plays everything (enter, every loop, exit). Then ask what to change, with AskUserQuestion again when the options are clear.

## The format

- **192 x 64 px**, **100 ms per frame**, transparent background, one 255-colour palette (`save_strip` does the export).
- Grid block `G = 6` px. Clawd is 8 blocks tall and 8 wide, plus a 2-block arm on each side. His head's top-left is `(OX, OY) = (16, 8)`, so there are only 8 px above his head.
- Clawd stands on the left (x 4..76). The activity area is the dark **panel** on the right (`PX0, PY0, PX1, PY1 = 98, 6, 186, 58`, 89 x 53 px). The free gap between Clawd and the panel is about 20 px.
- A set is a folder: `enter.gif` (plays once), `loop.gif`, `loop-2.gif`, ... (repeat), `exit.gif` (plays once), `full.gif` (preview).
- Enter and exit are 6 frames (0.6 s). Loops are 1-3 s, up to about 5 s for busy scenes.
- Scenes without a panel are possible (see `handoff` in `compact_sets.py`, `thinking_sets.py`), but then nothing may be anti-aliased against the transparent canvas (see gotchas).

## The seam contract (this is what makes the GIFs switchable)

Every set starts and ends on the same **seam pose**: Clawd with the panel at rest, eyes roughly centred, nothing in progress.

- `enter` ends exactly on the seam pose.
- every `loop` starts on it **and ends on it** (pixel-identical).
- `exit` starts on it and ends with the panel gone.

This lets a player switch from any GIF to any other without a jump. `save_set` checks it by comparing pixels.

### Ways to make content loop (all are used in the examples)

| Problem | Seam trick | Example |
|---|---|---|
| Content that cannot loop (typing, a growing chart, a pile) | Seam = the **empty** state. The take fills it and clears it again. | `trading.py`, `compact_sets.py`, `limit_sets.py` |
| Something keeps going forever (a chain, a conveyor) | Move it by exactly one period so the end equals the start. The git chain scrolls one node left; the belt phase wraps. | `git_sets.py` (`scroll_out`), `mode_sets.py` (`auto_run`) |
| Rotation (gears, a spinner) | Rotate by a whole number of tooth pitches for **every** gear (36 deg for 10 teeth, 45 deg for 8, 60 deg for 6) and set the **last frame's angle to exactly 0** so float noise cannot change a pixel. | `thinking_sets.py` |
| An effect that cannot be reversed (a rocket leaves, a sheet is written on) | Hide the reset behind something: a puff of smoke, a blink, a flash, a new rocket rising out of the ground. | `tool_sets.py` (`deploy_end`), `compact_sets.py` (`handoff`) |
| A state change that should look permanent (a gauge level, a selected model) | Keep the state **in the seam** and let the loop only wiggle around it. | `limit_sets.py` (context levels), `effort_sets.py`, `misc_sets.py` (`model_switch`) |
| Enter/exit when the seam is not `look=(2, 1)` | `slide_frames` always ends on `look=(2,1)`. Write your own enter/exit with `t = ease((i+1)/n)` (enter) and `t = 1 - ease(i/(n-1))` (exit) so the first exit frame equals the seam. | `thinking_sets.py` (`slide`) |

## Toolkit reference

`toolkit/clawd_core.py`
- `clawd(draw, look=(dx,dy), blink, lid, bob, dx, walk, color)`: Clawd. `look` shifts the eyes by px (dx at most 2, dy from -3 to 2). `lid` 0..1 half-closes the eyes. `bob` moves him vertically (negative = up, a hop). `dx` moves him sideways (can leave the canvas). `walk` 0/1 lifts one leg pair. `color` makes a second agent.
- `draw_smile(draw, x, y)`: the mouth. Call it after `clawd` at `(OX + 4*G, OY + 2*G + 1 + bob)`.
- `draw_panel(draw, slide, fill)`: the panel; returns `(x0, x1)`. `slide` shifts it right for enter/exit.
- `new_frame()`, `frames_of(n, painter)`, `ease(t)`, `slide_frames(make, n, reverse)`.
- `save_set(name, enter_fn, loop_fns, exit_fn)`: builds, **checks the seams**, writes GIFs and sheets. `check_seams`, `contact_sheet`, `save_strip` are the pieces.

`toolkit/props.py`
- `R(draw, x, y, w, h, color)`: rectangle by position and size (ignores empty sizes). Use this for everything; `draw.arc` and `draw.line` look dotty at this size.
- `dot(draw, cx, cy, r, color)`: filled circle without anti-aliasing. `tick(...)`, `cross(...)` with a scale `s`.
- `text(draw, x, y, "5H", color, scale)`: tiny 3x5 font. Glyphs in `GLYPHS`: `0 2 4 5 7 9 H D Z % ? E S C` only; add more with `GLYPHS["X"] = [...]`. Text is almost always too big at this size; prefer symbols.
- `sweat(...)`, `zzz(...)`, `cursor(...)`, `key_press(draw, bob)`: small expressive props.
- `clipped(img, x0, painter)`: draw things that start outside the panel (falling in, sliding in) and keep only what is inside it. **Use it whenever something crosses the panel border**, otherwise it leaks onto the transparent canvas.
- `lerp`, `mix(colour1, colour2, t)`, `intro(frame)` (idle + a blink), `finish(name, frame, loops)` (seam-slides enter/exit + `save_set`), `seam_slides(frame)`.

## Recipes

- **Eyes follow something:** `look=(2, dy)`, change `dy` as the thing moves (0 up, 1 middle, 2 down; -2 looks up).
- **Typing / tapping:** alternate `bob=1` with `key=True` on every other frame.
- **Happy hop:** `bob` through `0, -1, -2, -3, -2, -1, 0` plus `draw_smile`. Two characters hopping: use the **same frame numbers** for both.
- **Surprise:** `look=(0, 0)`, a quick `bob=-2`, `sweat` for worry.
- **Sleepy / relaxed / focused:** `lid` 0.85 / 0.4 / 0.0.
- **Walk across:** `dx` changes by about 8 px per frame with `walk=k % 2`.
- **A second agent:** `clawd(draw, dx=..., color=...)`; drawing order decides who is in front.
- **Accessories:** drawn after Clawd, above his head (8 px room). See `accessory()` in `misc_sets.py` (bitmap rows scaled by 1 or 2). For enter/exit, lift it by `slide // 8` so it drops on in the enter and lifts off in the exit.
- **Panel-style panels:** dark panel (`DARK`), light content, one accent colour per object. Terminals look like `session_sets.py`.
- **Moving a thing:** compute its position from the frame number with `ease(t)`, never hand-place frames.
- **Smooth, "realistic" objects (gears, clouds):** draw at 4x on a transparent layer, `resize((W, H), Image.BOX)`, composite. If the art sits **outside** a panel, threshold the alpha (`>= 110` becomes 255, else 0), otherwise the anti-aliased edge turns pink in the GIF. See `thinking_sets.py`.
- **Perspective / 3D:** keep it flat or simple. A warped screen looked wrong; the retro laptop with a frontal screen and a side-on keyboard worked. Mix of one frontal face and one thin side face is plenty.
- **Glitch / noise:** slice a crop of the panel into bands, paste them shifted, add seeded random pixels (`net_sets.py`, `crash_frame`).
- **Overlay dimming / flash:** composite a semi-transparent RGBA rectangle over the panel region only.

## Style (the user's taste, follow it)

- **Calm beats busy.** Hold poses 2-4 frames, move 1-2 px per frame. Fast or large steps strobe.
- Props 10-26 px. Smaller vanishes, larger crowds Clawd.
- **Clawd acts himself.** He picks things up with his own arm. No long stretched limbs.
- **Every motion needs a visible cause.** A press needs a rod holding the plate, a squeeze needs a wall that pushes, lines that disappear into a page need to slide into it. Nothing floats and nothing squashes by itself.
- **Symbols must be understandable at a glance.** Prefer a universal sign (tick, cross, bell, lock, key, coin with a $ for cost) over an abstract shape. If a reviewer cannot say what it is, redraw it.
- **No fake realism at 1 px.** If something looks pixelated because it tries to be realistic, either simplify it to a clean pixel icon or use the 4x supersampling recipe.
- Blink occasionally (one frame). Smile at success. Show effort with sweat, steam, shaking.
- Dark props vanish on dark backgrounds and white ones on light backgrounds. The site shows GIFs on a light grey panel, terminals are dark. Give props an outline or a mid-tone.
- The whole scene must fit inside 192 x 64. Nothing cut off at the edges unless it is deliberately sliding in.
- Use `AskUserQuestion` for anything that is genuinely the user's choice (which idea, which direction); do not ask about things you can decide.

## Gotchas (hard-won)

- Pillow merges identical consecutive frames in a saved GIF and adds their durations, so a decoded GIF has fewer frames than you drew. Compare on the frames you built (what `check_seams` does), never on decoded GIFs.
- A blink frame equal to a half-closed-lid frame merges away; use a clearly different pose.
- `slide_frames` ends on `look=(2, 1)`. If your seam uses another look, the seam check fails: write your own enter/exit.
- A rectangle with width or height 0 raises in Pillow; use `R()`, which ignores it.
- Anything drawn directly on the canvas that extends outside the panel is visible on the transparent background. Use `clipped(...)`.
- Anti-aliased edges against the transparent canvas turn pink (they are blended with the magenta export key). Inside the dark panel it is fine.
- A new top-level name in a set file can shadow a helper from `clawd_core` or `props`. Grep before you add one.
- Quantisation: all frames of a GIF share one palette, so a scene with many unrelated colours may shift slightly. Keep to a small palette per set.
- Objects must be physically right: an open padlock keeps its long shackle leg in the body and only the other leg comes out; a key points its tip at the lock. Check the direction of anything that moves toward something.
- Only Pillow is needed. Do not add other dependencies.
- Do not run `build.py`; it belongs to the site, not to creating a GIF.

## Catalog: look at the closest example before you start

| You want | Open | Sets in it |
|---|---|---|
| The smallest complete set | `template.py` | `template` |
| A panel with a growing chart / many takes | `trading.py` | `trading` |
| A gauge, levels, limits, a calendar, an hourglass | `limit_sets.py` | `context-*`, `limit-5h`, `limit-7d`, `limit-api-cost` |
| Tools and processes (plug, lock, rocket, database, download) | `tool_sets.py` | `tools`, `permission`, `deploy`, `database`, `download` |
| Pressing / squeezing / writing into a page, two characters | `compact_sets.py` | `compacting`, `handoff` |
| Smooth anti-aliased art, gears, a cloud | `thinking_sets.py` | `thinking` |
| A terminal, hops, sparkles, a key and lock, sunrise ideas | `session_sets.py` | `session-start`, `prompt`, `cwd`, `done`, `stop-failure` |
| Chains that scroll, nodes, branches, a cloud push | `git_sets.py` | `git-commit`, `git-push`, `git-pr` |
| Modes: blueprint, editor with accepted edits, conveyor belt | `mode_sets.py` | `mode-plan`, `mode-edit`, `mode-auto` |
| A dial and body language for effort | `effort_sets.py` | `effort-low` ... `effort-max` |
| Tests, review, speed lines, a gift, a corkboard, a dimmed overlay, small siblings with accessories, a background widget | `misc_sets.py` | `testing`, `code-review`, `fast-mode`, `update-available`, `memory-write`, `interrupt`, `model-switch`, `background-task` |
| Signal loss, request floods, glitches, a page fetch | `net_sets.py` | `offline`, `overloaded`, `crash`, `web-fetch` |
| A key in a lock, a book with a bookmark, a wipe | `cmd_sets.py` | `login`, `resume`, `clear` |
| Failure and retry, a todo list, goodbye, waiting agents, a timeline, a skill cartridge, a clock, linked windows | `event_sets.py` | `tool-failure`, `todo-list`, `session-end`, `teammate-idle`, `rewind`, `skills`, `scheduled-task`, `ide-connected` |
| Idle scenes with a prop and several variants (no panel) | `idle_sets.py` | `idle-coffee`, `idle-book` |

## Files

| Path | What |
|---|---|
| `clawd.md` | this file |
| `toolkit/clawd_core.py` | Clawd, canvas constants, frame helpers, seam check, GIF export, contact sheets |
| `toolkit/props.py` | rectangles, dots, ticks, tiny font, small props, clipping, `finish` |
| `toolkit/template.py` | smallest complete set, copy it |
| `toolkit/*_sets.py`, `trading.py` | worked examples, see the catalog |
| `mine/` | your output (git-ignored): GIFs and `sheet-*.png` per set |
| `index.html`, `build.py`, `sets/`, `zips/` | the website and its build script, not part of creating a GIF |
