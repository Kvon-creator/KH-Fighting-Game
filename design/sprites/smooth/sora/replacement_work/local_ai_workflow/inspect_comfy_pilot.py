"""Read-only export/provenance inspection; no drawing or image modification."""
import hashlib
import json
import re
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
attempt = sys.argv[1]
assert re.fullmatch(r'attempt_[0-9]{2,}', attempt)
folder = ROOT / 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial' / attempt
receipt = json.loads((folder / 'receipt.json').read_text(encoding='utf-8-sig'))
assert receipt['status'] == 'generated_pending_review' and len(receipt['files']) == 1
for file_key, hash_key in [('reference','referenceSha256'),('sourceSheet','sourceSheetSha256')]:
    source = (ROOT / receipt[file_key]).resolve()
    source.relative_to(ROOT)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == receipt[hash_key]
item = receipt['files'][0]
assert Path(item['file']).name == item['file']
candidate = folder / item['file']
assert hashlib.sha256(candidate.read_bytes()).hexdigest() == item['sha256']
image = Image.open(candidate)
image.load()
assert image.size == (512,512) and image.format == 'PNG'
alpha = image.getchannel('A').getextrema() if 'A' in image.getbands() else None
print(json.dumps({'attempt':attempt,'fullCanvas':[512,512],
                  'mode':image.mode,'pngDecodes':True,'nativeHashMatchesReceipt':True,
                  'originalSheetAndInputUnchanged':True,
                  'alphaRange':alpha,'hasActualTransparentPixels':bool(alpha and alpha[0]<255),
                  'pixelDifferenceFromInputFile':item['sha256'] != receipt['referenceSha256'],
                  'visualArtAndPoseApproval':'pending; file/hash difference does not certify a new or correct pose',
                  'limitations':['Whole-pose image-to-image pilot, not a complete running cycle.',
                                 'Visual style, grip, arm topology, rigid weapon and clipping require image review.',
                                 'No Godot/gameplay integration or final user artwork approval.']},indent=2))
