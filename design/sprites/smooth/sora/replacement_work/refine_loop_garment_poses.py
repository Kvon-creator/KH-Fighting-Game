"""Individual loop03/04 garment and arm drawing, with unchanged rigid carry.

Offline art helper. Does not run Godot or alter any prior sheet/review.
"""
from pathlib import Path
import argparse
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
parser = argparse.ArgumentParser()
parser.add_argument('--frame', type=int, choices=(3, 4))
args = parser.parse_args()


def buttons(a, points):
    for x, y in points:
        a.ellipse((x-1.5, y-1.5, x+1.5, y+1.5), '#87939f', '#141d26', .6)
        a.ellipse((x-.7, y-1, x+.7, y+.2), '#dce4e8')


def glove(a, x, y, lean):
    """Small relaxed far fist; never used for the approved carrying grip."""
    s, t = a.shape, a.stroke
    s((x-7, y-6), [((x-4, y-11), (x+3, y-10), (x+7, y-6)),
                    ((x+12, y-2), (x+10, y+5), (x+5, y+8)),
                    ((x-1, y+10), (x-8, y+6), (x-10, y+1)),
                    ((x-11, y-2), (x-9, y-4), (x-7, y-6))], '#222b34')
    s((x-6, y-5), [((x-3, y-8), (x+3, y-8), (x+6, y-4)),
                    ((x+5, y), (x, y+1), (x-6, y-1)),
                    ((x-7, y-2), (x-7, y-4), (x-6, y-5))], '#414b55', None)
    t((x-8, y-4), [((x-9, y), (x-5, y+5), (x-2, y+6))], '#ddb744', 1.3)
    t((x-5, y-6), [((x-1, y-8), (x+3, y-7), (x+5, y-5))], '#67727c', .7)
    for dx, dy in [(4, 4), (7, 1), (8, -2)]:
        a.ellipse((x+dx-1.4, y+dy-1.8, x+dx+1.4, y+dy+1.8), '#e8ae87', '#72503e', .5)


def loop03():
    a = Art()
    s, t = a.shape, a.stroke
    # The released arm extends back from the source's actual far shoulder.
    s((243, 147), [((232, 149), (222, 163), (219, 176)),
                    ((220, 185), (229, 191), (239, 190)),
                    ((248, 184), (257, 171), (256, 158)),
                    ((253, 151), (249, 147), (243, 147))], '#2b3037')
    s((240, 153), [((230, 156), (223, 168), (225, 177)),
                    ((227, 180), (232, 181), (237, 179)),
                    ((247, 171), (252, 158), (240, 153))], '#444a51', None)
    t((233, 157), [((228, 162), (226, 169), (226, 173))], '#697078', .7)
    s((221, 177), [((225, 184), (231, 187), (239, 185)),
                    ((237, 190), (232, 193), (227, 192)),
                    ((222, 190), (220, 184), (221, 177))], '#e0e5e7', '#192028', 1)
    t((222, 183), [((225, 189), (230, 191), (236, 187))], '#919ba4', .8)
    s((227, 190), [((223, 194), (216, 202), (211, 209)),
                    ((206, 215), (202, 221), (200, 227)),
                    ((198, 230), (191, 229), (190, 225)),
                    ((191, 217), (198, 207), (202, 201)),
                    ((208, 193), (216, 187), (220, 186)),
                    ((223, 186), (225, 187), (227, 190))], '#edb38c', '#3b2b26', 1.2)
    s((193, 222), [((197, 212), (205, 201), (211, 196)),
                    ((207, 204), (205, 212), (201, 220)),
                    ((199, 224), (197, 228), (195, 227)),
                    ((193, 227), (192, 225), (193, 222))], '#bd7d60', None)
    t((217, 194), [((211, 202), (205, 210), (202, 217))], '#ffd2a8', 1)
    glove(a, 194, 229, -1)

    # Hood and back flow into one chest, instead of a translated template pad.
    s((248, 128), [((257, 122), (272, 123), (282, 129)),
                    ((286, 138), (285, 155), (280, 166)),
                    ((270, 161), (251, 157), (238, 147)),
                    ((236, 139), (240, 132), (248, 128))], '#20252c')
    s((249, 130), [((258, 126), (273, 128), (278, 134)),
                    ((277, 137), (263, 135), (255, 138)),
                    ((248, 141), (244, 141), (242, 138)),
                    ((242, 134), (245, 132), (249, 130))], '#3d444c', None)
    t((245, 132), [((253, 127), (267, 129), (273, 131))], '#68727b', .7)
    s((258, 139), [((268, 139), (278, 146), (286, 158)),
                    ((300, 164), (318, 175), (329, 188)),
                    ((333, 204), (316, 223), (298, 234)),
                    ((281, 244), (254, 246), (232, 235)),
                    ((218, 228), (213, 217), (215, 207)),
                    ((219, 187), (232, 163), (245, 149)),
                    ((249, 142), (253, 139), (258, 139))], '#292e35')
    s((253, 147), [((261, 145), (269, 149), (273, 158)),
                    ((255, 170), (241, 190), (232, 214)),
                    ((226, 216), (221, 212), (222, 205)),
                    ((227, 183), (240, 158), (253, 147))], '#454b52', None)
    s((250, 166), [((254, 163), (260, 163), (261, 165)),
                    ((251, 181), (244, 199), (240, 218)),
                    ((236, 218), (233, 216), (235, 210)),
                    ((238, 193), (244, 178), (250, 166))], '#353b43', None)
    s((314, 192), [((318, 194), (322, 198), (321, 202)),
                    ((309, 222), (283, 236), (255, 239)),
                    ((250, 236), (247, 231), (246, 226)),
                    ((275, 229), (298, 212), (314, 192))], '#171d25', None)
    s((218, 207), [((222, 216), (228, 222), (237, 227)),
                    ((234, 231), (230, 232), (226, 229)),
                    ((218, 223), (215, 214), (218, 207))], '#1c222a', None)
    t((232, 205), [((228, 213), (231, 220), (238, 222))], '#697077', .8)
    t((225, 217), [((229, 222), (237, 226), (242, 226))], '#4f5963', .8)
    t((241, 233), [((245, 236), (255, 238), (264, 236))], '#414b56', .8)
    # Far epaulette is part of the sleeve's upper contour, not a round stamp.
    s((243, 145), [((250, 141), (258, 144), (262, 152)),
                    ((262, 160), (257, 163), (252, 160)),
                    ((245, 157), (239, 151), (243, 145))], '#39414a', '#7d8892', .8)
    t((244, 145), [((250, 142), (256, 146), (258, 149))], '#b5c0c8', .6)
    buttons(a, [(246, 146), (257, 156)])
    t((255, 167), [((256, 172), (253, 179), (250, 183))], '#d29e21', 2.7)
    t((254, 168), [((254, 173), (252, 177), (250, 179))], '#f5d052', .9)

    # V shirt and perspective lapels track neck-to-waist lean.
    s((286, 165), [((297, 166), (310, 171), (322, 180)),
                    ((311, 204), (289, 225), (265, 236)),
                    ((258, 233), (250, 226), (249, 219)),
                    ((262, 200), (276, 180), (286, 165))], '#121a23')
    s((286, 178), [((294, 182), (306, 180), (315, 177)),
                    ((305, 195), (286, 212), (273, 218)),
                    ((267, 216), (264, 213), (262, 208)),
                    ((270, 195), (279, 185), (286, 178))], '#333b45', None)
    t((288, 181), [((295, 187), (306, 183), (313, 179))], '#bec9d2', 1.6)
    t((278, 202), [((281, 204), (284, 208), (287, 204)),
                    ((290, 201), (294, 203), (296, 198))], '#aab8c4', 1.2)
    t((281, 191), [((281, 196), (279, 200), (278, 202))], '#b7c4cf', .6)
    s((270, 142), [((275, 141), (281, 146), (283, 151)),
                    ((275, 172), (260, 194), (248, 208)),
                    ((242, 207), (237, 203), (236, 200)),
                    ((246, 182), (261, 159), (270, 142))], '#303741')
    t((275, 143), [((278, 145), (282, 149), (283, 151)),
                    ((275, 172), (260, 194), (248, 208)),
                    ((244, 207), (239, 203), (236, 200))], '#dde4e8', 1.8)
    t((279, 153), [((271, 173), (257, 193), (247, 204))], '#8e9ca8', .7)
    t((322, 181), [((312, 204), (290, 224), (265, 235)),
                    ((256, 238), (244, 234), (238, 229))], '#dce3e7', 1.8)
    t((318, 186), [((306, 207), (286, 224), (264, 231))], '#697b8c', .7)
    buttons(a, [(308, 198), (297, 211), (284, 222)])
    # The short red hem connects to the source's streaming waist fabric.
    s((253, 224), [((259, 229), (266, 228), (275, 224)),
                    ((273, 231), (265, 236), (257, 237)),
                    ((249, 236), (242, 233), (237, 227)),
                    ((243, 230), (249, 229), (253, 224))], '#a21b24')
    t((247, 231), [((254, 235), (264, 233), (269, 230))], '#e24a38', 1.2)
    t((225, 229), [((244, 240), (268, 242), (285, 235))], '#e6b227', 3.2)
    t((229, 230), [((243, 237), (262, 239), (272, 237))], '#ffda52', .8)

    # Near sleeve and bent arm end at the existing, correctly oriented cuff.
    s((315, 177), [((326, 177), (336, 187), (335, 198)),
                    ((333, 207), (328, 216), (320, 217)),
                    ((308, 213), (300, 204), (300, 194)),
                    ((301, 184), (307, 178), (315, 177))], '#2a3038')
    s((316, 180), [((326, 182), (332, 189), (331, 198)),
                    ((325, 202), (319, 202), (312, 199)),
                    ((307, 193), (308, 183), (316, 180))], '#464d56', None)
    s((328, 190), [((333, 193), (334, 200), (329, 204)),
                    ((325, 207), (321, 204), (320, 200)),
                    ((319, 194), (323, 189), (328, 190))], '#363e48', '#8b97a1', .8)
    buttons(a, [(327, 192), (328, 201)])
    t((304, 196), [((306, 202), (313, 206), (317, 206))], '#606a74', .8)
    s((305, 204), [((312, 209), (323, 214), (332, 205)),
                    ((331, 213), (327, 219), (321, 221)),
                    ((313, 218), (307, 213), (305, 204))], '#dde4e8', '#18212b', 1)
    t((309, 210), [((317, 216), (325, 216), (330, 211))], '#8c9ba7', .8)
    s((321, 217), [((327, 216), (331, 228), (335, 237)),
                    ((338, 243), (343, 247), (348, 245)),
                    ((352, 243), (357, 246), (358, 252)),
                    ((355, 256), (349, 260), (343, 258)),
                    ((330, 255), (323, 243), (319, 232)),
                    ((317, 226), (316, 220), (321, 217))], '#ecb18a', '#3b2924', 1.2)
    s((319, 226), [((323, 242), (331, 253), (343, 257)),
                    ((349, 259), (354, 255), (356, 251)),
                    ((352, 253), (346, 254), (341, 251)),
                    ((330, 246), (328, 232), (325, 227)),
                    ((323, 225), (321, 225), (319, 226))], '#bd7c5e', None)
    t((325, 220), [((327, 229), (331, 239), (335, 243))], '#ffd2a6', 1.2)
    t((343, 247), [((347, 248), (350, 248), (353, 250))], '#f7c599', .9)
    t((337, 246), [((336, 249), (338, 252), (342, 252))], '#cd9471', .7)
    return a.finish(), 238, [(0, 0), (512, 0), (512, 174), (340, 174),
                            (324, 181), (301, 185), (288, 180), (281, 162),
                            (277, 144), (273, 131), (263, 119), (0, 119)]


def loop04():
    a = Art()
    s, t = a.shape, a.stroke
    # Far arm follows this higher, compressed stride; independent controls.
    s((258, 116), [((249, 121), (240, 134), (240, 145)),
                    ((243, 153), (253, 158), (263, 155)),
                    ((271, 148), (277, 134), (272, 124)),
                    ((268, 118), (263, 116), (258, 116))], '#2b3037')
    s((257, 123), [((248, 127), (244, 138), (247, 145)),
                    ((252, 148), (260, 145), (264, 140)),
                    ((268, 132), (267, 123), (257, 123))], '#454c54', None)
    t((250, 128), [((247, 133), (247, 139), (249, 142))], '#6b747d', .7)
    s((241, 145), [((247, 152), (255, 154), (263, 150)),
                    ((262, 157), (256, 161), (251, 161)),
                    ((244, 158), (240, 152), (241, 145))], '#e0e6e9', '#192129', 1)
    t((244, 150), [((249, 157), (256, 158), (260, 155))], '#919ea8', .8)
    s((252, 158), [((248, 162), (242, 169), (237, 174)),
                    ((231, 180), (225, 187), (220, 195)),
                    ((217, 199), (211, 197), (210, 193)),
                    ((214, 184), (224, 173), (230, 166)),
                    ((237, 158), (244, 153), (247, 153)),
                    ((249, 154), (251, 156), (252, 158))], '#edb28a', '#3b2a24', 1.2)
    s((212, 189), [((220, 177), (229, 168), (236, 162)),
                    ((232, 170), (227, 179), (222, 186)),
                    ((218, 191), (217, 196), (215, 197)),
                    ((212, 196), (211, 193), (212, 189))], '#be7d5d', None)
    t((244, 160), [((238, 168), (231, 175), (226, 181))], '#ffd2a7', 1)
    glove(a, 215, 201, 1)

    s((263, 99), [((273, 94), (287, 98), (299, 106)),
                    ((301, 117), (299, 128), (292, 141)),
                    ((279, 135), (262, 129), (252, 118)),
                    ((252, 110), (257, 102), (263, 99))], '#20262e')
    s((263, 103), [((275, 100), (287, 104), (294, 110)),
                    ((290, 113), (277, 110), (269, 112)),
                    ((263, 115), (259, 115), (257, 112)),
                    ((258, 108), (260, 105), (263, 103))], '#3c454e', None)
    t((261, 104), [((268, 100), (281, 104), (285, 106))], '#65727e', .7)
    s((274, 108), [((285, 109), (294, 120), (303, 138)),
                    ((320, 143), (339, 147), (347, 159)),
                    ((351, 176), (335, 193), (315, 206)),
                    ((297, 217), (271, 219), (250, 208)),
                    ((239, 202), (233, 190), (237, 177)),
                    ((240, 155), (252, 130), (263, 116)),
                    ((267, 111), (270, 108), (274, 108))], '#292f37')
    s((270, 117), [((279, 114), (286, 121), (288, 129)),
                    ((271, 141), (258, 163), (252, 184)),
                    ((244, 189), (240, 185), (242, 177)),
                    ((247, 153), (258, 129), (270, 117))], '#444c54', None)
    s((271, 137), [((276, 133), (281, 133), (282, 136)),
                    ((271, 152), (265, 169), (262, 187)),
                    ((258, 190), (254, 188), (255, 183)),
                    ((258, 164), (264, 147), (271, 137))], '#353d46', None)
    s((334, 163), [((338, 166), (341, 171), (338, 175)),
                    ((325, 197), (299, 210), (272, 212)),
                    ((266, 210), (262, 205), (261, 200)),
                    ((292, 199), (317, 181), (334, 163))], '#171e27', None)
    s((239, 182), [((243, 191), (249, 198), (257, 201)),
                    ((254, 205), (250, 204), (247, 202)),
                    ((240, 197), (236, 189), (239, 182))], '#1e252e', None)
    t((251, 177), [((248, 185), (251, 192), (258, 194))], '#69737d', .8)
    t((244, 192), [((250, 199), (259, 202), (264, 202))], '#4c5864', .8)
    t((264, 208), [((275, 213), (286, 212), (293, 209))], '#424f5d', .8)
    s((260, 115), [((267, 113), (274, 120), (275, 127)),
                    ((274, 135), (269, 137), (264, 133)),
                    ((257, 129), (254, 120), (260, 115))], '#38424c', '#7e8d99', .8)
    t((260, 116), [((265, 114), (270, 120), (272, 123))], '#b1c0ca', .6)
    buttons(a, [(261, 117), (271, 130)])
    t((274, 139), [((275, 145), (273, 151), (269, 155))], '#d5a424', 2.7)
    t((273, 140), [((273, 145), (271, 149), (269, 151))], '#f7d754', .9)

    s((306, 142), [((315, 142), (328, 146), (340, 154)),
                    ((328, 178), (306, 197), (285, 208)),
                    ((275, 208), (267, 201), (266, 194)),
                    ((280, 174), (295, 152), (306, 142))], '#131b25')
    s((305, 154), [((314, 161), (325, 157), (332, 152)),
                    ((324, 169), (306, 184), (291, 191)),
                    ((284, 189), (280, 184), (280, 180)),
                    ((291, 165), (298, 158), (305, 154))], '#333e4a', None)
    t((306, 155), [((314, 164), (326, 158), (331, 155))], '#c0ccd6', 1.6)
    t((295, 175), [((299, 179), (302, 183), (304, 178)),
                    ((307, 176), (311, 178), (312, 173))], '#aab9c7', 1.2)
    t((299, 164), [((299, 169), (296, 173), (295, 175))], '#b8c7d2', .6)
    s((286, 113), [((292, 114), (299, 121), (301, 128)),
                    ((291, 150), (277, 172), (265, 186)),
                    ((259, 185), (255, 181), (253, 177)),
                    ((264, 157), (278, 132), (286, 113))], '#313a45')
    t((290, 115), [((295, 118), (299, 125), (301, 128)),
                    ((291, 150), (277, 172), (265, 186)),
                    ((260, 185), (256, 180), (253, 177))], '#dce5eb', 1.8)
    t((297, 131), [((287, 152), (275, 171), (264, 182))], '#8a9cae', .7)
    t((340, 155), [((327, 180), (306, 198), (284, 209)),
                    ((276, 212), (265, 208), (260, 204))], '#dce5eb', 1.8)
    t((335, 161), [((322, 181), (305, 197), (284, 205))], '#6b7f92', .7)
    buttons(a, [(324, 174), (311, 187), (298, 197)])
    s((272, 196), [((279, 201), (286, 202), (296, 196)),
                    ((292, 205), (284, 209), (276, 210)),
                    ((269, 209), (263, 205), (260, 200)),
                    ((265, 202), (270, 201), (272, 196))], '#a21b24')
    t((270, 205), [((277, 208), (286, 205), (290, 202))], '#e84a36', 1.2)
    t((247, 204), [((263, 215), (286, 217), (304, 211))], '#e6b527', 3.2)
    t((252, 206), [((265, 213), (281, 215), (292, 213))], '#ffdd57', .8)

    s((335, 147), [((345, 148), (354, 159), (353, 169)),
                    ((351, 178), (345, 187), (337, 188)),
                    ((326, 184), (318, 174), (319, 163)),
                    ((320, 154), (326, 147), (335, 147))], '#2a323c')
    s((335, 151), [((344, 152), (350, 160), (349, 168)),
                    ((344, 172), (337, 172), (331, 169)),
                    ((325, 163), (327, 154), (335, 151))], '#45505c', None)
    s((346, 159), [((351, 162), (351, 169), (347, 173)),
                    ((343, 176), (338, 172), (338, 168)),
                    ((337, 162), (342, 158), (346, 159))], '#35414e', '#879ba9', .8)
    buttons(a, [(345, 161), (346, 170)])
    t((323, 166), [((326, 172), (331, 177), (335, 177))], '#5d7180', .8)
    s((324, 175), [((330, 182), (342, 185), (350, 176)),
                    ((350, 182), (344, 189), (338, 191)),
                    ((331, 187), (326, 182), (324, 175))], '#dee7ed', '#182430', 1)
    t((328, 181), [((335, 187), (343, 186), (347, 182))], '#8ba2b2', .8)
    s((338, 187), [((344, 189), (344, 204), (350, 212)),
                    ((353, 216), (357, 216), (360, 212)),
                    ((362, 209), (368, 211), (370, 216)),
                    ((368, 222), (363, 226), (357, 225)),
                    ((345, 224), (337, 214), (334, 203)),
                    ((332, 197), (332, 190), (338, 187))], '#ecb28a', '#3b2924', 1.2)
    s((334, 198), [((337, 212), (346, 222), (357, 225)),
                    ((363, 227), (368, 222), (369, 217)),
                    ((365, 220), (359, 221), (354, 218)),
                    ((345, 213), (342, 203), (340, 199)),
                    ((338, 197), (336, 197), (334, 198))], '#bd7d5f', None)
    t((340, 192), [((342, 201), (345, 209), (349, 212))], '#ffd2a6', 1.2)
    t((357, 216), [((360, 216), (363, 214), (365, 214))], '#f7c699', .9)
    t((351, 216), [((349, 220), (352, 222), (356, 221))], '#ce9370', .7)
    return a.finish(), 212, [(0, 0), (512, 0), (512, 145), (352, 145),
                            (338, 155), (318, 160), (305, 153), (300, 134),
                            (293, 119), (288, 103), (275, 96), (0, 96)]


def soften_cloth(im, index):
    """Broad light inside new charcoal paint; preserve edges and colored trim."""
    p = np.array(im)
    rgb = p[:, :, :3].astype(float)
    yy, xx = np.indices(p.shape[:2])
    cx, cy = (259, 172) if index == 3 else (279, 144)
    light = 5*np.exp(-((xx-cx)/27)**2-((yy-cy)/45)**2)
    light -= 3*np.exp(-((xx-(cx+22))/18)**2-((yy-(cy+45))/14)**2)
    cloth = (p[:, :, 3] > 0) & (rgb.max(2)-rgb.min(2) < 30) & (rgb.max(2) < 116) & (rgb.min(2) > 25)
    rgb[cloth] += light[cloth, None]
    p[:, :, :3] = np.clip(rgb, 0, 255).astype('uint8')
    return Image.fromarray(p, 'RGBA')


for index in [args.frame] if args.frame is not None else [3, 4]:
    before_dir = LAYERS/f'frame_{index:02d}_review_v2'
    source_dir = LAYERS/f'frame_{index:02d}_review_v1'
    out = LAYERS/f'frame_{index:02d}_review_v3'
    out.mkdir(parents=True, exist_ok=True)
    m = json.loads((before_dir/'manifest.json').read_text(encoding='utf-8'))
    before_path = before_dir/f'sora_run_loop_{index:02d}_review.png'
    before_hash = hashlib.sha256(before_path.read_bytes()).hexdigest()
    original = Image.open(source_dir/'original_crop.png').convert('RGBA')
    before = Image.open(before_path).convert('RGBA')
    repair, lower_y, head_contour = loop03() if index == 3 else loop04()
    repair = soften_cloth(repair, index)
    # Only the genuine lower body is retained. The old upper torso and raised
    # two-hand arm are not present beneath this individually drawn jacket.
    body = Image.new('RGBA', (512, 512))
    body.paste(original.crop((0, lower_y, 512, 512)), (0, lower_y))
    body = Image.alpha_composite(body, repair)
    head = Image.open(source_dir/'head_occlusion.png').convert('RGBA')
    mask = Image.new('L', head.size)
    ImageDraw.Draw(mask).polygon(head_contour, fill=255)
    head.putalpha(Image.composite(head.getchannel('A'), Image.new('L', head.size), mask))
    body = Image.alpha_composite(body, head)
    body, removed = retain_main_body(body)
    assert all(r['area_px'] < 60 for r in removed), removed
    preserve_y = m['lower_body_preserved_from_y']
    old_body = Image.open(before_dir/'body_rebuilt.png').convert('RGBA')
    body.paste(old_body.crop((0, preserve_y, 512, 512)), (0, preserve_y))

    layers = {name: Image.open(before_dir/(name+'.png')).convert('RGBA')
              for name in ['weapon_back', 'weapon_foreground', 'approved_grip', 'chain']}
    result = Image.alpha_composite(layers['weapon_back'], body)
    for name in ['weapon_foreground', 'approved_grip', 'chain']:
        result = Image.alpha_composite(result, layers[name])
    H = np.array(m['master_to_screen_homography'])
    cuff = H @ np.array([77, 50, 1])
    cuff = cuff[:2]/cuff[2]
    assert np.array(body.getchannel('A'))[int(round(cuff[1])), int(round(cuff[0]))] > 240, cuff
    assert np.array_equal(np.array(result)[preserve_y:], np.array(before)[preserve_y:])
    # The carrying hand is a separate untouched layer; its opaque interior
    # must remain pixel-identical even though its background has changed.
    interior = np.array(layers['approved_grip'].getchannel('A')) == 255
    assert np.count_nonzero(interior) > 20
    assert np.array_equal(np.array(result)[interior], np.array(before)[interior])
    save_clean(repair, out/'individual_garment_arm_repair.png')
    save_clean(head, out/'head_preserved.png')
    mask.save(out/'head_contour_mask.png')
    save_clean(body, out/'body_rebuilt.png')
    for name, im in layers.items():
        # Copy encoded files exactly, rather than reencode approved assets.
        (out/(name+'.png')).write_bytes((before_dir/(name+'.png')).read_bytes())
        assert (out/(name+'.png')).read_bytes() == (before_dir/(name+'.png')).read_bytes()
    save_clean(result, out/f'sora_run_loop_{index:02d}_review.png')
    comparison = Image.new('RGB', (1536, 550), '#202633')
    d = ImageDraw.Draw(comparison)
    for column, (im, label) in enumerate([(original, 'Source pose / previous two-hand weapon'),
                                         (before, 'v2 / shared garment repairs'),
                                         (result, 'v3 / individual jacket and arms')]):
        comparison.paste(im, (column*512, 30), im)
        d.text((column*512+12, 9), label, fill='white')
    comparison.save(out/'Garment_Comparison.png')
    review = Image.new('RGB', (1024, 720), '#202633')
    review.paste(result, (0, 30), result)
    light = Image.new('RGB', (512, 512), '#dedfe2')
    light.paste(result, (0, 0), result)
    review.paste(light, (512, 30))
    rd = ImageDraw.Draw(review)
    rd.text((12, 9), f'Loop{index:02d} / individual garment and arm refinement', fill='white')
    rd.text((140, 557), '128px and mirrored review', fill='white')
    for column, im in enumerate([result, result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
        small = im.resize((128, 128), Image.Resampling.LANCZOS)
        review.paste(small, (160+column*190, 580), small)
    review.save(out/'Dark_Light_Game_Review.png')
    m.update({'status': 'individual garment/arm refinement; full animation QA pending',
              'source_review': before_dir.name, 'prior_review_sha256': before_hash,
              'garment_method': 'new per-pose cubic contours; no translated torso template',
              'head_method': 'source hair/face/neck with contour excluding prior shoulder fragments',
              'source_lower_plate_starts_y': lower_y,
              'projected_wrist_cuff': cuff.tolist(),
              'removed_detached_body_fragments': removed,
              'checks': ['original sheet/prior review hashes unchanged',
                         'all four weapon/grip/chain layer files byte-identical to v2',
                         'opaque grip interior exact; projected cuff inside arm',
                         f'lower-body composite exact from y{preserve_y}'],
              'limitations': ['Other loop poses still use older garment repairs.',
                              'Cross-frame clothing/arm proportions need further visual review.',
                              'Gait/root/timing and start/stop seams remain unfinished.',
                              'Offline art checks only; no Godot integration or aerial production.']})
    (out/'manifest.json').write_text(json.dumps(m, indent=2), encoding='utf-8')
    (out/'README.md').write_text(
        f'# Loop{index:02d} individual garment refinement\n\n'
        'The jacket, sleeves, released far arm and bent holding arm are drawn for '
        'this source pose. Source hair/face/neck and lower-body pose remain. This '
        'replaces the shifted chest template and overlapping source shoulder fragments. '
        'KH2 charcoal cloth, silver piping, yellow straps and red waist trim are retained.\n\n'
        'All four rigid weapon/grip/chain PNG layers are copied exactly from v2. '
        'The carrying grip orientation, geometry and slight foreground yaw are unchanged. '
        'Previous review folders and original sheets are preserved. See manifest for '
        'pixel checks and lower-body preservation boundary.\n\n'
        'This is working art, still requiring full-cycle anatomy, gait and transition '
        'review against approved idle quality. No Godot test or aerial artwork.\n', encoding='utf-8')
    Image.open(out/f'sora_run_loop_{index:02d}_review.png').verify()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
    assert hashlib.sha256(before_path.read_bytes()).hexdigest() == before_hash
    print(f'Loop{index:02d}: individual torso/arms saved; cuff {cuff.tolist()}; lower body/rigid carry checks passed.')
