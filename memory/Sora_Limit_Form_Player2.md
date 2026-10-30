# Player 2: Sora's Limit Form model

**Fact or rule (Kvon, October 29):** `design/sprite_backups/sora_limit_form/` is Kvon's own model of Sora in his Limit Form (`Sora (Limit Form).dae` + texture000-004.png, ~2.5 MB; untracked in git - Kvon's files, don't commit or change them without asking). "Once I implement a player 2, I want you to copy all the current animations using this model."

**Why:** Player 2 will be Limit Form Sora, animated with the same moves as the current Sora.

**How to apply:**
- Wait until Kvon has implemented player 2 (Kvon does that part), then re-render every current animation with this model: the same pipeline (build_sprite_pilot.py -> render_2d_style.py -> stylize_2d_frames.py -> make_smears.py -> 384 px export), the same approved poses/versions, timings, DRAW_SHIFT / TALL_FEET values and smears.
- The current pipeline loads the KH2 Sora model; the Limit Form model will need its own import, rig/bone-name and Keyblade-grip check before the poses carry over - check that first and report any mismatch.
- "All the current animations" = the full set in KingdomArena/assets/sora at that time (movement, jump/dash, hurt set, all nine attacks).
