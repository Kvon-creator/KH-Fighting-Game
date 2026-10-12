# Current run and stop artwork

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
