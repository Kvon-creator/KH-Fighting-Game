"""Replace the lift frame's oversized cloth repair with anatomical local art."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, carry, save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
OUT = READY/'run_start/refinement_v4'
SOURCE = READY/'run_start/run_start_source.png'
EXPECTED = '1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
OUT.mkdir(parents=True, exist_ok=True)
original = Image.new('RGBA', (512, 512))
original.paste(Image.open(SOURCE).convert('RGBA').crop((889, 0, 1333, 450)), (0, 0))
removal = Image.new('L', original.size)
d = ImageDraw.Draw(removal)
d.polygon([(13, 132), (109, 127), (193, 215), (225, 246),
           (191, 268), (17, 190)], fill=255)
d.polygon([(153, 219), (191, 211), (237, 229), (255, 267),
           (238, 295), (214, 314), (161, 282)], fill=255)
d.polygon([(199, 207), (220, 208), (240, 231), (237, 251),
           (203, 239), (191, 224)], fill=255)
d.polygon([(239, 232), (312, 229), (338, 239), (327, 263),
           (250, 271), (237, 256)], fill=255)
d.polygon([(229, 279), (249, 279), (257, 320), (258, 349),
           (247, 355), (219, 351), (216, 326), (226, 311)], fill=255)
body = original.copy()
body.putalpha(Image.composite(Image.new('L', original.size), original.getchannel('A'), removal))

art = Art()
shape, stroke, ellipse = art.shape, art.stroke, art.ellipse
# Small jacket hem behind the former horizontal forearm. Do not extend the
# jacket into the old hand/guard position, which is outside the actual torso.
shape((244, 240), [((268, 237), (295, 237), (316, 239)),
                   ((317, 250), (311, 265), (299, 273)),
                   ((280, 278), (255, 270), (240, 257)),
                   ((237, 250), (238, 244), (244, 240))], '#252a31')
shape((245, 242), [((258, 240), (270, 242), (277, 246)),
                   ((268, 253), (253, 255), (243, 252)),
                   ((242, 248), (241, 244), (245, 242))], '#3d424a', None)
shape((298, 245), [((306, 248), (306, 258), (298, 265)),
                   ((288, 271), (273, 270), (266, 266)),
                   ((281, 263), (291, 255), (298, 245))], '#161d26', None)
shape((261, 254), [((274, 255), (282, 255), (291, 251)),
                   ((288, 261), (279, 267), (271, 266)),
                   ((266, 263), (263, 259), (261, 254))], '#a82027')
stroke((267, 258), [((274, 264), (282, 261), (287, 257))], '#ef4633', 1.2)
stroke((314, 241), [((310, 253), (306, 265), (298, 271)),
                    ((285, 277), (268, 272), (257, 267))], '#dce4e8', 1.9)
stroke((309, 247), [((306, 256), (301, 266), (297, 268))], '#77838e', .7)
stroke((251, 258), [((255, 261), (260, 263), (263, 263))], '#677079', .8)
stroke((300, 256), [((300, 259), (298, 262), (296, 263))], '#eeb733', 2)

# Left shorts area concealed by the old guard. Match the source's volume;
# the crotch gap below it stays transparent rather than becoming extra cloth.
shape((156, 271), [((177, 265), (204, 266), (227, 272)),
                   ((240, 270), (255, 270), (266, 279)),
                   ((258, 294), (244, 306), (225, 317)),
                   ((204, 319), (179, 309), (164, 298)),
                   ((156, 289), (152, 278), (156, 271))], '#24282e')
shape((186, 274), [((204, 272), (223, 278), (234, 290)),
                   ((230, 300), (218, 307), (206, 309)),
                   ((190, 300), (183, 283), (186, 274))], '#2d3237', None)
shape((241, 277), [((249, 276), (257, 279), (259, 285)),
                   ((249, 297), (237, 306), (225, 310)),
                   ((229, 298), (235, 286), (241, 277))], '#151c25', None)
shape((172, 273), [((190, 271), (208, 281), (218, 294)),
                   ((224, 303), (219, 313), (211, 319)),
                   ((195, 317), (178, 308), (169, 292)),
                   ((166, 284), (167, 277), (172, 273))], '#25292d')
shape((177, 278), [((190, 276), (204, 282), (211, 293)),
                   ((209, 303), (197, 308), (187, 306)),
                   ((178, 296), (174, 284), (177, 278))], '#2e3338', None)
shape((209, 291), [((215, 296), (218, 303), (217, 311)),
                   ((213, 316), (208, 318), (203, 317)),
                   ((208, 310), (210, 301), (209, 291))], '#171c22', None)
shape((200, 277), [((209, 280), (216, 287), (220, 295)),
                   ((221, 300), (221, 304), (218, 308)),
                   ((215, 298), (212, 292), (207, 288)),
                   ((204, 284), (201, 280), (200, 277))], '#ecb329', '#42311a', .8)
stroke((203, 279), [((211, 285), (216, 293), (218, 299))], '#ffda4a', .8)
shape((155, 257), [((165, 253), (179, 258), (190, 265)),
                   ((190, 272), (178, 280), (166, 285)),
                   ((157, 284), (150, 279), (147, 272)),
                   ((147, 265), (149, 260), (155, 257))], '#a82025')
shape((156, 260), [((164, 258), (175, 261), (183, 266)),
                   ((174, 273), (163, 278), (154, 277)),
                   ((151, 271), (152, 264), (156, 260))], '#e63e2e', None)
stroke((153, 262), [((162, 260), (173, 265), (180, 267))], '#fb6040', .8)
stroke((154, 282), [((166, 278), (176, 270), (183, 263))], '#171b22', 2.3)
shape((191, 267), [((213, 275), (240, 280), (265, 274)),
                   ((267, 277), (265, 281), (263, 283)),
                   ((237, 289), (207, 282), (188, 275)),
                   ((188, 272), (189, 269), (191, 267))], '#f1b62b', '#342d20', .9)
stroke((193, 269), [((217, 277), (242, 281), (263, 276))], '#ffe16b', .8)
shape((230, 278), [((233, 278), (237, 279), (240, 279)),
                   ((241, 283), (241, 286), (239, 287)),
                   ((236, 287), (232, 286), (230, 285)),
                   ((229, 282), (229, 280), (230, 278))], '#b8c1c7', '#202a34', .8)
stroke((233, 280), [((234, 281), (236, 282), (237, 282))], '#eff1ed', .6)

# Released far arm begins at the original sleeve; this is skin rather than
# the earlier oversized grey jacket panel under the lifted weapon.
shape((209, 208), [((214, 207), (219, 211), (220, 217)),
                   ((217, 224), (208, 231), (202, 239)),
                   ((204, 245), (214, 249), (222, 251)),
                   ((225, 254), (223, 261), (218, 263)),
                   ((202, 260), (189, 250), (188, 241)),
                   ((189, 230), (199, 214), (209, 208))], '#edb48b')
shape((192, 234), [((190, 243), (200, 254), (216, 258)),
                   ((220, 260), (219, 263), (216, 263)),
                   ((201, 260), (189, 251), (189, 241)),
                   ((189, 238), (190, 236), (192, 234))], '#bd8061', None)
stroke((204, 220), [((198, 229), (195, 236), (198, 240))], '#ffd4a8', 1.3)
shape((219, 248), [((225, 246), (231, 250), (234, 256)),
                   ((237, 262), (233, 269), (227, 270)),
                   ((220, 270), (213, 266), (213, 260)),
                   ((213, 255), (215, 251), (219, 248))], '#222e39')
shape((220, 251), [((225, 249), (231, 253), (232, 257)),
                   ((227, 260), (223, 261), (217, 258)),
                   ((216, 255), (218, 252), (220, 251))], '#434f5b', None)
stroke((216, 251), [((213, 257), (216, 264), (220, 266))], '#d9b143', 1.4)
for x, y in [(228, 264), (232, 261), (233, 258)]:
    ellipse((x-1.5, y-1.9, x+1.5, y+1.9), '#eeb48a', '#805940', .6)

# Near upper arm still emerges from its source sleeve. The elbow drops and
# the forearm folds up toward the lifting grip, with a supported wrist.
shape((319, 236), [((324, 237), (329, 247), (332, 256)),
                   ((336, 265), (332, 275), (325, 276)),
                   ((313, 276), (300, 268), (287, 258)),
                   ((284, 252), (288, 245), (294, 243)),
                   ((303, 248), (313, 258), (320, 260)),
                   ((316, 253), (311, 246), (309, 242)),
                   ((311, 238), (315, 236), (319, 236))], '#eab18a')
shape((328, 253), [((333, 261), (332, 270), (326, 271)),
                   ((312, 270), (299, 259), (291, 252)),
                   ((289, 255), (293, 261), (299, 265)),
                   ((313, 276), (329, 281), (334, 268)),
                   ((335, 262), (332, 257), (328, 253))], '#bd8061', None)
stroke((318, 240), [((323, 245), (325, 252), (326, 255))], '#ffd3a6', 1.2)
stroke((298, 249), [((305, 255), (312, 260), (316, 262))], '#ffd1a4', 1)

repair = art.finish()
body = Image.alpha_composite(body, repair)
# Source leg art restores every visible detail below the old guard. Remove
# only the chain and charm from the negative space between the thighs.
lower = original.crop((0, 305, 512, 512))
ImageDraw.Draw(lower).polygon([(227, 0), (249, 0), (257, 19), (258, 44),
                              (247, 50), (219, 46), (216, 21), (225, 6)], fill=(0, 0, 0, 0))
body.paste(lower, (0, 305))
hand, angle, yaw = (306, 233), 214, 12
weapon, front, grip, chain, H, anchors = carry(READY/'run_loop/layers/art_pass_05', hand, angle, yaw)
# During the lift the weapon is still in front of the torso, before settling
# behind the head in frames 03 and 04.
result = body
for layer in [weapon, grip, chain]:
    result = Image.alpha_composite(result, layer)
for im, name in [(body, 'body_plate'), (repair, 'local_repair'), (weapon, 'weapon'),
                 (grip, 'grip'), (chain, 'chain')]:
    save_clean(im, OUT/f'frame_02_{name}.png')
save_clean(result, OUT/'sora_run_start_02.png')
removal.save(OUT/'frame_02_removal_mask.png')
comparison = Image.new('RGB', (1024, 550), '#202633')
for i, (im, title) in enumerate([(original, 'Original lift source'),
                                (result, 'Lift: local hem, articulated arms and open crotch gap')]):
    comparison.paste(im, (i*512, 32), im)
    ImageDraw.Draw(comparison).text((i*512+12, 10), title, fill='white')
comparison.save(OUT/'Frame_02_Comparison.png')
assert np.array_equal(np.array(body)[360:], np.array(original)[360:])
assert body.getpixel((241, 337))[3] == 0
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
(OUT/'frame_02_manifest.json').write_text(json.dumps({
    'status': 'individual lift detail refinement; art review', 'source_crop': [889, 0, 1333, 450],
    'source_sha256': EXPECTED, 'hand_anchor': hand, 'screen_angle_degrees': angle,
    'foreground_yaw_degrees': yaw, 'physical_master_length_px': 285, 'master_scale': 1,
    'master_to_screen_homography': H.tolist(), 'projected_anchors': anchors,
    'occlusion': 'lifting weapon in front; settles behind head in subsequent frames',
    'limitations': ['Arms and inferred garment seams remain art-review work.',
                    'No root-motion/timing approval or Godot test.']}, indent=2), encoding='utf-8')
(OUT/'README.md').write_text(
    '# Lift detail revision\n\nFrame 02 replaces the oversized grey garment repair in v3. '
    'The released arm is drawn from its source sleeve, the near elbow supports the lifting '
    'wrist, and the chain cleanup leaves the real gap between the legs open. Source head, '
    'upper jacket and lower legs remain. Weapon scale, grip anchor and projection are '
    'unchanged. This is still an art review, not final idle-quality approval.\n', encoding='utf-8')
print('Saved lift detail revision:', OUT)
