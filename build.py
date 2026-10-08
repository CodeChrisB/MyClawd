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
    'Context': ['context-empty', 'context-quarter', 'context-half', 'context-three-quarters', 'context-full', 'auto-compact', 'compacting'],
    'Limits': ['limit-5h', 'limit-7d', 'limit-api-cost'],
    'Session': ['session-start', 'login', 'prompt', 'cwd', 'resume', 'rewind', 'clear', 'done', 'interrupt', 'update-available',
                'session-end'],
    'Problems': ['tool-failure', 'offline', 'overloaded', 'stop-failure', 'crash'],
    'Idle': ['idle', 'idle-coffee', 'idle-book', 'idle-chat', 'idle-doze', 'idle-heart', 'idle-look', 'idle-swag', 'idle-walk', 'idle-yawn',
             'idle-fall', 'idle-juggle'],
    'Idle with music': ['radio', 'dj', 'disco'],
    'Speech': ['right', 'lets-look', 'tests-pass', 'sorry', 'great-question', 'proceed', 'thinking-aloud'],
    'Dev work': ['debug', 'merge-conflict', 'lint', 'security', 'benchmark', 'api-request', 'friday-deploy'],
    'Memes': ['this-is-fine'],
    'Misc': ['legal', 'celebrate', 'night-owl', 'new-mail', 'hello', 'overworked'],
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
    'effort-max': 'Max effort: everything Claude has', 'legal': 'Legal: free to use, no data, not affiliated, just for fun',
    'auto-compact': 'Auto-compact: the bell rings at 90% and the context compacts itself',
    'mode-default': 'Default mode: Claude asks before each step', 'mode-sandbox': 'Sandbox mode: free inside, walls outside',
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
    'debug': 'Claude hunts a bug or steps through code', 'merge-conflict': 'Claude resolves a merge conflict',
    'lint': 'Claude formats the file and clears the warnings', 'security': 'Claude scans for leaked secrets and audits packages',
    'benchmark': 'Claude measures speed and reads a flame graph', 'api-request': 'Claude calls an API: 200, 404 or 500',
    'celebrate': 'Two Clawds and a cake: blow out the candles, confetti, dance',
    'right': "Claude says: You're absolutely right!", 'lets-look': 'Claude says: Let me take a look', 'tests-pass': 'Claude says: All tests pass!',
    'sorry': 'Claude says: I apologize for the confusion', 'great-question': 'Claude says: Great question!', 'proceed': 'Claude says: Should I proceed?',
    'thinking-aloud': 'Claude says: Hmm, let me think', 'overworked': 'Too many tickets, too much coffee',
    'friday-deploy': 'Deploying on Friday the 13th', 'this-is-fine': 'This is fine. Clawd sips coffee while the room burns', 'night-owl': 'Working late at night',
    'new-mail': 'A new message arrives', 'hello': 'Clawd says hello',
    'idle-fall': 'Idle, falling through the clouds', 'idle-juggle': 'Idle, juggling three balls',
    'radio': 'Idle, listening to the radio', 'dj': 'Idle, DJing', 'disco': 'Idle, dancing at the disco',
}

# Search tags: every set gets its category's tags plus its own
GROUP_TAGS = {
    'Working': ['work'], 'Modes': ['mode', 'settings'], 'Effort': ['effort', 'settings'], 'Agents': ['agent', 'work'],
    'Git': ['git', 'terminal', 'work'], 'Tools': ['tool', 'work'], 'Build and CI': ['build', 'terminal', 'work'],
    'Docs and learning': ['docs', 'learning'], 'Multimodal': ['media', 'input'], 'Context': ['context', 'status'],
    'Limits': ['limit', 'status'], 'Session': ['session'], 'Problems': ['error', 'problem'], 'Idle': ['idle', 'fun'],
    'Idle with music': ['idle', 'music', 'fun'], 'Speech': ['speech', 'talk', 'fun'], 'Memes': ['meme', 'fun'], 'Dev work': ['dev', 'work', 'program'], 'Misc': ['fun'],
}
SET_TAGS = {
    'bash': ['terminal', 'shell', 'command'], 'browser': ['program', 'web', 'chrome'], 'search': ['web', 'internet'],
    'web-fetch': ['web', 'internet'], 'trading': ['program', 'finance', 'money'], 'excel': ['program', 'office'],
    'powerpoint': ['program', 'office'], 'pdf': ['program', 'office', 'document'], 'video': ['program'],
    'multitasking': ['program', 'windows'], 'ide-connected': ['program', 'editor'], 'writing': ['code', 'editor'],
    'reading': ['code', 'editor'], 'thinking': ['brain', 'idea'], 'deploy': ['terminal', 'server'], 'database': ['server', 'data'],
    'download': ['network', 'files'], 'cwd': ['terminal', 'folder'], 'session-start': ['terminal', 'start'], 'prompt': ['terminal', 'input'],
    'login': ['terminal', 'account'], 'resume': ['terminal'], 'clear': ['terminal'], 'crash': ['terminal'], 'offline': ['network'],
    'overloaded': ['network', 'api'], 'stop-failure': ['api'], 'api-request': ['api', 'network', 'http', 'terminal'],
    'debug': ['bug', 'terminal', 'fix'], 'lint': ['format', 'code', 'terminal'], 'security': ['secrets', 'safety', 'audit'],
    'benchmark': ['performance', 'speed'], 'merge-conflict': ['git', 'code'], 'testing': ['tests', 'terminal'],
    'code-review': ['code', 'diff'], 'handoff': ['session'], 'done': ['session', 'success'], 'update-available': ['version'],
    'radio': ['music'], 'dj': ['music'], 'disco': ['music'], 'celebrate': ['party', 'success'], 'night-owl': ['night', 'time'],
    'new-mail': ['message', 'notification'], 'hello': ['greeting'], 'scheduled-task': ['time', 'cron'], 'legal': ['info'],
    'overworked': ['work', 'stress', 'coffee'], 'friday-deploy': ['deploy', 'time', 'risk', 'terminal'], 'this-is-fine': ['fire', 'coffee'],
    'celebrate': ['party', 'success', 'friend'], 'idle-fall': ['animation'], 'idle-juggle': ['animation'],
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
import datetime, subprocess
def added(n):  # date the set first entered the repo, today for a set that is not committed yet
    try:
        out = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%as', '--', f'sets/{n}/enter.gif'], cwd=HERE, capture_output=True, text=True).stdout.split()
        return out[-1] if out else datetime.date.today().isoformat()
    except Exception:
        return datetime.date.today().isoformat()
ADDED = {n: added(n) for n in names}
TAGS = {}
for t, g in GROUPS.items():
    for n in g:
        if n in names:
            TAGS[n] = sorted(set(GROUP_TAGS.get(t, []) + SET_TAGS.get(n, [])))
groups = [{'title': t, 'sets': [n for n in g if n in names]} for t, g in GROUPS.items()]
rest = [n for n in names if not any(n in g for g in GROUPS.values())]
if rest: groups.append({'title': 'Other', 'sets': rest})
(HERE / 'sets.js').write_text('const DESC = ' + json.dumps(DESC) + ';' + chr(10) + 'const PLAY = ' + json.dumps(PLAY) + ';' + chr(10) + 'const ADDED = ' + json.dumps(ADDED) + ';' + chr(10) + 'const TAGS = ' + json.dumps(TAGS) + ';' + chr(10) + 'const GROUPS = ' + json.dumps([g for g in groups if g['sets']]) + ';' + chr(10))  # .js, not .json: fetch() is blocked on file://
(HERE / 'clawd-md.js').write_text('const CLAWD_MD = ' + json.dumps((HERE / 'clawd.md').read_text(encoding='utf-8')) + ';' + chr(10), encoding='utf-8')  # inlined so the dialog works from file:// too
print(len(names), 'sets')
import re, time  # cache-bust: a visitor's browser must not mix a new index.html with an old sets.js
idx = HERE / 'index.html'
idx.write_text(re.sub(r'(sets\.js|clawd-md\.js)\?v=\w+', lambda m: f'{m.group(1)}?v={int(time.time())}', idx.read_text(encoding='utf-8')), encoding='utf-8')
