"""Package the corrected eight-pose loop carry for offline visual review."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
LOOP = READY/'run_loop'
L = LOOP/'layers'
OUT = LOOP/'review_cycle_v2'
OUT.mkdir(parents=True, exist_ok=True)
images, records = [], []
master_hashes, grip_hashes = set(), set()
for i in range(8):
    source_dir = L/f'frame_{i:02d}_review_v2'
    path = source_dir/f'sora_run_loop_{i:02d}_review.png'
    m = json.loads((source_dir/'manifest.json').read_text(encoding='utf-8'))
    im = Image.open(path).convert('RGBA')
    visible = np.argwhere(np.array(im.getchannel('A')) > 32)
    # Register the retained repair-plate pelvis estimate. Gait/root trajectory
    # remains review work; no scaling or new pose is produced by packaging.
    offset_x = m.get('body_reconstruction_offset', [0, 0])[0]
    hip_x = 278+offset_x
    dx, dy = 280-hip_x, 432-int(visible[:, 0].max())-1
    aligned = Image.new('RGBA', (512, 512))
    aligned.paste(im, (dx, dy))
    assert np.count_nonzero(np.array(aligned.getchannel('A')) > 32) == len(visible), (i, dx, dy)
    name = f'sora_run_loop_{i:02d}.png'
    save_clean(aligned, OUT/name)
    images.append(aligned)
    T = np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]])
    H = np.array(m['master_to_screen_homography'])
    records.append({'index': i, 'path': name, 'duration_ms': 100,
                    'source': str(path.relative_to(LOOP)),
                    'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'estimated_pelvis_x': hip_x, 'translation_xy': [dx, dy], 'scale': 1,
                    'master_to_export_homography': (T @ H).tolist(),
                    'physical_master_length_px': 285})
    master_hashes.add(m['weapon_master_sha256'])
    grip_hashes.add(m['grip_master_sha256'])
assert len(master_hashes) == len(grip_hashes) == 1

sheet = Image.new('RGBA', (2048, 1024))
board = Image.new('RGB', (1024, 600), '#202633')
mirror = Image.new('RGB', (1024, 320), '#202633')
bd, md = ImageDraw.Draw(board), ImageDraw.Draw(mirror)
flat = []
for i, im in enumerate(images):
    sheet.paste(im, ((i % 4)*512, (i // 4)*512))
    x, y = (i % 4)*256, (i // 4)*300
    small = im.resize((256, 256), Image.Resampling.LANCZOS)
    board.paste(small, (x, y+30), small)
    bd.text((x+10, y+10), f'Loop {i:02d} / overlap review', fill='white')
    bd.line((x, y+246, x+255, y+246), fill='#566270')
    for row, current in enumerate([im, im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):
        game = current.resize((128, 128), Image.Resampling.LANCZOS)
        mirror.paste(game, (i*128, row*160+24), game)
        md.text((i*128+8, row*160+6), f'{i:02d}', fill='white')
    bg = Image.new('RGB', im.size, '#202633')
    bg.paste(im, (0, 0), im)
    flat.append(bg)
sheet.save(OUT/'sora_run_loop_sheet.png')
board.save(OUT/'Contact_Sheet.png')
mirror.save(OUT/'Game_Size_Mirrored_Review.png')
flat[0].save(OUT/'sora_run_loop_preview.gif', save_all=True, append_images=flat[1:],
             duration=100, loop=0, disposal=2)

start_path = READY/'run_start/refinement_v4/review_cycle_v2/sora_run_start_07.png'
start = Image.open(start_path).convert('RGBA')
seam = Image.new('RGB', (1024, 710), '#202633')
sd = ImageDraw.Draw(seam)
for i, (im, label) in enumerate([(start, 'Start 07'), (images[0], 'Revised loop 00')]):
    seam.paste(im, (i*512, 28), im)
    sd.text((i*512+12, 8), label, fill='white')
    sd.line((i*512, 460, (i+1)*512-1, 460), fill='#566270')
    game = im.resize((128, 128), Image.Resampling.LANCZOS)
    seam.paste(game, (i*512+192, 564), game)
sd.text((12, 526), 'Carry overlap now agrees. Body pitch and rear-leg transition still need refinement.', fill='white')
seam.save(OUT/'Start_Loop_Seam_Review.png')
seam_flat = []
for im in [start, images[0]]:
    bg = Image.new('RGB', im.size, '#202633')
    bg.paste(im, (0, 0), im)
    seam_flat.append(bg)
seam_flat[0].save(OUT/'start_loop_seam_review.gif', save_all=True,
                  append_images=seam_flat[1:], duration=350, loop=0, disposal=2)

(OUT/'manifest.json').write_text(json.dumps({
    'status': 'eight-pose carry-overlap review; art/gait/seams unfinished',
    'canvas': [512, 512], 'floor_y': 432, 'review_root_x': 280, 'frames': records,
    'registration': 'repair-plate pelvis estimate and foot baseline; translation only',
    'shared_weapon_master_sha256': next(iter(master_hashes)),
    'shared_grip_master_sha256': next(iter(grip_hashes)),
    'limitations': ['Same rigid carry overlap across eight existing poses, not new gait approval.',
                    'Shared garment motifs and arm anatomy still need individual refinement.',
                    'Pelvis registration, flight offsets, timing and alternating gait need review.',
                    'Start07 to loop00 body pitch/rear-leg transition remains unfinished.',
                    'No protected engine changes, Godot test or aerial artwork.']}, indent=2), encoding='utf-8')
(OUT/'README.md').write_text(
    '# Eight-pose run-loop overlap review\n\n'
    'Each pose uses its existing body/head plates, with the rigid shaft behind the '
    'head and torso and the connected guard/corrected grip in front. Weapon projections '
    'and grip drawings are unchanged. Frame00 also preserves the exact approved hand/cuff '
    'region. Pose manifests record the exact lower-body preservation region. Original '
    'sheets, prior review images and review_cycle_v1 remain.\n\n'
    'Exports apply translation only to a preliminary pelvis estimate and foot baseline '
    'y432. This aligns the artwork for review; it does not finalize root movement or '
    'flight phases. Shared garment repairs, arm anatomy, gait and timing still require '
    'refinement against idle quality.\n\n'
    'The seam board/GIF compares final start pose07 with revised loop00. Carry overlap '
    'now uses the same rule; body pitch and rear-leg motion still differ. No image '
    'generation retries, protected engine edits or aerial production.\n', encoding='utf-8')
for rec in records:
    Image.open(OUT/rec['path']).verify()
    a = np.array(Image.open(OUT/rec['path']))
    assert np.all(a[a[:, :, 3] == 0, :3] == 0)
assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in images}) == 8
for name, expected_count in [('sora_run_loop_preview.gif', 8), ('start_loop_seam_review.gif', 2)]:
    gif = Image.open(OUT/name)
    assert gif.n_frames == expected_count
    for frame in range(gif.n_frames):
        gif.seek(frame)
        gif.load()
assert hashlib.sha256((LOOP/'run_loop_source.png').read_bytes()).hexdigest() == \
    '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
print('Verified eight corrected loop poses, shared masters, eight GIF frames and seam preview.', OUT)
print('Review translations:', [rec['translation_xy'] for rec in records])
