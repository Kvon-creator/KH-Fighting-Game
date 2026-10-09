"""Joint-following upper-body art for the local Sora run-loop workflow.

Pure drawing helpers: no image-generation calls, file mutations or CLI parsing.
"""
import math

import numpy as np
from PIL import Image

from local_pose_art import Art
from refine_loop_late_stride_poses import crown, metal


def jacket(pose):
    """Draw chest panels around independently moving neck/shoulder/waist points."""
    a = Art()
    B, N, S, WF, WN = [np.array(pose[key], float) for key in
                        ['back_neck', 'front_neck', 'near_shoulder', 'waist_far', 'waist_near']]
    compression, twist = pose['compression'], pose['twist']
    def p(anchor, x, y):
        return tuple(anchor+np.array([x, y]))
    s, t = a.shape, a.stroke
    s(tuple(B), [(p(B, 11, -2), p(N, -11, -15), tuple(N)),
                 (p(N, 11, 3), p(S, 6, -1), p(S, 15, 11)),
                 (p(S, 17, 26), p(WN, 23, -15), p(WN, 4, -4)),
                 (p(WN, -15, 7), p(WF, 21, 11), tuple(WF)),
                 (p(WF, -14, -6), p(WF, -23, -18), p(WF, -16, -32)),
                 (p(B, -31, 42), p(B, -15, 10), tuple(B))], '#292e35', width=1.65)
    # Back jacket plane and the underarm shadow change as the chest counter-turns.
    s(p(B, -6, 9), [(p(B, 3, 6), p(N, -22, -9), p(N, -19, 0)),
                    (p(B, -1, 40), p(WF, 5, -32), p(WF, -3, -14)),
                    (p(WF, -9, -11), p(WF, -14, -16), p(WF, -10, -25)),
                    (p(B, -27, 45), p(B, -15, 18), p(B, -6, 9))], '#414b56', None)
    s(p(S, 1, 15), [(p(S, 8, 17), p(S, 10, 22), p(S, 5, 28)),
                    (p(WN, 11, -9), p(WF, 43, 5), p(WF, 21, 1)),
                    (p(WF, 16, -2), p(WF, 13, -8), p(WF, 15, -11)),
                    (p(WF, 43, -11), p(S, -16, 34), p(S, 1, 15))], '#18212b', None)
    t(p(WF, 1, -37), [(p(WF, -5, -27), p(WF, -3, -19), p(WF, 4, -16))], '#60727f', .75)
    t(p(WF, 5, -8), [(p(WF, 13, -2-compression*2), p(WF, 24, 1), p(WF, 31, -1))], '#4d606e', .7)
    # Short yellow jacket attachment at the far chest.
    t(p(B, 4, 28), [(p(B, 4, 34), p(B, 0, 42), p(B, -4, 47))], '#dfaf28', 2.5)
    t(p(B, 3, 29), [(p(B, 3, 34), p(B, 0, 39), p(B, -2, 42))], '#f9d965', .8)
    # Black shirt and its curved neck opening remain separate from the jacket.
    shirt_bottom = WN+np.array([-27., 0.])
    s(tuple(N), [(p(N, 11, 1), p(S, 2, -2), p(S, 9, 6)),
                 (p(WN, 18, -28), p(WN, -4, -11), tuple(shirt_bottom)),
                 (p(shirt_bottom, -9, -4), p(shirt_bottom, -16, -10), p(shirt_bottom, -15, -18)),
                 (p(N, -26, 33), p(N, -11, 10), tuple(N))], '#141c27')
    s(p(N, -1, 14), [(p(N, 9, 21), p(S, -3, 4), p(S, 3, -1)),
                     (p(N, 16, 31), p(shirt_bottom, 22, -16), p(shirt_bottom, 6, -18)),
                     (p(shirt_bottom, 0, -21), p(shirt_bottom, -4, -25), p(shirt_bottom, -4, -29)),
                     (p(N, -17, 27), p(N, -8, 18), p(N, -1, 14))], '#34424e', None)
    t(p(N, 1, 16), [(p(N, 9, 24), p(S, -2, 7), p(S, 2, 3))], '#c2d0db', 1.35)
    pendant = N+np.array([-11+1.2*math.sin(pose['phase']-.5), 39.])
    crown(a, *pendant)
    # Narrow far lapel: anchored at the neck and waist rather than bitmap warped.
    lapel = B+np.array([21., -2.])
    lapel_end = WF+np.array([20., -13.])
    s(tuple(lapel), [(p(lapel, 6, 4), p(lapel, 12, 12), p(lapel, 11, 19)),
                     (p(lapel, 1, 43), p(lapel_end, 12, -15), tuple(lapel_end)),
                     (p(lapel_end, -4, 1), p(lapel_end, -8, -3), p(lapel_end, -10, -6)),
                     (p(lapel, -21, 50), p(lapel, -7, 20), tuple(lapel))], '#323d49')
    t(p(lapel, 5, 4), [(p(lapel, 9, 9), p(lapel, 12, 15), p(lapel, 11, 19)),
                       (p(lapel, 1, 43), p(lapel_end, 12, -15), tuple(lapel_end)),
                       (p(lapel_end, -2, 0), p(lapel_end, -5, -1), p(lapel_end, -7, -3))], '#dde7ed', 1.45)
    t(p(lapel, 3, 26), [(p(lapel, -7, 47), p(lapel_end, 5, -12), p(lapel_end, -5, -6))], '#7e94a5', .65)
    # Near jacket opening bows with shoulder motion and lower-chest compression.
    t(p(S, 9, 7), [(p(S, -3, 31), p(WN, -4, -10), tuple(shirt_bottom)),
                   (p(shirt_bottom, -9, 4), p(WF, 14, 0), p(WF, 9, -4))], '#dce6ec', 1.6)
    t(p(S, 5, 14), [(p(S, -9, 34), p(WN, -6, -8), p(shirt_bottom, 1, -4))], '#758b9b', .65)
    metal(a, [p(S, -7, 25), p(S, -20, 38), p(shirt_bottom, 15, -10)])
    # Small lower jacket lining and load-dependent folds.
    lining = shirt_bottom+np.array([-7., -9.])
    s(tuple(lining), [(p(lining, 7, 5), p(lining, 16, 4), p(lining, 25, -2)),
                      (p(lining, 22, 7), p(lining, 14, 12), p(lining, 6, 13)),
                      (p(lining, -3, 13), p(lining, -9, 8), p(lining, -13, 3)),
                      (p(lining, -7, 6), p(lining, -3, 3), tuple(lining))], '#a51e27')
    t(p(lining, -3, 8), [(p(lining, 3, 11), p(lining, 14, 8), p(lining, 18, 5))], '#e84a38', 1)
    t(p(WF, 12, -12), [(p(WF, 19, -9-compression), p(WF, 26, -9), p(WF, 34, -11))], '#697b88', .6)
    t(p(WF, 17, -7), [(p(WF, 22, -5+compression), p(WF, 28, -5), p(WF, 34, -7))], '#253441', .9)
    t(p(WF, -2, -1), [(p(WF, 16, 9), p(WN, -21, 8), tuple(WN))], '#e9b62c', 3.1)
    t(p(WF, 2, 1), [(p(WF, 17, 8), p(WN, -23, 7), p(WN, -11, 5))], '#ffe274', .85)
    im = a.finish()
    pixels = np.array(im)
    rgb = pixels[:, :, :3].astype(float)
    yy, xx = np.indices(pixels.shape[:2])
    light_center = (B+N)/2+np.array([-10., 19.])
    fabric = (pixels[:, :, 3] > 0) & (rgb.min(2) > 23) & (rgb.max(2) < 115) & (rgb.max(2)-rgb.min(2) < 40)
    glow = 4*np.exp(-((xx-light_center[0])/26)**2-((yy-light_center[1])/37)**2)
    rgb[fabric] += glow[fabric, None]
    pixels[:, :, :3] = np.clip(rgb, 0, 255).astype('uint8')
    return Image.fromarray(pixels, 'RGBA')


def waist_cloth(pose):
    """Folded red KH2 waist cloth, with the source's single crossing straps."""
    a = Art()
    bob, lag = pose['bob'], pose['cloth_lag']
    def p(x, y, amount=0):
        return (x+amount*lag, y+bob+amount*lag*.45)
    # A pointed folded silhouette matches the original, rather than two ovals.
    a.shape(p(279, 239), [(p(262, 233), p(245, 221, .25), p(232, 214, .4)),
                          (p(221, 221, .55), p(205, 231, .85), p(197, 242, 1)),
                          (p(191, 248, 1), p(196, 253, 1), p(205, 257, 1)),
                          (p(215, 265, .85), p(223, 269, .75), p(234, 265, .65)),
                          (p(250, 261, .4), p(270, 251, .1), p(279, 244)),
                          (p(280, 242), p(280, 240), p(279, 239))], '#bc1b25', '#27161d', 1.7)
    a.shape(p(230, 219, .45), [(p(221, 224, .6), p(210, 232, .8), p(203, 242, 1)),
                              (p(213, 239, .8), p(230, 232, .45), p(245, 235, .25)),
                              (p(242, 229, .25), p(235, 222, .35), p(230, 219, .45))], '#df3029', None)
    a.shape(p(227, 239, .6), [(p(216, 242, .8), p(207, 248, 1), p(207, 254, 1)),
                              (p(216, 263, .85), p(232, 266, .7), p(244, 259, .5)),
                              (p(261, 253, .15), p(274, 245), p(276, 241)),
                              (p(251, 243, .2), p(238, 239, .45), p(227, 239, .6))], '#d62525', None)
    a.shape(p(198, 244, 1), [(p(199, 251, 1), p(214, 263, .85), p(222, 264, .75)),
                            (p(220, 260, .8), p(215, 256, .85), p(214, 251, .9)),
                            (p(212, 247, .9), p(205, 245, .95), p(198, 244, 1))], '#871923', None)
    # Two crossing reinforcement straps, as on the source waist cloth.
    a.stroke(p(198, 246, 1), [(p(216, 241, .7), p(242, 238, .3), p(277, 240))], '#181b22', 4.5)
    a.stroke(p(231, 219, .45), [(p(226, 228, .5), p(223, 251, .7), p(221, 264, .8))], '#181b22', 5)
    a.stroke(p(200, 248, 1), [(p(218, 243, .7), p(243, 240, .3), p(258, 241, .1))], '#3c2d2c', .6)
    a.stroke(p(228, 223, .5), [(p(225, 235, .6), p(222, 254, .75), p(222, 260, .8))], '#44312f', .6)
    a.stroke(p(232, 215, .4), [(p(226, 215, .45), p(219, 219, .55), p(216, 222, .6))], '#4f1b23', 1.4)
    a.stroke(p(216, 257, .9), [(p(225, 267, .75), p(238, 264, .6), p(244, 260, .5))], '#ec4934', .85)
    a.stroke(p(245, 242, .25), [(p(253, 244, .15), p(258, 245, .1), p(262, 244, .05))], '#f3543b', .65)
    return a.finish()


def holding_skin(start, elbow, wrist):
    """Tapered upper arm/forearm with an underlap into the approved wrist cuff."""
    a = Art()
    start, elbow, wrist = [np.array(p, float) for p in [start, elbow, wrist]]
    wrist = wrist+(wrist-elbow)/np.linalg.norm(wrist-elbow)*3
    upper_axis, fore_axis = elbow-start, wrist-elbow
    n1 = np.array([-upper_axis[1], upper_axis[0]])/np.linalg.norm(upper_axis)
    n2 = np.array([-fore_axis[1], fore_axis[0]])/np.linalg.norm(fore_axis)
    def p(v):
        return tuple(v)
    s, t = a.shape, a.stroke
    s(p(start+n1*7.5), [(p(start+upper_axis*.4+n1*8), p(elbow+n1*8.5), p(elbow+n1*5)),
                        (p(elbow+fore_axis*.2+n2*7.3), p(wrist+n2*6), p(wrist+n2*5.8)),
                        (p(wrist+n2*3), p(wrist-n2*3), p(wrist-n2*5.8)),
                        (p(wrist-fore_axis*.5-n2*6.3), p(elbow-n1*7), p(elbow-n1*6.8)),
                        (p(elbow-upper_axis*.5-n1*7.6), p(start-n1*7), p(start-n1*7)),
                        (p(start-n1*3), p(start+n1*3), p(start+n1*7.5))], '#edb18a', '#452d25', 1.2)
    s(p(start+n1*4.8), [(p(start+upper_axis*.45+n1*5), p(elbow+n1*4.5), p(elbow+n1*2)),
                         (p(elbow+fore_axis*.3+n2*3), p(wrist+n2*3), p(wrist+n2*3)),
                         (p(wrist+n2*.3), p(wrist-n2*1), p(wrist-n2*1)),
                         (p(elbow+fore_axis*.4), p(elbow-n1*2), p(elbow-n1*2)),
                         (p(start+upper_axis*.5+n1*1), p(start+n1*3), p(start+n1*4.8))], '#ffd0a1', None)
    t(p(start-n1*5.5), [(p(start+upper_axis*.5-n1*5.8), p(elbow-n1*5.6), p(elbow-n1*4)),
                        (p(elbow+fore_axis*.3-n2*4), p(wrist-n2*4), p(wrist-n2*3))], '#bd7d5e', 2.2)
    t(p(elbow+n1*1), [(p(elbow+fore_axis*.1), p(elbow+fore_axis*.2), p(elbow+fore_axis*.25))], '#cb8c6a', .7)
    return a.finish()


def moving_chain(pommel, phase):
    """Keep the pommel attachment fixed while the pendant trails slightly."""
    a = Art()
    px, py = pommel
    sway = 3.2*(math.sin(phase-.45)-math.sin(-.45))
    for i in range(8):
        t = i/7
        x, y = px-6*t*t+sway*t**1.5, py+3+i*3.8
        if i % 2:
            a.ellipse((x-1, y-2.5, x+1, y+2.5), '#8394a3', '#25303a', .5)
            a.stroke((x-.4, y-1.5), [((x-.4, y-.5), (x-.4, y+.5), (x-.4, y+1.5))], '#dae0e5', .5)
        else:
            a.ellipse((x-2, y-2.7, x+2, y+2.7), None, '#b9c4cd', .8)
    cx, cy = px-6+sway, py+37
    a.ellipse((cx-10, cy-8, cx-1, cy+1), '#aab9c7', '#17232d', .9)
    a.ellipse((cx+1, cy-8, cx+10, cy+1), '#aab9c7', '#17232d', .9)
    a.ellipse((cx-6, cy-3, cx+6, cy+9), '#aab9c7', '#17232d', 1)
    a.ellipse((cx-4, cy-2, cx+1, cy+3), '#d5dfe6')
    return a.finish(), [cx, cy], sway
