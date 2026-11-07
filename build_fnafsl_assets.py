import os, urllib.request
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageSequence

ROOT = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(ROOT, 'assets5', 'bg')
SPRITE_DIR = os.path.join(ROOT, 'assets5', 'sprites')
CAM_DIR = os.path.join(ROOT, 'assets5', 'cams')

os.makedirs(BG_DIR, exist_ok=True)
os.makedirs(SPRITE_DIR, exist_ok=True)
os.makedirs(CAM_DIR, exist_ok=True)

WIKI_URLS = {
    'elevator.png':        'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/7/7e/1231.png/revision/latest?cb=20161205052742',
    'elevator_open.gif':   'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/3/3b/OpenElevator.gif/revision/latest?cb=20170124214143',
    'control_module.png':  'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/e/e6/1232.png/revision/latest?cb=20161205052804',
    'ballora_stage_v2.gif':'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/a/a2/Ballora_on_Stage.gif/revision/latest?cb=20161103222116',
    'ballora_dead.png':    'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/5/5d/BalloraGalleryDeadMan.png/revision/latest?cb=20161024151540',
    'foxy_stage.gif':      'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/7/77/FNAFSL_Funtime_Foxy_Onstage.gif/revision/latest?cb=20161011210504',
    'circus_control.png':  'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/c/cc/CircusControl.png/revision/latest?cb=20200308123702',
    'breaker_room.jpg':    'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/3/3c/Breaker_Room.jpg/revision/latest?cb=20240703100723',
    'scooping_real.gif':   'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/1/16/Scooping_Room-Sister_Location.gif/revision/latest?cb=20170124214207',
    'vlad_clara.png':      'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/e/e6/Vlad-and-Clara-concept1.png/revision/latest?cb=20180706124618',
    'butters_trophy.png':  'https://static.wikia.nocookie.net/freddy-fazbears-pizza/images/6/68/ExoticButters-Trophy.png/revision/latest?cb=20210510125753',
}

print("1. Downloading authentic FNaF Sister Location room & cutscene textures...")
for fname, url in WIKI_URLS.items():
    out_p = os.path.join(BG_DIR, fname)
    if not os.path.exists(out_p):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(out_p, 'wb') as f:
            f.write(resp.read())
        print("  Downloaded", fname)

# 2. Build the 8 Funtime / Sister Location Ashi Sprites with clean faceplate seams & cheek blush aligned to Ashi's head
def make_funtime_sprite(src_path, out_name, accent_rgb=(235, 50, 65), porcelain_mix=0.28, wire_mode=False):
    im = Image.open(src_path).convert('RGBA').resize((520, 650), Image.Resampling.LANCZOS)
    a = np.array(im, dtype=np.float32)
    alpha = a[:,:,3]
    rgb = a[:,:,:3]
    lum = 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]

    h_i, w_i = lum.shape
    yy, xx = np.mgrid[0:h_i, 0:w_i]

    # Detect head center from top 42% of non-transparent pixels
    head_region = (alpha[:int(h_i * 0.42), :] > 60)
    ys, xs = np.where(head_region)
    if len(xs) > 20:
        hx_min, hx_max = int(np.percentile(xs, 12)), int(np.percentile(xs, 88))
        hy_min, hy_max = int(np.percentile(ys, 8)), int(np.percentile(ys, 92))
    else:
        hx_min, hx_max = 175, 345
        hy_min, hy_max = 45, 240
    cx = (hx_min + hx_max) // 2
    cy = hy_min + int((hy_max - hy_min) * 0.56)
    hw = max(40, (hx_max - hx_min) // 2)

    out = np.zeros_like(a)
    if wire_mode:
        # ENNARD ASHI: Metallic silver endoskeleton + Springtrap-Ashi face intact
        edge = np.abs(np.gradient(lum)[0]) + np.abs(np.gradient(lum)[1])
        silver = np.clip(lum * 0.88 + edge * 1.35, 0, 255)
        out[:,:,0] = np.clip(rgb[:,:,0] * 0.45 + silver * 0.55, 0, 255)
        out[:,:,1] = np.clip(rgb[:,:,1] * 0.42 + silver * 0.52, 0, 255)
        out[:,:,2] = np.clip(rgb[:,:,2] * 0.45 + silver * 0.60, 0, 255)
        out[:,:,3] = alpha
    else:
        porcelain = np.clip(lum * 1.12 + 24.0, 0, 255)
        out[:,:,0] = np.clip(rgb[:,:,0] * (1 - porcelain_mix) + (porcelain * 0.72 + accent_rgb[0] * 0.28) * porcelain_mix, 0, 255)
        out[:,:,1] = np.clip(rgb[:,:,1] * (1 - porcelain_mix) + (porcelain * 0.72 + accent_rgb[1] * 0.28) * porcelain_mix, 0, 255)
        out[:,:,2] = np.clip(rgb[:,:,2] * (1 - porcelain_mix) + (porcelain * 0.72 + accent_rgb[2] * 0.28) * porcelain_mix, 0, 255)
        out[:,:,3] = alpha

    res = Image.fromarray(out.astype(np.uint8), mode='RGBA')
    overlay = Image.new('RGBA', (w_i, h_i), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Subtle Sister Location faceplate cross-seams strictly within the head bounds
    draw.line([(cx, hy_min + 10), (cx, hy_max - 5)], fill=(20, 20, 26, 155), width=3)
    draw.line([(cx - int(hw * 0.82), cy), (cx + int(hw * 0.82), cy)], fill=(20, 20, 26, 155), width=3)

    if wire_mode:
        # Red clown nose & party hat for Ennard Ashi
        draw.ellipse([cx - 16, cy - 12, cx + 16, cy + 18], fill=(220, 20, 25, 230), outline=(90, 0, 0, 255), width=2)
        draw.polygon([(cx, max(4, hy_min - 45)), (cx - 42, hy_min + 22), (cx + 42, hy_min + 22)], fill=(195, 170, 35, 230), outline=(45, 130, 45, 255))
    else:
        # Cute glossy Funtime rosy cheeks on left & right cheeks
        r_c, g_c, b_c = accent_rgb
        cr = max(14, int(hw * 0.22))
        lx, rx = cx - int(hw * 0.52), cx + int(hw * 0.52)
        chy = cy + int((hy_max - cy) * 0.22)
        draw.ellipse([lx - cr, chy - cr, lx + cr, chy + cr], fill=(r_c, g_c, b_c, 165))
        draw.ellipse([rx - cr, chy - cr, rx + cr, chy + cr], fill=(r_c, g_c, b_c, 165))

    # Mask overlay by sprite alpha so nothing ever floats outside the character!
    ov_arr = np.array(overlay, dtype=np.float32)
    ov_arr[:,:,3] = ov_arr[:,:,3] * (alpha / 255.0)
    res.alpha_composite(Image.fromarray(ov_arr.astype(np.uint8), mode='RGBA'))

    res = ImageEnhance.Contrast(res).enhance(1.22)
    res.save(os.path.join(SPRITE_DIR, out_name))
    print("  Created Sister Location sprite:", out_name)

make_funtime_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'chica.png'),      'baby.png',           accent_rgb=(235, 35, 45),  porcelain_mix=0.28)
make_funtime_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'bonnie.png'),     'ballora.png',        accent_rgb=(145, 55, 235), porcelain_mix=0.30)
make_funtime_sprite(os.path.join(ROOT, 'assets',  'sprites', 'freddy.png'),     'funtime_freddy.png', accent_rgb=(235, 75, 195), porcelain_mix=0.28)
make_funtime_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'puppet.png'),     'bonbon.png',         accent_rgb=(45, 125, 245), porcelain_mix=0.25)
make_funtime_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'foxy.png'),       'funtime_foxy.png',   accent_rgb=(245, 65, 155), porcelain_mix=0.26)
make_funtime_sprite(os.path.join(ROOT, 'assets3', 'sprites', 'springtrap.png'), 'ennard.png',         wire_mode=True)
make_funtime_sprite(os.path.join(ROOT, 'assets',  'sprites', 'bonnie.png'),     'bidybab.png',        accent_rgb=(210, 140, 120),porcelain_mix=0.32)
make_funtime_sprite(os.path.join(ROOT, 'assets2', 'sprites', 'buff.png'),       'minireena.png',      accent_rgb=(230, 210, 150),porcelain_mix=0.32)

def load_bg_rgb(fname, size=(1024, 576), frame_idx='mid'):
    p = os.path.join(BG_DIR, fname)
    im = Image.open(p)
    if fname.endswith('.gif'):
        frames = [f.copy().convert('RGB') for f in ImageSequence.Iterator(im)]
        idx = 0 if frame_idx == 'first' else (len(frames) - 1 if frame_idx == 'last' else len(frames) // 2)
        im = frames[idx]
    else:
        im = im.convert('RGB')
    return im.resize(size, Image.Resampling.LANCZOS)

def paste_sl(bg, sprite_name, scale_h, center_x, bottom_y, brightness=0.88, contrast=1.25, crop_bottom=1.0, flip_x=False):
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

print("3. Compositing all 41 Sister Location Story, Cutscene & Gameplay frames...")

# 1. Opening Prologue Blueprint (Mr. Afton Interview)
bp = Image.new('RGB', (1024, 576), (6, 18, 42))
draw_bp = ImageDraw.Draw(bp)
for gx in range(0, 1024, 32):
    draw_bp.line([(gx, 0), (gx, 576)], fill=(14, 42, 88), width=1)
for gy in range(0, 576, 32):
    draw_bp.line([(0, gy), (1024, gy)], fill=(14, 42, 88), width=1)
bp_baby = paste_sl(bp, 'baby.png', scale_h=510, center_x=512, bottom_y=555, brightness=0.92, contrast=1.30)
draw_bp2 = ImageDraw.Draw(bp_baby)
draw_bp2.rectangle([30, 26, 994, 550], outline=(80, 180, 255), width=2)
draw_bp2.text((52, 44), "AFTON ROBOTICS, LLC // BLUEPRINT: CIRCUS BABY ASHI (REV 4.2)", fill=(120, 210, 255))
draw_bp2.text((52, 180), "[A] INTERNAL HELIUM TANK (FINGERTIP INFLATION)", fill=(100, 195, 255))
draw_bp2.text((52, 310), "[B] INTERNAL ICE CREAM DISPENSER + STORAGE CAVITY", fill=(100, 195, 255))
draw_bp2.text((52, 440), "[C] SONG REQUEST VOICE SYNTHESIZER MODULE", fill=(100, 195, 255))
bp_baby.save(os.path.join(CAM_DIR, 'prologue_blueprint.jpg'), quality=90)

# 2. Elevator & Entryway Vent
load_bg_rgb('elevator.png').save(os.path.join(CAM_DIR, 'elevator_descent.jpg'), quality=90)
load_bg_rgb('elevator_open.gif').save(os.path.join(CAM_DIR, 'elevator_open.jpg'), quality=90)

vent = Image.new('RGB', (1024, 576), (14, 16, 22))
d_v = ImageDraw.Draw(vent)
for step in range(1, 9):
    pad_x, pad_y = step * 52, step * 30
    c_val = 22 + step * 8
    d_v.rectangle([pad_x, pad_y, 1024 - pad_x, 576 - pad_y], outline=(c_val, c_val + 4, c_val + 12), width=4)
vent.save(os.path.join(CAM_DIR, 'vent_crawl.jpg'), quality=90)

# 3. Primary Control Module & Ballora / Funtime Foxy Windows
load_bg_rgb('control_module.png').save(os.path.join(CAM_DIR, 'control_module.jpg'), quality=90)

bal_bg = load_bg_rgb('ballora_stage_v2.gif', frame_idx='first')
ImageEnhance.Brightness(bal_bg).enhance(0.16).save(os.path.join(CAM_DIR, 'ballora_window_dark.jpg'), quality=90)
ImageEnhance.Brightness(bal_bg).enhance(0.65).save(os.path.join(CAM_DIR, 'ballora_window_empty.jpg'), quality=90)

bal_stage = paste_sl(bal_bg, 'ballora.png', scale_h=390, center_x=512, bottom_y=495, brightness=0.88)
bal_stage = paste_sl(bal_stage, 'minireena.png', scale_h=200, center_x=310, bottom_y=505, brightness=0.84)
bal_stage = paste_sl(bal_stage, 'minireena.png', scale_h=200, center_x=715, bottom_y=505, brightness=0.84, flip_x=True)
bal_stage.save(os.path.join(CAM_DIR, 'ballora_window_stage.jpg'), quality=90)

bal_dead = load_bg_rgb('ballora_dead.png')
bal_dead.save(os.path.join(CAM_DIR, 'ballora_window_tech.jpg'), quality=90)

fox_bg = load_bg_rgb('foxy_stage.gif')
ImageEnhance.Brightness(fox_bg).enhance(0.14).save(os.path.join(CAM_DIR, 'foxy_window_dark.jpg'), quality=90)
ImageEnhance.Brightness(fox_bg).enhance(0.65).save(os.path.join(CAM_DIR, 'foxy_window_empty.jpg'), quality=90)

fox_stage = paste_sl(fox_bg, 'funtime_foxy.png', scale_h=390, center_x=512, bottom_y=495, brightness=0.90)
fox_stage.save(os.path.join(CAM_DIR, 'foxy_window_stage.jpg'), quality=90)
ImageEnhance.Color(bal_dead).enhance(0.6).transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(os.path.join(CAM_DIR, 'foxy_window_tech.jpg'), quality=90)

# 4. Circus Gallery Control Module & Under-the-Desk Bidybab Encounter (Night 2)
circ = load_bg_rgb('circus_control.png')
circ.save(os.path.join(CAM_DIR, 'circus_control.jpg'), quality=90)
circ_lit = paste_sl(ImageEnhance.Brightness(circ).enhance(1.35), 'baby.png', scale_h=310, center_x=512, bottom_y=395, brightness=0.68, crop_bottom=0.75)
circ_lit.save(os.path.join(CAM_DIR, 'circus_control_lit.jpg'), quality=90)

def make_desk_view(gap_px=0, bidy_count=0):
    base = Image.new('RGB', (1024, 576), (8, 9, 14))
    if bidy_count >= 1:
        base = paste_sl(base, 'bidybab.png', scale_h=360, center_x=430, bottom_y=540, brightness=0.82)
    if bidy_count >= 2:
        base = paste_sl(base, 'bidybab.png', scale_h=340, center_x=640, bottom_y=550, brightness=0.84, flip_x=True)
    metal = Image.new('RGBA', (1024, 576), (0, 0, 0, 0))
    dm = ImageDraw.Draw(metal)
    shield_end = max(220, 1024 - gap_px)
    dm.rectangle([0, 0, shield_end, 576], fill=(44, 48, 56, 248), outline=(95, 102, 115, 255), width=6)
    for r_y in range(90, 500, 78):
        for r_x in range(80, shield_end - 50, 82):
            dm.ellipse([r_x - 22, r_y - 22, r_x + 22, r_y + 22], fill=(10, 12, 18, 195), outline=(28, 32, 40, 255), width=2)
    out = base.convert('RGBA')
    out.alpha_composite(metal)
    return out.convert('RGB')

make_desk_view(gap_px=0, bidy_count=0).save(os.path.join(CAM_DIR, 'desk_hide_closed.jpg'), quality=90)
make_desk_view(gap_px=210, bidy_count=1).save(os.path.join(CAM_DIR, 'desk_hide_bidybab_1.jpg'), quality=90)
make_desk_view(gap_px=420, bidy_count=2).save(os.path.join(CAM_DIR, 'desk_hide_bidybab_2.jpg'), quality=90)

# 5. Ballora Gallery Crawl & Breaker Room (Night 2)
ImageEnhance.Brightness(bal_bg).enhance(0.18).save(os.path.join(CAM_DIR, 'ballora_crawl_dark.jpg'), quality=90)
paste_sl(ImageEnhance.Brightness(bal_bg).enhance(0.42), 'ballora.png', scale_h=520, center_x=512, bottom_y=570, brightness=0.88).save(os.path.join(CAM_DIR, 'ballora_crawl_near.jpg'), quality=90)

brk = load_bg_rgb('breaker_room.jpg')
brk.save(os.path.join(CAM_DIR, 'breaker_empty.jpg'), quality=90)
paste_sl(brk, 'funtime_freddy.png', scale_h=330, center_x=540, bottom_y=450, brightness=0.58, crop_bottom=0.80).save(os.path.join(CAM_DIR, 'breaker_freddy_far.jpg'), quality=90)
brk_close = paste_sl(brk, 'funtime_freddy.png', scale_h=530, center_x=490, bottom_y=576, brightness=0.88)
brk_close = paste_sl(brk_close, 'bonbon.png', scale_h=240, center_x=685, bottom_y=520, brightness=0.92)
brk_close.save(os.path.join(CAM_DIR, 'breaker_freddy_close.jpg'), quality=90)

# 6. Funtime Auditorium Flash Beacon & Parts and Service (Night 3 & Night 5)
Image.new('RGB', (1024, 576), (3, 3, 6)).save(os.path.join(CAM_DIR, 'auditorium_dark.jpg'), quality=90)
aud_lit = ImageEnhance.Brightness(fox_bg).enhance(0.55)
aud_lit.save(os.path.join(CAM_DIR, 'auditorium_flash_clear.jpg'), quality=90)
paste_sl(aud_lit, 'funtime_foxy.png', scale_h=310, center_x=512, bottom_y=440, brightness=0.80).save(os.path.join(CAM_DIR, 'auditorium_flash_foxy_far.jpg'), quality=90)
paste_sl(aud_lit, 'funtime_foxy.png', scale_h=550, center_x=512, bottom_y=576, brightness=0.94).save(os.path.join(CAM_DIR, 'auditorium_flash_foxy_close.jpg'), quality=90)

ps_base = Image.new('RGB', (1024, 576), (8, 10, 16))
dps = ImageDraw.Draw(ps_base)
dps.ellipse([180, 40, 844, 560], fill=(22, 26, 38))

ps_fred_closed = paste_sl(ps_base, 'funtime_freddy.png', scale_h=540, center_x=490, bottom_y=576, brightness=0.92)
ps_fred_closed = paste_sl(ps_fred_closed, 'bonbon.png', scale_h=250, center_x=710, bottom_y=535, brightness=0.94)
ps_fred_closed.save(os.path.join(CAM_DIR, 'parts_freddy_closed.jpg'), quality=90)

ps_fred_open = ps_fred_closed.copy()
d_fo = ImageDraw.Draw(ps_fred_open)
d_fo.rectangle([440, 390, 540, 500], fill=(18, 20, 26), outline=(140, 150, 170), width=4)
d_fo.ellipse([462, 415, 518, 471], fill=(255, 45, 65), outline=(255, 210, 210), width=3)
ps_fred_open.save(os.path.join(CAM_DIR, 'parts_freddy_open.jpg'), quality=90)

ps_baby = paste_sl(ps_base, 'ennard.png', scale_h=420, center_x=320, bottom_y=470, brightness=0.42)
ps_baby = paste_sl(ps_baby, 'baby.png', scale_h=545, center_x=512, bottom_y=576, brightness=0.92)
ps_baby.save(os.path.join(CAM_DIR, 'parts_baby_night5.jpg'), quality=90)

# 7. Night 4 Springlock Suit & Night 5 Scooping Room (Using authentic 1900x800 Scooping Room!)
scp_real = load_bg_rgb('scooping_real.gif', frame_idx='first')
scp_flash = load_bg_rgb('scooping_real.gif', frame_idx='mid')

def apply_springlock_visor(bg_img, open_plates=False):
    canvas = bg_img.copy().convert('RGBA')
    visor = Image.new('RGBA', (1024, 576), (0, 0, 0, 0))
    dv = ImageDraw.Draw(visor)
    if not open_plates:
        dv.rectangle([0, 0, 1024, 576], fill=(12, 10, 14, 175))
        dv.ellipse([160, 110, 460, 410], fill=(0, 0, 0, 0), outline=(70, 65, 80, 255), width=12)
        dv.ellipse([564, 110, 864, 410], fill=(0, 0, 0, 0), outline=(70, 65, 80, 255), width=12)
    else:
        dv.rectangle([0, 0, 140, 576], fill=(32, 30, 38, 235), outline=(90, 85, 105, 255), width=6)
        dv.rectangle([884, 0, 1024, 576], fill=(32, 30, 38, 235), outline=(90, 85, 105, 255), width=6)
    canvas.alpha_composite(visor)
    return canvas.convert('RGB')

sl_baby = paste_sl(scp_real, 'baby.png', scale_h=480, center_x=512, bottom_y=560, brightness=0.85)
apply_springlock_visor(sl_baby, open_plates=False).save(os.path.join(CAM_DIR, 'springlock_baby_talk.jpg'), quality=90)

sl_bal = paste_sl(scp_flash, 'ballora.png', scale_h=460, center_x=512, bottom_y=550, brightness=0.88)
apply_springlock_visor(sl_bal, open_plates=False).save(os.path.join(CAM_DIR, 'springlock_ballora_scooped.jpg'), quality=90)

sl_game = paste_sl(scp_real, 'minireena.png', scale_h=280, center_x=230, bottom_y=540, brightness=0.88)
sl_game = paste_sl(sl_game, 'minireena.png', scale_h=280, center_x=794, bottom_y=540, brightness=0.88, flip_x=True)
apply_springlock_visor(sl_game, open_plates=True).save(os.path.join(CAM_DIR, 'springlock_gameplay.jpg'), quality=90)

scp_ennard = paste_sl(scp_real, 'ennard.png', scale_h=500, center_x=512, bottom_y=565, brightness=0.92)
scp_ennard.save(os.path.join(CAM_DIR, 'scooping_room_ennard.jpg'), quality=90)

# 8. Private Room (Using real FNaF security office + 3 Monitors + Exotic Butters Trophy!)
priv_base = Image.open(os.path.join(ROOT, 'assets', 'bg', 'office_normal.png')).convert('RGB').resize((1024, 576), Image.Resampling.LANCZOS)
butters = Image.open(os.path.join(BG_DIR, 'butters_trophy.png')).convert('RGBA').resize((145, 145), Image.Resampling.LANCZOS)
priv_rgba = priv_base.convert('RGBA')
priv_rgba.alpha_composite(butters, dest=(445, 250))
priv_office = priv_rgba.convert('RGB')
priv_office.save(os.path.join(CAM_DIR, 'private_room_office.jpg'), quality=90)

paste_sl(priv_office, 'ennard.png', scale_h=470, center_x=155, bottom_y=545, brightness=0.85).save(os.path.join(CAM_DIR, 'private_room_ennard_left.jpg'), quality=90)
paste_sl(priv_office, 'ennard.png', scale_h=470, center_x=865, bottom_y=545, brightness=0.85, flip_x=True).save(os.path.join(CAM_DIR, 'private_room_ennard_right.jpg'), quality=90)
paste_sl(priv_office, 'ennard.png', scale_h=330, center_x=512, bottom_y=275, brightness=0.88, crop_bottom=0.65).save(os.path.join(CAM_DIR, 'private_room_ennard_vent.jpg'), quality=90)

# 9. Living Room CRT TV ("The Immortal and the Restless" starring Vlad-Ashi & Clara-Ashi + Exotic Butters!)
living = Image.new('RGB', (1024, 576), (8, 6, 18))
dl = ImageDraw.Draw(living)
# Living room wallpaper & table
dl.rectangle([0, 420, 1024, 576], fill=(24, 16, 30))
# CRT Television cabinet
dl.rectangle([250, 110, 774, 460], fill=(42, 30, 24), outline=(85, 65, 50), width=8)
dl.rectangle([280, 135, 744, 425], fill=(18, 24, 42), outline=(110, 120, 140), width=4)

# Paste Vlad & Clara scene inside TV screen with Ashi faces!
vc_img = load_bg_rgb('vlad_clara.png', size=(456, 282))
living.paste(vc_img, (284, 139))
living = paste_sl(living, 'ballora.png', scale_h=220, center_x=395, bottom_y=418, brightness=0.92, crop_bottom=0.68)
living = paste_sl(living, 'baby.png',    scale_h=210, center_x=615, bottom_y=418, brightness=0.94, crop_bottom=0.68, flip_x=True)

liv_rgba = living.convert('RGBA')
liv_rgba.alpha_composite(butters.resize((120, 120), Image.Resampling.LANCZOS), dest=(452, 8))
tv_final = liv_rgba.convert('RGB')
tv_final.save(os.path.join(CAM_DIR, 'tv_immortal_restless.jpg'), quality=90)

tv_ennard = paste_sl(tv_final, 'ennard.png', scale_h=500, center_x=820, bottom_y=576, brightness=0.88)
tv_ennard.save(os.path.join(CAM_DIR, 'tv_ennard_fake_ending.jpg'), quality=90)

# 10. Real Ending: Purple-lit Bathroom Mirror Silhouette with Glowing Purple Ennard-Ashi Eyes!
bath = Image.new('RGB', (1024, 576), (18, 8, 28))
db = ImageDraw.Draw(bath)
db.rectangle([260, 40, 764, 500], fill=(32, 16, 48), outline=(95, 60, 125), width=8)
bath_sil = paste_sl(bath, 'ennard.png', scale_h=460, center_x=512, bottom_y=500, brightness=0.35, contrast=1.55)
db2 = ImageDraw.Draw(bath_sil)
db2.ellipse([475, 145, 502, 168], fill=(235, 90, 255), outline=(255, 220, 255), width=3)
db2.ellipse([522, 145, 549, 168], fill=(235, 90, 255), outline=(255, 220, 255), width=3)
bath_sil.save(os.path.join(CAM_DIR, 'ending_bathroom_mirror.jpg'), quality=90)

print("Done! Total frames in assets5/cams:", len(os.listdir(CAM_DIR)))
