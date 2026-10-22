# Godot executable and testing

**Fact or rule:** On October22 Kvon gave the Godot location: `C:\Users\kvong\Godot_v4.7.2-stable_win64.exe\Godot_v4.7.2-stable_win64.exe`. The same folder contains `Godot_v4.7.2-stable_win64_console.exe`; use the console one for command-line runs. `--version` reports 4.7.2.stable.official.ed1daf0bf, matching the project target. The Godot project is `D:\KH Fighting Game\KingdomArena` (main scene `scenes/demo.tscn`, arena floor y=600, viewport 1280x720).

- **Docs:** the VS Code godot-tools extension (geequlim 2.7.1) is installed, but no `godot_docs` agent tool exists. Kvon did not object to using the official online docs (docs.godotengine.org/en/stable = 4.7); check them before writing engine code.
- **Commands that work:**
  - `--headless --path . --import` imports new assets.
  - `--path . res://scenes/X.tscn -- --capture=<png>` runs a scene and saves a screenshot (scenes read `OS.get_cmdline_user_args()`).
  - `--write-movie <dir>/frame.png --fixed-fps 30 --quit-after N` records frames to verify an animation actually plays.

**Why:** User supplied the path; the Agent Setup rules require running and testing scene/script changes.
