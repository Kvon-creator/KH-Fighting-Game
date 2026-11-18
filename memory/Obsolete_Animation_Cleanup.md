# Delete obsolete animation folders after each final approval

**Fact or rule (October 23):** Kvon said: "Remember this process of deleting obsolete folders every time I approve the final version of an animation cycle." This is a standing authorization: no need to ask again for each cleanup. Do it every time Kvon approves the final version of an animation cycle.

**The process:**
1. **Commit and push first,** so every version being deleted stays recoverable from git history. Note that commit's hash.
2. **In `design/models/sora/`, keep:**
   - the approved version's 3D folder(s) and their 2D-style (`*2d_*`) folder(s);
   - every other animation's current final version;
   - `saved_attacks/` (retired attacks Kvon asked to keep for future reference, November 6);
   - the non-animation folders: `blender_workflow`, `downloads`, `gemini_walk_review`, `gemini_animation`, `pose_edit`, `character_blockout_*`, `README.md`.
3. **Delete:** that animation's older versions, test and measurement renders (e.g. `_m`, `_look*` folders), and any animation the approved one replaced.
4. **In `KingdomArena/assets/sora/`:** delete the image files of folders Godot no longer loads. **Keep every `.import` file.** Kvon said "don't remove the .import files".
5. **Check before committing:**
   - nothing a script or scene loads was removed;
   - Godot still runs the move test without errors;
   - `project.godot` and the `.import` files are unchanged.
6. **Commit and push the cleanup.** Record what was kept and deleted, plus the recovery commit, in `Sora_Movement_Set.md`. Then tell Kvon.

**Limits:**
- Only obsolete versions of animations under the 3D pipeline.
- Ask before touching the old hand-drawn pipeline in `design/sprites/smooth/sora/replacement_work/` (it is used as reference images), or anything that isn't clearly an older version of an animation.
- If Claude Code's safety check blocks a deletion, stop and ask Kvon rather than working around it.

**Why:** Kvon wants only the final versions kept. First done October 23 (recovery commit f429bfd, cleanup commit 675b41f).

**Clarified (Kvon, November 18): "the multiple versions of each frame and animation shouldn't exist because of my instruction to delete obsolete files."** I had only cleaned up after an explicit "final"/"I approve"; versions Kvon called "fine for now" / "looks good for now", or that were in the game while a newer one waited for review, were kept - Kvon expects those gone too. **Rule now: once a version is in the game, every other version of that animation is obsolete** - delete them in the same step (commit + push first, keep .import files, test Godot, commit), unless Kvon says to keep one. Check which version the game really uses by comparing the game's sprites with each version's frames (notes can be stale: Crouching Medium's note said v23 final, the game used v24).
- **Done November 18** (Kvon confirmed the list): deleted 58 folders (recoverable from commit cb8b48a0). In the game and kept: Standing Light v12 (v11 had identical poses, v12 adds the smear), Standing Medium v15, Crouching Light v31, Crouching Medium v24, Jumping Light v8, Jumping Medium v7, Jumping Heavy v2, back-dash v2. Kept on purpose (not versions of in-game animations): research/, attacks/saved_attacks/, model/from_scratch_blockout/.
