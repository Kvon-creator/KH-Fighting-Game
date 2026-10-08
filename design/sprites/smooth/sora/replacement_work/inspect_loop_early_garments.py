"""Original torso coordinate boards for remaining loop00-02 art."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
L = ROOT/'ready/run_loop/layers'
for index, folder, name, box in [
    (0, 'pilot_v3', 'frame_00_original.png', (230, 130, 445, 280)),
    (1, 'frame_01_v1', 'original_crop.png', (210, 145, 430, 305)),
    (2, 'frame_02_v1', 'original_crop.png', (160, 125, 355, 285)),
]:
    out = L/f'frame_{index:02d}_review_v3'
    out.mkdir(parents=True, exist_ok=True)
    original = Image.open(L/folder/name).convert('RGBA').crop(box)
    board = Image.new('RGB', (original.width*4, original.height*4+30), '#56606b')
    scaled = original.resize((original.width*4, original.height*4))
    board.paste(scaled, (0, 30), scaled)
    d = ImageDraw.Draw(board)
    d.text((8, 8), f'Loop{index:02d} original jacket/arm coordinates', fill='white')
    for x in range((box[0]//10+1)*10, box[2], 10):
        px = (x-box[0])*4
        d.line((px, 30, px, board.height), fill='#76959f')
        d.text((px+2, 32), str(x), fill='white')
    for y in range((box[1]//10+1)*10, box[3], 10):
        py = (y-box[1])*4+30
        d.line((0, py, board.width, py), fill='#76959f')
        d.text((2, py+2), str(y), fill='white')
    board.save(out/'Original_Torso_Coordinates.png')
print('Saved original torso coordinates for loop00-02; no source modified.')
