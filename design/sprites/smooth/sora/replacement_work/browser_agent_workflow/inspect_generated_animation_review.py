"""Read-only export/provenance QA, not a natural-motion certification."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r"D:\KH Fighting Game".lower()
READY = ROOT / 'design/sprites/smooth/sora/replacement_work/ready'
reports = []
for animation in ('run_loop', 'run_stop'):
    folder = READY / animation / 'direct_generation_retry_v1/whole_frame_review_v1'
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
    assert manifest['frameCount'] == 12
    source = Path(manifest['source'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['sourceSha256']
    rows = []
    for frame in manifest['frames']:
        path = folder/frame['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == frame['sha256']
        with Image.open(path) as image:
            assert image.size == (512,512) and image.mode == 'RGBA'
            alpha = image.getchannel('A')
            assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] > 240
            bounds = alpha.getbbox()
            assert bounds[0] > 0 and bounds[1] > 0 and bounds[2] < 512 and bounds[3] < 512
            rows.append(dict(index=frame['index'],bounds=bounds,alphaExtrema=alpha.getextrema()))
        with Image.open(folder/'frames_128'/frame['file']) as game:
            assert game.size == (128,128) and game.mode == 'RGBA'
            assert game.getchannel('A').getextrema()[0] == 0
    assert len(set(frame['sha256'] for frame in manifest['frames'])) == 12
    suffix = 'Loop' if manifest['loop'] else 'Once'
    for size in (512,128):
        path = folder/f'Preview_{size}_{suffix}.gif'
        with Image.open(path) as gif:
            assert gif.n_frames == 12
            delays = []
            for index in range(12):
                gif.seek(index);delays.append(gif.info['duration'])
        assert delays == [frame['durationMs'] for frame in manifest['frames']]
        assert (b'NETSCAPE2.0' in path.read_bytes()) == manifest['loop']
    reports.append(dict(animation=animation,frameCount=12,nativeSourcePreserved=True,
                        transparent512And128=True,distinctImageHashes=12,frames=rows))
preserved = {
    'run_start/direct_imagegen_trial/attempt_03/sora_run_start_original.png':'6108be48aa93f736514c1860f1a9966de1998b0800814156c681321cb779530e',
    'run_start/direct_imagegen_trial/whole_figure_review_v3/frame_11.png':'cb54c1d39b5ea7a83a1bd053bd876a49391993d0ea2bec8a1d36472f1c6e737c',
    'run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif':'1f9f81975ea11f747e8956e72e9705968ae5fdb8379e5622bc785c7aad747d41',
    'standing_idle/sora_stand_idle_00.png':'baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7'
}
for relative, digest in preserved.items():
    assert hashlib.sha256((READY/relative).read_bytes()).hexdigest() == digest, relative
print(json.dumps(dict(scope='Offline export/provenance QA; motion and weapon consistency remain unapproved. No Godot/browser playback test.',
                      acceptedReferencesPreserved=True,animations=reports),indent=2))
