"""Ground grab review sheet and preview GIF: composite Sora's layer (atk_grab_vN) and the grabbed opponent's layer
(hurt_grab_vN) per drawing - the opponent drawn behind Sora where the build recorded it - on white with the floor line.
The opponent's layer is shown up to the strike (drawing 14); afterwards the game's knockdown takes over.
Effects in Sora's folder are layered in when present: frames_fx_back_512 behind both bodies, frames_smear_512 and
frames_fx_front_512 on top (frames_512 only).
v6: the crop shows the canvas from 12% down (v1-v5 cut at 22%, which hid the top of the toss), and the optional
--gif writes a half-speed preview (holds x2) with an optional --hitstop N extra game frames on the strike.
Run: python grab_review_sheet.py <sora folder> <opponent folder> <frames subfolder> <out png> [--gif out.gif]
                                 [--hitstop N]
     e.g. python grab_review_sheet.py atk_grab2d_v6 hurt_grab2d_v6 frames_512 atk_grab2d_v6/Grab_Sheet.png
          --gif atk_grab2d_v6/Grab_slow.gif --hitstop 10
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

SORA = Path(__file__).resolve().parents[1]
sora, opp, sub, out_png = sys.argv[1:5]
gif = sys.argv[sys.argv.index('--gif') + 1] if '--gif' in sys.argv else None
hitstop = int(sys.argv[sys.argv.index('--hitstop') + 1]) if '--hitstop' in sys.argv else 0
# --last N: the last drawing the opponent's layer is shown on (ground grab 14 = the strike; air grab 8).
LAST_OPP = int(sys.argv[sys.argv.index('--last') + 1]) if '--last' in sys.argv else 14
rep = json.loads((SORA / opp / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
behind = rep['grab_victim_behind']
holds = rep['game_frames_60fps']
n = len(behind)
# Crop from 12% down, or higher when a drawing reaches above that (the air grab's overhead haul).
_tops = [Image.open(SORA / d_ / sub / f'sora_idle3d_{i:02d}.png').getchannel('A').getbbox()[1]
         for d_ in (sora, opp) for i in range(n)
         if Image.open(SORA / d_ / sub / f'sora_idle3d_{i:02d}.png').getchannel('A').getbbox()]
_w0 = Image.open(SORA / sora / sub / 'sora_idle3d_00.png').size[0]
TOP = min(.12, max(0, min(_tops) - 16)/_w0)
S, COLS = 340, 6
rows = (n + COLS - 1)//COLS
sheet = Image.new('RGB', (COLS*S, rows*(S + 18)), 'white')
draw = ImageDraw.Draw(sheet)


def layer(folder, name):
    p = SORA / sora / folder / name
    return Image.open(p).convert('RGBA') if sub == 'frames_512' and p.is_file() else None


frames, durs = [], []
for i in range(n):
    a = Image.open(SORA / sora / sub / f'sora_idle3d_{i:02d}.png').convert('RGBA')
    b = Image.open(SORA / opp / sub / f'sora_idle3d_{i:02d}.png').convert('RGBA')
    bg = Image.new('RGBA', a.size, 'white')
    floor = rep['ground_baseline_y']
    ImageDraw.Draw(bg).line((0, floor, a.size[0], floor), fill=(190, 190, 190, 255), width=2)
    layers = [layer('frames_fx_back_512', f'sora_fx_{i:02d}.png')]
    layers += list(((b, a) if behind[i] else (a, b)) if i <= LAST_OPP else (a,))
    layers += [layer('frames_smear_512', f'sora_smear_{i:02d}.png'), layer('frames_fx_front_512', f'sora_fx_{i:02d}.png')]
    for l_ in layers:
        if l_ is not None:
            bg.alpha_composite(l_)
    w = a.size[0]
    side = 1 - TOP
    view = bg.crop((int(w*(1 - side)/2), int(w*TOP), int(w*(1 + side)/2), w)).convert('RGB')
    sheet.paste(view.resize((S, S)), ((i % COLS)*S, (i//COLS)*(S + 18) + 18))
    tag = f'{i}' + (' (opponent behind)' if behind[i] and i <= LAST_OPP else '')
    draw.text(((i % COLS)*S + 4, (i//COLS)*(S + 18) + 3), tag, fill='black')
    frames.append(view.resize((480, 480)))
    durs.append(round((holds[i] + (hitstop if i == LAST_OPP else 0))*1000/60*2, -1))
sheet.save(SORA / out_png)
print('SHEET_OK', out_png)
if gif:
    frames[0].save(SORA / gif, save_all=True, append_images=frames[1:], duration=durs, loop=0)
    print('GIF_OK', gif, durs)
