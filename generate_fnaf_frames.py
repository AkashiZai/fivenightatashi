import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

base_dir = r'C:\Users\pisit\.gemini\antigravity\scratch\fnaf-custom\assets'
bg_dir = os.path.join(base_dir, 'bg')
sp_dir = os.path.join(base_dir, 'sprites')
cam_dir = os.path.join(base_dir, 'cams')
os.makedirs(cam_dir, exist_ok=True)

sprites = {
    name: Image.open(os.path.join(sp_dir, f'{name}.png')).convert('RGBA')
    for name in ['freddy', 'bonnie', 'chica', 'foxy', 'golden']
}

# Exact pupil coordinates (left_x, right_x, eye_y) on the 720p sprites
PUPILS = {
    'freddy': (182, 245, 114),
    'bonnie': (124, 167, 98),
    'chica':  (158, 210, 118),
    'foxy':   (149, 202, 118),
    'golden': (180, 237, 117),
}

def load_bg(name):
    im = Image.open(os.path.join(bg_dir, name)).convert('RGBA')
    if im.size != (1600, 720):
        im = im.resize((1600, 720), Image.Resampling.LANCZOS)
    return im

def style_sprite(name, brightness=0.55, contrast=1.35, color=0.45, tint=(255, 255, 255), glowing_eyes=False, angle=0, crop_bottom=1.0):
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
    
    if glowing_eyes and name in PUPILS:
        lx, rx, ey = PUPILS[name]
        overlay = Image.new('RGBA', out.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for ex in (lx, rx):
            # Subtle dark iris + bright pinprick pupil glow
            draw.ellipse((ex-6, ey-4, ex+6, ey+4), fill=(5, 5, 10, 210))
            draw.ellipse((ex-2, ey-2, ex+2, ey+2), fill=(255, 255, 255, 255))
        overlay = overlay.filter(ImageFilter.GaussianBlur(0.4))
        out.alpha_composite(overlay)

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
        sh_a = alpha.point(lambda p: int(p * shadow))
        sh.putalpha(sh_a)
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        res.alpha_composite(sh, (x + 8, y + 6))
        
    res.alpha_composite(sp_resized, (x, y))
    return res

# --- Clean CAM 1A Empty Stage ---
cam1a_empty = load_bg('cam1a_empty.png')
draw1a = ImageDraw.Draw(cam1a_empty)
# Completely cover the old eyes on left (x:100..450, y:50..360) with exact background color (1, 13, 17)
draw1a.rectangle([80, 40, 440, 360], fill=(1, 13, 17, 255))
for cx in range(440, 1400, 75):
    draw1a.rectangle([cx, 0, cx+35, 720], fill=(18, 6, 10, 55))
cam1a_empty.convert('RGB').save(os.path.join(cam_dir, 'cam1a_empty.jpg'), quality=90)

# CAM 1A combinations
sp_b_stage = style_sprite('bonnie', brightness=0.62, contrast=1.35, color=0.55, tint=(210, 225, 255))
sp_f_stage = style_sprite('freddy', brightness=0.68, contrast=1.35, color=0.55, tint=(255, 225, 195))
sp_c_stage = style_sprite('chica', brightness=0.64, contrast=1.35, color=0.55, tint=(255, 240, 190))
sp_f_stare = style_sprite('freddy', brightness=0.55, contrast=1.55, color=0.35, tint=(200, 220, 255), glowing_eyes=True, angle=-4)

c1a_all = paste_char(cam1a_empty, sp_b_stage, 540, 735, 620)
c1a_all = paste_char(c1a_all, sp_c_stage, 1140, 735, 610)
c1a_all = paste_char(c1a_all, sp_f_stage, 850, 745, 675)
c1a_all.convert('RGB').save(os.path.join(cam_dir, 'cam1a_all.jpg'), quality=90)

c1a_nob = paste_char(cam1a_empty, sp_c_stage, 1140, 735, 610)
c1a_nob = paste_char(c1a_nob, sp_f_stage, 850, 745, 675)
c1a_nob.convert('RGB').save(os.path.join(cam_dir, 'cam1a_nobonnie.jpg'), quality=90)

c1a_noc = paste_char(cam1a_empty, sp_b_stage, 540, 735, 620)
c1a_noc = paste_char(c1a_noc, sp_f_stage, 850, 745, 675)
c1a_noc.convert('RGB').save(os.path.join(cam_dir, 'cam1a_nochica.jpg'), quality=90)

c1a_f = paste_char(cam1a_empty, sp_f_stage, 850, 745, 675)
c1a_f.convert('RGB').save(os.path.join(cam_dir, 'cam1a_freddy.jpg'), quality=90)

c1a_fs = paste_char(cam1a_empty, sp_f_stare, 950, 780, 790)
c1a_fs.convert('RGB').save(os.path.join(cam_dir, 'cam1a_freddy_stare.jpg'), quality=90)

# --- CAM 1B (Dining Area) ---
cam1b_empty = load_bg('cam1b_empty.png')
cam1b_empty.convert('RGB').save(os.path.join(cam_dir, 'cam1b_empty.jpg'), quality=90)

sp_b_1b1 = style_sprite('bonnie', brightness=0.38, contrast=1.4, color=0.35, tint=(180, 195, 255), glowing_eyes=True)
sp_b_1b2 = style_sprite('bonnie', brightness=0.48, contrast=1.45, color=0.4, tint=(195, 210, 255), glowing_eyes=True, angle=3)
paste_char(cam1b_empty, sp_b_1b1, 470, 560, 390).convert('RGB').save(os.path.join(cam_dir, 'cam1b_bonnie1.jpg'), quality=90)
paste_char(cam1b_empty, sp_b_1b2, 340, 710, 580).convert('RGB').save(os.path.join(cam_dir, 'cam1b_bonnie2.jpg'), quality=90)

sp_c_1b1 = style_sprite('chica', brightness=0.40, contrast=1.4, color=0.35, tint=(220, 215, 185), glowing_eyes=True)
sp_c_1b2 = style_sprite('chica', brightness=0.50, contrast=1.45, color=0.4, tint=(230, 225, 195), glowing_eyes=True, angle=-3)
paste_char(cam1b_empty, sp_c_1b1, 1020, 575, 410).convert('RGB').save(os.path.join(cam_dir, 'cam1b_chica1.jpg'), quality=90)
paste_char(cam1b_empty, sp_c_1b2, 1130, 715, 590).convert('RGB').save(os.path.join(cam_dir, 'cam1b_chica2.jpg'), quality=90)

sp_f_1b = style_sprite('freddy', brightness=0.18, contrast=1.8, color=0.15, tint=(180, 200, 255), glowing_eyes=True)
paste_char(cam1b_empty, sp_f_1b, 790, 480, 310).convert('RGB').save(os.path.join(cam_dir, 'cam1b_freddy.jpg'), quality=90)

# --- CAM 1C (Pirate Cove - Foxy) ---
cam1c_closed = load_bg('cam1c_closed.png')
cam1c_open = load_bg('cam1c_open.png')
cam1c_closed.convert('RGB').save(os.path.join(cam_dir, 'cam1c_0.jpg'), quality=90)

sp_foxy_peek = style_sprite('foxy', brightness=0.45, contrast=1.5, color=0.5, tint=(220, 190, 240), glowing_eyes=True)
c1c_1 = cam1c_closed.copy()
c1c_1 = paste_char(c1c_1, sp_foxy_peek, 1005, 670, 520, shadow=0.3)
right_curtain = cam1c_closed.crop((1032, 0, 1450, 720))
c1c_1.paste(right_curtain, (1032, 0))
c1c_1.convert('RGB').save(os.path.join(cam_dir, 'cam1c_1.jpg'), quality=90)

sp_foxy_out = style_sprite('foxy', brightness=0.58, contrast=1.45, color=0.6, tint=(230, 210, 255), glowing_eyes=True, angle=-4)
c1c_2 = paste_char(cam1c_closed, sp_foxy_out, 860, 735, 660)
c1c_2.convert('RGB').save(os.path.join(cam_dir, 'cam1c_2.jpg'), quality=90)

cam1c_open.convert('RGB').save(os.path.join(cam_dir, 'cam1c_3.jpg'), quality=90)

# --- CAM 2A (West Hall) ---
cam2a_empty = load_bg('cam2a_empty.png')
cam2a_empty.convert('RGB').save(os.path.join(cam_dir, 'cam2a_empty.jpg'), quality=90)

sp_b_2a = style_sprite('bonnie', brightness=0.36, contrast=1.55, color=0.35, tint=(200, 210, 255), glowing_eyes=True)
paste_char(cam2a_empty, sp_b_2a, 960, 680, 540).convert('RGB').save(os.path.join(cam_dir, 'cam2a_bonnie.jpg'), quality=90)

sp_fx_run = style_sprite('foxy', brightness=0.62, contrast=1.45, color=0.65, glowing_eyes=True, angle=6)
paste_char(cam2a_empty, sp_fx_run, 980, 560, 380).convert('RGB').save(os.path.join(cam_dir, 'cam2a_foxy_run1.jpg'), quality=90)
sp_fx_run2 = style_sprite('foxy', brightness=0.70, contrast=1.45, color=0.70, glowing_eyes=True, angle=-6)
paste_char(cam2a_empty, sp_fx_run2, 930, 690, 580).convert('RGB').save(os.path.join(cam_dir, 'cam2a_foxy_run2.jpg'), quality=90)
sp_fx_run3 = style_sprite('foxy', brightness=0.78, contrast=1.5, color=0.75, glowing_eyes=True, angle=5)
paste_char(cam2a_empty, sp_fx_run3, 860, 820, 820).convert('RGB').save(os.path.join(cam_dir, 'cam2a_foxy_run3.jpg'), quality=90)

# --- CAM 2B (West Hall Corner) ---
cam2b_empty = load_bg('cam2b_empty.png')
cam2b_empty.convert('RGB').save(os.path.join(cam_dir, 'cam2b_empty.jpg'), quality=90)

sp_b_2b = style_sprite('bonnie', brightness=0.62, contrast=1.45, color=0.5, tint=(185, 215, 255), glowing_eyes=False, crop_bottom=0.75)
paste_char(cam2b_empty, sp_b_2b, 920, 760, 740).convert('RGB').save(os.path.join(cam_dir, 'cam2b_bonnie.jpg'), quality=90)

sp_b_2b_tw = style_sprite('bonnie', brightness=0.68, contrast=1.65, color=0.3, tint=(255, 190, 220), glowing_eyes=True, angle=-8, crop_bottom=0.72)
paste_char(cam2b_empty, sp_b_2b_tw, 930, 775, 760).convert('RGB').save(os.path.join(cam_dir, 'cam2b_bonnie_twitch.jpg'), quality=90)

c2b_gold = cam2b_empty.copy()
sp_gold_poster = style_sprite('golden', brightness=0.75, contrast=1.55, color=0.65, tint=(255, 215, 90), glowing_eyes=True, crop_bottom=0.65)
c2b_gold = paste_char(c2b_gold, sp_gold_poster, 625, 495, 380, shadow=0.4)
draw_g = ImageDraw.Draw(c2b_gold)
draw_g.text((820, 180), "IT'S ME", fill=(220, 30, 30, 210))
c2b_gold.convert('RGB').save(os.path.join(cam_dir, 'cam2b_golden.jpg'), quality=90)

# --- CAM 3 (Supply Closet) ---
cam3_empty = load_bg('cam3_empty.png')
cam3_empty.convert('RGB').save(os.path.join(cam_dir, 'cam3_empty.jpg'), quality=90)

sp_b_3 = style_sprite('bonnie', brightness=0.66, contrast=1.4, color=0.55, tint=(255, 235, 185), glowing_eyes=True, angle=-5, crop_bottom=0.8)
paste_char(cam3_empty, sp_b_3, 920, 750, 720).convert('RGB').save(os.path.join(cam_dir, 'cam3_bonnie.jpg'), quality=90)

# --- CAM 4A (East Hall) ---
cam4a_empty = load_bg('cam4a_empty.png')
cam4a_empty.convert('RGB').save(os.path.join(cam_dir, 'cam4a_empty.jpg'), quality=90)

sp_c_4a1 = style_sprite('chica', brightness=0.48, contrast=1.4, color=0.45, tint=(195, 215, 255), glowing_eyes=True)
sp_c_4a2 = style_sprite('chica', brightness=0.62, contrast=1.45, color=0.5, tint=(205, 225, 255), angle=3)
paste_char(cam4a_empty, sp_c_4a1, 740, 620, 450).convert('RGB').save(os.path.join(cam_dir, 'cam4a_chica1.jpg'), quality=90)
paste_char(cam4a_empty, sp_c_4a2, 690, 740, 680).convert('RGB').save(os.path.join(cam_dir, 'cam4a_chica2.jpg'), quality=90)

sp_f_4a = style_sprite('freddy', brightness=0.35, contrast=1.6, color=0.3, tint=(180, 205, 255), glowing_eyes=True)
paste_char(cam4a_empty, sp_f_4a, 720, 710, 620).convert('RGB').save(os.path.join(cam_dir, 'cam4a_freddy.jpg'), quality=90)

# --- CAM 4B (East Hall Corner) ---
cam4b_empty = load_bg('cam4b_empty.png')
cam4b_empty.convert('RGB').save(os.path.join(cam_dir, 'cam4b_empty.jpg'), quality=90)

sp_c_4b = style_sprite('chica', brightness=0.62, contrast=1.45, color=0.55, tint=(185, 215, 255), crop_bottom=0.82)
paste_char(cam4b_empty, sp_c_4b, 860, 755, 730).convert('RGB').save(os.path.join(cam_dir, 'cam4b_chica.jpg'), quality=90)

sp_c_4b_tw = style_sprite('golden', brightness=0.66, contrast=1.55, color=0.6, tint=(200, 220, 255), glowing_eyes=True, angle=7, crop_bottom=0.85)
paste_char(cam4b_empty, sp_c_4b_tw, 870, 765, 750).convert('RGB').save(os.path.join(cam_dir, 'cam4b_chica_twitch.jpg'), quality=90)

sp_f_4b = style_sprite('freddy', brightness=0.45, contrast=1.6, color=0.35, tint=(175, 205, 255), glowing_eyes=True, angle=-3, crop_bottom=0.72)
paste_char(cam4b_empty, sp_f_4b, 880, 765, 760).convert('RGB').save(os.path.join(cam_dir, 'cam4b_freddy.jpg'), quality=90)

# --- CAM 5 (Backstage) ---
cam5_empty = load_bg('cam5_empty.png')
cam5_empty.convert('RGB').save(os.path.join(cam_dir, 'cam5_empty.jpg'), quality=90)

sp_b_5 = style_sprite('bonnie', brightness=0.52, contrast=1.4, color=0.45, tint=(200, 210, 230))
paste_char(cam5_empty, sp_b_5, 830, 725, 610).convert('RGB').save(os.path.join(cam_dir, 'cam5_bonnie1.jpg'), quality=90)

sp_b_5_close = style_sprite('bonnie', brightness=0.58, contrast=1.65, color=0.3, tint=(210, 220, 245), glowing_eyes=True, crop_bottom=0.58)
paste_char(cam5_empty, sp_b_5_close, 820, 790, 830).convert('RGB').save(os.path.join(cam_dir, 'cam5_bonnie_close.jpg'), quality=90)

# --- CAM 7 (Restrooms) ---
cam7_empty = load_bg('cam7_empty.png')
cam7_empty.convert('RGB').save(os.path.join(cam_dir, 'cam7_empty.jpg'), quality=90)

sp_c_7_1 = style_sprite('chica', brightness=0.44, contrast=1.45, color=0.4, tint=(195, 215, 235), glowing_eyes=True)
sp_c_7_2 = style_sprite('chica', brightness=0.56, contrast=1.45, color=0.5, tint=(205, 220, 240), angle=-4)
paste_char(cam7_empty, sp_c_7_1, 960, 620, 480).convert('RGB').save(os.path.join(cam_dir, 'cam7_chica1.jpg'), quality=90)
paste_char(cam7_empty, sp_c_7_2, 830, 740, 680).convert('RGB').save(os.path.join(cam_dir, 'cam7_chica2.jpg'), quality=90)

sp_f_7 = style_sprite('freddy', brightness=0.22, contrast=1.8, color=0.2, tint=(180, 200, 240), glowing_eyes=True, angle=8)
paste_char(cam7_empty, sp_f_7, 360, 620, 470).convert('RGB').save(os.path.join(cam_dir, 'cam7_freddy.jpg'), quality=90)

# --- THE OFFICE STATES ---
off_norm = load_bg('office_normal.png')
off_ll = load_bg('office_left_light.png')
off_rl = load_bg('office_right_light.png')
off_dark = load_bg('office_304.png')

off_norm.convert('RGB').save(os.path.join(cam_dir, 'office_normal.jpg'), quality=92)
off_ll.convert('RGB').save(os.path.join(cam_dir, 'office_left_empty.jpg'), quality=92)
off_rl.convert('RGB').save(os.path.join(cam_dir, 'office_right_empty.jpg'), quality=92)
off_dark.convert('RGB').save(os.path.join(cam_dir, 'office_dark.jpg'), quality=92)

# Bonnie at Left Doorway when Left Hall Light is ON (clipped to left doorway polygon + casting shadow in left window)
off_l_bonnie = off_ll.copy()
sp_b_door = style_sprite('bonnie', brightness=0.55, contrast=1.4, color=0.55, tint=(195, 215, 250))
door_layer = off_ll.copy()
door_layer = paste_char(door_layer, sp_b_door, 165, 720, 610)
mask_door = Image.new('L', (1600, 720), 0)
draw_d = ImageDraw.Draw(mask_door)
draw_d.polygon([(82, 55), (242, 145), (242, 720), (82, 720)], fill=255)
mask_door = mask_door.filter(ImageFilter.GaussianBlur(1.5))
off_l_bonnie = Image.composite(door_layer, off_ll, mask_door)
off_l_bonnie.convert('RGB').save(os.path.join(cam_dir, 'office_left_bonnie.jpg'), quality=92)

# Chica at Right Window when Right Hall Light is ON (showing both Chica face and Pizza Box inside the right window!)
off_r_chica = off_rl.copy()
sp_c_win = style_sprite('chica', brightness=0.56, contrast=1.45, color=0.55, tint=(195, 215, 245), crop_bottom=1.0)
win_layer = off_rl.copy()
win_layer = paste_char(win_layer, sp_c_win, 1180, 520, 315)
mask_win = Image.new('L', (1600, 720), 0)
draw_w = ImageDraw.Draw(mask_win)
draw_w.polygon([(1124, 232), (1232, 182), (1232, 522), (1124, 482)], fill=220)
mask_win = mask_win.filter(ImageFilter.GaussianBlur(2))
off_r_chica = Image.composite(win_layer, off_rl, mask_win)
off_r_chica.convert('RGB').save(os.path.join(cam_dir, 'office_right_chica.jpg'), quality=92)

# Power Outage Freddy flickering in Left Doorway (x=165)
off_dark_freddy = off_dark.copy()
sp_f_dark = style_sprite('freddy', brightness=0.35, contrast=1.7, color=0.3, tint=(200, 225, 255), glowing_eyes=True)
dark_layer = paste_char(off_dark, sp_f_dark, 165, 680, 570)
off_dark_freddy = Image.composite(dark_layer, off_dark, mask_door)
off_dark_freddy.convert('RGB').save(os.path.join(cam_dir, 'office_dark_freddy.jpg'), quality=92)

print('Updated all 35 custom FNaF 1 camera and office frames!')
