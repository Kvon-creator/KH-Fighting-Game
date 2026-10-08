"""Copy a curated portable art handoff; no original assets are modified."""
from pathlib import Path
import shutil,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'design/handoffs/Layer_ai_Sora_Running_2026-10-07'
WORK=ROOT/'design/sprites/smooth/sora/replacement_work'
selected=[]
def add(relative):
    p=ROOT/relative
    if not p.is_file():raise FileNotFoundError(p)
    selected.append(p)

for name in ['INDEX.md','Agent_Setup.md','Sora_Running_Keyblade_Carry.md',
             'Sora_Animation_Workflow.md','Sora_Base_Design.md','Sora_Art_Style.md',
             'Sora_Frame_Size.md','Sora_Standing_Height.md','Sora_Sprite_Facing.md',
             'Sora_Idle_Pose.md','Sora_Animation_Pose_Integrity.md',
             'Sora_Sprite_Directory.md','Sora_Transition_Frame_Count.md',
             'Sora_Replacement_Preview_Approval.md','Project_Location.md']:
    add(Path('memory')/name)
add(Path('design/references/Sora_KHIV_Render.webp'))
for p in (ROOT/'memory').glob('*.md'):
    selected.append(p)
for name in ['sora_stand_idle_00.png','sora_stand_idle_sheet.png',
             'sora_stand_idle_preview.gif','sora_stand_idle_manifest.json']:
    add(Path('design/sprites/smooth/sora/replacement_work/ready/standing_idle')/name)
for name in ['Running_Weapon_Correction_Plan.md','PRODUCTION_STATUS.md']:
    add(Path('design/sprites/smooth/sora/replacement_work/ready')/name)
for directory in ['run_start','run_loop','run_stop']:
    for p in (WORK/'ready'/directory).rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.png','.gif','.md','.json'}:
            selected.append(p)
for p in WORK.glob('*.py'):
    selected.append(p)
inventory=[]
for p in sorted(set(selected)):
    relative=p.relative_to(ROOT)
    out=DEST/relative
    out.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,out)
    inventory.append({'path':relative.as_posix(),'bytes':p.stat().st_size,
                      'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(DEST/'FILE_INVENTORY.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
# Root entry point for a remote agent, no implicit path knowledge required.
(DEST/'START_HERE.txt').write_text(
    'Read HANDOFF.md first.\n'
    'The short task at the top can be pasted into Layer.ai.\n'
    'Workspace-relative references and editable PNG layers are bundled.\n'
    'Latest flattened frames: ready/run_loop/layers/frame_00_review_v1 and frame_01_review_v1\n'
    '(under design/sprites/smooth/sora/replacement_work/).\n'
    'Older versions are history/dependencies; art_pass_04 has the rejected grip.\n'
    'This package has no PSD or Godot build. Preserve source sheets.\n',encoding='utf-8')
archive=DEST.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(DEST).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for item in inventory:
        assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
print('Bundle:',archive)
print('Asset/source files:',len(inventory))
print('Archive bytes:',archive.stat().st_size)
print('ZIP integrity and all bundled file hashes verified.')
