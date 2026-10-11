"""Read-only inspection of new complete-image generation trials."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image
import numpy as np
from inspect_flat_run_batch import components

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r"D:\KH Fighting Game".lower(), ROOT
parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()
path = (ROOT / args.path).resolve()
path.relative_to(ROOT)  # Raises if the resolved file escapes the workspace.
with Image.open(path) as image:
    alpha = image.getchannel("A") if "A" in image.getbands() else None
    counts = alpha.histogram() if alpha is not None else None
    all_components = components(np.asarray(alpha)) if alpha is not None else []
    main = sorted(all_components, reverse=True)[:12]
    frames = []
    if len(main) == 12 and min(component[0] for component in main) > 7000:
        assigned = {component[1]: [] for component in main}
        for component in all_components:
            if component in main:
                continue
            x0, y0, x1, y1 = component[1]
            cx, cy = (x0+x1)/2, (y0+y1)/2
            def distance(body):
                a,b,c,d = body[1]
                return max(a-cx,0,cx-c)**2 + max(b-cy,0,cy-d)**2 + .015*((a+c)/2-cx)**2 + .015*((b+d)/2-cy)**2
            owner = min(main, key=distance)
            assigned[owner[1]].append(component)
        rgba = np.asarray(image)
        for area, body in main:
            parts = [(area, body)] + assigned[body]
            x0 = max(0, min(part[1][0] for part in parts)-2)
            y0 = max(0, min(part[1][1] for part in parts)-2)
            x1 = min(image.width, max(part[1][2] for part in parts)+2)
            y1 = min(image.height, max(part[1][3] for part in parts)+2)
            row = min(2, int(((body[1]+body[3])/2)*3/image.height))
            col = min(3, int(((body[0]+body[2])/2)*4/image.width))
            core = np.asarray(alpha)[y0:y1,x0:x1] > 100
            assert np.count_nonzero(core) - sum(part[0] for part in parts) <= 8, (row*4+col, 'Neighbor artwork inside crop')
            eye_start = x0+int((x1-x0)*.65)
            eye = rgba[y0:y0+int((y1-y0)*.5), eye_start:x1]
            blue = ((eye[:,:,3]>128)&(eye[:,:,0]<220)&(eye[:,:,1]>80)&(eye[:,:,2]>100)&(eye[:,:,2]>eye[:,:,1]*1.05)&(eye[:,:,2]>eye[:,:,0]*1.15))
            ey, ex = np.nonzero(blue)
            eye_x = eye_start+float(np.median(ex)) if len(ex)>2 else x0+(x1-x0)*.72
            frames.append(dict(index=row*4+col, bounds=[x0,y0,x1,y1], area=area,
                               nativeEyeX=eye_x, blueEyePixels=int(len(ex)),
                               edgeClippingRisk=x0==0 or y0==0 or x1==image.width or y1==image.height))
        frames.sort(key=lambda frame:frame['index'])
        assert [frame['index'] for frame in frames] == list(range(12)), 'One whole figure per cell not established'
    print(json.dumps(dict(path=str(path), size=image.size, mode=image.mode,
                         alphaExtrema=alpha.getextrema() if alpha else None,
                         transparentPixelCount=counts[0] if counts else 0,
                         nonopaquePixelCount=sum(counts[:255]) if counts else 0,
                         nearlyOpaquePixelCount=sum(counts[240:]) if counts else 0,
                         completeFigureFrames=frames,
                         rgbaProbes={str(point): image.getpixel(point) for point in
                                     [(0, 0), (256, 64), (240, 105), (150, 160), (250, 300), (380, 340)]},
                         fileSha256=hashlib.sha256(path.read_bytes()).hexdigest()), indent=2))
