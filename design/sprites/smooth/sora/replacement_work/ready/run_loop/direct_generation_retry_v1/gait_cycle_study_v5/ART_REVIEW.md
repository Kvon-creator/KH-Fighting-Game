# Landing-transition candidate, October 12

18 complete poses, 960 ms. All 16 drawings from gait_cycle_study_v4 are retained. Two new articulated drawings show descent into near-leg contact and far-leg contact; the second bridges the cycle wrap. Each splits an existing 80 ms flight hold into two 40 ms poses.

The new knees, shorts, calves, boots and free arm are drawn on complete transparent canvases from the same native references. There are no component sprite layers, image-service retries or interpolated pixel images. The carrying grip, face and blade retain native pixels before whole-body integer bob.

Open [Review.html](Review.html) to compare the previous sixteen-pose candidate at the same cycle time, pause and step through each landing. [Contact_Sheet.png](Contact_Sheet.png), [loop GIF](Preview_512_Loop.gif), [transparent sheet](Sprite_Sheet_512.png), [manifest](manifest.json) and [QA report](QA_Report.json) are included.

This is a focused transition candidate, pending visual approval. Shorter spacing between landing drawings does not establish smoother perceived motion or solve the cloth, sleeve, shoe-depth and torso follow-through issues. Start-to-loop, braking drawings and the final idle join remain unfinished. The stop candidate is preserved and still does not share this loop entry.

Validation checks complete RGBA exports, alpha/margins, connected opaque figures, support-floor and flight clearance, guide lengths, protected upper pixels and source hashes, previous-drawing hashes, GIF timing/repeat and viewer asset links. Viewer controls have not been executed in a browser or JavaScript runtime in this session. No Godot integration or playback test.
