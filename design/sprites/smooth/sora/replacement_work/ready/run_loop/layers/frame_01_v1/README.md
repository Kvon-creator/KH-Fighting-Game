# Run-loop frame 01 local correction

Prepared October 7, 2026. Original source preserved. Crop is [445,0,889,450]; this is the second actual pose, not a scaled copy of frame 00. Comparison.png shows source, correction and rigid-axis overlay. Two_Frame_Comparison.png and Two_Frame_Review.gif compare frame 00 and frame 01; the GIF is a two-pose review at 450 ms each, not a finished cycle.

Reuses the exact weapon master from pilot_v3. The compressed body pose uses grip (384,244) and 28-degree foreground yaw, compared with (405,225) and 25 degrees in frame 00. All weapon parts share the same camera transform. The holding arm has a separately drawn tighter elbow bend; fingers follow the projected grip. The jacket clean-plate contours reuse the pilot repair translated to the second pose and still need artwork-specific refinement. Actual source legs and head supply the pose change.

Layer files and manifest.json remain editable. File names beginning frame_00 are shared renderer output names within this frame_01 folder; manifest frame_index=1 identifies the actual frame. Full export naming will be normalized only in a future separate package, without renaming existing files.

Limitations: rebuilt jacket and chain remain simplified; shoulder fit is visually approximate; two frames do not establish full gait continuity. No image generation, final asset replacement or Godot integration.
