# Current run and stop artwork

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
