# Sora Jumping Light

**Fact or rule:** Sora's jumping Light attack is a quick midair Kingdom Key slash.

**Why:** K'von selected this motion during basic-attack design review. No further reason was provided.

## Build (October 29)

- Kvon: "Aerial attacks now"; for the Jumping Light: "Design it from my descriptions, but look up similar attacks in fighting games as reference for creating the animations". Reference found: Ky's GGST j.S (Dustloop image, saved as `design/references/ky_ggst_js_reference.png`; also saved his j.H as `ky_ggst_jh_reference.png` for the diagonal Jumping Medium later): a quick level slash at chest height, body leaning in, front knee tucked high, back leg trailing down.
- `atk_jlight_vN` in build_sprite_pilot.py (hurt/attack section, not grounded: hips where the jump drawings have them, the game moves him). v1 (proposal, pending Kvon): lift (from the approved apex tuck jump_apex_v4) / draw-back over the rear shoulder / slash = hit (level, hand forward at chest height, Ky's legs L (.30, lift .58) R (-.26, lift .22), lean -10, drawn 60 px left) / follow-through across the camera side / back to the apex tuck. Smears on slash + follow. Holds [2,3,3,4,5] = startup 5 / active 3 / recovery 9 (proposed). `atk_jlight2d_v1/`: Jumping_Light_Sheet.png (apex first), Jumping_Light_slow.gif, Slash_vs_Ky_jS.png.
