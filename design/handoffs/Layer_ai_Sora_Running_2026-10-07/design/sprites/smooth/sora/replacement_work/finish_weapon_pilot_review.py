"""Colour harmony and single-frame review exports; no pose fabrication."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parent
L=ROOT/'ready/run_loop/layers'
SRC=L/'art_pass_06';OUT=L/'frame_00_review_v1'
OUT.mkdir(parents=True,exist_ok=True)
before=Image.open(SRC/'frame_00_art_preview.png').convert('RGBA')
p=np.array(before)
rgb=p[:,:,:3].astype(float)
y,x=np.indices(p.shape[:2])
# Only reconstructed navy fabric, not skin, gold, red, head or metal.
cloth=(p[:,:,3]>0)&(x>=208)&(x<=374)&(y>=145)&(y<=258)
cloth&=(rgb[:,:,0]<115)&(rgb[:,:,2]>rgb[:,:,0]+5)&(rgb[:,:,2]<155)
for source,name in [(L/'art_pass_05','weapon_instance.png'),
                    (L/'art_pass_05','foreground_grip.png'),
                    (L/'pilot_v3','head_occlusion.png')]:
    protected=np.array(Image.open(source/name).convert('RGBA'))[:,:,3]
    cloth&=protected==0
cloth[203:248,384:424]=False
luminance=.2126*rgb[:,:,0]+.7152*rgb[:,:,1]+.0722*rgb[:,:,2]
charcoal=np.stack([luminance*.93,luminance*.96,luminance],axis=2)
# Keep some original hue in highlights while bringing it toward original greys.
harmonized=rgb*.18+charcoal*.82
p[:,:,:3][cloth]=np.clip(harmonized[cloth],0,255).astype('uint8')
# Residual original-blade speck outside the new weapon and character.
weapon_alpha=np.array(Image.open(L/'art_pass_05/weapon_instance.png').convert('RGBA'))[:,:,3]
head_alpha=np.array(Image.open(L/'pilot_v3/head_occlusion.png').convert('RGBA'))[:,:,3]
cleanup=(x>=235)&(x<=267)&(y>=129)&(y<=149)&(weapon_alpha==0)&(head_alpha==0)
p[cleanup]=0
after=Image.fromarray(p,'RGBA')
after.save(OUT/'sora_run_loop_00_review.png')
ImageOps.mirror(after).save(OUT/'sora_run_loop_00_review_mirrored.png')
# Uniform downsampling for scale review only; it does not create new poses.
small=after.resize((128,128),Image.Resampling.LANCZOS)
small.save(OUT/'sora_run_loop_00_128_review.png')
comparison=Image.new('RGB',(1024,550),'#202633')
for i,(im,title) in enumerate([(before,'Previous navy reconstruction'),(after,'Charcoal outfit harmony')]):
    comparison.paste(im,(512*i,32),im)
    ImageDraw.Draw(comparison).text((512*i+12,10),title,fill='white')
comparison.save(OUT/'Colour_Comparison.png')
board=Image.new('RGB',(1056,740),'#202633')
d=ImageDraw.Draw(board)
for i,(im,title) in enumerate([(after,'Right-facing / dark background'),(ImageOps.mirror(after),'Mirrored / light background')]):
    color='#202633' if i==0 else '#e5e5e5'
    panel=Image.new('RGB',(512,512),color);panel.paste(im,(0,0),im)
    board.paste(panel,(16+512*i,32));d.text((24+512*i,12),title,fill='white')
for i,(im,title) in enumerate([(small,'128px canvas'),(ImageOps.mirror(small),'128px mirrored')]):
    board.paste(im,(24+180*i,576),im);d.text((24+180*i,556),title,fill='white')
d.text((440,582),'One frame for visual review.',fill='white')
d.text((440,602),'Uniform scale preview; no new animation poses.',fill='white')
d.text((440,622),'Original sheets and approved hand preserved.',fill='white')
board.save(OUT/'Frame_Review_Board.png')
assert np.array_equal(np.array(before)[203:248,384:424],np.array(after)[203:248,384:424])
assert np.array_equal(np.array(before)[300:],np.array(after)[300:])
m=json.loads((SRC/'manifest.json').read_text())
assert hashlib.sha256((ROOT/'ready/run_loop/run_loop_source.png').read_bytes()).hexdigest()==m['source_sha256']
m['status']='single-frame visual review candidate; not approved final artwork'
m['source_art_pass']='art_pass_06'
m['palette_pass']='charcoal harmony on reconstructed fabric only'
m['review_canvas']=[512,512]
m['game_scale_preview_canvas']=[128,128]
m['checks']=['approved hand exact','lower region exact','source sheet hash exact','weapon transform unchanged']
(OUT/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('Saved review candidate:',OUT)
