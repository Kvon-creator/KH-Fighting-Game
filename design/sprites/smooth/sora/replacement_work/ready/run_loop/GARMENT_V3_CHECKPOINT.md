# Loop03/04 garment checkpoint history

K'von requested a Gemini trial on October 8, 2026 before further local refinement. Preserve these candidates and resume only after his update if he requests returning to the local method.

Update: K'von subsequently ended the trial and requested returning to local work. Refinement resumed in frame_03_review_v4 and frame_04_review_v4, preserving these v3 candidates. New source waist contours repair the cut edge; narrower collar piping, visible straps and shirt/fold details are in review_cycle_v3. The notes below describe the old v3 candidates, not the new repair status. Full art/gait/seam review remains unfinished.

Following batch: review_cycle_v4 retains03/04 and adds frame_05_review_v3, frame_06_review_v3 and frame_07_review_v3. New per-pose jackets and articulated arms replace shifted templates; selected original hood/pad detail remains and06's old chest arm/guard strip is removed. Rigid carry/grip/chain files and recorded lower-body regions remain exact. Next:00-02 garments and whole-cycle anatomy/gait/root/timing/seams.

`layers/frame_03_review_v3/` and `frame_04_review_v3/` replace the shifted torso template with individually drawn jacket/sleeve/free-arm/holding-arm contours around the source heads and lower-body poses. The four weapon, grip and chain files are byte-identical to v2. Opaque gripping-hand pixels, projected cuff overlap, source/prior-review hashes and the recorded lower-body composite regions passed offline checks.

These are unapproved candidates, not the current packaged animation. Visual review found a horizontal cut edge in frame04's red waist fabric where the source lower plate starts at y212. Restore the upper trailing cloth with a contoured mask, narrow/reposition the large far collar flap, restore visible yellow garment straps and improve cloth volume before building a full v3 cycle. Check frame03's cloth join similarly. The torso drawing is still less polished than approved idle. No new GIF/package, Godot test or aerial work is claimed.

Helpers: `inspect_loop_garment_poses.py`, `refine_loop_garment_poses.py --frame 3|4`. Both derive paths from their own location and assert this workspace. Do not run legacy scripts with old absolute paths. The original sheets and prior v1/v2 reviews remain intact.
