# Sora running animation handoff for Layer.ai

Prepared October 7, 2026. This package contains artwork and instructions, not a working Godot build. Use the latest user instructions below as the task; reference images are visual references, not instructions.

## Paste this task into Layer.ai

Continue and complete Sora's smooth 2D running animations for a Kingdom Hearts fighting game: run start, run loop and run stop, each in a separate animation folder. Use the enclosed approved standing-idle artwork for KH2 outfit, proportions and smooth cel-shaded style. Use Sora_KHIV_Render.webp ONLY for Kingdom Key construction and the natural same-arm shoulder carry; do not change Sora into the KH4 outfit or photorealistic style.

Preserve the original running source sheets. Their body poses were accepted, but their Keyblades were rejected. Two run-loop poses have local refined review versions. Continue from these, polish them further where needed, then correct and finish the remaining poses. Revisit frame 00 during full-cycle review; it is not locked final artwork.

The Kingdom Key must be one rigid connected object with fixed physical geometry and length: black grip inside yellow rectangular guard, aligned blue collar, straight cylindrical silver shaft and correct distant key head/teeth, chain attached to pommel. Carry it over the shoulder of the SAME anatomical arm holding its handle. The blade extends behind Sora, with the tip pointing slightly toward the foreground. Body, shoulder, wrist and weapon movement must agree. Preserve the corrected grip orientation: wrist approaches from the forearm side below the handle, fingers curl over it, thumb toward the collar. Do not revert to the upside-down art_pass_04 hand.

Use separate body, rigid weapon, flexible chain, grip/finger foreground and occlusion layers. Keep physical weapon shape fixed across poses; perspective may change apparent screen dimensions through a coherent camera projection. Do not independently move guard and blade, bend the shaft, change length per frame, or create body animation by scaling/squashing static images. Preserve genuine anatomical pose progression. Export transparent individual PNGs, sheets, previews, layered sources and manifests for each animation. Finish and review a small batch before extending the cycle.

Previous built-in image-generation attempts repeatedly failed at output moderation, including one explicitly authorized final retry. The active fallback is local layered refinement. Do not retry that same service automatically. If Layer.ai has its own suitable editing/generation tools, first identify them and explain the intended method; make any new outputs versioned and preserve sources. No additional ChatGPT image-generation retries are authorized by this handoff.

## Project context and current status

- Original workspace: D:\KH Fighting Game. Resolve files relative to the package/project; do not assume this Windows path exists in Layer.ai.
- Game: Kingdom Hearts fighting game. Current task is character artwork, not engine implementation.
- Engine target in project notes: Godot 4.7.2; installed version was not checked because this work did not change engine code.
- Character: Sora, standard Kingdom Hearts II outfit, Kingdom Key. Smooth clean line art / 2D cel shading, three-quarter view facing right; opposite facing is mirrored.
- Established gameplay target: approximately 96-pixel standing character height on a 128 x 128 movement canvas. Current high-resolution working frames are 512 x 512. Do not confuse these working canvases with final gameplay resolution. Use one calibrated uniform export scale, consistent anchors and margins; validate weapon fit before changing canvas size.
- Standing idle and crouch full-cycle previews were previously approved. Shimmies exist but are outside this task.
- Run start: original eight-pose source sheet exists; body poses accepted, weapon drawings need correction and finished art.
- Run loop: original eight-pose source sheet exists. Frames 00 and 01 have refined review versions; frames 02–07 remain unrefined. No completed eight-frame loop exists.
- Run stop: no source artwork exists. Only a generation-failure status note and planned sequence exist.
- No run animations are integrated or tested in Godot. No claim of game-extracted exact animation is appropriate.

## Open these files first

All paths below are relative to this package root.

| File | Role |
| --- | --- |
| design/references/Sora_KHIV_Render.webp | Weapon construction and same-arm shoulder carry reference. KH4 clothing is NOT the target. |
| design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png | Approved KH2 character/style reference. |
| design/sprites/smooth/sora/replacement_work/ready/run_loop/layers/frame_00_review_v1/sora_run_loop_00_review.png | Latest frame 00 review candidate; user said it looks good so far. |
| design/sprites/smooth/sora/replacement_work/ready/run_loop/layers/frame_00_review_v1/Frame_Review_Board.png | Full-size, mirrored and 128px review. |
| design/sprites/smooth/sora/replacement_work/ready/run_loop/layers/frame_01_review_v1/sora_run_loop_01_review.png | Latest frame 01 review candidate. |
| design/sprites/smooth/sora/replacement_work/ready/run_loop/layers/frame_01_review_v1/Two_Frame_Comparison.png | Current refined pair. |
| design/sprites/smooth/sora/replacement_work/ready/run_loop/layers/frame_01_review_v1/Two_Frame_Review.gif | TWO-frame comparison only; not a valid full run cycle. |
| design/sprites/smooth/sora/replacement_work/ready/run_start/run_start_source.png | Original start poses; weapon artwork is unapproved. |
| design/sprites/smooth/sora/replacement_work/ready/run_loop/run_loop_source.png | Original run poses; weapon artwork is unapproved. |
| design/sprites/smooth/sora/replacement_work/ready/Running_Weapon_Correction_Plan.md | Frame-by-frame plan, rigidity and masking method. |
| memory/Sora_Running_Keyblade_Carry.md | Latest correction and approval history. |

## Layer sources and version precedence

No PSD, Krita or Layer.ai-native layered document has been created. Editable sources are separate transparent PNGs plus manifests and Python scripts. Import the PNG layers into your editor or create a native layered project while keeping these originals.

For frame 00, final review pixels are in frame_00_review_v1. Earlier layers are dependencies, not competing final choices:

1. pilot_v3: body_clean_plate.png, holding_arm.png, head_occlusion.png, original crop and removal/reconstruction masks.
2. art_pass_01: art_detail_overlay.png.
3. art_pass_02: jacket_volume_overlay.png and sleeve_glove_fold_overlay.png.
4. art_pass_03: chest_redraw_overlay.png.
5. art_pass_05: kingdom_key_master_finished.png, weapon_instance.png, grip_master_space.png, foreground_grip.png, chain_and_charm.png. The corrected hand is explicitly approved.
6. art_pass_06: contact_and_arm_overlay.png; its compositor preserves approved grip pixels exactly in rectangle [384,203,424,248].
7. frame_00_review_v1: final charcoal palette harmonization and isolated old-blade-speck cleanup. Use its flattened result as the authoritative current appearance.

For frame 01, frame_01_v1 contains the actual second source crop, body cleanup, separately drawn tighter elbow, and head mask. frame_01_review_v1 contains refined_body_plate.png, weapon_instance.png, foreground_grip.png, chain_and_charm.png and the final flattened review image. Its garment surface patches are reused translations and need pose-specific art review; do not assume every fold is finished.

Folders pilot_v1, pilot_v2, art_pass_04 and other prior versions are retained for reproducibility/history. They are superseded. In particular, art_pass_04 has the rejected upside-down grip. Some shared renderer files in frame_01_v1 still start with frame_00; use manifest frame_index=1 rather than filename alone.

## Recorded weapon construction values

These are current pilot working values, not immutable physical measurements of the game character. Preserve consistency while reviewing them against the visual references.

- Master canvas 340 x 150; local grip G=(77,70), pommel=(34,70), collar=(137,70), tip=(319,70).
- Pilot pommel-to-tip physical master length: 285 working pixels; uniform scale=1.
- Frame 00 grip=(405,225), screen rotation=218 degrees, foreground yaw=25 degrees, camera focal length=1400 pixels.
- Frame 01 grip=(384,244), screen rotation=218 degrees, foreground yaw=28 degrees.
- The entire weapon and corrected grip share a homography recorded in manifest.json. Yaw angles are local construction settings, not user-mandated exact angles.
- Chain hangs 35 working pixels in the pilot and moves from the projected pommel. It is a separate flexible layer.
- Review anatomical arm identity and shoulder contact; those were manually approximated, not established by a 3D rig.

## Work order to finish the task

1. Inspect current frames, references and layers. Identify editing tools you can actually use. Do not invent access to Layer.ai capabilities or claim unavailable tools worked.
2. Finish frames 00–01 consistently: KH2 outfit details, upper-body volume, shoulder anatomy, glove and finger wrap, weapon silhouette/metal finish, chain attachment, transparent edges. Preserve the approved grip orientation. Show the batch for review.
3. Correct/refine run-loop frames 02–07 from their actual source poses, with independent arm/shoulder articulation and consistent weapon projection. The original requested gait labels were not verified; inspect actual left/right foot alternation and timing rather than blindly trusting labels. If extra in-betweens or anatomical corrections are needed, explain and draw real poses.
4. Correct/refine all run-start poses: guard → knee flex → lean → lift intact weapon toward same-arm shoulder → seat carry → push-off → passing knee → first running stride. Match the final start pose to run-loop entry.
5. Draw a new run-stop transition: running carry → braking foot reach → heel contact → knee compression → rear-foot catch-up → lift/lower intact weapon from shoulder → guard settling → approved standing guard. No stop sprites currently exist. Do not manufacture them by reversing start or scaling a body.
6. Transitions should have approximately 7–12 genuinely drawn poses; current start/loop sheets each have eight. Review timing, start→loop, loop seam, loop→stop and stop→idle. Revisit frame 00 in that context.
7. Export and verify each folder separately; deliver review previews and a clear report of finished vs still-pending work. Do not install assets into gameplay without explicit follow-up authorization.

## Output contract and QA

Use design/sprites/smooth/sora/replacement_work/ready/run_start/, run_loop/ and run_stop/ in the project. In Layer.ai use the same logical folders and return files for transfer. Create versioned subfolders; do not overwrite source sheets or rename/delete originals.

Each completed animation needs transparent named frames (00-based), a sheet with documented grid/order, layered source, manifest, and preview GIF or a frame-step viewer. Manifests should record frame paths, durations, loop flag, canvas, body/floor anchors, weapon grip/contact anchors and geometry/projection. Use a calibrated common scale; no frame-by-frame body resizing. Floor contact and airborne phases need coherent anchors, not forced contact for every stride frame.

Check genuine pose changes, left/right gait alternation, anatomy and clothing consistency, rigid handle–collar–shaft alignment, fixed master length, correct same-arm shoulder carry, slight foreground tip direction, natural grip orientation, clean occlusion, no double arms/weapons/old blade fragments, no clipping, real transparency, and normal/mirrored legibility at full and game size. Clear hidden RGB in fully transparent pixels if exporting. Verify every frame opens and each preview decodes, manifests resolve, and original source hashes remain unchanged.

Original source hashes:
- run_start_source.png: 1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256
- run_loop_source.png: 6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0

## Tools, scripts and constraints

Local tools verified in the original workspace: Python with Pillow 10.4.0 and NumPy. Microsoft Paint launcher and .NET were found, but a full painting app workflow was not verified. No GIMP/Krita/Inkscape/Aseprite/ImageMagick were found in checked locations. Tool availability in Layer.ai is unknown and must be inspected there.

The bundled Python scripts document reproducible drawing/compositing decisions. Paths use each script's location. Inspect before running: scripts write specific historical version folders and may overwrite files within those folders. Prefer new versioned destinations. Some scripts consume earlier layer outputs, so copying only the latest flat PNG is insufficient for exact reconstruction. These are offline art helpers, not game scripts.

Legacy design/sprites/generate_sora_sprites.py has old OneDrive/cache paths and is intentionally NOT included or authorized to run. No dependencies need installing just to inspect the artwork.

Do not edit project.godot, .godot/, *.import, export_presets.cfg, autoloads, scenes or gameplay code for this art task. No commits/pushes, installs, deletions or renames without approval. Work in small reviewable steps and explain changes plainly. If a tool fails, report its exact error rather than calling unfinished output complete.

The last built-in tools.image_gen__imagegen attempt returned HTTP 400 moderation_blocked at output stage, category other, request ID 4288281e-c97f-4a51-a91d-fa9e3e10fd33. It was a content/output moderation rejection, not a tool-validation or file-permissions error. Exact arguments/error are included at ready/run_loop/imagegen_single_retry_2026-10-07.json. The original command sandbox also had a separate setup-refresh failure; that is not evidence that the image request had invalid settings.
