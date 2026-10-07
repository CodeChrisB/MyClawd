# MyClawd

Pixel-art animations of **Clawd**, the Claude Code mascot, for every moment of a Claude Code session.
Every set has an `enter`, one or more `loop`s and an `exit`, and all of them start and end on the same pose,
so any animation can follow any other without a jump.

- **Browse and download:** the site (GitHub Pages) shows every set, with a zip per set and one for all of them.
- **Make your own:** clone the repo, open Claude Code in it and paste the prompt from the site's *Clawd ur way* tab.
  Claude reads [`clawd.md`](clawd.md), asks what Clawd should be doing and draws the GIFs with Python and Pillow.

```
index.html      the site
sets/           the GIFs shown on the site
zips/           one zip per set + MyClawd-all.zip
toolkit/        drawing helpers and the example sets (used by clawd.md)
clawd.md        instructions for Claude
build.py        rebuilds sets/, zips/ and sets.js (maintainer only)
```
