"""Local, deterministic construction pilot. Never writes source sheets."""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'ready/run_loop/layers/pilot_v1'
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
def world(p):
    x,y=p[0]-G[0],p[1]-G[1]
    return (HAND[0]+c*x-s*y,HAND[1]+s*x+c*y)
# Pillow inverse affine maps output positions back to immutable master pixels.
aff=(c,s,G[0]-c*HAND[0]-s*HAND[1],
     -s,c,G[1]+s*HAND[0]-c*HAND[1])
weapon=master.transform(SIZE,Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC)
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
arm=small(arm)
arm.save(OUT/'holding_arm.png')
fingers=layer()
for x,y in [(395,217),(400,215),(405,215),(410,217)]:
    poly(fingers,[(x,y),(x+4,y-1),(x+6,y+7),(x+2,y+10),(x,y+7)],'#f3ba8c',width=1)
poly(fingers,[(400,231),(403,224),(408,223),(409,227),(406,234)],'#e7a97f',width=1)
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
manifest={'status':'construction pilot, not final art or approved replacement',
 'source_sha256':EXPECTED,'crop':[0,0,445,450],
 'master_grip':G,'hand_anchor':HAND,'rotation_degrees':218,'scale':1,
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
