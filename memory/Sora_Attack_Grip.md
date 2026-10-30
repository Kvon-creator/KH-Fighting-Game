# Sora attack grip: fist in the middle of the handle

**Fact or rule (Kvon, October 29):** "Remember the change for the down heavy animation I requested where Sora's hand was placed in the middle of the Keyblade handle? Apply that same change to every attack animation as well." On attacks, Sora's one-handed grip sits in the middle of the Kingdom Key's handle (between the guard's bars), not at the bottom against the lower bar.

**Why:** Kvon asked for it on the Crouching Heavy's thrust (atk_cheavy v7, `grip_slide` .10) and then made it the rule for all attacks.

**How to apply:**
- build_sprite_pilot.py `GRIP_MID_FROM` = {atk_clight: 31, atk_cmed: 24, atk_cheavy: 9, atk_jlight: 8, atk_jmed: 6}: from those versions on, every one-handed attack drawing (release >= .5, not the two-handed key_in_left grip) gets grip_slide .10 by default. Add each NEW attack to GRIP_MID_FROM from its first version.
- The last drawing of each attack (the crouch guard / jump tuck it hands back to) keeps the neutral grip so it matches crouch_hold / jump_air - the fist slides back down the handle as the attack settles.
- Not applied - Kvon, October 29: "Leave those attacks as they are": the Standing Light's guard-bash grip (Kvon-tuned, one hand on the shaft) and the two-handed Standing Medium / Heavy, whose two fists already fill the handle.
- In the game: Crouching Light v31, Crouching Medium v24, Crouching Heavy v9 and Jumping Light v8 replaced their game frames (offsets unchanged; tested headless, no errors). Jumping Medium v6 has it from the start. Related: [[Sora_Crouching_Heavy]], [[Sora_Jumping_Light]], [[Sora_Jumping_Medium]].
