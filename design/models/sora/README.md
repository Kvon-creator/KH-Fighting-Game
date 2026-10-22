# Sora 3D-to-sprite experiment

Kvon chose3D animation rendered into2D sprites. Existing sprite assets and gameplay settings remain unchanged. Blender5.2.2 LTS was located and tested on this24GB-RAM computer; CPU modeling/export and transparent renders work without adding software. The VS Code Blender Development extension (jacqueslucke0.0.31) is installed; scripts run through the same Blender from the command line or with the extension's "Blender: Run Script".

**Experiments folder deleted (October21):** At Kvon's request, `design/models/sora/experiments/` was deleted. Weapon pipeline v1-v3 and the Hunyuan pilot remain recoverable from Git history (last present in commit 7cdbb40). Weapon v4 and character blockouts v1-v5 were never committed; they can be regenerated with the scripts in `blender_workflow/`:

- Weapon: `build_weapon_pilot.py`, `finalize_reference_crown.py`, `refine_reference_crown_v4.py`, `render_crown_v4_review.py` and helpers.
- Character: `build_character_blockout.py -- character_blockout_vN` (N=1-5). v5 is the latest from-scratch model: approved v2 proportions, almond eyes and blade hair after `design/references/sora_kh2_full_render.png`.

Run e.g. `blender --background --factory-startup --python blender_workflow/build_character_blockout.py -- character_blockout_v5`. Builders refuse to overwrite an existing version folder.

**Next direction:** Kvon proposed using a downloaded Sora model from The Models Resource instead of building from scratch. The site blocks automated access (Cloudflare challenge), so Kvon downloads it manually into `design/models/sora/downloads/`. Ripped game models should stay out of Git unless Kvon decides otherwise.

Requirements carried forward: KH2 outfit, smooth cel style and rigid far-hand same-shoulder Kingdom Key carry behind the head, with slight foreground tip. Render run-start, loop and stop from one fixed orthographic camera; review against approved idle/run-start and match the joins before aerial movement.
