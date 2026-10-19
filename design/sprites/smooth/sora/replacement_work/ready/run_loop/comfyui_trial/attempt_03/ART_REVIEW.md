# Backward-arm pilot review — October14

**User approved this single pose on October19:** "Yes. Continue workflow." Use `final_pose_v1.png` as the style/carry anchor for subsequent complete flat running drawings. This is not approval of a full animation cycle. The original internal review and native model output remain preserved below.

The third local render used one complete hand-drawn flat guide, retained it in the latent, and applied a lighter DreamShaper finish on CPU. Its native output completed in373.81seconds. Direct painting then clarified the closed empty fist and restored exact protected source pixels on the same full canvas. No component production layers or scaled pose substitutes were used.

- Pose: the near arm retracts leftward from the shoulder through a bent elbow into a connected forearm and closed empty fist beside the near hip. The original leg pose is held for this isolated art test.
- Style/identity: clean2D outlines and matte cel shading remain consistent with the original reference; hair, face, outfit palette, shoes and camera stay coherent. This is a pilot calibration, not completion of the full idle-quality movement set.
- Carry: the original far holding arm, noninverted grip, guard/handle/collar/shaft/crown/chain and same-arm shoulder carry behind the head are preserved exactly in the checked source regions. The original slight foreground tip presentation is retained.
- Registration/fit: unchanged source foot/head placement; full512px canvas without clipping. The backward fist is a genuine redraw.
- Evidence: `Final_Preservation_QA.json` confirms all242,555 pixels outside the selection are unchanged and all three protected source regions match the original. Source, input, mask, native and refinement hashes are verified.

Native exact-preservation QA initially found16 antialiased background-edge values at x404, not blade pixels. `Protected_Edge_Differences.json` and the failed native QA remain preserved. The flat refinement restores the original values, and future selection creation hard-protects rectangle edges. No model resubmission was needed for that correction.

The preview is opaque RGB on white; transparent sprite export, chronological whole-frame loop/stop production, wrap/join/motion testing and Godot integration remain unfinished. Run-start benchmark, original sheet, idle, gait_cycle_study_v5 and stop motion_refinement_v4 remain preserved. Single-pose approval authorizes continuing this visual treatment; it does not establish a finished animation or gameplay integration.
