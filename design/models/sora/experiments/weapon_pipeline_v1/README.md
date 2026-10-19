# Blender 3D-to-sprite pipeline test

Blender5.2.2 LTS successfully built this procedural Kingdom Key interpretation, rendered three transparent512px PNGs on CPU, saved the scene and reopened it for validation. This tests the modeling/render path on the user's computer with24GB RAM. It is not a Sora character model or a finished production weapon.

Open [weapon_pipeline_pilot.blend](weapon_pipeline_pilot.blend) in Blender. It contains a rigid weapon root,24 mesh objects, an orthographic sprite camera and procedural cel materials. The grip, collars and shaft share one local axis. All parts turn with the same root; the chain is rigid in this first test.

Renders: [front three-quarter](front_three_quarter.png), [foreground angle](foreground_tip.png), [opposite angle](opposite_three_quarter.png). [QA_Report.json](QA_Report.json) verifies the saved scene, axis/root relationships, transparent alpha, image margins and original GLB structure.

Use [kingdom_key_flat_colors_v3.glb](kingdom_key_flat_colors_v3.glb) for model exchange. The original `kingdom_key_rigid_pilot.glb` and v2 are preserved diagnostics: glTF export did not translate the procedural color-ramp shader, making their materials white. Disabling nodes also did not fix the palette in Blender5.2. The corrected v3 uses explicit simple Principled materials and passes the four-color check in [Flat_Export_QA.json](Flat_Export_QA.json). The `.blend` remains the source for actual cel-rendered images; the full procedural toon shader is not portable to GLB without baking or rebuilding it.

Blender saved the scene successfully but reported a separate thumbnail-cache write error:

```text
ERROR OpenImageIO write failed: Could not open file "\.thumbnails\large\blender_26204_fbaa2e9c23e6b9b8e1ddf842c2a4bf08.png.png"
```

This is a thumbnail write failure, not an AI content refusal or failure of the model/render outputs. The saved scene was reopened and checked. Future pilot creation disables file previews in that process when supported. Two unused factory brush-material paths also could not be made relative; they are not used by the weapon. No user preferences were saved, software installed, reference art replaced or engine files changed.

The first QA helper used an unsupported `Euler.length` attribute; it failed before writing a report. The corrected helper compares angle components and passed. Later launches use `--python-exit-code 1` so script failures are reflected in the process exit status.

Next character stage: create or generate Sora's mesh, inspect all sides and separate any fused limb/weapon geometry, establish a neutral pose and skeleton, then animate run-start/loop/stop and render with a fixed camera. Keep the Kingdom Key rigidly attached to the far hand for the approved same-arm shoulder carry, behind the head with slight foreground tip direction. The existing sprite artwork remains the style reference. Mesh generation, character rigging, movement and matching the original line art are unfinished; no gameplay integration has been attempted.
