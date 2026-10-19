"""Read-only PNG/GIF/copy validation for the partial running preview."""
import hashlib
import json
import re
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version = sys.argv[1] if len(sys.argv)>1 else 'approved_style_sequence_v1'
assert re.fullmatch(r'approved_style_sequence_v[0-9]+',version)
base = ROOT / 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial'
folder = base / version
manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
assert len(manifest['frames'])==3 and manifest['loop'] is False and manifest['durationMs']==240
hashes=[]
floors=[]
for frame in manifest['frames']:
    image_path=folder/frame['file']
    assert image_path.parent==folder
    digest=hashlib.sha256(image_path.read_bytes()).hexdigest()
    assert digest==frame['sha256']==hashlib.sha256((base/frame['source']).read_bytes()).hexdigest()
    image=Image.open(image_path)
    image.load()
    assert image.mode=='RGB' and image.size==(512,512)
    rows=[y for y in range(350,512) if any(min(image.getpixel((x,y)))<100 for x in range(50,450))]
    floors.append(max(rows)+1)
    hashes.append(digest)
assert len(set(hashes))==3
gifs=[]
for filename,delay in [('Three_Pose_Once.gif',80),('Three_Pose_Slow_Once.gif',320)]:
    gif=Image.open(folder/filename)
    assert gif.size==(512,512) and gif.n_frames==3 and 'loop' not in gif.info
    durations=[]
    for n in range(3):
        gif.seek(n);gif.load();durations.append(gif.info['duration'])
    assert durations==[delay]*3
    gifs.append(dict(file=filename,frameCount=3,durationsMs=durations,repeatExtension=False))
board=Image.open(folder/'Contact_Sheet.png');board.load()
assert board.size==(1536,570)
assert max(floors)-min(floors)<=2, 'Unexpected support-floor drift in this partial study'
result=dict(passed=True,distinctCompletePoses=3,copiesMatchReviewedPoseHashes=True,fullCanvas=[512,512],background='opaque white',
            darkSoleExclusiveBottoms=floors,maximumFloorVariationPx=max(floors)-min(floors),gifs=gifs,poseBoard=[1536,570],
            approvedAnchorUnchanged=hashes[0]=='3dd7b620289eaf707973cb71ec05d901637f5251c45d3745f180f657a77b7d2b',
            naturalFullCycleMotionCertified=False,fullLoopReady=False,stopUpdated=False,browserTested=False,godotIntegrated=False)
target=folder/'QA_Report.json'
if target.exists():
    assert json.loads(target.read_text(encoding='utf-8'))==result, 'Preserve different QA record'
else:
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
