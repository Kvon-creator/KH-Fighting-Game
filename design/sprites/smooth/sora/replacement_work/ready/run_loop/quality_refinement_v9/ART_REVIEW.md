# Run and stop quality refinement v9

Open [Review.html](Review.html) for the512px/128px loop, one-pass stop, slow playback, frame scrubber and two-cycle run-to-stop preview. Open [Benchmark_Comparison.png](Benchmark_Comparison.png) for native-size run-start / previous / refined artwork. Stop assets live separately in `../../run_stop/quality_refinement_v9/`.

This pass brings back the accepted run-start's detailed shorts, boots, glove/fingers and gold guard. Original complete PNGs are used as reference brushes with new joint poses and direct painting on one complete RGBA canvas. There are no exported part sprites or production layers. The face/hair and costume surfaces reuse approved art; this is not a claim of drawing every pixel from scratch.

Leg proportions follow the source landmarks. The free arm now uses fixed55px/45px lengths through the swing and bracing approach. Sleeve roots and head edges are improved, and internal triangular arm-outline artifacts are removed. The near support ankle stays fixed through the stop; the recovery body height is corrected to keep it reachable. The far arm carries the connected Kingdom Key behind the head over that same shoulder. All weapon elements share a209-unit projected axis; the slight foreground appearance is stylized.

`QA_Report.json` records successful read-only decode, transparency, source-hash, joint-length, disconnected-pixel, sole registration and GIF checks. Each sequence has16 distinct poses. Loop960ms, stop1200ms; identical entry. The review controls pass an offline JavaScript harness. Godot and actual browser playback were not tested. All original sources and previous passes remain unchanged.

This is a stronger art draft, not final idle-quality or natural-motion approval. Remaining work: clothing overlap/sleeve joins, last-start-to-loop and wrap synchronization, cloth/chain follow-through, second-hand visibility and the final approved-idle transition. Continue running refinement before aerial production.
