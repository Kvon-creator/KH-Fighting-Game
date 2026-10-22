"""Package a rendered 3D idle loop: sprite sheet, looping GIFs and an approved-idle comparison.

Plain Python with Pillow (not Blender). Reads <version>/Idle_Loop_Report.json and its frames;
never modifies the frames or the approved sprites.
Run: python package_idle_loop.py idle_loop_v2
"""
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
OUT = ROOT / 'design/models/sora' / sys.argv[1]
APPROVED = ROOT / 'design/sprites/smooth/sora/replacement_work/ready/standing_idle'
report = json.loads((OUT / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
frames = [Image.open(OUT / 'frames_512' / f['filename']).convert('RGBA') for f in report['frames']]
durations = [f['duration_ms'] for f in report['frames']]
BG = (46, 52, 64, 255)  # same opaque dark blue-gray preview ground as the approved idle


def on_bg(im, color=BG):
    ground = Image.new('RGBA', im.size, color); ground.alpha_composite(im)
    return ground.convert('RGB')


# Sprite sheet: 5 x 2, row-major, transparent, matching the approved sheet layout.
sheet = Image.new('RGBA', (512*5, 512*2), (0, 0, 0, 0))
for i, im in enumerate(frames):
    sheet.alpha_composite(im, ((i % 5)*512, (i // 5)*512))
sheet.save(OUT / 'sora_idle3d_sheet.png')

# Looping previews at full and game size (GIF has no partial alpha, so use the preview ground).
on_bg(frames[0]).save(OUT / 'sora_idle3d_preview.gif', save_all=True, append_images=[on_bg(f) for f in frames[1:]],
                      duration=durations, loop=0, disposal=1)
small = [Image.open(OUT / 'frames_128' / f['filename']).convert('RGBA').resize((256, 256), Image.NEAREST)
         for f in report['frames']]
on_bg(small[0]).save(OUT / 'sora_idle3d_128_x2.gif', save_all=True, append_images=[on_bg(f) for f in small[1:]],
                     duration=durations, loop=0, disposal=1)

# Side-by-side: approved idle (left) and 3D render (right), each with its own frame timing.
approved = json.loads((APPROVED / 'sora_stand_idle_manifest.json').read_text(encoding='utf-8-sig'))
a_frames = [Image.open(APPROVED / f['filename']).convert('RGBA') for f in approved['frames']]
a_durations = [f['duration_ms'] for f in approved['frames']]
events = sorted({sum(a_durations[:i]) for i in range(len(a_durations))} | {sum(durations[:i]) for i in range(len(durations))})
total = max(sum(a_durations), sum(durations)); events.append(total)


def at(t, seq, durs):
    t %= sum(durs); acc = 0
    for im, d in zip(seq, durs):
        if t < acc + d:
            return im
        acc += d
    return seq[-1]


pairs, pair_durs = [], []
for start, end in zip(events, events[1:]):
    canvas = Image.new('RGBA', (1040, 512), BG)
    canvas.alpha_composite(at(start, a_frames, a_durations), (0, 0))
    canvas.alpha_composite(at(start, frames, durations), (528, 0))
    pairs.append(canvas.convert('RGB')); pair_durs.append(end - start)
pairs[0].save(OUT / 'Approved_vs_3D_idle.gif', save_all=True, append_images=pairs[1:], duration=pair_durs, loop=0)

# Verify what was written.
checks = {}
for name, expect in (('sora_idle3d_preview.gif', durations), ('sora_idle3d_128_x2.gif', durations),
                     ('Approved_vs_3D_idle.gif', pair_durs)):
    gif = Image.open(OUT / name); got = []
    for k in range(gif.n_frames):
        gif.seek(k); got.append(gif.info.get('duration'))
    # GIF stores delays in 10 ms units, so 55 ms frames are written as 50 or 60 ms.
    close = len(got) == len(expect) and all(g is not None and abs(g - e) <= 5 for g, e in zip(got, expect))
    checks[name] = {'frames': gif.n_frames, 'durations_match': close, 'loop': gif.info.get('loop')}
alpha = [im.getchannel('A').getbbox() for im in frames]
checks['frames_512'] = {'count': len(frames), 'sizes_ok': all(im.size == (512, 512) for im in frames),
                        'lowest_opaque_row': max(b[3] for b in alpha) - 1, 'distinct': len({im.tobytes() for im in frames})}
(OUT / 'Package_QA.json').write_text(json.dumps(checks, indent=2) + '\n', encoding='utf-8')
print('PACKAGE_OK', json.dumps(checks))
