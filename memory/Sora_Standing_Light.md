# Sora Standing Light

**Fact or rule:** Sora's standing Light is a guard bash, like bunting with a baseball bat: he holds the Kingdom Key level across his body - LEFT fist on the handle inside the leading guard, RIGHT hand steadying the shaft behind it (swapped per Kvon; final v11, frame data 6/3/13) - and pushes it a short way forward so the Keyblade's guard hits the opponent. Fast, almost no wind-up, short range. This replaces the earlier "short Kingdom Key thrust".

**Why:** October 27, after Gemini's round-41 thrust concept, Kvon: "I think the wind-up makes it too slow for a light attack though and the range may be too long as well. Instead of the approved standing light attack, I want sora to hit the enemy with the guard of the keyblade with one hand while holding it stable across his body with the other hand. Think of punting with a baseball bat" (read as bunting).

**Direction decided, October 27:** Kvon chose "Blade back, guard leads": the Key is level at chest height with the guard in front toward the opponent and the blade pointing back behind him; right hand on the handle (the guard wraps that fist), left hand steadying the shaft further back; a short shove forward so the guard hits. Gemini's round-43 sheet mostly drew the opposite (blade toward the opponent), so it is built directly on the 3D model (`atk_slight_vN`).

**Hands swapped, October 27:** Kvon: "Specifically for this attack, swap which hand is holding the handle of the keyblade." LEFT fist on the handle inside the guard (leading), RIGHT hand steadying the shaft behind it. Built (v3+) by solving the right hand on the shaft and sliding the Key along its own line so its handle sits in the left fist; the return drawing hands it back to the right hand for the idle.

**Correction, October 27:** Kvon: "For the hitting part of the attack, he needs to extend the keyblade out in front of him. Right now, he just holds it up to his torso. His wrists also don't line up with the parts of the keyblade they are holding." v4: the bash pushes the guard out to arm's length (step in and lean), and the Key is placed from the solved fists - handle centre in the left fist, shaft through the right fist (v3 slid the Key so the right fist hung under the shaft and the left fist sat at the handle's end).

**Correction, October 27:** Kvon: "The angle of the keyblade should be oriented so the tip of the blade points slightly towards the player." v6: blade direction -U*.80 + V*.55 (about 35 deg toward the camera; v5 was about 18 deg); the right hand sits on the shaft along that line.

**Correction, October 27:** Kvon: "Increase the angle a little bit more, and fix the hand that is holding the shaft of the blade. Right now, the wrist is unnecessarily bent and doesn't line up with the part of the blade being held." v7: blade ~45 deg toward the camera (-U*.72 + V*.70); right (shaft) hand uses a straight wrist (`wrist_roll`), the roll searched per drawing so the fist's grip axis lines up with the shaft (v6 forced the idle's handle-grip hand angle, which bent the wrist).

**Correction, October 27:** Kvon: "Now slide the hand holding the shaft slightly further up. Bend the elbow and adjust the shoulder angle as needed." v9: the right hand sits .44 m from the left fist along the shaft (was .36); elbow/shoulder follow from the arm solve; straight-wrist grip as v8.

**Correction, October 27:** Kvon: "Bring his front foot in a little closer to his torso during the attack." v10: front foot at idle -.03 m on the set and idle -.05 m on the bash/recoil (v9 stepped it out +.12).

**Correction, October 27:** Kvon: "Bring the foot in a little further." v11: front foot idle -.07 (set) / -.10 (bash, recoil).
