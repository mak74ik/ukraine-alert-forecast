import math
import os
import subprocess
from PIL import Image, ImageDraw

def create_radar_icon(size=1024):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer squircle / rounded rect base
    padding = int(size * 0.08)
    radius = int(size * 0.22)
    box = [padding, padding, size - padding, size - padding]
    
    # Background: Deep tech dark blue gradient simulation
    draw.rounded_rectangle(box, radius=radius, fill=(10, 15, 29, 255), outline=(30, 45, 75, 255), width=int(size * 0.015))
    
    # Radar center & max radius
    cx, cy = size // 2, size // 2
    r_max = int(size * 0.38)
    
    # Concentric radar rings (cyan / blue glow)
    for step in [0.25, 0.5, 0.75, 1.0]:
        r = int(r_max * step)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(35, 70, 120, 180), width=int(size * 0.008))
        
    # Crosshairs
    draw.line([cx - r_max, cy, cx + r_max, cy], fill=(35, 70, 120, 180), width=int(size * 0.008))
    draw.line([cx, cy - r_max, cx, cy + r_max], fill=(35, 70, 120, 180), width=int(size * 0.008))
    
    # Radar sweep sector (transparent yellow/gold to blue)
    sweep_overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sweep_draw = ImageDraw.Draw(sweep_overlay)
    
    # Draw sweep gradient pie slices
    for angle in range(-45, 15):
        rad = math.radians(angle)
        alpha = int(200 * (angle + 45) / 60.0)
        # Ukrainian gold sweep: (255, 215, 0)
        x_end = cx + r_max * math.cos(rad)
        y_end = cy + r_max * math.sin(rad)
        sweep_draw.line([cx, cy, x_end, y_end], fill=(255, 215, 0, alpha), width=int(size * 0.015))
        
    # Composite sweep
    img = Image.alpha_composite(img, sweep_overlay)
    draw = ImageDraw.Draw(img)
    
    # Trident / Shield or Signal Pulse at center (Ukrainian Blue & Gold)
    # Gold top circle, blue bottom pulse
    draw.ellipse([cx - int(size*0.04), cy - int(size*0.04), cx + int(size*0.04), cy + int(size*0.04)], fill=(0, 102, 204, 255), outline=(255, 215, 0, 255), width=int(size * 0.012))
    
    # Blips (targets) on radar
    # Target 1 (red alert blip)
    t1_x, t1_y = cx + int(r_max * 0.45), cy - int(r_max * 0.35)
    draw.ellipse([t1_x - int(size*0.025), t1_y - int(size*0.025), t1_x + int(size*0.025), t1_y + int(size*0.025)], fill=(239, 68, 68, 255), outline=(255, 100, 100, 200), width=int(size*0.006))
    
    # Target 2 (yellow alert blip)
    t2_x, t2_y = cx - int(r_max * 0.5), cy - int(r_max * 0.2)
    draw.ellipse([t2_x - int(size*0.02), t2_y - int(size*0.02), t2_x + int(size*0.02), t2_y + int(size*0.02)], fill=(234, 179, 8, 255))
    
    return img

os.makedirs("assets", exist_ok=True)
base_img = create_radar_icon(1024)
base_img.save("assets/icon_1024.png")

# Generate iconset for macOS
iconset_dir = "assets/icon.iconset"
os.makedirs(iconset_dir, exist_ok=True)

sizes = [
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]

for s, name in sizes:
    resized = base_img.resize((s, s), Image.Resampling.LANCZOS)
    resized.save(os.path.join(iconset_dir, name))

# Build .icns using iconutil
subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", "assets/icon.icns"], check=True)

# Build .ico for Windows
base_img.save("assets/icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("Generated assets/icon.icns and assets/icon.ico successfully!")
