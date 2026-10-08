"""Pose-specific cleanup of the first lowering drawing, preserving source art."""
from pathlib import Path
import json,math,hashlib,argparse
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent;READY=ROOT/'ready';L=READY/'run_loop/layers'
parser=argparse.ArgumentParser();parser.add_argument('--version',choices=('v2','v3'),default='v2');args=parser.parse_args()
OUT=READY/f'run_start/refinement_{args.version}'
OUT.mkdir(parents=True,exist_ok=True)
source=READY/'run_start/run_start_source.png'
original=Image.new('RGBA',(512,512));original.paste(Image.open(source).convert('RGBA').crop((445,0,889,450)),(0,0))
body=original.copy();mask=Image.new('L',(512,512));d=ImageDraw.Draw(mask)
d.polygon([(43,105),(127,105),(222,236),(237,266),(194,274),(42,155)],fill=255)
d.polygon([(168,235),(233,225),(278,259),(281,313),(242,326),(186,298)],fill=255)
d.rectangle((164,245,201,292),fill=255)
d.rectangle((238,301,277,380),fill=255)
# Remove the two old hands/forearms, retaining sleeve and shoulder contours.
d.polygon([(224,231),(266,228),(314,250),(329,270),(307,285),(230,291),(212,260)],fill=255)
body.putalpha(Image.composite(Image.new('L',(512,512),0),body.getchannel('A'),mask))
paint=Image.new('RGBA',(2048,2048))
def curve(start,segs,fill,stroke='#172029',width=1.5):
    pts=[start];a=start
    for b,c,end in segs:
        for j in range(1,33):
            t=j/32;u=1-t
            pts.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    q=[(int(x*4),int(y*4)) for x,y in pts];p=ImageDraw.Draw(paint)
    p.polygon(q,fill=fill)
    if stroke:p.line(q+[q[0]],fill=stroke,width=round(width*4),joint='curve')
# Narrow underlying jacket repair, not a wholesale torso replacement.
curve((246,228),[
 ((265,224),(282,228),(296,244)),
 ((296,260),(283,281),(267,291)),
 ((251,292),(232,280),(219,267)),
 ((222,252),(232,237),(246,228))],'#252d35')
curve((243,233),[
 ((252,228),(268,231),(277,239)),
 ((269,252),(247,266),(231,267)),
 ((231,253),(235,240),(243,233))],'#3a4651',None)
curve((275,246),[
 ((288,248),(289,262),(278,276)),
 ((261,288),(245,278),(236,273)),
 ((252,276),(270,267),(275,246))],'#151f29',None)
# Pants hidden by the old guard/chain are rebuilt with a curved edge and folds.
curve((217,285),[
 ((240,279),(266,286),(277,303)),
 ((286,323),(277,346),(265,358)),
 ((250,357),(238,340),(235,319)),
 ((225,314),(214,303),(217,285))],'#25292f')
curve((229,291),[
 ((244,287),(258,292),(266,305)),
 ((265,317),(258,330),(254,337)),
 ((248,321),(240,308),(229,301)),
 ((227,297),(227,294),(229,291))],'#363c44',None)
# Holding arm reconnects the near sleeve to the low guard grip.
curve((322,245),[
 ((328,249),(332,259),(326,270)),
 ((310,287),(281,292),(242,290)),
 ((229,291),(218,288),(219,281)),
 ((228,270),(243,269),(254,274)),
 ((278,277),(299,271),(307,260)),
 ((311,252),(317,247),(322,245))],'#e9ad82')
curve((319,251),[
 ((323,258),(317,267),(305,275)),
 ((290,284),(264,287),(243,284)),
 ((254,289),(290,289),(308,282)),
 ((325,277),(330,264),(319,251))],'#bd7e5c',None)
# Freed far arm sits on the left side rather than retaining a second grip.
curve((220,236),[
 ((226,238),(233,244),(231,251)),
 ((222,262),(216,274),(207,278)),
 ((199,276),(199,270),(204,261)),
 ((208,250),(211,242),(220,236))],'#eab087')
curve((206,269),[
 ((214,267),(222,274),(218,283)),
 ((212,290),(201,289),(198,282)),
 ((196,277),(201,272),(206,269))],'#1b2834')
repair=paint.resize((512,512),Image.Resampling.LANCZOS);repair.save(OUT/'frame_01_local_repair.png')
body=Image.alpha_composite(body,repair)
# Keep the original shorts/legs below the local guard repair, eliminating the
# earlier inferred cloth tail in the gap occupied by the original key chain.
lower=original.crop((0,317,512,512))
ld=ImageDraw.Draw(lower)
if args.version=='v3':
    ld.polygon([(247,0),(264,0),(268,25),(286,30),(288,52),(281,66),(247,66),(236,60),(236,33),(247,25)],fill=(0,0,0,0))
else:
    ld.rectangle((231,0,282,68),fill=(0,0,0,0))
body.paste(lower,(0,317))
if args.version=='v3':
    paint=Image.new('RGBA',(2048,2048))
    curve((229,314),[
      ((238,311),(248,314),(251,320)),
      ((254,330),(239,344),(228,350)),
      ((222,349),(224,337),(229,314))],'#23272e')
    curve((232,317),[
      ((239,316),(246,318),(247,323)),
      ((244,330),(237,334),(230,337)),
      ((232,330),(230,325),(232,317))],'#30353c',None)
    stitch=ImageDraw.Draw(paint)
    stitch.line([(224*4,348*4),(232*4,344*4),(240*4,338*4)],fill='#bcc3c9',width=5,joint='curve')
    body=Image.alpha_composite(body,paint.resize((512,512),Image.Resampling.LANCZOS))
body.save(OUT/'frame_01_body_plate.png')
hand=(235,270);theta=math.radians(220);c,s=math.cos(theta),math.sin(theta);yaw=math.radians(8)
H=np.array([[c,-s,hand[0]],[s,c,hand[1]],[0,0,1]])@np.array([[math.cos(yaw),0,0],[0,1,0],[-math.sin(yaw)/1400,0,1]])@np.array([[1,0,-77],[0,1,-70],[0,0,1]])
inv=np.linalg.inv(H);inv/=inv[2,2]
result=body
for file,name in [('kingdom_key_master_finished.png','frame_01_weapon.png'),('grip_master_space.png','frame_01_grip.png')]:
    layer=Image.open(L/'art_pass_05'/file).convert('RGBA').transform((512,512),Image.Transform.PERSPECTIVE,tuple(inv.flatten()[:8]),Image.Resampling.BICUBIC)
    layer.save(OUT/name);result=Image.alpha_composite(result,layer)
q=H@np.array([34,70,1]);pom=q[:2]/q[2]
chain=Image.new('RGBA',(512,512));cd=ImageDraw.Draw(chain);cd.line([tuple(pom),(pom[0],pom[1]+35)],fill='#b2c0cc',width=2)
cd.ellipse((pom[0]-5,pom[1]+31,pom[0]+5,pom[1]+41),fill='#a7b7c4',outline='#192936')
result=Image.alpha_composite(result,chain)
pixels=np.array(result);pixels[pixels[:,:,3]==0,:3]=0
result=Image.fromarray(pixels,'RGBA');result.save(OUT/'sora_run_start_01.png')
comparison=Image.new('RGB',(1024,550),'#202633')
for i,(im,title) in enumerate([(original,'Original lowering pose'),(result,'Pose-specific guard / arm repair')]):
    comparison.paste(im,(i*512,32),im);ImageDraw.Draw(comparison).text((i*512+12,10),title,fill='white')
comparison.save(OUT/'Frame_01_Comparison.png')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'
(OUT/'frame_01_manifest.json').write_text(json.dumps({'status':'pose-specific refinement review, not finished idle-quality art','source_crop':[445,0,889,450],'hand_anchor':hand,'master_to_screen_homography':H.tolist(),'limitations':['Pants/chest areas concealed by original weapon are manually inferred.','Forearm proportions, outline joins and freed-hand silhouette still need art review.','Original head and most clothing/legs preserved.']},indent=2),encoding='utf-8')
print('Saved pose-specific lowering refinement:',OUT)
