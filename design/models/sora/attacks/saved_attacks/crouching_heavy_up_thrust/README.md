# Saved attack: Crouching Heavy "up thrust" (after Sora's SSBU up smash)

Sora's crouching Heavy launcher from October 29 to November 6, 2026. Kvon replaced it with the original grounded
upward-swing concept because its hitbox made it very hard to combo into, and asked to keep this version for future
reference alongside other attacks.

- **Motion:** from the kneel he gathers low with the Key upright in both hands, rises, then thrusts it straight up
  overhead one-handed. He stands tall on his toes with his back to the viewer (turned 120 deg) and his free arm down
  behind him. He holds it with the back knee lifted, tips the Key back over his shoulder and settles into the crouch
  guard. Reference: `design/references/Sora_Up_Smash.gif`.
- **Source:** `build_sprite_pilot.py -- atk_cheavy_v9` (the recipe stays in the script, so it can be re-rendered or
  reused), then `render_2d_style.py -- atk_cheavy_v9 atk_cheavy2d_v9`, `stylize_2d_frames.py`, `make_smears.py`.
  v9 = v8 (Kvon's final) rebuilt with the mid-handle grip rule.
- **Files:** `game_384/` + `game_smear_384/` are the exact in-game frames (384 x 576). `frames_512/` +
  `frames_smear_512/` are the 512 x 768 2D renders. The sheet, slow GIF and `Sequence_vs_UpSmash.png` are v8's review
  images (v9 is the same pose apart from the grip).
- **Game data when it was in the game:** holds [6, 5, 4, 8, 5, 4, 5] = startup 11, active 4 (drawing 2), recovery 22.
  TALL_FEET (192, 546). No DRAW_SHIFT.
- **Hitbox** (drawing 2, 384-scale frame px): Rect2(216, 78, 152, 296), i.e. from 172 px above his feet up to 468 px.
  make_boxes.py gave it FORWARD_PX 110 and SWEEP_FROM 0. See `hitbox_preview_drawing2.png`.
