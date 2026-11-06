# Sora attack cancels (Kvon, November 5)

**Fact or rule:** Kvon: "I want to implement animation cancels with Sora's actions." Answers:
- Cancel types: **chain into stronger** (Light -> Medium -> Heavy) and **jump cancel**. Not dash cancels, not same-button repeats.
- Chains need **contact - hit or guard** - and are allowed from the hit until the attack ends; a whiffed attack can't be cancelled.
- Chain routes: **standing and crouching mix, skipping allowed** (L -> M, L -> H, M -> H; holding down picks the crouching version, so L -> cH launcher works). Air chain the same way: jL -> jM / jH, jM -> jH.
- Jump cancel: **ground attacks only on hit** (not on guard); **air attacks on hit or guard** (into the second jump - so only while it is unused).

**Why:** Kvon's answers; no further reasons given.

## Air dash -> air attack cancel (Kvon, November 6)
**Fact or rule:** Kvon: "I want to be able to cancel an air dash into a normal aerial attack." Answers: **both** air dashes (forward and back), **from the burst on** (not during the forward dash's tuck or the back dash's push = first drawing); ~~keeps the dash's end momentum (AIR_DASH_CARRY)~~ - **corrected same day:** Kvon: "canceling Sora's air dash into an attack makes him lose his momentum ... I want the momentum to be maintained into the attack." Now he **keeps the dash's current speed (e.g. 16 px/frame) for the whole attack**, then it fades as usual (AIR_DRAG); he falls during it. Not tied to hit or guard.
**Why:** Kvon's answers; no further reasons given.
**Built:** fighter.gd `_dash_cancellable()` / `_end_air_dash()`. Tested: Light 8 frames into the forward dash cancels (vx 6.3 carried); Light in the tuck ignored; back dash: Light in the push ignored, Medium on the hop cancels.

## Dash button R1 (Kvon, November 6)
**Fact or rule:** Kvon first asked for Light + Medium (+ direction) = dash with R1 as a shortcut, then the same day: "Nevermind about Light and Medium being the dash input. Instead, keep R1 as a dedicated shortcut for dashing." **Light + Medium is NOT a dash** (it is just an attack). **R1 = dash:** with back held = back-dash (ground or air); otherwise (forward or no direction) = forward dash - the glide on the ground (glides on while R1 or forward is held), the air dash in the air. Same limits as double-tap dashes (once per jump, not during an air attack).
**Why:** Kvon changed his mind; no reason given.
**Built/tested:** fighter.gd input "dash"; match.gd `_pad_input` R1; test flag `--r1-demo-at=N[,N]`. Tested ground neutral / held / back, air neutral / back, L+M = Medium.
