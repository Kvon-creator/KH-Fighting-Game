# Next running-cycle drawing plan

October8 progress: this twelve-drawing table was used as the first construction guide, now preserved in gait_refinement_v1. The newer gait_refinement_v2 adds two genuinely drawn intermediates per stride after contact review found a large passing-to-toe-off gap. Its16 phase indices are00/08 contact,01/09 compression,02/10 passing,03/11 late passing,04/12 heel-off,05/13 toe-off,06/14 flight and07/15 opposite-foot pre-contact. New legs/shoes, body bob and free-arm swing are delivered as a separate draft;00's upper artwork remains a reference cutout. Neither draft replaces the eight-pose garment review or reaches final idle quality. See gait_refinement_v2/QA_NOTES.md and memory/Sora_Run_Loop_Gait_Refinement.md.

Following upper pass: gait_refinement_v3 retains those sixteen lower poses/contacts and adds new per-phase chest, lining, waist cloth and arm drawings around independent neck/shoulder/waist controls. Wrist/carry projections follow the holding shoulder, with the approved grip/master retained. The source face/hair/hood details remain. Material/foreshortening/hair motion, timing and transitions still need work against approved idle; see gait_refinement_v3/QA_NOTES.md.

The individual jacket/arm pass is packaged in review_cycle_v5. This does not validate the existing eight source poses as a complete alternating run. The current sequence repeatedly shows similar leading-leg arrangements and uses provisional pelvis estimates/common-floor alignment.

Use this twelve-drawing guide when constructing the missing movement phases. Twelve is a working art target, not a change to gameplay timing or a claim that more frames automatically produce smoother motion.

| Phase | Near leg supports | Far leg supports | Required movement |
| --- | ---: | ---: | --- |
| Contact | 00 | 06 | Leading foot reaches the ground; the other leg trails. |
| Compression | 01 | 07 | Supporting knee/hip absorb weight; body lowers slightly. |
| Passing | 02 | 08 | Swinging thigh passes the support leg; support foot moves behind the hips. |
| Push-off | 03 | 09 | Support leg extends through the toe; opposite knee drives forward. |
| Flight | 04 | 10 | Both feet clear the ground; retain the forward momentum and controlled torso rise. |
| Opposite-foot pre-contact | 05 | 11 | Opposite leg prepares to land; connect05->06 and11->00. |

Near/far identifies the limbs relative to the fixed three-quarter camera. First map them on source thigh/calf/shoe landmarks instead of assuming screen-left equals anatomical left. Do not mirror the whole character to create the opposite stride. Current source drawings remain references; they must not be declared complete phases without checking their joints and contacts.

- Draw genuine thigh/calf/ankle/shoe changes and coherent pelvic/free-arm counter-motion. Preserve the approved KH2 proportions, shoe construction and cloth materials. Use source poses that fit a phase; redraw missing phases rather than stretching a static sprite.
- For an in-place loop, the stance foot travels back relative to the hips while the free foot follows a continuous recovery arc. Do not force every airborne foot onto the floor baseline. Actual world foot planting will need matching to engine movement later.
- Keep the weapon a rigid Kingdom Key with the approved grip orientation, same-arm shoulder carry and slight foreground tip. Body/shoulder/wrist should agree with its projection. Preserve the master geometry; record any new pose anchors.
- Inspect the full cycle and the wraparound at normal and slow playback, with mirrored facing. Check both contacts, leg identity, root drift, body bob, wrist stability, blade overlap and cloth follow-through.
- Resolve the gait/root trajectory before finalizing timings and start/stop seams. Existing review PNG/GIF decoding checks do not certify animation fluidity or gameplay physics.

No image-generation retries, protected engine changes or aerial production are part of this plan.
