"""Local rigid-master surface and anatomically curled grip refinement."""
from pathlib import Path
import hashlib,json,math,argparse
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
L=ROOT/'ready/run_loop/layers'
parser=argparse.ArgumentParser()
parser.add_argument('--correct-hand',action='store_true')
args=parser.parse_args()
SRC=L/'art_pass_03'; P=L/'pilot_v3'; OUT=L/('art_pass_05' if args.correct_hand else 'art_pass_04')
OUT.mkdir(parents=True,exist_ok=True)
m=json.loads((SRC/'manifest.json').read_text())
AA=4

def curve(im,start,segments,fill=None,stroke=None,width=1,closed=True):
    points=[start];a=start
    for b,c,end in segments:
        for j in range(1,25):
            t=j/24;u=1-t
            points.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*end[0],
                           u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*end[1]))
        a=end
    q=[(round(x*AA),round(y*AA)) for x,y in points]
    d=ImageDraw.Draw(im)
    if fill:d.polygon(q,fill=fill)
    if stroke:d.line(q+([q[0]] if closed else []),fill=stroke,width=round(width*AA),joint='curve')

master=Image.open(L/'art_pass_01/kingdom_key_master_shaded.png').convert('RGBA')
pixels=np.array(master)
# Cross-axis bands model a round metal shaft inside the same rigid silhouette.
for y in range(62,81):
    h=(y-62)/18
    value=int(96+133*math.exp(-((h-.29)/.25)**2)+36*math.exp(-((h-.78)/.13)**2))
    for x in range(141,310):
        if pixels[y,x,3]>0:
            pixels[y,x,:3]=[value,min(255,value+5),min(255,value+12)]
master=Image.fromarray(pixels,'RGBA')
surface=Image.new('RGBA',(master.width*AA,master.height*AA))
d=ImageDraw.Draw(surface)
# Inner gold bevel catches light, outer bottom rim gets depth.
d.line((49*AA,46*AA,102*AA,46*AA),fill='#fff0a0',width=AA)
d.line((46*AA,52*AA,46*AA,88*AA),fill='#ffe481',width=AA)
d.line((49*AA,99*AA,105*AA,99*AA),fill='#98701b',width=2*AA)
d.line((113*AA,51*AA,113*AA,90*AA),fill='#8a6518',width=AA)
surface=surface.resize(master.size,Image.Resampling.LANCZOS)
master=Image.alpha_composite(master,surface)
master.putalpha(Image.open(P/'kingdom_key_master.png').getchannel('A'))
master.save(OUT/'kingdom_key_master_finished.png')
H=np.array(m['master_to_screen_homography'])
inv=np.linalg.inv(H);inv/=inv[2,2]
coeff=tuple(inv.flatten()[:8])
def project(im):
    return im.transform((512,512),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
weapon=project(master);weapon.save(OUT/'weapon_instance.png')

# Draw hand in master coordinates, so curved fingers actually wrap the grip.
hand=Image.new('RGBA',(340*AA,150*AA))
curve(hand,(64,72),[
 ((70,71),(81,72),(88,75)),
 ((93,78),(91,86),(85,88)),
 ((77,89),(69,86),(65,82)),
 ((62,78),(62,75),(64,72))],'#19232d','#0c1621',1)
curve(hand,(67,78),[
 ((74,80),(84,78),(88,79)),
 ((88,84),(81,85),(75,83)),
 ((70,82),(68,80),(67,78))],'#344552')
for x in (65,71,77,83):
    curve(hand,(x,65),[
       ((x+1,62),(x+5,62),(x+5,65)),
       ((x+6,68),(x+6,72),(x+4,75)),
       ((x+2,77),(x-1,75),(x,72)),
       ((x+1,69),(x-1,67),(x,65))],'#edb185','#4d3026',.7)
    curve(hand,(x+1,65),[
       ((x+2,64),(x+4,64),(x+4,66)),
       ((x+4,68),(x+4,69),(x+3,70)),
       ((x+2,69),(x+1,67),(x+1,65))],'#ffd1a4')
    curve(hand,(x+1,73),[
       ((x+2,74),(x+3,74),(x+4,72))],stroke='#bc7d60',width=.65,closed=False)
curve(hand,(91,74),[
 ((91,79),(87,83),(82,82)),
 ((79,81),(79,78),(82,77)),
 ((85,76),(86,73),(87,71)),
 ((89,71),(91,72),(91,74))],'#d99570','#4d3026',.7)
curve(hand,(88,73),[
 ((89,74),(88,78),(85,79))],stroke='#fbc69a',width=.8,closed=False)
if args.correct_hand:
    # Reorient only the grip drawing about the handle axis. Weapon geometry
    # and camera remain fixed. Palm/glove moves to the approaching wrist side.
    hand=hand.transform(hand.size,Image.Transform.AFFINE,
                        (1,0,0,0,-1,140*AA),Image.Resampling.BICUBIC)
    # Wrist enters from below the visible handle, matching the bent forearm.
    curve(hand,(68,54),[
       ((69,50),(72,46),(78,46)),
       ((82,46),(86,49),(87,54)),
       ((84,59),(74,60),(68,54))],'#19232d','#0c1621',.8)
    curve(hand,(71,52),[
       ((76,55),(82,55),(85,51))],stroke='#738491',width=.8,closed=False)
hand=hand.resize((340,150),Image.Resampling.LANCZOS)
hand.save(OUT/'grip_master_space.png')
grip=project(hand);grip.save(OUT/'foreground_grip.png')

def world(p):
    q=H@np.array([p[0],p[1],1.]);return q[:2]/q[2]
start=world((34,70))
chain=Image.new('RGBA',(2048,2048));d=ImageDraw.Draw(chain)
# Fixed 35-pixel hanging length, interlocking alternating link orientations.
for i in range(7):
    x=start[0]-i*.65;y=start[1]+i*4.3
    rx,ry=(2,3.2) if i%2==0 else (1.2,3.2)
    box=((x-rx)*AA,y*AA,(x+rx)*AA,(y+2*ry)*AA)
    d.ellipse(box,outline='#182631',width=2*AA)
    d.arc(box,175,355,fill='#d3dee6',width=AA)
    d.arc(box,-5,175,fill='#8293a2',width=AA)
x=start[0]-4.5;y=start[1]+35
for cx,cy,r in [(x-5,y-5,3.8),(x+5,y-5,3.8),(x,y,6.8)]:
    d.ellipse(((cx-r)*AA,(cy-r)*AA,(cx+r)*AA,(cy+r)*AA),fill='#8799a8',outline='#172632',width=AA)
    d.arc(((cx-r+.8)*AA,(cy-r+.8)*AA,(cx+r-.8)*AA,(cy+r-.8)*AA),190,290,fill='#e3edf4',width=AA)
chain=chain.resize((512,512),Image.Resampling.LANCZOS)
chain.save(OUT/'chain_and_charm.png')
# Clear previous fingers and chain by rebuilding from retained local plates.
body=Image.open(P/'body_clean_plate.png').convert('RGBA')
base=Image.alpha_composite(body,Image.open(P/'holding_arm.png').convert('RGBA'))
for source,name in [(L/'art_pass_01','art_detail_overlay.png'),
                    (L/'art_pass_02','jacket_volume_overlay.png'),
                    (L/'art_pass_02','sleeve_glove_fold_overlay.png'),
                    (SRC,'chest_redraw_overlay.png')]:
    base=Image.alpha_composite(base,Image.open(source/name).convert('RGBA'))
base=Image.alpha_composite(base,weapon)
base=Image.alpha_composite(base,chain)
base=Image.alpha_composite(base,Image.open(P/'head_occlusion.png').convert('RGBA'))
base=Image.alpha_composite(base,grip)
data=np.array(base);data[data[:,:,3]==0,:3]=0
after=Image.fromarray(data,'RGBA');after.save(OUT/'frame_00_art_preview.png')
before=Image.open((L/'art_pass_04' if args.correct_hand else SRC)/'frame_00_art_preview.png').convert('RGBA')
comparison=Image.new('RGB',(1024,550),'#202633')
closeup=Image.new('RGB',(960,350),'#202633')
labels=('Previous upside-down grip','Reoriented palm, thumb and wrist') if args.correct_hand else ('Previous grip and weapon finish','Curled grip, round shaft shading, linked chain')
for i,(im,title) in enumerate([(before,labels[0]),(after,labels[1])]):
    comparison.paste(im,(i*512,32),im);ImageDraw.Draw(comparison).text((i*512+12,10),title,fill='white')
    crop=im.crop((320,175,480,280)).resize((480,315),Image.Resampling.LANCZOS)
    closeup.paste(crop,(480*i,32),crop);ImageDraw.Draw(closeup).text((480*i+10,10),title,fill='white')
comparison.save(OUT/'Art_Comparison.png');closeup.save(OUT/'Grip_Comparison.png')
assert np.array_equal(np.array(master)[:,:,3],np.array(Image.open(P/'kingdom_key_master.png'))[:,:,3])
assert hashlib.sha256((ROOT/'ready/run_loop/run_loop_source.png').read_bytes()).hexdigest()==m['source_sha256']
m['status']='hand orientation correction; still unfinished' if args.correct_hand else 'fourth local art pass: grip and weapon finish, still unfinished'
m['source_art_pass']='art_pass_04' if args.correct_hand else 'art_pass_03'
m['grip_orientation']='palm/wrist below handle; fingers wrap over, thumb toward collar' if args.correct_hand else 'superseded inverted grip'
m['chain_length_px']=35
(OUT/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('Saved',OUT)
