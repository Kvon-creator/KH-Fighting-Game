"""Read-only QA for the new articulated near-leg stride drawings."""
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from inspect_flat_run_batch import components

ROOT=Path(__file__).resolve().parents[6]
assert str(ROOT).lower()==r'D:\KH Fighting Game'.lower()
READY=ROOT/'design/sprites/smooth/sora/replacement_work/ready'
version=sys.argv[1]
assert version.startswith('near_stride_study_v') and version[len('near_stride_study_v'):].isdigit()
folder=READY/'run_loop/direct_generation_retry_v1'/version
manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
body=np.asarray(Image.open(manifest['sourceFiles'][0]))
for source,expected in zip(manifest['sourceFiles'],manifest['sourceHashes']):
    path=Path(source);path.relative_to(ROOT)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
rows=[]
for frame in manifest['frames']:
    path=folder/frame['file'];image=Image.open(path)
    assert image.mode=='RGBA' and image.size==(512,512)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==frame['sha256']
    pixels=np.asarray(image);alpha=image.getchannel('A');bounds=alpha.getbbox()
    assert alpha.getextrema()==(0,255)
    assert bounds[0]>0 and bounds[1]>0 and bounds[2]<512 and bounds[3]<512
    top=frame['protectedUpperExclusiveY'];shift=frame['bodyShiftY']
    expected=body[-shift:top-shift]
    assert np.array_equal(pixels[:top],expected),frame['index']
    joints=frame['joints'];error=0
    for a,b,length in [(0,1,manifest['nearThigh']),(1,2,manifest['nearShin']),
                       (3,4,manifest['farThigh']),(4,5,manifest['farShin'])]:
        error=max(error,abs(math.dist(joints[a],joints[b])-length))
    assert error<.002
    game=Image.open(folder/'frames_128'/frame['file'])
    assert game.size==(128,128) and game.mode=='RGBA' and game.getchannel('A').getextrema()[0]==0
    detached=components(np.asarray(alpha))[:-1]
    # Print detected defects for art review before asserting or inserting any pose.
    rows.append({'index':frame['index'],'phase':frame['phase'],'bounds':bounds,
                 'exclusiveBottom':bounds[3],'clearanceFromFloor470':470-bounds[3],
                 'opaqueExclusiveBottom':Image.fromarray((pixels[...,3]>100).astype('uint8')*255).getbbox()[3],
                 'leftFootRegionBottom':Image.fromarray(pixels[380:,:,:][...,3][:,:330]).getbbox()[3]+380,
                 'rightFootRegionBottom':Image.fromarray(pixels[380:,:,:][...,3][:,330:]).getbbox()[3]+380,
                 'unchangedUpperAfterIntegerBob':True,'maximumGuideLengthError':error,
                 'detachedOpaqueComponentsAbove8Pixels':detached})
assert len({f['sha256'] for f in manifest['frames']})==3
for size in (512,128):
    path=folder/f'Near_Stride_{size}_Once.gif';gif=Image.open(path)
    assert gif.n_frames==3 and b'NETSCAPE2.0' not in path.read_bytes()
    for index in range(3):
        gif.seek(index);assert gif.info['duration']==100
print(json.dumps({'version':version,'distinctDrawings':3,'sourceHashesUnchanged':True,
                  'allFullAndGameExportsDecodeWithTransparency':True,'onceOnlyGifTimingVerified':True,
                  'frames':rows,'limitations':['This is a partial stride drawing study, not a finished run cycle.',
                    'Geometry/raster checks do not certify idle-quality anatomy or natural motion.',
                    'No actual-browser or Godot playback test.']},indent=2))
