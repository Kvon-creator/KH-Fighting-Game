"""Local, deterministic construction pilot. Never writes source sheets."""
from pathlib import Path
import hashlib
import json
import math
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--foreground',action='store_true')
parser.add_argument('--refine',action='store_true')
args=parser.parse_args()
if args.refine:
    args.foreground=True
OUT = ROOT / ('ready/run_loop/layers/pilot_v3' if args.refine else
              'ready/run_loop/layers/pilot_v2' if args.foreground else 'ready/run_loop/layers/pilot_v1')
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'ready/run_loop/run_loop_source.png'
EXPECTED = '6934bfa1b330834e64f765def9a9f24bcf37cb47fba61b59815f3a7365bf90f0'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
SIZE = (512, 512)
AA = 4

def layer(size=SIZE):
    return Image.new('RGBA', (size[0]*AA, size[1]*AA))

def poly(im, points, fill, outline='#171a20', width=2):
    d = ImageDraw.Draw(im)
    p = [(round(x*AA), round(y*AA)) for x,y in points]
    d.polygon(p, fill=fill)
    if outline:
        d.line(p+[p[0]], fill=outline, width=width*AA, joint='curve')

def line(im, points, fill, width=2):
    ImageDraw.Draw(im).line([(int(x*AA),int(y*AA)) for x,y in points],fill=fill,width=width*AA,joint='curve')

def ellipse(im, box, fill, outline='#171a20', width=2):
    ImageDraw.Draw(im).ellipse(tuple(int(v*AA) for v in box),fill=fill,outline=outline,width=width*AA)

def small(im):
    return im.resize((im.width//AA,im.height//AA),Image.Resampling.LANCZOS)

def curve(im, start, segments, fill, outline='#171a20', width=2, closed=True):
    """Sample cubic curves at working resolution for smooth local redrawing."""
    points=[start]
    a=start
    for b,c,end in segments:
        for step in range(1,25):
            t=step/24.0; u=1-t
            points.append((u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*end[0],
                           u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*end[1]))
        a=end
    if closed:
        poly(im,points,fill,outline,width)
    else:
        line(im,points,outline,width)

original=Image.new('RGBA',SIZE)
original.paste(Image.open(SOURCE).convert('RGBA').crop((0,0,445,450)),(0,0))
original.save(OUT/'frame_00_original.png')
body=original.copy()
mask=layer()
# Old exposed shaft, teeth, chain, guard and chest grip. Reconstruction below
# deliberately affects only the upper-body repair region, leaving gait intact.
poly(mask,[(72,49),(170,49),(239,140),(291,140),(306,221),
           (284,246),(241,240),(205,231),(143,231),(137,185),
           (204,150),(76,104)],'white',None)
poly(mask,[(72,53),(162,53),(239,143),(248,173),(199,161),(72,111)],'white',None)
if args.refine:
    # Remove the old near forearm as well, avoiding two poses sharing a shoulder.
    poly(mask,[(283,190),(328,174),(361,192),(366,231),(337,242),(284,224)],'white',None)
mask=small(mask).getchannel('A')
body.putalpha(Image.composite(Image.new('L',SIZE,0),body.getchannel('A'),mask))
repair=layer()
# Local outfit clean plate, retaining the original torso silhouette and palette.
poly(repair,[(286,144),(315,145),(335,178),(339,214),(314,237),
             (281,243),(237,221),(218,190),(234,169),(265,153)],'#252b32')
poly(repair,[(278,158),(293,151),(311,160),(304,181),(287,194),
             (254,196),(243,182)],'#363f48')
poly(repair,[(278,179),(301,182),(319,206),(301,224),(260,220),
             (237,201)],'#161d25')
line(repair,[(280,163),(283,186),(290,212),(310,232)],'#919aa0',2)
line(repair,[(285,165),(288,188),(297,210)],'#e9edf0',1)
poly(repair,[(238,217),(274,226),(284,239),(258,247),(234,232)],'#b92321')
poly(repair,[(238,219),(268,228),(257,237),(238,231)],'#ec4330',None)
line(repair,[(253,209),(270,221),(299,230)],'#efc93e',4)
# Far arm released from the old grip, with a lowered glove.
poly(repair,[(250,164),(271,166),(271,184),(255,193),(239,187),(238,177)],'#303941')
line(repair,[(245,180),(256,185),(269,179)],'#b9bec3',3)
poly(repair,[(243,188),(254,194),(247,211),(233,223),(223,216),(230,199)],'#edb184')
poly(repair,[(232,203),(241,210),(235,222),(225,230),(215,224),(218,215)],'#1b2129')
line(repair,[(225,217),(230,220)],'#8d989c',2)
if args.refine:
    repair=layer()
    # Rounded jacket volume follows the unchanged running lean and waist.
    curve(repair,(287,146),[
        ((301,140),(322,147),(332,168)),
        ((341,178),(347,194),(342,212)),
        ((339,228),(318,239),(292,243)),
        ((266,241),(244,228),(229,209)),
        ((220,197),(218,185),(231,174)),
        ((245,162),(267,151),(287,146))],'#252d35')
    curve(repair,(283,153),[
        ((295,148),(311,153),(316,169)),
        ((309,181),(290,188),(271,187)),
        ((254,184),(246,178),(248,174)),
        ((258,164),(271,159),(283,153))],'#3d4852',None)
    curve(repair,(283,181),[
        ((299,177),(323,176),(331,187)),
        ((341,203),(330,224),(311,229)),
        ((290,235),(269,230),(254,219)),
        ((269,220),(285,208),(283,181))],'#18212a',None)
    curve(repair,(297,149),[
        ((303,167),(293,188),(304,210)),
        ((310,223),(317,225),(322,226))],None,'#a9b3bc',2,False)
    curve(repair,(301,151),[
        ((307,166),(300,186),(309,207))],None,'#e1e5e9',1,False)
    curve(repair,(261,200),[
        ((267,207),(276,210),(286,211))],None,'#59636d',1,False)
    curve(repair,(305,218),[
        ((315,218),(323,214),(328,208))],None,'#4b5660',1,False)
    # KH2 red waist panels and yellow trim follow the torso contours.
    curve(repair,(239,217),[
        ((251,222),(267,228),(281,230)),
        ((281,239),(269,247),(258,247)),
        ((245,242),(237,231),(239,217))],'#b72125')
    curve(repair,(244,223),[
        ((253,226),(264,231),(274,232)),
        ((266,239),(256,240),(247,233)),
        ((245,230),(243,226),(244,223))],'#ef4235',None)
    curve(repair,(256,213),[
        ((272,225),(297,234),(318,231))],None,'#e7bf35',4,False)
    # Far sleeve and released forearm, with rounded elbow and knuckles.
    curve(repair,(247,169),[
        ((254,163),(266,165),(272,173)),
        ((276,182),(267,190),(255,194)),
        ((245,192),(236,185),(239,179)),
        ((241,174),(244,171),(247,169))],'#303b45')
    curve(repair,(242,182),[
        ((249,190),(260,191),(270,181))],None,'#bbc2c8',3,False)
    curve(repair,(245,191),[
        ((247,196),(244,201),(237,209)),
        ((233,214),(228,218),(222,217)),
        ((217,211),(224,202),(230,196)),
        ((235,191),(241,189),(245,191))],'#eeb284')
    curve(repair,(234,197),[
        ((229,201),(223,208),(222,211))],None,'#ffd1a5',2,False)
    curve(repair,(222,210),[
        ((230,209),(236,216),(234,222)),
        ((232,231),(218,237),(212,230)),
        ((207,223),(213,213),(222,210))],'#202a34')
    line(repair,[(216,223),(223,226),(231,220)],'#77828d',2)
    # Near sleeve rotates forward into the raised carrying arm.
    curve(repair,(339,183),[
        ((348,175),(365,180),(370,191)),
        ((375,204),(366,216),(355,219)),
        ((342,216),(333,207),(334,196)),
        ((333,190),(336,186),(339,183))],'#28333d')
    curve(repair,(343,184),[
        ((352,178),(364,184),(365,193)),
        ((365,198),(359,200),(351,195)),
        ((345,193),(340,189),(343,184))],'#414d57',None)
    curve(repair,(338,206),[
        ((347,217),(359,218),(369,207))],None,'#c2c9ce',3,False)
body=Image.alpha_composite(body,small(repair))
body.save(OUT/'body_clean_plate.png')
small(repair).save(OUT/'body_reconstruction.png')
mask.save(OUT/'old_weapon_removal_mask.png')

# One master with collinear pommel, grip, collar, shaft and key head.
master=layer((340,150))
poly(master,[(35,65),(124,65),(124,75),(35,75)],'#737b84')
poly(master,[(52,63),(103,63),(103,77),(52,77)],'#20252b')
for x in range(58,101,7): line(master,[(x,64),(x-2,76)],'#49515c',1)
poly(master,[(43,33),(108,33),(121,45),(121,95),(108,107),(43,107),
             (32,95),(32,45)],'#e5b92e')
poly(master,[(49,44),(104,44),(109,50),(109,90),(103,96),(49,96),
             (44,89),(44,50)],'#f5ce49')
# Transparent guard interior reveals black handle, never covers it with fill.
d=ImageDraw.Draw(master)
d.rectangle((51*AA,50*AA,102*AA,90*AA),fill=(0,0,0,0))
poly(master,[(50,63),(103,63),(103,77),(50,77)],'#20252b')
for x in range(58,101,7): line(master,[(x,64),(x-2,76)],'#49515c',1)
poly(master,[(116,59),(135,59),(139,65),(139,75),(135,81),(116,81)],'#27487d')
line(master,[(120,61),(133,61)],'#7393bb',2)
poly(master,[(137,61),(314,61),(319,66),(319,76),(314,81),(137,81)],'#a8b2bf')
poly(master,[(140,63),(311,63),(315,66),(140,68)],'#f0f3f6',None)
poly(master,[(140,75),(315,75),(311,79),(140,79)],'#626d7c',None)
# Three consistent teeth at the distal end; their shape is part of the master.
poly(master,[(273,61),(273,33),(281,33),(283,45),(291,40),(295,29),
             (302,29),(304,42),(311,38),(315,28),(321,31),(321,65),
             (315,69),(310,61)],'#aeb8c4')
line(master,[(278,58),(278,37),(281,48),(293,43),(298,34)],'#e8edf3',2)
ellipse(master,(28,64,40,76),'#d8b33c')
master=small(master)
master.save(OUT/'kingdom_key_master.png')

G=(77,70)
HAND=(405,225)
ANGLE=math.radians(218)
c,s=math.cos(ANGLE),math.sin(ANGLE)
YAW=math.radians(25 if args.foreground else 0)
FOCAL=1400.0
cy=math.cos(YAW)
k=math.sin(YAW)/FOCAL
def world(p):
    x,y=p[0]-G[0],p[1]-G[1]
    # Positive master x brings the tip closer to the camera, never changes
    # master-space geometry. All components use this same camera projection.
    denominator=1-k*x
    u,v=cy*x/denominator,y/denominator
    return (HAND[0]+c*u-s*v,HAND[1]+s*u+c*v)
translate=np.array([[1,0,-G[0]],[0,1,-G[1]],[0,0,1]],dtype=float)
camera=np.array([[cy,0,0],[0,1,0],[-k,0,1]],dtype=float)
screen=np.array([[c,-s,HAND[0]],[s,c,HAND[1]],[0,0,1]],dtype=float)
inverse=np.linalg.inv(screen @ camera @ translate)
inverse/=inverse[2,2]
coefficients=tuple(inverse.flatten()[:8])
weapon=master.transform(SIZE,Image.Transform.PERSPECTIVE,coefficients,Image.Resampling.BICUBIC)
weapon.save(OUT/'weapon_instance.png')
arm=layer()
# Near arm bends upward from retained shoulder; glove surrounds grip pivot.
poly(arm,[(345,213),(356,211),(369,239),(394,225),(399,214),
          (410,216),(416,226),(402,241),(371,256),(357,246)],'#efb286')
poly(arm,[(352,219),(364,246),(374,248),(399,232),(407,220),
          (414,227),(401,241),(371,256),(359,246)],'#c98765',None)
line(arm,[(354,216),(369,242),(394,229)],'#ffd0a0',2)
poly(arm,[(393,218),(401,208),(412,210),(420,219),(418,233),
          (408,240),(397,235)],'#19212b')
line(arm,[(400,230),(408,235),(416,230)],'#788690',2)
if args.refine:
    arm=layer()
    curve(arm,(346,216),[
        ((351,216),(357,217),(361,216)),
        ((367,226),(369,236),(375,240)),
        ((383,236),(392,229),(398,221)),
        ((402,217),(410,221),(412,226)),
        ((408,239),(389,252),(375,257)),
        ((365,260),(357,250),(355,239)),
        ((352,230),(349,222),(346,216))],'#eeb084')
    curve(arm,(358,223),[
        ((361,238),(365,252),(375,252)),
        ((388,248),(402,237),(407,228)),
        ((404,238),(388,255),(375,257)),
        ((365,259),(357,243),(358,223))],'#bd7f60',None)
    curve(arm,(354,218),[
        ((362,231),(365,241),(373,244)),
        ((382,240),(391,233),(396,227))],None,'#ffd1a3',2,False)
    curve(arm,(397,217),[
        ((399,211),(407,208),(413,212)),
        ((421,217),(422,228),(416,234)),
        ((411,241),(400,240),(396,233)),
        ((393,228),(394,221),(397,217))],'#19232d')
    curve(arm,(399,231),[
        ((405,237),(411,235),(417,230))],None,'#87939c',2,False)
arm=small(arm)
arm.save(OUT/'holding_arm.png')
fingers=layer()
for x,y in [(395,217),(400,215),(405,215),(410,217)]:
    poly(fingers,[(x,y),(x+4,y-1),(x+6,y+7),(x+2,y+10),(x,y+7)],'#f3ba8c',width=1)
poly(fingers,[(400,231),(403,224),(408,223),(409,227),(406,234)],'#e7a97f',width=1)
if args.refine:
    fingers=layer()
    # Fingers are constructed around the projected master handle, not screen
    # positions guessed independently of the weapon's orientation.
    for local_x in (66,72,78,84):
        p0=world((local_x,66))
        p1=world((local_x+4,66))
        p2=world((local_x+5,75))
        p3=world((local_x,77))
        curve(fingers,p0,[
            (p1,p1,p2),
            (p3,p3,p0)],'#f2b78b',width=1)
    thumb=[world(p) for p in [(88,73),(87,78),(81,79),(79,76),(84,72)]]
    poly(fingers,thumb,'#df9b75',width=1)
fingers=small(fingers)
fingers.save(OUT/'foreground_fingers.png')
chain=layer()
pommel=world((34,70))
chain_pts=[pommel,(pommel[0]+2,pommel[1]+12),(pommel[0]-2,pommel[1]+24),
           (pommel[0]-6,pommel[1]+35)]
line(chain,chain_pts,'#26313b',4)
line(chain,chain_pts,'#b8c2cb',2)
x,y=chain_pts[-1]
ellipse(chain,(x-5,y-2,x+5,y+8),'#abb6c3')
ellipse(chain,(x-8,y-5,x-2,y+1),'#d2dae0',width=1)
ellipse(chain,(x+2,y-5,x+8,y+1),'#d2dae0',width=1)
chain=small(chain)
chain.save(OUT/'chain.png')
preview=Image.alpha_composite(body,arm)
preview=Image.alpha_composite(preview,weapon)
preview=Image.alpha_composite(preview,chain)
# Restore original head/hair above the shaft, keeping the weapon instance intact.
head_mask=layer()
poly(head_mask,[(302,111),(324,91),(346,83),(369,58),(384,69),
                (411,66),(437,87),(442,132),(425,155),(413,166),
                (386,188),(366,185),(343,170),(321,157)],'white',None)
head_mask=small(head_mask).getchannel('A')
head=original.copy()
head.putalpha(Image.composite(original.getchannel('A'),Image.new('L',SIZE,0),head_mask))
head.save(OUT/'head_occlusion.png')
preview=Image.alpha_composite(preview,head)
preview=Image.alpha_composite(preview,fingers)
preview.save(OUT/'frame_00_construction_preview.png')
anchors={'grip':G,'pommel':(34,70),'collar':(137,70),'tip':(319,70),
         'shoulder_contact':(137,70)}
overlay=preview.copy()
dr=ImageDraw.Draw(overlay)
dr.line([world((34,70)),world((319,70))],fill='#00e5ff',width=1)
for name,p in anchors.items():
    x,y=world(p); dr.ellipse((x-3,y-3,x+3,y+3),fill='#ff4baa')
overlay.save(OUT/'frame_00_anchor_overlay.png')
comparison=Image.new('RGB',(SIZE[0]*3,550),'#202633')
for i,(im,title) in enumerate([(original,'Original'),(preview,'Construction pilot'),(overlay,'Rigid-axis anchors')]):
    comparison.paste(im,(i*SIZE[0],32),im)
    ImageDraw.Draw(comparison).text((i*SIZE[0]+12,10),title,fill='white')
comparison.save(OUT/'Comparison.png')
if args.foreground:
    previous=Image.open(ROOT/'ready/run_loop/layers/pilot_v1/frame_00_construction_preview.png').convert('RGBA')
    depth_compare=Image.new('RGB',(1024,550),'#202633')
    for i,(im,title) in enumerate([(previous,'Previous flat carry'),(preview,'Tip yawed 25 degrees toward viewer')]):
        depth_compare.paste(im,(i*512,32),im)
        ImageDraw.Draw(depth_compare).text((i*512+12,10),title,fill='white')
    depth_compare.save(OUT/'Foreground_Comparison.png')
if args.refine:
    previous=Image.open(ROOT/'ready/run_loop/layers/pilot_v2/frame_00_construction_preview.png').convert('RGBA')
    refine_compare=Image.new('RGB',(1024,550),'#202633')
    for i,(im,title) in enumerate([(previous,'Previous construction'),(preview,'Refined torso / arm / projected grip')]):
        refine_compare.paste(im,(i*512,32),im)
        ImageDraw.Draw(refine_compare).text((i*512+12,10),title,fill='white')
    refine_compare.save(OUT/'Refinement_Comparison.png')
manifest={'status':'construction pilot, not final art or approved replacement',
 'source_sha256':EXPECTED,'crop':[0,0,445,450],
 'master_grip':G,'hand_anchor':HAND,'rotation_degrees':218,'scale':1,
 'tip_toward_camera_yaw_degrees':math.degrees(YAW),
 'camera_focal_length_px':FOCAL,
 'master_to_screen_homography':(screen @ camera @ translate).tolist(),
 'tip_depth_relative_to_grip_px':-(319-G[0])*math.sin(YAW),
 'projected_shoulder_contact':world((137,70)),
 'master_anchors':anchors,'world_anchors':{k:world(v) for k,v in anchors.items()},
 'pommel_to_tip_length_px':285,
 'holding_arm':'near visible arm, provisional anatomical mapping requires review',
 'limitations':['Local chest and forearm are manual construction drawings needing stylistic review.',
 'Master length is a pilot value, not yet approved for the full batch.',
 'Shoulder contact and finger occlusion require visual review before propagation.',
 'No full animation or Godot integration.']}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
print('Saved construction pilot to',OUT)
