"""Read-only QA for complete-canvas motion studies; never edits raster files."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image
from inspect_flat_run_batch import components

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
READY = ROOT / 'design/sprites/smooth/sora/replacement_work/ready'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(version):
    reports = []
    for animation in ('run_loop', 'run_stop'):
        directory = READY / animation / 'direct_generation_retry_v1' / version
        manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8-sig'))
        rows = []
        for frame in manifest['frames']:
            path = directory / frame['file']
            original = Path(frame['source'])
            original.relative_to(ROOT)
            assert digest(path) == frame['sha256']
            assert digest(original) == frame['sourceSha256']
            image = Image.open(path)
            assert image.mode == 'RGBA' and image.size == (512, 512)
            pixels = np.asarray(image)
            alpha = image.getchannel('A')
            assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] > 240
            bounds = alpha.getbbox()
            assert bounds[0] > 0 and bounds[1] > 0 and bounds[2] < 512 and bounds[3] < 512
            game = Image.open(directory / 'frames_128' / frame['file'])
            assert game.size == (128, 128) and game.mode == 'RGBA'
            assert game.getchannel('A').getextrema()[0] == 0
            row = {'index': frame['index'], 'bounds': bounds,
                   'detachedComponentsAbove8Pixels': components(np.asarray(alpha))[:-1]}
            if animation == 'run_loop':
                native = np.asarray(Image.open(original))
                change = np.any(pixels != native, axis=2)
                y, x = np.indices(change.shape)
                protected = (x < 280) | (x > 505) | (y < math.floor(frame['eyeY'] + 30)) | (y >= 350) | ((y >= 335) & (x < 350))
                assert not np.any(change & protected), (frame['index'], int((change & protected).sum()))
                assert change.sum() > 1000
                row['changedPixels'] = int(change.sum())
                row['protectedPixelsChanged'] = 0
                row['jointLengthError'] = max(abs(math.dist(frame['shoulder'], frame['elbow']) - frame['upperLength']),
                                              abs(math.dist(frame['elbow'], frame['wrist']) - frame['forearmLength']))
                assert row['jointLengthError'] < .002
            else:
                assert path.read_bytes() == original.read_bytes()
                row['wholeSelectedSourceExact'] = True
            rows.append(row)
            assert not row['detachedComponentsAbove8Pixels'], (animation, frame['index'], row['detachedComponentsAbove8Pixels'])
        assert len(manifest['frames']) == 12
        assert len({f['sha256'] for f in manifest['frames']}) == 12
        suffix = 'Loop' if manifest['loop'] else 'Once'
        for size in (512, 128):
            gif_path = directory / f'Preview_{size}_{suffix}.gif'
            gif = Image.open(gif_path)
            assert gif.n_frames == 12
            assert (b'NETSCAPE2.0' in gif_path.read_bytes()) == manifest['loop']
            delays = []
            for i in range(12):
                gif.seek(i)
                delays.append(gif.info['duration'])
            assert delays == [f['durationMs'] for f in manifest['frames']]
        reports.append({'animation': animation, 'frameCount': 12,
                        'durationMs': manifest['durationMs'], 'frames': rows})
    loop = READY / 'run_loop/direct_generation_retry_v1' / version / 'sora_run_loop_00.png'
    stop = READY / 'run_stop/direct_generation_retry_v1' / version / 'sora_run_stop_00.png'
    assert loop.read_bytes() == stop.read_bytes()
    preserved = {
        'run_loop/direct_generation_retry_v1/sora_run_loop_generated_original.png': '9d919b4f317981b331010a1ddb049a7807fb8f21ba214d82a40b04291c9065c7',
        'run_stop/direct_generation_retry_v1/sora_run_stop_generated_original.png': '89b6f8044e80f33f0ee8010acdf44942a0185ee82f8bb5a0adf5b1dad88d552e',
        'run_start/direct_imagegen_trial/attempt_03/sora_run_start_original.png': '6108be48aa93f736514c1860f1a9966de1998b0800814156c681321cb779530e',
        'run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif': '1f9f81975ea11f747e8956e72e9705968ae5fdb8379e5622bc785c7aad747d41',
        'standing_idle/sora_stand_idle_00.png': 'baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7',
    }
    for relative, expected in preserved.items():
        assert digest(READY / relative) == expected, relative
    return {'version': version, 'sharedEntryExact': True, 'preservedSourceHashes': preserved,
            'allExportsDecodeWithTransparency': True, 'sequences': reports,
            'limitations': ['Read-only raster/provenance checks do not certify natural gait, rigid weapon geometry or idle quality.',
                            'No actual-browser or Godot playback test.']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    args = parser.parse_args()
    assert args.version.startswith('motion_refinement_v') and args.version[len('motion_refinement_v'):].isdigit()
    print(json.dumps(inspect(args.version), indent=2))
