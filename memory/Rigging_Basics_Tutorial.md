# Rigging Basics (tutorial Kvon shared)

**Fact or rule:** Kvon pasted the transcript of a beginner Blender rigging tutorial (Blender 4.1; author not named in the transcript) on November 16 and asked me to remember it. Its method, in order:

1. **Prepare the mesh:** object origin at the bottom centre (between the feet), so scaling keeps him on the floor; real-world size (the video scales a 3.58 m character to 1.9 m; our Sora is 1.6 m). A Mirror and a Subdivision Surface modifier can stay on - the rig still works.
2. **Add the armature at the centre:** Shift+S > Cursor to World Origin, front view (numpad 1), Shift+A > Armature > Single Bone. Object Data properties > Viewport Display > **In Front**, so bones show through the body.
3. **Place bones in Edit Mode** (Tab) - not Object Mode, so the object origin stays at the feet. A bone has a head, a body (selects all of it) and a tail. Keep centre-line bones on the Z axis (G then Z).
4. **Spine by extruding:** select a tail, E then Z: two torso bones (so he can bend in half), neck, head.
5. **Arm:** extrude from the base of the neck: shoulder (clavicle), upper arm, forearm, hand.
6. **Name one side with .L / .R** (F2, or Bone properties > name), e.g. `hip.L`, `shoulder.L`, `upper_arm.L`, `forearm.L`, `hand.L`. Without the suffix, X-Axis Mirror and Symmetrize do nothing. Then select everything > right click > **Symmetrize** to make the .R side, and turn on **X-Axis Mirror** so new extrusions happen on both sides (hip, thigh, shin, foot). Name every bone - the video left its legs as `hip.L.003`, which it says not to copy.
7. **Bind the mesh:** Object Mode, click the body, then the armature **last** (active, highlighted in the outliner), Ctrl+P > Armature Deform > **With Automatic Weights**. This adds an Armature modifier and one vertex group per bone (each bone's weights on the vertices near it).
8. **Test:** select the armature, Pose Mode (Ctrl+Tab), select a bone, R to rotate.
9. **Pinching at joints:** usually too little topology - a joint needs several edge loops, not one. To see it, enable the Armature modifier's "display in Edit Mode" and "on cage". The modifier's **Preserve Volume** checkbox helps only when there is enough topology.
10. **Root bone:** add a separate root bone that moves the whole character, and parent the hip bones to it (Edit Mode: select the hip bones, then the root last, Ctrl+P > Keep Offset). Without it, moving the base bone leaves the legs behind.

The video calls this rig very basic, not efficient (no IK, no control bones) - a starting point only.

**How it applies here (my note):** the game's Sora (PS2 model) is already rigged - 49 FK bones with Japanese names and L_/R_ prefixes (momo thigh, sune shin, ashi foot, kata shoulder, ude arm, te hand, mune chest, hara belly, kubi neck, atama head; Root > center > koshi). This method is for a model with no rig yet, e.g. the from-scratch blockouts or a future character. It does not cover the techniques the current animation work uses (IK solving, posing by aiming bones) - see [[Sora_Grab]] for those.

**Why:** Kvon asked me to remember it ("Here is the transcript from a video that I want you to remember"); no further reason given. Earlier the same day Kvon asked whether I could learn rigging and animation from tutorial videos - transcripts saved as notes like this are how it carries over between sessions.
