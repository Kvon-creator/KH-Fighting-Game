# Sora Crouching Medium

**Fact or rule:** Sora's crouching Medium attack is a wide low Kingdom Key sweep.

**Why:** K'von selected this motion during basic-attack design review. No further reason was provided.

**Active pose reference, October28:** Kvon: "Let's move on to the crouching medium. For the active pose, I'm thinking something similar to Ky's 2s in guilty gear strive." Supplied image saved as `design/references/ky_ggst_2s_active_kvon.png` (1145x499; earlier Dustloop 2S image: `ky_ggst_2s_reference.png`). Observed: deep low stance, back knee down (close to Sora's kneeling crouch), torso leaning forward and twisted, sword arm fully extended with the blade trailing back and low at the end of a wide horizontal sweep, free fist pulled in at the chest, a wide floor-level elliptical smear circling him. Reference only (not an extracted animation). Plan: active-pose candidates first, then the full animation, then the floor smear.

**Active-pose candidates, October28 (pending Kvon's pick):** `build_sprite_pilot.py -- atk_cmed_vN` (new `atk_cmed` recipe inside the Crouching Light section: builds approved atk_clight_v30 first - HURT swapped to it so the Light's old version branches don't leak in - then replaces the drawings). v1/v2 are review-only: A = Ky's pose (end of the sweep, sword arm reaching back past the hip, blade trailing behind, chest opened to the camera twist -20, pitch 24), B = A with small lean (pitch 12), C = mid-sweep with the blade low in front (twist 35). v1's A/B hand sat in front of the knee and the tip went under the floor; v2 fixed (hand U_ -.50, z .66/.70; offset_px +100). C's tip dips ~5 px under the floor. Sheet: `atk_cmed2d_v2/Active_Pose_Options.png`.
