# Running weapon correction plan

Prepared October 6, 2026. Planning only: no raster edits, image-generation retries, package execution or engine changes.

## Preserved sources

Both sources are 1774 x 887 RGBA. Frames are numbered 00–07 in reading order, four across then four below. Locate transparent gutters before cropping: dimensions do not divide evenly into four columns and two rows, so do not assume exact integer cell sizes.

| Source | SHA-256 |
| --- | --- |
| run_start/run_start_source.png | 1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256 |
| run_loop/run_loop_source.png | 6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0 |

Keep these files untouched. Future corrections go into versioned sibling files and a layers/ subfolder in each animation folder. Retain approved body and leg poses; any hand/forearm correction is limited to achieving the grip. No run-stop source exists yet.

## Local tools identified before edits

| Tool | Evidence and role |
| --- | --- |
| Python 3.8 installation, Pillow 10.4.0 | Import verified. Can crop, mask, rotate, composite RGBA layers, inspect alpha, hash originals and assemble review sheets. |
| NumPy | Import availability verified; can compare masks and geometry. |
| Microsoft Paint | mspaint.exe launcher found in WindowsApps. App launch, version, layer support and transparency editing have not been verified. |
| .NET and existing AnimationPackaging.cs | dotnet.exe found; project helper uses System.Drawing for bounds, PNG and GIF packaging. Helper was inspected, not executed in this task. |
| GIMP, Krita, Inkscape, Aseprite, ImageMagick, Photoshop, Affinity, Paint.NET | No matches in checked PATH, Program Files folder names or uninstall records. This is not proof of absence from every portable location. |
| Windows convert.exe | Filesystem conversion utility; not ImageMagick and not suitable for image work. |

Pillow is the confirmed local compositing option. Manual reconstruction quality remains a separate requirement; it cannot recover hidden body artwork automatically. No packages or editors will be installed as part of this plan.

## One rigid weapon master

Use workspace-relative design/references/Sora_KHIV_Render.webp as carry/construction reference. Retain KH2 outfit and existing smooth cel shading. Draw one clean transparent Kingdom Key master rather than using the inconsistent weapons from the generated sheets. The render supplies geometry, not the final rendering style.

Define local grip pivot G=(0,0) at the palm center on the black handle. Define the longitudinal axis from pommel through handle center, blue collar, silver shaft and terminal key head. Record fixed master anchors for pommel P, collar C, shoulder-contact point S along the shaft, and tip T. Guard encloses the handle; shaft emerges along the handle axis. Chain attaches only to the pommel.

Choose master length once against approved idle weapon/body proportions; record pixel length after the common export scale is chosen. Do not infer a pixel length from the perspective photo or choose a fresh length per frame. Fix guard width, handle length, shaft width, teeth shape and collar spacing in the master. Do not stretch, bend or independently rotate components. Use one constant uniform scale for the entire batch, rotation about G and translation only. Keep a consistent view; if genuine perspective rotation is later necessary, it requires a deliberately constructed matching projection, not arbitrary per-frame distortion.

For each frame transform all master anchors together: world(A)=hand_anchor + scale * rotation(angle) * (A-G). The hand anchor is measured from the intended palm center. The transformed shaft must pass over the holding arm's shoulder contact; if it cannot reach with a natural wrist, adjust only the local arm pose/contact mask, not the weapon geometry. Preserve the same anatomical holding arm across frames; do not relabel it when limbs overlap. Mark it once on the first pose after matching the supplied reference.

The chain may be a separate flexible layer with modest motion, but its attachment remains at transformed P and its length is fixed. It cannot substitute for or alter blade geometry.

Later user direction: point the tip slightly toward the foreground and coordinate body/shoulder/wrist movement with it. Local pilots now use one camera projection of the unchanged master (25-degree tip-toward-viewer yaw). Apparent screen dimensions may change through that projection; physical master dimensions remain fixed. Refine shoulder and finger overlap per pose rather than treating the body as a static carrier. Current pilot is ready/run_loop/layers/pilot_v3; it is one review frame, not a completed gait.

## Layers and occlusion

Maintain: original source; body-clean plate; weapon master instance; chain; foreground fingers/hand mask; shoulder/head/hair occlusion mask; flattened review output. The master remains one object even where masks hide parts of it. Use local masks to place visible portions behind hair/shoulder and the grip beneath fingers; do not cut the master into independently positioned pieces.

Remove old weapon pixels and reconstruct only the newly exposed local body/arm areas on a separate clean plate. Check every old shaft, guard and chain segment so no ghost weapon remains. Generated hands often use two-handed chest grip; the intended one-handed shoulder carry needs a small hand/forearm redraw and a free-arm treatment. Do not claim this can be achieved with a simple pasted overlay alone.

## Run start: frame-by-frame

| Frame | Preserve body motion | Rigid weapon/grip correction |
| --- | --- | --- |
| 00 | Standing guard, wide stance | Fit intact master to guard grip as starting position; establish holding arm and G. Preserve initial guard rather than starting already slung. |
| 01 | Knee flex, hips lower | Hand begins lift; rotate the entire weapon toward same-arm shoulder. Free hand releases; retain connected handle/shaft axis. |
| 02 | Forward lean | Continue lift with elbow bend; keep grip anchored to palm. Shaft approaches holding shoulder without crossing through face or torso. |
| 03 | Raised arm, pre-push stance | Seat shaft on same-arm shoulder; replace current raised two-hand arrangement locally. Guard sits beside holding hand, blade extends behind shoulder away from travel. |
| 04 | Deeper lean and push preparation | Keep shoulder contact; translate with shoulder motion and apply small rigid rotation. Match arm to grip rather than moving blade independently. |
| 05 | Push-off, trailing leg extends | Keep carry seated during acceleration; move the whole master with hand/shoulder. Check hair and shoulder occlusion. |
| 06 | Passing knee, compressed stride | Preserve grip and contact during torso bob; correct current hand-on-shaft appearance. Free arm follows body motion. |
| 07 | Extended running stride | Match run-loop 00 carry geometry, scale and shoulder relationship; check weapon has no jump at transition. |

## Run loop: frame-by-frame

The existing body drawings are retained. Their gait phase labels are provisional; do not alter approved footwork to force the originally requested gait sequence.

| Frame | Existing body characteristic | Rigid weapon/grip correction |
| --- | --- | --- |
| 00 | Long trailing leg, front foot low | Establish loop carry from run-start 07; palm G beside same-arm shoulder, shaft seated above it. |
| 01 | Legs gather beneath torso | Follow lowered shoulder with translation; keep the same length, grip and shoulder contact. |
| 02 | Raised leading knee | Small rigid angle adjustment only as torso rises; verify collar aligns with handle and fingers enclose grip. |
| 03 | Extended airborne stride | Follow forward lean without swinging blade away from shoulder; mask head/hair overlaps. |
| 04 | Foot approaches ground | Follow landing body height; no independent guard tilt or blade shortening. |
| 05 | Legs pass/overlap | Preserve holding-arm identity through overlaps; free hand must not accidentally acquire the grip. |
| 06 | Compact knee-up pose | Follow compressed torso with anchored palm and shoulder; verify no shaft passes through arm. |
| 07 | Extended stride returning to 00 | Compare 07→00 hand, shoulder, blade tip and angle; remove abrupt weapon-only jump without changing body pose. |

## Run stop: future eight-frame layout

No sheet exists to correct. When body art is available, apply the same master: 00 running carry; 01 braking reach with seated carry; 02 heel contact following shoulder rise; 03 knee compression retaining grip; 04 stable rear-foot plant; 05 lift shaft off shoulder and lower whole object; 06 free hand rejoins guard as needed; 07 approved standing guard. Do not fabricate body frames by scaling or reversing run-start images.

## Measurement and review before export

Record frame crop rectangle, anatomical holding arm, palm anchor, shoulder contact, angle, fixed scale and occlusion mask paths in a per-animation manifest. Coordinates and angles are deliberately not invented here; measure them from actual crops during correction. Master-space geometry stays identical for every instance. Render from the original master each time to avoid cumulative resampling.

Review each pose at full size and game size: continuous pommel–handle–collar–shaft axis; consistent silhouette and length; fingers on handle; correct shoulder; no detached guard, extra hands, old weapon pixels or clipping. Inspect contact visually and with transformed anchor overlays. Review start→loop, loop 07→00 and eventual loop→stop/stop→idle seams at slow speed, mirrored and normal. Verify PNG alpha, equal export canvases and unchanged source hashes. Outputs remain review assets until accepted; this plan does not integrate anything into Godot.
