# Sora 3D-to-sprite experiment

Kvon chose3D animation rendered into2D sprites. Existing sprite assets and gameplay settings remain unchanged. Blender5.2.2 LTS was located and tested on this24GB-RAM computer; CPU modeling/export and transparent renders work without adding software.

Current weapon: [reference crown review](experiments/weapon_pipeline_v3/Review.html), [Blender model](experiments/weapon_pipeline_v3/kingdom_key_reference_crown.blend), [crown close-up](experiments/weapon_pipeline_v3/reference_crown_detail.png). This uses the newest attached Kingdom Key image, with angled outer prongs and two rounded inner projections. The guard/chain are preliminary and no Sora shoulder carry has been tested yet. Earlier v1/v2 teeth are preserved history.

AI character pilot: [Hunyuan result](experiments/hunyuan_idle_pilot_v1/RESULT.md). The approved idle image was uploaded to the explicitly authorized official Tencent Hunyuan3D2.1 demo. It accepted the job, then returned `event: error` / `data: null`, without a model or cause. Exact input, request, acknowledgement and complete event stream are saved. No retry, paid service, package/model installation or alternate-provider upload followed. No AI Sora mesh, rig or animation exists yet.

Next character work requires a usable mesh, checked from all sides before cleanup, neutral-pose rigging and animation. Preserve the KH2 outfit, smooth cel style and rigid far-hand same-shoulder Kingdom Key carry behind the head, with slight foreground tip. Then render run-start, loop and stop from one fixed orthographic camera; review against approved idle/run-start and match the joins before aerial movement.
