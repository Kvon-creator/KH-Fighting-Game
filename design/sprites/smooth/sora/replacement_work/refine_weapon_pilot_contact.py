"""Arm/sleeve and shoulder contact polish, preserving approved grip pixels."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
L=ROOT/'ready/run_loop/layers'
SRC=L/'art_pass_05';OUT=L/'art_pass_06'
OUT.mkdir(parents=True,exist_ok=True)
AA=4
paint=Image.new('RGBA',(2048,2048))
def curve(start,segments,fill=None,stroke=None,width=1,closed=True):
    points=[start];a=start
    for b,c,end in segments:
        for j in range(1,33):
            t=j/32;u=1-t
            points.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],
                           u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    q=[(round(x*AA),round(y*AA)) for x,y in points]
    d=ImageDraw.Draw(paint)
    if fill:d.polygon(q,fill=fill)
    if stroke:d.line(q+([q[0]] if closed else []),fill=stroke,width=round(width*AA),joint='curve')

# Cuff thickness follows the curved sleeve opening and shades the skin beneath.
curve((341,209),[
 ((346,214),(353,216),(361,212)),
 ((363,213),(364,215),(363,217)),
 ((355,221),(346,217),(341,213)),
 ((340,212),(340,211),(341,209))],'#8496a3','#192733',.8)
curve((342,209),[
 ((349,214),(355,215),(362,211))],stroke='#d3dce2',width=1.2,closed=False)
curve((348,217),[
 ((352,220),(358,222),(362,219)),
 ((363,221),(364,224),(365,227)),
 ((360,227),(354,224),(351,222)),
 ((349,220),(348,218),(348,217))],'#ab7358')
# Forearm volume: highlight ridge, midtone, and elbow crease.
curve((354,223),[
 ((358,232),(360,241),(365,246)),
 ((370,251),(376,252),(382,248)),
 ((379,252),(372,256),(367,253)),
 ((360,247),(356,235),(354,223))],'#d2926c')
curve((356,224),[
 ((360,233),(363,242),(368,246)),
 ((366,241),(364,233),(362,229)),
 ((359,226),(357,224),(356,224))],'#f4c197')
curve((368,249),[
 ((372,250),(376,249),(379,248))],stroke='#8e5a43',width=.8,closed=False)
# Released arm skin transition and a slight underside shadow at sleeve edge.
curve((240,191),[
 ((243,193),(244,195),(243,198)),
 ((239,199),(235,202),(232,205)),
 ((231,204),(231,202),(233,199)),
 ((236,195),(237,193),(240,191))],'#c38a67')
curve((234,198),[
 ((231,203),(227,208),(224,210))],stroke='#f7c89e',width=.8,closed=False)
# Contact darkening under the resting weapon and subtle sleeve folds.
curve((339,189),[
 ((346,191),(352,195),(358,200)),
 ((361,203),(361,207),(357,210)),
 ((352,206),(348,204),(344,203)),
 ((341,199),(339,194),(339,189))],'#182733')
curve((342,198),[
 ((346,201),(351,204),(355,206))],stroke='#536b7b',width=.8,closed=False)
curve((335,212),[
 ((337,217),(334,221),(330,224))],stroke='#0e1c28',width=1,closed=False)
curve((337,212),[
 ((339,216),(337,219),(336,220))],stroke='#667f90',width=.7,closed=False)
overlay=paint.resize((512,512),Image.Resampling.LANCZOS)
overlay.save(OUT/'contact_and_arm_overlay.png')
before=Image.open(SRC/'frame_00_art_preview.png').convert('RGBA')
after=Image.alpha_composite(before,overlay)
# Put the identical weapon back over fabric contact shading.
after=Image.alpha_composite(after,Image.open(SRC/'weapon_instance.png').convert('RGBA'))
after=Image.alpha_composite(after,Image.open(L/'pilot_v3/head_occlusion.png').convert('RGBA'))
after=Image.alpha_composite(after,Image.open(SRC/'foreground_grip.png').convert('RGBA'))
# Preserve every pixel in the approved hand region, including cuff silhouettes.
after.paste(before.crop((384,203,424,248)),(384,203))
a=np.array(after);a[a[:,:,3]==0,:3]=0
after=Image.fromarray(a,'RGBA');after.save(OUT/'frame_00_art_preview.png')
compare=Image.new('RGB',(1024,550),'#202633')
detail=Image.new('RGB',(960,340),'#202633')
for i,(im,title) in enumerate([(before,'Approved grip, prior arm joins'),(after,'Sleeve joins, elbow volume and shoulder contact')]):
    compare.paste(im,(i*512,32),im);ImageDraw.Draw(compare).text((i*512+12,10),title,fill='white')
    crop=im.crop((210,175,450,270)).resize((480,190),Image.Resampling.LANCZOS)
    detail.paste(crop,(i*480,32),crop);ImageDraw.Draw(detail).text((i*480+12,10),title,fill='white')
compare.save(OUT/'Art_Comparison.png');detail.save(OUT/'Arm_Comparison.png')
old=np.array(before);new=np.array(after)
assert np.array_equal(old[203:248,384:424],new[203:248,384:424])
assert np.array_equal(old[330:],new[330:])
m=json.loads((SRC/'manifest.json').read_text())
assert hashlib.sha256((ROOT/'ready/run_loop/run_loop_source.png').read_bytes()).hexdigest()==m['source_sha256']
m['status']='sixth local pass: sleeve and contact refinement, unfinished'
m['source_art_pass']='art_pass_05'
m['approved_grip_region_preserved']=[384,203,424,248]
(OUT/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('Saved',OUT)
