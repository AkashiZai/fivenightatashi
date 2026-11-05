import os
import shutil
import urllib.request
import urllib.parse
import json
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

root_dir = r'C:\Users\pisit\.gemini\antigravity\scratch\fnaf-custom\assets2'
raw_dir = os.path.join(root_dir, 'raw')
bg_dir = os.path.join(root_dir, 'bg')
sp_dir = os.path.join(root_dir, 'sprites')
cam_dir = os.path.join(root_dir, 'cams')

for d in (raw_dir, bg_dir, sp_dir, cam_dir):
    os.makedirs(d, exist_ok=True)

# 1. Copy 6 raw images from Downloads\fivenightashi2
src_dir = r'c:\Users\pisit\Downloads\fivenightashi2'
for f in os.listdir(src_dir):
    shutil.copy2(os.path.join(src_dir, f), os.path.join(raw_dir, f))

# 2. Download FNaF 2 backgrounds from Wiki
targets = {
    'office_normal.png': 'File:The Office 2 No Flashlight.png',
    'office_flashlight.png': 'File:FNAF2OfficeOnlyFlashlight.png',
    'office_left_vent.png': 'File:OfficeLeftVentLight.png',
    'office_right_vent.png': 'File:OfficeRightVentLight.png',
    'mask.png': 'File:Freddy Fazbear mask FNaF 2.png',
    'cam01_empty.png': 'File:Party Room 1.png',
    'cam02_empty.png': 'File:Party Room 2.png',
    'cam03_empty.png': 'File:PartyRoom3.png',
    'cam04_empty.png': 'File:Party Room 4.png',
    'cam05_empty.png': 'File:TheLeftAirVent.png',
    'cam06_empty.png': 'File:TheRightAirVent.png',
    'cam07_empty.png': 'File:Main Hall.png',
    'cam08_empty.png': 'File:PartsAndServicesEmpty.png',
    'cam09_empty.png': 'File:FNAF2EmptyShowStageNoLight.png',
    'cam10_empty.png': 'File:TheGameArea.png',
    'cam11_empty.png': 'File:FNAF-PRIZE-CORNER.png',
    'cam12_empty.png': "File:Kid's Cove.png",
}

for out_name, wiki_title in targets.items():
    out_path = os.path.join(bg_dir, out_name)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        continue
    api_url = f'https://freddy-fazbears-pizza.fandom.com/api.php?action=query&titles={urllib.parse.quote(wiki_title)}&prop=imageinfo&iiprop=url&format=json'
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        for pid, pdata in data['query']['pages'].items():
            ii = pdata.get('imageinfo', [])
            if ii:
                r2 = urllib.request.Request(ii[0]['url'], headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(r2, timeout=15) as ir:
                    raw = ir.read()
                    with open(out_path, 'wb') as f:
                        f.write(raw)
                print(f'Downloaded {out_name} ({len(raw)} bytes)')

# 3. Chroma-key the 5 blue-screen images + extract Monchhichi sprite
raw_map = {
    'chica':   'watermarked_img_12976864321481174641.jpg',  # Sport top (Toy Chica - Left Vent)
    'foxy':    'watermarked_img_16706469538711400293.jpg',  # Fire Jacket Phoenix (Withered Foxy - Hallway Flashlight)
    'freddy':  'watermarked_img_1686269018769438363.jpg',   # Dark Ashi (Toy Freddy - Hallway -> Office Mask)
    'buff':    'watermarked_img_16895164229245470490.jpg',  # Giant Right Arm Buff Ashi (Withered Bonnie/Freddy - Parts & Service -> Office/Vent)
    'bonnie':  'watermarked_img_17687967310638655798.jpg',  # Tribal Crown Ashi (Toy Bonnie - Right Vent)
    'puppet':  'watermarked_img_876003268448254256.jpg',    # Monchhichi (The Puppet - Prize Corner Music Box)
}

sprites = {}
for name, fname in raw_map.items():
    im = Image.open(os.path.join(raw_dir, fname)).convert('RGBA')
    w, h = im.size
    if name != 'puppet':
        arr = np.array(im, dtype=np.float32)
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        # Blue screen removal while preserving orange fire sparks and skin/clothes
        blue_dom = b - np.maximum(r * 1.06, g * 0.86)
        mask = np.clip(1.0 - (blue_dom - 6.0) / 28.0, 0.0, 1.0)
        keep = (r > b + 4) | ((r < 55) & (g < 55) & (b < 75))
        mask = np.where(keep, 1.0, mask)
        alpha_im = Image.fromarray((mask * 255).astype(np.uint8), 'L')
        alpha_im = alpha_im.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
        edge = np.array(alpha_im, dtype=np.float32) / 255.0
        arr[:,:,2] = np.where(edge < 0.92, np.minimum(b, np.maximum(r, g)), b)
        arr[:,:,3] = np.array(alpha_im, dtype=np.float32)
        clean = Image.fromarray(arr.astype(np.uint8), 'RGBA')
        bbox = clean.getbbox()
        if bbox:
            clean = clean.crop(bbox)
    else:
        # For Monchhichi (puppet), crop around the doll (x: 200..960, y: 15..880) with soft vignette mask
        clean = im.crop((210, 15, 955, 885))
        cw, ch = clean.size
        yy, xx = np.ogrid[:ch, :cw]
        # Elliptical mask centered on the furry Monchhichi body
        cx, cy = cw * 0.50, ch * 0.52
        rx, ry = cw * 0.47, ch * 0.48
        dist = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        alpha = np.clip((1.08 - dist) * 5.0, 0.0, 1.0) * 255.0
        alpha_im = Image.fromarray(alpha.astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(4))
        clean.putalpha(alpha_im)

    cw, ch = clean.size
    new_h = 720
    new_w = int(cw * (new_h / ch))
    clean = clean.resize((new_w, new_h), Image.Resampling.LANCZOS)
    clean.save(os.path.join(sp_dir, f'{name}.png'))
    sprites[name] = clean
    print(f'Saved FNaF2 sprite {name}.png: {clean.size}')
