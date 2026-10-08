"""Fix loop00 carry overlap using retained local body/weapon layers.

No pose scaling, weapon registration change, or original-source replacement.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import save_clean, retain_main_body


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
L = READY/'run_loop/layers'
OUT = L/'frame_00_review_v2'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = READY/'run_loop/run_loop_source.png'
EXPECTED = '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
old_path = L/'frame_00_review_v1/sora_run_loop_00_review.png'
old_hash = hashlib.sha256(old_path.read_bytes()).hexdigest()
before = Image.open(old_path).convert('RGBA')
metadata = json.loads((L/'frame_00_review_v1/manifest.json').read_text(encoding='utf-8'))
H = np.array(metadata['master_to_screen_homography'])
inverse = np.linalg.inv(H)
inverse /= inverse[2, 2]
coefficients = tuple(inverse.flatten()[:8])

# Rebuild the body from plates, not by erasing the shaft from the finished PNG.
body = Image.open(L/'pilot_v3/body_clean_plate.png').convert('RGBA')
body_sources = [L/'pilot_v3/holding_arm.png',
                L/'art_pass_01/art_detail_overlay.png',
                L/'art_pass_02/jacket_volume_overlay.png',
                L/'art_pass_02/sleeve_glove_fold_overlay.png',
                L/'art_pass_03/chest_redraw_overlay.png',
                L/'art_pass_06/contact_and_arm_overlay.png',
                L/'pilot_v3/head_occlusion.png']
for path in body_sources:
    body = Image.alpha_composite(body, Image.open(path).convert('RGBA'))
pixels = np.array(body)
rgb = pixels[:, :, :3].astype(float)
yy, xx = np.indices(pixels.shape[:2])
cloth = ((pixels[:, :, 3] > 0) & (xx >= 208) & (xx <= 374)
         & (yy >= 145) & (yy <= 258) & (rgb[:, :, 0] < 115)
         & (rgb[:, :, 2] > rgb[:, :, 0]+5) & (rgb[:, :, 2] < 155))
head_alpha = np.array(Image.open(L/'pilot_v3/head_occlusion.png').getchannel('A'))
cloth &= head_alpha == 0
cloth[203:248, 384:424] = False
lum = .2126*rgb[:, :, 0]+.7152*rgb[:, :, 1]+.0722*rgb[:, :, 2]
neutral = np.stack([lum*.93, lum*.96, lum], axis=2)
pixels[:, :, :3][cloth] = np.clip((rgb*.18+neutral*.82)[cloth], 0, 255).astype('uint8')
body = Image.fromarray(pixels, 'RGBA')
body, removed = retain_main_body(body)
assert all(item['area_px'] < 250 for item in removed), removed
# Keep even the prior leg/boot boundary antialiasing exactly. This region has
# no weapon, so it can be retained directly in the separated body plate.
body.paste(before.crop((0, 300, 512, 512)), (0, 300))
removed = [item for item in removed if item['bbox'][1] < 300]
save_clean(body, OUT/'body_rebuilt.png')

master_path = L/'art_pass_05/kingdom_key_master_finished.png'
grip_path = L/'art_pass_05/grip_master_space.png'
master = Image.open(master_path).convert('RGBA')


def projected(im):
    return im.transform((512, 512), Image.Transform.PERSPECTIVE,
                        coefficients, Image.Resampling.BICUBIC)


weapon = projected(master)
front_mask = Image.new('L', master.size)
ImageDraw.Draw(front_mask).rectangle((0, 0, 141, master.height), fill=255)
front_master = master.copy()
front_master.putalpha(Image.composite(master.getchannel('A'), Image.new('L', master.size), front_mask))
front = projected(front_master)
grip = Image.open(L/'art_pass_05/foreground_grip.png').convert('RGBA')
chain = Image.open(L/'art_pass_05/chain_and_charm.png').convert('RGBA')
after = Image.alpha_composite(weapon, body)
for layer in [front, chain, grip]:
    after = Image.alpha_composite(after, layer)
# Preserve the exact user-approved hand/cuff area, including its overlaps.
after.paste(before.crop((384, 203, 424, 248)), (384, 203))
save_clean(weapon, OUT/'weapon_back.png')
save_clean(front, OUT/'weapon_foreground.png')
save_clean(grip, OUT/'approved_grip.png')
save_clean(chain, OUT/'chain.png')
save_clean(after, OUT/'sora_run_loop_00_review.png')

comparison = Image.new('RGB', (1024, 550), '#202633')
for i, (im, title) in enumerate([(before, 'Prior shaft across torso'),
                                (after, 'Shaft behind head/body; same guard and approved grip')]):
    comparison.paste(im, (i*512, 32), im)
    ImageDraw.Draw(comparison).text((i*512+12, 10), title, fill='white')
comparison.save(OUT/'Occlusion_Comparison.png')
review = Image.new('RGB', (1024, 710), '#202633')
rd = ImageDraw.Draw(review)
for i, color in enumerate(['#202633', '#e1e2e4']):
    bg = Image.new('RGB', (512, 512), color)
    bg.paste(after, (0, 0), after)
    review.paste(bg, (i*512, 28))
    current = after if i == 0 else after.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    small = current.resize((128, 128), Image.Resampling.LANCZOS)
    review.paste(small, (i*512+192, 564), small)
rd.text((12, 8), 'Loop00 carry-overlap review / dark and light', fill='white')
review.save(OUT/'Frame_Review_Board.png')

actual = Image.open(OUT/'sora_run_loop_00_review.png').convert('RGBA')
assert np.array_equal(np.array(before)[203:248, 384:424], np.array(actual)[203:248, 384:424])
assert np.array_equal(np.array(before)[300:], np.array(actual)[300:])
assert np.array_equal(np.array(weapon), np.array(Image.open(L/'art_pass_05/weapon_instance.png')))
assert hashlib.sha256(old_path.read_bytes()).hexdigest() == old_hash
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
metadata.update({
    'status': 'loop00 rear-shaft overlap correction; art/seam review',
    'source_review': 'frame_00_review_v1',
    'occlusion': 'shaft behind head/body; connected guard and approved hand in front',
    'weapon_master_sha256': hashlib.sha256(master_path.read_bytes()).hexdigest(),
    'grip_master_sha256': hashlib.sha256(grip_path.read_bytes()).hexdigest(),
    'body_layers': [str(path.relative_to(L)) for path in body_sources],
    'removed_detached_body_fragments': removed,
    'checks': ['approved hand/cuff area exact', 'lower body exact', 'weapon projection exact',
               'original sheet and prior review hashes unchanged'],
    'limitations': ['Clothing/arm construction still needs idle-quality refinement.',
                    'Start07 to loop00 rear-leg/body-pitch differences remain.',
                    'Other loop poses need the same overlap review.',
                    'No Godot integration or engine test.']})
(OUT/'manifest.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
(OUT/'README.md').write_text(
    '# Loop00 shoulder-carry overlap revision\n\n'
    'Rebuilt the weapon-free body from retained local plates, then placed the shaft '
    'behind the head and torso. The guard/collar and approved grip stay in front. '
    'The rigid master, perspective matrix, 25-degree foreground yaw, chain and '
    'exact approved hand/cuff region are unchanged. Lower-body pixels are exact.\n\n'
    'The older reviewed sprite and original sheet are preserved. This fixes layer '
    'order, not the remaining start-to-loop anatomical transition, clothing quality, '
    'timing or gameplay integration. Other loop poses still need overlap review.\n', encoding='utf-8')
print('Saved loop00 occlusion revision; approved grip, lower body and weapon projection verified.', OUT)
