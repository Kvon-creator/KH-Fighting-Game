"""Remaining genuine source poses with rigid carry; review, not engine assets."""
from pathlib import Path
import json,hashlib,math,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parent;READY=ROOT/'ready';L=READY/'run_loop/layers'
parser=argparse.ArgumentParser();parser.add_argument('--animation',choices=('run_loop','run_start'),default='run_loop');args=parser.parse_args()
ANIM=args.animation;TARGET=READY/ANIM/'layers'
source=READY/ANIM/f'{ANIM}_source.png'
sheet=Image.open(source).convert('RGBA')
expected='1abc5a81595d4e6c8896c020fe77ec003191c616a23c6e8c93643e7cb043f256' if ANIM=='run_start' else '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
def load(p):return Image.open(p).convert('RGBA')
def shift(im,dx,dy):return im.transform((512,512),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC)
def path(im,start,segs,fill,outline='#19222b'):
    pts=[start];a=start
    for b,c,end in segs:
        for j in range(1,33):
            t=j/32;u=1-t
            pts.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    d=ImageDraw.Draw(im);p=[(round(x*4),round(y*4)) for x,y in pts]
    d.polygon(p,fill=fill);d.line(p+[p[0]],fill=outline,width=6,joint='curve')
configs={
 3:((1333,0,1774,450),(-40,10),(365,235),24,218),
 4:((0,450,445,887),(-28,-28),(377,197),23,217),
 5:((445,450,889,887),(-20,-20),(385,205),26,218),
 6:((889,450,1333,887),(-55,5),(350,230),28,219),
 7:((1333,450,1774,887),(-44,-15),(361,210),26,218)}
if ANIM=='run_start':
    boxes=[(0,0,445,450),(445,0,889,450),(889,0,1333,450),(1333,0,1774,450),(0,450,445,887),(445,450,889,887),(889,450,1333,887),(1333,450,1774,887)]
    specs=[((-25,25),(224,250),5,234),((-25,60),(260,270),8,226),((-5,30),(310,241),12,218),((0,25),(371,215),18,215),((5,35),(378,225),23,216),((28,10),(401,221),25,218),((15,0),(385,213),26,218),((38,-5),(408,213),25,218)]
    configs={i:(boxes[i],*specs[i]) for i in range(8)}
repair=load(L/'pilot_v3/body_reconstruction.png')
master=load(L/'art_pass_05/kingdom_key_master_finished.png')
gripmaster=load(L/'art_pass_05/grip_master_space.png')
headmask=load(L/'pilot_v3/head_occlusion.png').getchannel('A')
orighead=load(L/'pilot_v3/frame_00_original.png').getchannel('A')
# Head-mask shape comes from recorded polygon rather than alpha of frame00.
hm=Image.new('L',(512,512));ImageDraw.Draw(hm).polygon([(302,111),(324,91),(346,83),(369,58),(384,69),(411,66),(437,87),(442,132),(425,155),(413,166),(386,188),(366,185),(343,170),(321,157)],fill=255)
oldchain=load(L/'art_pass_05/chain_and_charm.png')
oldmeta=json.loads((L/'art_pass_05/manifest.json').read_text())
for index,(crop,(dx,dy),hand,yaw,angle) in configs.items():
    out=TARGET/f'frame_{index:02d}_review_v1';out.mkdir(parents=True,exist_ok=True)
    original=Image.new('RGBA',(512,512));original.paste(sheet.crop(crop),(0,0));original.save(out/'original_crop.png')
    body=original.copy()
    mask=Image.open(L/'pilot_v3/old_weapon_removal_mask.png').convert('L').transform((512,512),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy))
    md=ImageDraw.Draw(mask)
    md.rectangle((0,0,238+dx,214+dy),fill=255)
    md.rectangle((35,160+dy,190+dx,247+dy),fill=255)
    oldguards={3:(145,145,242,224),4:(180,103,274,185),5:(198,124,289,204),6:(160,138,254,225),7:(169,113,277,199)}
    oldarms={3:(214,196,334,253),4:(233,166,349,229),5:(257,181,373,234),6:(230,193,337,244),7:(222,166,353,238)}
    if ANIM=='run_start':
        oldguards={0:(165,207,269,299),1:(168,229,282,319),2:(150,201,279,310),3:(165,86,310,194),4:(180,105,308,211),5:(200,150,324,259),6:(169,165,310,262),7:(150,169,295,259)}
        oldarms={0:(219,225,327,268),1:(233,241,345,285),2:(234,211,353,270),3:(232,120,361,224),4:(246,159,364,251),5:(267,176,378,231),6:(248,184,370,235),7:(256,169,394,228)}
    md.rectangle(oldguards[index],fill=255);md.rectangle(oldarms[index],fill=255)
    body.putalpha(Image.composite(Image.new('L',(512,512),0),body.getchannel('A'),mask))
    body=Image.alpha_composite(body,shift(repair,dx,dy))
    # Preserve original pelvis/leg pixels below the jacket repair boundary.
    lower_y=225+dy
    body.paste(original.crop((0,lower_y,512,512)),(0,lower_y))
    if ANIM=='run_start':
        # The initial guard hid pants/chest pixels. Rebuild those local areas
        # before putting the new rigid weapon over them; never leave two guards.
        bd=ImageDraw.Draw(body)
        if index<3:
            gx0,gy0,gx1,gy1=oldguards[index]
            bd.rectangle((gx0,max(gy0,lower_y),gx1,gy1),fill='#202b33')
            chains={0:(231,282,265,362),1:(235,300,278,380),2:(220,278,267,356)}
            bd.rectangle(chains[index],fill='#202b33')
        else:
            chains={3:(169,180,208,245),4:(127,153,180,218),5:(170,168,224,221),6:(89,184,145,289),7:(93,172,157,254)}
            bd.rectangle(chains[index],fill=(0,0,0,0))
    # Each elbow is drawn with its own shoulder, elbow and wrist controls.
    sx,sy=350+dx,216+dy;wx,wy=hand
    ex,ey=sx+25+(index%2)*3,sy+33-(index%3)*3
    if ANIM=='run_start' and index<3:
        ex,ey=sx-16,sy+31
    arm=Image.new('RGBA',(2048,2048))
    path(arm,(sx-5,sy),[
      ((sx,sy+2),(sx+7,sy+1),(sx+11,sy-1)),
      ((sx+14,sy+14),(ex-5,ey-7),(ex,ey-3)),
      ((ex+9,ey-4),(wx-8,wy+6),(wx-5,wy-4)),
      ((wx+1,wy-8),(wx+9,wy-1),(wx+8,wy+5)),
      ((wx+1,wy+17),(ex+9,ey+14),(ex,ey+14)),
      ((ex-12,ey+13),(sx+5,sy+25),(sx-5,sy))],'#edb084')
    path(arm,(sx+6,sy+10),[
      ((sx+10,sy+24),(ex-7,ey+9),(ex+1,ey+9)),
      ((ex+11,ey+6),(wx+2,wy+8),(wx+5,wy+2)),
      ((wx+4,wy+12),(ex+10,ey+15),(ex,ey+14)),
      ((ex-11,ey+14),(sx+8,sy+29),(sx+6,sy+10))],'#bd7e5e', '#bd7e5e')
    arm=arm.resize((512,512),Image.Resampling.LANCZOS);arm.save(out/'holding_arm.png')
    body=Image.alpha_composite(body,arm)
    for folder,name in [('art_pass_01','art_detail_overlay.png'),('art_pass_02','jacket_volume_overlay.png'),('art_pass_02','sleeve_glove_fold_overlay.png'),('art_pass_03','chest_redraw_overlay.png')]:
        patch=np.array(load(L/folder/name));patch[210:,340:]=0
        body=Image.alpha_composite(body,shift(Image.fromarray(patch,'RGBA'),dx,dy))
    p=np.array(body);rgb=p[:,:,:3].astype(float);yy,xx=np.indices((512,512))
    cloth=(p[:,:,3]>0)&(xx>=208+dx)&(xx<=375+dx)&(yy>=145+dy)&(yy<=258+dy)&(rgb[:,:,0]<115)&(rgb[:,:,2]>rgb[:,:,0]+5)&(rgb[:,:,2]<155)
    lum=.2126*rgb[:,:,0]+.7152*rgb[:,:,1]+.0722*rgb[:,:,2]
    tone=np.stack([lum*.93,lum*.96,lum],axis=2);p[:,:,:3][cloth]=np.clip((rgb*.18+tone*.82)[cloth],0,255).astype('uint8')
    body=Image.fromarray(p,'RGBA');body.save(out/'refined_body_plate.png')
    theta=math.radians(angle);c,s=math.cos(theta),math.sin(theta);psi=math.radians(yaw);k=math.sin(psi)/1400
    H=np.array([[c,-s,hand[0]],[s,c,hand[1]],[0,0,1]])@np.array([[math.cos(psi),0,0],[0,1,0],[-k,0,1]])@np.array([[1,0,-77],[0,1,-70],[0,0,1]])
    inv=np.linalg.inv(H);inv/=inv[2,2]
    def project(im):return im.transform((512,512),Image.Transform.PERSPECTIVE,tuple(inv.flatten()[:8]),Image.Resampling.BICUBIC)
    weapon=project(master);grip=project(gripmaster)
    weapon.save(out/'weapon_instance.png');grip.save(out/'foreground_grip.png')
    q=H@np.array([34,70,1]);pommel=q[:2]/q[2]
    delta=pommel-np.array(oldmeta['world_anchors']['pommel']);chain=shift(oldchain,*delta);chain.save(out/'chain_and_charm.png')
    head=original.copy();maskhead=Image.new('L',(512,512))
    headboxes={3:(250,45,410,202),4:(245,15,425,178),5:(270,25,440,182),6:(235,40,395,201),7:(245,30,425,186)}
    if ANIM=='run_start':
        headboxes={0:(240,40,410,190),1:(240,105,410,250),2:(260,75,430,225),3:(280,75,440,214),4:(255,35,430,220),5:(280,25,440,198),6:(270,15,435,193),7:(285,20,444,190)}
    # Semantic hair/skin connected component avoids restoring the original
    # chest grip as a rectangular patch around the new shoulder carry.
    arr=np.array(original);col=arr[:,:,:3].astype(float)
    bx0,by0,bx1,by1=headboxes[index]
    seed=(col[:,:,0]>col[:,:,1]*1.1)&(col[:,:,0]>col[:,:,2]*1.35)&(arr[:,:,3]>32)
    bound=np.zeros((512,512),bool);bound[by0:by1,bx0:bx1]=True
    if ANIM!='run_start':
        for oldbox in (oldguards[index],oldarms[index]):
            x0,y0,x1,y1=oldbox;bound[y0:y1,x0:x1]=False
    binary=Image.fromarray((seed&bound).astype('uint8')*255).filter(ImageFilter.MaxFilter(5))
    occupied=np.array(binary)>0;visited=np.zeros((512,512),bool);best=[]
    for py,px in zip(*np.where(occupied)):
        if visited[py,px]:continue
        stack=[(py,px)];visited[py,px]=True;component=[]
        while stack:
            cy,cx=stack.pop();component.append((cy,cx))
            for ny,nx in ((cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)):
                if 0<=ny<512 and 0<=nx<512 and occupied[ny,nx] and not visited[ny,nx]:
                    visited[ny,nx]=True;stack.append((ny,nx))
        if len(component)>len(best):best=component
    chosen=np.zeros((512,512),np.uint8)
    for py,px in best:chosen[py,px]=255
    maskhead=Image.fromarray(chosen).filter(ImageFilter.MaxFilter(3))
    head_a=np.array(maskhead)
    gold=(col[:,:,0]>120)&(col[:,:,1]>80)&(col[:,:,2]<75)&(col[:,:,1]>.65*col[:,:,0])
    head_a[gold]=0;maskhead=Image.fromarray(head_a)
    head.putalpha(Image.composite(original.getchannel('A'),Image.new('L',(512,512),0),maskhead));head.save(out/'head_occlusion.png')
    result=body
    for im in (weapon,chain,head,grip):result=Image.alpha_composite(result,im)
    data=np.array(result);data[data[:,:,3]==0,:3]=0;result=Image.fromarray(data,'RGBA')
    result.save(out/f'sora_{ANIM}_{index:02d}_review.png')
    (out/'manifest.json').write_text(json.dumps({'frame_index':index,'crop':crop,'hand_anchor':hand,'body_reconstruction_offset':[dx,dy],'rotation_degrees':angle,'tip_toward_camera_yaw_degrees':yaw,'master_to_screen_homography':H.tolist(),'status':'provisional refined source pose; anatomy/style review pending','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2),encoding='utf-8')

batch=READY/ANIM/'review_cycle_v1';batch.mkdir(exist_ok=True)
frames=[load(TARGET/f'frame_{i:02d}_review_v1'/f'sora_{ANIM}_{i:02d}_review.png') for i in range(8)]
atlas=Image.new('RGBA',(2048,1024));board=Image.new('RGB',(2048,1088),'#202633');flat=[]
for i,im in enumerate(frames):
    im.save(batch/f'sora_{ANIM}_{i:02d}.png');atlas.paste(im,(i%4*512,i//4*512))
    board.paste(im,(i%4*512,i//4*544+24),im);ImageDraw.Draw(board).text((i%4*512+10,i//4*544+5),f'Frame {i:02d}',fill='white')
    bg=Image.new('RGB',(512,512),'#202633');bg.paste(im,(0,0),im);flat.append(bg)
atlas.save(batch/f'sora_{ANIM}_sheet.png');board.save(batch/'Contact_Sheet.png')
delays=[160,120,100,100,100,90,90,100] if ANIM=='run_start' else [100]*8
flat[0].save(batch/f'sora_{ANIM}_preview.gif',save_all=True,append_images=flat[1:],duration=delays,loop=0)
(batch/'manifest.json').write_text(json.dumps({'status':'eight-pose art review, not final or integrated','canvas':[512,512],'frames':[{'path':f'sora_{ANIM}_{i:02d}.png','duration_ms':delays[i]} for i in range(8)],'loop':ANIM=='run_loop','limitations':['Pose registration and transitions need visual QA.','Upper-body repairs use shared motifs; anatomy may require further redraw.','No Godot testing.']},indent=2),encoding='utf-8')
print('Built eight-pose review:',batch)
