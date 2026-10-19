"""Render actual geometry close-ups for the user's tooth correction review."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
assert str(ROOT).lower()==r'D:\KH Fighting Game'.lower()
BASE=ROOT/'design/models/sora/experiments'
for version,label in [('weapon_pipeline_v2','previous_stepped_teeth'),('weapon_pipeline_v3','reference_crown_teeth')]:
    output=BASE/'weapon_pipeline_v3'/(label+'_detail.png')
    if output.exists():raise RuntimeError('Preserve previous detail render')
    bpy.ops.wm.open_mainfile(filepath=str(BASE/version/'weapon_pipeline_pilot.blend'),load_ui=False)
    camera=bpy.context.scene.camera
    bounds=[Vector(point) for point in bpy.data.objects['crown_teeth'].bound_box]
    target=(Vector(tuple(min(p[i] for p in bounds) for i in range(3)))+Vector(tuple(max(p[i] for p in bounds) for i in range(3))))/2
    camera.location=target+Vector((.50,-2,.30))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=.42
    bpy.context.scene.cycles.samples=16
    bpy.context.scene.render.filepath=str(output)
    bpy.ops.render.render(write_still=True)
print('Two geometry close-ups saved; source scenes unchanged.')
