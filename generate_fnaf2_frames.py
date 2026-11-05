import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

root_dir = r'C:\Users\pisit\.gemini\antigravity\scratch\fnaf-custom\assets2'
bg_dir = os.path.join(root_dir, 'bg')
sp_dir = os.path.join(root_dir, 'sprites')
cam_dir = os.path.join(root_dir, 'cams')
os.makedirs(cam_dir, exist_ok=True)

sprites = {
    name: Image.open(os.path.join(sp_dir, f'{name}.png')).convert('RGBA')
    for name in ['freddy', 'bonnie', 'chica', 'foxy', 'buff', 'puppet']
}

def load_bg(name):
    p = os.path.join(bg_dir, name)
    im = Image.open(p).convert('RGBA')
    if im.size != (1600, 720):
        im = im.resize((1600, 720), Image.Resampling.LANCZOS)
    return im

def style_sp(name, brightness=0.58, contrast=1.38, color=0.55, tint=(255, 255, 255), angle=0, crop_bottom=1.0):
    sp = sprites[name].copy()
    w, h = sp.size
    if crop_bottom < 1.0:
        sp = sp.crop((0, 0, w, int(h * crop_bottom)))
    rgb = sp.convert('RGB')
    rgb = ImageEnhance.Color(rgb).enhance(color)
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    arr = np.array(rgb, dtype=np.float32)
    arr[:,:,0] = np.clip(arr[:,:,0] * (tint[0] / 255.0), 0, 255)
    arr[:,:,1] = np.clip(arr[:,:,1] * (tint[1] / 255.0), 0, 255)
    arr[:,:,2] = np.clip(arr[:,:,2] * (tint[2] / 255.0), 0, 255)
    out = Image.fromarray(arr.astype(np.uint8), 'RGB').convert('RGBA')
    out.putalpha(sp.split()[3])
    if angle != 0:
        out = out.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    return out

def paste_char(bg, sp, center_x, bottom_y, target_h, shadow=0.55):
    res = bg.copy()
    w, h = sp.size
    scale = target_h / h
    nw, nh = int(w * scale), int(target_h)
    sp_resized = sp.resize((nw, nh), Image.Resampling.LANCZOS)
    x = int(center_x - nw // 2)
    y = int(bottom_y - nh)
    if shadow > 0:
        alpha = sp_resized.split()[3]
        sh = Image.new('RGBA', (nw, nh), (0, 0, 0, 0))
        sh.putalpha(alpha.point(lambda p: int(p * shadow)))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        res.alpha_composite(sh, (x + 8, y + 6))
    res.alpha_composite(sp_resized, (x, y))
    return res

# --- 1. FNAF 2 OFFICE STATES ---
off_norm = load_bg('office_normal.png')
off_flash = load_bg('office_flashlight.png')
off_lvent = load_bg('office_left_vent.png')
off_rvent = load_bg('office_right_vent.png')

off_norm.convert('RGB').save(os.path.join(cam_dir, 'office_normal.jpg'), quality=90)
off_flash.convert('RGB').save(os.path.join(cam_dir, 'office_hall_empty.jpg'), quality=90)
off_lvent.convert('RGB').save(os.path.join(cam_dir, 'office_left_empty.jpg'), quality=90)
off_rvent.convert('RGB').save(os.path.join(cam_dir, 'office_right_empty.jpg'), quality=90)

# Central Hallway Flashlight states (Hallway is centered around x=775, y=130..535 behind the desk!)
# Create a mask so characters in the Central Hallway stand BEHIND the office desk (desk top is around y=495)
desk_mask = Image.new('L', (1600, 720), 0)
draw_dm = ImageDraw.Draw(desk_mask)
draw_dm.polygon([(590, 95), (960, 95), (960, 515), (590, 515)], fill=255)
desk_mask = desk_mask.filter(ImageFilter.GaussianBlur(3))

def make_hall_frame(sp, cx=775, by=525, th=390, base=off_flash):
    layer = paste_char(base, sp, cx, by, th)
    return Image.composite(layer, base, desk_mask)

sp_foxy_hall = style_sp('foxy', brightness=0.72, contrast=1.35, color=0.85, tint=(255, 235, 200))
make_hall_frame(sp_foxy_hall, 775, 520, 395).convert('RGB').save(os.path.join(cam_dir, 'office_hall_foxy.jpg'), quality=90)

sp_freddy_hall = style_sp('freddy', brightness=0.58, contrast=1.45, color=0.55, tint=(225, 220, 205))
make_hall_frame(sp_freddy_hall, 775, 535, 420).convert('RGB').save(os.path.join(cam_dir, 'office_hall_freddy.jpg'), quality=90)

sp_chica_hall = style_sp('chica', brightness=0.62, contrast=1.4, color=0.6, tint=(235, 230, 210))
make_hall_frame(sp_chica_hall, 775, 525, 390).convert('RGB').save(os.path.join(cam_dir, 'office_hall_chica.jpg'), quality=90)

sp_buff_hall = style_sp('buff', brightness=0.58, contrast=1.45, color=0.55, tint=(225, 220, 210))
make_hall_frame(sp_buff_hall, 775, 535, 430).convert('RGB').save(os.path.join(cam_dir, 'office_hall_buff.jpg'), quality=90)

# Both Foxy & Freddy in Hallway
layer_both = paste_char(off_flash, sp_foxy_hall, 705, 505, 350)
layer_both = paste_char(layer_both, sp_freddy_hall, 845, 530, 400)
Image.composite(layer_both, off_flash, desk_mask).convert('RGB').save(os.path.join(cam_dir, 'office_hall_foxy_freddy.jpg'), quality=90)

# Left Vent Blindspot Light (Left Vent opening is around x: 115..255, y: 390..605)
lvent_mask = Image.new('L', (1600, 720), 0)
ImageDraw.Draw(lvent_mask).polygon([(110, 385), (255, 395), (255, 610), (110, 610)], fill=255)
lvent_mask = lvent_mask.filter(ImageFilter.GaussianBlur(2))

sp_chica_lv = style_sp('chica', brightness=0.66, contrast=1.35, color=0.65, tint=(220, 230, 255), angle=8, crop_bottom=0.65)
lv_c = paste_char(off_lvent, sp_chica_lv, 185, 625, 270)
Image.composite(lv_c, off_lvent, lvent_mask).convert('RGB').save(os.path.join(cam_dir, 'office_left_chica.jpg'), quality=90)

sp_buff_lv = style_sp('buff', brightness=0.62, contrast=1.45, color=0.6, tint=(220, 230, 255), angle=6, crop_bottom=0.65)
lv_b = paste_char(off_lvent, sp_buff_lv, 185, 625, 280)
Image.composite(lv_b, off_lvent, lvent_mask).convert('RGB').save(os.path.join(cam_dir, 'office_left_buff.jpg'), quality=90)

# Right Vent Blindspot Light (Right Vent opening is around x: 1320..1465, y: 390..610)
rvent_mask = Image.new('L', (1600, 720), 0)
ImageDraw.Draw(rvent_mask).polygon([(1315, 395), (1470, 385), (1470, 610), (1315, 610)], fill=255)
rvent_mask = rvent_mask.filter(ImageFilter.GaussianBlur(2))

sp_bonnie_rv = style_sp('bonnie', brightness=0.66, contrast=1.4, color=0.65, tint=(215, 230, 255), angle=-8, crop_bottom=0.7)
rv_b = paste_char(off_rvent, sp_bonnie_rv, 1390, 625, 275)
Image.composite(rv_b, off_rvent, rvent_mask).convert('RGB').save(os.path.join(cam_dir, 'office_right_bonnie.jpg'), quality=90)

# Office Blackout Confrontations (Animatronic standing right in front of your desk requiring the Mask!)
for who in ['freddy', 'buff', 'bonnie', 'chica']:
    sp_in = style_sp(who, brightness=0.48, contrast=1.55, color=0.45, tint=(210, 215, 235))
    frame_in = paste_char(off_norm, sp_in, 810, 720, 680, shadow=0.75)
    frame_in.convert('RGB').save(os.path.join(cam_dir, f'office_inside_{who}.jpg'), quality=90)

# --- 2. FNAF 2 CAMERAS (CAM 01 to CAM 12) ---
# CAM 01 (Party Room 1)
c01 = load_bg('cam01_empty.png')
c01.convert('RGB').save(os.path.join(cam_dir, 'cam01_empty.jpg'), quality=90)
paste_char(c01, style_sp('chica', 0.56, 1.4, 0.55), 820, 720, 620).convert('RGB').save(os.path.join(cam_dir, 'cam01_chica.jpg'), quality=90)
paste_char(c01, style_sp('buff', 0.52, 1.45, 0.5), 760, 720, 650).convert('RGB').save(os.path.join(cam_dir, 'cam01_buff.jpg'), quality=90)

# CAM 02 (Party Room 2)
c02 = load_bg('cam02_empty.png')
c02.convert('RGB').save(os.path.join(cam_dir, 'cam02_empty.jpg'), quality=90)
paste_char(c02, style_sp('bonnie', 0.56, 1.4, 0.55), 920, 720, 600).convert('RGB').save(os.path.join(cam_dir, 'cam02_bonnie.jpg'), quality=90)

# CAM 03 (Party Room 3)
c03 = load_bg('cam03_empty.png')
c03.convert('RGB').save(os.path.join(cam_dir, 'cam03_empty.jpg'), quality=90)
paste_char(c03, style_sp('bonnie', 0.54, 1.4, 0.55), 780, 720, 610).convert('RGB').save(os.path.join(cam_dir, 'cam03_bonnie.jpg'), quality=90)
paste_char(c03, style_sp('buff', 0.50, 1.5, 0.45), 850, 735, 670).convert('RGB').save(os.path.join(cam_dir, 'cam03_buff.jpg'), quality=90)

# CAM 04 (Party Room 4)
c04 = load_bg('cam04_empty.png')
c04.convert('RGB').save(os.path.join(cam_dir, 'cam04_empty.jpg'), quality=90)
paste_char(c04, style_sp('bonnie', 0.58, 1.45, 0.55, angle=-4), 860, 745, 680).convert('RGB').save(os.path.join(cam_dir, 'cam04_bonnie.jpg'), quality=90)
paste_char(c04, style_sp('chica', 0.55, 1.4, 0.55), 760, 720, 610).convert('RGB').save(os.path.join(cam_dir, 'cam04_chica.jpg'), quality=90)

# CAM 05 (Left Air Vent)
c05 = load_bg('cam05_empty.png')
c05.convert('RGB').save(os.path.join(cam_dir, 'cam05_empty.jpg'), quality=90)
paste_char(c05, style_sp('chica', 0.56, 1.45, 0.5, crop_bottom=0.75), 800, 740, 660).convert('RGB').save(os.path.join(cam_dir, 'cam05_chica.jpg'), quality=90)
paste_char(c05, style_sp('buff', 0.54, 1.5, 0.45, crop_bottom=0.75), 800, 740, 680).convert('RGB').save(os.path.join(cam_dir, 'cam05_buff.jpg'), quality=90)

# CAM 06 (Right Air Vent)
c06 = load_bg('cam06_empty.png')
c06.convert('RGB').save(os.path.join(cam_dir, 'cam06_empty.jpg'), quality=90)
paste_char(c06, style_sp('bonnie', 0.58, 1.45, 0.5, crop_bottom=0.75), 800, 740, 670).convert('RGB').save(os.path.join(cam_dir, 'cam06_bonnie.jpg'), quality=90)

# CAM 07 (Main Hall)
c07 = load_bg('cam07_empty.png')
c07.convert('RGB').save(os.path.join(cam_dir, 'cam07_empty.jpg'), quality=90)
paste_char(c07, style_sp('chica', 0.52, 1.4, 0.5), 720, 710, 580).convert('RGB').save(os.path.join(cam_dir, 'cam07_chica.jpg'), quality=90)
paste_char(c07, style_sp('buff', 0.48, 1.5, 0.45), 820, 720, 620).convert('RGB').save(os.path.join(cam_dir, 'cam07_buff.jpg'), quality=90)

# CAM 08 (Parts / Service)
c08 = load_bg('cam08_empty.png')
c08.convert('RGB').save(os.path.join(cam_dir, 'cam08_empty.jpg'), quality=90)
c08_all = paste_char(c08, style_sp('buff', 0.44, 1.5, 0.45), 580, 720, 610)
c08_all = paste_char(c08_all, style_sp('foxy', 0.58, 1.4, 0.75), 1040, 720, 610)
c08_all.convert('RGB').save(os.path.join(cam_dir, 'cam08_all.jpg'), quality=90)
paste_char(c08, style_sp('buff', 0.48, 1.5, 0.45), 780, 720, 640).convert('RGB').save(os.path.join(cam_dir, 'cam08_buff.jpg'), quality=90)
paste_char(c08, style_sp('foxy', 0.62, 1.45, 0.8), 820, 720, 640).convert('RGB').save(os.path.join(cam_dir, 'cam08_foxy.jpg'), quality=90)

# CAM 09 (Show Stage)
c09 = load_bg('cam09_empty.png')
c09.convert('RGB').save(os.path.join(cam_dir, 'cam09_empty.jpg'), quality=90)
sp_b_st = style_sp('bonnie', 0.64, 1.35, 0.65)
sp_f_st = style_sp('freddy', 0.64, 1.35, 0.65)
sp_c_st = style_sp('chica',  0.66, 1.35, 0.65)

c09_all = paste_char(c09, sp_b_st, 520, 725, 610)
c09_all = paste_char(c09_all, sp_c_st, 1100, 725, 600)
c09_all = paste_char(c09_all, sp_f_st, 810, 735, 660)
c09_all.convert('RGB').save(os.path.join(cam_dir, 'cam09_all.jpg'), quality=90)

c09_nob = paste_char(c09, sp_c_st, 1100, 725, 600)
c09_nob = paste_char(c09_nob, sp_f_st, 810, 735, 660)
c09_nob.convert('RGB').save(os.path.join(cam_dir, 'cam09_nobonnie.jpg'), quality=90)

paste_char(c09, sp_f_st, 810, 735, 660).convert('RGB').save(os.path.join(cam_dir, 'cam09_freddy.jpg'), quality=90)

# CAM 10 (Game Area)
c10 = load_bg('cam10_empty.png')
c10.convert('RGB').save(os.path.join(cam_dir, 'cam10_empty.jpg'), quality=90)
paste_char(c10, style_sp('freddy', 0.54, 1.45, 0.55), 820, 725, 630).convert('RGB').save(os.path.join(cam_dir, 'cam10_freddy.jpg'), quality=90)

# CAM 11 (Prize Corner — The Puppet / Monchhichi Music Box!)
c11 = load_bg('cam11_empty.png')
# Stage 0: Monchhichi sleeping peacefully in the Prize Corner
paste_char(c11, style_sp('puppet', 0.65, 1.25, 0.75), 1060, 690, 360).convert('RGB').save(os.path.join(cam_dir, 'cam11_0.jpg'), quality=90)
# Stage 1: Music Box low — Monchhichi rising up larger!
paste_char(c11, style_sp('puppet', 0.68, 1.35, 0.75, angle=-4), 960, 720, 520).convert('RGB').save(os.path.join(cam_dir, 'cam11_1.jpg'), quality=90)
# Stage 2: Music Box almost empty — Monchhichi right up against the camera lens!
paste_char(c11, style_sp('puppet', 0.72, 1.5, 0.7, angle=5), 820, 760, 720).convert('RGB').save(os.path.join(cam_dir, 'cam11_2.jpg'), quality=90)
# Stage 3: Music Box empty — Monchhichi GONE from Prize Corner!
c11.convert('RGB').save(os.path.join(cam_dir, 'cam11_3.jpg'), quality=90)

# CAM 12 (Kids' Cove)
c12 = load_bg('cam12_empty.png')
c12.convert('RGB').save(os.path.join(cam_dir, 'cam12_empty.jpg'), quality=90)
paste_char(c12, style_sp('foxy', 0.64, 1.4, 0.8), 820, 720, 610).convert('RGB').save(os.path.join(cam_dir, 'cam12_foxy.jpg'), quality=90)

print('Generated all 42 Five Nights at Ashi 2 camera and office frames!')
