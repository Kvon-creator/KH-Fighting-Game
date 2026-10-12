"""Read-only raster/provenance checks; never paints or saves image pixels."""
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from inspect_flat_run_batch import components

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
READY = ROOT / 'design/sprites/smooth/sora/replacement_work/ready'
version = sys.argv[1]
assert version.startswith('gait_cycle_study_v') and version[len('gait_cycle_study_v'):].isdigit()
folder = READY / 'run_loop/direct_generation_retry_v1' / version
manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8-sig'))
count = manifest['frameCount']
assert count == len(manifest['frames']) and count in (12,16)
assert sum(f['durationMs'] for f in manifest['frames']) == manifest['durationMs'] == 960
for frame in manifest['frames']:
    key = frame.get('keyPosition',frame['index'])
    expected_support = 'far' if key < 5 else 'near' if 6 <= key <= 10 else 'none'
    assert frame['support'] == expected_support
native = np.asarray(Image.open(manifest['sourceFiles'][1]))
body = np.asarray(Image.open(manifest['sourceFiles'][0]))
for source, expected in zip(manifest['sourceFiles'], manifest['sourceHashes']):
    source = Path(source)
    source.relative_to(ROOT)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected

protected = {
    'acceptedRunStartGif': ('run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif',
                           '1f9f81975ea11f747e8956e72e9705968ae5fdb8379e5622bc785c7aad747d41'),
    'approvedIdle': ('standing_idle/sora_stand_idle_00.png',
                     'baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7'),
    'generatedLoopOriginal': ('run_loop/direct_generation_retry_v1/sora_run_loop_generated_original.png',
                             '9d919b4f317981b331010a1ddb049a7807fb8f21ba214d82a40b04291c9065c7'),
    'generatedStopOriginal': ('run_stop/direct_generation_retry_v1/sora_run_stop_generated_original.png',
                             '89b6f8044e80f33f0ee8010acdf44942a0185ee82f8bb5a0adf5b1dad88d552e')}
for name, (relative, expected) in protected.items():
    assert hashlib.sha256((READY / relative).read_bytes()).hexdigest() == expected, name

rows = []
for frame in manifest['frames']:
    path = folder / frame['file']
    image = Image.open(path)
    assert image.mode == 'RGBA' and image.size == (512,512)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == frame['sha256']
    pixels = np.asarray(image)
    alpha = pixels[...,3]
    bounds = image.getchannel('A').getbbox()
    assert int(alpha.min()) == 0 and int(alpha.max()) == 255
    assert 0 < bounds[0] and 0 < bounds[1] and bounds[2] < 512 and bounds[3] < 512
    solid_y = np.nonzero(alpha > 100)[0]
    solid_bottom = int(solid_y.max())+1
    assert solid_bottom == frame['supportOpaqueBottom']
    if frame['support'] == 'none':
        assert solid_bottom < manifest['floor']
    else:
        assert solid_bottom == manifest['floor']
    detached = components(alpha)[:-1]
    assert not detached, (frame['index'], detached)
    shift = frame['bodyShiftY']
    # Whole-canvas arm stages are editable complete sprites, never part layers.
    stage_file = frame.get('upperWholeCanvasStage')
    upper = body
    if stage_file:
        stage_path = folder / stage_file
        assert hashlib.sha256(stage_path.read_bytes()).hexdigest() == frame['upperStageSha256']
        upper = np.asarray(Image.open(stage_path))
        # These source-exact regions protect the carrying hand/guard and face/hair.
        assert np.array_equal(upper[:270,:280], native[:270,:280])
        assert np.array_equal(upper[:223,280:], native[:223,280:])
        # Native carried blade and teeth, separately checked from the free arm.
        assert np.array_equal(upper[207:259,410:485], native[207:259,410:485]), frame['index']
    # Integer bob with transparent padding, including positive compression shifts.
    top = frame['protectedUpperExclusiveY']
    source_y = np.arange(top)-shift
    expected = np.zeros_like(pixels[:top])
    valid = (source_y >= 0) & (source_y < 512)
    # System.Drawing.Color.Transparent uses white hidden RGB with zero alpha.
    expected[~valid,:,:3] = 255
    expected[valid] = upper[source_y[valid]]
    assert np.array_equal(pixels[:top], expected), frame['index']
    joints = frame['joints']
    error = max(abs(math.dist(joints[a], joints[b])-length) for a,b,length in
                [(0,1,manifest['nearThigh']),(1,2,manifest['nearShin']),
                 (3,4,manifest['farThigh']),(4,5,manifest['farShin'])])
    assert error < .002
    arm_error = None
    if frame.get('arm'):
        arm = frame['arm']
        arm_error = max(abs(math.dist(arm['shoulder'],arm['elbow'])-arm['upperLength']),
                        abs(math.dist(arm['elbow'],arm['wrist'])-arm['forearmLength']))
        assert arm_error < .002
    game = Image.open(folder / 'frames_128' / frame['file'])
    assert game.mode == 'RGBA' and game.size == (128,128)
    assert game.getchannel('A').getextrema()[0] == 0
    rows.append({'index':frame['index'],'phase':frame['phase'],'support':frame['support'],
                 'alphaBounds':bounds,'solidSoleExclusiveBottom':solid_bottom,
                 'solidFlightClearance':manifest['floor']-solid_bottom,
                 'faintEdgeBelowFloor':max(0,bounds[3]-manifest['floor']),
                 'noDetachedOpaqueComponentsAbove8Pixels':True,
                 'maximumLegGuideError':error,'maximumArmGuideError':arm_error,
                 'wholeCanvasUpperPreservedAfterIntegerBob':True})
assert len({f['sha256'] for f in manifest['frames']}) == count
for size in (512,128):
    path = folder / f'Preview_{size}_Loop.gif'
    gif = Image.open(path)
    assert gif.size == (size,size) and gif.n_frames == count and gif.info['loop'] == 0
    for index, frame in enumerate(manifest['frames']):
        gif.seek(index)
        assert gif.info['duration'] == frame['durationMs']

# This reports drawing gaps rather than pretending fixed joint lengths certify fluidity.
steps = []
for i, frame in enumerate(manifest['frames']):
    after = manifest['frames'][(i+1)%count]
    steps.append({'from':i,'to':(i+1)%count,
                  'nearAnkleDistance':math.dist(frame['joints'][2], after['joints'][2]),
                  'farAnkleDistance':math.dist(frame['joints'][5], after['joints'][5])})
print(json.dumps({'version':version,'distinctWholeDrawings':count,
                  'alternatingSupportAndFlightOrderVerified':True,
                  'all512And128RgbaExportsDecode':True,
                  'originalsBenchmarkIdleAndBrushSourcesUnchanged':True,
                  'gifFrameTimingAndRepeatVerified':True,
                  'protectedCarryingGripFaceAndBladeSourcePixelsVerified':bool(manifest.get('counterSwing')),
                  'frames':rows,'cyclicAnkleStepMeasurements':steps,
                  'limitations':['Recorded support is construction intent; raster checks do not establish anatomical or natural-motion approval.',
                                 'Faint source edge/shadow alpha can extend below the solid-sole floor.',
                                 'Garment/sleeve joins, shoe depth, upper follow-through and start/stop joins remain unfinished.',
                                 'No actual-browser or Godot playback test.']},indent=2))
