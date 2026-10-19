"""Read-only raster/provenance QA. Writes JSON reports, never modifies images."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
BASE = ROOT / 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial'

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def project(relative):
    result = (ROOT / relative).resolve()
    result.relative_to(ROOT)
    return result

provenance = load_json(BASE / 'adjacent_guides_v3/provenance.json')
anchor_path = project(provenance['approvedAnchor'])
assert digest(anchor_path) == provenance['approvedAnchorSha256']
anchor = Image.open(anchor_path).convert('RGB')
source_manifest = load_json(BASE.parent / 'direct_generation_retry_v1/whole_frame_review_v1/manifest.json')
records = []
final = '--final' in sys.argv[1:]
for index, attempt in [(1, 'attempt_04'), (2, 'attempt_05')]:
    frame = provenance['frames'][index-1]
    receipt_path = BASE / attempt / 'receipt.json'
    receipt = load_json(receipt_path)
    assert receipt['status'] == 'generated_pending_review' and len(receipt['files']) == 1
    for path_key, hash_key in [('sourceSheet','sourceSheetSha256'), ('reference','referenceSha256'), ('mask','maskSha256')]:
        assert digest(project(receipt[path_key])) == receipt[hash_key]
    source_path = project(frame['source'])
    assert digest(source_path) == frame['sourceSha256']
    manifest_frame = source_manifest['frames'][index]
    assert manifest_frame['file'] == source_path.name and manifest_frame['sha256'] == frame['sourceSha256']
    native = receipt['files'][0]
    native_path = receipt_path.parent / native['file']
    assert native_path.parent == receipt_path.parent and digest(native_path) == native['sha256']
    image_path = native_path
    candidate_sha = native['sha256']
    if final:
        finish = load_json(receipt_path.parent / 'final_pose_v2_manifest.json')
        assert finish['sourceNativeSha256'] == native['sha256'] and finish['guideSha256'] == receipt['referenceSha256'] and finish['maskSha256'] == receipt['maskSha256']
        image_path = receipt_path.parent / finish['file']
        candidate_sha = finish['sha256']
        assert image_path.parent == receipt_path.parent and digest(image_path) == candidate_sha
    image = Image.open(image_path)
    image.load()
    assert image.size == (512,512) and image.mode == 'RGB'
    guide = Image.open(project(receipt['reference'])).convert('RGB')
    mask = Image.open(project(receipt['mask'])).convert('RGB')
    original = Image.open(source_path).convert('RGBA')
    outside = outside_changed = selected_changed = 0
    protected_changed = [0,0,0]
    protected_mask_leaks = [0,0,0]
    lower_opaque = lower_changed = 0
    lower_visible = lower_visible_changed = lower_blend_max_error = 0
    bounds = [512,512,-1,-1]
    bob = frame['bodyShiftY']
    for y in range(512):
        for x in range(512):
            pixel = image.getpixel((x,y))
            if min(pixel) < 240:
                bounds = [min(bounds[0],x),min(bounds[1],y),max(bounds[2],x),max(bounds[3],y)]
            selected = mask.getpixel((x,y))[0] != 0
            changed = pixel != guide.getpixel((x,y))
            if selected:
                selected_changed += changed
            else:
                outside += 1
                outside_changed += changed
            for k,(left,top,width,height) in enumerate(frame['protectedRectangles']):
                if left <= x < left+width and top <= y < top+height:
                    protected_changed[k] += pixel != anchor.getpixel((x,y-bob))
                    protected_mask_leaks[k] += selected
            source_pixel = original.getpixel((x,y))
            if y >= 350 and source_pixel[3] == 255:
                lower_opaque += 1
                lower_changed += pixel != source_pixel[:3]
            if final and y >= 350 and source_pixel[3] > 100:
                alpha = source_pixel[3]
                expected = tuple((value*alpha+255*(255-alpha)+127)//255 for value in source_pixel[:3])
                difference = max(abs(a-b) for a,b in zip(pixel,expected))
                lower_visible += 1
                lower_visible_changed += difference > 2
                lower_blend_max_error = max(lower_blend_max_error,difference)
    passed = outside_changed == 0 and selected_changed > 0 and not any(protected_changed+protected_mask_leaks) and lower_changed == 0 and min(bounds[:2]) > 0 and max(bounds[2:]) < 511
    record = dict(attempt=attempt,index=index,candidate=image_path.name,candidateSha256=candidate_sha,nativeSha256=native['sha256'],canvas=[512,512],mode=image.mode,
                  allInputHashesVerified=True,approvedAnchorSha256=provenance['approvedAnchorSha256'],bodyShiftY=bob,
                  outsideSelectionPixels=outside,changedOutsideSelectionPixels=outside_changed,
                  changedSelectedPixels=selected_changed,changedApprovedProtectedRegions=protected_changed,
                  selectedProtectedPixels=protected_mask_leaks,unchangedOpaqueOriginalLegPixels=lower_opaque,
                  changedOpaqueOriginalLegPixels=lower_changed,darkPixelBoundsInclusive=bounds,
                  preservationPassed=passed,visualReview='required; these checks do not certify anatomy, pose phase or natural motion',
                  fullCycleReady=False,godotIntegrated=False)
    if final:
        record['originalVisibleLegPixelsCompared'] = lower_visible
        record['originalLegPixelsBeyondCompositingTolerance'] = lower_visible_changed
        record['maximumWhiteCompositingRoundingError'] = lower_blend_max_error
        record['preservationPassed'] = passed = passed and lower_visible > 10000 and lower_visible_changed == 0
    report_path = receipt_path.parent / ('Final_Adjacent_Pose_QA.json' if final else 'Adjacent_Pose_QA.json')
    if report_path.exists():
        assert load_json(report_path) == record, 'Preserve different existing QA'
    else:
        report_path.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    records.append(record)
    assert passed, record
print(json.dumps(records,indent=2))
