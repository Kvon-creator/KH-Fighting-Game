# Run arm-motion study, October 11

Version4 lowers the forward free hand in poses03-07 so it stays below the carried blade. This removes the unintended appearance of a second weapon grip. Version3 remains preserved; arm timing, anatomy and the full gait are still under review.

Open [Review.html](Review.html) for the original/new comparison, slow playback, frame stepping, floor guide and run-to-stop study. The new candidate lives in **D:\KH Fighting Game**. Originals and earlier studies are preserved.

The twelve complete generated drawings now have an articulated free-arm swing. Native sleeve/glove material is painted from the complete run00 PNG onto each full canvas; the exposed jacket join and skin are painted directly. The near arm moves forward and backward while the far hand retains shoulder carry. No part bitmap, body/weapon sprite or production layer is created. Upper-arm/forearm guide lengths are40.4969/36 working pixels. These are construction guides, not a certified anatomical measurement of every visible contour.

The latest pass removes the old arm's lower edge and detached remnants. All pixels outside the front-arm edit envelope remain exact, including the feet, most of the lower body, hair/eyes and carrying grip. Where the new hand passes in front of the lower face or blade, it produces a new occlusion.

The loop is twelve frames at80ms each (960ms), with transparent512px and128px PNGs, sheets and white-background GIFs. The body/leg sequence is retained from the new generated sheet; the phase labels and floor placement remain provisional. Arm motion alone does not fix missing alternate-leg poses, body jitter or the loop seam.

The separate stop study selects five complete carry poses from this loop (00,01,02,05,08), followed by the original stop05-11. Stop00 is byte-identical to loop00. This fixes the earlier lowered-blade-to-carry reversal, while leaving braking foot paths, carry clearance and the upright-to-guard join unfinished. It does not create new braking-leg drawings or establish consistent weapon geometry.

The local stop painting pilots contain horizontal waist seams and are excluded. Seven pilots and motion studies1/2/3 are preserved as diagnostics. The earlier painter states were not snapshotted for those pilots; do not claim the current helper reproduces their exact strokes. This pass includes its own Flat_Painter_Source.cs.

Read-only QA checks all24 full/game PNGs, alpha/margins, source hashes, unchanged protected pixels, arm guide lengths, no detached opaque component above8pixels, GIF counts/timing and the shared entry. The offline HTML harness checks asset links and controls, including the36-frame two-loops-to-stop view. These are not actual-browser or Godot playback tests.

Next drawing work: refine the shoulder/cuff outlines and new forearm shadows; draw the missing alternating-leg transitions with the same rich clothing/shoe finish; then correct the complete-frame rigid weapon geometry, braking poses and final approved-idle join. No image-generation retry followed the preserved service refusal.
