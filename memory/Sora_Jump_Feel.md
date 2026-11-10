# Jump feel: less floaty, short / long jumps, fast fall after air hits (Kvon, November 6)

**Fact or rule:** Kvon: "the jump makes characters feel bit too floaty ... add the ability for short jumps and long jumps with the length of a jump being determined by how long the player holds the jump button. Also, there is too much end-lag when landing aerial attacks, making it impossible to continue a combo." Answers:
- **Air time ~15% shorter:** same 200 px height, JUMP_RISE_FRAMES 26 -> **22** (full jump 44 frames in the air, was 52). Accepted trade-off: a Jumping Heavy pressed at the very top is cut short by the landing (supersedes the October rule that it must finish from the top).
- **Smooth short/long jumps, first and second jump:** letting go of jump while rising = gravity x2 for the rest of the rise. Tap ~109 px, full ~209 px.
- **Combo fix = fast fall on hit:** once a jumping attack hits or is guarded, gravity x2.5 for the rest of the jump (reset on landing / second jump). Hitstun unchanged.
- **Correction (same day):** Kvon: "The fast fall effect on aerial attacks should only happen when hitting a grounded opponent." Only when the opponent was on the ground at contact (match.gd sets `hit_grounded`); air-to-air hits (jumping or juggled opponent) keep the normal fall. Guarded by a grounded opponent still counts.
- Launches / juggles keep the old gravity (LAUNCH_GRAVITY). The CPU holds jump 24 frames so its jump-ins stay full jumps.

**Why:** Kvon's request and answers; no further reasons given.

**Tested:** jH hitting at the jump's top: lands with 9 frames of hitstun left (was -2) - jH -> Light combos; jH -> Medium has a 1-frame gap from that top-height hit only. Lower jH hits land with 12-14 frames left.

**Bug found while testing (fixed):** take_hit called _end_moves() (which clears _air) before checking _air, so a jumping fighter hit air-to-air got the ground hit reaction and floated in place; now it is knocked up (hurt_air) as intended.

**Juggles (Kvon, November 6):** "when juggling an opponent in the air, the only attack that should trigger a fast fall attack is a jump heavy." Rule now: the fast fall starts when a jumping attack touches an opponent on the ground, OR a juggled opponent (hurt_air) with the Jumping Heavy. A jumping opponent who is not being juggled: no fast fall. match.gd sets `fast_fall_hit` (replaces hit_grounded). Tested: after the launcher, jL / jM juggles fall normally (land T76) and jH fast-falls (T69); grounded jH is unchanged (T42).
**Bug fixed with it:** on the frame a jumping attack started, the fast-fall check ran before the new attack cleared the previous attack's contact, so a grounded hit (e.g. the launcher) followed by a jump-in fast-fell at once. Contact flags are now cleared when the air attack starts.
