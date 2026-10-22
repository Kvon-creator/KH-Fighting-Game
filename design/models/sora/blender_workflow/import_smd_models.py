"""Import the downloaded rigged .smd models with Blender Source Tools (project-local copy).

Source Tools 3.4.2 lives in the git-ignored .local/blender_addons/addons and is registered
only inside this Blender process. Each SMD is imported into a fresh scene, its materials get
the matching PNG from the same folder, and a .blend plus front/side/back previews are saved.
Downloaded source files are not modified.
Run: blender --background --factory-startup --python import_smd_models.py -- smd_import_v1
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'smd_import_v1'
MODELS = ROOT / 'design/models'
sys.path.insert(0, str(ROOT / '.local/blender_addons/addons'))
import io_scene_valvesource as source_tools  # noqa: E402
assert source_tools.bl_info['version'] == (3, 4, 2), source_tools.bl_info['version']
# (file, up axis): Xigbar's rip is Y-up and imported lying down with the default Z.
TARGETS = {'xigbar': ('downloads/Xigbar.smd', 'Y'), 'riku': ('downloads/Riku_KH2/Riku_2.smd', 'Z'),
           'kairi': ('downloads/Kairi_KH2/Kairi_KH2.smd', 'Z')}
REVIEW = MODELS / version
if REVIEW.exists():
    raise RuntimeError('Preserve existing import; choose a new version')
REVIEW.mkdir(parents=True)


def textured(mat, image):
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nodes.new('ShaderNodeTexImage'); tex.image = image
    links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])


def render_views(stem, meshes):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'FLAT'
    scene.display.shading.color_type = 'TEXTURE'
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = 512, 768
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    center, size = (lo+hi)/2, hi-lo
    names = []
    for view, yaw in (('front', 0), ('side', 90), ('back', 180)):
        cam_data = bpy.data.cameras.new(f'review_{view}'); cam_data.type = 'ORTHO'
        cam_data.ortho_scale = max(size.z, max(size.x, size.y)*1.5)*1.08
        cam_data.clip_end = max(size)*20 + 100
        cam = bpy.data.objects.new(f'review_{view}', cam_data); scene.collection.objects.link(cam)
        t = math.radians(yaw); dist = max(size)*5 + 10
        cam.location = center + Vector((dist*math.sin(t), -dist*math.cos(t), 0))
        cam.rotation_euler = (math.radians(90), 0, t)
        scene.camera = cam
        scene.render.filepath = str(REVIEW / f'{stem}_{view}.png')
        bpy.ops.render.render(write_still=True)
        names.append(f'{stem}_{view}.png')
    return names, [round(v, 4) for v in size]


report = []
# Register once: unregistering between files leaves Source Tools handlers referencing missing Scene.vs.
source_tools.register()
for character, (rel, up_axis) in TARGETS.items():
    src = MODELS / character / rel
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0  # reset by factory settings; avoids .blend1 backups
    result =bpy.ops.import_scene.smd(filepath=str(src), upAxis=up_axis)
    arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    missing = []
    for mat in bpy.data.materials:
        png = src.parent / mat.name
        if not png.suffix:
            png = png.with_suffix('.png')
        if png.exists():
            textured(mat, bpy.data.images.load(str(png)))
        else:
            missing.append(mat.name)
    bones = [b for a in arms for b in a.data.bones]
    placeholder = [b.name for b in bones if b.name.startswith('NotABone')]
    skinned = [o for o in meshes if any(m.type == 'ARMATURE' and m.object for m in o.modifiers)]
    weighted = sum(1 for o in meshes for v in o.data.vertices if v.groups)
    entry = {
        'character': character, 'source': f'{character}/{rel}', 'up_axis': up_axis,
        'operator_result': sorted(result),
        'armatures': len(arms), 'bones': len(bones), 'placeholder_bones': len(placeholder),
        'root_bones': sum(1 for b in bones if b.parent is None),
        'mesh_objects': len(meshes), 'vertices': sum(len(o.data.vertices) for o in meshes),
        'faces': sum(len(o.data.polygons) for o in meshes), 'skinned_meshes': len(skinned),
        'weighted_vertices': weighted, 'materials': sorted(m.name for m in bpy.data.materials),
        'missing_textures': missing,
    }
    if meshes:
        entry['renders'], entry['bbox_size'] = render_views(character, meshes)
    blend = MODELS / character / f'{character}_rigged_{version}.blend'
    if blend.exists():
        raise RuntimeError(f'Preserve {blend.name}')
    # Relative texture paths need a saved file first, so the repository stays portable.
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
    entry['texture_paths'] = sorted(img.filepath for img in bpy.data.images if img.source == 'FILE')
    entry['blend'] = blend.relative_to(MODELS).as_posix()
    report.append(entry)
    print('SMD_IMPORTED', json.dumps(entry))

(REVIEW / 'SMD_Import_Report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('SMD_IMPORT_OK', len(report))
