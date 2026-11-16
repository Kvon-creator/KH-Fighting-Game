# Rigify Rigging (second tutorial Kvon shared)

**Fact or rule:** On November 16 Kvon pasted the transcript and six screenshots of a second rigging tutorial (Crashsune Academy's Blender character modeling series, the part before [[Weight_Painting_Tutorial]]; Blender 4.2.1 LTS, a low-poly anime girl; chapters seen: "Aligning our Meta Rig Skeleton" at 9:21, "Generating our Rigify Rig" at 13:43 of 19:29; the next video in its series is weight painting). Its point: understand bones by hand, but build real character rigs with **Rigify** - faster, correct names and bone orientations, and it adds IK/FK controls, control shapes and a layer menu.

**Bone basics shown on a test (a tall cube with ~20 loop cuts + two bones, screenshot 1):**
- In Front (Object Data > Viewport Display) to see bones through the mesh. Head = the bottom joint, tail = the top (N panel shows both).
- Parent: Object Mode, Alt+A deselect, click the mesh, then the armature last, Ctrl+P > Armature Deform > With Automatic Weights. Ctrl+Tab = Pose Mode.
- Pose Mode: A select all, **Alt+R** reset rotations. Edit Mode: **Shift+D** duplicate a bone, **Alt+P** clear its parent (it then stops following).
- Hierarchy: bones follow their parents, so a few parent bones move a lot of the body - organised, fewer keys, more natural.
- The tutorial recommends, for deeper theory: Joey Carlino's "Rigging for impatient people" and his rigging-for-beginners videos, and a video called "3D rigging is beautiful, here's how it works" (skeleton vs skinning vs controls).

**Rigify method:**
1. Enable the add-on: Edit > Preferences > Add-ons, search "rigify", tick it, Save Preferences. (Not checked yet for our Blender 5.2.)
2. Shift+A > Armature > Rigify Meta-Rigs > Basic > **Basic Human** - not the full Human meta-rig (fingers, face, eyelids, mouth: too much for a simple style). Turn on In Front.
3. Front view (numpad 1), S to scale it to the character (pivot: Median Point or Bounding Box Center; S X to widen), then **Ctrl+A > Apply All Transforms** (or Scale).
4. Edit Mode: move heads/tails onto the model's joints - elbow and knee on their edge loops, wrist, hand tip; turn on wireframe (Viewport Overlays > Geometry > Wireframe). Turn on **X-Axis Mirror** (top right) so the other side follows; if a side was moved without it, turn it on and nudge the bone to re-mirror.
5. Foot: the heel bone drives the foot roll - place its ends on the edges of the foot, toward the back (G X to slide along one axis). Head and neck: two neck bones, the head bone ends where the neck does. Alt+Z = X-ray, to select bones inside the mesh; H hides bones, Alt+H reveals.
6. Side view (3) and top view (7): joints sit inside the body (they rotate from there). **Keep a slight bend in the knees and elbows** - a perfectly straight leg leaves Blender (IK) unable to tell which way it bends. Delete bones you don't need (its breast bones; the screenshot caption: keep them if the character needs them).
7. Object Data > Rigify > **Generate Rig**: a new rig with control shapes (screenshot 6) appears over the meta-rig; turn on In Front, hide the meta-rig (eye icon) - **don't delete it**.
8. Bind: select every mesh piece of the character (Ctrl+box-select deselects; H checks nothing is left), Shift-click the generated rig last, Ctrl+P > With Automatic Weights. Pose Mode: arms and legs bend the right way; hands and feet stay put when the torso moves (IK on by default).
9. N panel > Rig Layers: hide what you don't need (Tweak, FK when using IK). Bone collections: Torso, Torso (Tweak), Arm.L/R (IK / FK / Tweak), Leg.L/R (IK / FK / Tweak), Root.
10. Fixing: unhide the meta-rig, edit it (e.g. the spine leaned forward and tilted the neck ~30 deg - move both spine bones together with G Y in X-ray, carefully), then Rigify > **Re-Generate Rig**. Any time.
11. Leftover problems (hair or chest pieces following the arm) are fixed by weight painting - see [[Weight_Painting_Tutorial]].

**How it applies here (my note):** Sora's game model keeps its PS2 rig (Japanese bone names, no Rigify); the posing scripts solve IK themselves, so Rigify doesn't change the current Sora work. It is the better route than the first tutorial's hand-built rig ([[Rigging_Basics_Tutorial]]) for any model with no rig yet - a from-scratch blockout or a new character. Its slight-bend rule matches a problem the posing work also has: straight limbs make the bend direction ambiguous.

**Why:** Kvon shared it as possibly useful, after asking me to remember the first tutorial; no further reason given.
