"""Rebuild sets/, zips/ and sets.js from the Clawd status-bar source. Usage: python build.py
Delete a set you don't want published: remove its sets/<name>/ folder, zips/<name>.zip and re-run with its name in EXCLUDE."""
import json, shutil, zipfile
from PIL import Image, ImageSequence
from pathlib import Path

SRC = Path(__file__).parent / '_source' / 'statusbar'  # copy of Downloads/gifs.zip (2026-10-07); keep out of the published repo
EXCLUDE = {'youtrack'}  # company-branded, not published
GROUPS = {  # section title -> sets, in display order; anything unlisted lands in 'Other'
    'Working': ['thinking', 'writing', 'reading', 'ask'],
    'Agents': ['agent', 'agents'],
    'Tools': ['search', 'browser', 'bash', 'git'],
    'Idle': ['idle', 'idle-chat', 'idle-doze', 'idle-heart', 'idle-look', 'idle-swag', 'idle-walk', 'idle-yawn'],
    'Idle with music': ['radio', 'dj', 'disco'],
}
DESC = {  # one line per set, shown under the name
    'thinking': 'Claude is thinking', 'writing': 'Claude is writing or editing code', 'reading': 'Claude is reading files',
    'ask': 'Claude requires user input', 'agent': 'Claude runs a sub-agent', 'agents': 'Claude runs several agents in parallel',
    'search': 'Claude searches the web', 'browser': 'Claude controls the browser',
    'bash': 'Claude runs shell commands', 'git': 'Claude digs through git history and code',
    'idle': 'Claude is waiting for you', 'idle-chat': 'Idle, chatting with a friend', 'idle-doze': 'Idle, dozing off',
    'idle-heart': 'Idle, feeling the love', 'idle-look': 'Idle, looking around', 'idle-swag': 'Idle, with swag',
    'idle-walk': 'Idle, taking a walk', 'idle-yawn': 'Idle, yawning',
    'radio': 'Idle, listening to the radio', 'dj': 'Idle, DJing', 'disco': 'Idle, dancing at the disco',
}
RENAME = {'gitfind': 'git'}  # source folder -> published name (sets/, zips/, folder inside the zip, title)
FILES = ('full', 'enter', 'exit')  # plus every loop*.gif of the set
HERE = Path(__file__).parent

for d in ('sets', 'zips'):
    shutil.rmtree(HERE / d, ignore_errors=True); (HERE / d).mkdir()
names = []
PLAY = {}  # name -> {enter, exit (ms), loops: [[file, ms]]} for the header player (durations can't be read by JS on file://)


def ms(path):
    im = Image.open(path)
    return sum(f.info.get('duration', 100) or 100 for f in ImageSequence.Iterator(im))
for s in sorted(p for p in SRC.iterdir() if p.is_dir() and p.name not in EXCLUDE):
    name = RENAME.get(s.name, s.name)
    out = HERE / 'sets' / name; out.mkdir()
    gifs = [f'{f}.gif' for f in FILES] + sorted(p.name for p in s.glob('loop*.gif'))
    for g in gifs: shutil.copy(s / g, out / g)
    with zipfile.ZipFile(HERE / 'zips' / f'{name}.zip', 'w', zipfile.ZIP_STORED) as z:  # gifs are already compressed
        for g in gifs: z.write(out / g, f'{name}/{g}')
    names.append(name)
    PLAY[name] = {'enter': ms(out / 'enter.gif'), 'exit': ms(out / 'exit.gif'), 'loops': [[g, ms(out / g)] for g in gifs if g.startswith('loop')]}
groups = [{'title': t, 'sets': [n for n in g if n in names]} for t, g in GROUPS.items()]
rest = [n for n in names if not any(n in g for g in GROUPS.values())]
if rest: groups.append({'title': 'Other', 'sets': rest})
(HERE / 'sets.js').write_text('const DESC = ' + json.dumps(DESC) + ';' + chr(10) + 'const PLAY = ' + json.dumps(PLAY) + ';' + chr(10) + 'const GROUPS = ' + json.dumps([g for g in groups if g['sets']]) + ';' + chr(10))  # .js, not .json: fetch() is blocked on file://
print(len(names), 'sets')
