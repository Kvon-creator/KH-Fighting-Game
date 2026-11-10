# Sora Grab (throw)

**Fact or rule:** Sora gets a grab attack before special moves (Kvon, November 10). Animation idea (Kvon's words): Sora grabs the opponent's torso with his non-sword (left) arm, spins around once with the opponent in hand, then after one full rotation throws the opponent's body up in the air, prepares a strike with the Keyblade, and sends the opponent flying backward.

**Answers so far (asked one at a time):**
- Input: **Medium + Heavy pressed together** (I + O on the keyboard, Triangle + Circle on the DualSense).
- Escape: **yes, by grabbing back** - the grabbed fighter presses Medium + Heavy within a short window, both push apart, no damage.
- Where: **ground and air** (a ground grab on grounded opponents, plus an air grab on opponents also in the air).
- Air grab ending: **no Keyblade strike - Sora tosses the opponent down to the ground.** Reference: Magik's air throw from Marvel Tokon (no reference file in design/references yet).
- Ground grab damage: **1200 total**.
- After the Keyblade strike: **knockdown** (existing knockdown, then get up; no follow-up combo).
- Grabbed opponent: **new dedicated "being held" poses** rendered in the same Blender pipeline so both bodies line up through the spin (not reused hurt drawings).
- Pose planning: **Gemini concept sheet, combined with researching the Magik (Marvel Tokon) air throw reference.**

**Research (November 10):** The web guides I checked (tokonfightingsouls.net, tokonguide.com, altarofgaming.com) don't describe the look of Magik's air throw. tokon.gg returned 403. They only give the general Tokon throw rules: M + H, usable in the air, unblockable, short range, can't throw an opponent in hitstun/blockstun, escaped by entering the same throw input at once, the ground version moves forward a bit when not point-blank, a corner throw causes a Wall Break. Asked Kvon for a clip of the air throw (design/references/) before drawing the air grab.

**Reference added (November 10):** `design/references/Magik Air Throw.gif` (564x532, 164 frames at 40 ms; cinematic close camera, heavy effects). My reading: 0-34 both airborne, Magik catches the opponent chest-to-chest / 40-80 camera zooms in, she twists around with them (gold ring, red portal behind) / 84-88 she hauls them up over her head / 90-134 she alone, body turning through the follow-through, the opponent off-screen / 138 the opponent falls low on the far side while she reaches back / 141-146 she brings her big sword down toward them. Kvon's answer: **toss down only** - grab, twist with them, haul them overhead, hurl them down to the ground. No Keyblade swing (Magik's final sword swing is not copied); the Keyblade stays in his right hand out of the way.
- Air grab damage: **1200, existing knockdown** on landing (same as the ground grab).
- Targets (Kvon): **the ground grab only catches grounded opponents and the air grab only catches airborne opponents** - neither works on the other.
- **Gemini round 55** (ground grab concept, fresh chat, battle idle reference only, prompt GRAB_CONCEPT_ROUND_55.txt; review in `gemini_walk_review/round_55/REVIEW.md`): grab, toss, wind-up and strike read well, but the spin doesn't: pose 2 is almost the same as pose 1 and the opponent stays on Sora's right throughout. Kvon chose option 1 (Gemini spin-only correction in a fresh chat). Tool fix: Gemini's composer previews lost their alt text, so gemini_cdp.mjs previewsReady also counts blob: thumbnails (an earlier failed check had attached the reference twice; a new chat cleared it).
- My proposed values (shown to Kvon November 10; he said "Start the Gemini concept sheet" without changing them): close range only, ground version steps in a little; 7-frame startup; 10-frame escape window; no grabbing an opponent in hitstun/blockstun or invincible; a miss = short open-hand reach, ~25 frames of punishable recovery; no corner effect. Not yet confirmed: grab range/startup, whiff animation.

**Why:** Kvon's design; no further reason given.
- **Rounds 56-57 (spin corrections, fresh chats):** 56 (idle + round 55 sheet) mostly copied round 55. 57 (idle only, "hammer throw ... travel AROUND Sora") has Sora turning front -> back -> front and the opponent off the floor and horizontal, but the opponent still stays on his right (only the legs swing to the left in pose 4). Reviews are in each round folder. Next step proposed to Kvon: build the spin path in Blender from 57's body poses + 55's strike.
