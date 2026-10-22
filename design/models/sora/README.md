# Sora 3D-to-sprite experiment

Kvon chose3D animation rendered into2D sprites. Existing sprite assets and gameplay settings remain unchanged. Blender5.2.2 LTS was located and tested on this24GB-RAM computer; CPU modeling/export and transparent renders work without adding software. The VS Code Blender Development extension (jacqueslucke0.0.31) is installed; scripts run through the same Blender from the command line or with the extension's "Blender: Run Script".

**Experiments folder deleted (October21):** At Kvon's request, `design/models/sora/experiments/` was deleted. Weapon pipeline v1-v3 and the Hunyuan pilot remain recoverable from Git history (last present in commit 7cdbb40). Weapon v4 and character blockouts v1-v5 were never committed; they can be regenerated with the scripts in `blender_workflow/`:

- Weapon: `build_weapon_pilot.py`, `finalize_reference_crown.py`, `refine_reference_crown_v4.py`, `render_crown_v4_review.py` and helpers.
- Character: `build_character_blockout.py -- character_blockout_vN` (N=1-5). v5 is the latest from-scratch model: approved v2 proportions, almond eyes and blade hair after `design/references/sora_kh2_full_render.png`.

Run e.g. `blender --background --factory-startup --python blender_workflow/build_character_blockout.py -- character_blockout_v5`. Builders refuse to overwrite an existing version folder.

**Downloaded models (current direction):** Kvon downloaded models from The Models Resource into each character's `downloads/` folder and approved pushing them to GitHub. Sora's KH2 model `downloads/p_ex150.fbx` is rigged (49 bones, T-pose); `downloads/Kingdom Key/` holds the weapon. [inspect_downloaded_models.py](blender_workflow/inspect_downloaded_models.py) imports every OBJ/FBX read-only; results and front/side/back previews are in [../model_inspection_v1/](../model_inspection_v1/Inspection_Report.json).

**Sprite pilot (October21):** [build_sprite_pilot.py](blender_workflow/build_sprite_pilot.py) turns the downloaded model into one sprite frame. It scales Sora to 1.6 m and welds the rip's split vertices. The Kingdom Key is re-centered on its grip with the loose keychain links removed, then attached to his `R_buki` weapon bone. Each pose uses analytic two-bone aiming toward hand/foot targets. Original textures get a two-tone cel ramp, a heavy outer Freestyle contour and faint interior lines. One fixed orthographic camera at yaw -40 is framed like the approved idle: 512px canvas, soles at y=470, plus a 128px export.

- **Current:** [sprite_pilot_v4](sprite_pilot_v4/Approved_Idle_vs_Pilot.png).
- **Earlier revisions (kept):** v1 used IK constraints (twisted legs) and drew every rip seam. v2 cleaned the lines but stood narrow and upright. v3 widened the stance but stayed too dark from dense interior outlines.
- **Not done:** the pose is approximate and the left hand only roughly reaches the handle. No animation, no final approval.

**Idle breathing loop (October21):** `build_sprite_pilot.py -- idle_loop_vN` renders a refined pose: deeper, wider crouch, lower and more forward grip, flatter blade. The left hand's weapon socket is placed on the handle, landing within about 2 cm. Packaging: `python package_idle_loop.py idle_loop_vN`.

- **Loop:** 10 frames with the approved idle's timing (1480 ms). The body sinks and leans with the breath; hands, Key and head trail by 12% of a cycle.
- **Key placement:** placed rigidly at the grip every frame, because a bone-parented Key wobbled as the re-solved hand twisted.
- **Current:** [idle_loop_v6](idle_loop_v6/Approved_vs_3D_idle.gif). Per Kvon, the Keyblade teeth face up, and each wrist is twisted about its forearm so the palm wraps the handle; twist and finger curl are searched per hand.
- **v5:** After Kvon said the Keyblade was held the wrong way, v4 turns the guard face toward the camera with the teeth down and puts the fist inside the guard. v5 adds an automatic finger curl (partial; the palms still need a wrist roll).
- **v3:** the breathing Kvon approved, with the wrong grip orientation. It includes 512/128px frames, a 5x2 sheet, looping GIFs, a keyed `.blend` and `Package_QA.json` (GIF timings, loop flag, soles at y=470-471, 10 distinct frames).
- **Earlier:** v2 is kept and repeats frames in a ping-pong, from a symmetric breath with no lag. v1 was an aborted first render.
- **Not done:** not tested in Godot, and not user-approved.

Requirements carried forward: KH2 outfit, smooth cel style and rigid far-hand same-shoulder Kingdom Key carry behind the head, with slight foreground tip. Render run-start, loop and stop from one fixed orthographic camera; review against approved idle/run-start and match the joins before aerial movement.
