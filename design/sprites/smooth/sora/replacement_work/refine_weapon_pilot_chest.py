"""Local chest redraw, preserving source art and fixed weapon registration."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
LAYERS=ROOT/'ready/run_loop/layers'
SRC=LAYERS/'art_pass_02'
PILOT=LAYERS/'pilot_v3'
OUT=LAYERS/'art_pass_03'
OUT.mkdir(parents=True,exist_ok=True)
AA=4
overlay=Image.new('RGBA',(2048,2048))
def path(start,segments,fill=None,stroke=None,width=1,closed=True):
    points=[start];a=start
    for b,c,end in segments:
        for j in range(1,33):
            t=j/32;u=1-t
            points.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],
                           u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    q=[(round(x*AA),round(y*AA)) for x,y in points]
    d=ImageDraw.Draw(overlay)
    if fill:d.polygon(q,fill=fill)
    if stroke:d.line(q+([q[0]] if closed else []),fill=stroke,width=round(width*AA),joint='curve')

# Replace the hanging construction lines with a compact jacket panel following
# the shoulder-to-waist diagonal. Head and weapon are restored above this plate.
path((286,148),[
 ((298,143),(317,151),(331,173)),
 ((339,187),(339,209),(327,224)),
 ((316,233),(297,237),(281,227)),
 ((276,215),(275,199),(280,181)),
 ((282,168),(286,157),(286,148))],'#27333d')
path((289,151),[
 ((299,148),(311,155),(318,166)),
 ((315,173),(303,181),(287,183)),
 ((284,176),(286,160),(289,151))],'#45535f')
path((285,186),[
 ((298,182),(313,173),(320,169)),
 ((326,178),(324,192),(316,203)),
 ((306,213),(289,217),(280,211)),
 ((279,203),(283,193),(285,186))],'#202b35')
path((282,212),[
 ((295,218),(310,211),(320,201)),
 ((325,196),(331,191),(335,190)),
 ((338,207),(330,222),(316,228)),
 ((304,232),(289,231),(282,224)),
 ((281,220),(281,216),(282,212))],'#141f29')
# Shirt is near the front of the chest; side/back panel no longer has a zipper.
path((320,169),[
 ((329,174),(336,182),(336,194)),
 ((335,207),(326,218),(314,224)),
 ((316,213),(313,202),(314,190)),
 ((315,180),(318,174),(320,169))],'#101721','#0c131c',1.2)
path((317,170),[
 ((313,181),(308,189),(310,205)),
 ((311,214),(310,222),(306,227)),
 ((315,224),(320,216),(319,207)),
 ((315,191),(319,180),(322,174)),
 ((321,172),(318,170),(317,170))],'#495660','#111b25',1)
path((319,174),[
 ((316,183),(313,191),(315,204)),
 ((317,212),(313,220),(310,223))],stroke='#cad2d8',width=1.4,closed=False)
path((333,182),[
 ((337,193),(334,207),(325,215))],stroke='#778996',width=1,closed=False)
# KH2 inner shirt trim and zipper sit in the front opening.
path((323,187),[
 ((323,195),(321,203),(324,210))],stroke='#a7b5bf',width=1,closed=False)
for x,y in [(323,190),(323,194),(322,198),(322,202),(323,206)]:
    ImageDraw.Draw(overlay).line((x*AA,y*AA,(x+2)*AA,(y-1)*AA),fill='#d5dfe5',width=AA)
ImageDraw.Draw(overlay).rounded_rectangle((322*AA,208*AA,326*AA,214*AA),radius=AA,fill='#b4c0c8',outline='#344450',width=AA)
# Necklace follows neck/chest direction rather than the discarded side seam.
path((325,176),[
 ((322,182),(321,188),(325,192)),
 ((329,190),(331,185),(331,182))],stroke='#acbbc6',width=1,closed=False)
ImageDraw.Draw(overlay).polygon([(324*AA,191*AA),(322*AA,195*AA),(326*AA,198*AA),(329*AA,194*AA)],fill='#dce4ea',outline='#607482')
# Back/side folds follow the forward lean with smaller edge highlights.
path((291,157),[
 ((287,166),(286,175),(287,179))],stroke='#788794',width=.8,closed=False)
path((284,192),[
 ((283,201),(284,207),(288,210))],stroke='#5c6e7c',width=.8,closed=False)
path((288,221),[
 ((298,225),(306,224),(310,221))],stroke='#4a5d6c',width=.8,closed=False)
path((298,185),[
 ((305,184),(310,181),(313,178))],stroke='#111c26',width=1,closed=False)
overlay=overlay.resize((512,512),Image.Resampling.LANCZOS)
overlay.save(OUT/'chest_redraw_overlay.png')
before=Image.open(SRC/'frame_00_art_preview.png').convert('RGBA')
after=Image.alpha_composite(before,overlay)
after=Image.alpha_composite(after,Image.open(LAYERS/'art_pass_01/weapon_shaded_instance.png').convert('RGBA'))
for name in ('chain.png','head_occlusion.png','foreground_fingers.png'):
    after=Image.alpha_composite(after,Image.open(PILOT/name).convert('RGBA'))
pixels=np.array(after)
pixels[pixels[:,:,3]==0,:3]=0
after=Image.fromarray(pixels,'RGBA')
after.save(OUT/'frame_00_art_preview.png')
for name,color in [('Light_Background_Check.png','#e6e6e6'),('Dark_Background_Check.png','#202633')]:
    bg=Image.new('RGB',(512,512),color);bg.paste(after,(0,0),after);bg.save(OUT/name)
compare=Image.new('RGB',(1024,550),'#202633')
detail=Image.new('RGB',(960,320),'#202633')
for i,(im,title) in enumerate([(before,'Previous chest'),(after,'Redrawn jacket panel and chest opening')]):
    compare.paste(im,(i*512,32),im)
    ImageDraw.Draw(compare).text((i*512+12,10),title,fill='white')
    crop=im.crop((210,140,450,270)).resize((480,260),Image.Resampling.LANCZOS)
    detail.paste(crop,(i*480,32),crop)
    ImageDraw.Draw(detail).text((i*480+12,10),title,fill='white')
compare.save(OUT/'Art_Comparison.png');detail.save(OUT/'Upper_Body_Comparison.png')
manifest=json.loads((SRC/'manifest.json').read_text())
manifest['status']='third art pass, local chest redraw; unfinished'
manifest['source_art_pass']='art_pass_02'
assert hashlib.sha256((ROOT/'ready/run_loop/run_loop_source.png').read_bytes()).hexdigest()==manifest['source_sha256']
assert np.array_equal(np.array(before)[300:],np.array(after)[300:])
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Saved',OUT)
