# RAPP Brainstem — The Interactive Walkthrough

**Run it:** https://kody-w.github.io/rapp-brainstem-walkthrough/

The real brainstem UI — byte-identical `index.html` from the product — running
**"The First Interview"**, its 14-step guided tour, entirely in your browser.
No server, no Python, no GitHub account, no dependencies: one static HTML file
with a small simulator shim that answers the brainstem's own API calls
(`/chat`, `/chat/stream`, `/agents`, the RAR registry) from canned, in-browser
state. Memory persists in `localStorage`; append `?reset` to start fresh.

Everything in the tour works for real against the simulation:

- **Memory** — introduce yourself, clear the chat, and it still knows you
- **Agent surgery** — export, delete, and drag-drop-restore a live agent file
- **Honesty** — ask for what it can no longer do and watch it say so
- **The registry** — install `@rapp/learn_new` (SHA-256 verified in-page)
- **Creation** — describe an agent in plain words; the file is written and hot-loaded

When trainees finish, the real thing is one line away:

```bash
curl -fsSL https://kody-w.github.io/rapp-installer/install.sh | bash
```

## Also here: the produced video

[**video.html**](https://kody-w.github.io/rapp-brainstem-walkthrough/video.html) —
all 14 steps of the [full RAPP guide](https://github.com/kody-w/rapp-installer/blob/main/skill.md)
(clean machine → Teams/M365 Copilot) as one produced walkthrough video with
seekable chapters, filmed on real surfaces with [RAPP Video](https://kody-w.github.io/rapp-video/).

## Rebuilding the page

```bash
python3 tools/build.py   # stock brainstem index.html + tools/sim_shim.js → index.html
```

The build injects the shim as the first `<script>` after `<body>` and embeds the
preinstalled agent files plus a 10-agent RAR catalog subset (real bytes, digests
recomputed to match). The stock UI is never edited.

---

<sub>RAPP and the RAPP family of names are trademarks of the RAPP project. Code is
MIT-licensed; see [DISCLAIMER.md](DISCLAIMER.md).</sub>
