"""Per-phase upper-body/carry refinement over the preserved16-pose gait.

Offline local art only. No legacy absolute paths, generation retries or engine
changes. The v2 legs/contact trajectories and all earlier artwork are retained.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, carry, save_clean
from refine_loop_late_stride_poses import sleeve, bent_arm, free_fist
from draw_loop_upper_motion import jacket, waist_cloth, holding_skin, moving_chain


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
LOOP = ROOT/'ready/run_loop'
REF = LOOP/'layers/frame_00_review_v3'
PRIOR = LOOP/'gait_refinement_v2'
OUT = LOOP/'gait_refinement_v3'
MASTER = LOOP/'layers/art_pass_05'
SIZE = (512, 512)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def translated(im, xy):
    result = Image.new('RGBA', SIZE)
    result.alpha_composite(im, tuple(int(v) for v in xy))
    assert np.count_nonzero(np.array(result.getchannel('A')) > 32) == \
        np.count_nonzero(np.array(im.getchannel('A')) > 32), 'Source cutout clipped'
    return result


def two_bone(start, end, upper=54., lower=44.):
    start, end = np.array(start, float), np.array(end, float)
    distance = np.linalg.norm(end-start)
    assert abs(upper-lower) < distance < upper+lower
    axis = (end-start)/distance
    normal = np.array([axis[1], -axis[0]])
    along = (upper**2-lower**2+distance**2)/(2*distance)
    joint = start+axis*along+normal*math.sqrt(upper**2-along**2)
    assert abs(np.linalg.norm(joint-start)-upper) < 1e-8
    assert abs(np.linalg.norm(end-joint)-lower) < 1e-8
    return joint


def projected(H, point):
    q = H@np.array([*point, 1.])
    return q[:2]/q[2]


def pose_controls(record):
    phase = record['index']*2*math.pi/16
    bob = record['body_bob_px']
    twist = math.sin(phase)
    pitch = np.array([3*math.sin(2*phase)+1.2*twist,
                      -1.4*(1-math.cos(2*phase))])
    near_delta = pitch+np.array([2.1*(math.cos(phase)-1), 1.1*twist])
    far_delta = pitch+np.array([-1.5*(math.cos(phase)-1), -.8*twist])
    bob_vector = np.array([0., bob])
    return {
        'phase': phase, 'bob': bob, 'twist': twist, 'compression': max(0, bob)/6,
        'back_neck': (np.array([307., 154.])+pitch+bob_vector+np.array([1.1*(math.cos(phase)-1), 0.])),
        'front_neck': np.array([343., 177.])+pitch+bob_vector,
        'near_shoulder': np.array([367., 188.])+near_delta+bob_vector,
        'far_shoulder': np.array([302., 165.])+far_delta+bob_vector,
        'waist_far': np.array([283., 246.+bob]), 'waist_near': np.array([346., 247.+bob]),
        'hand': np.array([407., 228.+bob])+pitch*.6+np.array([1.2*(math.cos(phase)-1), 1.1*math.sin(2*phase)]),
        'carry_angle': 218+1.3*math.sin(2*phase)+.4*twist,
        'carry_yaw': 25+.6*twist,
        'cloth_lag': 3.2*(math.sin(2*phase-.65)-math.sin(-.65)),
        'head_translation': [2+round(pitch[0]), 3+bob+round(pitch[1])],
        'hood_translation': [2+round(far_delta[0]), 3+bob+round(far_delta[1])],
    }


def render(record, source_head, source_hood):
    i = record['index']
    pose = pose_controls(record)
    lower_dir = PRIOR/'layers'/f'phase_{i:02d}'
    layer_dir = OUT/'layers'/f'phase_{i:02d}'
    layer_dir.mkdir(parents=True, exist_ok=True)
    lower = {name: Image.open(lower_dir/(name+'.png')).convert('RGBA')
             for name in ['far_leg', 'near_leg', 'pelvis']}
    if i == 0:
        weapon = {name: Image.open(lower_dir/(name+'.png')).convert('RGBA')
                  for name in ['weapon_back', 'weapon_foreground', 'approved_grip', 'chain']}
        H = np.array(record['master_to_export_homography'])
        anchors = {name: projected(H, point).tolist() for name, point in
                   {'grip': (77, 70), 'pommel': (34, 70), 'collar': (137, 70), 'tip': (319, 70)}.items()}
        charm_center, chain_sway = [anchors['pommel'][0]-6, anchors['pommel'][1]+37], 0.
    else:
        back, front, grip, _, H, anchors = carry(MASTER, pose['hand'], pose['carry_angle'], pose['carry_yaw'])
        chain, charm_center, chain_sway = moving_chain(anchors['pommel'], pose['phase'])
        weapon = {'weapon_back': back, 'weapon_foreground': front, 'approved_grip': grip, 'chain': chain}
    wrist = projected(H, (77, 50))
    shoulder = pose['near_shoulder']
    elbow = shoulder+np.array([7.+1.2*math.sin(pose['phase']),
                               60.+2.5*(1-math.cos(pose['phase']))])
    cuff = shoulder+(elbow-shoulder)/np.linalg.norm(elbow-shoulder)*29
    near_sleeve = Art()
    sleeve(near_sleeve, shoulder, cuff)
    skin = holding_skin(cuff, elbow, wrist)
    near = Image.alpha_composite(skin, near_sleeve.finish())
    free_shoulder = pose['far_shoulder']
    free_wrist = np.array(record['free_arm']['wrist'], float)
    free_vector = free_wrist-free_shoulder
    if np.linalg.norm(free_vector) >= 97.5:
        free_wrist = free_shoulder+free_vector/np.linalg.norm(free_vector)*97.
    free_elbow = two_bone(free_shoulder, free_wrist)
    free_cuff = free_shoulder+(free_elbow-free_shoulder)/54*31
    free = Art()
    sleeve(free, free_shoulder, free_cuff)
    bent_arm(free, free_cuff, free_elbow, free_wrist, 5.3)
    free_fist(free, *free_wrist)
    torso = jacket(pose)
    cloth = waist_cloth(pose)
    head = translated(source_head, pose['head_translation'])
    hood = translated(source_hood, pose['hood_translation'])
    body = free.finish()
    for layer in [lower['far_leg'], lower['pelvis'], lower['near_leg'], cloth, torso, hood, near, head]:
        body = Image.alpha_composite(body, layer)
    result = Image.alpha_composite(weapon['weapon_back'], body)
    for name in ['weapon_foreground', 'approved_grip', 'chain']:
        result = Image.alpha_composite(result, weapon[name])
    prior_result = Image.open(PRIOR/record['path']).convert('RGBA')
    if i == 0:
        box = (386, 206, 426, 251)
        result.paste(prior_result.crop(box), box[:2])
        assert np.array_equal(np.array(result.crop(box)), np.array(prior_result.crop(box)))
        save_clean(prior_result.crop(box), layer_dir/'approved_hand_cuff_region.png')
    grip_interior = np.array(weapon['approved_grip'].getchannel('A')) == 255
    assert np.array_equal(np.array(result)[grip_interior], np.array(weapon['approved_grip'])[grip_interior]), 'Opaque grip changed'
    assert np.array(body.getchannel('A'))[round(wrist[1]), round(wrist[0])] > 240, 'Wrist socket gap'
    assert np.linalg.norm(np.array(anchors['collar'])-shoulder) < 14, 'Carry leaves holding shoulder'
    assert np.allclose(projected(H, (77, 70)), pose['hand']), 'Handle/grip anchor mismatch'
    prior_body = Image.open(lower_dir/'body.png').convert('RGBA')
    assert np.array_equal(np.array(body)[300:], np.array(prior_body)[300:]), 'Retained lower-body drawing changed'
    assert np.array_equal(np.array(result)[312:], np.array(prior_result)[312:]), 'Lower-frame pixels changed'
    head_interior = np.array(head.getchannel('A')) == 255
    assert np.array_equal(np.array(body)[head_interior], np.array(head)[head_interior]), 'Source face/neck changed'
    new_layers = {'jacket': torso, 'waist_cloth': cloth, 'holding_arm': near,
                  'free_arm': free.finish(), 'head': head, 'hood_detail': hood, 'body': body, **weapon}
    for name, layer in new_layers.items():
        save_clean(layer, layer_dir/(name+'.png'))
    for name in lower:
        (layer_dir/(name+'.png')).write_bytes((lower_dir/(name+'.png')).read_bytes())
        assert sha(layer_dir/(name+'.png')) == sha(lower_dir/(name+'.png'))
    save_clean(result, OUT/record['path'])
    updated = dict(record)
    updated.update({
        'upper_method': 'new chest/lining/cloth curves anchored to independent neck/shoulder/waist controls; new arms',
        'upper_landmarks': {key: pose[key].tolist() for key in ['back_neck', 'front_neck', 'near_shoulder', 'far_shoulder', 'waist_far', 'waist_near']},
        'head_translation_xy': pose['head_translation'], 'hood_translation_xy': pose['hood_translation'],
        'holding_arm': {'shoulder': shoulder.tolist(), 'sleeve_cuff': cuff.tolist(), 'elbow': elbow.tolist(),
                        'wrist_socket': wrist.tolist(), 'projected_forearm_length_px': float(np.linalg.norm(wrist-elbow))},
        'free_arm': {'shoulder': free_shoulder.tolist(), 'elbow': free_elbow.tolist(), 'wrist': free_wrist.tolist()},
        'carry_angle_degrees': pose['carry_angle'], 'foreground_yaw_degrees': pose['carry_yaw'],
        'master_to_export_homography': H.tolist(), 'projected_weapon_anchors': anchors,
        'shoulder_collar_distance_px': float(np.linalg.norm(np.array(anchors['collar'])-shoulder)),
        'cloth_tip_lag_px': pose['cloth_lag'], 'chain_sway_px': chain_sway, 'charm_center': charm_center,
        'prior_frame_sha256': sha(PRIOR/record['path']), 'body_layer_exact_from_y': 300,
        'final_composite_exact_from_y': 312,
        'approved_hand_region_xy': [386, 206] if i == 0 else None,
    })
    updated.pop('upper_reference_translation_xy', None)
    return result, updated


def package(images, records, pilot=False):
    rows = (len(images)+3)//4
    sheet = Image.new('RGBA', (2048, rows*512))
    board = Image.new('RGB', (1024, rows*280), '#202633')
    mirror = Image.new('RGB', (len(images)*128, 336), '#202633')
    flat = []
    for column, (im, record) in enumerate(zip(images, records)):
        sheet.paste(im, (column % 4*512, column//4*512))
        small = im.resize((256, 256), Image.Resampling.LANCZOS)
        x, y = column % 4*256, column//4*280
        board.paste(small, (x, y+20), small)
        ImageDraw.Draw(board).text((x+8, y+5), f'{record["index"]:02d} {record["phase"]} / upper motion', fill='white')
        ImageDraw.Draw(board).line((x, y+236, x+255, y+236), fill='#637180')
        for row, view in enumerate([im, im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
            game = view.resize((128, 128), Image.Resampling.LANCZOS)
            mirror.paste(game, (column*128, row*168+24), game)
            ImageDraw.Draw(mirror).text((column*128+6, row*168+6), f'{record["index"]:02d}', fill='white')
        bg = Image.new('RGB', SIZE, '#202633')
        bg.paste(im, (0, 0), im)
        flat.append(bg)
    if pilot:
        board.save(OUT/'Pilot_Upper_Review.png')
        return
    save_clean(sheet, OUT/'sora_run_loop_gait_sheet.png')
    board.save(OUT/'Contact_Sheet.png')
    mirror.save(OUT/'Game_Size_Mirrored_Review.png')
    for name, duration in [('sora_run_loop_gait_preview.gif', 60), ('sora_run_loop_gait_slow.gif', 180)]:
        flat[0].save(OUT/name, save_all=True, append_images=flat[1:], duration=duration, loop=0, disposal=2)
        gif = Image.open(OUT/name)
        assert gif.n_frames == 16
        for index in range(16):
            gif.seek(index)
            gif.load()
    comparison = Image.new('RGB', (2048, 640), '#202633')
    for column, index in enumerate([0, 4, 8, 12]):
        for row, (folder, label) in enumerate([(PRIOR, 'v2 fixed upper'), (OUT, 'v3 new jacket/arms/cloth')]):
            im = Image.open(folder/records[index]['path']).convert('RGBA')
            crop = im.crop((240, 135, 470, 280)).resize((460, 290), Image.Resampling.LANCZOS)
            comparison.paste(crop, (column*512+16, row*320+26), crop)
            ImageDraw.Draw(comparison).text((column*512+16, row*320+6), f'{index:02d} / {label}', fill='white')
    comparison.save(OUT/'Upper_Body_Comparison.png')
    cloth_comparison = Image.new('RGB', (960, 360), '#dedfe2')
    for column, (path, label) in enumerate([
        (LOOP/'review_cycle_v5/sora_run_loop_00.png', 'Original folded waist cloth'),
        (OUT/records[0]['path'], 'v3 folded cloth / new belt attachment')]):
        im = Image.open(path).convert('RGBA')
        crop = im.crop((180, 195, 290, 280)).resize((440, 340), Image.Resampling.LANCZOS)
        cloth_comparison.paste(crop, (column*480, 20), crop)
        ImageDraw.Draw(cloth_comparison).text((column*480+10, 5), label, fill='black')
    cloth_comparison.save(OUT/'Waist_Cloth_Reference_Comparison.png')


def main(pilot):
    OUT.mkdir(parents=True, exist_ok=True)
    protected = [LOOP/'run_loop_source.png', ROOT/'ready/run_start/run_start_source.png',
                  MASTER/'kingdom_key_master_finished.png', MASTER/'grip_master_space.png']
    for folder in [REF, LOOP/'review_cycle_v5', LOOP/'gait_refinement_v1', PRIOR]:
        protected.extend(path for path in folder.rglob('*') if path.is_file())
    hashes = {path: sha(path) for path in protected}
    assert hashes[MASTER/'kingdom_key_master_finished.png'] == 'd942f08de984050119716906f0311a467f5be3150811ae634b40c327c6eaa800'
    assert hashes[MASTER/'grip_master_space.png'] == '75c8d5cffdc90775dccaffb409759101abdeb9e774b0a763e486b6ac8aa8d58f'
    source = json.loads((PRIOR/'manifest.json').read_text(encoding='utf-8'))
    head = Image.open(REF/'head_preserved.png').convert('RGBA')
    hood = Image.open(REF/'source_jacket_detail.png').convert('RGBA')
    indices = [0, 1, 6, 8] if pilot else list(range(16))
    images, records = [], []
    for index in indices:
        im, record = render(source['frames'][index], head, hood)
        images.append(im)
        records.append(record)
        Image.open(OUT/record['path']).verify()
        pixels = np.array(Image.open(OUT/record['path']))
        assert np.all(pixels[pixels[:, :, 3] == 0, :3] == 0)
        print(f'Upper{index:02d}: wrist joined; shoulder/collar {record["shoulder_collar_distance_px"]:.2f}px; lower pose retained.', flush=True)
    package(images, records, pilot)
    for path, value in hashes.items():
        assert sha(path) == value, f'Original/prior artwork changed: {path}'
    if pilot:
        print('Four-pose upper pilot checked; complete cycle not packaged yet.')
        return
    assert len({sha(OUT/record['path']) for record in records}) == 16
    assert len({sha(OUT/'layers'/f'phase_{i:02d}'/'jacket.png') for i in range(16)}) == 16
    source.update({
        'status': '16-pose upper-body follow-through candidate; idle quality/timing/seams unfinished',
        'frames': records,
        'upper_reference': 'new per-phase chest/waist/arm drawings; source head/hood details translated without scaling',
        'method': 'retained v2 gait joints/contact/legs; independent neck/shoulder/waist controls and new upper drawings',
        'prior_artwork_sha256': {str(path.relative_to(ROOT)): value for path, value in hashes.items()},
        'checks': ['16 distinct frames/jacket drawings; PNG/GIF decoding',
                   'three v2 lower layers byte-identical per phase; body exact below y300, final RGBA exact below y312',
                   'frame00 approved hand/cuff region exact; opaque grip interiors preserved',
                   'projected cuff inside holding forearm; collar stays within14px of same holding shoulder',
                   'fixed master/grip hashes and285px physical weapon length; one transform for blade/guard/handle',
                   'original sheets and all captured prior candidates unchanged'],
        'limitations': ['Head/hair remain source reference cutouts; hair secondary motion is unfinished.',
                        'Clothing/arm/leg/shoe materials and foreshortened anatomy need more comparison with approved idle.',
                        'Contact trajectory and60ms timing remain provisional; no engine foot planting.',
                        'Start/stop/idle weapon transitions remain unfinished; no Godot test or aerial production.'],
    })
    (OUT/'manifest.json').write_text(json.dumps(source, indent=2), encoding='utf-8')
    (OUT/'README.md').write_text(
        '# Run loop: upper-body follow-through pass\n\n'
        'Each of the16 gait phases now has a new jacket/lining/waist drawing around '
        'independent neck, shoulder and waist controls. New sleeves and tapered carrying '
        'arms join the projected wrist cuff. The free arm follows its new shoulder, while '
        'red waist panels and the pommel-attached chain lag slightly. Source face/hair and '
        'small hood details are translated without resizing; secondary hair motion remains.\n\n'
        'The Kingdom Key uses the same285px master and corrected grip. Small angle/yaw '
        'changes retain foreground tip depth and shoulder carry; blade, guard and handle '
        'share one projection. Frame00 retains its exact approved hand/cuff region and '
        'four carry layers. Other poses project the approved master grip without flipping it.\n\n'
        'The three lower layers, joints, body bob, floor/air clearances and provisional60ms '
        'timing are retained from v2. The body layer is exact below y300; the moving chain '
        'can reach y307, so the final composite is exact from y312 down. All original '
        'sheets, v1/v2 gait drafts and eight-pose garment reviews remain. This is another '
        'art candidate, not approved-idle quality or gameplay integration. Materials, '
        'foreshortened anatomy, timing and start/stop/idle transitions still need work. '
        'No image-generation retry, protected engine edit, Godot test or aerial production.\n', encoding='utf-8')
    (OUT/'QA_NOTES.md').write_text(
        '# Upper-body follow-through checkpoint\n\n'
        'Sixteen separate jacket/waist/arm drawings replace the fixed upper reference. '
        'Small shoulder/neck offsets and chest folds follow the existing gait; the '
        'carrying arm connects to the approved master wrist. Red cloth has the original '
        'pointed fold and crossing straps, with its root under the belt. Source face/hair '
        'and selected hood details remain reference cutouts.\n\n'
        '- Preserve all originals and earlier candidates, including v1/v2 and review_cycle_v5.\n'
        '- The initial rounded cloth pilot was corrected before completing this package. '
        'Use Waist_Cloth_Reference_Comparison.png for the final comparison.\n'
        '- Frame00 keeps the exact approved hand/cuff crop and carry layers. Other poses '
        'reuse the corrected master grip under one shared weapon projection; no flip or '
        'physical length change. The collar remains near the holding shoulder.\n'
        '- Lower layers are byte-identical to v2. Body pixels below y300 and final pixels '
        'below y312 are exact. The higher cutoff accounts for the moving pendant. '
        'Recorded foot contacts, airborne clearances and gait timing are unchanged.\n'
        '- Next refine garment/skin/boot shading and projected arm/leg proportions against '
        'approved idle. Source patch detail remains richer than the new fabric planes. '
        'Hair secondary motion, motion/timing review and start/stop/idle seams remain.\n\n'
        'Offline PNG/GIF and preservation checks only. No Godot test, protected engine '
        'changes, generation retry or aerial production.\n', encoding='utf-8')
    print('Verified16 new upper drawings, fixed weapon geometry, wrist joins, preserved grip and unchanged lower gait.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true', help='Inspect00/01/06/08 before packaging the full cycle')
    main(parser.parse_args().pilot)
