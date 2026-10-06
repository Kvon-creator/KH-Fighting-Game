# Sora model-sheet and breathing-idle drawing guide

Status: manual-production specification. This guide contains no completed sprite art or animated preview. Gameplay files are unchanged. Pixel locations and timing below are starting proposals to review against drawn art.

## Approved brief

Sora: standard Kingdom Hearts II outfit, Kingdom Key, recognizable KH2 combat stance. Pixel art, transparent 128 x 128 frames, approximately 96 pixels tall in the standing reference. Draw facing right and mirror for the opposite side. Preserve his versatile all-rounder identity and expressive aerial-combo potential.

## 1. Set up the canvas

Use your available pixel-art editor; no particular editor or installation is required.

1. Create a transparent 128 x 128 canvas. Coordinates start at the top-left: x increases rightward, y downward.
2. Add non-exporting guides: center axis x=64, foot-contact line y=112, standing hair-tip guide near y=16. These make approximately 96 pixels of standing height.
3. Keep all visible pixels inside the canvas. A bent-knee combat pose may be shorter than the standing model; do not stretch it to force exactly 96 pixels.
4. Draw with a one-pixel pencil and inspect both at 100% and enlarged with sharp pixel scaling. Avoid soft brushes and blur.
5. Separate guides, body, Kingdom Key and optional chain into editor layers. Export with guides hidden and real transparency.

The foot-contact guide is an alignment reference, not a physics collider. Do not place both shoes at the same height if perspective makes one appear higher: lock each shoe's original contact pixels during idle.

## 2. Model-sheet deliverables

| Drawing | Purpose | Check |
| --- | --- | --- |
| Front standing | Establish outfit, anatomy and approximately 96-pixel height. | Recognizable proportions and costume. |
| Right-facing side | Establish profile and weapon proportions. | Clear face, shoes, hair and Keyblade silhouette. |
| Right-facing combat guard | Master frame for idle. | KH2 stance, bent knees, staggered feet, balanced grip; match a visual reference before finalizing. |
| Isolated Kingdom Key | Lock weapon length and recognizable shape. | Silver key-shaped blade, gold guard, grip and chain charm; check visual reference for exact details. |
| Palette strip | Keep colors consistent across frames. | Every frame uses the same approved swatches. |

Suggested starting palette families: three hair browns, three skin shades, dark outline, three outfit darks, light trim, red accent pair, yellow/gold pair, three blade grays and a blue eye accent. These are proposals; choose final swatches from the approved visual reference. Readability matters more than preserving tiny details at any cost.

Before animating, test the full character and weapon inside the canvas. Do not shorten the weapon or shrink individual poses inconsistently to make them fit. Return for a canvas decision if necessary.

## 3. Build the eight-frame idle

Start from the reviewed combat-guard drawing. Duplicate its canvas for each frame, then redraw small areas. Do not translate the entire sprite upward to simulate breathing: shoes must stay planted and anatomy must remain connected.

Negative vertical offsets move upward. All offsets below are relative to the master frame and affect the upper torso/head locally, not the whole image.

| Frame | Breath phase | Upper-body change | Secondary motion | Hold |
| --- | --- | --- | --- | ---: |
| 00 | Neutral | Master guard; shoulders and head at reference height. | Chain rests naturally. | 160 ms |
| 01 | Begin inhale | Expand chest contour subtly; shoulder height unchanged. | Jacket highlight shifts by at most one pixel. | 140 ms |
| 02 | Inhale | Lift shoulder/head contours approximately 1 pixel; connect neck and arms by redrawing. | Elbows and weapon grip follow smoothly. | 140 ms |
| 03 | Full inhale | Keep 1-pixel lift; slightly fuller chest contour. | Chain lags the small weapon adjustment. | 200 ms |
| 04 | Begin exhale | Maintain height while softening chest contour. | Chain begins settling. | 160 ms |
| 05 | Exhale | Return shoulders/head to reference height. | Grip follows without blade bending. | 140 ms |
| 06 | Settle | Reference height; relaxed chest contour. | Subtle chain/clothing settling. | 140 ms |
| 07 | Loop bridge | Return toward frame 00 contours; no sudden pose change. | Chain settles near its initial shape. | 200 ms |

Total proposed cycle: 1,280 ms. Frames are eight time samples; small repeated pixel regions are expected. Do not invent a large head bob, swaying feet, changing hair length, or changing weapon proportions to make every frame look different.

The weapon may move slightly with the hands, but stays rigid. Both hands must stay connected to the approved grip. Use no idle motion trails, dust or glow.

## 4. Record anchors and attachment points

For every frame, record these actual measured pixel positions after drawing:

- Body anchor: proposed (64,112), constant within the sheet.
- Front and rear foot-contact points: fixed in idle.
- Weapon grip: the point where hands hold the weapon.
- Weapon tip: end of the blade, following the rigid weapon.
- Head reference: useful for checking breathing motion and accidental scale changes.

Do not fill these measurements with guessed anatomy values. Mirroring pixel locations uses x_left=127-x_right on a 128-pixel canvas. Future engine node transforms must apply facing and offsets once; do not mirror the coordinates a second time.

## 5. Export package

Proposed names, created only when art exists:

- sora_model_front_v1.png
- sora_model_side_v1.png
- sora_model_guard_v1.png
- sora_kingdom_key_reference_v1.png
- sora_idle_00.png through sora_idle_07.png
- sora_idle_sheet_v1.png: four columns by two rows, 512 x 256 pixels; frame order 00-03 on top, 04-07 below; no padding.
- sora_idle_manifest.json: measured anchors, attachment points, frame filenames, holds above, loop=true, canvas size and palette reference.
- Preview loops in both facings, enlarged with sharp pixel scaling and shown at native size against the arena.

Keep label-bearing reference boards separate from transparent gameplay frames. The eight drawings are body frames; effects belong in separate files when later requested.

## 6. Review checks

1. At native size, recognize Sora's KH2 outfit, hair, shoes and Kingdom Key.
2. Confirm master stance against the selected KH2 visual reference; do not call an approximation an extracted animation.
3. Confirm every body frame is exactly 128 x 128 with transparent background and no clipped blade or hair.
4. Overlay frames: foot-contact pixels should not drift; head motion should stay restrained.
5. Play the loop at proposed timing: breathing should read without obvious hopping or a seam between 07 and 00.
6. Check hands, blade shape, chain attachment, outfit features and palette consistency across all eight frames.
7. Mirror preview and check that the pose remains readable; visible weapon handedness switches as approved.
8. Record missing frames honestly. A model sheet or these instructions do not constitute a completed idle animation.

Next checkpoint: review actual model-sheet drawings and idle playback before expanding movement and attack art. Engine integration needs its own version/documentation checks and actual gameplay test. No engine test is claimed for this drawing guide.
