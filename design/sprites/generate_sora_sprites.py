import os
import json
import numpy as np
from PIL import Image

WORKSPACE = r"C:\Users\kvong\OneDrive\Documents\KH Fighting Game"
OUTPUT_DIR = os.path.join(WORKSPACE, "design", "sprites")
os.makedirs(OUTPUT_DIR, exist_ok=True)

APP_DIR = r"C:\Users\kvong\.gemini\antigravity\brain\c8b3a7ca-3090-4801-8b06-a34e5fdda80a"

SRC_FRONT = os.path.join(APP_DIR, "sora_kh2_pixel_art_sprite_1791316705843.jpg")
SRC_SIDE = os.path.join(APP_DIR, "sora_kh2_pixel_art_profile_1791316704264.jpg")
SRC_GUARD = os.path.join(APP_DIR, "hero_key_sprite_1791316199839.jpg")
SRC_KEY = os.path.join(APP_DIR, "kingdom_key_pixel_art_v3_png_1791316733926.jpg")

def isolate_sprite(image_path, threshold=240):
    """Removes white background and returns cropped RGBA sprite image."""
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)
    # Mask pure/near white
    white = (arr[:, :, 0] >= threshold) & (arr[:, :, 1] >= threshold) & (arr[:, :, 2] >= threshold)
    arr[white, 3] = 0
    # Clean up alpha
    vis = np.where(arr[:, :, 3] > 0)
    ymin, ymax = vis[0].min(), vis[0].max()
    xmin, xmax = vis[1].min(), vis[1].max()
    crop = Image.fromarray(arr[ymin:ymax+1, xmin:xmax+1])
    return crop

def create_model_front():
    crop = isolate_sprite(SRC_FRONT)
    # Standing height target ~96 pixels
    target_h = 96
    scale = target_h / crop.height
    target_w = int(round(crop.width * scale))
    scaled = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    # Align feet at y=112, centered on x=64
    x_pos = 64 - (target_w // 2)
    y_pos = 112 - target_h
    canvas.paste(scaled, (x_pos, y_pos), scaled)
    return canvas

def create_model_side():
    crop = isolate_sprite(SRC_SIDE)
    # Side standing height target ~96 pixels
    target_h = 96
    scale = target_h / crop.height
    target_w = int(round(crop.width * scale))
    scaled = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    x_pos = 64 - (target_w // 2)
    y_pos = 112 - target_h
    canvas.paste(scaled, (x_pos, y_pos), scaled)
    return canvas

def create_model_guard():
    crop = isolate_sprite(SRC_GUARD)
    # Combat guard has bent knees; body height ~88 pixels
    target_h = 88
    scale = target_h / crop.height
    target_w = int(round(crop.width * scale))
    scaled = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    x_pos = 64 - (target_w // 2) - 4 # slightly shifted left to center mass
    y_pos = 112 - target_h
    canvas.paste(scaled, (x_pos, y_pos), scaled)
    return canvas

def create_keyblade_ref():
    crop = isolate_sprite(SRC_KEY)
    # Scale to weapon proportions: weapon blade length ~56 pixels, fits inside 128x128
    target_w = 90
    scale = target_w / crop.width
    target_h = int(round(crop.height * scale))
    scaled = crop.resize((target_w, target_h), Image.Resampling.NEAREST)
    
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    x_pos = (128 - target_w) // 2
    y_pos = (128 - target_h) // 2
    canvas.paste(scaled, (x_pos, y_pos), scaled)
    return canvas

def generate_idle_frames(guard_master):
    """
    Builds the 8 breathing idle frames according to Sora_Idle_Drawing_Guide:
    - Feet stay completely locked at foot-contact y=112
    - Shins and lower shorts remain stationary
    - Torso, chest, shoulders, head and rigid Keyblade follow breathing offsets
    """
    arr = np.array(guard_master)
    
    # Split anatomy:
    # Lower body: y >= 76 (shorts, legs, shoes)
    # Upper body: y < 76 (torso, arms, head, Keyblade)
    split_y = 75
    
    frames = []
    
    # Breathing specification table from guide:
    # 00: Neutral, dy=0, cx=0, chain=0, hold=160
    # 01: Begin inhale, dy=0, cx=1, chain=0, hold=140
    # 02: Inhale, dy=-1, cx=0, chain=0, hold=140
    # 03: Full inhale, dy=-1, cx=1, chain=1, hold=200
    # 04: Begin exhale, dy=-1, cx=0, chain=1, hold=160
    # 05: Exhale, dy=0, cx=0, chain=0, hold=140
    # 06: Settle, dy=0, cx=0, chain=0, hold=140
    # 07: Loop bridge, dy=0, cx=0, chain=0, hold=200
    frame_specs = [
        {"dy": 0, "cx": 0, "chain": 0, "hold": 160},
        {"dy": 0, "cx": 1, "chain": 0, "hold": 140},
        {"dy": -1, "cx": 0, "chain": 0, "hold": 140},
        {"dy": -1, "cx": 1, "chain": 1, "hold": 200},
        {"dy": -1, "cx": 0, "chain": 1, "hold": 160},
        {"dy": 0, "cx": 0, "chain": 0, "hold": 140},
        {"dy": 0, "cx": 0, "chain": 0, "hold": 140},
        {"dy": 0, "cx": 0, "chain": 0, "hold": 200},
    ]
    
    for idx, spec in enumerate(frame_specs):
        f_arr = np.zeros_like(arr)
        dy = spec["dy"]
        cx = spec["cx"]
        
        # 1. Lower body (stationary, feet firmly planted)
        f_arr[split_y:, :] = arr[split_y:, :]
        
        # 2. Upper body with dy offset
        upper = arr[:split_y, :]
        # Shift upper body by dy
        if dy == 0:
            f_arr[:split_y, :] = upper
        elif dy == -1:
            # Shift up by 1 pixel
            f_arr[:split_y - 1, :] = upper[1:, :]
            # Fill the seam at split_y - 1 to maintain seamless anatomical connection
            f_arr[split_y - 1, :] = upper[-1, :]
            
        # 3. Chest expansion (subtle 1px lateral contour expansion if cx=1)
        if cx == 1:
            # Chest region is roughly y: 48..65, x: 55..65
            # Subtly widen chest highlight/contour by 1 pixel forward
            for y in range(48 + dy, 62 + dy):
                for x in range(65, 45, -1):
                    if f_arr[y, x, 3] > 0:
                        # duplicate edge pixel 1px rightward for gentle expansion
                        f_arr[y, x + 1] = f_arr[y, x]
                        break

        frame_img = Image.fromarray(f_arr)
        frames.append((frame_img, spec["hold"]))
        
    return frames, frame_specs

def build_sprite_sheet(frames):
    # 4 columns by 2 rows -> 512 x 256
    sheet = Image.new("RGBA", (512, 256), (0, 0, 0, 0))
    for i, (frame_img, _) in enumerate(frames):
        col = i % 4
        row = i // 4
        sheet.paste(frame_img, (col * 128, row * 128), frame_img)
    return sheet

def measure_anchors(frames):
    """
    Measures attachment points for each frame:
    - body anchor: (64, 112)
    - rear foot contact: lowest opaque pixel in rear shoe
    - front foot contact: lowest opaque pixel in front shoe
    - weapon grip: center of handguard/grip
    - weapon tip: highest/farthest pixel of keyblade teeth
    - head reference: top spike of hair
    """
    manifest_frames = []
    
    for i, (frame_img, hold) in enumerate(frames):
        arr = np.array(frame_img)
        vis = np.where(arr[:, :, 3] > 0)
        
        # Head reference (topmost pixel in hair region x: 45..65)
        hair_mask = (vis[1] >= 40) & (vis[1] <= 65)
        if np.any(hair_mask):
            head_y = int(vis[0][hair_mask].min())
            head_x = int(vis[1][hair_mask][vis[0][hair_mask].argmin()])
        else:
            head_y = int(vis[0].min())
            head_x = 64
            
        # Front foot contact (x >= 60, lowest y)
        front_mask = vis[1] >= 60
        front_y = int(vis[0][front_mask].max())
        front_x = int(vis[1][front_mask][vis[0][front_mask].argmax()])
        
        # Rear foot contact (x < 60, lowest y)
        rear_mask = vis[1] < 60
        rear_y = int(vis[0][rear_mask].max())
        rear_x = int(vis[1][rear_mask][vis[0][rear_mask].argmax()])
        
        # Weapon tip (x > 80, highest y in that zone)
        tip_mask = vis[1] >= 80
        if np.any(tip_mask):
            tip_y = int(vis[0][tip_mask].min())
            tip_x = int(vis[1][tip_mask][vis[0][tip_mask].argmin()])
        else:
            tip_x, tip_y = 95, 30
            
        # Grip point (hands region around x: 55..65, y: 55..65)
        # In frame 00 it is approximately (58, 62)
        dy = 0 if i in [0, 1, 5, 6, 7] else -1
        grip_x = 58
        grip_y = 62 + dy
        
        frame_data = {
            "index": i,
            "filename": f"sora_idle_{i:02d}.png",
            "duration_ms": hold,
            "canvas_size": [128, 128],
            "body_anchor": [64, 112],
            "front_foot_contact": [front_x, front_y],
            "rear_foot_contact": [rear_x, rear_y],
            "head_reference": [head_x, head_y],
            "weapon_grip": [grip_x, grip_y],
            "weapon_tip": [tip_x, tip_y],
            "mirrored_facing_right_to_left": {
                "body_anchor": [127 - 64, 112],
                "front_foot_contact": [127 - front_x, front_y],
                "rear_foot_contact": [127 - rear_x, rear_y],
                "head_reference": [127 - head_x, head_y],
                "weapon_grip": [127 - grip_x, grip_y],
                "weapon_tip": [127 - tip_x, tip_y]
            }
        }
        manifest_frames.append(frame_data)
        
    return manifest_frames

def main():
    print("Generating Sora character model sheet and idle pilot...")
    
    # 1. Model sheet
    model_front = create_model_front()
    path_front = os.path.join(OUTPUT_DIR, "sora_model_front_v1.png")
    model_front.save(path_front)
    print(f"Saved: {path_front}")
    
    model_side = create_model_side()
    path_side = os.path.join(OUTPUT_DIR, "sora_model_side_v1.png")
    model_side.save(path_side)
    print(f"Saved: {path_side}")
    
    model_guard = create_model_guard()
    path_guard = os.path.join(OUTPUT_DIR, "sora_model_guard_v1.png")
    model_guard.save(path_guard)
    print(f"Saved: {path_guard}")
    
    model_key = create_keyblade_ref()
    path_key = os.path.join(OUTPUT_DIR, "sora_kingdom_key_reference_v1.png")
    model_key.save(path_key)
    print(f"Saved: {path_key}")
    
    # 2. Eight-frame idle animation
    frames, specs = generate_idle_frames(model_guard)
    for i, (frame_img, _) in enumerate(frames):
        p = os.path.join(OUTPUT_DIR, f"sora_idle_{i:02d}.png")
        frame_img.save(p)
        print(f"Saved: {p}")
        
    # 3. Source sprite sheet (512x256, 4x2)
    sheet = build_sprite_sheet(frames)
    path_sheet = os.path.join(OUTPUT_DIR, "sora_idle_sheet_v1.png")
    sheet.save(path_sheet)
    print(f"Saved sprite sheet: {path_sheet}")
    
    # 4. Animated GIF previews
    # Native 128x128
    gif_frames = [f[0].convert("RGBA") for f in frames]
    durations = [f[1] for f in frames]
    path_gif = os.path.join(OUTPUT_DIR, "sora_idle_preview.gif")
    gif_frames[0].save(
        path_gif,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    print(f"Saved animated preview: {path_gif}")
    
    # Scaled 3x (384x384) for clear inspection
    scaled_frames = [f[0].resize((384, 384), Image.Resampling.NEAREST).convert("RGBA") for f in frames]
    path_gif_scaled = os.path.join(OUTPUT_DIR, "sora_idle_preview_scaled.gif")
    scaled_frames[0].save(
        path_gif_scaled,
        save_all=True,
        append_images=scaled_frames[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    print(f"Saved scaled preview: {path_gif_scaled}")
    
    # Mirrored preview (facing left)
    mirrored_frames = [f.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for f in scaled_frames]
    path_gif_mirrored = os.path.join(OUTPUT_DIR, "sora_idle_preview_mirrored.gif")
    mirrored_frames[0].save(
        path_gif_mirrored,
        save_all=True,
        append_images=mirrored_frames[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    print(f"Saved mirrored preview: {path_gif_mirrored}")
    
    # 5. Manifest JSON
    manifest_data = {
        "character": "Sora",
        "design": "Standard Kingdom Hearts II outfit & Kingdom Key",
        "animation": "combat_stance_idle",
        "total_frames": 8,
        "total_duration_ms": sum(durations),
        "loop": True,
        "canvas_size": [128, 128],
        "standing_height_target": 96,
        "combat_pose_height": 88,
        "foot_contact_baseline_y": 112,
        "sprite_sheet": {
            "filename": "sora_idle_sheet_v1.png",
            "dimensions": [512, 256],
            "columns": 4,
            "rows": 2,
            "frame_order": ["00", "01", "02", "03", "04", "05", "06", "07"]
        },
        "frames": measure_anchors(frames)
    }
    
    path_manifest = os.path.join(OUTPUT_DIR, "sora_idle_manifest.json")
    with open(path_manifest, "w") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Saved manifest: {path_manifest}")

if __name__ == "__main__":
    main()
