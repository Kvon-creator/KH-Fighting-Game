"""Eight genuine run-start poses, aligned for offline art/transition review."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
START = READY/'run_start'
OUT = START/'refinement_v4/review_cycle_v2'
OUT.mkdir(parents=True, exist_ok=True)
inputs = [START/'refinement_v2/sora_run_start_00.png',
          START/'refinement_v3/sora_run_start_01.png',
          START/'refinement_v4/sora_run_start_02.png']
inputs += [START/'refinement_v3'/f'sora_run_start_{i:02d}.png' for i in (3, 4)]
inputs += [START/'refinement_v4'/f'sora_run_start_{i:02d}.png' for i in (5, 6, 7)]
# Estimated pelvis centers in each working drawing. Pure translation stabilizes
# the review origin without deforming a head, body, limb, or weapon.
hip_x = [256, 255, 251, 254, 280, 272, 225, 278]
review_root_x = 280
records, images = [], []
for i, (path, hip) in enumerate(zip(inputs, hip_x)):
    im = Image.open(path).convert('RGBA')
    occupied = np.argwhere(np.array(im.getchannel('A')) > 32)
    bottom = int(occupied[:, 0].max())+1
    dx, dy = review_root_x-hip, 432-bottom
    aligned = Image.new('RGBA', (512, 512))
    aligned.paste(im, (dx, dy))
    # Ensure translation did not clip opaque artwork at any canvas boundary.
    assert np.count_nonzero(np.array(aligned.getchannel('A')) > 32) == len(occupied), (i, dx, dy)
    name = f'sora_run_start_{i:02d}.png'
    save_clean(aligned, OUT/name)
    images.append(aligned)
    rec = {'index': i, 'path': name, 'source': str(path.relative_to(START)),
           'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'estimated_pelvis_x': hip, 'translation_xy': [dx, dy], 'scale': 1,
           'review_floor_y': 432, 'timing_ms': 160 if i in (0, 7) else 100}
    pose_manifest = path.parent/f'frame_{i:02d}_manifest.json'
    if pose_manifest.exists():
        data = json.loads(pose_manifest.read_text(encoding='utf-8'))
        H = np.array(data['master_to_screen_homography'])
        T = np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]])
        rec['master_to_export_homography'] = (T @ H).tolist()
        rec['weapon_physical_master_length_px'] = 285
    records.append(rec)

sheet = Image.new('RGBA', (2048, 1024))
contact = Image.new('RGB', (1024, 600), '#202633')
cd = ImageDraw.Draw(contact)
for i, im in enumerate(images):
    sheet.paste(im, ((i % 4)*512, (i // 4)*512))
    x, y = (i % 4)*256, (i // 4)*300
    small = im.resize((256, 256), Image.Resampling.LANCZOS)
    contact.paste(small, (x, y+30), small)
    cd.text((x+10, y+10), f'Run start {i:02d}', fill='white')
    cd.line((x, y+246, x+255, y+246), fill='#566270')
sheet.save(OUT/'sora_run_start_sheet.png')
contact.save(OUT/'Contact_Sheet.png')

gif_frames = []
for im in images:
    bg = Image.new('RGB', im.size, '#202633')
    bg.paste(im, (0, 0), im)
    gif_frames.append(bg)
gif_frames[0].save(OUT/'sora_run_start_preview.gif', save_all=True,
                   append_images=gif_frames[1:], duration=[r['timing_ms'] for r in records],
                   loop=0, disposal=2)

# Inspect the transition into the current run-loop key pose. Do not silently
# append it to the start package or call a discontinuity finished.
loop_path = READY/'run_loop/layers/frame_00_review_v2/sora_run_loop_00_review.png'
loop = Image.open(loop_path).convert('RGBA')
visible = np.argwhere(np.array(loop.getchannel('A')) > 32)
loop_dy = 432-int(visible[:, 0].max())-1
loop_dx = review_root_x-278
loop_aligned = Image.new('RGBA', (512, 512))
loop_aligned.paste(loop, (loop_dx, loop_dy))
seam = Image.new('RGB', (1024, 710), '#202633')
sd = ImageDraw.Draw(seam)
for i, (im, title) in enumerate([(images[7], 'Start 07'), (loop_aligned, 'Current loop 00')]):
    seam.paste(im, (i*512, 30), im)
    sd.text((i*512+12, 9), title, fill='white')
    sd.line((i*512, 462, (i+1)*512-1, 462), fill='#566270')
    small = im.resize((128, 128), Image.Resampling.LANCZOS)
    seam.paste(small, (i*512+192, 554), small)
sd.text((12, 522), 'Carry overlap agrees. Body pitch and rear leg still need a transition pass.', fill='white')
seam.save(OUT/'Start_Loop_Seam_Review.png')
seam_frames = []
for im in [images[7], loop_aligned]:
    bg = Image.new('RGB', im.size, '#202633')
    bg.paste(im, (0, 0), im)
    seam_frames.append(bg)
seam_frames[0].save(OUT/'start_loop_seam_review.gif', save_all=True,
                    append_images=seam_frames[1:], duration=350, loop=0, disposal=2)

mirror = Image.new('RGB', (1024, 320), '#202633')
md = ImageDraw.Draw(mirror)
for i, im in enumerate(images):
    for row, current in enumerate([im, im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
        small = current.resize((128, 128), Image.Resampling.LANCZOS)
        mirror.paste(small, (i*128, row*160+24), small)
        md.text((i*128+8, row*160+6), f'{i:02d}', fill='white')
mirror.save(OUT/'Game_Size_Mirrored_Review.png')

background_review = Image.new('RGB', (1536, 1090), '#202633')
bd = ImageDraw.Draw(background_review)
for col, im in enumerate(images[5:]):
    for row, color in enumerate(['#202633', '#e1e2e4']):
        bg = Image.new('RGB', (512, 512), color)
        bg.paste(im, (0, 0), im)
        background_review.paste(bg, (col*512, row*545+28))
        bd.text((col*512+12, row*545+8), f'Stride {col+5:02d} / background review', fill='white')
background_review.save(OUT/'Stride_Dark_Light_Review.png')

manifest = {'status': 'complete eight-pose start art review; quality/timing/seams unfinished',
            'frames': records, 'canvas': [512, 512], 'floor_y': 432,
            'root_x': review_root_x, 'registration': 'estimated pelvis x and foot baseline; translation only',
            'loop_seam_reference': str(loop_path.relative_to(READY)),
            'loop_reference_translation_xy': [loop_dx, loop_dy],
            'limitations': ['New drawing set covers all start poses, but is not final animation approval.',
                            'Earlier repairs and clothing materials remain below idle detail.',
                            'Idle endpoint retains its original weapon; rigid-master blend is pending.',
                            'Start07/loop00 have different body pitch and rear-leg positions.',
                            'Root/flight trajectory, timing and gait need refinement before integration.',
                            'No Godot integration/test or aerial production.']}
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
(OUT/'README.md').write_text(
    '# Eight-pose run-start art review\n\n'
    'All eight start poses now have individual working artwork. Endpoint 00 is approved '
    'idle from v2; 01, 03 and 04 use v3; 02, 05, 06 and 07 use v4. Original sheets and '
    'earlier reviews remain untouched. This is a complete pose set for review, not final '
    'idle-quality artwork or gameplay integration.\n\n'
    'Frames 05-07 preserve actual source stride changes and use individually drawn arms '
    'and cloth repairs. The last source crop extends 27 pixels into the neighboring cell '
    'to recover its whole trailing shoe. Foreign shoe pixels are removed from frame 06. '
    'Only detached old-weapon fragments are filtered from the cleaned body plates; '
    'manifests list their locations. The rigid master and approved grip remain separate.\n\n'
    'Review exports apply translation only to estimated pelvis x280 and foot baseline '
    'y432. Raw working layers keep their original coordinates. Foot contact/flight offsets '
    'and root motion still need animation review. The GIF resets after frame 07.\n\n'
    'The separate seam board/GIF compares 07 with revised loop00. Carry overlap agrees; '
    'body pitch and rear-leg extension still differ, so this seam is pending. Clothing details, '
    'earlier start repairs and the idle weapon endpoint also need refinement. Running '
    'must reach idle quality before aerial artwork starts. No image-generation retries '
    'or protected engine edits.\n', encoding='utf-8')

for r in records:
    Image.open(OUT/r['path']).verify()
    a = np.array(Image.open(OUT/r['path']))
    assert np.all(a[a[:, :, 3] == 0, :3] == 0)
assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in images}) == 8
for name, count in [('sora_run_start_preview.gif', 8), ('start_loop_seam_review.gif', 2)]:
    gif = Image.open(OUT/name)
    assert gif.n_frames == count
    for i in range(gif.n_frames):
        gif.seek(i)
        gif.load()
assert hashlib.sha256((START/'run_start_source.png').read_bytes()).hexdigest() == \
    '1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'
assert hashlib.sha256((READY/'run_loop/run_loop_source.png').read_bytes()).hexdigest() == \
    '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
print('Verified full start review: 8 PNGs, 8 GIF frames, 2 seam GIF frames.', OUT)
