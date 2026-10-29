# Sora Jumping Medium

**Fact or rule:** Sora's jumping Medium attack is a broad diagonal Kingdom Key slash.

**Why:** K'von selected this motion during basic-attack design review. No further reason was provided.

## Build (October 29)

- Kvon: "Move on to the jumping medium" (after the Jumping Light v7 went into the game; v7 not yet called final, so its v1-v6 are kept). Same brief as the Light: design from his description with fighting-game references - Ky's GGST j.H (`design/references/ky_ggst_jh_reference.png`): a big one-handed slash from high behind down to low in front, both knees tucked high.
- `atk_jmed_vN` in build_sprite_pilot.py (attack section, not grounded, like atk_jlight). v1 (proposal, pending Kvon): lift / wind-up high over the rear shoulder, leaning back / overhead (smear) / hit = diagonal cut down in front, arm extended, body curled forward, lean -12 (smear, drawn 60 px left) / follow-through down past the legs (smear) / back to the apex tuck. Knees: tuck L (.24, lift .45) R (-.08, .30); front knee turned out like the approved Light (knee hint U .6 + cam .9 + up .45, hip_pivot -40) on overhead/hit/follow. Raised Keys tipped back/toward the camera and hands .16 lower to stay inside the top edge. Holds [2,3,3,3,5,7] = startup 8 / active 3 / recovery 12 (proposed). `atk_jmed2d_v1/`: Jumping_Medium_Sheet.png (apex first), Jumping_Medium_slow.gif, Hit_vs_Ky_jH.png.
