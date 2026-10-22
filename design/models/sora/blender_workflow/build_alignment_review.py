"""Write Alignment_Review_v18.json: per sequence, the sheet and first-frame alignment points.

Head top is measured from the final 2D frame (topmost solid row); bone and grip points come
from export_alignment_points.py, all in 512 px frame coordinates (x right, y down).
Run: python build_alignment_review.py
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
S = ROOT / 'design/models/sora'
BONES = {  # from export_alignment_points.py, frame 1 of each sequence
    'walk_fwd_v18t': ([265.0, 200.4], [267.9, 320.2], [268.9, 324.1]),
    'walk_fwd_v18': ([265.7, 227.6], [269.0, 351.1], [269.8, 354.9]),
    'walk_fwd_v18b': ([265.6, 224.4], [269.9, 346.4], [270.5, 350.2]),
    'walk_fwd_v18w': ([267.0, 224.4], [268.9, 347.4], [269.7, 351.3]),
}
SEQS = [('1 Start Transition', 'walk_fwd_v18t', 'walk_fwd2d_v18t_ink', '4x1'),
        ('2 Grounded Walk Cycle', 'walk_fwd_v18', 'walk_fwd2d_v18_ink', '4x3'),
        ('3 Brake 1 - Feet Together', 'walk_fwd_v18b', 'walk_fwd2d_v18b_ink', '4x1'),
        ('4 Brake 2 - Wide Stance', 'walk_fwd_v18w', 'walk_fwd2d_v18w_ink', '4x1')]
out = []
for name, rig, d2, grid in SEQS:
    alpha = np.asarray(Image.open(S / d2 / 'frames_512/sora_idle3d_00.png').getchannel('A')) > 200
    rows = np.where(alpha.any(1))[0]
    top = int(rows.min())
    sheet = next((S / d2).glob(f'*_sheet_white_{grid}.png'))
    head, grip, socket = BONES[rig]
    out.append({'sequence': name, 'sheet': sheet.relative_to(ROOT).as_posix(),
                'sheet_size': list(Image.open(sheet).size), 'grid': grid,
                'first_frame_512': {'head_top_silhouette': [int(np.where(alpha[top])[0].mean()), top],
                                    'head_bone_atama': head, 'front_grip_hand_center_R': grip,
                                    'front_grip_socket_R_buki': socket, 'feet_floor_row': int(rows.max())}})
(S / 'Alignment_Review_v18.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
for o in out:
    print(o['sequence'], o['sheet_size'], o['first_frame_512'])
