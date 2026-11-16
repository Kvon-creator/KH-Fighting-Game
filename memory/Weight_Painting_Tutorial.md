# Weight Painting (third tutorial Kvon shared)

**Fact or rule:** On November 16 Kvon shared "How To Weight Paint Your Characters! Blender 3D Character Modeling Tutorial - Part 10 [2024]" by Crashsune Academy (https://www.youtube.com/watch?v=Xooago2F8h8, 24:29) - the next part of the same series as [[Rigify_Rigging_Tutorial]] (same character, Rigify rig). Kvon's message had only a chapter summary; I read the video's full English captions. I could not see its frames (see the tool note at the end). Its method:

**What weights are**
- Weight Paint mode: click the mesh in Object Mode, then Ctrl+Tab > Weight Paint (or the mode menu).
- A **vertex group** = a container of vertices with a weight each; binding with automatic weights to a Rigify rig makes one per deform bone (`DEF-...`; the head is `DEF-spine.006`, the chest `DEF-spine.002`). Switch the shown group at the top of the viewport or Object Data > Vertex Groups (arrow keys step through them).
- Colours show the active group's weight: **red = 1 (100%, follows the bone fully), blue = 0 (not at all)**, green about 0.5.

**Tools and settings** (N panel > Tool, same as the Properties editor)
- **Draw**: Weight = the value painted (Ctrl+F); **Strength = opacity** (Shift+F); Radius = brush size (F). E.g. weight 0 at strength 0.5 moves halfway to 0.
- **Gradient**: drag a line for a smooth falloff between two weights (use an orthographic view; lower strength for a softer blend). **Blur** softens transitions.
- Low-poly models: set the Draw brush **falloff to the flat (constant) preset** - every click paints exactly the weight, no soft edge.
- **X Symmetry**: mirrors the paint to the matching bone's group on the other side (Rigify bones are symmetric).
- **Front Faces Only** off + **Falloff Shape: Projected** (not Sphere) = paint straight through the mesh (e.g. all round a cylinder). Turn both back after.
- X-ray (Alt+Z) does not work in Rendered shading - use Solid; to keep textures, the shading dropdown > Flat + Texture.
- **Auto Normalize** (Tool > Options): **always turn it on** - it is off by default. With it, a vertex's weights over all bones always add up to 100%: painting weight onto one bone takes it from the others. Without it, a vertex can end up over 100% across several bones.
- Face / vertex selection masking (1 / 2) limits painting to selected faces or vertices (not needed on a low-poly model).

**Fixing stray movement (hair and collar moved with the hand)**
1. Hair mesh, Weight Paint, active group `DEF-spine.006` (head), Auto Normalize on, Gradient with weight 1 and strength 1, drag a few times: the whole hair 100% on the head - Auto Normalize strips the arm's weight from it.
2. Torso mesh: step through the groups to find the bone already holding most of the collar (`DEF-spine.002`), gradient it to 100%; optionally a lower-strength gradient for a little `DEF-spine.001` blend.
3. Test: Object Mode, the rig, Pose Mode, move the hand.

**Checking weights bone by bone:** rig > Object Data > Bone Collections > star (isolate) the **DEF** collection to show the deform bones; click the rig, Shift-click the mesh, Ctrl+Tab > Weight Paint; **Alt+click a bone** to show its group. R / G / S pose bones in this mode (not Rigify's DEF bones).

**Adding a bone for secondary motion** (hair sway, a tail, ears)
1. Rig, Edit Mode, Shift+A: a new bone. Object Data > Bone Collections > + > rename it "hair" > **Assign** the bone to it.
2. Place it: the **head (where it rotates from) at the root of the hair, the tail at the tip** (front view G Z, R, S; side view G Y). F2 rename it (e.g. `hair_front`); optional colour in Bone > Viewport Display.
3. Bind: click the hair mesh, Shift-click the rig, Ctrl+P > Armature Deform **With Empty Groups** - adds an empty vertex group named after the bone (automatic weights "sometimes won't do what you want").
4. Weight Paint that group: Draw, weight 1, strength 1, on the hair's vertices.
5. Parent: Edit Mode, the new bone, Bone properties > Relations > **Parent** = the head bone (`DEF-spine.006`) - a line appears between them, and the hair bone now follows the head. Then animate its sway.

**My notes (not from the video):**
- Bones added straight onto a Rigify-generated rig are lost when you press Re-Generate Rig. The Rigify way to keep them is to add them to the meta-rig (as a simple copied or chain bone type) and regenerate. I haven't checked this in our Blender 5.2.
- For Sora this matches [[Sora_Secondary_Motion_Idea]]: the PS2 model already has hair, hood, necklace and jacket bones with weights, so hair sway there would be animating existing bones, not adding new ones. Still parked until Kvon revives it.
- **Tool note:** the watch-video skill's `yt-dlp` (2024.10.22, on Python 3.8) can no longer download YouTube video ("Requested format is not available"). Captions still download: `python -m yt_dlp --ignore-no-formats-error --skip-download --write-subs --write-auto-subs --sub-langs "en-orig,en" --sub-format vtt <url>`. Getting frames needs a newer yt-dlp (and Python 3.9+) - installing it is Kvon's call (Agent Setup: ask before installing packages).

**Why:** Kvon shared it to learn from, after the two rigging tutorials; no further reason given.
