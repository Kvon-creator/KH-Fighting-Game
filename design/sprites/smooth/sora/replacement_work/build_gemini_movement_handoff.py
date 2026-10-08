"""Copy complete-image references and build a compact, verified Gemini handoff."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

from PIL import Image


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[4]
assert WORKSPACE.name == 'KH Fighting Game'
OUT = WORKSPACE/'design/gemini_movement_handoff'
READY = ROOT/'ready'
copies = [
    (READY/'standing_idle/sora_stand_idle_00.png', 'references/01_Approved_Idle.png', 'approved design/quality'),
    (READY/'run_loop/layers/frame_00_review_v2/sora_run_loop_00_review.png', 'references/02_Run_Carry_Grip_Reference.png', 'carry/grip only; unfinished body'),
    (WORKSPACE/'design/references/Sora_KHIV_Render.webp', 'references/03_Carry_Photo.webp', 'carry/weapon only; do not copy KH4 clothing'),
    (READY/'standing_idle/sora_stand_idle_sheet.png', 'optional_motion_guides/Approved_Idle_Cycle.png', 'approved reference cycle'),
    (READY/'standing_idle/sora_stand_idle_preview.gif', 'optional_motion_guides/Approved_Idle_Preview.gif', 'approved reference cycle'),
    (READY/'crouch_cycle/sora_crouch_sheet.png', 'optional_motion_guides/Approved_Crouch_Transitions.png', 'approved transition poses; crouch-idle review still pending'),
    (READY/'crouch_cycle/sora_crouch_full_cycle_preview.gif', 'optional_motion_guides/Approved_Crouch_Transitions_Preview.gif', 'approved transition cycle'),
    (READY/'shimmy_forward/sora_shimmy_forward_sheet.png', 'optional_motion_guides/Draft_Forward_Shimmy.png', 'review pending'),
    (READY/'shimmy_backward/sora_shimmy_backward_sheet.png', 'optional_motion_guides/Draft_Backward_Shimmy_Reversed_Source.png', 'uses reversed forward poses; needs genuine backward transfer'),
    (READY/'run_start/refinement_v4/review_cycle_v2/sora_run_start_sheet.png', 'optional_motion_guides/Draft_Run_Start.png', 'unfinished art/root/timing/seams'),
    (READY/'run_start/refinement_v4/review_cycle_v2/sora_run_start_preview.gif', 'optional_motion_guides/Draft_Run_Start_Preview.gif', 'unfinished art/root/timing/seams'),
    (READY/'run_loop/review_cycle_v2/sora_run_loop_sheet.png', 'optional_motion_guides/Draft_Run_Loop.png', 'unfinished clothing/arms/gait/root/timing'),
    (READY/'run_loop/review_cycle_v2/sora_run_loop_preview.gif', 'optional_motion_guides/Draft_Run_Loop_Preview.gif', 'unfinished clothing/arms/gait/root/timing'),
    (READY/'run_stop/refinement_v2/sora_run_stop_sheet.png', 'optional_motion_guides/Draft_Run_Stop.png', 'construction polish; unfinished anatomy/torso seams/guard transition'),
    (READY/'run_stop/refinement_v2/sora_run_stop_preview.gif', 'optional_motion_guides/Draft_Run_Stop_Preview.gif', 'construction polish; not idle-quality art'),
]
assert all(path.is_file() for path, _, _ in copies)
records = []
for source, name, status in copies:
    destination = OUT/name
    destination.parent.mkdir(parents=True, exist_ok=True)
    original_bytes = source.read_bytes()
    shutil.copy2(source, destination)
    assert destination.read_bytes() == original_bytes
    im = Image.open(destination)
    im.verify()
    im = Image.open(destination)
    frames = getattr(im, 'n_frames', 1)
    for i in range(frames):
        im.seek(i)
        im.load()
    records.append({'source': source.relative_to(WORKSPACE).as_posix(), 'copy': name,
                    'status': status, 'sha256': hashlib.sha256(original_bytes).hexdigest(),
                    'size_bytes': len(original_bytes), 'dimensions': list(im.size), 'frames': frames})
(OUT/'SOURCE_FILES.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
archive = OUT/'GEMINI_MOVEMENT_HANDOFF.zip'
package_files = [OUT/name for name in ['PROMPT.txt', 'MOVEMENTS.md', 'README.md', 'SOURCE_FILES.json']]
package_files += [OUT/name for _, name, _ in copies]
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in package_files:
        z.write(path, path.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(package_files)
    assert not any('layers/' in name for name in z.namelist())
    for path in package_files:
        assert z.read(path.relative_to(OUT).as_posix()) == path.read_bytes()
for source, _, _ in copies:
    assert source.exists()
print(f'Verified {len(copies)} unchanged complete-image references and {len(package_files)} ZIP entries.')
print(f'Archive: {archive} ({archive.stat().st_size/1024/1024:.2f} MiB)')
print(f'Compact prompt: {len((OUT/"PROMPT.txt").read_text(encoding="utf-8").split())} words.')
