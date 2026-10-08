"""New articulated stop construction: actual joints, no scaled body frames."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent;READY=ROOT/'ready';L=READY/'run_loop/layers';OUT=READY/'run_stop/construction_v1'
OUT.mkdir(parents=True,exist_ok=True)
def load(p):return Image.open(p).convert('RGBA')
SIZE=(512,512)
upper=load(L/'pilot_v3/body_clean_plate.png')
for folder,name in [('art_pass_01','art_detail_overlay.png'),('art_pass_02','jacket_volume_overlay.png'),('art_pass_02','sleeve_glove_fold_overlay.png'),('art_pass_03','chest_redraw_overlay.png')]:
    patch=np.array(load(L/folder/name));patch[210:,340:]=0
    upper=Image.alpha_composite(upper,Image.fromarray(patch,'RGBA'))
upper=Image.alpha_composite(upper,load(L/'pilot_v3/head_occlusion.png'))
mask=Image.new('L',SIZE);ImageDraw.Draw(mask).polygon([(200,45),(445,45),(445,225),(337,265),(226,267),(200,220)],fill=255)
upper.putalpha(Image.composite(upper.getchannel('A'),Image.new('L',SIZE,0),mask))
upper.save(OUT/'upper_body_cutout.png')
idle=load(READY/'standing_idle/sora_stand_idle_00.png')
boots=[idle.crop((61,385,164,478)),idle.crop((330,385,445,478))]
for i,b in enumerate(boots):b.save(OUT/f'boot_source_{i}.png')
master=load(L/'art_pass_05/kingdom_key_master_finished.png');gripmaster=load(L/'art_pass_05/grip_master_space.png')
states=[
 {'hips':[(244,275),(302,270)],'knees':[(184,317),(363,324)],'ankles':[(147,364),(395,426)],'pitch':2,'hand':(401,225),'angle':219},
 {'hips':[(245,272),(301,268)],'knees':[(212,331),(357,333)],'ankles':[(205,421),(385,430)],'pitch':7,'hand':(382,224),'angle':221},
 {'hips':[(245,269),(300,268)],'knees':[(224,327),(341,325)],'ankles':[(215,430),(372,430)],'pitch':11,'hand':(360,228),'angle':224},
 {'hips':[(245,268),(300,267)],'knees':[(219,325),(331,326)],'ankles':[(210,430),(365,430)],'pitch':14,'hand':(337,235),'angle':227},
 {'hips':[(245,267),(300,267)],'knees':[(211,328),(333,327)],'ankles':[(190,430),(367,430)],'pitch':16,'hand':(310,243),'angle':230},
 {'hips':[(245,267),(300,267)],'knees':[(198,328),(337,328)],'ankles':[(166,430),(380,430)],'pitch':18,'hand':(282,249),'angle':233},
]
frames=[load(L/'frame_00_review_v1/sora_run_loop_00_review.png')]
metadata=[{'phase':'running entry','source':'reviewed run-loop frame 00'}]
def limb(d,a,b,width,fill):
    d.line([(round(a[0]*4),round(a[1]*4)),(round(b[0]*4),round(b[1]*4))],fill='#121c24',width=(width+3)*4)
    d.line([(round(a[0]*4),round(a[1]*4)),(round(b[0]*4),round(b[1]*4))],fill=fill,width=width*4)
    r=width*2
    for p in (a,b):d.ellipse((p[0]*4-r,p[1]*4-r,p[0]*4+r,p[1]*4+r),fill=fill,outline='#121c24',width=5)
for index,state in enumerate(states,1):
    im=Image.new('RGBA',SIZE);legs=Image.new('RGBA',(2048,2048));d=ImageDraw.Draw(legs)
    for side in (0,1):
        hip=np.array(state['hips'][side],float);knee=np.array(state['knees'][side],float);ankle=np.array(state['ankles'][side],float)
        shin_end=ankle-np.array([0,58])
        limb(d,knee,shin_end,22,'#e8ad83')
        # Shorts are separate joint-following thigh volumes, drawn each pose.
        mid=(hip+knee)/2
        limb(d,hip,knee,65,'#252a30' if side==0 else '#30353b')
        d.line([(int((mid[0]-18)*4),int((mid[1]+10)*4)),(int((knee[0]+22)*4),int((knee[1]+4)*4))],fill='#b7c0c7',width=6)
        d.line([(int((hip[0]-7)*4),int((hip[1]+1)*4)),(int((mid[0]-13)*4),int((mid[1]-2)*4))],fill='#e5b632',width=16)
    im=Image.alpha_composite(im,legs.resize(SIZE,Image.Resampling.LANCZOS))
    for side in (0,1):
        ankle=state['ankles'][side];boot=boots[side]
        im.alpha_composite(boot,(int(ankle[0]-boot.width/2),int(ankle[1]-boot.height)))
    torso=upper.rotate(state['pitch'],resample=Image.Resampling.BICUBIC,center=(300,260))
    im=Image.alpha_composite(im,torso)
    # Neck/torso pitching is an articulated cutout rotation; no body scaling.
    theta=math.radians(-state['pitch']);c,s=math.cos(theta),math.sin(theta)
    shoulder=np.array([300,260])+np.array([[c,-s],[s,c]])@(np.array([350,210])-np.array([300,260]))
    hand=np.array(state['hand']);elbow=(shoulder+hand)/2+np.array([12,33])
    arm=Image.new('RGBA',(2048,2048));ad=ImageDraw.Draw(arm)
    limb(ad,shoulder,elbow,23,'#eab087');limb(ad,elbow,hand,21,'#eab087')
    im=Image.alpha_composite(im,arm.resize(SIZE,Image.Resampling.LANCZOS))
    angle=math.radians(state['angle']);c,s=math.cos(angle),math.sin(angle);yaw=math.radians(25-index*2)
    H=np.array([[c,-s,hand[0]],[s,c,hand[1]],[0,0,1]])@np.array([[math.cos(yaw),0,0],[0,1,0],[-math.sin(yaw)/1400,0,1]])@np.array([[1,0,-77],[0,1,-70],[0,0,1]])
    inv=np.linalg.inv(H);inv/=inv[2,2]
    for layer in (master,gripmaster):im=Image.alpha_composite(im,layer.transform(SIZE,Image.Transform.PERSPECTIVE,tuple(inv.flatten()[:8]),Image.Resampling.BICUBIC))
    q=H@np.array([34,70,1.]);pom=q[:2]/q[2]
    chain=Image.new('RGBA',SIZE);cd=ImageDraw.Draw(chain);cd.line([tuple(pom),(pom[0],pom[1]+35)],fill='#abbac6',width=2)
    cd.ellipse((pom[0]-6,pom[1]+31,pom[0]+6,pom[1]+43),fill='#99aab8',outline='#182631')
    im=Image.alpha_composite(im,chain)
    a=np.array(im);a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a,'RGBA')
    frames.append(im);metadata.append({'phase':['braking reach','heel contact','knee compression','rear-foot catch-up','carry lowering','guard settling'][index-1],**state,'master_to_screen_homography':H.tolist()})
# Exact approved idle artwork aligned to the common review floor (432px).
final=Image.new('RGBA',SIZE);final.alpha_composite(idle,(0,-38));frames.append(final)
metadata.append({'phase':'approved standing guard','source':'standing_idle/sora_stand_idle_00.png','translation':[0,-38],'limitation':'Original approved guard weapon retained; master-to-idle geometry seam needs review.'})
sheet=Image.new('RGBA',(2048,1024));board=Image.new('RGB',(2048,1088),'#202633');flat=[]
for i,im in enumerate(frames):
    im.save(OUT/f'sora_run_stop_{i:02d}.png');sheet.paste(im,(i%4*512,i//4*512))
    board.paste(im,(i%4*512,i//4*544+24),im);ImageDraw.Draw(board).text((i%4*512+10,i//4*544+5),metadata[i]['phase'],fill='white')
    bg=Image.new('RGB',SIZE,'#202633');bg.paste(im,(0,0),im);flat.append(bg)
sheet.save(OUT/'sora_run_stop_sheet.png');board.save(OUT/'Contact_Sheet.png')
delays=[120,100,100,100,100,100,120,350]
flat[0].save(OUT/'sora_run_stop_preview.gif',save_all=True,append_images=flat[1:],duration=delays,loop=0)
(OUT/'manifest.json').write_text(json.dumps({'status':'new articulated construction draft, not finished cel-shaded art','canvas':SIZE,'loop':False,'frames':[{'path':f'sora_run_stop_{i:02d}.png','duration_ms':delays[i],**metadata[i]} for i in range(8)],'method':'New per-pose thigh/shin drawings and joint coordinates; reusable boots/upper torso cutouts; no whole-body scaling or reversed run start.','limitations':['Manual anatomy, shoe crop edges and outfit details require substantial art refinement.','Torso cutout pitching may need redrawn volume/perspective.','Final guard master seam unresolved.','Not integrated or tested in Godot.']},indent=2),encoding='utf-8')
print('Saved articulated run-stop construction:',OUT)
