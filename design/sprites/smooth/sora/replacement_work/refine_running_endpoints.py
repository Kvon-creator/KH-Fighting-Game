"""Use the actual approved idle at stationary endpoints; preserve all sources."""
from pathlib import Path
import json
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent;READY=ROOT/'ready'
idle=Image.open(READY/'standing_idle/sora_stand_idle_00.png').convert('RGBA')
out=READY/'run_start/refinement_v2';out.mkdir(parents=True,exist_ok=True)
frame=Image.new('RGBA',(512,512));frame.alpha_composite(idle,(0,-38))
frame.save(out/'sora_run_start_00.png')
bg=Image.new('RGB',(512,544),'#202633');bg.paste(frame,(0,32),frame)
ImageDraw.Draw(bg).text((12,10),'Approved idle as run-start guard endpoint',fill='white')
bg.save(out/'Frame_00_Review.png')
(out/'manifest.json').write_text(json.dumps({'status':'one refined endpoint only; intermediate start frames still require redraw','frame_index':0,'path':'sora_run_start_00.png','source':'../standing_idle/sora_stand_idle_00.png','canvas':[512,512],'translation':[0,-38],'uniform_scale':1,'floor_y':432,'limitations':['Original approved idle weapon retained; fixed-master transition seam still needs review.','No claim that the previous failed start draft is finished.']},indent=2),encoding='utf-8')
print('Saved approved-art start endpoint:',out)
