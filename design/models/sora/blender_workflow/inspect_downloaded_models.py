"""Read-only inspection of downloaded character/weapon models under design/models/*/downloads.

Imports each OBJ/FBX into a fresh empty scene, records mesh, material, texture and
skeleton facts, and renders flat textured front/side previews. Source files are not modified.
Run: blender --background --factory-startup --python inspect_downloaded_models.py -- model_inspection_v1
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'model_inspection_v1'
MODELS = ROOT / 'design/models'
OUT = MODELS / version
if OUT.exists():
    raise RuntimeError('Preserve existing inspection; choose a new version')
OUT.mkdir(parents=True)
IMPORTERS = {'.obj': lambda p: bpy.ops.wm.obj_import(filepath=p),
             '.fbx': lambda p: bpy.ops.import_scene.fbx(filepath=p)}
NATIVE_UNSUPPORTED = {'.dae': 'Collada import was removed in Blender 5.0',
                      '.smd': 'Source engine SMD needs an add-on such as Blender Source Tools'}


def render_views(stem, objs):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'FLAT'
    scene.display.shading.color_type = 'TEXTURE'
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = 512, 768
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center, size = (lo+hi)/2, hi-lo
    paths = []
    for view, yaw in (('front', 0), ('side', 90), ('back', 180)):
        cam_data = bpy.data.cameras.new(view); cam_data.type = 'ORTHO'
        cam_data.ortho_scale = max(size.z, max(size.x, size.y)*1.5)*1.08
        cam_data.clip_end = max(size)*20 + 100
        cam = bpy.data.objects.new(view, cam_data); scene.collection.objects.link(cam)
        t = math.radians(yaw); dist = max(size)*5 + 10
        cam.location = center + Vector((dist*math.sin(t), -dist*math.cos(t), 0))
        cam.rotation_euler = (math.radians(90), 0, t)
        scene.camera = cam
        path = OUT / f'{stem}_{view}.png'
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path.name)
    return paths, [round(v, 4) for v in size]


report = []
files = sorted(p for p in MODELS.glob('*/downloads/**/*') if p.is_file())
for path in files:
    ext = path.suffix.lower()
    rel = path.relative_to(MODELS).as_posix()
    if ext in NATIVE_UNSUPPORTED:
        report.append({'file': rel, 'status': 'not imported', 'reason': NATIVE_UNSUPPORTED[ext]})
        continue
    if ext not in IMPORTERS:
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    entry = {'file': rel}
    try:
        IMPORTERS[ext](str(path))
    except Exception as exc:  # record the exact importer failure
        entry.update(status='import failed', error=repr(exc)); report.append(entry); continue
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    images = []
    for img in bpy.data.images:
        if img.source != 'FILE':
            continue
        images.append({'name': img.name, 'path': img.filepath, 'loaded': img.has_data or img.size[0] > 0})
    stem = rel.replace('/downloads/', '__').replace('/', '__').replace(' ', '_').rsplit('.', 1)[0] + '_' + ext[1:]
    entry.update(
        status='imported', mesh_objects=len(meshes),
        vertices=sum(len(o.data.vertices) for o in meshes),
        faces=sum(len(o.data.polygons) for o in meshes),
        materials=sorted({s.material.name for o in meshes for s in o.material_slots if s.material}),
        images=images, missing_images=[i['path'] for i in images if not i['loaded']],
        armatures=len(arms), bones=sum(len(a.data.bones) for a in arms),
        skinned_meshes=sum(1 for o in meshes if any(m.type == 'ARMATURE' for m in o.modifiers)),
        shape_keys=sum(1 for o in meshes if o.data.shape_keys),
        actions=len(bpy.data.actions))
    if meshes:
        entry['renders'], entry['bbox_size'] = render_views(stem, meshes)
    report.append(entry)
    print('INSPECTED', rel, entry.get('vertices'), 'bones', entry.get('bones'), 'missing', entry.get('missing_images'))

(OUT / 'Inspection_Report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('INSPECTION_OK', len(report))
