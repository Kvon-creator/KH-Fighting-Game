"""Small offline drawing utilities for local Sora pose refinements."""
import math

import numpy as np
from PIL import Image, ImageDraw


class Art:
    def __init__(self, size=(512, 512), scale=4):
        self.size, self.scale = size, scale
        self.image = Image.new('RGBA', tuple(v*scale for v in size))

    def points(self, start, segments):
        points = [start]
        a = start
        for b, c, end in segments:
            for j in range(1, 33):
                t, u = j/32, 1-j/32
                points.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],
                               u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
            a = end
        return [(round(x*self.scale), round(y*self.scale)) for x, y in points]

    def shape(self, start, segments, color, outline='#14171d', width=1.5):
        points = self.points(start, segments)
        d = ImageDraw.Draw(self.image)
        d.polygon(points, fill=color)
        if outline:
            d.line(points+points[:1], fill=outline, width=round(width*self.scale), joint='curve')

    def stroke(self, start, segments, color, width=1.2):
        ImageDraw.Draw(self.image).line(self.points(start, segments), fill=color,
                                      width=round(width*self.scale), joint='curve')

    def ellipse(self, box, color, outline=None, width=1):
        ImageDraw.Draw(self.image).ellipse(tuple(round(v*self.scale) for v in box), fill=color,
                                         outline=outline, width=round(width*self.scale))

    def finish(self):
        return self.image.resize(self.size, Image.Resampling.LANCZOS)


def carry(master_dir, hand, angle, yaw_degrees, size=(512, 512)):
    """One projection of fixed master geometry; split only for body occlusion."""
    theta, yaw = math.radians(angle), math.radians(yaw_degrees)
    c, s = math.cos(theta), math.sin(theta)
    H = (np.array([[c, -s, hand[0]], [s, c, hand[1]], [0, 0, 1]])
         @ np.array([[math.cos(yaw), 0, 0], [0, 1, 0], [-math.sin(yaw)/1400, 0, 1]])
         @ np.array([[1, 0, -77], [0, 1, -70], [0, 0, 1]]))
    inverse = np.linalg.inv(H)
    inverse /= inverse[2, 2]

    def transform(im):
        return im.transform(size, Image.Transform.PERSPECTIVE,
                            tuple(inverse.flatten()[:8]), Image.Resampling.BICUBIC)

    def project(p):
        q = H @ np.array([p[0], p[1], 1])
        return (q[:2]/q[2]).tolist()

    master = Image.open(master_dir/'kingdom_key_master_finished.png').convert('RGBA')
    front_mask = Image.new('L', master.size)
    ImageDraw.Draw(front_mask).rectangle((0, 0, 141, master.height), fill=255)
    front = master.copy()
    front.putalpha(Image.composite(master.getchannel('A'), Image.new('L', master.size), front_mask))
    grip = Image.open(master_dir/'grip_master_space.png').convert('RGBA')
    anchors = {name: project(p) for name, p in {'grip': (77, 70), 'pommel': (34, 70),
               'collar': (137, 70), 'tip': (319, 70)}.items()}
    assert np.allclose(anchors['grip'], hand)
    assert abs(float(np.cross(np.array(anchors['tip'])-anchors['collar'],
                              np.array(anchors['collar'])-anchors['grip']))) < 1e-6
    chain_art = Art(size)
    px, py = anchors['pommel']
    for i in range(8):
        t = i/7
        x, y = px-6*t*t, py+3+i*3.8
        if i % 2:
            chain_art.ellipse((x-1, y-2.5, x+1, y+2.5), '#8394a3', '#25303a', .5)
            chain_art.stroke((x-.4, y-1.5), [((x-.4, y-.5), (x-.4, y+.5), (x-.4, y+1.5))], '#dae0e5', .5)
        else:
            chain_art.ellipse((x-2, y-2.7, x+2, y+2.7), None, '#b9c4cd', .8)
    cx, cy = px-6, py+37
    chain_art.ellipse((cx-10, cy-8, cx-1, cy+1), '#aab9c7', '#17232d', .9)
    chain_art.ellipse((cx+1, cy-8, cx+10, cy+1), '#aab9c7', '#17232d', .9)
    chain_art.ellipse((cx-6, cy-3, cx+6, cy+9), '#aab9c7', '#17232d', 1)
    chain_art.ellipse((cx-4, cy-2, cx+1, cy+3), '#d5dfe6')
    return transform(master), transform(front), transform(grip), chain_art.finish(), H, anchors


def save_clean(im, path):
    pixels = np.array(im)
    pixels[pixels[:, :, 3] == 0, :3] = 0
    Image.fromarray(pixels, 'RGBA').save(path)
