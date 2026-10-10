"""Build whole-frame motion diagrams for complete-image Gemini rendering.

No existing artwork is edited and no body/weapon sprite layers are produced.
The fixed weapon axis helps constrain the difficult idle-to-far-carry transfer.
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[6]
if str(ROOT).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {ROOT}")
OUT = ROOT / "design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/guides_clean"
OUT.mkdir(parents=True, exist_ok=True)
ground = 470
grips = [(224,280),(225,280),(226,277),(226,270),(224,252),(220,228),
         (218,190),(216,168),(215,168),(213,169),(215,172),(215,170)]
angles = [-131,-130,-125,-115,-96,-64,-29,6,6,5,6,6]
hip_y = [329,331,336,339,337,332,327,326,322,313,320,327]
far_elbows = [(215,244),(214,247),(213,251),(211,254),(212,260),(212,266),
              (215,253),(219,247),(224,248),(226,244),(227,246),(228,249)]
near_hands = [(232,283),(233,283),(234,280),(244,275),(258,268),(281,261),
              (306,253),(333,245),(354,237),(357,231),(361,234),(360,238)]
far_ankles = [(130,438)]*4 + [(132,438),(138,431),(139,429),(140,435),
              (151,439),(183,402),(185,394),(179,402)]
near_ankles = [(381,438)]*4 + [(378,438),(374,438),(362,438),(340,425),
               (327,410),(350,412),(376,423),(384,438)]
near_knees = [(333,389),(333,390),(333,393),(334,394),(336,391),(337,389),
              (334,382),(328,371),(320,362),(325,363),(328,374),(330,384)]
far_knees = [(176,388),(175,390),(174,393),(173,394),(172,391),(171,386),
             (170,384),(169,384),(177,387),(192,379),(198,374),(192,379)]
poses = []
def line(draw, points, color, width):
    draw.line(points, fill=color, width=width, joint="curve")
    for x,y in points:
        draw.ellipse((x-width/2,y-width/2,x+width/2,y+width/2), fill=color)

for i in range(12):
    im = Image.new("RGB", (512,512), "white")
    draw = ImageDraw.Draw(im)
    bob = hip_y[i]-329
    lean = min(i,7)*3
    far_shoulder = (242+lean,211+bob)
    near_shoulder = (318+lean,205+bob)
    head = (308+lean,133+bob)
    hip = (256,hip_y[i])
    grip = grips[i]
    theta = math.radians(angles[i])
    u = (math.cos(theta),math.sin(theta))
    n = (-u[1],u[0])
    def weapon_point(along, across=0):
        return (grip[0]+along*u[0]+across*n[0],grip[1]+along*u[1]+across*n[1])
    tip = weapon_point(225)
    collar = weapon_point(32)
    pommel = weapon_point(-28)
    def weapon():
        line(draw,[pommel,collar],(40,48,65),9)
        line(draw,[collar,tip],(135,148,167),12)
        line(draw,[weapon_point(29),weapon_point(40)],(56,108,171),14)
        guard = [weapon_point(-32,-24),weapon_point(32,-24),
                 weapon_point(32,24),weapon_point(-32,24),weapon_point(-32,-24)]
        draw.line(guard,fill=(196,145,30),width=8,joint="curve")
        draw.ellipse((tip[0]-6,tip[1]-6,tip[0]+6,tip[1]+6),fill=(80,91,113))
        draw.line([pommel,(pommel[0]-5,pommel[1]+24)],fill=(107,112,120),width=3)
    # Full diagram occlusion, not exported sprite layers: final carry goes behind head.
    if i >= 6:
        weapon()
    line(draw,[(246,hip_y[i]),far_knees[i],far_ankles[i]],(149,162,183),18)
    line(draw,[(269,hip_y[i]),near_knees[i],near_ankles[i]],(51,74,103),22)
    for ankle in (far_ankles[i],near_ankles[i]):
        x,y=ankle
        draw.rounded_rectangle((x-24,y+3,x+42,y+31),radius=8,fill=(209,157,35),outline=(70,61,45),width=3)
    draw.polygon([(far_shoulder[0]-15,far_shoulder[1]-10),
                  (near_shoulder[0]+10,near_shoulder[1]-9),(hip[0]+37,hip[1]+7),
                  (hip[0]-28,hip[1]+7)],fill=(225,231,239),outline=(51,74,103),width=3)
    line(draw,[far_shoulder,far_elbows[i],grip],(149,162,183),13)
    near_elbow = (291+lean,256+bob)
    line(draw,[near_shoulder,near_elbow,near_hands[i]],(51,74,103),15)
    if i < 6:
        weapon()
    draw.ellipse((head[0]-43,head[1]-54,head[0]+45,head[1]+55),fill=(243,220,190),outline=(94,71,50),width=3)
    draw.polygon([(head[0]+31,head[1]-13),(head[0]+55,head[1]+2),(head[0]+33,head[1]+15)],fill=(243,220,190),outline=(94,71,50))
    draw.ellipse((grip[0]-9,grip[1]-9,grip[0]+9,grip[1]+9),fill=(211,64,61),outline=(75,24,24),width=2)
    x,y=near_hands[i]
    draw.ellipse((x-8,y-8,x+8,y+8),fill=(45,133,95),outline=(24,76,48),width=2)
    im.save(OUT/f"guide_{i:02d}.png")
    poses.append({"frame":i,"farGrip":list(grip),"weaponAngleDegrees":angles[i],
                  "projectedGripToTipLength":225,"collar":list(collar),"tip":list(tip),
                  "pommel":list(pommel),"nearHand":list(near_hands[i]),
                  "groundY":ground,"guideNotFinalArtwork":True})
for start in (0,4,8):
    sheet=Image.new("RGB",(1024,1024),"white")
    for offset in range(4):
        with Image.open(OUT/f"guide_{start+offset:02d}.png") as frame:
            sheet.paste(frame,((offset%2)*512,(offset//2)*512))
    sheet.save(OUT/f"start_pose_guide_{start:02d}_{start+3:02d}.png")
(OUT/"manifest.json").write_text(json.dumps({"purpose":"whole-frame pose reference, not sprite layers", "frameCount":12,
                                             "frames":poses},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"guides":str(OUT),"frames":12,"constantProjectedWeaponLength":225}))
