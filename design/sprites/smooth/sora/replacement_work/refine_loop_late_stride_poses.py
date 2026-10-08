"""Individual loop05/07 jackets and articulated arms, preserving rigid carry."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, retain_main_body, save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
LAYERS = ROOT/'ready/run_loop/layers'
SOURCE = ROOT/'ready/run_loop/run_loop_source.png'
SOURCE_HASH = '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'


def contour(points):
    mask = Image.new('L', (2048, 2048))
    ImageDraw.Draw(mask).polygon([(x*4, y*4) for x, y in points], fill=255)
    return mask.resize((512, 512), Image.Resampling.LANCZOS)


def source_patch(original, mask, exclude_gold=False):
    p = np.array(original)
    ma = np.array(mask)
    if exclude_gold:
        rgb = p[:, :, :3].astype(float)
        gold = (rgb[:, :, 0] > 95) & (rgb[:, :, 1] > 65) & (rgb[:, :, 2] < 65) & (rgb[:, :, 1] > rgb[:, :, 0]*.60)
        ma[gold] = 0
    result = original.copy()
    result.putalpha(Image.fromarray((p[:, :, 3].astype(float)*ma/255).round().astype('uint8')))
    return result


def metal(a, points):
    for x, y in points:
        a.ellipse((x-1.45, y-1.45, x+1.45, y+1.45), '#8b9caa', '#172330', .55)
        a.ellipse((x-.6, y-1, x+.6, y), '#dce7ed')


def crown(a, x, y):
    a.stroke((x+2, y-15), [((x, y-10), (x-1, y-6), (x, y-3))], '#b2c4d1', .65)
    a.shape((x-3, y), [((x-3, y-2), (x-3, y-4), (x-3, y-5)),
                       ((x-2, y-4), (x-1, y-3), (x, y-3)),
                       ((x+1, y-5), (x+2, y-7), (x+2, y-7)),
                       ((x+3, y-5), (x+4, y-4), (x+4, y-3)),
                       ((x+6, y-4), (x+7, y-5), (x+7, y-5)),
                       ((x+7, y-3), (x+6, y-1), (x+6, y)),
                       ((x+2, y+2), (x-1, y+2), (x-3, y))], '#c8d5df', '#596c7c', .5)


def sleeve(a, shoulder, cuff):
    """Draw cloth around each pose's actual upper-arm direction."""
    sx, sy = shoulder
    cx, cy = cuff
    d = np.array([cx-sx, cy-sy], float)
    length = np.linalg.norm(d)
    assert length > 15
    normal = np.array([-d[1], d[0]])/length
    def p(t, width):
        v = np.array([sx, sy])+d*t+normal*width
        return tuple(v)
    a.shape(p(0, 10), [(p(-.1, 1), p(-.1, -8), p(0, -11)),
                       (p(.4, -16), p(.9, -11), p(1, -7)),
                       (p(1.08, -4), p(1.08, 5), p(1, 8)),
                       (p(.7, 14), p(.2, 15), p(0, 10))], '#2b333d')
    a.shape(p(.1, 7), [(p(.05, 2), p(.1, -6), p(.25, -8)),
                       (p(.5, -12), p(.85, -7), p(.86, -3)),
                       (p(.8, 3), p(.4, 9), p(.1, 7))], '#45515c', None)
    a.shape(p(.2, -8), [(p(.3, -12), p(.6, -12), p(.65, -7)),
                        (p(.7, -3), p(.5, -1), p(.35, -3)),
                        (p(.2, -4), p(.1, -6), p(.2, -8))], '#374553', '#8b9ba8', .75)
    metal(a, [p(.28, -8), p(.56, -6)])
    a.shape(p(.89, 9), [(p(.96, 5), p(.99, -2), p(.91, -8)),
                        (p(1.05, -9), p(1.12, -5), p(1.12, 0)),
                        (p(1.12, 5), p(1.06, 9), p(.99, 10)),
                        (p(.94, 10), p(.92, 10), p(.89, 9))], '#dde6ec', '#192530', 1)
    a.stroke(p(1.02, 8), [(p(1.1, 3), p(1.06, -3), p(1.02, -7))], '#8ea1af', .8)
    a.stroke(p(.5, 10), [(p(.65, 9), p(.8, 6), p(.85, 3))], '#617481', .7)


def bent_arm(a, start, elbow, wrist, width=5.5):
    """Pose-specific elbow/wrist trajectory, drawn rather than bitmap warped."""
    start, elbow, wrist = map(lambda p: np.array(p, float), (start, elbow, wrist))
    # Small underlap beneath the separate glove/cuff; anchor itself stays fixed.
    wrist = wrist+(wrist-elbow)/np.linalg.norm(wrist-elbow)*3.5
    n1 = np.array([-(elbow-start)[1], (elbow-start)[0]])/np.linalg.norm(elbow-start)*width
    n2 = np.array([-(wrist-elbow)[1], (wrist-elbow)[0]])/np.linalg.norm(wrist-elbow)*width
    def p(v):
        return tuple(v)
    a.shape(p(start+n1), [(p(start+(elbow-start)*.35+n1), p(elbow+n1), p(elbow+n1*.5)),
                         (p(elbow+(wrist-elbow)*.3+n2), p(wrist+n2), p(wrist+n2*.9)),
                         (p(wrist+n2*.6), p(wrist-n2*.6), p(wrist-n2*.9)),
                         (p(wrist+(elbow-wrist)*.4-n2), p(elbow-n1), p(elbow-n1*.8)),
                         (p(elbow+(start-elbow)*.4-n1), p(start-n1), p(start-n1)),
                         (p(start-n1*.5), p(start+n1*.5), p(start+n1))], '#ecb28a', '#3d2a24', 1.1)
    a.stroke(p(start+n1*.5), [(p(start+(elbow-start)*.6+n1*.6), p(elbow+n1*.3), p(elbow)),
                            (p(elbow+(wrist-elbow)*.4+n2*.2), p(wrist+n2*.3), p(wrist+n2*.35))], '#ffd1a4', 1.2)
    a.stroke(p(start-n1*.7), [(p(start+(elbow-start)*.6-n1*.7), p(elbow-n1*.65), p(elbow-n1*.4)),
                            (p(elbow+(wrist-elbow)*.4-n2*.6), p(wrist-n2*.6), p(wrist-n2*.6))], '#ba7b5b', 2.7)


def free_fist(a, x, y):
    a.shape((x-6, y-7), [((x-2, y-10), (x+4, y-8), (x+7, y-4)),
                         ((x+11, y), (x+8, y+6), (x+3, y+8)),
                         ((x-3, y+8), (x-9, y+4), (x-10, y)),
                         ((x-10, y-4), (x-8, y-6), (x-6, y-7))], '#26323e')
    a.shape((x-6, y-4), [((x-2, y-7), (x+3, y-5), (x+5, y-2)),
                         ((x+3, y+1), (x-3, y+1), (x-7, y-1)),
                         ((x-7, y-2), (x-7, y-3), (x-6, y-4))], '#445563', None)
    a.stroke((x-8, y-5), [((x-10, y), (x-7, y+5), (x-4, y+6))], '#d8b348', 1.2)
    for dx, dy in [(4, 4), (7, 1), (8, -2)]:
        a.ellipse((x+dx-1.3, y+dy-1.7, x+dx+1.3, y+dy+1.7), '#e9b087', '#78513e', .5)


def jacket05():
    a = Art()
    s, t = a.shape, a.stroke
    s((267, 126), [((279, 125), (293, 133), (304, 149)),
                    ((320, 152), (339, 161), (350, 173)),
                    ((354, 188), (341, 203), (325, 213)),
                    ((307, 224), (280, 227), (260, 217)),
                    ((245, 212), (239, 198), (244, 184)),
                    ((248, 164), (256, 137), (267, 126))], '#292f37')
    s((266, 138), [((275, 134), (286, 142), (288, 150)),
                    ((271, 163), (257, 184), (254, 201)),
                    ((249, 204), (244, 200), (247, 192)),
                    ((251, 171), (259, 147), (266, 138))], '#444e58', None)
    s((336, 177), [((342, 180), (345, 185), (341, 191)),
                    ((324, 212), (296, 224), (276, 219)),
                    ((272, 216), (270, 211), (272, 209)),
                    ((299, 210), (321, 196), (336, 177))], '#171f29', None)
    t((255, 180), [((250, 190), (251, 198), (257, 202))], '#657681', .75)
    t((259, 209), [((266, 214), (277, 217), (283, 215))], '#526371', .7)
    t((280, 147), [((283, 153), (283, 159), (281, 163))], '#657681', .65)
    t((275, 151), [((275, 157), (272, 164), (269, 168))], '#d7a925', 2.5)
    t((274, 152), [((274, 157), (272, 161), (270, 164))], '#f6d658', .8)
    s((309, 149), [((319, 149), (336, 157), (344, 166)),
                    ((331, 190), (309, 208), (289, 217)),
                    ((279, 212), (272, 206), (272, 199)),
                    ((285, 182), (299, 161), (309, 149))], '#121b26')
    s((308, 163), [((317, 170), (330, 165), (337, 161)),
                    ((327, 180), (309, 195), (294, 201)),
                    ((287, 198), (283, 193), (283, 190)),
                    ((292, 177), (302, 167), (308, 163))], '#34414d', None)
    t((309, 165), [((318, 173), (329, 167), (335, 164))], '#c0ced9', 1.4)
    crown(a, 298, 189)
    s((293, 128), [((299, 132), (303, 140), (301, 147)),
                    ((294, 169), (281, 190), (272, 204)),
                    ((268, 205), (264, 201), (263, 198)),
                    ((274, 178), (286, 147), (293, 128))], '#323c47')
    t((298, 132), [((301, 137), (303, 142), (301, 147)),
                    ((294, 169), (281, 190), (272, 204)),
                    ((270, 204), (267, 203), (266, 201))], '#dce5eb', 1.45)
    t((295, 151), [((287, 172), (277, 190), (267, 199))], '#7f93a4', .65)
    t((344, 167), [((331, 191), (309, 208), (289, 217)),
                    ((281, 221), (268, 217), (262, 212))], '#dde6ec', 1.6)
    t((339, 174), [((326, 194), (309, 207), (291, 213))], '#718797', .65)
    metal(a, [(329, 183), (315, 198), (304, 209)])
    s((282, 209), [((289, 214), (297, 214), (307, 208)),
                    ((303, 216), (296, 221), (288, 222)),
                    ((279, 221), (273, 218), (269, 212)),
                    ((274, 215), (279, 214), (282, 209))], '#a51e27')
    t((278, 217), [((285, 220), (296, 217), (300, 214))], '#e64b37', 1)
    t((258, 217), [((275, 226), (299, 229), (318, 220))], '#e6b329', 3)
    t((262, 219), [((277, 225), (297, 226), (307, 223))], '#ffdc5c', .75)
    return a.finish()


def jacket07():
    a = Art()
    s, t = a.shape, a.stroke
    s((263, 113), [((275, 112), (289, 121), (301, 136)),
                    ((318, 139), (338, 147), (348, 160)),
                    ((351, 175), (335, 192), (319, 202)),
                    ((298, 215), (271, 218), (250, 209)),
                    ((238, 203), (231, 190), (236, 176)),
                    ((243, 153), (250, 127), (263, 113))], '#292f37')
    s((261, 126), [((271, 122), (282, 130), (285, 139)),
                    ((267, 153), (251, 175), (246, 192)),
                    ((241, 193), (236, 190), (239, 182)),
                    ((245, 159), (253, 135), (261, 126))], '#434e59', None)
    s((333, 163), [((338, 166), (341, 171), (337, 177)),
                    ((320, 199), (290, 213), (269, 211)),
                    ((264, 207), (261, 202), (263, 200)),
                    ((292, 200), (316, 182), (333, 163))], '#171e28', None)
    t((246, 168), [((240, 178), (242, 187), (249, 191))], '#667581', .75)
    t((249, 198), [((256, 204), (267, 207), (275, 206))], '#526371', .7)
    t((276, 136), [((280, 142), (280, 146), (278, 151))], '#667581', .65)
    t((270, 138), [((270, 145), (267, 151), (263, 156))], '#d7a727', 2.5)
    t((269, 139), [((269, 144), (267, 149), (264, 152))], '#f6d559', .8)
    s((305, 138), [((315, 138), (331, 145), (340, 153)),
                    ((328, 177), (306, 197), (283, 208)),
                    ((274, 204), (267, 198), (268, 190)),
                    ((280, 172), (296, 150), (305, 138))], '#121b26')
    s((305, 151), [((314, 158), (326, 153), (334, 148)),
                    ((324, 167), (304, 184), (289, 191)),
                    ((283, 189), (278, 184), (279, 180)),
                    ((289, 166), (299, 156), (305, 151))], '#34414e', None)
    t((306, 153), [((314, 161), (326, 155), (333, 151))], '#bfced9', 1.4)
    crown(a, 294, 178)
    s((289, 116), [((295, 119), (300, 127), (299, 134)),
                    ((289, 157), (276, 181), (264, 195)),
                    ((260, 196), (256, 192), (255, 189)),
                    ((267, 168), (282, 136), (289, 116))], '#323c48')
    t((295, 120), [((298, 124), (300, 130), (299, 134)),
                    ((289, 157), (276, 181), (264, 195)),
                    ((262, 195), (259, 194), (258, 192))], '#dce6ec', 1.45)
    t((292, 139), [((283, 160), (271, 182), (259, 190))], '#7f94a5', .65)
    t((340, 155), [((327, 179), (306, 197), (283, 208)),
                    ((274, 212), (261, 207), (255, 203))], '#dce6ec', 1.6)
    t((336, 162), [((322, 182), (304, 198), (284, 204))], '#708797', .65)
    metal(a, [(324, 172), (311, 187), (298, 198)])
    s((276, 198), [((283, 203), (292, 202), (301, 197)),
                    ((297, 205), (289, 211), (281, 211)),
                    ((273, 211), (266, 207), (263, 202)),
                    ((269, 204), (273, 201), (276, 198))], '#a51e27')
    t((272, 206), [((279, 209), (290, 207), (294, 203))], '#e64a37', 1)
    t((248, 207), [((265, 216), (290, 218), (310, 209))], '#e7b52b', 3)
    t((252, 208), [((266, 214), (286, 216), (297, 213))], '#ffde61', .75)
    return a.finish()


POSES = {
    5: {'draw': jacket05, 'far_shoulder': (265, 141), 'far_cuff': (247, 177),
        'far_elbow': (232, 199), 'far_wrist': (220, 217),
        'near_shoulder': (345, 163), 'near_cuff': (346, 192), 'near_elbow': (355, 220),
        'head': [(270, 0), (512, 0), (512, 155), (364, 155), (348, 162), (328, 172),
                 (307, 165), (298, 147), (289, 129), (274, 110), (270, 110)],
        'jacket': [(258, 125), (264, 117), (279, 114), (295, 125), (297, 138),
                   (285, 138), (285, 150), (272, 151), (259, 138)],
        'remove': [[(31, 14), (150, 14), (157, 105), (221, 135), (210, 158), (29, 87)],
                   [(198, 129), (241, 115), (285, 149), (286, 180), (261, 207), (226, 215), (186, 174)],
                   [(113, 162), (162, 139), (196, 139), (204, 157), (164, 184), (159, 210), (117, 211)],
                   [(262, 171), (284, 171), (326, 181), (332, 193), (319, 209), (285, 212), (260, 193)]]},
    7: {'draw': jacket07, 'far_shoulder': (261, 129), 'far_cuff': (241, 166),
        'far_elbow': (229, 188), 'far_wrist': (212, 208),
        'near_shoulder': (337, 151), 'near_cuff': (334, 182), 'near_elbow': (336, 219),
        'head': [(270, 0), (512, 0), (512, 147), (364, 147), (347, 152), (329, 163),
                 (308, 158), (299, 143), (291, 125), (275, 105), (270, 105)],
        'jacket': [(249, 111), (258, 101), (273, 98), (290, 113), (291, 126),
                   (278, 126), (279, 140), (266, 141), (252, 125)],
        'remove': [[(17, 9), (138, 9), (144, 94), (201, 118), (190, 146), (15, 83)],
                   [(180, 113), (228, 97), (267, 130), (265, 167), (240, 198), (212, 201), (168, 156)],
                   [(97, 145), (142, 124), (180, 122), (184, 144), (145, 174), (139, 195), (102, 198)],
                   [(235, 161), (257, 157), (311, 173), (330, 182), (326, 196), (291, 207), (241, 184)]]},
}


def render(index):
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
    data = POSES[index]
    prior = LAYERS/f'frame_{index:02d}_review_v2'
    out = LAYERS/f'frame_{index:02d}_review_v3'
    out.mkdir(parents=True, exist_ok=True)
    original = Image.open(LAYERS/f'frame_{index:02d}_review_v1/original_crop.png').convert('RGBA')
    before_path = prior/f'sora_run_loop_{index:02d}_review.png'
    before_hash = hashlib.sha256(before_path.read_bytes()).hexdigest()
    before = Image.open(before_path).convert('RGBA')
    meta = json.loads((prior/'manifest.json').read_text(encoding='utf-8'))
    H = np.array(meta['master_to_screen_homography'])
    cuff = H @ np.array([77, 50, 1])
    cuff = cuff[:2]/cuff[2]
    removal = Image.new('L', original.size)
    for polygon in data['remove']:
        ImageDraw.Draw(removal).polygon(polygon, fill=255)
    body = original.copy()
    body.putalpha(Image.composite(Image.new('L', body.size), body.getchannel('A'), removal))
    far = Art()
    sleeve(far, data['far_shoulder'], data['far_cuff'])
    bent_arm(far, data['far_cuff'], data['far_elbow'], data['far_wrist'], 4.8)
    free_fist(far, *data['far_wrist'])
    body = Image.alpha_composite(body, far.finish())
    repair = data['draw']()
    p = np.array(repair)
    rgb = p[:, :, :3].astype(float)
    yy, xx = np.indices(p.shape[:2])
    origin = (275, 159) if index == 5 else (270, 150)
    light = 4*np.exp(-((xx-origin[0])/25)**2-((yy-origin[1])/40)**2)
    gray = (p[:, :, 3] > 0) & (rgb.max(2)-rgb.min(2) < 40) & (rgb.max(2) < 115) & (rgb.min(2) > 26)
    rgb[gray] += light[gray, None]
    p[:, :, :3] = np.clip(rgb, 0, 255).astype('uint8')
    repair = Image.fromarray(p, 'RGBA')
    body = Image.alpha_composite(body, repair)
    jacket_mask = contour(data['jacket'])
    jacket_detail = source_patch(original, jacket_mask, True)
    body = Image.alpha_composite(body, jacket_detail)
    near = Art()
    sleeve(near, data['near_shoulder'], data['near_cuff'])
    bent_arm(near, data['near_cuff'], data['near_elbow'], tuple(cuff), 5.7)
    body = Image.alpha_composite(body, near.finish())
    head_mask = contour(data['head'])
    head = source_patch(original, head_mask)
    body = Image.alpha_composite(body, head)
    body, removed = retain_main_body(body)
    assert all(record['area_px'] < 130 for record in removed), removed
    preserve_y = meta['lower_body_preserved_from_y']
    old_body = Image.open(prior/'body_rebuilt.png').convert('RGBA')
    body.paste(old_body.crop((0, preserve_y, 512, 512)), (0, preserve_y))
    layers = {name: Image.open(prior/(name+'.png')).convert('RGBA')
              for name in ['weapon_back', 'weapon_foreground', 'approved_grip', 'chain']}
    result = Image.alpha_composite(layers['weapon_back'], body)
    for name in ['weapon_foreground', 'approved_grip', 'chain']:
        result = Image.alpha_composite(result, layers[name])
    interior = np.array(layers['approved_grip'].getchannel('A')) == 255
    assert np.array_equal(np.array(result)[interior], np.array(before)[interior])
    assert np.array_equal(np.array(result)[preserve_y:], np.array(before)[preserve_y:])
    assert np.array(body.getchannel('A'))[int(round(cuff[1])), int(round(cuff[0]))] > 240
    for name, im in [('body_rebuilt', body), ('individual_clothing_repair', repair),
                     ('released_arm', far.finish()), ('holding_arm', near.finish()),
                     ('source_jacket_detail', jacket_detail), ('head_preserved', head),
                     (f'sora_run_loop_{index:02d}_review', result)]:
        save_clean(im, out/(name+'.png'))
    removal.save(out/'old_weapon_arm_removal_mask.png')
    jacket_mask.save(out/'source_jacket_detail_mask.png')
    head_mask.save(out/'head_contour_mask.png')
    for name in layers:
        (out/(name+'.png')).write_bytes((prior/(name+'.png')).read_bytes())
        assert (out/(name+'.png')).read_bytes() == (prior/(name+'.png')).read_bytes()
    meta.update({'status': 'individual late-stride garment/arm review; full gait QA pending',
                 'source_review': prior.name, 'prior_review_sha256': before_hash,
                 'head_layer': 'head_preserved.png', 'projected_wrist_cuff': cuff.tolist(),
                 'garment_method': 'pose-specific chest curves; sleeves/arms follow individual shoulder/elbow/cuff joints',
                 'source_jacket_method': 'small source hood/pad contour retained; old gold excluded',
                 'joint_controls': {name: data[name] for name in ['far_shoulder', 'far_cuff', 'far_elbow', 'far_wrist', 'near_shoulder', 'near_cuff', 'near_elbow']},
                 'removed_detached_body_fragments': removed,
                 'checks': ['original sheet/prior review hashes unchanged', 'four carry/grip/chain files byte-identical to v2',
                            'opaque gripping hand exact; cuff inside forearm', f'lower composite exact from y{preserve_y}'],
                 'limitations': ['Cross-frame garment/arm proportions still need comparison with idle.',
                                 'Alternating gait/contact order, root/timing and start/stop seams remain unfinished.',
                                 'Offline checks only; no Godot test or aerial artwork.']})
    (out/'manifest.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    (out/'README.md').write_text(
        f'# Loop{index:02d} late-stride garment repair\n\n'
        'Individual source-pose chest contours replace the shifted torso template. '
        'The released arm and carrying arm use recorded shoulder/elbow/wrist controls, '
        'not warped body sprites. Source hair/face/neck, lower-body pose and selected '
        'hood/pad detail remain. Old weapon/two-hand arm regions are removed with contours.\n\n'
        'All weapon, foreground guard, approved grip and chain files remain byte-identical '
        'to v2. Earlier reviews and original sheets remain. This is working art with '
        'unfinished cross-frame proportions, gait/root/timing and transitions. No Godot '
        'test, generation retry or aerial production.\n', encoding='utf-8')
    board = Image.new('RGB', (1536, 550), '#202633')
    for column, (im, label) in enumerate([(original, 'Original / two-hand source pose'),
                                         (before, 'v2 / shifted jacket template'),
                                         (result, 'v3 / individual jacket and articulated arms')]):
        board.paste(im, (column*512, 30), im)
        ImageDraw.Draw(board).text((column*512+12, 9), label, fill='white')
    board.save(out/'Garment_Comparison.png')
    review = Image.new('RGB', (1024, 720), '#202633')
    review.paste(result, (0, 30), result)
    light = Image.new('RGB', (512, 512), '#dedfe2')
    light.paste(result, (0, 0), result)
    review.paste(light, (512, 30))
    ImageDraw.Draw(review).text((12, 9), f'Loop{index:02d} / late stride clothing / dark, light and128px', fill='white')
    for column, im in enumerate([result, result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
        small = im.resize((128, 128), Image.Resampling.LANCZOS)
        review.paste(small, (160+column*190, 580), small)
    review.save(out/'Dark_Light_Game_Review.png')
    Image.open(out/f'sora_run_loop_{index:02d}_review.png').verify()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
    assert hashlib.sha256(before_path.read_bytes()).hexdigest() == before_hash
    print(f'Loop{index:02d}: new garment/joint drawing verified; cuff {cuff.tolist()}; sources/carry/feet retained.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--frame', type=int, choices=(5, 7))
    args = parser.parse_args()
    for index in [args.frame] if args.frame is not None else [5, 7]:
        render(index)
