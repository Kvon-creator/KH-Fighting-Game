# Pose-specific run-start refinements v3

Frame 01 repairs the overly broad previous chain cleanup: the original shorts silhouette is retained around a narrow removal polygon, with a curved local cloth edge. Frame 02 in this folder is historical; its oversized jacket/pants repairs are superseded by refinement_v4/sora_run_start_02.png. Frame 03 is the individually drawn shoulder-settle pose, and frame 04 is the distinct push-off pose. Both have locally drawn sleeves, jacket piping, fasteners, released far arms and bent carrying elbows, with source heads and lower bodies retained. The old gold guard and chains are removed with shaped masks.

The shared rigid weapon is projected with 20 and 22 degrees of foreground yaw for frames 03 and 04. The shaft is behind the head/body, while its connected guard and the approved corrected grip are in front. Body plates, repair drawings, weapon, grip, chain and cleanup masks are separate PNGs; pose manifests record registration. Weapon geometry is unchanged.

This version is still an art review, not matched-to-idle final work. Inferred jacket/pants material, local arm proportions and the seams between frames need further refinement. The earlier failed full-cycle start composite remains history, not the new reference. Current approved idle endpoint is in refinement_v2/sora_run_start_00.png. Its original weapon still needs a matching rigid-master transition.

review_sequence/ contains a partial five-pose preview using endpoint 00 from v2, frame 01 from v3, revised frame 02 from v4, and new frames 03-04 from v3. It applies vertical translation only to align grounded feet at y432. Its GIF restarts after 04; it is not the complete run-start cycle. Frames 05-07 await individual redraw.

Original source SHA-256 is checked by the renderers. New frames 03-04 also verify that their lower source pixels are unchanged. The review package checks all five PNGs, all five GIF frames, unique image content and clean transparent RGB pixels. No image generation, protected Godot edits or aerial production. Aerial work follows running's quality pass, as requested.
