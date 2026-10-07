"""Non-generative art-detail pass on the preserved rigid-layer pilot."""
from pathlib import Path
import json
import hashlib
import math
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'ready/run_loop/layers/pilot_v3'
OUT=ROOT/'ready/run_loop/layers/art_pass_01'
OUT.mkdir(parents=True,exist_ok=True)
AA=4
SIZE=(512,512)

def canvas(size=SIZE):
    return Image.new('RGBA',(size[0]*AA,size[1]*AA))

def path(im,start,segments,color,stroke=None,width=1,closed=True):
    points=[start]; a=start
    for b,c,end in segments:
        for j in range(1,25):
            t=j/24; u=1-t
            points.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],
                           u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    points=[(round(x*AA),round(y*AA)) for x,y in points]
    d=ImageDraw.Draw(im)
    if closed: d.polygon(points,fill=color)
    if stroke: d.line(points+([points[0]] if closed else []),fill=stroke,width=round(width*AA),joint='curve')

def finish(im):
    return im.resize((im.width//AA,im.height//AA),Image.Resampling.LANCZOS)

detail=canvas()
# Open short jacket, inset shirt, folded lapels and white piping.
path(detail,(302,151),[
 ((312,154),(321,163),(323,177)),
 ((328,187),(327,201),(317,212)),
 ((308,208),(301,195),(298,183)),
 ((298,173),(301,161),(302,151))],'#111923','#11151b',1.5)
path(detail,(296,149),[
 ((295,163),(290,174),(293,189)),
 ((294,200),(301,213),(312,220)),
 ((304,216),(294,210),(289,195)),
 ((284,179),(291,155),(296,149))],'#495661','#131b24',1)
path(detail,(304,154),[
 ((310,164),(319,170),(323,176)),
 ((325,182),(327,188),(326,194)),
 ((322,183),(316,179),(310,174)),
 ((306,167),(304,160),(304,154))],'#53616c','#171e25',1)
path(detail,(297,155),[
 ((293,173),(293,190),(301,204)),
 ((305,212),(312,218),(317,219))],None,'#dae0e4',1.4,False)
path(detail,(306,157),[
 ((312,169),(320,173),(324,185))],None,'#d7dde2',1.3,False)
# Zipper and teeth follow the chest curve instead of straight drafting lines.
path(detail,(312,179),[
 ((314,190),(312,201),(319,210))],None,'#929fa9',1.2,False)
for x,y in [(312,181),(312.5,185),(313,189),(313,193),(313.5,197),(314.5,201),(316,205)]:
    ImageDraw.Draw(detail).line((x*AA,y*AA,(x+3)*AA,(y-.5)*AA),fill='#d4dbe0',width=AA)
ImageDraw.Draw(detail).rounded_rectangle((315*AA,203*AA,320*AA,211*AA),radius=AA,fill='#b2bec8',outline='#263441',width=AA)
# Necklace drapes from the surviving collar into the visible shirt.
path(detail,(311,160),[
 ((309,172),(310,183),(316,187)),
 ((321,184),(322,178),(323,171))],None,'#b1bec9',1,False)
ImageDraw.Draw(detail).polygon([(315*AA,185*AA),(313*AA,190*AA),(317*AA,194*AA),(320*AA,188*AA)],fill='#e3e9ee',outline='#626f7b')
# Yellow KH2 accents sit at the side seam and sleeve, not across the shirt.
path(detail,(273,160),[
 ((266,169),(261,183),(265,194)),
 ((266,196),(270,196),(270,192)),
 ((266,181),(271,169),(277,163)),
 ((278,161),(276,159),(273,160))],'#d7ae32','#262522',1)
path(detail,(271,163),[
 ((267,169),(264,178),(265,184))],None,'#fbe471',1,False)
# Sleeve seam, inset shoulder shading and small fastening studs.
for x,y,flip in [(255,178,False),(354,191,True)]:
    path(detail,(x-13,y-4),[
      ((x-7,y-15),(x+9,y-14),(x+13,y-4)),
      ((x+9,y+3),(x-7,y+6),(x-13,y-4))],'#18242e','#172029',1)
    path(detail,(x-10,y-7),[
      ((x-2,y-13),(x+8,y-11),(x+10,y-5)),
      ((x+3,y-3),(x-6,y-3),(x-10,y-7))],'#53626d',None)
    path(detail,(x-11,y-2),[
      ((x-4,y+6),(x+7,y+5),(x+12,y-3))],None,'#bfc8ce',1.5,False)
    for dx in (-9,9):
        ImageDraw.Draw(detail).ellipse(((x+dx-1)*AA,(y-2)*AA,(x+dx+1)*AA,y*AA),fill='#d4dce2')
# Jacket fold shading near waist and restrained reflected edge light.
path(detail,(273,199),[
 ((276,210),(291,217),(301,216)),
 ((295,219),(276,220),(266,211)),
 ((265,207),(267,202),(273,199))],'#111a23',None)
path(detail,(241,205),[
 ((247,214),(259,218),(266,219))],None,'#67737d',1,False)
path(detail,(245,227),[
 ((253,231),(262,235),(271,233))],None,'#ff7960',1,False)
path(detail,(256,238),[
 ((261,240),(270,237),(276,233))],None,'#751b24',1.5,False)
# Visible forearm gains a midtone band, elbow crease and glove panel edges.
path(detail,(357,221),[
 ((360,230),(363,245),(374,249)),
 ((382,248),(391,241),(397,234)),
 ((392,244),(382,253),(373,253)),
 ((363,251),(359,239),(357,221))],'#d79570',None)
path(detail,(369,247),[
 ((372,245),(375,244),(378,244))],None,'#9c674e',1,False)
path(detail,(358,223),[
 ((361,230),(362,236),(365,239))],None,'#ffd6ac',1,False)
path(detail,(399,218),[
 ((406,212),(415,216),(418,223)),
 ((414,225),(412,228),(408,228)),
 ((404,225),(400,222),(399,218))],'#334453','#0d1720',1)
path(detail,(402,216),[
 ((408,215),(413,219),(415,222))],None,'#738492',1,False)
detail=finish(detail)
detail.save(OUT/'art_detail_overlay.png')

# Add metallic shading in master space; retain the exact alpha and geometry.
master=Image.open(SRC/'kingdom_key_master.png').convert('RGBA')
pixels=np.array(master).astype(float)
yy,xx=np.indices(pixels.shape[:2])
gold=(pixels[:,:,0]>145)&(pixels[:,:,1]>100)&(pixels[:,:,2]<110)&(pixels[:,:,3]>0)
silver=(pixels[:,:,0]>85)&(np.abs(pixels[:,:,0]-pixels[:,:,1])<35)&(pixels[:,:,2]>90)&(pixels[:,:,3]>0)
factor=np.ones(pixels.shape[:2])
factor[gold]=(1.1-.22*yy/150)[gold]
factor[silver]=(1.05-.12*yy/150+.03*np.cos(xx/35))[silver]
pixels[:,:,:3]=np.clip(pixels[:,:,:3]*factor[:,:,None],0,255)
painted=Image.fromarray(pixels.astype('uint8'),'RGBA')
metal=canvas(master.size)
md=ImageDraw.Draw(metal)
for x,y in [(43,42),(108,42),(43,98),(108,98)]:
    md.ellipse(((x-2)*AA,(y-2)*AA,(x+2)*AA,(y+2)*AA),fill='#b2851e',outline='#6d521a',width=AA)
    md.ellipse(((x-1)*AA,(y-2)*AA,(x+1)*AA,y*AA),fill='#fff19a')
md.line((47*AA,36*AA,104*AA,36*AA),fill='#fff2a0',width=AA)
md.line((35*AA,48*AA,35*AA,89*AA),fill='#ffe57c',width=AA)
metal=finish(metal)
painted=Image.alpha_composite(painted,metal)
painted.putalpha(master.getchannel('A'))
painted.save(OUT/'kingdom_key_master_shaded.png')
manifest=json.loads((SRC/'manifest.json').read_text())
inverse=np.linalg.inv(np.array(manifest['master_to_screen_homography']))
inverse/=inverse[2,2]
weapon=painted.transform(SIZE,Image.Transform.PERSPECTIVE,tuple(inverse.flatten()[:8]),Image.Resampling.BICUBIC)
weapon.save(OUT/'weapon_shaded_instance.png')
body=Image.open(SRC/'body_clean_plate.png').convert('RGBA')
arm=Image.open(SRC/'holding_arm.png').convert('RGBA')
preview=Image.alpha_composite(body,arm)
preview=Image.alpha_composite(preview,detail)
preview=Image.alpha_composite(preview,weapon)
for name in ('chain.png','head_occlusion.png','foreground_fingers.png'):
    preview=Image.alpha_composite(preview,Image.open(SRC/name).convert('RGBA'))
preview.save(OUT/'frame_00_art_preview.png')
before=Image.open(SRC/'frame_00_construction_preview.png').convert('RGBA')
comparison=Image.new('RGB',(1024,550),'#202633')
for i,(im,title) in enumerate([(before,'Construction draft'),(preview,'Local jacket, arm and metal detail pass')]):
    comparison.paste(im,(i*512,32),im)
    ImageDraw.Draw(comparison).text((i*512+12,10),title,fill='white')
comparison.save(OUT/'Art_Comparison.png')
assert np.array_equal(np.array(master)[:,:,3],np.array(painted)[:,:,3])
source=ROOT/'ready/run_loop/run_loop_source.png'
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
manifest['status']='first local art-detail pass, needs visual review'
manifest['geometry_preserved']=True
manifest['source_pilot']='pilot_v3'
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Saved art pass:',OUT)
