# Sora 3D-to-sprite experiment

**Experiments deleted, October21:** Kvon instructed deleting `design/models/sora/experiments/` and pushing all changes. Done; paths below under experiments/ no longer exist. Weapon v1-v3 and Hunyuan pilot are in Git history (commit 7cdbb40); weapon v4 and character blockouts v1-v5 were never committed but are reproducible from `blender_workflow/` scripts. Kvon then proposed downloading Sora's model from The Models Resource (https://models.spriters-resource.com, Kingdom Hearts tag) instead of building from scratch. The site returns a Cloudflare challenge (403) to automated tools; do not bypass it. Kvon downloads manually into `design/models/sora/downloads/`; extract into a separate folder and inspect before use. Kvon downloaded the models (Sora KH2 rigged FBX `sora/downloads/p_ex150.fbx` plus Kingdom Key OBJ) and allowed pushing them to GitHub; see [Character_Model_Folders.md](Character_Model_Folders.md). Use the downloaded Sora rather than the procedural blockout going forward. Blender5.x has no Collada import, so a .dae-only rip needs a converter (ask before installing).

**Why:** User instructions; accurate game models instead of procedural approximation.

**Sprite pilot, October21:** Kvon approved ("Let's do this") a Sora pilot covering normalize, cel style, Kingdom Key attachment, sprite camera and one idle-like test frame. `blender_workflow/build_sprite_pilot.py -- sprite_pilot_vN`; v4 is current (`design/models/sora/sprite_pilot_v4/`).

- **Model facts:** KH2 bone names are L/R_kata (shoulder), ude1/ude2 (arm), te (hand), buki (weapon socket), momo/sune/ashi1 (leg), with center/hara/mune/kubi/atama for the spine and head. Sora faces -Y.
- **Lessons:** IK pole constraints twisted the legs; use the analytic two-bone `aim` solver instead. Weld duplicate vertices before outlining. Freestyle silhouettes on the low-poly rip darken everything; use a heavy external contour plus faint interior lines.
- **Key handling:** the Key OBJ is offset ~300 units from origin, and its loose chain links lie in a row and must be removed.
- **Result:** soles land at y=470 like the approved idle. The pose is approximate and the image is not yet user-approved.

**Why:** User approved the proposed Sora pipeline pilot.

**Pilot approved, October21:** Kvon said "v4 looks great. Continue to the next step." Keep v4's look (cel ramp, outer contour + faint interior lines, camera yaw -40, framing). The next step was the refined pose plus breathing idle loop. `idle_loop_v3` is the current candidate: 10 distinct frames on the approved 1480 ms timing, Key re-placed rigidly each frame, follow-through lag 0.12 cycle. It is pending the user's review and not tested in Godot. Lessons: a bone-parented Key wobbles when arms are re-solved per frame, and a symmetric breath without lag produces duplicate ping-pong frames.

**Why:** User approval of v4 and instruction to continue.

**Grip correction, October21:** Kvon said the breathing is good, but the idle pose needs work and the Keyblade was held the wrong way. In v3 the Key was rotated 90 degrees about its blade (guard edge-on, teeth up) and anchored at the `buki` socket beyond the fingers. Rule now, per the approved idle: the guard's flat face toward the camera, teeth pointing down, and the fist inside the guard at the palm (midpoint of `te` and `buki`). This is `idle_loop_v4`. `idle_loop_v5` (current) adds automatic finger curl, but the rip's palms don't face the handle, so the fingers only partly close (mean ~5.6 cm from the handle). Wrist roll is still to do. Keep the breathing parameters.

**Why:** User correction of the grip orientation.

**Model choice and teeth direction, October21:**

- **Keep the KH2 rip.** Kvon rejected switching to a higher-quality Smash Ultimate Sora because it would outclass the other KH2-era character models. Keep the roster visually consistent, and fix limitations by rigging (wrist roll, then possibly added finger bones) rather than by swapping in models.
- **Teeth up.** Kvon asked to rotate the wrists and flip the Keyblade so the teeth face up. This supersedes v4/v5's teeth-down reading of the approved idle; the guard still faces the camera.
- **idle_loop_v6 (current):** a per-hand wrist twist about the forearm (R -165, L -150 degrees) plus finger curl, chosen by search. Fingers now average 3.4 cm from the handle (was 5.6 cm).

**Why:** User decisions on roster consistency and Keyblade orientation.

**Smash pose reference, October21:** Kvon said he has no idea how to use Blender and asked me to pose Sora from a Smash Ultimate idle screenshot, saved as `design/references/sora_smash_idle_pose_reference.png` (SHA256 44367CE9...7A7B). It is a pose reference only; the KH2 model and three-quarter sprite camera stay.

- **The pose:** wide toes-out stance, mild knee bend, upright torso, slight head tilt, both hands low in front, guard toward his right side facing out, blade up past his right shoulder (~49 degrees), teeth up, Key tip near head height (grip-to-tip 1.0 m).
- **Current: `idle_loop_v8`**, with `Reference_vs_3D_pose.png`, which pairs the reference with a near-front check render and the sprite view.
- **Known gap:** the left hand sits ~8 cm from its handle spot.
- **Don't ask Kvon to pose in Blender;** pose from references he supplies.

**Why:** User supplied the reference and asked me to do the posing.

**Posture correction, October21:** Kvon said part of the problem is Sora's posture and asked him to hunch over a little while bending his elbows to hold the Keyblade.

- **v9:** adds lower-spine `hara` 7 deg + chest `mune` 9 deg lean, and a neck `kubi` -10 deg counter so he looks ahead. The grip moves in toward the body so the elbows bend, but it rose too high.
- **`idle_loop_v10` (current):** same hunch with the grip lowered back to waist height.
- **Check renders:** v10+ also renders `side_check_frame00.png` (profile), because forward lean is invisible from the front views.
- **Known gap:** the left hand is ~5 cm from its handle spot.

**Why:** User posture correction.

**Stronger hunch and proper grip, October21:** Kvon asked for a little stronger hunch, then whatever arm changes are needed for Sora to properly hold the Keyblade.

- **Hunch:** v11 raises it to hara 10, mune 12, neck counter -16 degrees. If a hand still misses the grip after wrist correction, the shoulder (`kata`) swings toward it, capped at 20 degrees per step.
- **Grip point:** v12 measures the grip at the visible hand, the centroid of vertices on the `te` and `yubiB` bones. The te/buki midpoint had left both fists below the handle.
- **`idle_loop_v13` (current):** slides the Key 5 cm (`grip_shift`) so the fists wrap the handle inside the guard.
- **Remaining offset:** the left hand is ~2.3 cm from its target.
- **Status:** pending user review.

**Why:** User requested the stronger hunch and a correct grip.

**Palm-up grip suggestion, October22:** Kvon suggested rotating the front wrist so its palm faces up and the other wrist the opposite way, then sliding both hands up toward the hilt. Implemented as `idle_loop_v14`, pending review.

- **Front hand = right hand,** the one nearer the three-quarter camera.
- **Palm tracking:** rest-pose (T-pose) palms face -Z with the thumb bones pointing forward. The palm direction is tracked through the te bone.
- **Fingers:** curl toward the palm.
- **Wrist search** (10-degree steps): R twist 110 (palm-up score .65), L 80 (palm-down .52).
- **Hand slide:** `grip_shift` .11 slides the hands higher on the handle.
- **Review image:** `Hands_v13_vs_v14.png`.

**Why:** User's own grip suggestion.

**Fist wrap, October22:** Kvon asked for the best and easiest way to make both hands appear to wrap the handle, then approved the proposed bend approach. It is implemented as a `fist_wrap` shape key: each finger/thumb vertex is rolled around the handle line from its knuckle, then converted back to rest space through the vertex's skinning matrix. The hand centre is frozen in te-bone space first (`HAND_LOCAL`), so the curl doesn't move the grip.

- **v15:** the plain curl was too weak.
- **v16:** `WRAP_GAIN` 1.7 curls harder; the left fist forms, but the palm-up right fingers lay along the handle.
- **`idle_loop_v17` (current):** squares each wrist so the fingers cross the handle before wrapping. Both hands form fists and the front fist reads as wrapping the handle inside the guard.
- **Lesson:** fingers must cross the handle to wrap it.
- **Status:** pending review.

**Why:** User-approved approach to finishing the grip.

**Fact or rule:** On October19 Kvon requested experimenting with3D models instead of continuing the flat sprite batch. He selected "Animate it and render2D sprites". Use Blender for character cleanup/modeling, rigging, animation and transparent sprite renders; this is not a decision to switch gameplay to3D. Preserve all existing sprite work and keep the approved KH2 outfit, smooth cel style, far-hand same-shoulder carry and fixed connected Kingdom Key.

**Why:** The user explicitly chose the3D-to-2D route. No additional reason was provided.

**Verified first step:** The installed Blender5.2.2 LTS at `C:\Users\kvong\AppData\Local\Programs\Blender5.2\blender.exe` runs. `design/models/sora/experiments/weapon_pipeline_v1/` contains a procedural rigid Kingdom Key test, saved/reopened `.blend`, palette-corrected sibling GLB, three transparent512px CPU renders and QA. It is not a Sora character, rig or animation. No installation or gameplay/engine change. Original GLB and v2 lost shader colors and are preserved diagnostics; use flat_colors_v3 (explicit simple Principled materials, four-color QA passed) for exchange and the `.blend` for toon renders. A thumbnail-cache save error did not affect the model or PNGs; see the pilot README. Future builds disable preview caching in that process.

**AI pilot authorized, October19:** The user selected "Test AI generation using the approved idle image on Tencent’s Hunyuan3D2.1 Hugging Face demo". Upload that specific reference to the official `tencent/Hunyuan3D-2.1` Space and generate/review one model. No paid service, new local model/addon/package installation or gameplay replacement included. The model may need major mesh cleanup and a neutral pose before rigging; do not treat a generated posed mesh as automatically animation-ready. Hunyuan2.1 live metadata/config reported RUNNING with textured generation exposed at inspection; this does not guarantee anonymous GPU quota. TripoSR's official demo reported a runtime error. Do not assume earlier ComfyUI installation approval includes new3D packages.

**AI pilot result:** `design/models/sora/experiments/hunyuan_idle_pilot_v1/` preserves the exact reference/hash, live API schema, request, upload/submission responses and complete SSE. The upload succeeded and generation_all was accepted HTTP200, eventID93a82ac3e9e647a5a407e6585d1c16a9. Terminal response was exactly `event: error` / `data: null`; no model or cause supplied. Record as unspecified service execution failure after acceptance, not a known content refusal, permissions rejection, quota or outage. No automatic retry. There is no AI Sora mesh to rig yet.

**Tooth correction:** Kvon corrected the first procedural Keyblade teeth as wrong. V1 used triangular saw-like points. `weapon_pipeline_v2/` is a preserved sibling with three broad flat-ended stepped teeth, actual old/new close-up renders and Review.html using the supplied KHIV weapon reference. Its saved scene, rigid axis/root, transparent renders and flat-palette GLB pass checks. Shape remains a review candidate, not user-approved exact geometry. Use v2 for current tooth review; do not promote v1. The helper files accept explicit version arguments. Model orientation tests rotate about the shaft, not an actual Sora shoulder carry; that rig and foreground movement remain pending.

**Newest reference supersedes v2:** Kvon then attached a640px diagonal Kingdom Key image and said "Use this model for reference." Only an image was supplied, not mesh data. `weapon_pipeline_v3/kingdom_key_reference_crown.blend` and matching GLB are the current candidates, with reference_crown_detail.png, reference_crown_front.png and Review.html. The blade head now has slanted outer prongs, pointed recesses and two rounded inner projections, using hand-traced image landmarks. The hidden root extends inside the shaft; initial v3 trace files remain diagnostics before that connection fix. The newest reference replaces the earlier three-square-tooth interpretation. Guard/chain details remain preliminary; no claim of exact original geometry or user approval. Overall entry is `design/models/sora/README.md`. No new AI generation retry followed the Hunyuan failure.

**Character model request, October21:** Kvon asked to work with the installed Blender tool in VS Code to generate Sora's3D model. That tool is the Blender Development extension (jacqueslucke0.0.31, no Blender path configured); the agent drives the same Blender5.2.2 by command line, and scripts also run via the extension. `blender_workflow/build_character_blockout.py -- character_blockout_vN` builds a procedural neutral A-pose KH2 Sora (lofted tubes + subdivision, cel emission materials, Freestyle lines, four orthographic review views). v1 preserved; v2 adds back hair, fingerless-glove skin fingers and chunkier shoes. Pending user review; no rig/animation/Keyblade/GLB yet.

**Proportions approved, October21:** Kvon said the v2 proportions are good and asked to continue refining the face and details. Keep v2 body proportions fixed. v3 adds face features, side hair, pockets, hem trim and face close-up renders; v4 (current) shrinks the nose, sets the eyes into the face and fits the shoe straps to the shoe. Face/detail art is not yet approved.

**Why:** The user explicitly approved proportions and requested face/detail refinement next.

**Eye/hair correction, October21:** Using his supplied KH2 render (`design/references/sora_kh2_full_render.png`), Kvon said v4 eyes were a little too big and rounded on the bottom and the hair spikes needed more detail. v5 (current): smaller almond eyes with arched upper lid and nearly flat lower edge, raycast-projected onto the head surface; 38 flatter, sharper two-tone blade locks with a center bang. Head loft normals point inward, so surface offsets must flip toward -Y. Use that render as the KH2 design reference for further outfit detail.

**Why:** User correction against the supplied reference image.

**Why:** User request; procedural modeling avoids new installs and the failed Hunyuan route.

**Crown correction, October19:** Kvon said v3's crown was still not quite right compared with his reference. He did not specify an individual feature. `weapon_pipeline_v4/Review.html` is the new comparison candidate; use `kingdom_key_crown_v4_review.blend` and `kingdom_key_crown_v4.glb`. V4 reduces and smooths the round tips, adjusts the recesses and slanted outer ends, and reduces plate thickness from .045 to .018. The other23 meshes retain their geometry, root and grip/shaft axis. Old/new closeups use the same diagonal camera and light. Saved scenes were reopened; crown manifold/outward normals, transparent renders, whole-weapon fit and four-color GLB checks passed. All previous models/renders remain. These checks do not establish an exact reference match or user approval; landmarks are still estimates from the inline image, not calibrated image/mesh data. This replaces v3 as the current review candidate only. No character-generation retry, new installation or engine change.

**One-handed pose, October22:** Kvon said "Nevermind" to finishing the two-handed v17 grip and asked for Sora holding the Keyblade with one hand, blade angled toward his feet. These defaults were chosen and reported, not specified by Kvon:

- **Grip:** right hand (the sprite camera's front hand) at the hip.
- **Left arm:** relaxed.
- **Carried over:** the v11+ hunch and stance, the fist wrap and squared wrist on the right hand only, and the breathing loop.

Run with `build_sprite_pilot.py -- one_hand_vN` (folder `design/models/sora/one_hand_vN`).

- **v1:** the blade stood vertical and dipped below the floor.
- **v2:** the blade tilt is solved from the real grip so the tip angles out toward his right foot.
- **v3 (current):** the tip sits 10 cm up so the teeth clear the soles; lowest row 471.

Pending review.

**Why:** User's new pose request replacing the two-handed grip effort.

**Battle-ready one-handed pose, October22:** Kvon asked for suggestions to make the one-handed pose battle-ready and then said "Build it the way you've recommended". All five suggestions are built, using `design/references/Sora_battle_stance.gif` as the stance guide:

1. **Staggered stance:** left foot leading, right foot back and turned out, deeper knees.
2. **Body turn:** about 30 degrees toward the opponent, chin down, eyes toward the opponent.
3. **Keyblade:** low in the right hand, angled down and back, away from the opponent (the original idle rule).
4. **Guard hand:** the left hand up at chest height.
5. **Combat bounce:** a 1000 ms, 10-frame knee bob.

Run with `build_sprite_pilot.py -- battle_vN` (`design/models/sora/battle_vN`). POSE targets are in the turned body frame; feet need the turn added explicitly because `ashi1` doesn't inherit rotation.

- **v1:** the guard arm stuck out straight.
- **`battle_v2` (current):** bent guard elbow nearer the chest.

Pending review.

**Why:** User accepted the recommended battle-ready changes.

**KH2 pose-sheet reference, October22:** Kvon supplied a four-pose KH2 Sora illustration sheet, saved as `design/references/sora_kh2_pose_sheet.png`, and asked to emulate the top-right pose. That pose is a low, wide guard crouch: facing nearly forward, hunched, Key in the right fist at the hip, blade swung out level to his right with teeth up, left arm hanging by the thigh. It is built as `battle_v3` (current) with the combat bounce. The facial expression (gritted teeth) is not possible because the rip has no face rig. A first battle_v3 build silently duplicated v2 because of a failed edit and was deleted and rebuilt.

**Why:** User-supplied pose reference.

**Mirrored pose-sheet copy, October22:** Kvon asked me to look again closely at the top-right pose, mirror it, and copy it exactly. On close inspection that pose is two-handed (both fists on the handle low between the thighs), not one-handed as battle_v3 assumed.

- **The mirrored pose:** blade level out to his LEFT, tip a little up, grip slightly left of centre, very wide toes-out squat, hunched, head down and turned to his left (toward the opponent at screen right).
- **Build:** `battle_v4+` uses `TWO_HAND_BATTLE`. The right fist is on the pommel side and the left fist sits beside it toward the guard (`L_hand_along_handle` +.075). Fist wrap is on both hands.
- **Bug fix:** v4 first ran as a single-frame pilot because LOOP didn't include two-handed battle versions; fixed and rebuilt.
- **`battle_v5` (current):** hips higher (drop .19), feet ±.56, blade rising more.
- **Comparison image:** `Mirrored_Reference_vs_3D_pose.png`.
- **Not reproducible:** the gritted-teeth face and the hanging chain with the Mickey token.

**Why:** User instruction to mirror and copy the reference exactly.

**Standing angle, October22:** Kvon asked to change the angle Sora stands at to match the reference. Interpreted as his body orientation in the sprite view; the three-quarter camera (yaw -40) is unchanged. `battle_v6` (current) turns the whole body -25 degrees (blade and hand targets turn with it) so he faces nearly at the camera, turned slightly toward screen right, as in the mirrored drawing. Comparison image: `Mirrored_Reference_vs_Sprite_v5_v6.png`.

**Why:** User correction of the stance angle.

**Keyblade angle and leg spacing, October22:** Kvon asked to change the Keyblade's angle too, then (mid-task) to bring his legs a little closer together.

- **`battle_v7`:** sets the blade from screen-space measurements of the mirrored drawing (`screen_blade`: a 20-degree on-screen rise, tilted 37 degrees toward the sprite camera), so its apparent length matches the drawing (~0.57 of body height vs v6's 0.71).
- **`battle_v8` (current):** feet at +/-.46 m (were .56), and the left fist slightly nearer the right on the handle.
- **Known gap:** the left fist is ~10 cm from its exact handle target.
- **Comparison image:** `Mirrored_Reference_vs_Sprite_v7_v8.png`.

**Why:** User corrections to match the reference.

**Both hands on the handle, October22:** Kvon said battle_v8 is almost perfect and asked to make both hands grab the Keyblade handle.

- **`battle_v9` (current):** `auto_reach` moves the whole grip (right fist + Key) toward the left hand in up to 8 steps until the left fist lands on its handle spot.
- **Result:** the left fist is 1.2-1.7 cm from its spot in every frame, and both fists are inside the guard.
- **Measurement fix:** the per-frame grip metric had ignored `body_turn_deg` (it reported ~9-10 cm for v6-v8); fixed.
- **Comparison images:** `Hands_v8_vs_v9.png` and `Mirrored_Reference_vs_Sprite_v8_v9.png`.

**Why:** User request to finish the two-handed grip.

**Left palm to screen, October22:** Kvon asked if I can rotate the wrists (answered without changing anything), then asked to rotate the wrist not attached to the Keyblade so its palm faces the screen. The Key anchors to the right fist, so that wrist is the LEFT one.

- **`battle_v10` (current):** twists the left wrist about the forearm (search result -160 degrees) toward the sprite camera, with a palm-to-camera score of 0.62 (about 50 degrees from square).
- **Squaring skipped:** the left wrist is not squared to the handle, because squaring would undo the twist.
- **Grip:** the left fist stays ~2.5 cm from its handle spot.
- **Comparison image:** `Hands_v9_vs_v10.png`.

**Why:** User request.

**Palm slightly back, October22:** Kvon asked to slightly turn the left palm back toward Sora. `battle_v11` (current) applies `L_palm_back_deg` 25: both directions are tried and the one facing the palm more toward his hips is kept. The twist goes from -160 to -135 degrees; palm-to-camera drops from 0.62 to 0.57. The left fist is ~2.2 cm from its handle spot. Comparison image: `Hands_v10_vs_v11.png`.

**Why:** User fine-tuning of the left palm.

**Palm a little more, October22:** Kvon asked to rotate it a little more. `battle_v12` (current) uses `L_palm_back_deg` 45, about 20 degrees past v11. The twist goes to -115 degrees; palm-to-camera is now 0.44 and the palm faces slightly toward the body (0.10). The left fist is ~1.9 cm from its handle spot.

**Why:** User fine-tuning.

**battle_v12 approved for now, October22:** Kvon said "That is perfect for now." Treat `battle_v12` (mirrored pose-sheet guard crouch, both fists on the handle, left palm turned 45 degrees back from the camera, combat bounce) as Sora's current approved battle idle. "For now" means it may be revisited. Don't change it unless asked. Rebuild with `build_sprite_pilot.py -- battle_v12`; later pose work should use new version names. Not yet tested in Godot or integrated into gameplay.

**Why:** User approval.

**Gemini animation request refused, October22:** Kvon asked me to message Gemini in Brave, in his "Sora Battle Poses Character Sheet" conversation (the source of the pose sheet), and request a full animation of the reference pose.

- **Setup:** the dedicated profile (`Start-BraveGemini.ps1`, port 9222) was launched. Kvon signed in himself and opened that chat (tab 7EE1DA69611AD56975A47980E7697CAC, `/app/e3e4ea273a444d54`). `gemini_cdp.mjs` now also allows `design/models/sora/gemini_animation/attempt_NN` output.
- **Request:** one prompt (`SORA_POSE_SHEET_IDLE_ANIMATION.txt`) asked for an 8-frame 4x2 looping battle-idle sheet of the top-right pose.
- **Result:** Gemini replied exactly "I can't generate the image you requested right now due to interests of third-party content providers. Please edit your prompt and try again." No image was returned. This is a provider content refusal (receipt status `provider_block`).
- **No workaround:** no retry or rewording to evade it. Kvon may prompt Gemini himself.

**Why:** The user requested it; the provider refused.

**Next attempts chosen, October22:** Kvon offered two attempts: a new fully articulated 3D Sora from the pose sheet, or a 2D sprite with the same loop as the current 3D model. If he likes neither, we go back to the PS2-model workflow. He picked the 2D sprite version first.

- **Scripts:** `render_2d_style.py -- battle_v12 sprite2dN` re-renders the approved battle_v12 `.blend` with a cooler, larger cel shadow and darker, thicker Freestyle ink; the source `.blend` is not modified. `stylize_2d_frames.py battle_v12 sprite2d_vN` adds a crisp outer ink rim and lifts saturation slightly. Then `package_idle_loop.py` runs.
- **v1:** palette snap + median filter washed out colours and muddied the face.
- **v2:** a thick glow-like rim.
- **`sprite2d_v3` (current):** crisp dark ink at 2.2 + 1px rim. Same 10 frames, 1000 ms.
- **Lesson:** Freestyle linestyle colours are LINEAR (v1's .07/.06/.11 displayed as grey-lavender ~75/69/95).
- **Status:** pending Kvon's review. The new 3D-model attempt has not been started.

**Why:** User choice.
