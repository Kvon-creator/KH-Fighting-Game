"""Export the approved ground grab (v7, Kvon November 11) to the game.

The grab is drawn on a 1024 x 1024 canvas at the usual 512-render scale, so the game frames are 768 x 768 (x 0.75,
like every other animation's 512 -> 384). Feet point in those frames: (384, 738) (canvas centre, floor row 982 x .75
+ 1.5, matching the other animations' 470 -> 354).
- grab_768/sora_grab_NN.png          Sora (18 drawings)
- grab_fx_768/sora_grab_fx_NN.png    on top of everything: the Keyblade smear + the impact burst (empty when none)
- grab_held_768/sora_grab_held_NN.png the grabbed opponent (drawings 0-14), with the spin motion lines under them
Also prints the opponent body's centre on the strike drawing (14) relative to the feet point, and the hurt_air
drawing 0 body centre relative to its feet, so the game can start the knockdown where the opponent is drawn.
Plain Python + Pillow. Run: python export_grab_assets.py
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
assert (ROOT / 'KingdomArena/project.godot').is_file(), ROOT
SORA = ROOT / 'design/models/sora'
ASSETS = ROOT / 'KingdomArena/assets/sora'
ATK, HURT = SORA / 'atk_grab2d_v7', SORA / 'hurt_grab2d_v7'
LAST_HELD = 14
SIZE = 768

rep = json.loads((HURT / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
out = {k: ASSETS / k for k in ('grab_768', 'grab_fx_768', 'grab_held_768')}
for d in out.values():
    d.mkdir(parents=True, exist_ok=True)


def small(img):
    return img.resize((SIZE, SIZE), Image.LANCZOS)


for i in range(len(rep['game_frames_60fps'])):
    body = Image.open(ATK / 'frames_512' / f'sora_idle3d_{i:02d}.png').convert('RGBA')
    small(body).save(out['grab_768'] / f'sora_grab_{i:02d}.png')
    fx = Image.new('RGBA', body.size, (0, 0, 0, 0))
    for p in (ATK / 'frames_smear_512' / f'sora_smear_{i:02d}.png', ATK / 'frames_fx_front_512' / f'sora_fx_{i:02d}.png'):
        if p.is_file():
            fx.alpha_composite(Image.open(p).convert('RGBA'))
    small(fx).save(out['grab_fx_768'] / f'sora_grab_fx_{i:02d}.png')
    if i <= LAST_HELD:
        held = Image.new('RGBA', body.size, (0, 0, 0, 0))
        lines = ATK / 'frames_fx_back_512' / f'sora_fx_{i:02d}.png'
        if lines.is_file():
            held.alpha_composite(Image.open(lines).convert('RGBA'))
        held.alpha_composite(Image.open(HURT / 'frames_512' / f'sora_idle3d_{i:02d}.png').convert('RGBA'))
        small(held).save(out['grab_held_768'] / f'sora_grab_held_{i:02d}.png')


def centre(path, feet):
    bb = Image.open(path).convert('RGBA').getchannel('A').point(lambda a: 255 if a > 127 else 0).getbbox()
    return ((bb[0] + bb[2])/2 - feet[0], (bb[1] + bb[3])/2 - feet[1])


strike = centre(HURT / 'frames_512' / f'sora_idle3d_{LAST_HELD:02d}.png', (512, 982))
strike = (round(strike[0]*.75, 1), round(strike[1]*.75, 1))
air0 = centre(ASSETS / 'hurt_air_384' / 'sora_hurt_air_00.png', (192, 354))
print('EXPORT_OK holds', rep['game_frames_60fps'], 'behind', rep['grab_victim_behind'][:LAST_HELD + 1])
print('STRIKE_BODY_CENTRE', strike, 'HURT_AIR0_CENTRE', (round(air0[0], 1), round(air0[1], 1)))
