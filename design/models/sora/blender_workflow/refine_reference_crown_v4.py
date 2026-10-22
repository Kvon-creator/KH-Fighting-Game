"""Refine only the crown in a preserved sibling of the v3 Blender model.

Run from a factory-startup Blender 5.2 process with --python-exit-code 1.
The inline user reference is an image, not an available source mesh.
"""
import hashlib
import json
import math
import struct
from pathlib import Path

import bmesh
import bpy
from mathutils import Quaternion, Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
assert bpy.app.version[:2] == (5, 2), bpy.app.version_string
SOURCE = ROOT / 'design/models/sora/experiments/weapon_pipeline_v3/kingdom_key_reference_crown.blend'
OUT = ROOT / 'design/models/sora/experiments/weapon_pipeline_v4'
if OUT.exists():
    raise RuntimeError('Preserve existing review; this output folder must be new')
assert SOURCE.is_file()
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
OUT.mkdir()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False)
bpy.context.preferences.filepaths.file_preview_type = 'NONE'
scene = bpy.context.scene
root = bpy.data.objects['KingdomKey_Rigid_Root']
head = bpy.data.objects['crown_teeth']
camera = scene.camera
root.rotation_euler = (0, 0, 0)
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.render.resolution_x = scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.color_mode = 'RGBA'


def geometry_signature(obj):
    return dict(vertices=[list(v.co) for v in obj.data.vertices],
                faces=[list(face.vertices) for face in obj.data.polygons],
                matrix=[list(row) for row in obj.matrix_local],
                materials=[slot.material.name for slot in obj.material_slots])


unchanged = {obj.name: geometry_signature(obj) for obj in scene.objects
             if obj.type == 'MESH' and obj != head}


def set_camera(center, scale, diagonal=True, opposite=False):
    center = Vector(center)
    # See the same side of the crown as the user's diagonal reference:
    # local +X projects upper-left and local +Z projects upper-right.
    offset = Vector((0, -6 if opposite else 6, .48))
    camera.location = center + offset
    rotation = (center - camera.location).to_track_quat('-Z', 'Y')
    if diagonal:
        rotation = rotation @ Quaternion((0, 0, 1), math.atan2(.733, .680))
    camera.rotation_euler = rotation.to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale


def render(filename):
    target = OUT / filename
    if target.exists():
        raise RuntimeError('Preserve render ' + filename)
    scene.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)


head_center = (.107, 0, 1.265)
set_camera(head_center, .43)
render('previous_crown_same_view.png')

# Refine the previous coarse landmarks using smooth circular endings. These
# are estimates from the attached 640px image, not calibrated pixel extraction.
# Small outer flat ends, narrow necks, and three pointed recesses are retained.
points = [(511, 199), (475, 125), (484, 118), (505, 146)]


def round_tip(center, radius, start, end, steps=48):
    for index in range(steps + 1):
        angle = math.radians(start + (end - start) * index / steps)
        points.append((center[0] + radius * math.cos(angle),
                       center[1] + radius * math.sin(angle)))


round_tip((510.5, 120), 8.0, 110, 410)
points.append((543, 131))
round_tip((535.5, 100), 8.0, 100, 410)
points.extend([(566, 104), (538, 77), (548, 66), (600, 109)])
shaft_axis = Vector((.733, -.680)).normalized()
across = Vector((shaft_axis.y, -shaft_axis.x))
tip = Vector((609, 126))
scale = .00239
profile = [((Vector(point) - tip).dot(across) * scale,
            1.4 + (Vector(point) - tip).dot(shaft_axis) * scale)
           for point in points]
# Only the hidden attachment moves into the shaft; visible outer endpoints
# remain part of the silhouette rather than floating beside the cylinder.
profile[0] = (-.005, profile[0][1])
profile[-1] = (-.005, profile[-1][1])
thickness = .018
count = len(profile)
vertices = [(x, y, z) for y in (-thickness / 2, thickness / 2) for x, z in profile]
faces = [tuple(range(count)), tuple(reversed(range(count, count * 2)))]
faces += [(index, index + count, (index + 1) % count + count, (index + 1) % count)
          for index in range(count)]
mesh = bpy.data.meshes.new('crown_profile_smooth_v4')
mesh.from_pydata(vertices, [], faces)
mesh.update()
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
assert all(edge.is_manifold for edge in bm.edges)
volume = bm.calc_volume(signed=True)
assert volume > 0
bm.to_mesh(mesh)
bm.free()
assert not mesh.validate()
material = head.data.materials[0]
mesh.materials.append(material)
head.data = mesh
head.modifiers.clear()
bevel = head.modifiers.new('rounded_crown_edge_v4', 'BEVEL')
bevel.width = .0016
bevel.segments = 4
bevel.harden_normals = True
head['reference'] = 'Newest user-attached diagonal Kingdom Key image; approximate image interpretation'
head['revision'] = 'Smooth smaller round endings, refined recesses and outer ends, thinner plate'
assert all(geometry_signature(bpy.data.objects[name]) == signature for name, signature in unchanged.items())
render('revised_crown_same_view.png')
set_camera(head_center, .43, diagonal=False)
render('revised_crown_profile.png')
set_camera((.015, 0, .35), 2.55)
render('revised_weapon_reference_angle.png')
set_camera((.015, 0, .35), 2.55, diagonal=False, opposite=True)
render('revised_weapon_reverse.png')
set_camera((.015, 0, .35), 2.55)
scene.render.filepath = str(OUT / 'sprite_')
scene_path = OUT / 'kingdom_key_crown_v4.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(scene_path))

# The saved scene retains its cel shader. Export separate simple materials
# because glTF does not carry the procedural normal/color-ramp shader.
palette = {}
for obj in scene.objects:
    obj.select_set(obj.type == 'MESH' or obj == root)
    if obj.type != 'MESH':
        continue
    for slot in obj.material_slots:
        original = slot.material
        if original.name not in palette:
            mat = bpy.data.materials.new(original.name + '_v4_exchange')
            mat.diffuse_color = original.diffuse_color
            mat.use_nodes = True
            mat.node_tree.nodes.clear()
            output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
            surface = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            surface.inputs['Base Color'].default_value = original.diffuse_color
            surface.inputs['Roughness'].default_value = .9
            mat.node_tree.links.new(surface.outputs['BSDF'], output.inputs['Surface'])
            palette[original.name] = mat
        slot.material = palette[original.name]
bpy.context.view_layer.objects.active = root
glb_path = OUT / 'kingdom_key_crown_v4.glb'
bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format='GLB', use_selection=True,
                          export_cameras=False, export_lights=False)

# Reopen the delivered scene and check that the actual saved geometry and
# transparent renders are intact, rather than relying on the builder state.
bpy.ops.wm.open_mainfile(filepath=str(scene_path), load_ui=False)
scene = bpy.context.scene
root = bpy.data.objects['KingdomKey_Rigid_Root']
head = bpy.data.objects['crown_teeth']
meshes = [obj for obj in scene.objects if obj.type == 'MESH']
assert len(meshes) == 24 and all(obj.parent == root for obj in meshes)
assert all(geometry_signature(bpy.data.objects[name]) == signature for name, signature in unchanged.items())
assert abs(head.dimensions.y - thickness) < .001
for name in ('central_black_handle', 'gold_pommel', 'gold_collar', 'blue_collar', 'silver_shaft', 'silver_end_cap'):
    obj = bpy.data.objects[name]
    assert abs(obj.location.x) < 1e-6 and abs(obj.location.y) < 1e-6
    assert max(abs(angle) for angle in obj.rotation_euler) < 1e-6
assert scene.camera.data.type == 'ORTHO' and scene.render.film_transparent
bm = bmesh.new()
bm.from_mesh(head.data)
assert all(edge.is_manifold for edge in bm.edges)
assert bm.calc_volume(signed=True) > 0
bm.free()
assert min(v.co.x for v in head.data.vertices) < 0
renders = []
for filename in ('previous_crown_same_view.png', 'revised_crown_same_view.png', 'revised_crown_profile.png',
                 'revised_weapon_reference_angle.png', 'revised_weapon_reverse.png'):
    image = bpy.data.images.load(str(OUT / filename), check_existing=False)
    assert tuple(image.size) == (768, 768) and image.channels == 4
    alpha = list(image.pixels)[3::4]
    visible = [(i % 768, i // 768) for i, value in enumerate(alpha) if value > .1]
    bounds = [min(x for x, y in visible), min(y for x, y in visible),
              max(x for x, y in visible), max(y for x, y in visible)]
    assert min(alpha) == 0 and max(alpha) > .99
    # Closeups deliberately crop the shaft below the crown; full weapon fits.
    if filename.startswith('revised_weapon'):
        assert min(bounds[:2]) > 10 and max(bounds[2:]) < 757
    renders.append(dict(file=filename, sha256=hashlib.sha256((OUT / filename).read_bytes()).hexdigest(),
                        boundsBottomOrigin=bounds, alphaRange=[min(alpha), max(alpha)]))
glb = glb_path.read_bytes()
magic, version, length = struct.unpack_from('<4sII', glb)
assert magic == b'glTF' and version == 2 and length == len(glb)
json_length, json_type = struct.unpack_from('<II', glb, 12)
assert json_type == 0x4e4f534a
gltf = json.loads(glb[20:20 + json_length])
colors = [tuple(mat.get('pbrMetallicRoughness', {}).get('baseColorFactor', [])) for mat in gltf['materials']]
assert len(set(colors)) == 4 and len(gltf['meshes']) == 24
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
report = dict(passed=True, sourceScene=str(SOURCE.relative_to(ROOT)), sourceSha256=source_hash,
              sourcePreserved=True, savedSceneReopened=True, blenderVersion=bpy.app.version_string,
              crownOnlyGeometryChanged=True, unchangedMeshes=len(unchanged), meshCount=len(meshes),
              allMeshesShareRigidRoot=True, gripCollarsShaftShareLocalAxis=True,
              crownManifoldOutwardNormals=True, crownVolume=volume,
              crownPlateThickness=thickness, previousPlateThickness=.045,
              referenceMethod='Manual estimates from inline image; smooth analytical tip arcs, not calibrated tracing or mesh extraction',
              imageLandmarks=points, localSilhouetteXZ=profile, renders=renders,
              orthographicCamera=True, transparentRGBA=True, device='CPU', glbPaletteColors=4,
              scene=scene_path.name, sceneSha256=hashlib.sha256(scene_path.read_bytes()).hexdigest(),
              glb=glb_path.name, glbSha256=hashlib.sha256(glb).hexdigest(),
              userApprovedExactGeometry=False, soraRigOrAnimationTested=False, gameplayIntegrated=False)
(OUT / 'Crown_Refinement_QA.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(passed=True, scene=scene_path.name, sourcePreserved=True, meshCount=len(meshes),
                      unchangedMeshes=len(unchanged), crownPlateThickness=thickness, renders=len(renders),
                      glbPaletteColors=4), indent=2))
