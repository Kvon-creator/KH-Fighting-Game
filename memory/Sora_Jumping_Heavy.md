# Sora Jumping Heavy

**Fact or rule (October 29, replaces the earlier note):** Sora's jumping Heavy is an **overhead slash with both hands**, after Trunks' jumping heavy in Dragon Ball FighterZ - Kvon: "We'll do an overhead slash instead. Use Trunks' jump heavy and DBFZ as a reference"; grip "Two hands". This supersedes the earlier "wide midair spinning Kingdom Key slash" note; impact and knockdown properties remain undecided.

**Why:** Kvon changed the move when asked about the spin's axis/grip/reference. No further reason was provided.

## Build

- Reference: Dustloop's DBFZ Trunks j.H image, saved as `design/references/trunks_dbfz_jh_reference.png` - one huge vertical two-handed arc from high over his head down past his feet, body hunched over the sword, legs tucked back, thick crescent smear.
- `atk_jheavy_vN` in build_sprite_pilot.py (attack section, not grounded). Two-handed grip like the Standing Heavy (release 0, left hand on the handle, l_elbow_hint V .75 + U .10 - .65 z); the last drawing (jump tuck) back to the one-handed carry. In GRIP_MID_FROM from v1 (the rule only touches one-handed drawings).
- v1 (proposal, pending Kvon): lift / wind-up (Key high over and behind his head, back arched, knees up) / overhead (smear) / chop = hit (straight down in front past his feet, body curled forward, legs swung back, lean -14; smear from the wind-up over the top) / low / rise / jump tuck. Lift/overhead Keys tipped toward the camera and hands lowered, low Key tipped forward, hit/low drawn 20 px up, to stay in frame. Holds [3,5,3,4,7,6,5] = startup 11 / active 4 / recovery 18 (proposed). `atk_jheavy2d_v1/`: Jumping_Heavy_Sheet.png (labeled 2 rows), Jumping_Heavy_slow.gif, Hit_vs_Trunks_jH.png.
- Kvon: "In pose 5, angle the tip of the blade up more" (sheet cell 5 = the chop, drawing 3). v2: chop blade_dir from straight down (z -1.0) to U .75 + V .15 - .65 z (tip out toward the opponent); drawn 70 px left so the tip fits. `atk_jheavy2d_v2/`.
