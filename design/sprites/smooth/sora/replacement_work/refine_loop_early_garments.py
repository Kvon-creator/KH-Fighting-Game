"""Individual loop00-02 jackets/arms, with the approved loop00 hand protected."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, retain_main_body, save_clean
from refine_loop_late_stride_poses import contour, source_patch, sleeve, bent_arm, free_fist, metal, crown


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
LAYERS = ROOT/'ready/run_loop/layers'
SOURCE = ROOT/'ready/run_loop/run_loop_source.png'
SOURCE_HASH = '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
APPROVED_BOX = (384, 203, 424, 248)


def jacket00():
    a = Art()
    s, t = a.shape, a.stroke
    s((305, 151), [((316, 149), (330, 159), (340, 174)),
                    ((352, 177), (371, 184), (380, 196)),
                    ((382, 211), (367, 229), (348, 240)),
                    ((329, 251), (302, 254), (281, 243)),
                    ((267, 237), (260, 225), (265, 211)),
                    ((272, 190), (290, 161), (305, 151))], '#292f37')
    s((299, 160), [((308, 157), (319, 165), (322, 174)),
                    ((304, 188), (286, 210), (278, 229)),
                    ((272, 232), (267, 228), (270, 218)),
                    ((278, 196), (290, 169), (299, 160))], '#424d58', None)
    s((366, 200), [((373, 202), (376, 207), (371, 213)),
                    ((355, 235), (324, 248), (302, 244)),
                    ((297, 241), (294, 235), (296, 232)),
                    ((325, 232), (349, 219), (366, 200))], '#171f29', None)
    t((282, 206), [((276, 216), (278, 224), (285, 227))], '#657581', .75)
    t((286, 235), [((294, 241), (306, 244), (313, 242))], '#536471', .7)
    t((313, 169), [((317, 175), (317, 181), (315, 185))], '#627480', .65)
    t((309, 179), [((309, 185), (305, 193), (301, 198))], '#d9a927', 2.5)
    t((308, 180), [((308, 185), (305, 190), (303, 193))], '#f7d65a', .8)
    s((341, 174), [((352, 175), (367, 183), (374, 191)),
                    ((362, 216), (340, 233), (317, 244)),
                    ((308, 240), (301, 234), (302, 226)),
                    ((315, 207), (330, 184), (341, 174))], '#121b26')
    s((340, 188), [((350, 195), (362, 189), (368, 185)),
                    ((358, 205), (339, 220), (323, 226)),
                    ((317, 223), (313, 219), (313, 215)),
                    ((323, 201), (333, 192), (340, 188))], '#34414d', None)
    t((342, 190), [((350, 198), (362, 192), (367, 189))], '#bfccd7', 1.4)
    crown(a, 330, 213)
    s((326, 149), [((332, 153), (338, 161), (337, 168)),
                    ((327, 192), (313, 215), (301, 230)),
                    ((297, 231), (293, 227), (291, 224)),
                    ((305, 201), (319, 169), (326, 149))], '#323c48')
    t((331, 153), [((335, 158), (338, 164), (337, 168)),
                    ((327, 192), (313, 215), (301, 230)),
                    ((299, 230), (296, 229), (294, 227))], '#dce5eb', 1.45)
    t((329, 175), [((319, 196), (306, 218), (296, 224))], '#7f94a5', .65)
    t((374, 192), [((362, 216), (340, 234), (317, 244)),
                    ((308, 248), (295, 243), (290, 239))], '#dce6ec', 1.6)
    t((370, 199), [((356, 219), (339, 234), (318, 240))], '#718797', .65)
    metal(a, [(358, 210), (346, 223), (332, 234)])
    s((310, 235), [((317, 240), (326, 239), (335, 233)),
                    ((332, 242), (324, 247), (316, 248)),
                    ((307, 248), (301, 243), (297, 238)),
                    ((303, 241), (307, 238), (310, 235))], '#a51e27')
    t((307, 243), [((313, 246), (324, 243), (328, 240))], '#e64a37', 1)
    t((279, 242), [((297, 252), (323, 255), (344, 244))], '#e6b42a', 3)
    t((283, 244), [((298, 251), (319, 252), (333, 249))], '#ffde61', .75)
    return a.finish()


def jacket01():
    a = Art()
    s, t = a.shape, a.stroke
    s((281, 171), [((294, 169), (307, 180), (318, 196)),
                    ((334, 198), (353, 205), (362, 217)),
                    ((363, 232), (347, 247), (328, 255)),
                    ((307, 266), (280, 267), (258, 257)),
                    ((243, 251), (236, 238), (241, 224)),
                    ((249, 201), (266, 180), (281, 171))], '#292f37')
    s((277, 183), [((286, 179), (298, 188), (301, 197)),
                    ((283, 210), (264, 231), (257, 247)),
                    ((251, 249), (245, 244), (249, 235)),
                    ((256, 214), (268, 192), (277, 183))], '#424d58', None)
    s((348, 220), [((355, 223), (357, 229), (351, 235)),
                    ((333, 255), (301, 264), (279, 259)),
                    ((274, 255), (272, 251), (274, 247)),
                    ((304, 248), (331, 238), (348, 220))], '#171f29', None)
    t((259, 225), [((253, 234), (255, 241), (262, 245))], '#657681', .75)
    t((265, 252), [((272, 258), (284, 260), (291, 257))], '#536471', .7)
    t((294, 191), [((298, 197), (298, 201), (296, 206))], '#627480', .65)
    t((287, 200), [((287, 207), (283, 213), (279, 218))], '#d9aa27', 2.5)
    t((286, 201), [((286, 206), (283, 210), (281, 214))], '#f7d65a', .8)
    s((319, 195), [((330, 196), (348, 203), (355, 212)),
                    ((341, 236), (319, 252), (296, 261)),
                    ((287, 257), (280, 250), (281, 243)),
                    ((294, 224), (308, 205), (319, 195))], '#121b26')
    s((319, 207), [((329, 214), (342, 209), (349, 205)),
                    ((338, 225), (318, 239), (302, 246)),
                    ((296, 243), (292, 238), (292, 234)),
                    ((302, 221), (312, 212), (319, 207))], '#34414d', None)
    t((320, 209), [((330, 217), (342, 212), (347, 209))], '#bfccd7', 1.4)
    crown(a, 310, 230)
    s((305, 172), [((311, 176), (316, 183), (315, 190)),
                    ((305, 215), (292, 238), (281, 251)),
                    ((277, 252), (272, 248), (271, 245)),
                    ((284, 223), (299, 192), (305, 172))], '#323c48')
    t((310, 177), [((313, 181), (316, 186), (315, 190)),
                    ((305, 215), (292, 238), (281, 251)),
                    ((279, 251), (276, 250), (274, 248))], '#dce5eb', 1.45)
    t((307, 198), [((297, 219), (285, 240), (274, 246))], '#7f94a5', .65)
    t((355, 213), [((341, 237), (318, 253), (296, 261)),
                    ((287, 265), (274, 261), (267, 256))], '#dce6ec', 1.6)
    t((351, 220), [((336, 240), (318, 253), (298, 257))], '#718797', .65)
    metal(a, [(338, 230), (324, 243), (311, 252)])
    s((289, 252), [((296, 257), (305, 256), (314, 250)),
                    ((311, 259), (303, 264), (295, 265)),
                    ((286, 264), (280, 260), (276, 255)),
                    ((282, 258), (286, 255), (289, 252))], '#a51e27')
    t((286, 260), [((292, 263), (303, 260), (307, 257))], '#e64a37', 1)
    t((256, 257), [((275, 267), (299, 269), (322, 259))], '#e6b42a', 3)
    t((260, 259), [((276, 266), (297, 267), (310, 264))], '#ffde61', .75)
    return a.finish()


def jacket02():
    a = Art()
    s, t = a.shape, a.stroke
    s((222, 148), [((235, 146), (250, 157), (262, 174)),
                    ((276, 176), (295, 184), (306, 197)),
                    ((306, 212), (290, 226), (270, 236)),
                    ((250, 247), (224, 250), (202, 240)),
                    ((186, 234), (179, 222), (184, 208)),
                    ((192, 185), (208, 159), (222, 148))], '#292f37')
    s((216, 162), [((226, 157), (239, 165), (242, 174)),
                    ((223, 188), (208, 210), (201, 227)),
                    ((195, 230), (189, 225), (192, 216)),
                    ((198, 194), (207, 171), (216, 162))], '#424d58', None)
    s((290, 199), [((298, 202), (301, 207), (295, 213)),
                    ((278, 235), (247, 247), (225, 242)),
                    ((220, 238), (218, 234), (220, 231)),
                    ((248, 231), (273, 219), (290, 199))], '#171f29', None)
    t((202, 207), [((196, 216), (197, 224), (204, 227))], '#657681', .75)
    t((208, 235), [((216, 241), (226, 243), (233, 240))], '#536471', .7)
    t((233, 169), [((237, 175), (237, 180), (235, 185))], '#627480', .65)
    t((228, 178), [((228, 185), (224, 192), (220, 197))], '#d9aa27', 2.5)
    t((227, 179), [((227, 184), (224, 189), (222, 192))], '#f7d65a', .8)
    s((263, 174), [((274, 175), (291, 183), (298, 192)),
                    ((284, 217), (262, 233), (240, 243)),
                    ((230, 239), (223, 233), (224, 225)),
                    ((236, 206), (252, 185), (263, 174))], '#121b26')
    s((263, 188), [((273, 195), (285, 190), (292, 186)),
                    ((281, 206), (262, 220), (247, 227)),
                    ((240, 224), (236, 219), (236, 215)),
                    ((246, 201), (256, 193), (263, 188))], '#34414d', None)
    t((264, 190), [((274, 198), (286, 193), (290, 189))], '#bfccd7', 1.4)
    crown(a, 255, 211)
    s((250, 149), [((256, 153), (261, 161), (260, 168)),
                    ((250, 192), (236, 216), (225, 231)),
                    ((221, 232), (216, 228), (215, 225)),
                    ((229, 202), (243, 169), (250, 149))], '#323c48')
    t((255, 154), [((258, 158), (261, 164), (260, 168)),
                    ((250, 192), (236, 216), (225, 231)),
                    ((223, 231), (220, 230), (218, 227))], '#dce5eb', 1.45)
    t((252, 175), [((242, 196), (230, 218), (218, 225))], '#7f94a5', .65)
    t((298, 193), [((284, 217), (262, 234), (240, 243)),
                    ((231, 247), (218, 242), (212, 238))], '#dce6ec', 1.6)
    t((294, 200), [((279, 221), (262, 234), (241, 239))], '#718797', .65)
    metal(a, [(281, 210), (267, 224), (254, 235)])
    s((232, 234), [((240, 239), (248, 238), (258, 232)),
                    ((254, 241), (247, 246), (238, 247)),
                    ((230, 247), (223, 242), (219, 237)),
                    ((225, 240), (229, 237), (232, 234))], '#a51e27')
    t((230, 242), [((236, 245), (246, 242), (251, 239))], '#e64a37', 1)
    t((200, 240), [((219, 249), (244, 251), (265, 240))], '#e6b42a', 3)
    t((204, 242), [((220, 248), (241, 249), (254, 246))], '#ffde61', .75)
    return a.finish()


POSES = {
    0: {'source': 'pilot_v3/frame_00_original.png', 'draw': jacket00, 'light': (310, 187),
        'far_shoulder': (300, 162), 'far_cuff': (281, 199), 'far_elbow': (267, 220), 'far_wrist': (256, 236),
        'near_shoulder': (365, 185), 'near_cuff': (366, 213), 'near_elbow': (372, 245),
        'head': [(300, 0), (512, 0), (512, 171), (405, 171), (389, 179), (368, 193),
                 (342, 190), (331, 183), (323, 166), (319, 150), (302, 132), (300, 132)],
        'jacket': [(282, 150), (291, 145), (310, 141), (325, 154), (326, 168),
                   (311, 166), (312, 179), (298, 179), (286, 165)],
        'remove': [[(58, 24), (183, 24), (189, 133), (249, 160), (239, 184), (58, 111)],
                   [(225, 152), (271, 132), (321, 174), (316, 208), (282, 236), (248, 235), (205, 184)],
                   [(276, 198), (303, 194), (353, 209), (362, 222), (348, 239), (308, 240), (274, 219)],
                   [(140, 184), (184, 158), (220, 153), (226, 173), (185, 200), (181, 227), (145, 226)]]},
    1: {'source': 'frame_01_v1/original_crop.png', 'draw': jacket01, 'light': (287, 211),
        'far_shoulder': (278, 183), 'far_cuff': (259, 219), 'far_elbow': (245, 240), 'far_wrist': (232, 254),
        'near_shoulder': (349, 207), 'near_cuff': (347, 234), 'near_elbow': (351, 267),
        'head': [(275, 0), (512, 0), (512, 193), (385, 193), (370, 203), (346, 213),
                 (325, 211), (314, 203), (308, 184), (298, 164), (277, 151), (275, 151)],
        'jacket': [(257, 167), (267, 158), (286, 155), (307, 169), (309, 181),
                   (293, 181), (293, 195), (280, 195), (263, 180)],
        'remove': [[(35, 24), (149, 24), (157, 121), (218, 160), (208, 184), (35, 111)],
                   [(192, 169), (241, 145), (286, 187), (284, 222), (252, 249), (218, 250), (175, 205)],
                   [(244, 217), (273, 214), (323, 230), (333, 243), (318, 258), (279, 258), (244, 239)],
                   [(105, 197), (150, 170), (189, 164), (198, 184), (154, 213), (150, 239), (110, 239)]]},
    2: {'source': 'frame_02_v1/original_crop.png', 'draw': jacket02, 'light': (232, 190),
        'far_shoulder': (219, 166), 'far_cuff': (201, 201), 'far_elbow': (185, 224), 'far_wrist': (175, 240),
        'near_shoulder': (296, 187), 'near_cuff': (286, 214), 'near_elbow': (295, 246),
        'head': [(222, 0), (512, 0), (512, 169), (334, 169), (318, 179), (294, 192),
                 (272, 188), (264, 180), (257, 159), (246, 143), (225, 130), (222, 130)],
        'jacket': [(191, 153), (201, 140), (220, 135), (245, 148), (246, 162),
                   (233, 162), (236, 176), (222, 178), (203, 163)],
        'remove': [[(8, 61), (119, 61), (122, 153), (174, 174), (165, 199), (8, 155)],
                   [(154, 170), (197, 147), (246, 185), (242, 217), (207, 249), (173, 252), (140, 207)],
                   [(222, 203), (244, 199), (285, 210), (294, 223), (278, 239), (247, 239), (216, 223)],
                   [(78, 204), (111, 182), (148, 178), (157, 198), (122, 221), (118, 246), (82, 246)]]},
}


def render(index):
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
    data = POSES[index]
    prior = LAYERS/f'frame_{index:02d}_review_v2'
    out = LAYERS/f'frame_{index:02d}_review_v3'
    out.mkdir(parents=True, exist_ok=True)
    source_image = Image.open(LAYERS/data['source']).convert('RGBA')
    assert source_image.width <= 512 and source_image.height <= 512
    original = Image.new('RGBA', (512, 512))
    original.paste(source_image, (0, 0))
    assert np.array_equal(np.array(original.crop((0, 0, source_image.width, source_image.height))), np.array(source_image))
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
    ox, oy = data['light']
    light = 4*np.exp(-((xx-ox)/27)**2-((yy-oy)/42)**2)
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
    assert all(record['area_px'] < 180 for record in removed), removed
    preserve_y = meta.get('lower_body_preserved_from_y', 300)
    old_body = Image.open(prior/'body_rebuilt.png').convert('RGBA')
    body.paste(old_body.crop((0, preserve_y, 512, 512)), (0, preserve_y))
    layers = {name: Image.open(prior/(name+'.png')).convert('RGBA')
              for name in ['weapon_back', 'weapon_foreground', 'approved_grip', 'chain']}
    result = Image.alpha_composite(layers['weapon_back'], body)
    for name in ['weapon_foreground', 'approved_grip', 'chain']:
        result = Image.alpha_composite(result, layers[name])
    if index == 0:
        result.paste(before.crop(APPROVED_BOX), APPROVED_BOX[:2])
        assert np.array_equal(np.array(result.crop(APPROVED_BOX)), np.array(before.crop(APPROVED_BOX)))
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
    if index == 0:
        save_clean(before.crop(APPROVED_BOX), out/'approved_hand_cuff_region.png')
    for obsolete in ['garment_detail_reuse', 'arm_reconstruction_method', 'palette_pass', 'body_layers', 'source_art_pass']:
        meta.pop(obsolete, None)
    meta.update({'status': 'individual early-loop garment/arm refinement; full animation QA pending',
                 'frame_index': index, 'source_review': prior.name, 'prior_review_sha256': before_hash,
                 'physical_master_length_px': 285, 'master_scale': 1,
                 'head_layer': 'head_preserved.png', 'projected_wrist_cuff': cuff.tolist(),
                 'garment_method': 'individual source-pose jacket curves and shoulder/elbow/cuff arm controls',
                 'source_jacket_method': 'small source hood/pad contour retained; old gold excluded',
                 'source_crop_file': data['source'],
                 'body_layers': ['individual_clothing_repair.png', 'released_arm.png', 'holding_arm.png',
                                 'source_jacket_detail.png', 'head_preserved.png'],
                 'registration_note': 'old reconstruction offset retained only as the provisional package pelvis estimate',
                 'lower_body_preserved_from_y': preserve_y,
                 'joint_controls': {name: data[name] for name in ['far_shoulder', 'far_cuff', 'far_elbow', 'far_wrist', 'near_shoulder', 'near_cuff', 'near_elbow']},
                 'removed_detached_body_fragments': removed,
                 'checks': ['original sheet/prior review hashes unchanged', 'four carry/grip/chain files byte-identical to v2',
                            'opaque gripping hand exact; projected cuff inside forearm', f'lower composite exact from y{preserve_y}'],
                 'limitations': ['Cross-frame garment/arm proportions still need comparison with idle.',
                                 'Both alternating strides, root/flight offsets, timing and start/stop seams remain unfinished.',
                                 'Offline checks only; no Godot test or aerial production.']})
    if index == 0:
        meta['checks'].append('approved hand/cuff rectangle exact')
        meta['composition_final_override'] = {'file': 'approved_hand_cuff_region.png', 'xy': [384, 203],
                                              'size': [40, 45], 'mode': 'exact RGBA copy after composition'}
    (out/'manifest.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    (out/'README.md').write_text(
        f'# Loop{index:02d} source-pose garment repair\n\n'
        'Individual jacket contours replace the older chest reconstruction. '
        'Released/carrying arms follow recorded shoulder/elbow/wrist controls. '
        'Source head, lower pose and small hood/pad details remain; old weapon '
        'and two-hand-arm regions are removed with contours.\n\n'
        'All four weapon/grip/chain files remain byte-identical to v2. Loop00 '
        'also preserves its exact approved hand/cuff rectangle. Original sheet '
        'and earlier reviews remain. Cross-frame anatomy/materials, both strides, '
        'root/timing and start/stop seams still need work. No Godot test or aerial art.\n', encoding='utf-8')
    board = Image.new('RGB', (1536, 550), '#202633')
    for column, (im, label) in enumerate([(original, 'Original / two-hand source pose'),
                                         (before, 'v2 / older jacket reconstruction'),
                                         (result, 'v3 / source-pose jacket and joint drawing')]):
        board.paste(im, (column*512, 30), im)
        ImageDraw.Draw(board).text((column*512+12, 9), label, fill='white')
    board.save(out/'Garment_Comparison.png')
    review = Image.new('RGB', (1024, 720), '#202633')
    review.paste(result, (0, 30), result)
    light = Image.new('RGB', (512, 512), '#dedfe2')
    light.paste(result, (0, 0), result)
    review.paste(light, (512, 30))
    ImageDraw.Draw(review).text((12, 9), f'Loop{index:02d} / source-pose garment / dark, light and128px', fill='white')
    for column, im in enumerate([result, result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
        small = im.resize((128, 128), Image.Resampling.LANCZOS)
        review.paste(small, (160+column*190, 580), small)
    review.save(out/'Dark_Light_Game_Review.png')
    Image.open(out/f'sora_run_loop_{index:02d}_review.png').verify()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
    assert hashlib.sha256(before_path.read_bytes()).hexdigest() == before_hash
    print(f'Loop{index:02d}: source-pose jacket/arms verified; cuff {cuff.tolist()}; original/carry/lower body retained.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--frame', type=int, choices=(0, 1, 2))
    args = parser.parse_args()
    for index in [args.frame] if args.frame is not None else [0, 1, 2]:
        render(index)
