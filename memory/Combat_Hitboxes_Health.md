# Combat: hitboxes, hurtboxes, health (first pass)

**Fact or rule (Kvon, October 29):** "Implement hitboxes and hurtboxes for all of Sora's animations, then add a health bar on both sides of the screen at the top." Kvon's answers:
- Target until player 2 exists: **a training dummy Sora** on the right that doesn't move; when hit it plays the hurt animation and its health (right bar) drops. Replaced by the real player 2 later.
- Health **10000** each; damage **Light 300 / Medium 500 / Heavy 800** (crouching and jumping versions use their strength's number).
- Boxes **hidden by default, toggled with F1** (red = hitbox, blue = hurtbox).
- Health bars in a **Kingdom Hearts style** (green HP fill, dark frame), top left (Sora) and top right (dummy / player 2).

**Why:** Kvon picked these when asked; no further reason given.

## Built (October 29)
- Boxes: `design/models/sora/blender_workflow/make_boxes.py` generates `KingdomArena/scripts/sora_boxes.gd` (const HURT / HIT, keyed "<asset folder>/<file>", Rect2 in the drawing's 384-scale frame pixels) + `design/models/sora/boxes_preview/` overlays. **Re-run it whenever a drawing in the game changes or an attack is added** (add the attack to ATTACKS: game anim, 3D version, active drawing(s), 'key'/'guard', grip slide).
  - Hurtboxes: silhouette minus the Key's silver pixels, opened (9 px) to drop thin parts, 3 horizontal bands, grown 3 px - every drawing (166).
  - Hitboxes: the Key's line swept over the last half of the swing into the active drawing (Crouching Medium: the whole swing - its last half trails behind him; Jumping Medium: last fifth - the spin comes from high overhead); Standing Light: around the guard/left fist. Active drawings: L1 / M5 / H4 / cL2 / cM4 / cH2 / jL2 / jM3 / jH3.
- sora_move_test.gd: `_physics_process` = `_sora_step` (the old body) + `_dummy_step` + `_check_hits` + `_drain_lost_hp` + redraws. Dummy = second AnimatedSprite2D sharing Sora's SpriteFrames, x 860, scale.x -1 (mirrored, feet stay on its position); idle loop, `hurt_ground` when hit. `_boxes()` maps a drawing's boxes to world (sprite offset incl. DRAW_SHIFT/TALL_FEET, mirrored for scale.x < 0). One hit per attack (`_attack_hit` reset when an attack's drawing 0 shows). Damage by name suffix light/medium/heavy. F1 toggles the box view (`--show-boxes` launch flag for recordings). R also refills both bars. Bars: HUD Control drawn in `_draw_bars` (dark frame + light rim, green with bright top/dark bottom stripes, red trailing "just lost" part that waits 30 frames then drains 120 HP/frame), outer-edge anchored, name + HP number above; Title/Controls labels moved down 40 px.
- Tested: every attack hits on its first active frame for its damage (M 9, H 13, L 6, cL 5, cM 13, cH 11 up close, jH, jM, jL falling onto him); existing demos (knockdown, hit, glide, double jump, air dash, back-dash) run with no errors; recording checked by eye.
- Not done (not asked): no pushboxes (Sora can walk through the dummy), no hitstop/hitstun rules, the dummy doesn't attack so Sora's bar never drops, the launcher doesn't launch.

## Hitstun, hit-freeze, launcher, pushing (Kvon, October 29)
- Kvon: "Add Hitstun and hit-freeze, and add the launcher. When two hurtboxes collide, one character shouldn't be able to walk through the other, but instead push each other across the scene as they move."
- Answers: hit-freeze **L 11 / M 13 / H 16** game frames (both fighters freeze); hitstun **L 15 / M 19 / H 23** (the hurt animation is stretched to it); launcher = **launch + air juggle** (the dummy flies high; while airborne every hit pops it up a little; on landing it falls into the knockdown and gets up). Sora still doesn't jump by himself on the launcher.
- Pushing uses the **hurtboxes** themselves (Kvon's wording), not separate pushboxes.
