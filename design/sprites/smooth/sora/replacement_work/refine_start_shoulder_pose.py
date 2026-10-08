"""Local, pose-specific shoulder-settle drawing; never alters the source sheet.

Run from the workspace root. This is an offline art helper, not engine code.
"""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[4]
assert WORKSPACE.name == 'KH Fighting Game', WORKSPACE
READY = ROOT / 'ready'
OUT = READY / 'run_start/refinement_v3'
SOURCE = READY / 'run_start/run_start_source.png'
SOURCE_HASH = '1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
OUT.mkdir(parents=True, exist_ok=True)
S = 4
SIZE = (512, 512)
original = Image.new('RGBA', SIZE)
original.paste(Image.open(SOURCE).convert('RGBA').crop((1333, 0, 1774, 450)), (0, 0))


def samples(start, segments):
    points = [start]
    a = start
    for b, c, end in segments:
        for j in range(1, 33):
            t = j / 32
            u = 1 - t
            points.append((u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*end[0],
                           u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*end[1]))
        a = end
    return [(round(x*S), round(y*S)) for x, y in points]


paint = Image.new('RGBA', (512*S, 512*S))


def shape(start, segments, color, outline='#14171d', width=1.35):
    points = samples(start, segments)
    d = ImageDraw.Draw(paint)
    d.polygon(points, fill=color)
    if outline:
        d.line(points + points[:1], fill=outline, width=round(width*S), joint='curve')


def stroke(start, segments, color, width=1.2):
    ImageDraw.Draw(paint).line(samples(start, segments), fill=color,
                              width=round(width*S), joint='curve')


def ellipse(box, color, outline=None, width=1):
    ImageDraw.Draw(paint).ellipse(tuple(round(v*S) for v in box), fill=color,
                                 outline=outline, width=round(width*S))


# Preserve the actual source head with a contour, rather than a rectangular
# restoration that would bring back the old raised arm and gold guard.
head_mask = Image.new('L', SIZE)
head_outline = [(329, 86), (344, 100), (358, 86), (372, 116),
                (407, 117), (393, 132), (409, 150), (399, 158),
                (408, 166), (397, 169), (402, 182), (388, 174),
                (388, 195), (372, 197), (357, 193), (346, 199),
                (330, 190), (314, 186), (302, 188), (307, 173),
                (288, 183), (289, 171), (298, 159), (278, 164),
                (287, 152), (280, 145), (290, 139), (277, 131),
                (293, 125), (284, 119), (309, 115), (296, 99),
                (325, 105)]
ImageDraw.Draw(head_mask).polygon(head_outline, fill=255)
pixels = np.array(original)
hm = np.array(head_mask)
# The old gold guard touches the left hair edge. Exclude its yellow pixels.
gold = ((pixels[:, :, 0] > 95) & (pixels[:, :, 1] > 65)
        & (pixels[:, :, 2] < 40)
        & (pixels[:, :, 1] > pixels[:, :, 0]*.60))
gold[:, 292:] = False
hm[gold] = 0
head_mask = Image.fromarray(hm, 'L')
head = original.copy()
head.putalpha(Image.composite(original.getchannel('A'), Image.new('L', SIZE), head_mask))

removal = Image.new('L', SIZE)
rd = ImageDraw.Draw(removal)
# Original shaft/teeth, guard/two hands, raised arm, and dangling chain.
rd.polygon([(89, 17), (185, 17), (189, 84), (250, 115),
            (239, 143), (91, 68)], fill=255)
rd.polygon([(170, 118), (235, 100), (301, 135), (294, 180),
            (258, 206), (173, 202)], fill=255)
rd.polygon([(237, 157), (284, 160), (332, 188), (332, 222),
            (303, 228), (242, 204)], fill=255)
rd.polygon([(172, 187), (201, 190), (208, 225), (201, 247),
            (164, 246), (164, 218)], fill=255)
body = original.copy()
body.putalpha(Image.composite(Image.new('L', SIZE), original.getchannel('A'), removal))

# Far sleeve and the arm released from the former two-handed grip.
shape((248, 181), [((258, 180), (268, 188), (272, 201)),
                   ((266, 214), (249, 227), (235, 225)),
                   ((224, 218), (222, 208), (227, 196)),
                   ((233, 188), (240, 183), (248, 181))], '#2c3038')
shape((245, 187), [((256, 185), (266, 194), (265, 204)),
                   ((251, 215), (237, 217), (230, 210)),
                   ((231, 201), (237, 193), (245, 187))], '#454a53', None)
shape((240, 190), [((245, 186), (252, 187), (255, 192)),
                   ((258, 198), (253, 205), (248, 206)),
                   ((242, 205), (237, 197), (240, 190))], '#333a43', '#78838d', .8)
stroke((241, 191), [((245, 187), (251, 189), (253, 193))], '#a6afb5', .7)
ellipse((244, 194, 247, 197), '#b6c1c9', '#222b35', .5)
ellipse((249, 201, 252, 204), '#a6b3bd', '#222b35', .5)
shape((228, 208), [((239, 220), (254, 219), (266, 209)),
                   ((264, 216), (250, 228), (237, 230)),
                   ((230, 226), (225, 219), (228, 208))], '#e7eced')
stroke((230, 214), [((239, 225), (252, 224), (263, 215))], '#88939d', 1)
shape((232, 228), [((232, 233), (224, 238), (220, 243)),
                   ((221, 249), (229, 252), (237, 252)),
                   ((241, 254), (240, 261), (235, 263)),
                   ((221, 264), (210, 256), (209, 246)),
                   ((208, 237), (215, 230), (224, 224)),
                   ((227, 224), (230, 226), (232, 228))], '#eeb48b')
shape((213, 241), [((211, 249), (218, 256), (233, 258)),
                   ((236, 259), (235, 262), (232, 262)),
                   ((218, 261), (210, 254), (210, 246)),
                   ((209, 244), (211, 242), (213, 241))], '#bd8062', None)
stroke((219, 237), [((217, 242), (216, 246), (221, 250))], '#ffd2a5', 1.2)

# Chest material previously occluded by the horizontal arm. Follow the actual
# lean and keep the original lower jacket/waist and all of the source legs.
shape((279, 173), [((291, 171), (308, 176), (324, 189)),
                   ((338, 204), (338, 226), (321, 244)),
                   ((305, 257), (286, 263), (270, 258)),
                   ((250, 249), (238, 232), (239, 214)),
                   ((247, 199), (261, 182), (279, 173))], '#24282f')
shape((276, 181), [((282, 178), (292, 180), (297, 185)),
                   ((282, 196), (269, 215), (263, 232)),
                   ((254, 230), (246, 224), (247, 214)),
                   ((253, 200), (267, 186), (276, 181))], '#41454d', None)
shape((307, 201), [((317, 206), (326, 219), (321, 231)),
                   ((310, 245), (293, 255), (280, 255)),
                   ((293, 239), (302, 220), (307, 201))], '#151b23', None)
stroke((258, 219), [((253, 229), (257, 237), (267, 244))], '#62656a', .9)
stroke((275, 247), [((281, 251), (288, 253), (296, 250))], '#42484e', .9)

# Open shirt, silver-edged jacket lapels, and a neck opening beneath the head.
shape((300, 178), [((310, 178), (323, 182), (334, 191)),
                   ((322, 212), (310, 231), (294, 244)),
                   ((288, 241), (279, 233), (277, 227)),
                   ((287, 209), (294, 193), (300, 178))], '#141b24')
shape((304, 180), [((312, 181), (321, 187), (325, 194)),
                   ((318, 204), (308, 206), (301, 200)),
                   ((298, 194), (300, 186), (304, 180))], '#e7ab83')
shape((304, 199), [((312, 207), (321, 205), (326, 196)),
                   ((321, 214), (308, 227), (300, 233)),
                   ((296, 228), (293, 222), (292, 217)),
                   ((297, 209), (301, 202), (304, 199))], '#343941')
stroke((303, 203), [((312, 212), (318, 208), (324, 202))], '#bcc5cc', 1.5)
stroke((297, 220), [((301, 221), (305, 226), (307, 220)),
                    ((310, 218), (315, 220), (315, 215))], '#b4c0cb', 1.2)
shape((286, 175), [((291, 172), (299, 175), (303, 179)),
                   ((292, 193), (280, 211), (270, 226)),
                   ((263, 223), (257, 219), (254, 215)),
                   ((266, 203), (279, 187), (286, 175))], '#2e343d')
stroke((289, 175), [((294, 175), (300, 177), (303, 179)),
                    ((292, 194), (280, 211), (270, 226)),
                    ((264, 223), (258, 219), (254, 215))], '#d8dfe3', 1.9)
stroke((332, 191), [((322, 213), (309, 233), (296, 243))], '#e0e5e7', 1.9)
stroke((329, 196), [((320, 215), (308, 232), (298, 240))], '#737f89', .7)
shape((290, 239), [((290, 243), (284, 250), (278, 254)),
                   ((270, 252), (264, 247), (262, 242)),
                   ((270, 246), (280, 245), (290, 239))], '#a21d23')
shape((286, 242), [((283, 245), (280, 248), (277, 250)),
                   ((274, 250), (271, 248), (269, 247)),
                   ((275, 248), (281, 245), (286, 242))], '#ef4131', None)
stroke((296, 243), [((294, 248), (290, 254), (286, 258)),
                    ((280, 260), (272, 258), (267, 256))], '#dce2e5', 1.8)
stroke((292, 244), [((289, 249), (285, 253), (281, 254))], '#747e88', .7)
stroke((261, 236), [((264, 241), (269, 243), (273, 243))], '#60656a', .8)
# Yellow garment straps and small metal fasteners use the idle's materials.
stroke((263, 198), [((265, 204), (262, 212), (258, 215))], '#eab127', 2.3)
stroke((263, 201), [((261, 202), (259, 205), (258, 208))], '#f8da55', .8)
for x, y in [(315, 211), (309, 220), (302, 230)]:
    ellipse((x-1.8, y-1.8, x+1.8, y+1.8), '#8995a2', '#121b24', .6)
    ellipse((x-1, y-1.4, x+.5, y), '#e2e8ec')

# Released far glove; fingers curl independently rather than retain old grip.
shape((235, 249), [((240, 247), (246, 251), (248, 257)),
                   ((251, 263), (247, 269), (241, 270)),
                   ((234, 269), (229, 266), (228, 261)),
                   ((228, 255), (231, 252), (235, 249))], '#202b36')
shape((234, 252), [((239, 250), (244, 252), (246, 256)),
                   ((241, 259), (237, 260), (232, 258)),
                   ((232, 255), (233, 254), (234, 252))], '#414c56', None)
stroke((231, 253), [((229, 257), (231, 263), (235, 266))], '#d3ac40', 1.4)
for x, y in [(241, 264), (245, 262), (247, 259)]:
    ellipse((x-1.6, y-1.9, x+1.6, y+1.9), '#eab189', '#805940', .6)

# Near shoulder sleeve and articulated bent arm support the same-side carry.
shape((330, 190), [((343, 190), (355, 198), (362, 211)),
                   ((366, 222), (361, 234), (351, 238)),
                   ((339, 235), (330, 226), (326, 214)),
                   ((324, 203), (325, 195), (330, 190))], '#292e36')
shape((336, 195), [((347, 195), (357, 204), (359, 214)),
                   ((357, 223), (349, 229), (342, 226)),
                   ((332, 219), (329, 204), (336, 195))], '#474c54', None)
shape((348, 205), [((354, 206), (358, 215), (355, 219)),
                   ((350, 224), (343, 219), (340, 213)),
                   ((339, 207), (343, 203), (348, 205))], '#343a43', '#737c83', .8)
ellipse((347, 208, 350, 211), '#b6c1c9', '#222b35', .5)
ellipse((352, 216, 355, 219), '#a6b3bd', '#222b35', .5)
shape((334, 226), [((342, 231), (352, 233), (360, 226)),
                   ((360, 232), (356, 239), (350, 241)),
                   ((342, 240), (336, 234), (334, 226))], '#e2e6e8')
stroke((337, 229), [((346, 236), (353, 236), (358, 231))], '#84919b', 1)
shape((351, 238), [((356, 240), (359, 251), (365, 256)),
                   ((370, 258), (375, 255), (381, 252)),
                   ((385, 251), (389, 256), (386, 261)),
                   ((379, 267), (369, 273), (361, 268)),
                   ((351, 262), (346, 250), (346, 242)),
                   ((346, 239), (348, 238), (351, 238))], '#eab089')
shape((347, 244), [((350, 254), (355, 265), (363, 269)),
                   ((372, 272), (379, 266), (385, 260)),
                   ((382, 262), (373, 265), (366, 263)),
                   ((357, 259), (354, 250), (354, 244)),
                   ((352, 243), (349, 242), (347, 244))], '#bc7e60', None)
stroke((354, 241), [((357, 248), (359, 254), (363, 257))], '#ffd3a7', 1.4)
stroke((370, 258), [((374, 258), (376, 257), (379, 256))], '#ffd1a3', 1)

repair = paint.resize(SIZE, Image.Resampling.LANCZOS)
body = Image.alpha_composite(body, repair)
# Restore the contoured head last; no old raised-hand rectangle is copied.
body = Image.alpha_composite(body, head)

hand = (395, 242)
screen_angle = 218
foreground_yaw = 20
theta = math.radians(screen_angle)
yaw = math.radians(foreground_yaw)
c, s = math.cos(theta), math.sin(theta)
H = (np.array([[c, -s, hand[0]], [s, c, hand[1]], [0, 0, 1]])
     @ np.array([[math.cos(yaw), 0, 0], [0, 1, 0], [-math.sin(yaw)/1400, 0, 1]])
     @ np.array([[1, 0, -77], [0, 1, -70], [0, 0, 1]]))
inverse = np.linalg.inv(H)
inverse /= inverse[2, 2]


def project(point):
    q = H @ np.array([point[0], point[1], 1])
    return (q[:2] / q[2]).tolist()


def transformed(layer):
    return layer.transform(SIZE, Image.Transform.PERSPECTIVE,
                           tuple(inverse.flatten()[:8]), Image.Resampling.BICUBIC)


master_dir = READY / 'run_loop/layers/art_pass_05'
master = Image.open(master_dir / 'kingdom_key_master_finished.png').convert('RGBA')
weapon = transformed(master)
front_mask = Image.new('L', master.size)
ImageDraw.Draw(front_mask).rectangle((0, 0, 141, master.height), fill=255)
front_master = master.copy()
front_master.putalpha(Image.composite(master.getchannel('A'), Image.new('L', master.size), front_mask))
front_weapon = transformed(front_master)
grip = transformed(Image.open(master_dir / 'grip_master_space.png').convert('RGBA'))
# Shaft rests behind Sora's hair/neck. Guard and hand remain in front.
result = Image.alpha_composite(weapon, body)
result = Image.alpha_composite(result, front_weapon)
result = Image.alpha_composite(result, grip)

# A separate chain with alternating link faces and the three-circle charm.
paint = Image.new('RGBA', (512*S, 512*S))
pommel = project((34, 70))
for i in range(8):
    t = i / 7
    x = pommel[0] - 6*t*t
    y = pommel[1] + 3 + i*3.8
    if i % 2:
        ellipse((x-1, y-2.5, x+1, y+2.5), '#8394a3', '#25303a', .5)
        stroke((x-.4, y-1.5), [((x-.4, y-.5), (x-.4, y+.5), (x-.4, y+1.5))], '#dae0e5', .5)
    else:
        ellipse((x-2, y-2.7, x+2, y+2.7), None, '#b9c4cd', .8)
cx, cy = pommel[0]-6, pommel[1]+37
ellipse((cx-10, cy-8, cx-1, cy+1), '#aab9c7', '#17232d', .9)
ellipse((cx+1, cy-8, cx+10, cy+1), '#aab9c7', '#17232d', .9)
ellipse((cx-6, cy-3, cx+6, cy+9), '#aab9c7', '#17232d', 1)
ellipse((cx-4, cy-2, cx+1, cy+3), '#d5dfe6')
chain = paint.resize(SIZE, Image.Resampling.LANCZOS)
result = Image.alpha_composite(result, chain)


def save_clean(im, name):
    a = np.array(im)
    a[a[:, :, 3] == 0, :3] = 0
    Image.fromarray(a, 'RGBA').save(OUT / name)


for im, name in [(body, 'frame_03_body_plate.png'), (repair, 'frame_03_local_repair.png'),
                 (head_mask.convert('RGBA'), 'frame_03_head_mask.png'),
                 (weapon, 'frame_03_weapon.png'), (front_weapon, 'frame_03_weapon_foreground.png'),
                 (grip, 'frame_03_grip.png'), (chain, 'frame_03_chain.png'),
                 (result, 'sora_run_start_03.png')]:
    save_clean(im, name)
removal.save(OUT / 'frame_03_removal_mask.png')

comparison = Image.new('RGB', (1024, 550), '#202633')
for i, (im, title) in enumerate([(original, 'Original raised two-hand pose'),
                                (result, 'Shoulder settle: rigid carry and released far arm')]):
    comparison.paste(im, (i*512, 32), im)
    ImageDraw.Draw(comparison).text((i*512+12, 10), title, fill='white')
comparison.save(OUT / 'Frame_03_Comparison.png')

qa = Image.new('RGB', (1024, 720), '#202633')
qa.paste(result, (0, 28), result)
light = Image.new('RGB', SIZE, '#e1e2e4')
light.paste(result, (0, 0), result)
qa.paste(light, (512, 28))
d = ImageDraw.Draw(qa)
d.text((12, 8), 'Shoulder-settle art review / dark and light backgrounds', fill='white')
for i, im in enumerate([result, result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
    small = im.resize((128, 128), Image.Resampling.LANCZOS)
    qa.paste(small, (180+i*170, 568), small)
d.text((175, 548), '128px review / mirrored', fill='white')
qa.save(OUT / 'Frame_03_Review.png')

anchors = {name: project(p) for name, p in {'grip': (77, 70), 'pommel': (34, 70),
            'collar': (137, 70), 'tip': (319, 70)}.items()}
shaft = np.array(anchors['tip']) - anchors['collar']
handle = np.array(anchors['collar']) - anchors['grip']
assert abs(float(np.cross(shaft, handle))) < 1e-6
assert np.allclose(anchors['grip'], hand)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
# Lower-body source pixels are preserved exactly, excluding the new chain.
assert np.array_equal(np.array(body)[280:], np.array(original)[280:])
manifest = {'status': 'individual shoulder-settle art refinement; not final',
            'source_crop': [1333, 0, 1774, 450], 'source_sha256': SOURCE_HASH,
            'hand_anchor': hand, 'screen_angle_degrees': screen_angle,
            'foreground_yaw_degrees': foreground_yaw,
            'physical_master_length_px': 285, 'master_scale': 1,
            'master_to_screen_homography': H.tolist(), 'projected_anchors': anchors,
            'occlusion': 'shaft behind head/body; connected guard and approved grip in front',
            'limitations': ['New jacket/arm materials still need comparison with idle.',
                            'Adjacent frame registration and gait remain under review.',
                            'Offline image checks only; no Godot integration or testing.']}
(OUT / 'frame_03_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('Saved shoulder-settle art and layers:', OUT)
