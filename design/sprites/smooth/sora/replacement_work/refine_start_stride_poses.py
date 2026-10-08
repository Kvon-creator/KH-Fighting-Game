"""Pose-specific local art for the last three genuine run-start drawings."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, carry, save_clean, retain_main_body


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
OUT = READY/'run_start/refinement_v4'
SOURCE = READY/'run_start/run_start_source.png'
EXPECTED = '1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'


def finish_clothing_materials(layer, origin):
    """Charcoal clothing and gentle local lighting; no geometry changes."""
    pixels = np.array(layer)
    rgb = pixels[:, :, :3].astype(float)
    gray = ((pixels[:, :, 3] > 0) & (rgb[:, :, 0] < 125)
            & ((rgb.max(axis=2)-rgb.min(axis=2)) < 45))
    lum = .2126*rgb[:, :, 0]+.7152*rgb[:, :, 1]+.0722*rgb[:, :, 2]
    yy, xx = np.indices(lum.shape)
    gain = np.clip(1.045-.0009*(yy-origin[1])-.0006*(xx-origin[0])
                   +.025*np.exp(-((xx-origin[0])/45)**2), .88, 1.08)
    neutral = np.stack([lum*.96, lum*.985, lum*1.025], axis=2)*gain[:, :, None]
    pixels[:, :, :3][gray] = np.clip(neutral[gray], 0, 255).astype('uint8')
    return Image.fromarray(pixels, 'RGBA')


def free_glove(art, x, y):
    """Reusable glove material around a pose-specific released wrist."""
    shape, stroke, ellipse = art.shape, art.stroke, art.ellipse
    shape((x-7, y-8), [((x-1, y-11), (x+6, y-7), (x+9, y-2)),
                       ((x+12, y+4), (x+7, y+10), (x+1, y+11)),
                       ((x-6, y+10), (x-12, y+5), (x-11, y)),
                       ((x-11, y-4), (x-10, y-7), (x-7, y-8))], '#222c37')
    shape((x-6, y-5), [((x-1, y-7), (x+5, y-3), (x+6, y)),
                       ((x+2, y+3), (x-4, y+3), (x-8, y)),
                       ((x-8, y-2), (x-7, y-4), (x-6, y-5))], '#45515d', None)
    stroke((x-9, y-6), [((x-12, y), (x-9, y+6), (x-5, y+8))], '#d8b149', 1.4)
    for dx, dy in [(3, 5), (7, 2), (9, -1)]:
        ellipse((x+dx-1.6, y+dy-2, x+dx+1.6, y+dy+2), '#eeb58b', '#805940', .6)


def draw_05():
    cloth, far, near = Art(), Art(), Art()
    shape, stroke = cloth.shape, cloth.stroke
    # Left jacket volume hidden by the old two-handed grip. Leave the narrow
    # space inside the bent far elbow open, but reconnect the real torso.
    shape((261, 150), [((271, 150), (280, 155), (285, 168)),
                       ((284, 181), (274, 196), (262, 206)),
                       ((250, 210), (236, 205), (229, 196)),
                       ((232, 179), (246, 155), (261, 150))], '#282e36')
    shape((256, 156), [((265, 152), (275, 157), (277, 166)),
                       ((268, 180), (251, 188), (240, 187)),
                       ((242, 175), (250, 161), (256, 156))], '#424952', None)
    shape((270, 173), [((276, 178), (272, 191), (261, 200)),
                       ((251, 204), (240, 201), (235, 196)),
                       ((250, 194), (264, 184), (270, 173))], '#181f28', None)
    stroke((279, 164), [((270, 179), (258, 194), (248, 200)),
                        ((241, 197), (238, 192), (237, 187))], '#dce4e9', 1.8)
    stroke((274, 169), [((268, 180), (254, 193), (249, 196))], '#74818f', .7)
    stroke((254, 183), [((252, 188), (251, 191), (249, 192))], '#eeb633', 1.7)
    # Jacket hem hidden by the original straight forearm, inside the torso.
    shape((270, 177), [((292, 174), (316, 176), (339, 180)),
                       ((343, 191), (335, 205), (321, 212)),
                       ((303, 219), (280, 217), (261, 207)),
                       ((260, 195), (263, 184), (270, 177))], '#252b33', None)
    shape((270, 181), [((283, 177), (295, 181), (304, 184)),
                       ((295, 193), (279, 198), (265, 197)),
                       ((263, 190), (266, 184), (270, 181))], '#3d434c', None)
    shape((322, 185), [((330, 188), (332, 197), (324, 204)),
                       ((313, 213), (295, 213), (285, 209)),
                       ((301, 204), (315, 195), (322, 185))], '#171e28', None)
    shape((286, 198), [((298, 201), (306, 201), (317, 197)),
                       ((313, 207), (302, 212), (293, 210)),
                       ((289, 206), (287, 202), (286, 198))], '#ab2027')
    stroke((292, 203), [((301, 208), (308, 205), (313, 202))], '#ed4432', 1.2)
    stroke((338, 181), [((333, 194), (326, 206), (320, 211)),
                        ((304, 219), (283, 216), (271, 211))], '#dae3e8', 1.9)
    stroke((333, 187), [((330, 195), (324, 203), (319, 207))], '#76838f', .7)
    stroke((268, 202), [((272, 205), (277, 207), (280, 207))], '#65707a', .8)
    for x, y in [(330, 187), (325, 197), (319, 206)]:
        cloth.ellipse((x-1.7, y-1.7, x+1.7, y+1.7), '#8d9aa6', '#141d27', .6)
        cloth.ellipse((x-.9, y-1.3, x+.5, y), '#dce5eb')
    # Hip/left shorts volume occluded by the original guard; blend into real
    # source thighs below it instead of introducing a rectangle or a cape.
    shape((207, 213), [((229, 207), (252, 211), (271, 220)),
                       ((273, 233), (259, 247), (244, 258)),
                       ((225, 264), (204, 251), (194, 235)),
                       ((192, 225), (198, 218), (207, 213))], '#252a30', None)
    shape((211, 218), [((227, 214), (240, 221), (245, 232)),
                       ((241, 242), (229, 250), (218, 250)),
                       ((207, 238), (203, 225), (211, 218))], '#2c3239', None)
    shape((250, 222), [((260, 220), (267, 226), (265, 233)),
                       ((257, 245), (244, 255), (235, 256)),
                       ((240, 245), (246, 232), (250, 222))], '#171e27', None)
    # Red side flap and fixed yellow waist/leg straps, in the KH2 palette.
    shape((183, 204), [((195, 200), (215, 204), (229, 214)),
                       ((224, 222), (206, 231), (188, 234)),
                       ((178, 232), (172, 227), (173, 220)),
                       ((174, 213), (177, 208), (183, 204))], '#a51e25')
    shape((184, 208), [((196, 205), (211, 210), (221, 215)),
                       ((209, 222), (192, 227), (179, 226)),
                       ((178, 220), (180, 213), (184, 208))], '#e74030', None)
    stroke((178, 230), [((193, 225), (207, 216), (217, 207))], '#171b22', 2)
    shape((219, 207), [((237, 214), (266, 218), (294, 210)),
                       ((297, 213), (296, 217), (293, 219)),
                       ((268, 226), (240, 223), (216, 215)),
                       ((215, 212), (216, 209), (219, 207))], '#efb52b', '#352d20', .9)
    stroke((220, 209), [((244, 218), (267, 220), (292, 212))], '#ffdf67', .8)
    shape((232, 220), [((241, 224), (249, 231), (251, 240)),
                       ((249, 247), (246, 252), (242, 255)),
                       ((242, 242), (238, 234), (231, 230)),
                       ((230, 226), (231, 223), (232, 220))], '#edb52b', '#49351b', .8)
    stroke((234, 223), [((242, 230), (246, 240), (245, 247))], '#ffd84b', .8)
    # Distinct far elbow folds behind the waist during the push.
    shape, stroke = far.shape, far.stroke
    shape((241, 138), [((247, 141), (249, 147), (247, 153)),
                       ((234, 160), (219, 167), (207, 174)),
                       ((205, 179), (210, 185), (214, 188)),
                       ((215, 193), (210, 197), (205, 195)),
                       ((193, 188), (188, 178), (192, 171)),
                       ((204, 156), (225, 141), (241, 138))], '#eeb58c')
    shape((195, 169), [((191, 177), (198, 188), (207, 192)),
                       ((210, 194), (209, 196), (205, 195)),
                       ((194, 189), (189, 179), (192, 172)),
                       ((192, 171), (193, 170), (195, 169))], '#bc8062', None)
    stroke((237, 143), [((220, 150), (207, 160), (201, 166))], '#ffd6a9', 1.3)
    free_glove(far, 210, 193)
    # Near sleeve grows from this source shoulder, not a translated body plate.
    shape, stroke, ellipse = near.shape, near.stroke, near.ellipse
    shape((350, 148), [((361, 148), (372, 157), (377, 167)),
                       ((380, 177), (375, 190), (365, 194)),
                       ((355, 192), (345, 183), (343, 172)),
                       ((341, 162), (344, 153), (350, 148))], '#2b323b')
    shape((354, 153), [((363, 153), (373, 162), (373, 170)),
                       ((371, 179), (364, 185), (357, 181)),
                       ((349, 174), (347, 159), (354, 153))], '#49515b', None)
    shape((361, 159), [((367, 159), (372, 168), (369, 172)),
                       ((364, 177), (357, 172), (355, 166)),
                       ((354, 161), (358, 158), (361, 159))], '#343e49', '#7c8893', .8)
    ellipse((360, 161, 363, 164), '#b6c1c9', '#222b35', .5)
    ellipse((366, 169, 369, 172), '#a6b3bd', '#222b35', .5)
    shape((349, 180), [((356, 186), (368, 189), (375, 180)),
                       ((375, 187), (370, 194), (364, 197)),
                       ((357, 196), (352, 188), (349, 180))], '#e2e7ea')
    stroke((353, 185), [((360, 192), (368, 191), (373, 186))], '#85939f', 1)
    shape((365, 192), [((371, 195), (371, 213), (378, 218)),
                       ((384, 220), (391, 215), (396, 213)),
                       ((401, 212), (404, 218), (400, 222)),
                       ((392, 229), (380, 233), (372, 229)),
                       ((362, 222), (358, 207), (359, 197)),
                       ((360, 193), (362, 191), (365, 192))], '#ecb28b')
    shape((360, 201), [((362, 212), (366, 224), (374, 229)),
                       ((382, 234), (395, 226), (400, 221)),
                       ((393, 225), (385, 227), (379, 224)),
                       ((371, 220), (369, 207), (368, 199)),
                       ((366, 198), (362, 198), (360, 201))], '#bd8061', None)
    stroke((368, 196), [((370, 203), (371, 212), (374, 216))], '#ffd3a6', 1.3)
    stroke((383, 219), [((387, 219), (391, 217), (395, 215))], '#ffd2a4', 1)
    return cloth.finish(), far.finish(), near.finish()


def draw_06():
    cloth, far, near = Art(), Art(), Art()
    shape, stroke = cloth.shape, cloth.stroke
    # Side lapel and hem follow this tighter torso, independently of frame05.
    shape((237, 148), [((247, 148), (260, 153), (267, 166)),
                       ((266, 180), (252, 194), (239, 199)),
                       ((226, 200), (210, 193), (203, 184)),
                       ((211, 170), (226, 152), (237, 148))], '#282e36')
    shape((233, 155), [((243, 151), (254, 157), (257, 165)),
                       ((245, 178), (226, 182), (217, 178)),
                       ((221, 168), (228, 159), (233, 155))], '#424951', None)
    shape((252, 171), [((259, 177), (250, 189), (240, 194)),
                       ((227, 195), (216, 189), (210, 184)),
                       ((225, 186), (242, 180), (252, 171))], '#18202a', None)
    stroke((261, 163), [((252, 178), (237, 190), (227, 192)),
                        ((219, 189), (215, 184), (211, 179))], '#dce4e9', 1.8)
    stroke((254, 168), [((246, 178), (236, 187), (229, 189))], '#798795', .7)
    stroke((237, 180), [((235, 184), (232, 187), (229, 188))], '#efb735', 1.8)
    shape((233, 177), [((254, 173), (275, 173), (294, 176)),
                       ((296, 187), (285, 202), (270, 209)),
                       ((251, 215), (231, 209), (215, 200)),
                       ((218, 189), (224, 182), (233, 177))], '#262d36', None)
    shape((234, 182), [((246, 177), (262, 181), (269, 184)),
                       ((259, 193), (239, 197), (223, 194)),
                       ((225, 188), (230, 184), (234, 182))], '#3d4650', None)
    shape((274, 182), [((283, 185), (286, 193), (276, 202)),
                       ((263, 211), (246, 208), (238, 205)),
                       ((253, 201), (267, 191), (274, 182))], '#171f29', None)
    shape((242, 199), [((253, 201), (263, 201), (271, 195)),
                       ((268, 205), (258, 209), (248, 207)),
                       ((245, 204), (243, 201), (242, 199))], '#ac2027')
    stroke((247, 202), [((254, 207), (262, 203), (267, 200))], '#ed4432', 1.1)
    stroke((293, 179), [((287, 192), (278, 204), (268, 209)),
                        ((253, 214), (235, 209), (224, 205))], '#dce5e9', 1.8)
    stroke((287, 185), [((283, 194), (275, 203), (268, 205))], '#7a8897', .7)
    for x, y in [(284, 186), (278, 196), (270, 204)]:
        cloth.ellipse((x-1.7, y-1.7, x+1.7, y+1.7), '#8d9aa6', '#141d27', .6)
        cloth.ellipse((x-.9, y-1.3, x+.5, y), '#dce5eb')
    # Small hip material, with curved red flap and original legs retained.
    shape((179, 202), [((193, 196), (215, 200), (237, 210)),
                       ((247, 221), (232, 234), (219, 239)),
                       ((204, 241), (183, 233), (173, 220)),
                       ((171, 213), (174, 206), (179, 202))], '#252b32', None)
    shape((186, 206), [((200, 202), (214, 209), (218, 221)),
                       ((212, 229), (198, 232), (188, 228)),
                       ((181, 221), (180, 212), (186, 206))], '#303842', None)
    shape((222, 210), [((232, 210), (240, 216), (238, 222)),
                       ((232, 231), (222, 236), (212, 235)),
                       ((215, 226), (219, 218), (222, 210))], '#171e28', None)
    shape((164, 198), [((177, 193), (196, 200), (211, 208)),
                       ((205, 217), (186, 228), (167, 232)),
                       ((160, 231), (155, 225), (155, 219)),
                       ((156, 210), (159, 202), (164, 198))], '#a51e25')
    shape((165, 202), [((177, 198), (191, 203), (202, 209)),
                       ((188, 216), (173, 224), (160, 223)),
                       ((160, 216), (162, 207), (165, 202))], '#e63e30', None)
    stroke((159, 229), [((173, 222), (186, 211), (197, 201))], '#171b22', 2)
    shape((185, 198), [((204, 206), (228, 212), (250, 204)),
                       ((253, 207), (251, 212), (248, 214)),
                       ((227, 220), (201, 215), (182, 206)),
                       ((182, 203), (183, 200), (185, 198))], '#efb52b', '#352d20', .9)
    stroke((186, 201), [((207, 210), (230, 214), (248, 207))], '#ffdf67', .8)
    # Far elbow swings inward as the feet pass underneath the body.
    shape, stroke = far.shape, far.stroke
    shape((212, 133), [((218, 133), (222, 141), (219, 147)),
                       ((205, 153), (189, 162), (178, 169)),
                       ((179, 174), (185, 176), (192, 178)),
                       ((196, 181), (193, 188), (189, 188)),
                       ((176, 187), (163, 178), (164, 169)),
                       ((174, 155), (197, 138), (212, 133))], '#eeb48c')
    shape((169, 165), [((166, 171), (174, 181), (188, 184)),
                       ((193, 186), (192, 189), (188, 188)),
                       ((176, 187), (164, 179), (165, 170)),
                       ((165, 169), (167, 167), (169, 165))], '#bd8061', None)
    stroke((207, 138), [((191, 146), (177, 156), (172, 163))], '#ffd4a7', 1.3)
    free_glove(far, 193, 185)
    # Near upper arm and forearm use a new elbow, not frame05's artwork.
    shape, stroke, ellipse = near.shape, near.stroke, near.ellipse
    shape((300, 137), [((311, 137), (322, 146), (326, 157)),
                       ((328, 168), (323, 179), (313, 181)),
                       ((303, 177), (296, 167), (294, 155)),
                       ((292, 146), (295, 140), (300, 137))], '#2c333d')
    shape((303, 142), [((312, 142), (321, 151), (322, 160)),
                       ((319, 168), (312, 173), (305, 168)),
                       ((299, 161), (297, 147), (303, 142))], '#49525d', None)
    shape((310, 148), [((316, 148), (322, 157), (318, 161)),
                       ((313, 166), (307, 161), (305, 155)),
                       ((304, 150), (308, 147), (310, 148))], '#36404b', '#7e8b96', .8)
    ellipse((308, 150, 311, 153), '#b6c1c9', '#222b35', .5)
    ellipse((315, 159, 318, 162), '#a6b3bd', '#222b35', .5)
    shape((299, 166), [((305, 173), (317, 176), (324, 167)),
                       ((324, 175), (318, 181), (312, 184)),
                       ((306, 182), (301, 174), (299, 166))], '#e2e8eb')
    stroke((302, 172), [((309, 179), (317, 178), (322, 173))], '#8897a4', 1)
    shape((312, 180), [((318, 184), (320, 202), (325, 206)),
                       ((329, 206), (335, 197), (339, 192)),
                       ((343, 190), (348, 194), (346, 199)),
                       ((340, 209), (332, 220), (322, 218)),
                       ((310, 214), (306, 196), (306, 185)),
                       ((307, 181), (310, 179), (312, 180))], '#edb38c')
    shape((307, 190), [((309, 202), (313, 214), (323, 218)),
                       ((334, 221), (342, 207), (345, 200)),
                       ((340, 206), (334, 213), (328, 212)),
                       ((319, 209), (316, 195), (315, 187)),
                       ((312, 186), (309, 187), (307, 190))], '#bd8061', None)
    stroke((316, 184), [((318, 192), (320, 199), (322, 203))], '#ffd4a7', 1.3)
    stroke((330, 203), [((334, 199), (336, 196), (339, 194))], '#ffd2a5', 1)
    return cloth.finish(), far.finish(), near.finish()


def draw_07():
    cloth, far, near = Art(), Art(), Art()
    shape, stroke = cloth.shape, cloth.stroke
    # Most source jacket is unobscured in this pose and remains untouched.
    # Only repair the scarf/waist material hidden by the original rear grip.
    shape((194, 208), [((213, 205), (235, 207), (252, 214)),
                       ((250, 221), (240, 226), (227, 228)),
                       ((214, 227), (199, 221), (194, 216)),
                       ((193, 213), (193, 210), (194, 208))], '#252c35')
    shape((218, 213), [((228, 210), (238, 213), (244, 216)),
                       ((237, 223), (226, 225), (219, 223)),
                       ((216, 220), (215, 216), (218, 213))], '#39424d', None)
    shape((184, 189), [((195, 184), (215, 188), (236, 199)),
                       ((231, 209), (210, 216), (192, 217)),
                       ((181, 216), (173, 210), (172, 205)),
                       ((174, 198), (179, 192), (184, 189))], '#a32027')
    shape((186, 194), [((198, 190), (214, 195), (228, 200)),
                       ((217, 207), (197, 213), (181, 211)),
                       ((178, 205), (181, 198), (186, 194))], '#e83d30', None)
    stroke((178, 214), [((194, 209), (211, 198), (220, 190))], '#161b23', 2)
    stroke((183, 196), [((193, 192), (208, 196), (219, 199))], '#fc6040', .8)
    shape((230, 193), [((242, 190), (254, 194), (264, 201)),
                       ((257, 207), (245, 211), (234, 212)),
                       ((229, 207), (227, 198), (230, 193))], '#a31f27')
    shape((235, 196), [((244, 193), (251, 198), (257, 201)),
                       ((249, 205), (239, 208), (233, 206)),
                       ((232, 203), (233, 199), (235, 196))], '#df352b', None)
    stroke((234, 196), [((239, 200), (245, 204), (248, 206))], '#141a22', 1.7)
    shape((211, 204), [((224, 205), (239, 211), (253, 212)),
                       ((254, 215), (252, 219), (249, 221)),
                       ((235, 219), (221, 214), (208, 211)),
                       ((208, 208), (209, 205), (211, 204))], '#efb62b', '#352d20', .9)
    stroke((213, 206), [((225, 208), (241, 214), (250, 214))], '#ffdf67', .8)
    # Source rear upper arm reconnects to a released fist beside the hip.
    shape, stroke = far.shape, far.stroke
    shape((241, 150), [((247, 152), (249, 158), (246, 164)),
                       ((234, 172), (222, 177), (214, 180)),
                       ((214, 183), (220, 186), (223, 189)),
                       ((225, 193), (220, 198), (216, 196)),
                       ((206, 191), (199, 184), (201, 178)),
                       ((209, 167), (229, 154), (241, 150))], '#edb48c')
    shape((204, 174), [((201, 180), (208, 189), (217, 193)),
                       ((222, 195), (219, 198), (216, 196)),
                       ((205, 191), (200, 184), (202, 178)),
                       ((202, 177), (203, 175), (204, 174))], '#bd8061', None)
    stroke((237, 155), [((225, 160), (214, 168), (209, 174))], '#ffd4a7', 1.3)
    free_glove(far, 220, 194)
    # Holding shoulder follows the fully extended stride's original lean.
    shape, stroke, ellipse = near.shape, near.stroke, near.ellipse
    shape((343, 150), [((355, 149), (366, 158), (371, 169)),
                       ((374, 179), (367, 188), (357, 191)),
                       ((347, 187), (338, 176), (337, 165)),
                       ((336, 157), (338, 153), (343, 150))], '#2c333c')
    shape((347, 155), [((356, 154), (366, 163), (367, 171)),
                       ((364, 179), (357, 184), (350, 178)),
                       ((343, 171), (341, 159), (347, 155))], '#48515c', None)
    shape((354, 161), [((360, 159), (366, 167), (364, 171)),
                       ((359, 177), (353, 173), (349, 167)),
                       ((348, 163), (351, 161), (354, 161))], '#35404a', '#7e8a95', .8)
    ellipse((353, 162, 356, 165), '#b6c1c9', '#222b35', .5)
    ellipse((359, 170, 362, 173), '#a6b3bd', '#222b35', .5)
    shape((342, 177), [((349, 184), (360, 187), (368, 178)),
                       ((368, 185), (363, 192), (357, 194)),
                       ((350, 192), (345, 183), (342, 177))], '#e2e8eb')
    stroke((346, 182), [((353, 190), (361, 188), (366, 183))], '#8897a4', 1)
    shape((357, 190), [((363, 192), (363, 206), (370, 211)),
                       ((376, 213), (384, 203), (390, 198)),
                       ((394, 196), (399, 200), (395, 205)),
                       ((386, 216), (376, 226), (366, 222)),
                       ((355, 217), (350, 202), (351, 194)),
                       ((352, 191), (354, 189), (357, 190))], '#ecb38b')
    shape((352, 198), [((354, 208), (359, 219), (368, 223)),
                       ((379, 227), (391, 211), (394, 206)),
                       ((387, 211), (381, 219), (374, 217)),
                       ((365, 213), (362, 204), (360, 196)),
                       ((357, 194), (354, 195), (352, 198))], '#bd8061', None)
    stroke((361, 194), [((363, 200), (364, 206), (367, 209))], '#ffd4a7', 1.3)
    stroke((379, 207), [((383, 203), (386, 201), (389, 200))], '#ffd2a5', 1)
    return cloth.finish(), far.finish(), near.finish()


POSES = {
    5: {'crop': (445, 450, 889, 887), 'hand': (408, 201), 'angle': 219, 'yaw': 24,
        'shoulder': (365, 165), 'preserve_below': 280, 'lighting_origin': (275, 177), 'draw': draw_05,
        'masks': [
            [(37, 96), (125, 93), (132, 132), (228, 157), (225, 181), (37, 152)],
            [(194, 149), (244, 144), (294, 177), (301, 218), (274, 250), (248, 255), (195, 215)],
            [(177, 157), (220, 139), (243, 141), (247, 162), (210, 180), (197, 204), (170, 196)],
            [(268, 172), (343, 169), (360, 182), (354, 202), (270, 204), (258, 189)],
            [(78, 176), (158, 151), (203, 147), (211, 173), (163, 189), (143, 218), (100, 224), (78, 207)]]},
    6: {'crop': (889, 450, 1333, 887), 'hand': (350, 183), 'angle': 217, 'yaw': 26,
        'shoulder': (309, 147), 'preserve_below': 258, 'lighting_origin': (248, 180), 'draw': draw_06,
        'masks': [
            [(0, 128), (66, 128), (74, 153), (189, 158), (188, 184), (0, 184)],
            [(129, 156), (178, 147), (204, 144), (226, 132), (230, 145), (211, 159), (203, 189), (155, 196), (124, 183)],
            [(177, 145), (193, 129), (208, 126), (218, 130), (215, 146), (177, 161)],
            [(169, 148), (188, 126), (207, 120), (213, 128), (205, 140), (183, 157), (169, 156)],
            [(171, 161), (211, 158), (256, 180), (263, 204), (240, 229), (216, 229), (175, 209), (169, 186)],
            [(225, 175), (297, 171), (309, 184), (301, 205), (233, 209), (218, 194)],
            [(63, 219), (120, 189), (152, 179), (168, 191), (126, 214), (114, 245), (78, 254), (61, 237)]]},
    7: {'crop': (1306, 450, 1774, 887), 'hand': (402, 186), 'angle': 218, 'yaw': 26,
        'shoulder': (358, 155), 'preserve_below': 230, 'lighting_origin': (245, 210), 'draw': draw_07,
        'masks': [
            [(35, 111), (139, 110), (147, 151), (205, 171), (199, 197), (33, 156)],
            [(164, 180), (204, 172), (232, 187), (247, 206), (228, 223), (174, 216)],
            [(194, 158), (228, 160), (244, 170), (234, 184), (211, 196), (192, 185)],
            [(205, 159), (222, 152), (240, 146), (246, 151), (244, 165), (220, 185), (203, 185)]]},
}


def render(index):
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    data = POSES[index]
    OUT.mkdir(parents=True, exist_ok=True)
    original = Image.new('RGBA', (512, 512))
    original.paste(Image.open(SOURCE).convert('RGBA').crop(data['crop']), (0, 0))
    removal = Image.new('L', original.size)
    md = ImageDraw.Draw(removal)
    for points in data['masks']:
        md.polygon(points, fill=255)
    if index == 6:
        # The neighboring final pose's shoe spills into the right cell margin.
        md.rectangle((412, 210, 511, 511), fill=255)
    body = original.copy()
    body.putalpha(Image.composite(Image.new('L', original.size), original.getchannel('A'), removal))
    cloth, far, near = data['draw']()
    cloth = finish_clothing_materials(cloth, data['lighting_origin'])
    for layer in [cloth, far, near]:
        body = Image.alpha_composite(body, layer)
    y = data['preserve_below']
    keep_width = 412 if index == 6 else 512
    # Preserve the source legs exactly, including their boundary antialiasing.
    body.paste(original.crop((0, y, keep_width, 512)), (0, y))
    body, removed = retain_main_body(body)
    assert all(region['area_px'] < 250 for region in removed), removed
    weapon, front, grip, chain, H, anchors = carry(READY/'run_loop/layers/art_pass_05',
                                                  data['hand'], data['angle'], data['yaw'])
    result = Image.alpha_composite(weapon, body)
    for layer in [front, grip, chain]:
        result = Image.alpha_composite(result, layer)
    for im, name in [(body, 'body_plate'), (cloth, 'clothing_repair'), (far, 'released_arm'),
                     (near, 'carrying_arm'), (weapon, 'weapon'), (front, 'weapon_foreground'),
                     (grip, 'grip'), (chain, 'chain')]:
        save_clean(im, OUT/f'frame_{index:02d}_{name}.png')
    save_clean(result, OUT/f'sora_run_start_{index:02d}.png')
    removal.save(OUT/f'frame_{index:02d}_removal_mask.png')
    # The actual head and feet are retained, with no static body scaling.
    before, after = np.array(original)[y:, :keep_width], np.array(body)[y:, :keep_width]
    visible = before[:, :, 3] > 32
    assert np.array_equal(before[visible], after[visible])
    assert np.linalg.norm(np.array(anchors['collar'])-data['shoulder']) < 14
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    comparison = Image.new('RGB', (1024, 550), '#202633')
    for i, (im, title) in enumerate([(original, f'Original stride {index:02d}'),
                                    (result, 'Individual arm / shoulder carry refinement')]):
        comparison.paste(im, (i*512, 32), im)
        ImageDraw.Draw(comparison).text((i*512+12, 10), title, fill='white')
    comparison.save(OUT/f'Frame_{index:02d}_Comparison.png')
    (OUT/f'frame_{index:02d}_manifest.json').write_text(json.dumps({
        'status': 'individual stride refinement; art review', 'source_crop': data['crop'],
        'source_sha256': EXPECTED, 'hand_anchor': data['hand'], 'holding_shoulder_anchor': data['shoulder'],
        'screen_angle_degrees': data['angle'], 'foreground_yaw_degrees': data['yaw'],
        'physical_master_length_px': 285, 'master_scale': 1,
        'master_to_screen_homography': H.tolist(), 'projected_anchors': anchors,
        'material_pass': 'local charcoal lighting and trim; source body and weapon untouched',
        'removed_detached_fragments': removed,
        'occlusion': 'shaft behind head/body; connected guard and approved grip in front',
        'limitations': ['Inferred garment/arm materials still need idle-quality comparison.',
                        'Root registration, timing and transition seam remain under review.',
                        'No aerial production or Godot changes/testing.']}, indent=2), encoding='utf-8')
    print('Saved individual stride:', index, OUT, 'detached fragments:', removed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=int, choices=sorted(POSES), required=True)
    render(parser.parse_args().frame)
