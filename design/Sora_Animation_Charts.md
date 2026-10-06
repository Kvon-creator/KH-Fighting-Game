# Sora animation design charts

Status: approved motion design, updated for smooth-art production. Animation timing and gameplay values remain separate specifications.

## Approved design

| Property | Decision |
| --- | --- |
| Identity | Versatile all-rounder with strong aerial combos. Future Keyblade transformations remain undecided. |
| Appearance | Standard KH2 outfit, Kingdom Key, smooth 2D cel-shaded artwork. |
| Dimensions | 512 x 512 smooth source frames; approximately 384-pixel standing height (equivalent to 96 pixels at 128 x 128). |
| Facing | One drawn direction, mirrored for opposite facing. |
| Idle | KH2 combat stance with subtle breathing. |
| Jump | KH1 normal first jump, then KH2 Aerial Dodge-inspired second jump. Defensive properties are undecided. |
| Attacks | Nine basics: standing/crouching/airborne Light, Medium, Heavy. Down + Heavy launches. |

## Proposed movement chart

Drawing counts do not define gameplay timing.

| Animation | Drawings | Sequence |
| --- | ---: | --- |
| Idle | 10 | Guard, inhale, exhale; planted feet and subtle clothing motion; seamless loop. |
| Duck / stand up | 8 each | Lower into balanced guard / rise back into combat stance. |
| Crouching idle | 4 | Restrained low-guard breathing loop. |
| Forward shimmy | 10 | Lead foot advances, trailing foot follows; preserve guard. |
| Backward shimmy | 10 | Rear foot retreats, lead foot follows; preserve opponent-facing guard. |
| Run start / loop / stop | 4 / 8 / 4 | Accelerate; longer strides with Keyblade over shoulder farthest from opponent; settle into guard. |
| First-jump takeoff / ascent | 3 / 4 | KH1 normal-jump reference poses. |
| Apex / fall / land | 2 / 3 / 4 | Air transition; prepare descent; compress on actual floor contact. |
| Second jump | 8 | KH2 Aerial Dodge-inspired somersault, then return to air pose. |
| Backdash | 6 | Quick backward hop, recoil, landing. |
| Forward air dash | 6 | Anticipation, forward burst, braking pose. |
| Backward air dash | 6 | Backward burst and distinct recoil, facing opponent. |
| Backdash wind | 4 | Separate thin trailing streaks that diminish briefly. |

## Proposed basic-attack chart

Every attack requires readable preparation, commitment, striking and recovery poses. Actual damage windows, hitboxes and cancel timing belong to later move data.

| Attack | Drawings | Preparation -> strike -> recovery |
| --- | ---: | --- |
| Standing Light | 6 | Small draw-back -> short Keyblade thrust -> tight guard return. |
| Standing Medium | 8 | Side wind-up -> horizontal Keyblade slash across his body -> follow-through toward Heavy. |
| Standing Heavy | 10 | Planted rotational wind-up -> wide spinning Keyblade slash -> visible full-body settle. |
| Crouching Light | 6 | Low small draw-back -> quick low Keyblade slash -> balanced low guard. |
| Crouching Medium | 8 | Low torso rotation -> wide low Keyblade sweep -> re-center in crouch. |
| Crouching Heavy | 10 | Compressed grounded wind-up -> upward Keyblade swing that launches the opponent while Sora stays grounded -> grounded recovery or approved air-chase transition. |
| Jumping Light | 6 | Compact wind-up -> quick midair Keyblade slash -> airborne guard. |
| Jumping Medium | 8 | Shoulder rotation -> broad diagonal midair Keyblade slash -> aerial follow-through. |
| Jumping Heavy | 10 | Rotational wind-up -> wide midair spinning Keyblade slash -> airborne recovery. |

Low pose height does not automatically define low-block properties; a downward slash does not automatically cause a spike or knockdown.

## Production and review

1. Approve charts, then review a character model sheet and breathing-idle pilot.
2. Review movement in small batches: crouch/shimmy, run, jumps, dashes.
3. Define combat interfaces and test one complete attack in-engine before expanding implemented combat.
4. Review standing, crouching and airborne attack art batches.
5. Package individual transparent frames, source sheets, named manifest, animation mappings, timing proposals, previews and missing-art inventory.

Use stable foot/body anchors and record weapon grip/tip locations per pose. Account for offsets, scale and facing once. Keep body art and effects separate; wind follows actual movement and has an explicit lifetime. Static key poses are not complete cycles.

Test full weapon extension inside 128 x 128 before producing batches. Ask before enlarging canvases; do not shrink Sora inconsistently to fit attacks. Draw facing right as a proposal. Verify mirrored shoulder placement and silhouette.

The current placeholder uses a 36 x 96 collider, speed 360, jump speed 680 and gravity 1800; it implements only movement, single jump and reset. Do not modify movement to accommodate unsuitable artwork. Art does not implement double jump, dashes or combat.

Exact KH1 jump, KH2 Aerial Dodge and combat-stance poses need visual reference verification before production. New pixel animations are adaptations, not extracted game animations. Gameplay timings, dash limits, invulnerability and air-chase rules remain separate decisions. Version verification, required documentation and real gameplay testing precede engine implementation.

Adapted from the supplied boss methodology: constraints first, clear identity, complete action sequences, calibrated anchors, separate effects, event lifetimes, honest asset inventory and actual engine validation. Boss AI, traps and progression are not requested Sora features.
