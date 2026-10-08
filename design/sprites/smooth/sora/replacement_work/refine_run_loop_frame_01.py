"""Apply local garment refinements and rigid master to actual second pose."""
from pathlib import Path
import json,hashlib,argparse
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
L=ROOT/'ready/run_loop/layers'
parser=argparse.ArgumentParser()
parser.add_argument('--frame',type=int,choices=(1,2),default=1)
args=parser.parse_args()
POSE=L/f'frame_{args.frame:02d}_v1';OUT=L/f'frame_{args.frame:02d}_review_v1'
OUT.mkdir(parents=True,exist_ok=True)
m=json.loads((POSE/'manifest.json').read_text())
dx,dy=m['body_reconstruction_offset']
SIZE=(512,512)
def load(p):return Image.open(p).convert('RGBA')
def shift(im,dx,dy):
    return im.transform(SIZE,Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC)

base=Image.alpha_composite(load(POSE/'body_clean_plate.png'),load(POSE/'holding_arm.png'))
# Reuse garment surface motifs as editable local patches; retain actual pose
# legs/head and the independently articulated second-frame arm.
for folder,name in [('art_pass_01','art_detail_overlay.png'),
                    ('art_pass_02','jacket_volume_overlay.png'),
                    ('art_pass_02','sleeve_glove_fold_overlay.png'),
                    ('art_pass_03','chest_redraw_overlay.png')]:
    patch=load(L/folder/name)
    a=np.array(patch)
    # Remove frame-00 carrying-arm detail, which does not match this elbow.
    a[210:,:][np.indices(a[210:].shape[:2])[1]>=340]=0
    patch=Image.fromarray(a,'RGBA')
    base=Image.alpha_composite(base,shift(patch,dx,dy))
contact=load(L/'art_pass_06/contact_and_arm_overlay.png')
a=np.array(contact)
a[215:,340:]=0
base=Image.alpha_composite(base,shift(Image.fromarray(a,'RGBA'),dx,dy))

# Neutralize reconstructed navy fabric, keeping skin, red and yellow intact.
p=np.array(base);rgb=p[:,:,:3].astype(float);y,x=np.indices(p.shape[:2])
cloth=(p[:,:,3]>0)&(x>=208+dx)&(x<=375+dx)&(y>=145+dy)&(y<=258+dy)
cloth&=(rgb[:,:,0]<115)&(rgb[:,:,2]>rgb[:,:,0]+5)&(rgb[:,:,2]<155)
lum=.2126*rgb[:,:,0]+.7152*rgb[:,:,1]+.0722*rgb[:,:,2]
tone=np.stack([lum*.93,lum*.96,lum],axis=2)
p[:,:,:3][cloth]=np.clip((rgb*.18+tone*.82)[cloth],0,255).astype('uint8')
base=Image.fromarray(p,'RGBA');base.save(OUT/'refined_body_plate.png')
H=np.array(m['master_to_screen_homography']);inv=np.linalg.inv(H);inv/=inv[2,2]
coeff=tuple(inv.flatten()[:8])
def project(im):return im.transform(SIZE,Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
weapon=project(load(L/'art_pass_05/kingdom_key_master_finished.png'))
grip=project(load(L/'art_pass_05/grip_master_space.png'))
weapon.save(OUT/'weapon_instance.png');grip.save(OUT/'foreground_grip.png')
# Fixed chain/charm drawings move with the actual projected pommel.
old=json.loads((L/'art_pass_05/manifest.json').read_text())
old_p=np.array(old['world_anchors']['pommel']);new_p=np.array(m['world_anchors']['pommel'])
delta=new_p-old_p
chain=shift(load(L/'art_pass_05/chain_and_charm.png'),*delta)
chain.save(OUT/'chain_and_charm.png')
after=Image.alpha_composite(base,weapon)
after=Image.alpha_composite(after,chain)
after=Image.alpha_composite(after,load(POSE/'head_occlusion.png'))
after=Image.alpha_composite(after,grip)
p=np.array(after);p[p[:,:,3]==0,:3]=0
after=Image.fromarray(p,'RGBA');after.save(OUT/f'sora_run_loop_{args.frame:02d}_review.png')
before=load(POSE/'frame_00_construction_preview.png')
comparison=Image.new('RGB',(1024,550),'#202633')
for i,(im,title) in enumerate([(before,'Frame 01 construction'),(after,'Frame 01 refined treatment / approved grip orientation')]):
    comparison.paste(im,(i*512,32),im);ImageDraw.Draw(comparison).text((i*512+12,10),title,fill='white')
comparison.save(OUT/'Art_Comparison.png')
first=load(L/f'frame_{args.frame-1:02d}_review_v1'/f'sora_run_loop_{args.frame-1:02d}_review.png')
pair=Image.new('RGB',(1024,550),'#202633')
frames=[]
for i,(im,title) in enumerate([(first,f'Refined frame {args.frame-1:02d}'),(after,f'Refined frame {args.frame:02d}')]):
    pair.paste(im,(i*512,32),im);ImageDraw.Draw(pair).text((i*512+12,10),title,fill='white')
    flat=Image.new('RGB',SIZE,'#202633');flat.paste(im,(0,0),im);frames.append(flat)
pair.save(OUT/'Two_Frame_Comparison.png')
frames[0].save(OUT/'Two_Frame_Review.gif',save_all=True,append_images=frames[1:],duration=[450,450],loop=0)
# No claim of completed gait: just two actual source poses for transition review.
original=np.array(load(POSE/'frame_00_original.png'));final=np.array(after)
opaque=original[330:,:,3]>0
assert np.array_equal(original[330:][opaque],final[330:][opaque])
assert hashlib.sha256((ROOT/'ready/run_loop/run_loop_source.png').read_bytes()).hexdigest()==m['source_sha256']
m['status']=f'frame {args.frame:02d} refinement review; provisional, not final run cycle'
m['weapon_master']='art_pass_05/kingdom_key_master_finished.png'
m['grip_master']='art_pass_05/grip_master_space.png'
m['chain_attachment_translation']=delta.tolist()
m['garment_detail_reuse']=f'local patches translated {dx},{dy}; needs per-pose art review'
(OUT/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('Saved',OUT)
