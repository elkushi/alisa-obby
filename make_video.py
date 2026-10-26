# -*- coding: utf-8 -*-
"""Роблокс-ролик для телеграма: те же аватары и та же блочная графика, что в игре."""
from PIL import Image, ImageDraw, ImageFont
import math, os, shutil

HERE   = "/home/moustafa/Desktop/Alisa_birthday "
SPR    = os.path.join(HERE, "game/sprites")
FRAMES = os.path.join(HERE, "video_out/frames")
W, H, FPS, SECS = 1080, 1080, 30, 15
N = FPS * SECS

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_big = ImageFont.truetype(FONT, 92)
f_mid = ImageFont.truetype(FONT, 46)
f_sm  = ImageFont.truetype(FONT, 34)

def hx(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def mix(c, d, a): return tuple(int(c[i] + (d[i] - c[i]) * a) for i in range(3))
def lite(c, a): return mix(c, (255, 255, 255), a)
def dark(c, a): return mix(c, (11, 16, 36), a)

GRASS, STONE, ROSE, CREAM = hx('#5FA83C'), hx('#98A3B6'), hx('#A9535F'), hx('#E8DFCF')
GOLD, RED, DIRT           = hx('#F2B93B'), hx('#C0202B'), hx('#7A5230')
SKY_HI, SKY_LO            = hx('#8FD3F4'), hx('#EFF8FD')

def part(d, x, y, w, h, col, depth=18, studs=True):
    x, y = int(x), int(y)
    d.polygon([(x+w,y),(x+w+depth,y-depth),(x+w+depth,y+h-depth),(x+w,y+h)], fill=dark(col,.30))
    d.polygon([(x,y),(x+depth,y-depth),(x+w+depth,y-depth),(x+w,y)],         fill=lite(col,.24))
    d.rectangle([x, y, x+w, y+h], fill=col)
    d.rectangle([x, y+int(h*.72), x+w, y+h], fill=dark(col,.13))     # низ темнее
    if studs and w >= 60:
        n = max(1, round(w/78))
        rx = min(20, (w/n)*.26); ry = rx*.55
        for i in range(n):
            sx = x + ((i+.5)/n)*w + depth*.5; sy = y - depth*.5
            d.ellipse([sx-rx, sy-ry+ry*.6, sx+rx, sy+ry+ry*.6], fill=dark(col,.12))
            d.ellipse([sx-rx, sy-ry-ry*.2, sx+rx, sy+ry-ry*.2], fill=lite(col,.46))
    d.rectangle([x, y, x+w, y+h], outline=dark(col,.42), width=3)

def gift(d, cx, cy, s=1.0):
    w, h = int(64*s), int(54*s)
    part(d, cx-w//2, cy-h, w, h, GOLD, depth=int(13*s), studs=False)
    d.rectangle([cx-int(7*s), cy-h, cx+int(7*s), cy], fill=RED)
    part(d, cx-int(w*.62), cy-h-int(18*s), int(w*1.24), int(18*s), hx('#FFD469'), depth=int(13*s), studs=False)
    d.rectangle([cx-int(7*s), cy-h-int(18*s), cx+int(7*s), cy-h], fill=RED)
    r = int(14*s)
    d.ellipse([cx-int(30*s)-r, cy-h-int(30*s)-r, cx-int(30*s)+r, cy-h-int(30*s)+r], fill=RED)
    d.ellipse([cx+int(30*s)-r, cy-h-int(30*s)-r, cx+int(30*s)+r, cy-h-int(30*s)+r], fill=RED)

def tree(d, x, base):
    part(d, x-26, base-150, 52, 150, DIRT, depth=12, studs=False)
    part(d, x-92, base-295, 184, 160, hx('#4E9B37'), depth=16)
    part(d, x-64, base-400, 128, 115, hx('#5CAF3F'), depth=14)

def balloons(d, x, base, t):
    cols = [RED, GOLD, hx('#4FC3F7'), ROSE]
    for i, c in enumerate(cols):
        bx = x + i*74 - 110
        by = base - 430 - math.sin(t*1.4 + i)*26
        d.line([(bx, by+58), (bx + math.sin(t+i)*10, base-60)], fill=(60,72,104), width=3)
        d.ellipse([bx-38, by-48, bx+38, by+48], fill=c)
        d.ellipse([bx-24, by-30, bx-8, by-8], fill=(255,255,255,90))

# ---------- мир ----------
SEGS = [(0,700,760), (820,1380,760), (1500,2020,720), (2140,3300,760)]
def surface(x):
    for a,b,y in SEGS:
        if a <= x <= b: return y
    return None
def player_pos(x):
    s = surface(x)
    if s is not None: return s, 0.0
    prev = [t for t in SEGS if t[1] < x][-1]
    nxt  = [t for t in SEGS if t[0] > x][0]
    t = (x - prev[1]) / (nxt[0] - prev[1])
    base = prev[2] + (nxt[2]-prev[2])*t
    return base - math.sin(t*math.pi)*240, t

alisa_r  = Image.open(f"{SPR}/alisa_faceR.png").convert("RGBA")
alisa_f  = Image.open(f"{SPR}/alisa_front.png").convert("RGBA")
mous_l   = Image.open(f"{SPR}/moustafa_faceL.png").convert("RGBA")
def scaled(im, h):
    return im.resize((max(1, round(im.width*h/im.height)), h), Image.LANCZOS)

SKY = Image.new("RGB", (1, H))
sd = ImageDraw.Draw(SKY)
for yy in range(H):
    sd.point((0, yy), fill=mix(SKY_HI, SKY_LO, min(1, yy/(H*0.85))))
SKY = SKY.resize((W, H))

def text_c(d, s, cy, font, fill=(255,255,255), outline=(20,27,51), ow=7):
    bb = d.textbbox((0,0), s, font=font); tw = bb[2]-bb[0]
    x, y = (W-tw)//2 - bb[0], cy
    for dx in range(-ow, ow+1):
        for dy in range(-ow, ow+1):
            if dx*dx+dy*dy <= ow*ow: d.text((x+dx, y+dy), s, font=font, fill=outline)
    d.text((x, y), s, font=font, fill=fill)

if os.path.isdir(FRAMES): shutil.rmtree(FRAMES)
os.makedirs(FRAMES)

for i in range(N):
    t = i / FPS
    # камера: едет вправе вместе с Алисой, в конце останавливается на Мустафе
    px = 230 + min(t, 10.5) * 232
    py, arc = player_pos(px)
    cam = max(0, min(2400, px - W*0.40))

    img = SKY.copy()
    d = ImageDraw.Draw(img, "RGBA")

    for k in range(-1, 7):                                   # облака
        cx = int(k*430 + (k*137) % 190 - cam*0.22) % (W+900) - 300
        cy = 90 + (k*83) % 170
        d.rectangle([cx, cy, cx+190, cy+62], fill=(255,255,255))
        d.rectangle([cx+52, cy-42, cx+184, cy+20], fill=(255,255,255))
        d.rectangle([cx, cy+52, cx+190, cy+66], fill=(203,229,246))

    for k in range(7):                                        # дальние холмы
        hx0 = int(k*520 - cam*0.12)
        d.rectangle([hx0, 700, hx0+380, H], fill=(150, 196, 225))

    tree(d, 360-cam, 760)
    tree(d, 1760-cam, 720)

    for a, b, y in SEGS:                                      # платформы
        col = ROSE if y == 720 else (CREAM if a == 2140 else GRASS)
        part(d, a-cam, y, b-a, 320, col)

    for gx, gy in [(560,660),(1120,650),(1760,610),(2320,640)]:  # подарки
        if -200 < gx-cam < W+200:
            gift(d, gx-cam, gy + math.sin(t*2.4+gx)*10, .95)

    balloons(d, 2980-cam, 760, t)
    gift(d, 2700-cam, 760, 2.1)                                # большой подарок
    m = scaled(mous_l, 250); img.paste(m, (int(2860-cam-m.width/2), 760-250), m)

    moving = t < 10.4
    spr = scaled(alisa_r if moving else alisa_f, 215)
    if arc > 0.02 and arc < 0.98 and px > 1900:                # сальто на последнем прыжке
        spr = spr.rotate(-arc*360, resample=Image.BICUBIC, expand=True)
    bob = abs(math.sin(t*9))*7 if surface(px) is not None else 0
    img.paste(spr, (int(px-cam-spr.width/2), int(py-spr.height-bob)), spr)

    if t > 11.0:                                               # финальные титры
        k = min(1, (t-11.0)/0.5)
        ov = Image.new("RGBA", (W, H), (20, 27, 51, int(150*k)))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(img, "RGBA")
        text_c(d, "С ДНЁМ РОЖДЕНИЯ,", 430, f_mid, fill=(242,185,59), ow=5)
        text_c(d, "АЛИСА!", 490, f_big)
        if t > 12.3:
            text_c(d, "твоё обби уже ждёт", 630, f_sm, fill=(232,236,250), ow=5)

    img.save(f"{FRAMES}/f{i:04d}.png")
    if i % 60 == 0: print(f"  {i}/{N}", flush=True)

print("frames done")
