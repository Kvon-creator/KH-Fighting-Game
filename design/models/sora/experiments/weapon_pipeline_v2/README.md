# Revised Keyblade teeth

Kvon identified the first pilot's teeth as wrong. This version replaces the triangular saw-like edge with three broad, flat-ended stepped teeth, using `design/references/Sora_KHIV_Render.webp` as the weapon reference. The new silhouette is a review candidate, not a claim of exact production geometry or user approval. V1 remains preserved.

[Review.html](Review.html) compares the actual old/new geometry close-ups. Open [weapon_pipeline_pilot.blend](weapon_pipeline_pilot.blend) for the complete model, camera and cel materials. [kingdom_key_flat_colors_v3.glb](kingdom_key_flat_colors_v3.glb) is the palette-preserving exchange export; the original GLB in this folder is a shader-export diagnostic. Use the `.blend` for the full procedural cel finish.

The model reopened successfully,24 meshes share one rigid root, and the grip/collars/shaft share the same axis. Three512px transparent CPU renders have clear margins. [QA_Report.json](QA_Report.json) and [Flat_Export_QA.json](Flat_Export_QA.json) record checks. Close-ups intentionally frame just the blade head. The three full-weapon orientations rotate about its shaft; they do not test an actual Sora shoulder carry or calibrated tip movement.

The creation process disabled file previews and the earlier thumbnail-cache write error did not recur. The unused factory brush-path warnings remain unrelated to this geometry. No user preferences were saved or existing artwork replaced. Sora's character mesh, rig, animation and final 2D-style match remain unfinished.
