# Character model folders

**Fact or rule:** On October21 Kvon asked for model folders for Riku, Kairi, Xemnas, Larxene and Xigbar. They exist as `design/models/riku`, `kairi`, `xemnas`, `larxene` and `xigbar`, alongside `sora`. Each of the six has an empty `downloads/` subfolder for manually downloaded model files, committed to Git. Kvon briefly had them git-ignored, then said the downloaded 3D assets "can be pushed to Github as well"; the ignore rule was removed and they were pushed on October21. This supersedes the earlier keep-out-of-Git recommendation.

**Downloaded assets (inspected October21, model_inspection_v1):** Six characters plus Kingdom Key, Way to the Dawn and Oathkeeper.

- **Rigged FBX:** Sora `p_ex150.fbx` (KH2 outfit, 49 bones) and Xemnas `b_eh110.fbx` (86 bones), both T-pose at about 0.016-0.02 units tall.
- **Static OBJ:** Riku, Kairi and Larxene, about 150-230 units tall. Riku's and Kairi's skeletons are only in their `.smd` files (Source engine format). Xigbar is `.smd` only (331 nodes).
- **Blender limits:** Blender 5.2 cannot open .smd without an add-on (ask before installing) or a project-written parser. It also cannot open .dae (Collada removed in 5.0); the OBJ/FBX copies cover those.
- **Material fixes:** Kairi's `texture003` material lacks its map_Kd although `texture003.png` exists. The Kingdom Key .mtl uses the ripper's absolute path, but the texture still resolved.
- **Credits:** Ripper readmes say no credit needed (Roxas358 for Riku/Kairi, Zerox for Larxene).

**Why:** The user downloaded the assets and asked to check them. This sets up folders only. It does not confirm a playable roster, movesets or which outfit each character uses. Ask before assuming those.

**Why:** User request. No reason was given; it likely relates to the plan of downloading character models (see [Sora_3D_Sprite_Experiment.md](Sora_3D_Sprite_Experiment.md)).
