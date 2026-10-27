# Sora Standing Medium

**Fact or rule:** Sora's standing Medium attack is a horizontal Kingdom Key slash across his body.

**Why:** K'von selected this motion during basic-attack design review. No further reason was provided.

**Direction, October 27 (after Gemini round 44):** Kvon: keep Gemini's poses, including the ones with the Keyblade raised over his shoulder, and "create more poses that smoothly transition from his idle pose to those points"; have Sora "throw his weight into the attack by having him turn his torso more and have other affected body parts follow in a realistic way"; add smear effects on the Keyblade to show motion. He asked whether Blender has a downloadable smear tool.
**Why:** Kvon's review of round 44.

**Smears, October 27:** Kvon chose "Build my own": no download (the SMEAR extension would install outside the project and was reported to error on Blender 5.2.1 with a rigged character). Generate the smear from the Keyblade's actual swept arc between drawings with Blender's built-in tools, rendered as a separate effect layer (the chart's rule: effects separate from body frames), timed in Godot.
**Why:** Kvon's choice.

**Correction, October 27:** Kvon: "The wind-up of him putting the keyblade above his shoulder doesn't match that of the poses gemini gave. There is also no smear effect like I asked for." Gemini's poses 1-2: both hands up by his REAR shoulder (beside his head, screen-left side), the blade angled UP and FORWARD over his head like a batter's stance (v2 pointed it up and back). Smears must come with the attack, not be deferred.
**Why:** Kvon's correction.

**Reference, October 27:** Kvon: "I think a good reference would be Ekko's standing heavy attack in 2XKO." Saved the 2XKO wiki's 5H image (screenshot of the public wiki image) as `design/references/ekko_2xko_5h_reference.png`; wiki frame data 13 startup / 3 active / 21 recovery ("The mandatory batter normal"). Impact frame: deep lunge (front knee bent far forward, back leg straight behind, heel up), body leaning hard into the swing, torso turned through, both arms extended, weapon level and slightly up; the smear is a thick SOLID crescent from low behind him up to the weapon, widest at the weapon, tapering to a point at the start. v4 follows this: lunge impact, tapered solid crescents (impact smear spans windup -> begin -> impact), raised poses lowered (v3 ran off the top).

**Correction, October 27:** Kvon: "Where is Sora's arm that isn't holding the keyblade in poses 3-8?" Cause: v5 placed the hands toward his right (camera) side; once the body turned, the left hand could not reach the handle (grip error up to .28 m) and the left arm hid behind the body. v6: hands toward his midline, the left shoulder may reach (`shoulder_reach`), check grip_error_L in the report (< ~.03 m).

**Correction, October 27:** Kvon: "The arms on poses 6 and 7 still looked messed up. For example, 7's pose features the arms being completely behind Sora's body while holding the keyblade." (sheet numbering: 6 = slash start, 7 = impact.) Cause: in those drawings his chest faced AWAY from the camera (turn 45 / 15 plus twist), so the arms reached forward on the far side of the body. v10: chest toward the camera through the swing (like Ekko's frame and his idle): turn 20 / -20 / -40 for slash start / impact / follow-through, arms in front of the body; feet keep the lunge.

**Correction, October 27:** Kvon: "In the attack animation, it would be best for his body to follow the keyblade as it swings. Think of someone swinging a bat." v13: batter's kinetic chain - hips lead into the swing (shoulders lag), shoulders/arms whip through to impact, and the body keeps turning with the Key after the hit: an extra "wrap" drawing (Key sweeping on around in front), then the follow-through with hips/chest fully round, back foot pivoting onto its toe with the knee turned in, front leg straighter, arms wrapped over the front shoulder.

**Correction, October 27:** Kvon: "Bring his legs in closer to almost meet under his torso and fully extend the keyblade for max range during the attack." v14: feet almost together under his torso from the wind-up through the recovery (raised pose halfway); impact arms straight at shoulder height with the blade pointing straight at the opponent. Full reach exceeds the 512 frame, so those drawings are shifted left inside the frame (`offset_px`, recorded in key_track as `offset_world`) and Godot must shift the sprite back by the same amount per drawing (the chart forbids shrinking Sora to fit attacks); make_smears.py moves earlier drawings' Key positions into the current drawing's frame.
