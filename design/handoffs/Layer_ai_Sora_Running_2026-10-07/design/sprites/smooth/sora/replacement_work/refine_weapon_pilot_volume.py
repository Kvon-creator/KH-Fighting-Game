"""Second local art pass: garment volume, shoulder panels and alpha cleanup."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parent
LAYERS=ROOT/'ready/run_loop/layers'
SRC=LAYERS/'art_pass_01'
PILOT=LAYERS/'pilot_v3'
OUT=LAYERS/'art_pass_02'
OUT.mkdir(parents=True,exist_ok=True)
SIZE=(512,512); AA=4

def canvas(): return Image.new('RGBA',(2048,2048))
def curve(im,start,segments,fill=None,stroke=None,width=1,closed=True):
    points=[start];a=start
    for b,c,end in segments:
        for j in range(1,33):
            t=j/32;u=1-t
            points.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],
                           u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    q=[(round(x*AA),round(y*AA)) for x,y in points]
    d=ImageDraw.Draw(im)
    if fill: d.polygon(q,fill=fill)
    if stroke: d.line(q+([q[0]] if closed else []),fill=stroke,width=round(width*AA),joint='curve')
def finish(im): return im.resize(SIZE,Image.Resampling.LANCZOS)

base=Image.open(SRC/'frame_00_art_preview.png').convert('RGBA')
# Smooth volume limited to the reconstructed jacket, preserving its silhouette.
garment=np.array(Image.open(PILOT/'body_reconstruction.png').convert('RGBA'))
rgb=garment[:,:,:3].astype(float)
y,x=np.indices((512,512))
darkcloth=(garment[:,:,3]>0)&(rgb[:,:,0]<105)&(rgb[:,:,2]<120)&(rgb[:,:,0]<rgb[:,:,2]+18)
region=(x>235)&(x<340)&(y>150)&(y<234)
coverage=darkcloth&region
light=np.exp(-((x-275)/28)**2-((y-172)/21)**2)
fold=np.exp(-((x-285)/18)**2-((y-211)/16)**2)
shadow=np.exp(-((x-324)/12)**2-((y-209)/19)**2)
volume=np.zeros((512,512,4),dtype=np.uint8)
volume[:,:,:3]=[115,135,150]
volume[:,:,3]=(coverage*light*35).astype(np.uint8)
highlight=Image.fromarray(volume,'RGBA')
volume[:,:,:3]=[7,13,20]
volume[:,:,3]=(coverage*(fold*34+shadow*58)).astype(np.uint8)
shade=Image.fromarray(volume,'RGBA')
soft=Image.alpha_composite(highlight,shade)
soft.save(OUT/'jacket_volume_overlay.png')
base=Image.alpha_composite(base,soft)

draw=canvas()
# Replace ring-like construction panels with curved inset sleeve armour.
for cx,cy in [(255,178),(354,191)]:
    curve(draw,(cx-15,cy-6),[
       ((cx-12,cy-15),(cx+5,cy-17),(cx+14,cy-7)),
       ((cx+16,cy-2),(cx+12,cy+5),(cx+4,cy+7)),
       ((cx-5,cy+8),(cx-15,cy+3),(cx-15,cy-6))],'#26333d','#111b23',1.5)
    curve(draw,(cx-12,cy-7),[
       ((cx-6,cy-15),(cx+5,cy-13),(cx+10,cy-7)),
       ((cx+11,cy-3),(cx+4,cy-1),(cx-1,cy-2)),
       ((cx-7,cy-3),(cx-13,cy-3),(cx-12,cy-7))],'#50616e')
    curve(draw,(cx-13,cy-2),[
       ((cx-4,cy+6),(cx+7,cy+6),(cx+13,cy-2))],stroke='#8797a2',width=1.2,closed=False)
    curve(draw,(cx-11,cy-7),[
       ((cx-5,cy-13),(cx+3,cy-12),(cx+8,cy-9))],stroke='#9cabb5',width=.8,closed=False)
    d=ImageDraw.Draw(draw)
    for dx,dy in [(-11,0),(10,0)]:
        d.ellipse(((cx+dx-1)*AA,(cy+dy-1)*AA,(cx+dx+1)*AA,(cy+dy+1)*AA),fill='#a0adb6',outline='#19242d',width=AA)
# Folds link the back panel, armhole and cropped jacket hem.
curve(draw,(269,183),[
 ((273,190),(276,193),(283,195))],stroke='#17212a',width=1.4,closed=False)
curve(draw,(249,195),[
 ((252,203),(257,207),(263,208))],stroke='#131e27',width=1.3,closed=False)
curve(draw,(250,197),[
 ((254,202),(258,204),(261,204))],stroke='#64747f',width=.7,closed=False)
curve(draw,(284,219),[
 ((295,223),(306,224),(314,221))],stroke='#111c25',width=1.2,closed=False)
# Side accent has a black base and restrained yellow face, avoiding a bright blob.
curve(draw,(267,174),[
 ((265,181),(267,186),(269,190)),
 ((271,188),(271,184),(270,179)),
 ((270,176),(269,174),(267,174))],'#b6952e','#283039',.8)
# Free glove receives a cuff, anatomical knuckle planes and finger separation.
curve(draw,(215,215),[
 ((221,210),(231,214),(234,220)),
 ((231,226),(225,232),(219,232)),
 ((212,231),(209,226),(215,215))],'#192632','#101a23',1)
curve(draw,(215,216),[
 ((221,214),(227,217),(229,219)),
 ((227,222),(219,223),(214,220)),
 ((213,219),(214,217),(215,216))],'#435363')
curve(draw,(215,224),[
 ((220,225),(225,225),(229,221))],stroke='#7d8e9b',width=.9,closed=False)
for xx,yy in [(215,226),(220,228),(225,226)]:
    curve(draw,(xx,yy),[((xx+1,yy-2),(xx+2,yy-3),(xx+3,yy-4))],stroke='#0b151e',width=.8,closed=False)
# A narrow forearm highlight follows its volume rather than a long white line.
curve(draw,(359,226),[
 ((362,234),(365,240),(371,242)),
 ((369,241),(365,237),(365,233)),
 ((362,229),(361,227),(359,226))],'#f6c499')
curve(draw,(369,250),[
 ((372,252),(378,252),(382,250))],stroke='#9f674d',width=.9,closed=False)
overlay=finish(draw)
overlay.save(OUT/'sleeve_glove_fold_overlay.png')
base=Image.alpha_composite(base,overlay)
# Maintain foreground weapon, head and grip ordering over the new clothing.
base=Image.alpha_composite(base,Image.open(SRC/'weapon_shaded_instance.png').convert('RGBA'))
for name in ('chain.png','head_occlusion.png','foreground_fingers.png'):
    base=Image.alpha_composite(base,Image.open(PILOT/name).convert('RGBA'))
data=np.array(base)
data[data[:,:,3]==0,:3]=0
base=Image.fromarray(data,'RGBA')
base.save(OUT/'frame_00_art_preview.png')
before=Image.open(SRC/'frame_00_art_preview.png').convert('RGBA')
comparison=Image.new('RGB',(1024,550),'#202633')
for i,(im,title) in enumerate([(before,'Previous detail pass'),(base,'Sleeve volume, garment folds and glove refinement')]):
    comparison.paste(im,(512*i,32),im)
    ImageDraw.Draw(comparison).text((512*i+12,10),title,fill='white')
comparison.save(OUT/'Art_Comparison.png')
# Actual foreground compositing checks avoid interpreting hidden RGB as artwork.
for name,color in [('Light_Background_Check.png',(230,230,230,255)),('Dark_Background_Check.png',(32,38,51,255))]:
    check=Image.new('RGBA',SIZE,color);check.alpha_composite(base)
    check.convert('RGB').save(OUT/name)
closeup=Image.new('RGB',(960,480),'#202633')
for i,im in enumerate((before,base)):
    crop=im.crop((210,140,450,260)).resize((480,240),Image.Resampling.LANCZOS)
    closeup.paste(crop,(i*480,40),crop)
ImageDraw.Draw(closeup).text((12,12),'Previous upper body',fill='white')
ImageDraw.Draw(closeup).text((492,12),'Refined upper body',fill='white')
closeup.save(OUT/'Upper_Body_Comparison.png')
m=json.loads((SRC/'manifest.json').read_text())
assert hashlib.sha256((ROOT/'ready/run_loop/run_loop_source.png').read_bytes()).hexdigest()==m['source_sha256']
m['status']='second local art pass, unfinished and awaiting visual review'
m['source_art_pass']='art_pass_01'
m['fully_transparent_rgb_cleared']=True
(OUT/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('Saved',OUT)
