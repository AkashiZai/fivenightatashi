import os, urllib.request
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageSequence

ROOT = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(ROOT, 'assets4', 'bg')
SPRITE_DIR = os.path.join(ROOT, 'assets4', 'sprites')
CAM_DIR = os.path.join(ROOT, 'assets4', 'cams')

os.makedirs(BG_DIR, exist_ok=True)
os.makedirs(SPRITE_DIR, exist_ok=True)
os.makedirs(CAM_DIR, exist_ok=True)

WIKI_URLS = {
    'bedroom_main.jpg':   'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/e/ef/Bedroomviewfnaf4.jpg/revision/latest?cb=20180615024413',
    'bed_empty.png':      'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/c/c5/Bed.png/revision/latest?cb=20150728180100',
    'left_hall.png':      'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/7/76/LeftHall.png/revision/latest?cb=20150730153347',
    'right_hall.png':     'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/f/fc/Righthall.png/revision/latest?cb=20150730170154',
    'closet_plush.png':   'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/3/32/MangleDollCloset.png/revision/latest?cb=20151031190749',
    'left_door_anim.gif': 'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/7/71/FNAF4_LeftDoor_OpenClose.gif/revision/latest?cb=20150801212344',
    'right_door_anim.gif':'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/e/e3/FNAF4_RightDoor_OpenClose.gif/revision/latest?cb=20150801212412',
    'closet_anim.gif':    'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/7/74/FNAF4_Closet_OpenClose.gif/revision/latest?cb=20250515132938',
}

print("1. Downloading authentic FNaF 4 room, door, hall, closet & bed textures...")
for fname, url in WIKI_URLS.items():
    out_p = os.path.join(BG_DIR, fname)
    if not os.path.exists(out_p):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(out_p, 'wb') as f:
            f.write(resp.read())
        print("  Downloaded", fname)

def extract_gif_extremes(gif_path):
    im = Image.open(gif_path)
    frames = [f.copy().convert('RGB') for f in ImageSequence.Iterator(im)]
    # First frame is open/dark doorway, middle frame is fully shut door!
    return frames[0], frames[len(frames)//2]

ld_open, ld_shut = extract_gif_extremes(os.path.join(BG_DIR, 'left_door_anim.gif'))
rd_open, rd_shut = extract_gif_extremes(os.path.join(BG_DIR, 'right_door_anim.gif'))
cl_open, cl_shut = extract_gif_extremes(os.path.join(BG_DIR, 'closet_anim.gif'))

# 2. Build the 7 Nightmare Ashi Sprites (Gritty dark crimson/indigo Nightmare aesthetic + glowing eyes & Nightmare claws/teeth)
def make_nightmare_sprite(src_path, out_name, tint=(1.15, 0.72, 0.72), dark_pow=1.45, alpha_scale=1.0, shadow_mode=False):
    im = Image.open(src_path).convert('RGBA')
    a = np.array(im, dtype=np.float32)
    alpha = a[:,:,3]
    rgb = a[:,:,:3]
    lum = 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]

    h_i, w_i = lum.shape
    yy_i, xx_i = np.mgrid[0:h_i, 0:w_i]

    # High-frequency metallic/withered micro-rips & edge rim-lighting
    edge_grad = np.abs(np.gradient(lum)[0]) + np.abs(np.gradient(lum)[1])
    rim = np.clip(edge_grad * 1.8, 0, 95)

    out = np.zeros_like(a)
    if shadow_mode:
        # NIGHTMARE (Translucent black/shadow animatronic with crimson-red rim & glowing eyes)
        base = np.clip((lum / 255.0) ** 2.2 * 55.0, 0, 65)
        out[:,:,0] = np.clip(base + rim * 1.45, 0, 255)
        out[:,:,1] = np.clip(base * 0.35 + rim * 0.25, 0, 255)
        out[:,:,2] = np.clip(base * 0.45 + rim * 0.35, 0, 255)
        out[:,:,3] = np.clip(alpha * 0.88, 0, 255)
    else:
        crushed = ((lum / 255.0) ** dark_pow) * 255.0
        out[:,:,0] = np.clip((rgb[:,:,0] * 0.55 + crushed * 0.45) * tint[0] + rim * 0.55, 0, 255)
        out[:,:,1] = np.clip((rgb[:,:,1] * 0.55 + crushed * 0.45) * tint[1] + rim * 0.22, 0, 255)
        out[:,:,2] = np.clip((rgb[:,:,2] * 0.55 + crushed * 0.45) * tint[2] + rim * 0.28, 0, 255)
        out[:,:,3] = np.clip(alpha * alpha_scale, 0, 255)

    res = Image.fromarray(out.astype(np.uint8), mode='RGBA')
    res = ImageEnhance.Contrast(res).enhance(1.42)
    res = ImageEnhance.Sharpness(res).enhance(2.0)
    res.save(os.path.join(SPRITE_DIR, out_name))
    print("  Created Nightmare sprite:", out_name)

make_nightmare_sprite(os.path.join(ROOT, 'assets', 'sprites', 'freddy.png'),   'n_freddy.png',   tint=(1.12, 0.78, 0.65), dark_pow=1.40)
make_nightmare_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'bonnie.png'),  'n_bonnie.png',   tint=(0.78, 0.82, 1.25), dark_pow=1.42)
make_nightmare_sprite(os.path.join(ROOT, 'assets', 'sprites', 'chica.png'),    'n_chica.png',    tint=(1.22, 0.95, 0.58), dark_pow=1.40)
make_nightmare_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'foxy.png'),    'n_foxy.png',     tint=(1.32, 0.65, 0.55), dark_pow=1.38)
make_nightmare_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'buff.png'),    'n_fredbear.png', tint=(1.28, 1.05, 0.52), dark_pow=1.35)
make_nightmare_sprite(os.path.join(ROOT, 'assets3', 'sprites', 'springtrap.png'), 'nightmare.png', shadow_mode=True)
make_nightmare_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'puppet.png'),  'plushtrap.png',  tint=(0.95, 1.15, 0.62), dark_pow=1.30)

# 3. Helper to composite sprites with FNaF 4 Flashlight cone effect
def apply_flashlight_vignette(img_rgb, cx=512, cy=384, rx=430, ry=340, ambient=0.14):
    a = np.array(img_rgb, dtype=np.float32)
    h_i, w_i, _ = a.shape
    yy, xx = np.mgrid[0:h_i, 0:w_i]
    dist = np.sqrt(((xx - cx) / float(rx)) ** 2 + ((yy - cy) / float(ry)) ** 2)
    beam = np.clip(1.18 - (dist ** 1.65), ambient, 1.08)
    a[:,:,0] = np.clip(a[:,:,0] * beam * 1.04, 0, 255)
    a[:,:,1] = np.clip(a[:,:,1] * beam * 0.98, 0, 255)
    a[:,:,2] = np.clip(a[:,:,2] * beam * 0.88, 0, 255)
    return Image.fromarray(a.astype(np.uint8), mode='RGB')

def paste_nm(bg, sprite_name, scale_h, center_x, bottom_y, brightness=0.72, contrast=1.38, crop_bottom=1.0, flip_x=False):
    canvas = bg.copy().convert('RGBA')
    sp = Image.open(os.path.join(SPRITE_DIR, sprite_name)).convert('RGBA')
    if flip_x:
        sp = sp.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if crop_bottom < 1.0:
        sp = sp.crop((0, 0, sp.width, int(sp.height * crop_bottom)))
    sp = ImageEnhance.Brightness(sp).enhance(brightness)
    sp = ImageEnhance.Contrast(sp).enhance(contrast)
    ratio = scale_h / float(sp.height)
    new_w = max(1, int(sp.width * ratio))
    sp = sp.resize((new_w, int(scale_h)), Image.Resampling.LANCZOS)
    px = int(center_x - new_w // 2)
    py = int(bottom_y - scale_h)
    canvas.alpha_composite(sp, dest=(px, py))
    return canvas.convert('RGB')

print("3. Compositing all FNaF 4 Bedroom, Hallway, Closet, Bed & Plushtrap views...")

# A. Bedroom Center Views (1300x768)
bed_main = Image.open(os.path.join(BG_DIR, 'bedroom_main.jpg')).convert('RGB')
bed_main.save(os.path.join(CAM_DIR, 'bedroom_normal.jpg'), quality=90)

# Bedroom with Foxy peeking from Closet or Bonnie/Chica peeking from side doors
bed_closet_peek = paste_nm(bed_main, 'n_foxy.png', scale_h=260, center_x=652, bottom_y=515, brightness=0.42, contrast=1.50, crop_bottom=0.65)
bed_closet_peek.save(os.path.join(CAM_DIR, 'bedroom_closet_open.jpg'), quality=90)

# B. Left Door & Left Hallway (1024x768)
ld_open.save(os.path.join(CAM_DIR, 'left_door_dark.jpg'), quality=90)
ld_shut.save(os.path.join(CAM_DIR, 'left_door_shut.jpg'), quality=90)

lhall = Image.open(os.path.join(BG_DIR, 'left_hall.png')).convert('RGB')
lhall.save(os.path.join(CAM_DIR, 'left_hall_empty.jpg'), quality=90)

# Far in Left Hallway (peeking from behind the far pillar around x=545, y=490)
lh_bon_far = paste_nm(lhall, 'n_bonnie.png', scale_h=285, center_x=548, bottom_y=520, brightness=0.58, contrast=1.45, crop_bottom=0.80)
lh_bon_far.save(os.path.join(CAM_DIR, 'left_hall_bonnie_far.jpg'), quality=90)

# Close in Left Hallway (looming right in the hallway beam!)
lh_bon_close = paste_nm(lhall, 'n_bonnie.png', scale_h=640, center_x=520, bottom_y=755, brightness=0.78, contrast=1.48, crop_bottom=0.85)
lh_bon_close.save(os.path.join(CAM_DIR, 'left_hall_bonnie_close.jpg'), quality=90)

lh_fb = paste_nm(lhall, 'n_fredbear.png', scale_h=540, center_x=535, bottom_y=690, brightness=0.75, contrast=1.50, crop_bottom=0.85)
lh_fb.save(os.path.join(CAM_DIR, 'left_hall_fredbear.jpg'), quality=90)

lh_nm = paste_nm(lhall, 'nightmare.png', scale_h=560, center_x=535, bottom_y=705, brightness=0.85, contrast=1.55, crop_bottom=0.85)
lh_nm.save(os.path.join(CAM_DIR, 'left_hall_nightmare.jpg'), quality=90)

# C. Right Door & Right Hallway (1024x768)
rd_open.save(os.path.join(CAM_DIR, 'right_door_dark.jpg'), quality=90)
rd_shut.save(os.path.join(CAM_DIR, 'right_door_shut.jpg'), quality=90)

rhall = Image.open(os.path.join(BG_DIR, 'right_hall.png')).convert('RGB')
rhall.save(os.path.join(CAM_DIR, 'right_hall_empty.jpg'), quality=90)

rh_chi_far = paste_nm(rhall, 'n_chica.png', scale_h=285, center_x=475, bottom_y=520, brightness=0.58, contrast=1.45, crop_bottom=0.80)
rh_chi_far.save(os.path.join(CAM_DIR, 'right_hall_chica_far.jpg'), quality=90)

rh_chi_close = paste_nm(rhall, 'n_chica.png', scale_h=640, center_x=500, bottom_y=755, brightness=0.78, contrast=1.48, crop_bottom=0.85)
rh_chi_close.save(os.path.join(CAM_DIR, 'right_hall_chica_close.jpg'), quality=90)

rh_fb = paste_nm(rhall, 'n_fredbear.png', scale_h=540, center_x=490, bottom_y=690, brightness=0.75, contrast=1.50, crop_bottom=0.85)
rh_fb.save(os.path.join(CAM_DIR, 'right_hall_fredbear.jpg'), quality=90)

rh_nm = paste_nm(rhall, 'nightmare.png', scale_h=560, center_x=490, bottom_y=705, brightness=0.85, contrast=1.55, crop_bottom=0.85)
rh_nm.save(os.path.join(CAM_DIR, 'right_hall_nightmare.jpg'), quality=90)

# D. Closet Views (1024x768)
cl_open.save(os.path.join(CAM_DIR, 'closet_dark.jpg'), quality=90)
cl_shut.save(os.path.join(CAM_DIR, 'closet_shut.jpg'), quality=90)

cl_plush = Image.open(os.path.join(BG_DIR, 'closet_plush.png')).convert('RGB')
cl_plush.save(os.path.join(CAM_DIR, 'closet_plush.jpg'), quality=90)
# Empty closet illuminated
cl_lit = apply_flashlight_vignette(ImageEnhance.Brightness(cl_open).enhance(2.2), cx=512, cy=400, rx=360, ry=330)
cl_lit.save(os.path.join(CAM_DIR, 'closet_empty.jpg'), quality=90)

cl_fx1 = paste_nm(cl_lit, 'n_foxy.png', scale_h=480, center_x=512, bottom_y=690, brightness=0.68, contrast=1.45, crop_bottom=0.78)
cl_fx1.save(os.path.join(CAM_DIR, 'closet_foxy_1.jpg'), quality=90)

cl_fx2 = paste_nm(cl_lit, 'n_foxy.png', scale_h=680, center_x=512, bottom_y=768, brightness=0.82, contrast=1.52, crop_bottom=0.68)
cl_fx2.save(os.path.join(CAM_DIR, 'closet_foxy_2.jpg'), quality=90)

cl_fb = paste_nm(cl_lit, 'n_fredbear.png', scale_h=650, center_x=512, bottom_y=760, brightness=0.78, contrast=1.50, crop_bottom=0.72)
cl_fb.save(os.path.join(CAM_DIR, 'closet_fredbear.jpg'), quality=90)

cl_nm = paste_nm(cl_lit, 'nightmare.png', scale_h=670, center_x=512, bottom_y=768, brightness=0.88, contrast=1.55, crop_bottom=0.72)
cl_nm.save(os.path.join(CAM_DIR, 'closet_nightmare.jpg'), quality=90)

# E. Bed Views (1024x768 - Behind You!)
bed_lit = Image.open(os.path.join(BG_DIR, 'bed_empty.png')).convert('RGB')
bed_lit.save(os.path.join(CAM_DIR, 'bed_empty.jpg'), quality=90)

bed_dark = ImageEnhance.Brightness(bed_lit).enhance(0.16)
bed_dark.save(os.path.join(CAM_DIR, 'bed_dark.jpg'), quality=90)

# 1, 2, and 3 Mini-Ashis (Freddles) sitting on the Bed!
f1 = paste_nm(bed_lit, 'n_freddy.png', scale_h=220, center_x=510, bottom_y=470, brightness=0.72, contrast=1.48, crop_bottom=0.72)
f1.save(os.path.join(CAM_DIR, 'bed_freddles_1.jpg'), quality=90)

f2 = paste_nm(f1, 'n_freddy.png', scale_h=210, center_x=370, bottom_y=485, brightness=0.70, contrast=1.48, crop_bottom=0.72, flip_x=True)
f2.save(os.path.join(CAM_DIR, 'bed_freddles_2.jpg'), quality=90)

f3 = paste_nm(f2, 'n_freddy.png', scale_h=215, center_x=655, bottom_y=485, brightness=0.74, contrast=1.48, crop_bottom=0.72)
f3.save(os.path.join(CAM_DIR, 'bed_freddles_3.jpg'), quality=90)

bed_fb = paste_nm(bed_lit, 'n_fredbear.png', scale_h=560, center_x=512, bottom_y=640, brightness=0.78, contrast=1.50, crop_bottom=0.68)
bed_fb.save(os.path.join(CAM_DIR, 'bed_fredbear.jpg'), quality=90)

bed_nm = paste_nm(bed_lit, 'nightmare.png', scale_h=580, center_x=512, bottom_y=650, brightness=0.88, contrast=1.55, crop_bottom=0.68)
bed_nm.save(os.path.join(CAM_DIR, 'bed_nightmare.jpg'), quality=90)

# F. Fun with Plushtrap Hallway Views (1024x768)
pt_base = lhall.copy()
draw_pt = ImageDraw.Draw(pt_base)
# Draw the white 'X' on the floor at (512, 615) for Fun with Plushtrap!
draw_pt.line([(465, 585), (560, 645)], fill=(220, 220, 200), width=9)
draw_pt.line([(560, 585), (465, 645)], fill=(220, 220, 200), width=9)
pt_base.save(os.path.join(CAM_DIR, 'plushtrap_empty.jpg'), quality=90)

pt_dark = ImageEnhance.Brightness(pt_base).enhance(0.12)
pt_dark.save(os.path.join(CAM_DIR, 'plushtrap_dark.jpg'), quality=90)

pt_chair = paste_nm(pt_base, 'plushtrap.png', scale_h=175, center_x=512, bottom_y=450, brightness=0.68, contrast=1.42, crop_bottom=0.85)
pt_chair.save(os.path.join(CAM_DIR, 'plushtrap_chair.jpg'), quality=90)

pt_far = paste_nm(pt_base, 'plushtrap.png', scale_h=245, center_x=512, bottom_y=535, brightness=0.74, contrast=1.45, crop_bottom=0.85)
pt_far.save(os.path.join(CAM_DIR, 'plushtrap_far.jpg'), quality=90)

pt_x = paste_nm(pt_base, 'plushtrap.png', scale_h=340, center_x=512, bottom_y=635, brightness=0.82, contrast=1.48, crop_bottom=0.85)
pt_x.save(os.path.join(CAM_DIR, 'plushtrap_x.jpg'), quality=90)

print("Done! Total frames in assets4/cams:", len(os.listdir(CAM_DIR)))
