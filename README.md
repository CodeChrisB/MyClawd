# MyClawd

**Live site: https://codechrisb.github.io/MyClawd/**

Pixel-art animations of **Clawd**, the Claude Code mascot, for every moment of a Claude Code session.
Every set has an `enter`, one or more `loop`s and an `exit`, and all of them start and end on the same pose,
so any animation can follow any other without a jump.

<table>
<tr><td align="center"><img src="sets/thinking/full.gif" width="260"><br><sub>Thinking</sub></td><td align="center"><img src="sets/session-start/full.gif" width="260"><br><sub>Session start</sub></td><td align="center"><img src="sets/testing/full.gif" width="260"><br><sub>Testing</sub></td></tr>
<tr><td align="center"><img src="sets/git-pr/full.gif" width="260"><br><sub>Git pull request</sub></td><td align="center"><img src="sets/mode-auto/full.gif" width="260"><br><sub>Auto mode</sub></td><td align="center"><img src="sets/effort-max/full.gif" width="260"><br><sub>Max effort</sub></td></tr>
<tr><td align="center"><img src="sets/handoff/full.gif" width="260"><br><sub>Handoff</sub></td><td align="center"><img src="sets/model-switch/full.gif" width="260"><br><sub>Model switch</sub></td><td align="center"><img src="sets/compacting/full.gif" width="260"><br><sub>Compacting</sub></td></tr>
</table>

- **Browse and download:** the [site](https://codechrisb.github.io/MyClawd/) shows every set, with a zip per set and one for all of them.
- **Make your own:** clone the repo, open Claude Code in it and paste the prompt from the site's *Create your own* tab.
  Claude reads [`clawd.md`](clawd.md), asks what Clawd should be doing and draws the GIFs with Python and Pillow.

```
index.html      the site
sets/           the GIFs shown on the site
zips/           one zip per set + MyClawd-all.zip
toolkit/        drawing helpers and the example sets (used by clawd.md)
clawd.md        instructions for Claude
build.py        rebuilds sets/, zips/ and sets.js (maintainer only)
```
