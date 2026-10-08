# Sora running Keyblade carry

**Current local refinement:** run_loop/review_cycle_v3 uses new frame_03_review_v4 and frame_04_review_v4 garment/arm drawings with the other six v2 poses. Source waist contours restore the red fabric, collars are narrower and straps/shirt detail are visible. All four weapon/grip/chain PNG layers on03/04 remain byte-identical to v2. Shaft overlap stays behind the head/body, with connected guard and approved grip in front. Frame00's approved hand/cuff region and original sources/prior reviews remain intact. These checks do not imply finished anatomy, clothing, gait or timing; see the new package's QA_NOTES.md.

**Fact or rule:** Running artwork must carry the Kingdom Key slung over the shoulder of the arm holding its handle. Use design/references/Sora_KHIV_Render.webp as the carry and weapon-construction reference, retaining the approved KH2 outfit and smooth style. Keep the weapon form consistent: handle, guard, shaft and blade must connect and move as one rigid object.

**Why:** K'von accepted the body poses but corrected the majority of Keyblade drawings for incorrect placement and inconsistent geometry.

**Workflow decision:** Preserve original sheets and stop image-generation retries. Use a separate rigid weapon master with fixed geometry, length and grip, and per-frame transforms and overlap masks. K'von authorized continuing this local workflow after reviewing the correction plan. First deliver one construction pilot before extending it across the animations.

**Movement direction:** The Keyblade tip should point slightly toward the foreground, with Sora's body, shoulder and wrist moving coherently with that carry. Use a controlled perspective projection of fixed weapon geometry rather than changing the weapon's physical shape or length.

**Why:** K'von requested this adjustment for more realistic movement.

**Grip correction:** The art_pass_04 hand appears upside-down. Correct thumb, knuckle and wrist orientation against the supplied shoulder-carry reference before continuing other art refinement; keep weapon registration fixed.

**Why:** K'von identified the inverted gripping hand and authorized correcting it.

**Grip approval:** K'von approved the corrected art_pass_05 hand orientation on October 7, 2026. Preserve that grip during further refinement of this frame.

**Why:** K'von said it looks good and authorized continuing the frame's refinement.

**Frame review:** K'von said frame_00_review_v1 looks good so far and authorized continuing on October 7, 2026. Use this treatment as the current visual reference for the next running pose; this is provisional review feedback, not approval of a full run cycle.

**Single generation retry:** K'von authorized exactly one further image-generation attempt, returning to local layers if it failed. The October 7 attempt failed with output-stage moderation_blocked, category other, request ID 4288281e-c97f-4a51-a91d-fa9e3e10fd33. Resume local layered work; no additional generation retries are authorized by that request. Exact arguments and error are saved in ready/run_loop/imagegen_single_retry_2026-10-07.json.

**Handoff cancelled:** K'von requested deleting design/handoffs/ and resuming the original local layered process. The exact folder was deleted on October 7, 2026; project artwork was retained.

**Gemini trial ended:** On October 8 K'von requested returning to the original local workflow and deleting design/gemini_movement_handoff/. The exact folder is removed, original art is retained and local refinement has resumed. The older design/handoffs/ folder remains deleted. Carry geometry, same-arm shoulder placement, foreground tip and approved grip remain requirements. See Sora_Gemini_Movement_Trial.md.
