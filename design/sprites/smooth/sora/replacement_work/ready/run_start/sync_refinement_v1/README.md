# Selected-sheet refinement checkpoint

Use `timing_review_v1/Review.html` to play once, slow down or scrub the twelve intact complete drawings. `Run_Start_128_Once.gif` is the small one-pass preview, and `Remaining_Gaps.png` compares the four largest gaps. Timing is provisional; final motion/weapon approval is pending.

The art source is `../direct_imagegen_trial/attempt_03/sora_run_start_original.png`, selected by K'von for its art quality. The corrected whole-figure registration is `../direct_imagegen_trial/whole_figure_review_v3/`. Equal-grid reviews are historical crop diagnostics, not production frames. Whole-figure v2 is an explicitly documented incomplete export. Preserve all originals and historical reviews.

No individual production layers, new motion drawings or body-part transforms were added in the timing checkpoint. PNG bytes are copied from whole-figure v3. The original sheet's SHA256 remains `6108be48aa93f736514c1860f1a9966de1998b0800814156c681321cb779530e`.

## Generation record

- Built-in tool: `image_gen.imagegen`, callable `image_gen__imagegen`.
- `inbetweens_trial/attempt_01/`: four returned full-drawing candidates, excluded for high holding wrists.
- `inbetweens_trial/attempt_02/request.json`: exact request; no recoverable response or saved image. `result_unavailable.json` records uncertainty without inferring a cause.
- `inbetweens_trial/attempt_03/request.json`: exact latest arguments, including the two existing frame references and transparent-background setting.
- `inbetweens_trial/attempt_03/EXACT_TOOL_ERROR.txt`: complete verbatim error returned by the latest call. `result.json` distinguishes the output-stage content refusal from validation, permissions or service failure. No image returned. No subsequent image-generation call was made in this pass.

## Next art work

Use complete-image edits of the selected drawings. Do not restore the cancelled layer fallback. Resolve01-to02 first: the new wrist belongs between the endpoints at lower-chest height, with the blade midway from diagonal up-left to nearly upright. Keep head/body/feet placement and connected Kingdom Key dimensions. Then resolve03-to04,05-to06 and09-to10. Compare each complete new drawing against both neighbors at512px and128px before insertion. Keep the far-arm same-shoulder carry behind the head, empty near arm, correct wrist/thumb, attached chain and slight foreground tip.

Pacing cannot repair missing intermediate poses or weapon projection changes. Running refinement remains ahead of aerial work. No engine assets were replaced or gameplay timing tested.
