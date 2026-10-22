# Character model folders

**Fact or rule:** On October21 Kvon asked for model folders for Riku, Kairi, Xemnas, Larxene and Xigbar. They exist as `design/models/riku`, `kairi`, `xemnas`, `larxene` and `xigbar`, alongside `sora`. Each of the six has an empty `downloads/` subfolder for manually downloaded model files, committed to Git. Kvon briefly had them git-ignored, then said the downloaded 3D assets "can be pushed to Github as well"; the ignore rule was removed and they were pushed on October21. This supersedes the earlier keep-out-of-Git recommendation.

**Downloaded assets (inspected October21, model_inspection_v1):** Six characters plus Kingdom Key, Way to the Dawn and Oathkeeper.

- **Rigged FBX:** Sora `p_ex150.fbx` (KH2 outfit, 49 bones) and Xemnas `b_eh110.fbx` (86 bones), both T-pose at about 0.016-0.02 units tall.
- **Static OBJ:** Riku, Kairi and Larxene, about 150-230 units tall. Riku's and Kairi's skeletons are only in their `.smd` files (Source engine format). Xigbar is `.smd` only (331 nodes).
- **Blender limits:** Blender 5.2 cannot open .smd without an add-on (ask before installing) or a project-written parser. It also cannot open .dae (Collada removed in 5.0); the OBJ/FBX copies cover those.
- **Material fixes:** Kairi's `texture003` material lacks its map_Kd although `texture003.png` exists. The Kingdom Key .mtl uses the ripper's absolute path, but the texture still resolved.
- **Credits:** Ripper readmes say no credit needed (Roxas358 for Riku/Kairi, Zerox for Larxene).

**Why:** The user downloaded the assets and asked to check them.

**SMD import, October21:** Kvon said "Download Blender Source Tools and work on the .smd files first", which authorizes this add-on install. The install is Source Tools 3.4.2 from GitHub tag 3.4.2 (HTTPS archive SHA256 0979eb81203ccd1e6f9ac96cb88f54027759d53e922d7c14078ada94a5d778a6; the official page's download link is plain HTTP). It is extracted only to git-ignored `.local/blender_addons/addons/io_scene_valvesource` and registered inside script processes. It is not installed into Blender's user preferences, which are outside the project.

- **Import script:** `sora/blender_workflow/import_smd_models.py -- smd_import_v1` saved `xigbar/`, `riku/` and `kairi/` `<name>_rigged_smd_import_v1.blend`, with relative texture paths and previews in `design/models/smd_import_v1/`.
- **Rigs:** Xigbar has 331 bones, Riku 213 and Kairi 265. All vertices are weighted, and a 45-degree bone test deforms each mesh. "SMD only supports 128 bones" is only an importer warning.
- **Placeholder bones:** `NotABone*` root bones (Xigbar 15, Riku 4, Kairi 10) are rip placeholders.
- **Up axis:** Xigbar's SMD is Y-up and needs `upAxis='Y'`; Riku and Kairi are Z-up. Xigbar's two Arrowguns are separate pieces at his feet.
- **Bone display mesh:** each blend contains an `smd_bone_vis` sphere mesh for drawing bones. Find the body mesh by its Armature modifier.

**Why:** User requested the add-on and SMD work before setting up Sora. This sets up folders only. It does not confirm a playable roster, movesets or which outfit each character uses. Ask before assuming those.

**Why:** User request. No reason was given; it likely relates to the plan of downloading character models (see [Sora_3D_Sprite_Experiment.md](Sora_3D_Sprite_Experiment.md)).
