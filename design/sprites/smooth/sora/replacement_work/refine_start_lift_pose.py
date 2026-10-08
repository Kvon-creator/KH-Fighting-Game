"""Individually drawn arm/cloth cleanup for the next actual run-start pose."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent;READY=ROOT/'ready';L=READY/'run_loop/layers';OUT=READY/'run_start/refinement_v3'
OUT.mkdir(parents=True,exist_ok=True);source=READY/'run_start/run_start_source.png'
original=Image.new('RGBA',(512,512));original.paste(Image.open(source).convert('RGBA').crop((889,0,1333,450)),(0,0))
body=original.copy();mask=Image.new('L',(512,512));md=ImageDraw.Draw(mask)
md.polygon([(13,132),(109,127),(193,215),(225,246),(191,268),(17,190)],fill=255)
md.polygon([(153,219),(191,211),(237,229),(255,267),(238,295),(214,314),(161,282)],fill=255)
md.polygon([(177,217),(225,219),(267,231),(314,244),(313,268),(252,276),(186,267)],fill=255)
md.polygon([(225,281),(248,281),(256,321),(257,349),(246,355),(222,348),(218,329),(228,312)],fill=255)
body.putalpha(Image.composite(Image.new('L',(512,512),0),body.getchannel('A'),mask))
paint=Image.new('RGBA',(2048,2048))
def curve(start,segs,fill,outline='#16212b',width=1.5):
    pts=[start];a=start
    for b,c,end in segs:
        for j in range(1,33):
            t=j/32;u=1-t
            pts.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    p=[(round(x*4),round(y*4)) for x,y in pts];d=ImageDraw.Draw(paint)
    d.polygon(p,fill=fill)
    if outline:d.line(p+[p[0]],fill=outline,width=round(width*4),joint='curve')
# Rebuild only small jacket areas formerly hidden by the chest grip.
curve((201,221),[
 ((219,214),(248,219),(264,232)),
 ((278,250),(267,270),(253,282)),
 ((228,284),(204,274),(187,259)),
 ((187,245),(193,229),(201,221))],'#252e37')
curve((202,226),[
 ((218,220),(237,225),(244,233)),
 ((234,245),(214,254),(196,252)),
 ((194,243),(198,232),(202,226))],'#3e4b56',None)
curve((243,243),[
 ((256,240),(269,248),(267,258)),
 ((258,273),(233,276),(210,266)),
 ((225,267),(239,256),(243,243))],'#15212c',None)
# Curved red side panel reconnects to the original KH2 waist details.
curve((166,261),[
 ((181,263),(198,273),(215,276)),
 ((211,285),(197,289),(184,284)),
 ((175,280),(166,271),(166,261))],'#b5262a')
curve((171,266),[
 ((183,270),(198,277),(207,278)),
 ((197,283),(179,278),(171,266))],'#ee4937',None)
# Cloth at the former guard location, trimmed to match shorts silhouette.
curve((173,273),[
 ((190,269),(207,273),(219,286)),
 ((224,295),(221,307),(216,314)),
 ((197,315),(179,304),(170,289)),
 ((168,283),(168,277),(173,273))],'#252a31')
curve((179,278),[
 ((191,275),(204,281),(212,290)),
 ((210,301),(199,307),(188,306)),
 ((181,297),(176,287),(179,278))],'#3a4149',None)
# Near arm raises the holding hand; different elbow/forearm articulation.
curve((309,241),[
 ((315,240),(322,243),(327,252)),
 ((334,261),(336,269),(330,274)),
 ((319,279),(301,267),(286,258)),
 ((281,252),(285,244),(292,241)),
 ((302,238),(308,248),(317,253)),
 ((314,248),(309,245),(309,241))],'#e9ac82')
curve((324,254),[
 ((330,262),(329,268),(322,269)),
 ((310,266),(296,257),(291,251)),
 ((289,254),(294,260),(301,265)),
 ((318,278),(332,277),(333,267)),
 ((334,262),(328,256),(324,254))],'#bd7f5f',None)
# Far arm releases toward the hip.
curve((207,215),[
 ((213,217),(217,224),(214,230)),
 ((210,241),(199,251),(190,258)),
 ((184,258),(181,254),(183,248)),
 ((191,237),(198,223),(207,215))],'#eab187')
curve((186,250),[
 ((194,246),(202,251),(202,258)),
 ((201,266),(190,271),(184,266)),
 ((178,261),(180,254),(186,250))],'#1d2b36')
repair=paint.resize((512,512),Image.Resampling.LANCZOS)
rp=np.array(repair);rgb=rp[:,:,:3].astype(float)
cloth=(rp[:,:,3]>0)&(rgb[:,:,0]<100)&(rgb[:,:,2]>rgb[:,:,0]+4)
lum=.2126*rgb[:,:,0]+.7152*rgb[:,:,1]+.0722*rgb[:,:,2]
neutral=np.stack([lum*.94,lum*.97,lum],axis=2)
rp[:,:,:3][cloth]=np.clip(neutral[cloth],0,255).astype('uint8')
repair=Image.fromarray(rp,'RGBA');repair.save(OUT/'frame_02_local_repair.png')
body=Image.alpha_composite(body,repair)
lower=original.crop((0,305,512,512));ld=ImageDraw.Draw(lower)
ld.polygon([(227,0),(247,0),(255,24),(254,44),(247,50),(222,43),(218,27),(225,12)],fill=(0,0,0,0))
body.paste(lower,(0,305))
paint=Image.new('RGBA',(2048,2048))
curve((211,301),[
 ((223,297),(237,300),(242,309)),
 ((244,320),(230,334),(217,341)),
 ((210,337),(208,319),(211,301))],'#24282f')
curve((214,304),[
 ((223,302),(232,305),(234,311)),
 ((232,318),(223,324),(215,327)),
 ((215,319),(212,311),(214,304))],'#343a41',None)
stitch=ImageDraw.Draw(paint)
stitch.line([(207*4,329*4),(217*4,332*4),(227*4,329*4)],fill='#bec7ce',width=5,joint='curve')
body=Image.alpha_composite(body,paint.resize((512,512),Image.Resampling.LANCZOS));body.save(OUT/'frame_02_body_plate.png')
hand=(306,233);theta=math.radians(214);c,s=math.cos(theta),math.sin(theta);yaw=math.radians(12)
H=np.array([[c,-s,hand[0]],[s,c,hand[1]],[0,0,1]])@np.array([[math.cos(yaw),0,0],[0,1,0],[-math.sin(yaw)/1400,0,1]])@np.array([[1,0,-77],[0,1,-70],[0,0,1]])
inv=np.linalg.inv(H);inv/=inv[2,2];result=body
for filename,name in [('kingdom_key_master_finished.png','frame_02_weapon.png'),('grip_master_space.png','frame_02_grip.png')]:
    layer=Image.open(L/'art_pass_05'/filename).convert('RGBA').transform((512,512),Image.Transform.PERSPECTIVE,tuple(inv.flatten()[:8]),Image.Resampling.BICUBIC)
    layer.save(OUT/name);result=Image.alpha_composite(result,layer)
q=H@np.array([34,70,1]);pom=q[:2]/q[2];chain=Image.new('RGBA',(512,512));cd=ImageDraw.Draw(chain)
for i in range(7):cd.ellipse((pom[0]-2,pom[1]+i*4.5,pom[0]+2,pom[1]+i*4.5+6),outline='#a7b8c6',width=1)
cd.ellipse((pom[0]-5,pom[1]+31,pom[0]+5,pom[1]+41),fill='#a9bac8',outline='#1b2b36')
result=Image.alpha_composite(result,chain);a=np.array(result);a[a[:,:,3]==0,:3]=0;result=Image.fromarray(a,'RGBA')
result.save(OUT/'sora_run_start_02.png')
comparison=Image.new('RGB',(1024,550),'#202633')
for i,(im,title) in enumerate([(original,'Original forward lean'),(result,'Individually articulated lift and released arm')]):
    comparison.paste(im,(i*512,32),im);ImageDraw.Draw(comparison).text((i*512+12,10),title,fill='white')
comparison.save(OUT/'Frame_02_Comparison.png')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256'
(OUT/'frame_02_manifest.json').write_text(json.dumps({'status':'individual lift refinement, still under art review','source_crop':[889,0,1333,450],'hand_anchor':hand,'master_to_screen_homography':H.tolist(),'limitations':['Inferred clothing and forearm anatomy need refinement against idle.','Source head and most legs retained; no engine test.']},indent=2),encoding='utf-8')
print('Saved individual run-start lift:',OUT)
