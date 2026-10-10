# Sora running Keyblade carry

**Latest correction, October 10:** K'von likes Gemini's attempt05 artwork but wants the Kingdom Key held by the other arm and carried over that arm's other shoulder, behind Sora's head. For the current right-facing pilot, switch from the visible near/front gripping arm to the opposite far arm; the near arm becomes the free swinging arm. Preserve Sora's facing, KH2 outfit, finish, connected weapon geometry and slight foreground tip. This changes the carry-arm target for the next complete-frame Gemini revision; earlier approved near-arm local constructions remain preserved references, not the new placement target.

**Why:** K'von specifically requested the arm/shoulder switch after liking the latest pilot. It is approval of its general artwork with a requested carry correction, not final approval of that unchanged frame.

**Current local refinement:** run_loop/review_cycle_v5 now includes individual jackets/arms on all eight existing poses. New00/01/02 review_v3 follows source shoulders/necks and preserves frame00's approved hand/cuff rectangle exactly;05/06/07 remain review_v3 and03/04 review_v4. All four weapon/grip/chain files are byte-identical to v2 across the cycle. Shaft overlap remains behind head/body with connected guard and approved grip in front. Original sources and prior reviews remain. This finishes a garment-repair pass, not idle-quality anatomy or gait approval. Material/arm proportions, alternating stride, root/flight offsets, timing and start/stop seams remain; see QA_NOTES.md and GAIT_REFINEMENT_PLAN.md.

**New gait candidate:** gait_refinement_v2 adds16 independent lower-body drawings. The existing00 carry projection/layers translate with the retained upper reference and body bob, preserving fixed master length/geometry, same-arm shoulder placement and foreground perspective. The approved hand/cuff rectangle remains exact after each translation, with the exported homography recorded. Master/grip and older artwork hashes are unchanged. Per-phase torso/carrying-arm refinement and cloth/chain follow-through remain; see Sora_Run_Loop_Gait_Refinement.md. This candidate does not replace the prior garment review or finalize the animation.

**Latest upper/carry pass:** gait_refinement_v3 adds sixteen new jacket/waist/arm drawings and coherent shoulder/wrist/carry motion. Frame00 keeps the exact approved hand/cuff rectangle and carry layers. Other poses project the same corrected master grip with small angle changes and positive foreground yaw24.4-25.6 degrees; physical master length remains285px. Blade/guard/handle share one transform, wrist sockets join the forearms and the collar stays5.73-8.71px from the holding shoulder. The chain remains attached at the pommel while its pendant trails slightly. Original sources, v1/v2 gait and review_cycle_v5 remain unchanged. Material/anatomy/timing and transition work are still required; no generation retry or aerial production.

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
