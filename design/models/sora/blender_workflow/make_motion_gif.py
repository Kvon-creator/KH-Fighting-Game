"""Preview GIFs on white for a 2D sprite version, optionally travelling by its root motion.

Run: python make_motion_gif.py <version> <out.gif> [--travel] [--cycles N]
Holds come from the version's game_frames_60fps; root motion (m) is converted at 512 px scale.
Plain Python + Pillow; reads only the version's frames and report.
"""
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
assert (ROOT / 'KingdomArena/project.godot').is_file(), ROOT  # project root (any clone)
version, out_name = sys.argv[1], sys.argv[2]
travel = '--travel' in sys.argv
cycles = int(sys.argv[sys.argv.index('--cycles') + 1]) if '--cycles' in sys.argv else 3
OUT = ROOT / 'design/models/sora' / version
rep = json.loads((OUT / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
holds = rep['game_frames_60fps']
root = rep.get('root_motion_m') or [0]*len(holds)
px_per_m = 180.5 * 512 / 384
frames = [Image.open(OUT / 'frames_512' / f['filename']).convert('RGBA') for f in rep['frames']]
width = 512 + (int(sum(root)*px_per_m*cycles) + 40 if travel else 0)
x, imgs, durs = 0.0, [], []
for _ in range(cycles):
    for im, h, m in zip(frames, holds, root):
        x += m*px_per_m if travel else 0
        bg = Image.new('RGBA', (width, 512), (255, 255, 255, 255))
        bg.alpha_composite(im, (int(round(x)), 0))
        imgs.append(bg.convert('RGB')); durs.append(max(20, round(h*1000/60/10)*10))
imgs[0].save(OUT / out_name, save_all=True, append_images=imgs[1:], duration=durs, loop=0)
print('GIF_OK', out_name, len(imgs), sum(durs), 'ms', 'width', width)
