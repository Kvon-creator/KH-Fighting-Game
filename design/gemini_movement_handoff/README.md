# Gemini movement handoff

1. Paste `PROMPT.txt` into Gemini.
2. Attach the three files in `references/` first. They contain complete images, not production layers.
3. Provide `MOVEMENTS.md` for the full animation list and delivery details. Ask for one animation at a time if the whole set exceeds the session's capacity.
4. Attach files from `optional_motion_guides/` only when needed. Their filenames distinguish approved reference cycles from unfinished drafts.
5. Bring back the new frames/sheets, previews and manifest, plus Gemini's stated omissions or limitations. Original project art must remain unchanged.

`GEMINI_MOVEMENT_HANDOFF.zip` is a convenience archive: extract it locally and select files for upload. This handoff does not assume Gemini can read a local drive path or unpack an archive.

Essential references:

- `01_Approved_Idle.png`: approved smooth KH2 design and quality target.
- `02_Run_Carry_Grip_Reference.png`: complete running sprite with corrected grip and rigid shoulder carry. Body/clothing remains unfinished; use for carry only.
- `03_Carry_Photo.webp`: supplied shoulder-carry/Kingdom Key reference. Its KH4 clothing is not the character design for this game.

Project context: 2D fighting game, standard KH2 Sora, one direction mirrored for the other, 128px gameplay frames at approximately 96px standing height. New source art is 512px. Idle and crouch transition previews were approved; shimmies still need review; all running clips remain drafts; aerial movement has not been produced. Art files do not implement gameplay.

Local refinement is paused for this trial. The latest unapproved loop03/04 garment candidates are preserved in `ready/run_loop/layers/frame_03_review_v3/` and `frame_04_review_v3/`, but are deliberately not handed over as quality references. Frame04 has a cut edge in the red trailing fabric; collar trim and cloth volume still need work. The full-cycle running reference uses the prior v2 package. If K'von finds the Gemini results unsuccessful, resume this checkpoint after his update.

`SOURCE_FILES.json` records source paths and hashes of copied assets. All copied references retain their original bytes. No layers, helper scripts, protected engine files or private account data are included in the archive.
