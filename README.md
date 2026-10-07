# MyClawd

**Live site: https://codechrisb.github.io/MyClawd/**

Pixel-art animations of **Clawd**, the Claude Code mascot, for every moment of a Claude Code session.
Every set has an `enter`, one or more `loop`s and an `exit`, and all of them start and end on the same pose,
so any animation can follow any other without a jump.

<table>
<tr><td align="center"><img src="sets/browser/full.gif" width="300"><br><sub>Browser</sub></td><td align="center"><img src="sets/bash/full.gif" width="300"><br><sub>Bash</sub></td></tr>
<tr><td align="center"><img src="sets/resume/full.gif" width="300"><br><sub>Resume</sub></td><td align="center"><img src="sets/crash/full.gif" width="300"><br><sub>Crash</sub></td></tr>
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

---

Fan project, made for fun and not for profit. Not affiliated with, endorsed or sponsored by Anthropic. Clawd, Claude and Claude Code are Anthropic's names and marks ([trademark guidelines](https://www.anthropic.com/legal/trademark-guidelines)). If Anthropic wants anything changed or removed, open an issue.
