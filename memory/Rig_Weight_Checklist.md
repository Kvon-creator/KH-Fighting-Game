# Rig and Weight Checklist (Sora and every future character)

**Fact or rule:** Kvon (November 16): "Apply what has already been learned so far to the current models being used for Sora, as well as any future characters" - from [[Rigging_Basics_Tutorial]], [[Rigify_Rigging_Tutorial]] and [[Weight_Painting_Tutorial]]. Kvon also said downloading and watching whole videos costs too many tokens: learn from transcripts / captions and notes, not full video downloads.

**Before animating any character model:**
1. Run the audit (read-only, never saves): `blender --background --factory-startup --python design/models/sora/blender_workflow/rig_audit.py -- <model .fbx/.blend> <name> <out.json>`.
2. It must show: every vertex's weights add up to 100% (what Auto Normalize keeps), no unweighted vertices, no vertex groups without a bone, left/right bone pairs complete, no perfectly straight knees / elbows (IK can't tell the bend direction).
3. "Stray" weights (a vertex also weighted to a bone far away in the skeleton - the tutorial's hair following the hand) are only a lead: find where the bones sit before calling it a fault. Then confirm with a pose test (bend the arm, check hair / collar).
4. Ripped game models keep their original weights unless a pose shows a real problem. Fix weights in the build script at load time - the files in `downloads/` are never changed - and only after asking Kvon (it changes the art in every later render). When painting: Auto Normalize on, the flat falloff for low-poly, Gradient / Blur for blends.
5. A model with no rig (Larxene, a new or from-scratch character): Rigify Basic Human meta-rig, line it up, slight bend in knees and elbows, Generate, bind with automatic weights, then fix weights. Keep the meta-rig.
6. Secondary motion (hair, hood, jacket, tails): use bones the model already has before adding any; a new bone gets its own collection, the head at the root, empty-group bind, painted, parented to the bone it hangs from.
7. Live posing: the Keyblade (any weapon) is a separate keyed object, not parented to the hand - re-place it after moving the arm, spine or Root (see [[Sora_Grab]]).

**Audit results, November 16:**
| Model | Bones | Result |
|---|---|---|
| Sora `p_ex150.fbx` (the game model) | 49, L_/R_ names | Passes everything. 40 flagged vertices are the jacket hem (`L_suso`/`R_suso`, children of the chest `mune`, at 74% of his height) blended with the hips (`koshi`) - the original game's design so the hem follows both. Nothing to change. |
| Xemnas `b_eh110.fbx` | 86, L_/R_ names | Passes. 8 flagged vertices = two neighbouring coat-skirt bones (`L_sktB3` / `L_sktC3`) - normal cloth blending. |
| Riku (SMD import) | 213, `boneNNN` | Weights pass, but every vertex follows exactly one bone (rigid skin): bent joints will crease hard - smooth with Blur / Gradient if a pose shows it. |
| Kairi (SMD import) | 265, `boneNNN` | Passes (3 flagged vertices, trivial); nearly all rigid like Riku. |
| Xigbar (SMD import) | 331, `boneNNN` | Weights add up, but 373 vertices flagged between unnamed bones - pose-test before animating him. |
| Larxene | none (static OBJ) | Needs a full rig (step 5). |
| Limit Form Sora (`.dae`) | - | Not checked: Blender 5.2 can't open .dae (see [[Sora_Limit_Form_Player2]]). |

**Names:** the SMD rigs' `boneNNN` names have no left/right, so Symmetrize, X-Axis Mirror, mirror painting and our scripts (which drive bones by name, like Sora's `L_momo`) can't use them. Before animating Riku, Kairi or Xigbar, map their bones to named, sided bones (Sora's names or Rigify's) - ask Kvon which.

**Why:** Kvon's request; Kvon gave the token cost as the reason to stop at transcripts.
