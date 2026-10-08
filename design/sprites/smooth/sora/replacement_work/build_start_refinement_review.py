"""Package only the individually refined start poses; preserve artwork scale."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
START = ROOT/'ready/run_start'
OUT = START/'refinement_v3/review_sequence'
OUT.mkdir(parents=True, exist_ok=True)
inputs = [START/'refinement_v2/sora_run_start_00.png'] + [
    START/'refinement_v3'/f'sora_run_start_{i:02d}.png' for i in range(1, 5)]
inputs[2] = START/'refinement_v4/sora_run_start_02.png'
records, images = [], []
for i, path in enumerate(inputs):
    im = Image.open(path).convert('RGBA')
    alpha = np.array(im.getchannel('A'))
    # Baseline for these grounded poses only. No scale or anatomical warping.
    visible = np.argwhere(alpha > 32)
    bottom = int(visible[:, 0].max())+1
    dy = 432-bottom
    aligned = Image.new('RGBA', (512, 512))
    aligned.paste(im, (0, dy))
    name = f'sora_run_start_{i:02d}.png'
    save_clean(aligned, OUT/name)
    images.append(aligned)
    rec = {'index': i, 'path': name, 'source': str(path.relative_to(START)),
           'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'translation_xy': [0, dy], 'scale': 1, 'contact_floor_y': 432}
    pose_manifest = path.parent/f'frame_{i:02d}_manifest.json'
    if pose_manifest.exists():
        data = json.loads(pose_manifest.read_text(encoding='utf-8'))
        if 'master_to_screen_homography' in data:
            H = np.array(data['master_to_screen_homography'])
            T = np.array([[1, 0, 0], [0, 1, dy], [0, 0, 1]])
            rec['master_to_export_homography'] = (T @ H).tolist()
    records.append(rec)

sheet = Image.new('RGBA', (512*5, 512))
strip = Image.new('RGB', (256*5, 300), '#202633')
d = ImageDraw.Draw(strip)
for i, im in enumerate(images):
    sheet.paste(im, (i*512, 0))
    small = im.resize((256, 256), Image.Resampling.LANCZOS)
    strip.paste(small, (i*256, 30), small)
    d.text((i*256+12, 10), f'Run start {i:02d}', fill='white')
    d.line((i*256, 246, (i+1)*256-1, 246), fill='#566270')
sheet.save(OUT/'sora_run_start_first_five_sheet.png')
strip.save(OUT/'Run_Start_First_Five.png')

gif_frames = []
for im in images:
    bg = Image.new('RGB', im.size, '#202633')
    bg.paste(im, (0, 0), im)
    gif_frames.append(bg)
gif_frames[0].save(OUT/'sora_run_start_partial_preview.gif', save_all=True,
                   append_images=gif_frames[1:], duration=[220, 120, 120, 120, 350],
                   loop=0, disposal=2)
manifest = {'status': 'partial five-frame art review, not a complete run-start animation',
            'frames': records, 'canvas': [512, 512], 'floor_y': 432,
            'method': 'translation only; genuine source articulation retained',
            'limitations': ['Frames 05-07 still await individual redraw.',
                            'Earlier arm/garment repairs still need idle-quality comparison.',
                            'Idle endpoint retains its original weapon; rigid-master seam is pending.',
                            'Timing, root motion, and transition into run loop are unfinished.',
                            'Floor alignment is an offline review aid, not gameplay integration.']}
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
(OUT/'README.md').write_text(
    '# Partial run-start review\n\n'
    'Only frames 00-04 are included. This is an art comparison, not the complete animation. '
    'The preview restarts after frame 04. Frames 05-07 need individual repair before full-cycle review.\n\n'
    'Frame 00 is the approved idle endpoint. Frames 01-04 retain their genuine source body '
    'articulation and use local redraws plus the fixed rigid weapon and approved grip. '
    'These review exports apply only vertical translation to put grounded feet at y432; '
    'individual repair files and layers remain in their original working coordinates.\n\n'
    'The new frames improve carry and garment construction, but running has not yet reached '
    'idle quality. The approved idle endpoint still retains its original weapon. Earlier '
    'arm repairs, garment consistency, timing and weapon/run-loop seams still '
    'need work. No image generation, aerial artwork or engine changes.\n', encoding='utf-8')

for record in records:
    Image.open(OUT/record['path']).verify()
    export = np.array(Image.open(OUT/record['path']))
    assert np.all(export[export[:, :, 3] == 0, :3] == 0)
gif = Image.open(OUT/'sora_run_start_partial_preview.gif')
assert gif.n_frames == 5
for i in range(gif.n_frames):
    gif.seek(i)
    gif.load()
assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in images}) == 5
assert hashlib.sha256((START/'run_start_source.png').read_bytes()).hexdigest() == \
    '1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'
print('Verified partial review: 5 distinct PNGs, 5 GIF frames; translations:',
      [r['translation_xy'] for r in records])
