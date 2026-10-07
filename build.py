"""Rebuild sets/, zips/ and sets.js from the Clawd status-bar source. Usage: python build.py
Delete a set you don't want published: remove its sets/<name>/ folder, zips/<name>.zip and re-run with its name in EXCLUDE."""
import json, shutil, zipfile
from PIL import Image, ImageSequence
from pathlib import Path

SRC = Path(__file__).parent / '_source' / 'statusbar'  # copy of Downloads/gifs.zip (2026-10-07); keep out of the published repo
EXCLUDE = {'youtrack'}  # company-branded, not published
GROUPS = {  # section title -> sets, in display order; anything unlisted lands in 'Other'
    'Working': ['writing', 'reading', 'thinking', 'todo-list', 'testing', 'code-review', 'ask', 'permission'],
    'Modes': ['mode-default', 'mode-plan', 'mode-edit', 'mode-auto', 'mode-sandbox', 'fast-mode', 'model-switch'],
    'Effort': ['effort-low', 'effort-medium', 'effort-high', 'effort-xhigh', 'effort-max', 'effort-adaptive', 'effort-ultrathink'],
    'Agents': ['agent', 'agent-spawn', 'agent-report', 'agent-merge', 'agents', 'handoff', 'teammate-idle', 'background-task'],
    'Git': ['git', 'git-commit', 'git-push', 'git-pr'],
    'Tools': ['search', 'web-fetch', 'browser', 'bash', 'trading', 'tools', 'skills', 'ide-connected', 'scheduled-task', 'database', 'download'],
    'Build and CI': ['ci-pipeline', 'build', 'container', 'deploy'],
    'Docs and learning': ['docs-read', 'tutorial', 'learned', 'memory-write'],
    'Multimodal': ['paste-image', 'voice-input', 'screenshot', 'video', 'pdf', 'excel', 'powerpoint', 'multitasking'],
    'Context': ['context-empty', 'context-quarter', 'context-half', 'context-three-quarters', 'context-full', 'compacting'],
    'Limits': ['limit-5h', 'limit-7d', 'limit-api-cost'],
    'Session': ['session-start', 'login', 'prompt', 'cwd', 'resume', 'rewind', 'clear', 'done', 'interrupt', 'update-available',
                'session-end'],
    'Problems': ['tool-failure', 'offline', 'overloaded', 'stop-failure', 'crash'],
    'Idle': ['idle', 'idle-coffee', 'idle-book', 'idle-chat', 'idle-doze', 'idle-heart', 'idle-look', 'idle-swag', 'idle-walk', 'idle-yawn'],
    'Idle with music': ['radio', 'dj', 'disco'],
}
DESC = {  # one line per set, shown under the name
    'thinking': 'Claude is thinking', 'writing': 'Claude is writing or editing code', 'reading': 'Claude is reading files',
    'ask': 'Claude requires user input', 'agent': 'Claude runs a sub-agent', 'agents': 'Claude runs several agents in parallel',
    'search': 'Claude searches the web', 'browser': 'Claude controls the browser',
    'bash': 'Claude runs shell commands', 'trading': 'Claude watches the markets and makes trades',
    'tools': 'Claude connects tools and plugins', 'permission': 'Claude needs your permission', 'deploy': 'Claude deploys',
    'database': 'Claude queries and updates a database', 'download': 'Claude downloads files',
    'context-empty': 'Context is almost empty, a fresh start', 'context-quarter': 'Context is about a quarter full',
    'context-half': 'Context is about half full', 'context-three-quarters': 'Context is about three quarters full',
    'context-full': 'Context is full, Claude has to compact',
    'compacting': 'Claude compacts the conversation', 'session-start': 'A new session starts',
    'prompt': 'Your message arrives', 'cwd': 'Claude changes directory', 'done': 'Claude finished the turn',
    'stop-failure': 'The API call failed',
    'mode-plan': 'Plan mode: Claude plans before touching anything', 'mode-edit': 'Edit mode: edits are accepted automatically',
    'mode-auto': 'Auto mode: Claude runs everything on its own', 'fast-mode': 'Fast mode',
    'model-switch': 'Claude switches model', 'testing': 'Claude runs the tests', 'code-review': 'Claude reviews a diff',
    'update-available': 'A new Claude Code version is available', 'memory-write': 'Claude writes a memory',
    'interrupt': 'You interrupted Claude with Esc', 'background-task': 'Claude works while a background task runs',
    'effort-low': 'Low effort: calm and quick', 'effort-medium': 'Medium effort: steady work',
    'effort-high': 'High effort: focused', 'effort-xhigh': 'Extra high effort: working hard',
    'effort-max': 'Max effort: everything Claude has', 'mode-default': 'Default mode: Claude asks before each step', 'mode-sandbox': 'Sandbox mode: free inside, walls outside',
    'effort-ultrathink': 'Ultrathink: effort goes past max', 'effort-adaptive': 'Adaptive effort: the dial follows the task',
    'agent-spawn': 'Claude spawns a sub-agent', 'agent-report': 'A sub-agent reports back', 'agent-merge': 'Results from several agents are merged',
    'video': 'Claude watches a video', 'multitasking': 'Claude works in three programs at once',
    'ci-pipeline': 'CI runs lint, test, build and ship', 'build': 'Claude builds the project',
    'container': 'Claude builds a container layer by layer', 'docs-read': 'Claude reads the docs',
    'tutorial': 'Claude follows a tutorial step by step', 'learned': 'Claude learns something new',
    'paste-image': 'You paste an image', 'voice-input': 'You talk to Claude with voice input',
    'screenshot': 'Claude reads a screenshot', 'pdf': 'Claude reads a PDF', 'excel': 'Claude works with a spreadsheet',
    'powerpoint': 'Claude works with slides', 'tool-failure': 'A tool failed, Claude retries', 'todo-list': 'Claude works through a todo list',
    'session-end': 'The session ends', 'teammate-idle': 'Teammate agents wait for work', 'rewind': 'Claude rewinds the conversation',
    'skills': 'Claude loads a skill', 'scheduled-task': 'A scheduled task fires', 'ide-connected': 'Claude connects to the IDE',
    'idle-coffee': 'Idle, with a coffee', 'idle-book': 'Idle, reading a book',
    'offline': 'No connection: Claude is offline', 'overloaded': 'The API is overloaded (529)',
    'crash': 'Claude Code crashed and restarts', 'web-fetch': 'Claude fetches a web page', 'login': 'Claude logs in',
    'resume': 'Claude resumes a conversation', 'clear': 'Claude clears the conversation', 'git-commit': 'Claude commits', 'git-push': 'Claude pushes to the remote', 'git-pr': 'Claude opens and merges a pull request', 'handoff': 'Claude hands over to another agent', 'limit-5h': 'Claude hit the 5-hour limit',
    'limit-7d': 'Claude hit the 7-day limit', 'limit-api-cost': 'Claude hit the API cost limit', 'git': 'Claude digs through git history and code',
    'idle': 'Claude is waiting for you', 'idle-chat': 'Idle, chatting with a friend', 'idle-doze': 'Idle, dozing off',
    'idle-heart': 'Idle, feeling the love', 'idle-look': 'Idle, looking around', 'idle-swag': 'Idle, with swag',
    'idle-walk': 'Idle, taking a walk', 'idle-yawn': 'Idle, yawning',
    'radio': 'Idle, listening to the radio', 'dj': 'Idle, DJing', 'disco': 'Idle, dancing at the disco',
}
RENAME = {'gitfind': 'git', 'context': 'context-full'}  # source folder -> published name (sets/, zips/, folder inside the zip, title)
FILES = ('full', 'enter', 'exit')  # plus every loop*.gif of the set
HERE = Path(__file__).parent

for d in ('sets', 'zips'):
    shutil.rmtree(HERE / d, ignore_errors=True); (HERE / d).mkdir()
names = []
all_zip = zipfile.ZipFile(HERE / 'zips' / 'MyClawd-all.zip', 'w', zipfile.ZIP_STORED)  # every set, one folder each
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
    for g in gifs: all_zip.write(out / g, f'{name}/{g}')
    names.append(name)
    PLAY[name] = {'enter': ms(out / 'enter.gif'), 'exit': ms(out / 'exit.gif'), 'loops': [[g, ms(out / g)] for g in gifs if g.startswith('loop')]}
all_zip.close()
groups = [{'title': t, 'sets': [n for n in g if n in names]} for t, g in GROUPS.items()]
rest = [n for n in names if not any(n in g for g in GROUPS.values())]
if rest: groups.append({'title': 'Other', 'sets': rest})
(HERE / 'sets.js').write_text('const DESC = ' + json.dumps(DESC) + ';' + chr(10) + 'const PLAY = ' + json.dumps(PLAY) + ';' + chr(10) + 'const GROUPS = ' + json.dumps([g for g in groups if g['sets']]) + ';' + chr(10))  # .js, not .json: fetch() is blocked on file://
(HERE / 'clawd-md.js').write_text('const CLAWD_MD = ' + json.dumps((HERE / 'clawd.md').read_text(encoding='utf-8')) + ';' + chr(10), encoding='utf-8')  # inlined so the dialog works from file:// too
print(len(names), 'sets')
