"""Apply connected rigid-carry overlap to existing genuine loop poses 01-07."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

from local_pose_art import retain_main_body, save_clean


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
READY = ROOT/'ready'
L = READY/'run_loop/layers'
SOURCE = READY/'run_loop/run_loop_source.png'
EXPECTED = '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
MASTER = L/'art_pass_05/kingdom_key_master_finished.png'
GRIP = L/'art_pass_05/grip_master_space.png'
ATTACHED_WEAPON_REMOVAL = {
    3: [[(194, 124), (212, 124), (225, 133), (239, 136), (239, 146), (195, 149)]],
    4: [[(217, 97), (236, 93), (245, 107), (259, 107), (259, 119), (243, 123), (215, 116)]],
}


def opaque_bottom(im):
    points = np.argwhere(np.array(im.getchannel('A')) > 8)
    return int(points[:, 0].max())+1 if len(points) else 0


def render(index):
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    old = L/f'frame_{index:02d}_review_v1'
    out = L/f'frame_{index:02d}_review_v2'
    out.mkdir(parents=True, exist_ok=True)
    old_path = old/f'sora_run_loop_{index:02d}_review.png'
    old_hash = hashlib.sha256(old_path.read_bytes()).hexdigest()
    before = Image.open(old_path).convert('RGBA')
    m = json.loads((old/'manifest.json').read_text(encoding='utf-8'))
    H = np.array(m['master_to_screen_homography'])
    inverse = np.linalg.inv(H)
    inverse /= inverse[2, 2]
    coefficients = tuple(inverse.flatten()[:8])

    def projected(im):
        return im.transform((512, 512), Image.Transform.PERSPECTIVE,
                            coefficients, Image.Resampling.BICUBIC)

    # These are the individual source-pose body and head plates already drawn.
    body = Image.open(old/'refined_body_plate.png').convert('RGBA')
    head_path = (L/f'frame_{index:02d}_v1/head_occlusion.png'
                 if index < 3 else old/'head_occlusion.png')
    body = Image.alpha_composite(body, Image.open(head_path).convert('RGBA'))
    attached_mask = Image.new('L', body.size)
    for points in ATTACHED_WEAPON_REMOVAL.get(index, []):
        ImageDraw.Draw(attached_mask).polygon(points, fill=255)
    body.putalpha(Image.composite(Image.new('L', body.size), body.getchannel('A'), attached_mask))
    if index in ATTACHED_WEAPON_REMOVAL:
        attached_mask.save(out/'attached_old_weapon_removal_mask.png')
    body, removed = retain_main_body(body)
    assert all(item['area_px'] < 250 for item in removed), (index, removed)
    master = Image.open(MASTER).convert('RGBA')
    weapon = projected(master)
    front_mask = Image.new('L', master.size)
    ImageDraw.Draw(front_mask).rectangle((0, 0, 141, master.height), fill=255)
    front_master = master.copy()
    front_master.putalpha(Image.composite(master.getchannel('A'), Image.new('L', master.size), front_mask))
    front = projected(front_master)
    grip = Image.open(old/'foreground_grip.png').convert('RGBA')
    chain = Image.open(old/'chain_and_charm.png').convert('RGBA')
    preserve_y = max(300, opaque_bottom(weapon)+2, opaque_bottom(grip)+2, opaque_bottom(chain)+2)
    assert preserve_y < 350, (index, preserve_y)
    # No weapon enters this region. Preserve all previous leg/boot pixels.
    body.paste(before.crop((0, preserve_y, 512, 512)), (0, preserve_y))
    removed = [item for item in removed if item['bbox'][1] < preserve_y]
    after = Image.alpha_composite(weapon, body)
    for layer in [front, chain, grip]:
        after = Image.alpha_composite(after, layer)
    for im, name in [(body, 'body_rebuilt'), (weapon, 'weapon_back'), (front, 'weapon_foreground'),
                     (grip, 'approved_grip'), (chain, 'chain')]:
        save_clean(im, out/f'{name}.png')
    save_clean(after, out/f'sora_run_loop_{index:02d}_review.png')
    actual = np.array(Image.open(out/f'sora_run_loop_{index:02d}_review.png'))
    old_pixels = np.array(before)
    # Translucent edge pixels blend with their new backdrop. Fully opaque hand
    # interiors, and the entire projected grip drawing, must remain exact.
    grip_core = np.array(grip.getchannel('A')) == 255
    assert np.count_nonzero(grip_core) > 20, index
    assert np.array_equal(np.array(projected(Image.open(GRIP).convert('RGBA'))), np.array(grip)), index
    assert np.array_equal(old_pixels[grip_core, :3], actual[grip_core, :3]), index
    assert np.array_equal(old_pixels[preserve_y:], actual[preserve_y:]), index
    assert np.array_equal(np.array(weapon), np.array(Image.open(old/'weapon_instance.png'))), index
    assert hashlib.sha256(old_path.read_bytes()).hexdigest() == old_hash
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    comparison = Image.new('RGB', (1024, 550), '#202633')
    for col, (im, title) in enumerate([(before, f'Prior loop {index:02d} carry'),
                                      (after, 'Rigid shaft behind head/body; same grip and pose')]):
        comparison.paste(im, (col*512, 32), im)
        ImageDraw.Draw(comparison).text((col*512+12, 10), title, fill='white')
    comparison.save(out/'Occlusion_Comparison.png')
    m.update({'status': 'rigid carry overlap revision; anatomy/art/gait review pending',
              'source_review': old.name, 'head_layer': str(head_path.relative_to(L)),
              'occlusion': 'shaft behind head/body; connected guard and original corrected grip in front',
              'weapon_master_sha256': hashlib.sha256(MASTER.read_bytes()).hexdigest(),
              'grip_master_sha256': hashlib.sha256(GRIP.read_bytes()).hexdigest(),
              'physical_master_length_px': 285, 'master_scale': 1,
              'lower_body_preserved_from_y': preserve_y,
              'removed_detached_body_fragments': removed,
              'attached_old_weapon_removal_polygons': ATTACHED_WEAPON_REMOVAL.get(index, []),
              'checks': ['opaque grip interior exact', 'lower body exact', 'weapon projection exact',
                         'original sheet and prior review hashes unchanged'],
              'limitations': ['Existing shared clothing repairs still need individual art refinement.',
                              'Pose registration, gait and transition seams remain unfinished.',
                              'No Godot integration or aerial production.']})
    (out/'manifest.json').write_text(json.dumps(m, indent=2), encoding='utf-8')
    (out/'README.md').write_text(
        f'# Loop {index:02d} carry-overlap revision\n\n'
        'The existing individual body/head plates cover the rear shaft. Connected guard '
        'and corrected grip remain in front, with unchanged perspective and weapon master. '
        'The earlier review and original sheet remain. This fixes overlap; anatomy, '
        'shared clothing repairs, gait and seam timing still need refinement.\n', encoding='utf-8')
    print('Verified overlap pose:', index, 'lower preservation y:', preserve_y, 'fragments:', removed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', type=int, choices=range(1, 8))
    args = parser.parse_args()
    for i in ([args.frame] if args.frame is not None else range(1, 8)):
        render(i)
