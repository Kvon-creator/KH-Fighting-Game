"""Repair loop06 around its own source jacket and articulated carry arm.

Offline image helper. Earlier reviews, master/grip and original sheets remain.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, retain_main_body, save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
LAYERS = READY/'run_loop/layers'
SOURCE = READY/'run_loop/run_loop_source.png'
SOURCE_HASH = '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
PRIOR = LAYERS/'frame_06_review_v2'
OUT = LAYERS/'frame_06_review_v3'
OUT.mkdir(parents=True, exist_ok=True)
original = Image.open(LAYERS/'frame_06_review_v1/original_crop.png').convert('RGBA')
before_path = PRIOR/'sora_run_loop_06_review.png'
before_hash = hashlib.sha256(before_path.read_bytes()).hexdigest()
before = Image.open(before_path).convert('RGBA')
meta = json.loads((PRIOR/'manifest.json').read_text(encoding='utf-8'))


def contour(points):
    mask = Image.new('L', (2048, 2048))
    ImageDraw.Draw(mask).polygon([(x*4, y*4) for x, y in points], fill=255)
    return mask.resize((512, 512), Image.Resampling.LANCZOS)


removal = Image.new('L', (512, 512))
rd = ImageDraw.Draw(removal)
for polygon in [
    [(20, 40), (127, 40), (127, 109), (217, 140), (210, 166), (23, 109)],
    [(185, 134), (224, 125), (265, 149), (264, 186), (238, 222), (204, 225), (169, 184), (166, 158)],
    [(232, 181), (259, 178), (304, 193), (317, 197), (317, 213), (297, 224), (259, 219), (231, 205)],
    [(105, 176), (124, 161), (159, 155), (190, 139), (191, 157), (159, 179), (150, 218), (119, 224), (103, 214)],
]:
    rd.polygon(polygon, fill=255)
body = original.copy()
body.putalpha(Image.composite(Image.new('L', body.size), body.getchannel('A'), removal))

# Retain only source jacket regions that are outside the old hand/weapon.
hood_mask = contour([(235, 128), (248, 120), (263, 124), (274, 133),
                     (274, 147), (263, 142), (243, 139), (236, 134)])
pad_mask = contour([(237, 135), (247, 133), (260, 139), (264, 151),
                    (256, 156), (246, 151), (239, 146), (236, 139)])
source_jacket_mask = Image.fromarray(np.maximum(np.array(hood_mask), np.array(pad_mask)))
pixels = np.array(original)
rgb = pixels[:, :, :3].astype(float)
gold = (rgb[:, :, 0] > 95) & (rgb[:, :, 1] > 65) & (rgb[:, :, 2] < 65) & (rgb[:, :, 1] > rgb[:, :, 0]*.60)
jm = np.array(source_jacket_mask)
jm[gold] = 0
source_jacket_mask = Image.fromarray(jm)
source_jacket = original.copy()
source_jacket.putalpha(Image.fromarray((pixels[:, :, 3].astype(float)*jm/255).round().astype('uint8')))

far = Art()
s, t = far.shape, far.stroke
s((239, 147), [((229, 153), (220, 167), (218, 177)),
                ((220, 184), (229, 189), (236, 186)),
                ((244, 179), (252, 164), (248, 154)),
                ((246, 150), (243, 147), (239, 147))], '#2c333b')
s((237, 154), [((230, 159), (224, 169), (224, 176)),
                ((228, 179), (233, 178), (238, 173)),
                ((243, 165), (246, 158), (237, 154))], '#424c57', None)
s((219, 177), [((223, 182), (230, 186), (236, 182)),
                ((235, 188), (230, 192), (225, 191)),
                ((220, 188), (218, 182), (219, 177))], '#dce5eb', '#1a2631', 1)
t((221, 182), [((225, 188), (230, 189), (234, 186))], '#869baa', .8)
s((224, 188), [((219, 192), (213, 200), (209, 206)),
                ((206, 210), (205, 218), (201, 220)),
                ((196, 223), (191, 219), (192, 215)),
                ((195, 205), (203, 195), (208, 190)),
                ((212, 186), (217, 183), (220, 184)),
                ((222, 185), (223, 187), (224, 188))], '#ecb28a', '#3e2d26', 1.15)
s((193, 213), [((198, 203), (204, 195), (210, 191)),
                ((207, 198), (204, 204), (202, 211)),
                ((200, 216), (199, 220), (197, 220)),
                ((193, 220), (192, 216), (193, 213))], '#bd7b5b', None)
t((215, 194), [((210, 201), (207, 208), (206, 212))], '#ffd1a2', 1)
# Relaxed released fist; it does not reuse the source's second gripping hand.
s((192, 214), [((195, 210), (203, 212), (206, 217)),
                ((210, 222), (207, 228), (202, 230)),
                ((195, 231), (188, 227), (187, 222)),
                ((186, 218), (189, 215), (192, 214))], '#25313d')
s((191, 217), [((194, 214), (200, 215), (203, 219)),
                ((201, 222), (194, 222), (190, 220)),
                ((190, 219), (190, 218), (191, 217))], '#465664', None)
t((189, 216), [((187, 220), (189, 225), (193, 227))], '#ddb54a', 1.2)
for x, y in [(202, 225), (205, 222), (206, 219)]:
    far.ellipse((x-1.3, y-1.7, x+1.3, y+1.7), '#eab18a', '#775440', .5)
body = Image.alpha_composite(body, far.finish())

cloth = Art()
s, t = cloth.shape, cloth.stroke
s((246, 138), [((255, 137), (266, 145), (273, 156)),
                ((284, 164), (302, 170), (314, 181)),
                ((324, 195), (308, 213), (292, 222)),
                ((275, 231), (248, 233), (229, 224)),
                ((217, 219), (211, 208), (214, 196)),
                ((219, 175), (232, 150), (246, 138))], '#292f37')
s((242, 148), [((249, 146), (257, 151), (259, 159)),
                ((243, 172), (231, 190), (227, 207)),
                ((223, 209), (218, 205), (220, 198)),
                ((225, 177), (235, 157), (242, 148))], '#414b56', None)
s((244, 169), [((249, 165), (255, 164), (256, 166)),
                ((246, 182), (239, 199), (236, 215)),
                ((232, 216), (229, 211), (231, 205)),
                ((234, 190), (239, 177), (244, 169))], '#343d48', None)
s((306, 187), [((311, 189), (315, 193), (313, 199)),
                ((297, 218), (269, 228), (246, 227)),
                ((242, 224), (240, 219), (241, 216)),
                ((266, 217), (291, 205), (306, 187))], '#171e28', None)
t((228, 193), [((224, 202), (226, 211), (232, 214))], '#667480', .75)
t((233, 220), [((240, 224), (249, 225), (257, 223))], '#4d5e6c', .7)
t((258, 152), [((261, 158), (261, 163), (259, 168))], '#64717c', .65)
t((244, 166), [((245, 172), (243, 179), (239, 184))], '#d9a825', 2.5)
t((243, 167), [((243, 172), (241, 177), (240, 180))], '#f5d359', .8)

# Narrow lapel, shirt opening and necklace under the retained source neck.
s((277, 161), [((287, 164), (302, 169), (312, 177)),
                ((302, 198), (282, 216), (260, 226)),
                ((250, 222), (244, 218), (243, 211)),
                ((255, 192), (268, 174), (277, 161))], '#121b26')
s((278, 174), [((288, 180), (299, 176), (306, 173)),
                ((297, 190), (281, 202), (266, 209)),
                ((260, 207), (255, 202), (255, 198)),
                ((264, 186), (273, 178), (278, 174))], '#333f4b', None)
t((279, 177), [((287, 184), (298, 178), (304, 175))], '#bbcbd7', 1.4)
t((275, 184), [((271, 188), (270, 194), (273, 197))], '#adbfce', .65)
cloth.shape((270, 200), [((270, 198), (270, 195), (270, 195)),
                       ((271, 196), (272, 198), (273, 198)),
                       ((274, 196), (275, 193), (275, 193)),
                       ((276, 194), (277, 197), (277, 198)),
                       ((279, 197), (280, 196), (280, 196)),
                       ((280, 198), (279, 200), (279, 201)),
                       ((276, 203), (272, 203), (270, 200))], '#c9d4de', '#566b7d', .5)
s((263, 138), [((268, 140), (272, 146), (273, 151)),
                ((266, 173), (252, 195), (243, 209)),
                ((240, 210), (236, 207), (235, 204)),
                ((244, 185), (257, 155), (263, 138))], '#303b46')
t((268, 142), [((271, 146), (273, 149), (273, 151)),
                ((266, 173), (252, 195), (243, 209)),
                ((241, 209), (239, 208), (238, 207))], '#dbe4eb', 1.45)
t((266, 158), [((258, 177), (247, 197), (239, 204))], '#7e94a5', .65)
t((312, 179), [((301, 200), (281, 218), (260, 226)),
                ((251, 228), (240, 224), (234, 220))], '#dce6ec', 1.6)
t((308, 185), [((295, 205), (280, 216), (263, 222))], '#6b8091', .65)
for x, y in [(299, 194), (288, 207), (275, 218)]:
    cloth.ellipse((x-1.45, y-1.45, x+1.45, y+1.45), '#8a9eae', '#14202b', .5)
    cloth.ellipse((x-.6, y-1, x+.6, y), '#dde8ee')
s((248, 217), [((255, 222), (263, 222), (271, 218)),
                ((267, 225), (260, 229), (254, 230)),
                ((246, 229), (240, 226), (237, 221)),
                ((241, 223), (245, 221), (248, 217))], '#a41d27')
t((245, 225), [((250, 228), (261, 226), (265, 223))], '#e54c38', 1)
t((226, 224), [((242, 232), (265, 236), (280, 229))], '#e7b52b', 3)
t((230, 225), [((243, 232), (259, 233), (269, 231))], '#ffde61', .75)
repair = cloth.finish()
p = np.array(repair)
yy, xx = np.indices(p.shape[:2])
rp = p[:, :, :3].astype(float)
gray = (p[:, :, 3] > 0) & (rp.max(2)-rp.min(2) < 40) & (rp.max(2) < 115) & (rp.min(2) > 26)
light = 4*np.exp(-((xx-245)/28)**2-((yy-171)/35)**2)
rp[gray] += light[gray, None]
p[:, :, :3] = np.clip(rp, 0, 255).astype('uint8')
repair = Image.fromarray(p, 'RGBA')
body = Image.alpha_composite(body, repair)
body = Image.alpha_composite(body, source_jacket)

near = Art()
s, t = near.shape, near.stroke
s((303, 170), [((313, 170), (324, 178), (325, 189)),
                ((324, 198), (320, 208), (312, 211)),
                ((302, 207), (293, 197), (292, 187)),
                ((292, 178), (297, 171), (303, 170))], '#2b343e')
s((305, 175), [((313, 174), (321, 182), (320, 190)),
                ((316, 195), (309, 197), (302, 191)),
                ((298, 184), (299, 177), (305, 175))], '#44515d', None)
s((317, 180), [((322, 182), (325, 189), (321, 194)),
                ((317, 198), (311, 194), (311, 189)),
                ((310, 184), (313, 180), (317, 180))], '#354452', '#889aa8', .7)
for x, y in [(316, 183), (319, 191)]:
    near.ellipse((x-1.35, y-1.35, x+1.35, y+1.35), '#b6c7d3', '#253746', .5)
s((297, 196), [((304, 204), (315, 207), (323, 198)),
                ((323, 205), (317, 212), (312, 214)),
                ((305, 210), (300, 204), (297, 196))], '#e0e7ec', '#182632', 1)
t((301, 203), [((308, 209), (316, 209), (320, 205))], '#8ea3b2', .8)
s((312, 210), [((318, 213), (318, 230), (323, 237)),
                ((326, 242), (332, 244), (335, 240)),
                ((338, 238), (342, 243), (342, 247)),
                ((339, 252), (333, 255), (327, 251)),
                ((315, 247), (308, 235), (307, 223)),
                ((306, 218), (307, 212), (312, 210))], '#edb38c', '#3d2b24', 1.15)
s((307, 223), [((310, 236), (316, 248), (327, 251)),
                ((334, 255), (340, 251), (342, 247)),
                ((338, 248), (331, 249), (326, 245)),
                ((318, 239), (316, 228), (314, 222)),
                ((311, 220), (309, 221), (307, 223))], '#bd7e5e', None)
t((315, 214), [((315, 224), (319, 234), (321, 237))], '#ffd2a6', 1.1)
t((330, 243), [((332, 244), (336, 244), (339, 246))], '#f6c799', .85)
body = Image.alpha_composite(body, near.finish())

# Source hair/face/neck only: no old gold/straight-arm component survives.
head_mask = contour([(229, 0), (512, 0), (512, 169), (335, 169), (323, 174),
                     (305, 184), (284, 180), (273, 166), (267, 145),
                     (258, 126), (238, 114), (229, 114)])
head = original.copy()
head.putalpha(Image.fromarray((pixels[:, :, 3].astype(float)*np.array(head_mask)/255).round().astype('uint8')))
body = Image.alpha_composite(body, head)
body, removed = retain_main_body(body)
assert all(record['area_px'] < 90 for record in removed), removed
preserve_y = meta['lower_body_preserved_from_y']
old_body = Image.open(PRIOR/'body_rebuilt.png').convert('RGBA')
body.paste(old_body.crop((0, preserve_y, 512, 512)), (0, preserve_y))

layers = {name: Image.open(PRIOR/(name+'.png')).convert('RGBA')
          for name in ['weapon_back', 'weapon_foreground', 'approved_grip', 'chain']}
result = Image.alpha_composite(layers['weapon_back'], body)
for name in ['weapon_foreground', 'approved_grip', 'chain']:
    result = Image.alpha_composite(result, layers[name])
H = np.array(meta['master_to_screen_homography'])
cuff = H @ np.array([77, 50, 1])
cuff = cuff[:2]/cuff[2]
assert np.array(body.getchannel('A'))[int(round(cuff[1])), int(round(cuff[0]))] > 240, cuff
interior = np.array(layers['approved_grip'].getchannel('A')) == 255
assert np.array_equal(np.array(result)[interior], np.array(before)[interior])
assert np.array_equal(np.array(result)[preserve_y:], np.array(before)[preserve_y:])
for name, im in [('body_rebuilt', body), ('individual_clothing_repair', repair),
                 ('released_arm', far.finish()), ('holding_arm', near.finish()),
                 ('source_jacket_detail', source_jacket), ('head_preserved', head),
                 ('sora_run_loop_06_review', result)]:
    save_clean(im, OUT/(name+'.png'))
removal.save(OUT/'old_weapon_arm_removal_mask.png')
source_jacket_mask.save(OUT/'source_jacket_detail_mask.png')
head_mask.save(OUT/'head_contour_mask.png')
for name in layers:
    (OUT/(name+'.png')).write_bytes((PRIOR/(name+'.png')).read_bytes())
    assert (OUT/(name+'.png')).read_bytes() == (PRIOR/(name+'.png')).read_bytes()
meta.update({'status': 'individual loop06 jacket/arm refinement; gait/seam review pending',
             'source_review': PRIOR.name, 'prior_review_sha256': before_hash,
             'head_layer': 'head_preserved.png', 'projected_wrist_cuff': cuff.tolist(),
             'source_jacket_method': 'retained hood/far-pad detail outside old grip/guard, with gold excluded',
             'garment_method': 'new source-pose chest/sleeve contours and articulated arms; no shared torso template',
             'removed_detached_body_fragments': removed,
             'checks': ['original sheet/prior review hashes unchanged',
                        'weapon/grip/chain files byte-identical to v2',
                        'opaque grip interior exact; cuff inside forearm',
                        f'lower-body composite exact from y{preserve_y}'],
             'limitations': ['Cross-frame jacket and arm proportions still need idle-quality review.',
                             'Other garment repairs, alternating gait/root/timing and transitions remain unfinished.',
                             'Offline checks only; no Godot test or aerial work.']})
(OUT/'manifest.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
(OUT/'README.md').write_text(
    '# Loop06 jacket/arm repair\n\nThe old straight-arm fragment and shifted chest '
    'template are replaced with source-pose jacket, sleeve and bent-arm drawings. '
    'The real source head, waist/legs and small hood/far-pad details remain. '
    'Source-jacket and head contours exclude the previous gold guard/raised hand.\n\n'
    'Weapon, foreground guard, approved grip and chain PNG files are byte-identical '
    'to v2. See manifest for cuff, grip and lower-body preservation checks. '
    'Original sheet and prior versions remain. This is unfinished working art; '
    'gait/root/timing and transitions still need review. No Godot test or aerial art.\n', encoding='utf-8')
board = Image.new('RGB', (1536, 550), '#202633')
for column, (im, label) in enumerate([(original, 'Original / two-hand source pose'),
                                     (before, 'v2 / old straight-arm chest fragment'),
                                     (result, 'v3 / individual jacket and bent arm')]):
    board.paste(im, (column*512, 30), im)
    ImageDraw.Draw(board).text((column*512+12, 9), label, fill='white')
board.save(OUT/'Garment_Comparison.png')
review = Image.new('RGB', (1024, 720), '#202633')
review.paste(result, (0, 30), result)
light = Image.new('RGB', (512, 512), '#dedfe2')
light.paste(result, (0, 0), result)
review.paste(light, (512, 30))
ImageDraw.Draw(review).text((12, 9), 'Loop06 / jacket and wrist repair / dark, light and128px', fill='white')
for column, im in enumerate([result, result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
    small = im.resize((128, 128), Image.Resampling.LANCZOS)
    review.paste(small, (160+column*190, 580), small)
review.save(OUT/'Dark_Light_Game_Review.png')
Image.open(OUT/'sora_run_loop_06_review.png').verify()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
assert hashlib.sha256(before_path.read_bytes()).hexdigest() == before_hash
print('Loop06 saved; original source, grip/carry layers and lower body preserved. Cuff:', cuff.tolist())
