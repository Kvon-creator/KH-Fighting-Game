"""Draw the distinct push-off arm/jacket around the fourth source transition."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, carry, save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
OUT = READY/'run_start/refinement_v3'
SOURCE = READY/'run_start/run_start_source.png'
EXPECTED = '1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
OUT.mkdir(parents=True, exist_ok=True)
original = Image.new('RGBA', (512, 512))
original.paste(Image.open(SOURCE).convert('RGBA').crop((0, 450, 445, 887)), (0, 0))

head_mask = Image.new('L', original.size)
ImageDraw.Draw(head_mask).polygon([
    (357, 43), (372, 63), (369, 47), (388, 79), (418, 80),
    (398, 98), (418, 112), (408, 122), (419, 132), (402, 134),
    (410, 145), (396, 138), (398, 157), (384, 174), (369, 171),
    (359, 163), (347, 159), (341, 174), (326, 178), (307, 178),
    (305, 164), (309, 159), (302, 149), (291, 155), (295, 144),
    (285, 144), (293, 133), (282, 130), (285, 124), (268, 117),
    (288, 111), (274, 101), (298, 91), (282, 91), (307, 80),
    (296, 74), (322, 76), (309, 58), (334, 69), (336, 56)], fill=255)
hm, pixels = np.array(head_mask), np.array(original)
gold = ((pixels[:, :, 0] > 95) & (pixels[:, :, 1] > 65) & (pixels[:, :, 2] < 40)
        & (pixels[:, :, 1] > pixels[:, :, 0]*.60))
gold[:, 302:] = False
hm[gold] = 0
head_mask = Image.fromarray(hm, 'L')
head = original.copy()
head.putalpha(Image.composite(original.getchannel('A'), Image.new('L', original.size), head_mask))

removal = Image.new('L', original.size)
d = ImageDraw.Draw(removal)
d.polygon([(85, 15), (180, 15), (183, 63), (252, 97),
           (237, 125), (84, 66)], fill=255)
d.polygon([(191, 110), (244, 93), (282, 112), (289, 163),
           (269, 186), (219, 184), (183, 143)], fill=255)
d.polygon([(246, 154), (278, 158), (306, 182), (328, 193),
           (328, 214), (292, 222), (260, 202), (244, 180)], fill=255)
d.polygon([(120, 174), (187, 113), (216, 111), (220, 140),
           (181, 169), (168, 209), (130, 211), (118, 197)], fill=255)
body = original.copy()
body.putalpha(Image.composite(Image.new('L', original.size), original.getchannel('A'), removal))

art = Art()
shape, stroke, ellipse = art.shape, art.stroke, art.ellipse
# Far shoulder rotates back; elbow swings toward the waist rather than staying
# in the source two-handed grip. Its articulation differs from frame 03.
shape((264, 127), [((277, 126), (289, 136), (291, 146)),
                   ((285, 158), (270, 169), (256, 167)),
                   ((246, 164), (239, 153), (241, 144)),
                   ((245, 135), (255, 128), (264, 127))], '#2b3038')
shape((258, 133), [((269, 129), (282, 138), (284, 146)),
                   ((277, 156), (264, 161), (252, 156)),
                   ((250, 146), (252, 139), (258, 133))], '#464b53', None)
shape((256, 133), [((263, 130), (270, 134), (272, 141)),
                   ((273, 148), (266, 154), (260, 152)),
                   ((253, 150), (251, 139), (256, 133))], '#343a43', '#7b8690', .8)
ellipse((258, 136, 261, 139), '#b6c1c9', '#222b35', .5)
ellipse((264, 146, 267, 149), '#a6b3bd', '#222b35', .5)
shape((244, 152), [((252, 161), (267, 165), (280, 157)),
                   ((278, 165), (267, 172), (257, 172)),
                   ((248, 169), (243, 162), (244, 152))], '#e1e7ea')
stroke((247, 159), [((256, 170), (269, 168), (277, 162))], '#85929c', 1)
shape((255, 169), [((251, 174), (244, 181), (239, 186)),
                   ((240, 191), (246, 196), (250, 200)),
                   ((253, 204), (249, 210), (244, 209)),
                   ((233, 204), (226, 195), (227, 187)),
                   ((229, 178), (238, 169), (247, 163)),
                   ((250, 164), (253, 166), (255, 169))], '#eeb58d')
shape((231, 181), [((228, 187), (231, 196), (242, 203)),
                   ((246, 205), (248, 207), (244, 208)),
                   ((234, 204), (227, 196), (228, 188)),
                   ((228, 185), (229, 183), (231, 181))], '#bc8061', None)
stroke((243, 176), [((237, 181), (234, 185), (237, 190))], '#ffd4a7', 1.2)

# The chest follows the push-off's stronger forward lean. Its lower hem meets
# the existing yellow waist belt, whose source pixels remain untouched below225.
shape((284, 145), [((298, 146), (316, 159), (332, 177)),
                   ((346, 187), (340, 199), (324, 209)),
                   ((308, 220), (286, 222), (268, 216)),
                   ((250, 209), (240, 195), (247, 180)),
                   ((256, 165), (271, 151), (284, 145))], '#252a31')
shape((278, 151), [((287, 148), (296, 152), (301, 158)),
                   ((286, 168), (271, 182), (265, 196)),
                   ((258, 195), (249, 188), (252, 179)),
                   ((258, 168), (269, 156), (278, 151))], '#41464e', None)
shape((316, 180), [((326, 184), (331, 193), (323, 202)),
                   ((310, 213), (289, 217), (280, 213)),
                   ((296, 205), (309, 193), (316, 180))], '#171e27', None)
stroke((260, 191), [((258, 196), (261, 200), (267, 203))], '#5e636b', .9)
stroke((267, 207), [((274, 211), (279, 211), (286, 211))], '#434a53', .9)
shape((310, 158), [((317, 159), (326, 167), (334, 176)),
                   ((323, 191), (307, 201), (296, 205)),
                   ((290, 203), (283, 198), (280, 191)),
                   ((291, 180), (303, 167), (310, 158))], '#171f29')
shape((308, 174), [((315, 181), (323, 178), (330, 174)),
                   ((322, 187), (306, 195), (297, 198)),
                   ((293, 194), (291, 190), (291, 187)),
                   ((298, 182), (304, 178), (308, 174))], '#363d46')
stroke((308, 177), [((314, 186), (323, 181), (328, 178))], '#c4cdd4', 1.4)
stroke((299, 191), [((304, 192), (308, 194), (309, 189)),
                    ((312, 187), (317, 189), (318, 185))], '#bac5ce', 1.2)
shape((290, 146), [((296, 146), (305, 152), (311, 157)),
                   ((296, 169), (281, 183), (270, 195)),
                   ((264, 193), (259, 188), (255, 183)),
                   ((269, 169), (280, 156), (290, 146))], '#303741')
stroke((292, 147), [((300, 150), (307, 154), (311, 157)),
                    ((296, 169), (281, 183), (270, 195)),
                    ((264, 193), (259, 188), (255, 183))], '#dce3e6', 1.9)
stroke((333, 176), [((324, 193), (309, 205), (296, 214)),
                    ((285, 218), (275, 214), (269, 211))], '#dfe5e8', 1.9)
stroke((331, 181), [((322, 194), (306, 207), (297, 210))], '#77838f', .7)
shape((292, 203), [((290, 207), (285, 210), (281, 211)),
                   ((274, 209), (270, 207), (267, 203)),
                   ((275, 206), (284, 206), (292, 203))], '#b82127')
stroke((271, 205), [((277, 209), (282, 209), (286, 207))], '#ed4935', 1.2)
stroke((273, 162), [((276, 166), (274, 171), (270, 174))], '#efb62c', 2.2)
stroke((275, 164), [((273, 164), (271, 166), (270, 169))], '#ffdb54', .8)
for x, y in [(322, 183), (314, 191), (306, 199)]:
    ellipse((x-1.8, y-1.8, x+1.8, y+1.8), '#8e9ba7', '#121b24', .6)
    ellipse((x-1, y-1.4, x+.5, y), '#e2e8ec')

# Released far glove sits beside the waist, clear of the new carrying arm.
shape((245, 197), [((251, 196), (256, 200), (258, 205)),
                   ((261, 211), (258, 217), (252, 219)),
                   ((245, 219), (239, 215), (238, 210)),
                   ((238, 204), (241, 200), (245, 197))], '#222c37')
shape((244, 200), [((249, 198), (255, 202), (256, 206)),
                   ((251, 209), (246, 210), (241, 207)),
                   ((241, 204), (242, 202), (244, 200))], '#424d58', None)
stroke((241, 200), [((238, 205), (241, 212), (244, 214))], '#d3ad42', 1.4)
for x, y in [(252, 213), (256, 210), (257, 207)]:
    ellipse((x-1.5, y-1.9, x+1.5, y+1.9), '#ebb48d', '#805940', .6)

# Near elbow folds beneath the grip. Shoulder, wrist, and rigid shaft remain on
# one side of the body, with the same approved hand orientation.
shape((336, 176), [((347, 176), (358, 185), (361, 195)),
                   ((364, 205), (355, 217), (347, 218)),
                   ((337, 214), (330, 206), (327, 195)),
                   ((325, 186), (329, 178), (336, 176))], '#2a3038')
shape((338, 181), [((347, 180), (356, 190), (357, 198)),
                   ((355, 205), (348, 210), (341, 206)),
                   ((333, 199), (331, 187), (338, 181))], '#484e56', None)
shape((347, 187), [((353, 187), (357, 195), (354, 199)),
                   ((350, 205), (344, 201), (341, 195)),
                   ((340, 190), (343, 187), (347, 187))], '#343c46', '#7c8790', .8)
ellipse((346, 189, 349, 192), '#b6c1c9', '#222b35', .5)
ellipse((351, 197, 354, 200), '#a6b3bd', '#222b35', .5)
shape((333, 205), [((340, 211), (351, 214), (358, 205)),
                   ((358, 211), (353, 218), (347, 221)),
                   ((339, 219), (335, 213), (333, 205))], '#e1e7ea')
stroke((337, 210), [((345, 217), (351, 216), (356, 211))], '#88959f', 1)
shape((347, 217), [((353, 219), (352, 230), (359, 234)),
                   ((365, 237), (374, 231), (380, 227)),
                   ((384, 225), (388, 231), (384, 235)),
                   ((376, 242), (365, 248), (356, 245)),
                   ((346, 241), (342, 229), (342, 220)),
                   ((342, 217), (345, 216), (347, 217))], '#ecb28b')
shape((343, 224), [((345, 234), (350, 242), (358, 246)),
                   ((368, 248), (379, 240), (384, 234)),
                   ((379, 237), (369, 242), (362, 240)),
                   ((353, 237), (351, 227), (350, 222)),
                   ((347, 221), (344, 221), (343, 224))], '#bd8061', None)
stroke((350, 221), [((351, 226), (353, 232), (357, 235))], '#ffd4a7', 1.3)
stroke((365, 236), [((371, 235), (375, 232), (379, 230))], '#ffd1a4', 1)

repair = art.finish()
body = Image.alpha_composite(body, repair)
body = Image.alpha_composite(body, head)
hand, angle, yaw = (390, 215), 218, 22
weapon, front, grip, chain, H, anchors = carry(READY/'run_loop/layers/art_pass_05', hand, angle, yaw)
result = Image.alpha_composite(weapon, body)
for layer in [front, grip, chain]:
    result = Image.alpha_composite(result, layer)
for im, name in [(body, 'body_plate'), (repair, 'local_repair'), (weapon, 'weapon'),
                 (front, 'weapon_foreground'), (grip, 'grip'), (chain, 'chain')]:
    save_clean(im, OUT/f'frame_04_{name}.png')
save_clean(result, OUT/'sora_run_start_04.png')
head_mask.save(OUT/'frame_04_head_mask.png')
removal.save(OUT/'frame_04_removal_mask.png')
comparison = Image.new('RGB', (1024, 550), '#202633')
for i, (im, title) in enumerate([(original, 'Original push-off pose'),
                                (result, 'Push-off: individual arm / connected shoulder carry')]):
    comparison.paste(im, (i*512, 32), im)
    ImageDraw.Draw(comparison).text((i*512+12, 10), title, fill='white')
comparison.save(OUT/'Frame_04_Comparison.png')
assert np.array_equal(np.array(body)[250:], np.array(original)[250:])
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
(OUT/'frame_04_manifest.json').write_text(json.dumps({
    'status': 'individual push-off refinement; art review', 'source_crop': [0, 450, 445, 887],
    'source_sha256': EXPECTED, 'hand_anchor': hand, 'screen_angle_degrees': angle,
    'foreground_yaw_degrees': yaw, 'physical_master_length_px': 285, 'master_scale': 1,
    'master_to_screen_homography': H.tolist(), 'projected_anchors': anchors,
    'occlusion': 'shaft behind head/body; guard and corrected hand in front',
    'limitations': ['New chest/arm details require further idle-quality comparison.',
                    'Floor alignment and neighboring-frame timing are package review work.',
                    'No Godot integration or engine testing.']}, indent=2), encoding='utf-8')
print('Saved individual push-off art and layers:', OUT)
