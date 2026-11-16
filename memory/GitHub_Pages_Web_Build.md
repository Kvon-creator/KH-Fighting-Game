# GitHub Pages Web Build

**Fact or rule:** Kvon (November 16) wants an index.html for a GitHub Pages link: a **playable browser build** of the game, kept in **`docs/` on main**. Kvon explicitly authorized creating the protected `KingdomArena/export_presets.cfg` for this, holding one "Web" preset (single-threaded, export path `../docs/index.html`). Other protected-file rules are unchanged.
- **Re-export after game changes** (the site does not update by itself): `Godot_v4.7.2-stable_win64_console.exe --headless --path KingdomArena --export-release "Web" "d:/KH Fighting Game/docs/index.html"`, then commit and push `docs/`. `docs/.nojekyll` stops GitHub's Jekyll step.
- Why single-threaded: threads need COOP/COEP server headers, which GitHub Pages can't send; Godot's docs call single-threaded "the preferred and now default way" for web. Web needs the Compatibility renderer - the project already uses it.
- Export templates for 4.7.2 (web included) were already installed in `%APPDATA%\Godot\export_templates\4.7.2.stable` - nothing was installed.
- Size (Nov 16): index.wasm 39.5 MB, index.pck 10.3 MB (GitHub's per-file limit is 100 MB, warning at 50 MB).
- Tested: served `docs/` locally, headless Chrome through the DevTools protocol (scratch script, waits ~20 s for the engine to start): menu shows, keyboard picks Training, the match draws with no console errors.
- Browser limits from the docs: a gamepad is only detected after one of its buttons is pressed; browser audio needs a click or key press first (the game has no audio yet).
- **Kvon's step:** GitHub > the repository > Settings > Pages > Deploy from a branch > `main` / `/docs` > Save. The site is then https://kvon-creator.github.io/KH-Fighting-Game/ (free Pages needs a public repository). `gh` is not installed here, so I can't turn it on.

**Why:** Kvon's request, to have a shareable link.
