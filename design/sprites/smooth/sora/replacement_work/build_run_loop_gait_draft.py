"""New alternating run gait drawings; preserves the preceding garment reviews.

Offline art construction only. New thigh, calf and shoe contours follow fixed
joint lengths. Upper reference art is translated, never resized into new poses.
"""
from pathlib import Path
import argparse
from functools import lru_cache
import hashlib
import json
import math

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import Art, save_clean
from refine_loop_late_stride_poses import contour, source_patch, sleeve, bent_arm, free_fist


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
parser = argparse.ArgumentParser()
parser.add_argument('--refined', action='store_true', help='16-pose gait/material review; preserves the first12-pose draft')
args = parser.parse_args()
REFINED = args.refined
LOOP = ROOT/'ready/run_loop'
REF = LOOP/'layers/frame_00_review_v3'
OUT = LOOP/('gait_refinement_v2' if REFINED else 'gait_refinement_v1')
SIZE = (512, 512)
FLOOR = 432
THIGH, CALF = 87., 68.
BOB = ([0, 6, 4, 0, -2, -4, -8, -4] if REFINED else [0, 6, 2, -4, -8, -4])*2
PHASES = (['contact', 'compression', 'passing', 'late passing', 'heel-off', 'toe-off', 'flight', 'pre-contact']
          if REFINED else ['contact', 'compression', 'passing', 'toe-off', 'flight', 'pre-contact'])*2
HALF = len(PHASES)//2


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def translate(im, xy):
    out = Image.new('RGBA', SIZE)
    out.alpha_composite(im, tuple(xy))
    assert np.count_nonzero(np.array(im.getchannel('A')) > 32) == \
        np.count_nonzero(np.array(out.getchannel('A')) > 32), 'Opaque pixels clipped'
    return out


def two_bone(start, end, upper, lower):
    """Analytic joint location with a forward-bending knee/elbow."""
    start, end = np.array(start, float), np.array(end, float)
    delta = end-start
    distance = float(np.linalg.norm(delta))
    assert abs(upper-lower)+.01 < distance < upper+lower-.01, (start, end, distance)
    axis = delta/distance
    perpendicular = np.array([axis[1], -axis[0]])
    along = (upper**2-lower**2+distance**2)/(2*distance)
    across = math.sqrt(max(0., upper**2-along**2))
    joint = start+axis*along+perpendicular*across
    assert abs(np.linalg.norm(joint-start)-upper) < 1e-8
    assert abs(np.linalg.norm(end-joint)-lower) < 1e-8
    return joint


def shoe(a, ankle, angle, far=False):
    """One fixed KH2 shoe geometry, redrawn at each rigid foot orientation.

    All contour distances are constant; no bitmap scale or shoe-length change.
    The farther foot receives a consistent darker material palette.
    """
    theta = math.radians(angle)
    rotation = np.array([[math.cos(theta), -math.sin(theta)],
                         [math.sin(theta), math.cos(theta)]])
    ankle = np.array(ankle, float)
    def p(x, y):
        return tuple(ankle+rotation@np.array([x, y]))
    def s(start, segments, fill, outline='#15181d', width=1.5):
        a.shape(p(*start), [tuple(p(*q) for q in segment) for segment in segments], fill, outline, width)
    def t(start, segments, fill, width=1.1):
        a.stroke(p(*start), [tuple(p(*q) for q in segment) for segment in segments], fill, width)
    yellow, gold, glow = ('#eab91e', '#a96d13', '#ffe85c') if far else ('#facb28', '#c08513', '#fff071')
    black = '#21252b' if far else '#272b31'
    # Continuous padded collar, heel and oversized toe silhouette.
    s((-20, -9), [((-30, -8), (-34, 1), (-32, 13)),
                   ((-32, 27), (-34, 43), (-31, 55)),
                   ((-27, 66), (5, 67), (32, 61)),
                   ((62, 57), (88, 46), (90, 31)),
                   ((92, 17), (74, 8), (53, 10)),
                   ((38, 11), (27, 21), (13, 27)),
                   ((12, 9), (16, -5), (7, -10)),
                   ((0, -14), (-11, -13), (-20, -9))], black, width=1.9)
    # Heel side, with the red KH2 insert beneath the crossing straps.
    s((-29, 25), [((-21, 27), (-8, 33), (1, 42)),
                  ((9, 48), (12, 55), (13, 61)),
                  ((0, 63), (-17, 62), (-27, 57)),
                  ((-30, 49), (-30, 34), (-29, 25))], '#a81f27' if far else '#c2272c')
    s((-27, 29), [((-19, 32), (-11, 36), (-8, 40)),
                  ((-14, 41), (-20, 44), (-27, 44)),
                  ((-28, 37), (-28, 32), (-27, 29))], '#e34536', None)
    # Convex yellow toe and its shaded side wall.
    s((15, 28), [((27, 21), (36, 11), (54, 11)),
                 ((74, 8), (88, 19), (88, 31)),
                 ((81, 40), (60, 53), (36, 57)),
                 ((25, 58), (17, 57), (13, 53)),
                 ((9, 48), (12, 36), (15, 28))], yellow)
    s((15, 39), [((20, 43), (27, 47), (37, 46)),
                 ((59, 44), (76, 31), (86, 26)),
                 ((90, 32), (81, 43), (68, 49)),
                 ((48, 59), (24, 61), (13, 53)),
                 ((10, 50), (11, 43), (15, 39))], gold, None)
    t((29, 23), [((42, 14), (63, 12), (72, 16))], glow, 1.6)
    t((26, 25), [((35, 20), (42, 18), (46, 18))], '#fff4a0', .6)
    if REFINED:
        # Curved toe planes, rather than a flat yellow area.
        s((25, 30), [((31, 20), (45, 14), (57, 14)),
                     ((69, 14), (78, 18), (81, 23)),
                     ((72, 24), (64, 31), (53, 35)),
                     ((42, 39), (29, 38), (25, 34)),
                     ((24, 33), (24, 31), (25, 30))], '#ffde44' if not far else '#f9cb35', None)
        t((20, 44), [((32, 53), (55, 44), (69, 37))], '#e6a91c' if not far else '#cf951d', 1.3)
        t((35, 21), [((43, 17), (55, 15), (63, 16))], '#fff5a1', .75)
    # Rubber sole; toe cap follows the same fixed three-quarter construction.
    s((-31, 52), [((-20, 58), (7, 60), (29, 56)),
                  ((48, 53), (68, 44), (81, 37)),
                  ((84, 34), (87, 29), (89, 29)),
                  ((94, 45), (63, 59), (32, 65)),
                  ((9, 71), (-26, 68), (-31, 59)),
                  ((-32, 57), (-32, 54), (-31, 52))], '#181b20')
    s((30, 55), [((46, 51), (71, 42), (84, 33)),
                 ((86, 36), (86, 40), (83, 43)),
                 ((66, 51), (46, 60), (32, 61)),
                 ((31, 59), (30, 57), (30, 55))], '#30353b', None)
    t((-25, 60), [((-12, 65), (9, 65), (23, 61))], '#43474d', .9)
    t((34, 61), [((54, 58), (75, 48), (85, 42))], '#44494f', .9)
    if REFINED:
        # The black front toe face is prominent on the approved KH2 shoes.
        s((67, 35), [((76, 25), (87, 24), (90, 30)),
                     ((95, 42), (76, 56), (51, 63)),
                     ((57, 54), (59, 44), (67, 35))], '#25292f', '#13191f', 1.3)
        s((73, 35), [((79, 29), (87, 28), (88, 33)),
                     ((86, 40), (76, 47), (64, 51)),
                     ((65, 45), (69, 39), (73, 35))], '#3d4349', None)
        t((75, 33), [((81, 29), (86, 30), (87, 32))], '#646b70', .75)
        t((70, 37), [((73, 40), (73, 45), (72, 48))], '#1c232b', .7)
    for x in [45, 58, 71]:
        t((x, 53-(x-45)*.38), [((x+2, 51-(x-45)*.38), (x+1, 56-(x-45)*.38), (x+1, 58-(x-45)*.38))], '#161b21', .75)
    # Padded yellow ankle collar, white lining and raised tongue.
    s((-29, 0), [((-25, -9), (-5, -12), (7, -8)),
                 ((13, -6), (13, 3), (9, 10)),
                 ((8, 17), (-14, 20), (-25, 13)),
                 ((-31, 10), (-33, 4), (-29, 0))], gold)
    s((-27, 2), [((-23, -3), (-7, -5), (3, -2)),
                 ((4, 4), (1, 9), (-1, 12)),
                 ((-8, 17), (-23, 11), (-27, 7)),
                 ((-28, 5), (-28, 3), (-27, 2))], yellow, None)
    t((-25, -1), [((-20, -6), (-6, -7), (1, -4)),
                  ((3, 0), (2, 4), (0, 7))], '#e0e4e4', 2.1)
    t((-22, -2), [((-16, -5), (-8, -4), (-4, -2))], '#313b45', 1.2)
    s((5, -9), [((14, -11), (17, -5), (14, 5)),
                ((12, 18), (8, 28), (2, 33)),
                ((0, 26), (1, 9), (5, -9))], '#3e4750', '#bdc8cd', 1.1)
    t((10, -4), [((12, 0), (10, 9), (7, 15))], '#9dabb3', .8)
    s((-15, 16), [((-6, 16), (7, 19), (12, 27)),
                  ((6, 37), (3, 47), (0, 52)),
                  ((-10, 44), (-16, 30), (-15, 16))], yellow)
    # Black instep X, lace openings and small rivets.
    s((-26, 16), [((-15, 20), (4, 35), (17, 48)),
                  ((17, 52), (14, 54), (12, 54)),
                  ((-4, 36), (-21, 25), (-28, 23)),
                  ((-29, 21), (-27, 18), (-26, 16))], '#1b2027', width=.8)
    s((13, 15), [((19, 21), (21, 28), (20, 33)),
                 ((7, 41), (-3, 46), (-13, 49)),
                 ((-16, 48), (-15, 44), (-12, 42)),
                 ((-2, 36), (6, 26), (13, 15))], '#1b2027', width=.8)
    t((-23, 20), [((-11, 25), (3, 38), (12, 47))], '#52606a', .75)
    t((13, 22), [((10, 30), (0, 39), (-9, 43))], '#59656e', .7)
    for x, y in [(-14, 21), (-6, 29), (2, 36), (10, 26), (4, 33)]:
        q = p(x, y)
        a.ellipse((q[0]-.85, q[1]-.85, q[0]+.85, q[1]+.85), '#929da3', '#222c36', .35)
    t((-24, 46), [((-22, 50), (-19, 53), (-15, 54))], '#ee6250', .8)


@lru_cache(maxsize=16)
def foot_extent(angle):
    a = Art()
    shoe(a, (256, 256), angle)
    alpha = np.array(a.finish().getchannel('A'))
    return int(np.argwhere(alpha > 32)[:, 0].max())-256


def grounded(x, angle=0):
    return (x, FLOOR-foot_extent(angle))


def calf(a, knee, ankle, far):
    knee, ankle = np.array(knee), np.array(ankle)
    direction = (ankle-knee)/CALF
    normal = np.array([-direction[1], direction[0]])
    def p(t, w):
        return tuple(knee+(ankle-knee)*t+normal*w)
    a.shape(p(-.08, -12), [(p(.25, -14), p(.55, -11), p(1.07, -9)),
                          (p(1.12, -5), p(1.12, 5), p(1.07, 9)),
                          (p(.65, 12), p(.22, 15), p(-.08, 12)),
                          (p(-.15, 7), p(-.15, -7), p(-.08, -12))], '#e3a47d' if far else '#efb58d', '#432e27', 1.5)
    a.shape(p(.03, 8), [(p(.3, 12), p(.7, 8), p(1.02, 5)),
                        (p(1.07, 2), p(1.07, -3), p(1.02, -4)),
                        (p(.7, -2), p(.25, 3), p(.03, 8))], '#ffcf9e' if not far else '#f6c291', None)
    a.shape(p(.08, -11), [(p(.35, -13), p(.8, -9), p(1.08, -7)),
                          (p(1.1, -4), p(1.08, -2), p(1.02, -1)),
                          (p(.7, -4), p(.25, -8), p(.08, -11))], '#bb7c5e', None)
    a.stroke(p(.38, 10), [(p(.52, 10), p(.75, 7), p(.88, 6))], '#ffd9ad', .65)


def shorts(a, hip, knee, far):
    hip, knee = np.array(hip), np.array(knee)
    axis = (knee-hip)/THIGH
    normal = np.array([-axis[1], axis[0]])
    def p(x, y):
        return tuple(hip+normal*x+axis*y)
    def s(start, segments, fill, outline='#14181e', width=1.6):
        a.shape(p(*start), [tuple(p(*q) for q in segment) for segment in segments], fill, outline, width)
    def t(start, segments, fill, width=1):
        a.stroke(p(*start), [tuple(p(*q) for q in segment) for segment in segments], fill, width)
    if REFINED:
        s((-23, -13), [((-35, -4), (-44, 20), (-40, 51)),
                        ((-42, 70), (-32, 88), (-13, 96)),
                        ((8, 105), (32, 96), (38, 78)),
                        ((44, 52), (41, 13), (24, -11)),
                        ((11, -20), (-9, -22), (-23, -13))], '#232629' if far else '#282b2e', width=1.9)
        s((-21, -7), [((-33, 7), (-34, 34), (-29, 60)),
                       ((-27, 80), (-12, 89), (7, 92)),
                       ((4, 80), (-5, 57), (-6, 37)),
                       ((-4, 18), (4, 1), (7, -9)),
                       ((-2, -15), (-13, -11), (-21, -7))], '#2f3338' if far else '#34393f', None)
        s((22, 2), [((32, 18), (34, 46), (30, 69)),
                     ((25, 88), (1, 96), (-18, 90)),
                     ((-4, 105), (25, 100), (36, 83)),
                     ((44, 60), (41, 21), (25, -4)),
                     ((24, -2), (23, 0), (22, 2))], '#1b1f24', None)
        t((-38, 64), [((-23, 75), (15, 82), (37, 69))], '#c2c9cf', 1.6)
        t((-34, 67), [((-20, 77), (15, 82), (32, 73))], '#65717d', .65)
        t((-27, 86), [((-11, 96), (12, 97), (24, 87))], '#444e59', .75)
        t((-30, 33), [((-32, 44), (-28, 58), (-22, 62))], '#58636e', .6)
        t((27, 48), [((27, 58), (24, 62), (20, 66))], '#43505d', .65)
        t((-25, 7), [((-21, 19), (-19, 25), (-20, 31))], '#535e69', .65)
        # The strap is shared below; each pose still follows its own thigh axis.
    else:
        s((-23, -13), [((-34, -6), (-46, 32), (-39, 67)),
                        ((-43, 86), (-32, 106), (-10, 110)),
                        ((12, 116), (35, 106), (39, 88)),
                        ((45, 53), (40, 12), (24, -11)),
                        ((11, -20), (-9, -22), (-23, -13))], '#24272c' if far else '#292c32', width=1.9)
        s((-21, -7), [((-33, 10), (-35, 45), (-28, 69)),
                   ((-26, 88), (-11, 100), (9, 101)),
                   ((6, 90), (-5, 65), (-6, 45)),
                   ((-4, 21), (4, 1), (7, -9)),
                   ((-2, -15), (-13, -11), (-21, -7))], '#363b42' if far else '#3d434b', None)
        s((22, 2), [((33, 20), (34, 56), (29, 82)),
                 ((24, 99), (-1, 109), (-20, 99)),
                 ((-6, 114), (24, 112), (35, 96)),
                 ((43, 66), (42, 22), (25, -4)),
                 ((24, -2), (23, 0), (22, 2))], '#191f27', None)
    # Compression folds bend around the real knee; curved white hem piping.
        t((-37, 77), [((-21, 86), (16, 93), (37, 80))], '#c2c9cf', 1.6)
        t((-33, 79), [((-20, 88), (15, 93), (32, 85))], '#697684', .65)
        t((-27, 97), [((-12, 103), (10, 107), (23, 99))], '#4e5864', .75)
        t((-28, 35), [((-31, 49), (-28, 64), (-21, 71))], '#68727c', .7)
        t((28, 55), [((26, 65), (25, 71), (21, 75))], '#47535f', .7)
        t((-25, 7), [((-21, 19), (-19, 25), (-20, 31))], '#535e69', .7)
    # Gold straps wrap diagonally around the upper thigh, as on the KH2 outfit.
    if REFINED:
        s((-31, 11), [((-16, 4), (6, -7), (25, -12)),
                       ((27, -11), (30, -7), (30, -3)),
                       ((11, 2), (-12, 13), (-26, 20)),
                       ((-30, 20), (-32, 15), (-31, 11))], '#d9a328' if far else '#efbd31', '#654c20', .8)
        t((-28, 12), [((-12, 4), (9, -6), (24, -9))], '#ffe272', .95)
        q = p(-25, 13)
    else:
        s((-18, -16), [((-20, -3), (-23, 14), (-27, 25)),
                        ((-26, 30), (-21, 31), (-17, 26)),
                        ((-12, 12), (-8, -2), (-10, -14)),
                        ((-12, -17), (-15, -17), (-18, -16))], '#d8a52a' if far else '#efbd31', '#654c20', .8)
        t((-16, -11), [((-18, 3), (-21, 16), (-22, 23))], '#ffe272', .95)
        q = p(-15, -9)
    a.ellipse((q[0]-1, q[1]-1, q[0]+1, q[1]+1), '#e2e7e3', '#494b42', .45)


def pelvis(a, bob):
    def p(x, y):
        return (x, y+bob)
    a.shape(p(251, 248), [(p(272, 246), p(295, 248), p(319, 253)),
                          (p(325, 267), p(311, 284), p(292, 294)),
                          (p(276, 302), p(257, 290), p(245, 275)),
                          (p(240, 263), p(244, 254), p(251, 248))], '#242b34')
    a.shape(p(269, 251), [(p(280, 254), p(300, 255), p(310, 256)),
                          (p(296, 270), p(286, 279), p(277, 286)),
                          (p(270, 287), p(265, 281), p(262, 276)),
                          (p(266, 267), p(267, 257), p(269, 251))], '#3c4651', None)
    a.stroke(p(296, 257), [(p(288, 268), p(278, 279), p(269, 283))], '#a9b6bf', 1.2)
    for x, y in [(290, 264), (282, 273), (272, 280)]:
        a.ellipse((x-1, y+bob-1, x+1, y+bob+1), '#c3ccd1', '#202a35', .5)


def leg_finish(a, hip, knee, ankle, angle):
    im = a.finish()
    if not REFINED:
        return im
    pixels = np.array(im)
    rgb = pixels[:, :, :3].astype(float)
    yy, xx = np.indices(rgb.shape[:2])
    center = (np.array(hip)+np.array(knee))/2
    fabric = (pixels[:, :, 3] > 0) & (rgb.max(2) < 105) & (rgb.min(2) > 23) & (rgb.max(2)-rgb.min(2) < 35)
    volume = 5*np.exp(-((xx-center[0]+8)/31)**2-((yy-center[1]+5)/39)**2)
    rgb[fabric] += volume[fabric, None]
    # A local-coordinate light keeps the yellow toe rounded as the foot turns.
    theta = math.radians(angle)
    dx, dy = xx-ankle[0], yy-ankle[1]
    local_x = math.cos(theta)*dx+math.sin(theta)*dy
    local_y = -math.sin(theta)*dx+math.cos(theta)*dy
    yellow = (pixels[:, :, 3] > 0) & (rgb[:, :, 0] > 170) & (rgb[:, :, 1] > 115) & (rgb[:, :, 2] < 100)
    toe_light = np.exp(-((local_x-52)/25)**2-((local_y-22)/12)**2)
    for channel, strength in [(0, 8), (1, 12), (2, 5)]:
        rgb[:, :, channel][yellow] += (toe_light*strength)[yellow]
    pixels[:, :, :3] = np.clip(rgb, 0, 255).astype('uint8')
    return Image.fromarray(pixels, 'RGBA')


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    # Capture originals and every preceding per-pose/cycle PNG before writing.
    protected = [LOOP/'run_loop_source.png', ROOT/'ready/run_start/run_start_source.png']
    protected += list((LOOP/'review_cycle_v5').glob('*'))
    protected += list(REF.glob('*'))
    if REFINED:
        protected += list((LOOP/'gait_refinement_v1').rglob('*'))
    protected += [LOOP/'layers/art_pass_05/kingdom_key_master_finished.png',
                  LOOP/'layers/art_pass_05/grip_master_space.png']
    before_hashes = {p: sha(p) for p in protected if p.is_file()}
    assert before_hashes[LOOP/'run_loop_source.png'] == '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
    source_body = Image.open(REF/'body_rebuilt.png').convert('RGBA')
    # Reassemble the source jacket/head/holding arm without its old released arm.
    upper = Image.new('RGBA', SIZE)
    for name in ['individual_clothing_repair', 'source_jacket_detail', 'holding_arm', 'head_preserved']:
        upper = Image.alpha_composite(upper, Image.open(REF/(name+'.png')).convert('RGBA'))
    waist_mask = contour([(192, 231), (201, 221), (225, 210), (245, 218),
                          (258, 231), (278, 241), (308, 248), (341, 240),
                          (345, 251), (311, 260), (278, 260), (258, 259),
                          (230, 265), (208, 258), (195, 246)])
    waist = source_patch(source_body, waist_mask)
    upper = Image.alpha_composite(waist, upper)
    save_clean(upper, OUT/'upper_reference.png')
    waist_mask.save(OUT/'waist_source_mask.png')
    source_meta = json.loads((REF/'manifest.json').read_text(encoding='utf-8'))
    H = np.array(source_meta['master_to_screen_homography'])
    rigid = {name: Image.open(REF/(name+'.png')).convert('RGBA')
             for name in ['weapon_back', 'weapon_foreground', 'approved_grip', 'chain']}
    approved_region = Image.open(REF/'approved_hand_cuff_region.png').convert('RGBA')
    # Each half has one stance sequence and the opposite limb's recovery arc.
    stance = [(grounded(374), 0), (grounded(338), 0), (grounded(298), 0),
              (grounded(187, 25), 25), ((183, 300), 60), ((221, 305), 75)]
    swing = [((161, 311), 60), ((205, 298), 75), ((255, 302), 0),
             ((316, 327), -15), ((353, 350), -10),
             ((340, grounded(340, -5)[1]-8), -5)]
    if REFINED:
        # Two new drawings distribute the stance-foot travel across heel-off.
        stance = [(grounded(374), 0), (grounded(338), 0), (grounded(298), 0),
                  (grounded(243, 10), 10), (grounded(218, 20), 20),
                  (grounded(187, 25), 25), ((183, 300), 60), ((190, 300), 65)]
        swing = [((161, 311), 60), ((180, 302), 70), ((205, 298), 75),
                 ((255, 302), 40), ((288, 314), 5), ((316, 327), -15),
                 ((353, 350), -10), ((340, grounded(340, -5)[1]-8), -5)]
    frames, records = [], []
    for i in range(len(PHASES)):
        bob = BOB[i]
        near_hip, far_hip = np.array([294., 268.+bob]), np.array([257., 270.+bob])
        if i < HALF:
            near_ankle, near_angle = stance[i]
            far_ankle, far_angle = swing[i]
        else:
            far_ankle, far_angle = stance[i-HALF]
            far_ankle = (far_ankle[0]-(37 if REFINED else 23), far_ankle[1])
            near_ankle, near_angle = swing[i-HALF]
            near_ankle = (near_ankle[0]+37, near_ankle[1])
        near_knee = two_bone(near_hip, near_ankle, THIGH, CALF)
        far_knee = two_bone(far_hip, far_ankle, THIGH, CALF)
        far, near = Art(), Art()
        for a, hip, knee, ankle, angle, distant in [
            (far, far_hip, far_knee, far_ankle, far_angle, True),
            (near, near_hip, near_knee, near_ankle, near_angle, False)]:
            calf(a, knee, ankle, distant)
            shorts(a, hip, knee, distant)
            shoe(a, ankle, angle, distant)
        center = Art()
        pelvis(center, bob)
        # The free arm counter-swings continuously; the carrying arm is retained.
        phase = i*2*math.pi/len(PHASES)
        shoulder = np.array([302., 165.+bob])
        wrist = np.array([293.+57*math.cos(phase), 232.-11*math.sin(phase)+bob])
        elbow = two_bone(shoulder, wrist, 54., 44.)
        cuff = shoulder+(elbow-shoulder)/54*31
        arm = Art()
        sleeve(arm, shoulder, cuff)
        bent_arm(arm, cuff, elbow, wrist, 5.2)
        free_fist(arm, *wrist)
        shift = (2, 3+bob)
        shifted_upper = translate(upper, shift)
        far_image = leg_finish(far, far_hip, far_knee, far_ankle, far_angle)
        near_image = leg_finish(near, near_hip, near_knee, near_ankle, near_angle)
        body = Image.alpha_composite(arm.finish(), far_image)
        body = Image.alpha_composite(body, center.finish())
        body = Image.alpha_composite(body, near_image)
        body = Image.alpha_composite(body, shifted_upper)
        projected = {name: translate(im, shift) for name, im in rigid.items()}
        im = Image.alpha_composite(projected['weapon_back'], body)
        for name in ['weapon_foreground', 'approved_grip', 'chain']:
            im = Image.alpha_composite(im, projected[name])
        approved_xy = (384+shift[0], 203+shift[1])
        im.paste(approved_region, approved_xy)
        assert np.array_equal(np.array(im.crop((*approved_xy, approved_xy[0]+40, approved_xy[1]+45))),
                              np.array(approved_region)), 'Approved hand/cuff changed'
        layer_dir = OUT/'layers'/f'phase_{i:02d}'
        layer_dir.mkdir(parents=True, exist_ok=True)
        for name, layer in [('far_leg', far_image), ('near_leg', near_image),
                            ('pelvis', center.finish()), ('free_arm', arm.finish()),
                            ('upper', shifted_upper), ('body', body), *projected.items()]:
            save_clean(layer, layer_dir/(name+'.png'))
        name = f'sora_run_loop_gait_{i:02d}.png'
        save_clean(im, OUT/name)
        frames.append(im)
        exported_H = np.array([[1, 0, shift[0]], [0, 1, shift[1]], [0, 0, 1]])@H
        foot_bounds = {}
        for side, ankle, angle in [('near', near_ankle, near_angle), ('far', far_ankle, far_angle)]:
            foot = Art()
            shoe(foot, ankle, angle, side == 'far')
            occupied = np.argwhere(np.array(foot.finish().getchannel('A')) > 32)
            lowest = int(occupied[:, 0].max())
            sole = occupied[occupied[:, 0] == lowest, 1]
            foot_bounds[side] = {'sole_bottom_y': lowest, 'floor_clearance_px': FLOOR-lowest,
                                 'sole_lowest_span_x': [int(sole.min()), int(sole.max())],
                                 'sole_lowest_sample_x': float(sole.mean())}
            assert lowest <= FLOOR, (i, side, lowest)
        support = ('near' if i < HALF else 'far') if i % HALF < HALF-2 else None
        if support:
            assert foot_bounds[support]['sole_bottom_y'] == FLOOR, (i, support, foot_bounds)
        else:
            assert min(v['floor_clearance_px'] for v in foot_bounds.values()) > 0
        records.append({'index': i, 'path': name, 'phase': PHASES[i], 'support_leg': support,
                        'duration_ms': 60 if REFINED else 70, 'body_bob_px': bob, 'root_xy': [280, 268+bob],
                        'near': {'hip': near_hip.tolist(), 'knee': near_knee.tolist(),
                                 'ankle': list(near_ankle), 'shoe_angle_deg': near_angle, **foot_bounds['near']},
                        'far': {'hip': far_hip.tolist(), 'knee': far_knee.tolist(),
                                'ankle': list(far_ankle), 'shoe_angle_deg': far_angle, **foot_bounds['far']},
                        'free_arm': {'shoulder': shoulder.tolist(), 'elbow': elbow.tolist(), 'wrist': wrist.tolist()},
                        'master_to_export_homography': exported_H.tolist(),
                        'approved_hand_region_xy': list(approved_xy), 'upper_reference_translation_xy': list(shift)})
    package(frames, records)
    if REFINED:
        for half, side in [(records[:HALF], 'near'), (records[HALF:], 'far')]:
            contacts = [r[side]['sole_lowest_sample_x'] for r in half if r['support_leg']]
            travel = np.diff(contacts)
            assert np.all(travel < 0), ('Stance foot reverses', side, travel)
            assert np.max(np.abs(travel)) <= 45, ('Large stance contact jump', side, travel)
    for p, original_hash in before_hashes.items():
        assert sha(p) == original_hash, f'Protected prior artwork changed: {p}'
    for record in records:
        Image.open(OUT/record['path']).verify()
        pixels = np.array(Image.open(OUT/record['path']))
        assert np.all(pixels[pixels[:, :, 3] == 0, :3] == 0)
    assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in frames}) == len(PHASES)
    for name in ['sora_run_loop_gait_preview.gif', 'sora_run_loop_gait_slow.gif']:
        gif = Image.open(OUT/name)
        assert gif.n_frames == len(PHASES)
        for i in range(len(PHASES)):
            gif.seek(i)
            gif.load()
    (OUT/'manifest.json').write_text(json.dumps({
        'status': 'new alternating gait art draft; not idle-quality or gameplay approval',
        'canvas': [512, 512], 'gameplay_review_size': [128, 128], 'floor_y': FLOOR,
        'projected_thigh_length_px': THIGH, 'projected_calf_length_px': CALF,
        'method': 'New per-pose thigh/calf/shoe contours; fixed joint lengths; independently changing near/far limbs.',
        'upper_reference': 'layers/frame_00_review_v3; retained jacket/head/holding arm, translated only',
        'shoe_geometry': 'one fixed local contour geometry drawn at recorded rigid rotations; no bitmap resizing',
        'physical_master_length_px': 285, 'master_scale': 1,
        'weapon_master_sha256': before_hashes[LOOP/'layers/art_pass_05/kingdom_key_master_finished.png'],
        'grip_master_sha256': before_hashes[LOOP/'layers/art_pass_05/grip_master_space.png'],
        'prior_artwork_sha256': {str(p.relative_to(ROOT)): h for p, h in before_hashes.items()},
        'frames': records,
        'checks': [f'{len(PHASES)} distinct full frames; PNG/GIF decoding', 'fixed projected joint lengths',
                   'support feet on floor; airborne feet above floor', 'approved hand/cuff exact after translation',
                   'rigid carry layers translate with upper body without scaling', 'all captured prior/source hashes unchanged']
                  + (['Both stance contact samples move backward by at most45px per drawing'] if REFINED else []),
        'limitations': ['New lower-body materials and silhouettes need comparison with the approved idle.',
                        'Fixed upper reference needs per-phase torso/shoulder/cloth follow-through refinement.',
                        'Planar joint constraints are drawing aids, not exact three-dimensional anatomy.',
                        f'Foot speed and {60 if REFINED else 70}ms timing are provisional; no engine speed matching.',
                        'Start/stop/idle transitions are not changed; no Godot test or aerial artwork.']}, indent=2), encoding='utf-8')
    (OUT/'README.md').write_text(
        '# Alternating run gait drawing draft\n\n'
        'Twelve new lower-body drawings establish near-foot contact00 and far-foot contact06. '
        'Each half has compression, passing, toe-off, flight and opposite-foot pre-contact. '
        'Both legs retain projected joint lengths87/68px; thigh, calf and shoe contours are '
        'drawn at their actual joint positions. No scaled character copies or whole-character '
        'mirrors create the opposite stride. The shoes share fixed local geometry and vary '
        'only by rigid orientation and near/far lighting.\n\n'
        'The existing00 jacket/head/carrying arm and source waist detail provide the upper '
        'reference, with a translated body bob and a newly drawn counter-swinging free arm. '
        'The Kingdom Key projection, approved grip and final hand/cuff region move with that '
        'upper reference. All preceding reviews and original sheets remain intact.\n\n'
        'This is a gait art draft, not final animation quality. Fixed upper-body reuse needs '
        'phase-specific torso/shoulder/cloth follow-through. New shorts, calves and shoes need '
        'material/silhouette polish. Contact trajectory and70ms timings are provisional and '
        'not matched to engine movement. Start/stop seams remain. No generation retry, '
        'protected engine edit, Godot test or aerial production.\n', encoding='utf-8')
    if REFINED:
        (OUT/'README.md').write_text(
            '# Sixteen-pose alternating gait refinement\n\n'
            'New late-passing and heel-off drawings bridge each stride before toe-off. '
            'The sole-contact samples retreat by at most45px per drawing; the stance ankle '
            'moves at most55px, replacing the first draft\'s111px ankle jump. '
            'Near-foot contact is00, far-foot contact08. '
            'The foot-recovery arcs connect through both half-cycle seams. '
            'Shorts are shorter/rounder with softer charcoal planes, and the fixed shoe '
            'geometry has curved yellow toe planes and local light. Both limbs are '
            'drawn at fixed87/68px projected joints; no scaled pose copies.\n\n'
            'The current00 upper artwork remains the reference, with translation-only '
            'bob and a newly drawn free-arm swing. The rigid Kingdom Key, corrected grip '
            'and final hand/cuff region move together. This is an art/gait candidate; '
            'upper-body follow-through, limb perspective/materials, foot trajectory and '
            'provisional60ms timing still need refinement against approved idle. '
            'Prior12-pose gait draft, all eight-pose garment reviews and originals remain. '
            'Start/stop seams are unchanged. No Godot test or aerial artwork.\n', encoding='utf-8')
        (OUT/'QA_NOTES.md').write_text(
            '# Gait candidate review limits\n\n'
            '- Grounded phases have a sole touching y432; the two air phases each half '
            'retain positive floor clearance. Hip/foot positions and bone lengths are recorded.\n'
            '- New sixteen drawings reduce the passing-to-push-off gap. This is not proof '
            'of matching engine speed; actual stance-foot planting depends on world movement.\n'
            '- All poses reuse00\'s jacket/head/holding arm with body bob. Per-phase torso '
            'pitch, shoulders, carrying-arm anatomy and cloth/hair follow-through remain.\n'
            '- The new shorts/boots are still less detailed than approved idle. Compare '
            'silhouette, calf proportions and near/far occlusion before replacing the garment review.\n'
            '- Common projected bone lengths are drawing constraints, not exact3D anatomy. '
            'No gameplay integration/test, start/stop seam changes or aerial production.\n', encoding='utf-8')
    print(f'Verified{len(PHASES)} new gait drawings, fixed joints, contact/flight feet, exact hand and preserved sources.', OUT)
    print('Near/far floor clearances:', [(r['near']['floor_clearance_px'], r['far']['floor_clearance_px']) for r in records])


def package(frames, records):
    rows = len(frames)//4
    sheet = Image.new('RGBA', (2048, rows*512))
    board = Image.new('RGB', (1024, rows*280), '#202633')
    mirror = Image.new('RGB', (len(frames)*128, 336), '#202633')
    landmarks = Image.new('RGB', (2048, rows*544), '#202633')
    flat = []
    for i, (im, record) in enumerate(zip(frames, records)):
        sheet.paste(im, (i % 4*512, i//4*512))
        small = im.resize((256, 256), Image.Resampling.LANCZOS)
        x, y = i % 4*256, i//4*280
        board.paste(small, (x, y+20), small)
        d = ImageDraw.Draw(board)
        d.text((x+8, y+5), f'{i:02d} {record["support_leg"] or "air"}: {record["phase"]}', fill='white')
        d.line((x, y+236, x+255, y+236), fill='#637180')
        for row, current in enumerate([im, im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
            game = current.resize((128, 128), Image.Resampling.LANCZOS)
            mirror.paste(game, (i*128, row*168+24), game)
            ImageDraw.Draw(mirror).text((i*128+6, row*168+6), f'{i:02d}', fill='white')
        lx, ly = i % 4*512, i//4*544
        landmarks.paste(im, (lx, ly+24), im)
        ld = ImageDraw.Draw(landmarks)
        ld.text((lx+10, ly+5), f'{i:02d} / {record["phase"]} / cyan near, pink far', fill='white')
        ld.line((lx, ly+24+FLOOR, lx+511, ly+24+FLOOR), fill='#708294')
        for side, color in [('far', '#ef86ba'), ('near', '#67dae5')]:
            points = [(lx+record[side][key][0], ly+24+record[side][key][1]) for key in ['hip', 'knee', 'ankle']]
            ld.line(points, fill=color, width=2)
            for xj, yj in points:
                ld.ellipse((xj-3, yj-3, xj+3, yj+3), fill=color)
        bg = Image.new('RGB', SIZE, '#202633')
        bg.paste(im, (0, 0), im)
        flat.append(bg)
    save_clean(sheet, OUT/'sora_run_loop_gait_sheet.png')
    board.save(OUT/'Contact_Sheet.png')
    mirror.save(OUT/'Game_Size_Mirrored_Review.png')
    landmarks.save(OUT/'Joint_Contact_Review.png')
    flat[0].save(OUT/'sora_run_loop_gait_preview.gif', save_all=True, append_images=flat[1:], duration=60 if REFINED else 70, loop=0, disposal=2)
    flat[0].save(OUT/'sora_run_loop_gait_slow.gif', save_all=True, append_images=flat[1:], duration=180 if REFINED else 210, loop=0, disposal=2)


if __name__ == '__main__':
    build()
