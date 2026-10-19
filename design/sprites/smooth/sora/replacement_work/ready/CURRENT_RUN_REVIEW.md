# Current run and stop artwork

October19: the user approved the [backward-arm pilot](run_loop/comfyui_trial/attempt_03/final_pose_v1.png) and requested continuing this workflow. Two adjacent complete flat guides are in [adjacent_guides_v3](run_loop/comfyui_trial/adjacent_guides_v3/provenance.json); the earlier v1/v2 guides are construction diagnostics with clipped contours and are excluded. The new guides retain original-sheet compression/passing leg drawings, add independently drawn empty-arm swings and use the approved carry with a small integer shoulder bob. [Attempt04](run_loop/comfyui_trial/attempt_04/receipt.json) and [attempt05](run_loop/comfyui_trial/attempt_05/receipt.json) contain the exact local CPU requests and receipt IDs. Collect these submissions without sending them again. Artwork review and the short sequence export are in progress; full loop/stop remain unfinished.

Approved single-pose pilot: [original/refined comparison](run_loop/comfyui_trial/attempt_03/Original_Final_Comparison.png), [complete backward-arm pose](run_loop/comfyui_trial/attempt_03/final_pose_v1.png), [art review](run_loop/comfyui_trial/attempt_03/ART_REVIEW.md) and [final preservation QA](run_loop/comfyui_trial/attempt_03/Final_Preservation_QA.json). The near empty arm retracts into a closed fist beside the hip; original face, far holding grip and connected same-shoulder Keyblade carry remain exact. The user approved its style and carry on October19. It has an opaque white background; full run/stop cycles, motion joins/wrap, transparent exports and gameplay integration remain unfinished. Earlier candidates/failed QA/guides and all approved originals are preserved.

Local setup: [workflow](../local_ai_workflow/README.md) has its runtime/model installed and integrity checked. CUDA reports `No CUDA GPUs are available`; the approved workflow uses CPU. Attempts01/02 completed but failed visual review; attempt03 led to the approved flat-finished pilot above. They are terminal records, not jobs to resubmit. The original pose00 input and all earlier drawings remain preserved.

Continued Gemini corrections, October 12: [attempt12 sheet](run_loop/gemini_browser_trial/attempt_12/gemini_original_preview.jpg) / [review](run_loop/gemini_browser_trial/attempt_12/ART_REVIEW.md) is rejected for 16 cells, changed camera/style and reversed/malformed carry. A fresh single-pose backward-front-arm pilot then failed with a generic service error; [attempt13 record](run_loop/gemini_browser_trial/attempt_13/ART_REVIEW.md). One same-prompt retry returned "I was not able to generate that image," without a reason or image; [attempt14 record](run_loop/gemini_browser_trial/attempt_14/ART_REVIEW.md). The corrected art remains outstanding. No earlier candidate is promoted and no gameplay art was replaced.

Latest Gemini browser trial, October 12: [first candidate](run_loop/gemini_browser_trial/attempt_10/gemini_original_preview.jpg) / [review](run_loop/gemini_browser_trial/attempt_10/ART_REVIEW.md), followed by [carry-correction candidate](run_loop/gemini_browser_trial/attempt_11/gemini_original_preview.jpg) / [review](run_loop/gemini_browser_trial/attempt_11/ART_REVIEW.md). The original generated sheet was uploaded as the reference. Attempt10 swaps/misses carrying grips; attempt11 improves grip presence but holds the free arm forward and returns 16 cells with grid lines. Both are opaque RGB candidates; neither completes the requested corrections or supersedes the gait study below. Native downloads and exact prompts are preserved in those folders.

Latest original-sheet correction attempt, October 12: [new generated candidate](run_loop/direct_generation_retry_v1/sheet_correction_v1/sora_run_loop_sheet_candidate.png) and [review/error record](run_loop/direct_generation_retry_v1/sheet_correction_v1/REVIEW.md). This candidate still holds the free arm forward in most poses. The targeted arm follow-up was rejected at image-service output moderation; no corrected follow-up image returned. The requested fixes are incomplete, and this attempt does not supersede the gait candidate below.

Current landing-transition candidate, October 12: **run_loop/direct_generation_retry_v1/gait_cycle_study_v5**, saved in **D:\KH Fighting Game**.

- [Previous/new comparison with pause, slow playback and frame stepping](run_loop/direct_generation_retry_v1/gait_cycle_study_v5/Review.html)
- [New eighteen-pose loop GIF](run_loop/direct_generation_retry_v1/gait_cycle_study_v5/Preview_512_Loop.gif)
- [Pose board](run_loop/direct_generation_retry_v1/gait_cycle_study_v5/Contact_Sheet.png)
- [Drawing review and remaining work](run_loop/direct_generation_retry_v1/gait_cycle_study_v5/ART_REVIEW.md)
- [Verified export and provenance checks](run_loop/direct_generation_retry_v1/gait_cycle_study_v5/QA_Report.json)

Two new articulated flight-to-contact drawings bridge both landings, including the cycle wrap. All sixteen v4 drawings are unchanged; two 80 ms flight holds become 40/40 ms, preserving 960 ms total. Solid-sole support/flight, limb guides, protected carrying grip/face/blade, source hashes, transparent exports, GIF timing/repeat and viewer links pass validation. Browser controls and Godot playback were not tested in this session. Garment polish, torso/cloth follow-through, run-start/stop joins and final motion approval remain pending. Stop remains the preserved motion_refinement_v4 study.

Previous sixteen-pose checkpoint:

Current run-loop drawing study: **run_loop/direct_generation_retry_v1/gait_cycle_study_v4**, saved in **D:\KH Fighting Game**.

- [Animated previous/new comparison, slow playback and frame stepping](run_loop/direct_generation_retry_v1/gait_cycle_study_v4/Review.html)
- [New sixteen-pose run loop](run_loop/direct_generation_retry_v1/gait_cycle_study_v4/Preview_512_Loop.gif)
- [New pose board](run_loop/direct_generation_retry_v1/gait_cycle_study_v4/Contact_Sheet.png)
- [Drawing review and remaining work](run_loop/direct_generation_retry_v1/gait_cycle_study_v4/ART_REVIEW.md)
- [Original/arm/stop comparison board](run_loop/direct_generation_retry_v1/motion_refinement_v4/Original_Refinement_Comparison.png)

New legs alternate support, compression, passing and flight, while the free arm counter-swings below the blade. Four new articulated transitions reduce the largest adjacent ankle gap while preserving960ms timing. Sprites are complete flat canvases, with transparent128px exports. Garment/sleeve polish, torso/cloth/chain follow-through and run-start/stop/idle joins remain unfinished. The preserved stop below does not yet share the new loop entry. No actual-browser or Godot playback test.

Previous arm and current stop carry-order study: **direct_generation_retry_v1/motion_refinement_v4**.

- [Original/new comparison with slow playback and frame stepping](run_loop/direct_generation_retry_v1/motion_refinement_v4/Review.html)
- [Refined free-arm run study](run_loop/direct_generation_retry_v1/motion_refinement_v4/Preview_512_Loop.gif)
- [Stop carry-order study, plays once](run_stop/direct_generation_retry_v1/motion_refinement_v4/Preview_512_Once.gif)
- [Run drawing/motion review](run_loop/direct_generation_retry_v1/motion_refinement_v4/ART_REVIEW.md)
- [Stop drawing/motion review](run_stop/direct_generation_retry_v1/motion_refinement_v4/ART_REVIEW.md)

The loop now has distinct articulated free-arm poses while preserving the generated body detail. Version4 lowers the forward hand so it reads as empty rather than a second Keyblade grip. The stop selects complete carry poses before clearance/lowering and shares the exact loop entry. This is an unfinished study: alternating stride, arm/jacket joins, braking footwork, rigid weapon consistency and the final idle transition still need drawing. Failed stop repainting pilots are preserved and excluded. No individual production layers or additional image-generation retries were used.

Newest AI trial: **direct_generation_retry_v1**. Workspace: **D:\KH Fighting Game**.

Both original built-in generation requests returned new complete12-pose sheets with native transparency. The drawing style is closer to the accepted run-start artwork. Their motion remains unapproved: run stride alternation/free-arm swing, weapon geometry and the loop seam need work; stop lowers the weapon too early, then returns to carry. The targeted stop carry-order edit received an output-stage content refusal, so no more generation retries followed in this pass.

- [New generated run and stop preview with slow playback and scrubbing](run_loop/direct_generation_retry_v1/whole_frame_review_v1/Review.html)
- [New generated run-loop GIF](run_loop/direct_generation_retry_v1/whole_frame_review_v1/Preview_512_Loop.gif)
- [New generated run-stop GIF, plays once](run_stop/direct_generation_retry_v1/whole_frame_review_v1/Preview_512_Once.gif)
- [New native run sheet on white](run_loop/direct_generation_retry_v1/sora_run_loop_generated_original_White_Review.png)
- [New native stop sheet on white](run_stop/direct_generation_retry_v1/sora_run_stop_generated_original_White_Review.png)
- [Run generation exact tool arguments](run_loop/direct_generation_retry_v1/request.json)
- [Stop generation exact tool arguments](run_stop/direct_generation_retry_v1/request.json)
- [Stop correction classification, exact arguments and full error](run_stop/direct_generation_retry_v1/carry_order_edit_v1/RESULT.md)
- [New generation review notes](run_loop/direct_generation_retry_v1/REVIEW_NOTES.md)

The whole-frame review contains12 complete512px PNGs and transparent128px exports for each animation, plus GIFs and contact boards. Export scaling/registration is provisional and does not establish a natural gait. No individual body/weapon layers or new local pose paintings were used in this trial. The raw generated PNGs and accepted run-start source remain preserved.

Earlier local refinement: **quality_refinement_v9**.

The earlier `flat_cycle_v5`, `flat_stop_v5` and approved run-start files are preserved. New artwork is saved in the separate folders below.

- [Run and stop preview with slow playback and frame scrubbing](run_loop/quality_refinement_v9/Review.html)
- [Run-loop GIF](run_loop/quality_refinement_v9/Preview_512_Loop.gif)
- [Run-stop GIF, plays once](run_stop/quality_refinement_v9/Preview_512_Once.gif)
- [Run-start / previous / refined art comparison](run_loop/quality_refinement_v9/Benchmark_Comparison.png)
- [Run-loop frames and review notes](run_loop/quality_refinement_v9/ART_REVIEW.md)
- [Run-stop frames and review notes](run_stop/quality_refinement_v9/ART_REVIEW.md)

The earlier local pass has16 complete512px PNGs and transparent128px exports for each animation. It restores richer clothing, boot, glove and guard detail, corrects limb proportions and removes triangular arm-outline artifacts. These drafts are also preserved; motion joins and the final idle transition remain unfinished.

In VS Code, use Ctrl+P and paste:

```text
design/sprites/smooth/sora/replacement_work/ready/CURRENT_RUN_REVIEW.md
```
