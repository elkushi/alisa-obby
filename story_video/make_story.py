# -*- coding: utf-8 -*-
"""Как всё началось — блочный роблокс-ролик про парк, скамейку и пинг-понг."""
from PIL import Image, ImageDraw, ImageFont
import math, os, shutil

BASE   = "/home/moustafa/Desktop/Alisa_birthday "
SPR    = os.path.join(BASE, "game/sprites")
OUT    = os.path.join(BASE, "story_video")
FRAMES = os.path.join(OUT, "frames")
W, H, FPS = 1080, 1080, 30
BAR = 96                                    # кинематографичные поля

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_title = ImageFont.truetype(F, 62)
f_card  = ImageFont.truetype(F, 42)
f_bub   = ImageFont.truetype(F, 40)

def hx(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def mix(c,d,a): return tuple(int(c[i]+(d[i]-c[i])*a) for i in range(3))
def lite(c,a): return mix(c,(255,255,255),a)
def dark(c,a): return mix(c,(11,16,36),a)

GRASS, PATH, WOOD = hx('#5FA83C'), hx('#C9BFA6'), hx('#8A5A3B')
TABLE, NET, SKIN  = hx('#2E7D57'), hx('#E8E8E8'), hx('#E0A878')
BRICK             = hx('#8E7F76')

def part(d,x,y,w,h,col,depth=16,studs=True):
    x,y,w,h = int(x),int(y),int(w),int(h)
    if x > W+250 or x+w < -250: return
    d.polygon([(x+w,y),(x+w+depth,y-depth),(x+w+depth,y+h-depth),(x+w,y+h)], fill=dark(col,.30))
    d.polygon([(x,y),(x+depth,y-depth),(x+w+depth,y-depth),(x+w,y)],         fill=lite(col,.24))
    d.rectangle([x,y,x+w,y+h], fill=col)
    d.rectangle([x,y+int(h*.74),x+w,y+h], fill=dark(col,.12))
    if studs and w>=60:
        n=max(1,round(w/80)); rx=min(18,(w/n)*.25); ry=rx*.55
        for i in range(n):
            sx=x+((i+.5)/n)*w+depth*.5; sy=y-depth*.5
            d.ellipse([sx-rx,sy-ry+ry*.6,sx+rx,sy+ry+ry*.6], fill=dark(col,.12))
            d.ellipse([sx-rx,sy-ry-ry*.2,sx+rx,sy+ry-ry*.2], fill=lite(col,.46))
    d.rectangle([x,y,x+w,y+h], outline=dark(col,.40), width=3)

def tree(d,x,base,s=1.0):
    part(d,x-22*s,base-135*s,44*s,135*s,WOOD,depth=int(11*s),studs=False)
    part(d,x-82*s,base-268*s,164*s,148*s,hx('#4E9B37'),depth=int(15*s))
    part(d,x-56*s,base-362*s,112*s,104*s,hx('#5CAF3F'),depth=int(13*s))

def bench(d,x,base,s=1.0):
    part(d,x-108*s,base-34*s,216*s,16*s,WOOD,depth=int(12*s),studs=False)     # сиденье
    part(d,x-108*s,base-96*s,216*s,14*s,WOOD,depth=int(12*s),studs=False)     # спинка
    for dx in (-88,80):
        part(d,x+dx*s,base-34*s,18*s,34*s,dark(WOOD,.2),depth=int(8*s),studs=False)
        part(d,x+dx*s,base-100*s,14*s,66*s,dark(WOOD,.2),depth=int(8*s),studs=False)

def pingpong(d,x,base,s=1.0):
    part(d,x-130*s,base-88*s,260*s,14*s,TABLE,depth=int(14*s),studs=False)
    d.rectangle([x-130*s,base-84*s,x+130*s,base-81*s], fill=NET)
    part(d,x-6*s,base-112*s,12*s,26*s,NET,depth=int(10*s),studs=False)        # сетка
    for dx in (-118,104):
        part(d,x+dx*s,base-88*s,16*s,88*s,dark(TABLE,.28),depth=int(7*s),studs=False)

def buildings(d,cam,base):
    for k in range(9):
        bx = k*250 - (cam*0.35)%250 - 250
        bh = 300 + ((k*137)%5)*90
        part(d,bx,base-bh,200,bh,mix(BRICK,(40,48,80),.45),depth=18,studs=False)
        for r in range(bh//70):
            for c in range(3):
                lit = ((k*7+r*3+c) % 3) != 0
                col = hx('#FFD98A') if lit else hx('#2B3352')
                wx = bx+22+c*58; wy = base-bh+30+r*70
                d.rectangle([wx,wy,wx+34,wy+40], fill=col)

def bystander(d,x,base,h,shirt,pants,hair,sit=False):
    u = h/100.0
    legh = 30*u if sit else 42*u
    part(d,x-14*u,base-legh,28*u,legh,pants,depth=int(6*u),studs=False)
    part(d,x-17*u,base-legh-40*u,34*u,40*u,shirt,depth=int(7*u),studs=False)
    part(d,x-25*u,base-legh-38*u,9*u,34*u,SKIN,depth=int(4*u),studs=False)
    part(d,x+16*u,base-legh-38*u,9*u,34*u,SKIN,depth=int(4*u),studs=False)
    part(d,x-13*u,base-legh-70*u,26*u,30*u,SKIN,depth=int(6*u),studs=False)
    part(d,x-15*u,base-legh-80*u,30*u,13*u,hair,depth=int(6*u),studs=False)

def bubble(img,d,cx,cy,text,font,tail=True):
    bb=d.textbbox((0,0),text,font=font); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    w,h = tw+56, th+44
    x,y = cx-w//2, cy-h
    d.rounded_rectangle([x,y,x+w,y+h], radius=20, fill=(255,255,255), outline=(30,40,70), width=4)
    if tail: d.polygon([(cx-14,y+h-2),(cx+14,y+h-2),(cx,y+h+22)], fill=(255,255,255), outline=None)
    d.text((x+28-bb[0], y+22-bb[1]), text, font=font, fill=(34,48,92))

def textc(d,s,cy,font,fill=(255,255,255),ow=6):
    bb=d.textbbox((0,0),s,font=font); x=(W-(bb[2]-bb[0]))//2-bb[0]
    for dx in range(-ow,ow+1):
        for dy in range(-ow,ow+1):
            if dx*dx+dy*dy<=ow*ow: d.text((x+dx,cy+dy),s,font=font,fill=(18,24,46))
    d.text((x,cy),s,font=font,fill=fill)

def shadow(d,x,base,w):
    d.ellipse([x-w,base-9,x+w,base+9], fill=(40,60,40))

S={}
for n in ("alisa_front","alisa_back","alisa_faceL","alisa_faceR",
          "moustafa_front","moustafa_back","moustafa_faceL","moustafa_faceR"):
    S[n]=Image.open(f"{SPR}/{n}.png").convert("RGBA")
def put(img,name,x,base,h,bob=0.0):
    sp=S[name]; s=sp.resize((max(1,round(sp.width*h/sp.height)),int(h)),Image.LANCZOS)
    img.paste(s,(int(x-s.width/2),int(base-h-bob)),s)

def sky(tint):
    top,bot = tint
    g=Image.new("RGB",(1,H)); gd=ImageDraw.Draw(g)
    for y in range(H): gd.point((0,y),fill=mix(top,bot,min(1,y/(H*.8))))
    return g.resize((W,H))

GOLD_SKY = (hx('#FFC98A'), hx('#CFE6F5'))
EVE_SKY  = (hx('#2B3A6B'), hx('#7A5C86'))

def clouds(d,cam,warm=True):
    for k in range(-1,7):
        cx=int(k*430+(k*137)%190-cam*0.18)%(W+900)-300
        cy=70+(k*83)%150
        c=(255,246,232) if warm else (120,128,170)
        d.rectangle([cx,cy,cx+180,cy+58],fill=c)
        d.rectangle([cx+48,cy-38,cx+172,cy+16],fill=c)

# ---------------- сцены ----------------
GB = 920          # линия земли в парке

def treeline(d,cam,base,warm):
    col = mix(hx('#3E7A2A'),(150,190,215),.45) if warm else mix(hx('#24402B'),(60,74,120),.5)
    for k in range(16):
        bx=int(k*150-(cam*0.28)%150-150); bh=150+((k*97)%4)*52
        d.rectangle([bx,base-bh,bx+150,base],fill=col)

def bush(d,x,base,s=1.0):
    part(d,x-52*s,base-58*s,104*s,58*s,hx('#4E9B37'),depth=int(11*s))

def park_bg(img,d,cam,warm=True,trees_at=(220,760,1500,2100)):
    clouds(d,cam,warm)
    treeline(d,cam,GB-90,warm)
    d.rectangle([0,GB-120,W,GB],fill=lite(GRASS,.28) if warm else dark(GRASS,.35))
    part(d,-300-cam*0,GB,W+600,300,GRASS if warm else dark(GRASS,.30),depth=20,studs=False)
    d.rectangle([0,GB+120,W,GB+190],fill=PATH if warm else dark(PATH,.35))
    for k in range(9):
        bx=int(k*330-(cam*0.9)%330-200)
        d.rectangle([bx,GB+132,bx+120,GB+140],fill=dark(PATH,.10))
    for k in range(6):
        bush(d,int(k*430-(cam*0.95)%430-200),GB,1.05)
    for tx in trees_at: tree(d,tx-cam,GB,1.55)

def sc1(img,d,p,t):      # парк, Мустафа ждёт у стола
    cam=-60+p*90
    park_bg(img,d,cam)
    pingpong(d,640-cam,GB,2.0)
    shadow(d,470-cam,GB,60)
    put(img,"moustafa_faceR",470-cam,GB,330,abs(math.sin(t*2))*4)
    return "Парк. Я просто ждал свою очередь."

def sc2(img,d,p,t):      # Алиса и две подруги
    cam=120-p*60
    park_bg(img,d,cam,trees_at=(180,820,1480))
    bench(d,900-cam,GB,1.5)
    bystander(d,820-cam,GB-46,300,hx('#C9748A'),hx('#3A4B7A'),hx('#4A3226'),sit=True)
    bystander(d,1010-cam,GB-46,300,hx('#7FA8C9'),hx('#5B4A3A'),hx('#2E2320'),sit=True)
    shadow(d,690-cam,GB,42)
    put(img,"alisa_front",690-cam,GB,325,abs(math.sin(t*1.6))*3)
    return "И тут была она. С двумя подругами."

def sc3(img,d,p,t):      # крупный план: он смотрит с любопытством
    cam=0
    park_bg(img,d,cam,trees_at=(120,900))
    pingpong(d,900,GB,2.0)
    h=430+p*70
    shadow(d,470,GB,60)
    put(img,"moustafa_faceR",470,GB,h)
    if p>0.35: bubble(img,d,760,GB-h-40,"Где я её видел?",f_bub)
    return None

def sc4(img,d,p,t):      # она оглядывается
    park_bg(img,d,40,trees_at=(200,980))
    shadow(d,560,GB,58)
    name = "alisa_faceL" if p<0.55 else "alisa_front"
    put(img,name,560,GB,430)
    if 0.25<p<0.8: bubble(img,d,840,GB-460,"...",f_bub)
    return None

def sc5(img,d,p,t):      # идут вместе и болтают
    cam=p*620
    park_bg(img,d,cam,trees_at=(300,1100,1900,2600))
    x1,x2 = 430, 610
    shadow(d,x1,GB,42); shadow(d,x2,GB,42)
    b=abs(math.sin(t*5))*6
    put(img,"alisa_faceR",x1,GB,320,b)
    put(img,"moustafa_faceR",x2,GB,340,abs(math.sin(t*5+1.4))*6)
    return "Потом мы встречались ещё. И ещё."

def sc6(img,d,p,t):      # скамейка, «подъезд»
    park_bg(img,d,80,trees_at=(160,1000))
    bench(d,560,GB,1.7)
    shadow(d,455,GB,40); shadow(d,650,GB,40)
    put(img,"alisa_front",455,GB-58,300)
    put(img,"moustafa_front",650,GB-58,315)
    if p>0.2: bubble(img,d,360,GB-400,"«Подъезд»",f_bub)
    if p>0.62: bubble(img,d,760,GB-420,"...что?",f_bub)
    return "Она объясняла мне слова. Я старался."

def sc7(img,d,p,t):      # арабское слово
    park_bg(img,d,80,trees_at=(160,1000))
    bench(d,560,GB,1.7)
    shadow(d,455,GB,40); shadow(d,650,GB,40)
    j=abs(math.sin(t*6))*5 if p>0.55 else 0
    put(img,"alisa_front",455,GB-58,300,j)
    put(img,"moustafa_front",650,GB-58,315,j)
    if p>0.18: bubble(img,d,760,GB-420,"«Йалла!»",f_bub)
    if p>0.55: bubble(img,d,360,GB-400,"«Йалла!»",f_bub)
    return "А я — свои."

def sc8(img,d,p,t):      # вечерняя Москва
    cam=p*520
    clouds(d,cam,False)
    buildings(d,cam,GB)
    part(d,-300,GB,W+600,300,dark(PATH,.42),depth=20,studs=False)
    x1,x2=440,620
    d.ellipse([x1-44,GB-9,x1+44,GB+9],fill=(30,34,58))
    d.ellipse([x2-44,GB-9,x2+44,GB+9],fill=(30,34,58))
    put(img,"alisa_faceR",x1,GB,320,abs(math.sin(t*5))*6)
    put(img,"moustafa_faceR",x2,GB,340,abs(math.sin(t*5+1.4))*6)
    return "Москва вечером. Мы просто шли и смеялись."

def sc9(img,d,p,t):      # снова у стола
    park_bg(img,d,-40,trees_at=(240,900,1600))
    pingpong(d,800,GB,2.0)
    shadow(d,430,GB,44); shadow(d,600,GB,42)
    put(img,"moustafa_faceR",430,GB,215)
    put(img,"alisa_faceL",600,GB,200)
    return "Тот же парк. Та же очередь в пинг-понг."

def sc10(img,d,p,t):     # уходят, камера отъезжает
    z=1.0-p*0.22
    park_bg(img,d,-40+p*40,trees_at=(200,880,1560,2200))
    x1,x2 = 470+p*150, 640+p*150
    shadow(d,x1,GB,40); shadow(d,x2,GB,40)
    put(img,"alisa_back",x1,GB,320*z,abs(math.sin(t*4))*5)
    put(img,"moustafa_back",x2,GB,340*z,abs(math.sin(t*4+1.3))*5)
    return None

SCENES=[(4.5,sc1),(3.6,sc2),(3.6,sc3),(3.4,sc4),(4.4,sc5),
        (5.0,sc6),(4.4,sc7),(4.4,sc8),(4.0,sc9),(5.6,sc10)]
TOTAL=sum(s[0] for s in SCENES)
N=int(TOTAL*FPS)

if os.path.isdir(FRAMES): shutil.rmtree(FRAMES)
os.makedirs(FRAMES)
SKY_W, SKY_E = sky(GOLD_SKY), sky(EVE_SKY)

i=0; elapsed=0.0
for dur,fn in SCENES:
    for k in range(int(dur*FPS)):
        t=elapsed+k/FPS; p=k/(dur*FPS)
        img=(SKY_E if fn is sc8 else SKY_W).copy()
        d=ImageDraw.Draw(img,"RGBA")
        cap=fn(img,d,p,t)
        d=ImageDraw.Draw(img,"RGBA")
        if cap:
            a=min(1,p/0.12,(1-p)/0.12)
            if a>0.02:
                ov=Image.new("RGBA",(W,H),(0,0,0,0))
                od=ImageDraw.Draw(ov)
                bb=od.textbbox((0,0),cap,font=f_card)
                od.rectangle([0,H-BAR-6,W,H],fill=(14,18,34,int(215*a)))
                x=(W-(bb[2]-bb[0]))//2-bb[0]
                od.text((x,H-BAR+40),cap,font=f_card,fill=(238,242,255,int(255*a)))
                img=Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
                d=ImageDraw.Draw(img,"RGBA")
        d.rectangle([0,0,W,BAR-6],fill=(14,18,34))          # верхнее поле
        if not cap: d.rectangle([0,H-BAR+6,W,H],fill=(14,18,34))
        if fn is sc10:
            if p<0.78:                       # сначала одна мысль, потом другая
                if p>0.30: textc(d,"Всё началось с того,",300,f_title)
                if p>0.44: textc(d,"что я просто ждал",378,f_title)
                if p>0.56: textc(d,"свою очередь.",456,f_title)
            if p>0.80:
                ov=Image.new("RGBA",(W,H),(14,18,34,int(200*min(1,(p-0.80)/0.12))))
                img=Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
                d=ImageDraw.Draw(img,"RGBA")
                textc(d,"С днём рождения,",470,f_card,fill=(242,185,59),ow=4)
                textc(d,"Алиса",530,f_title)
        img.save(f"{FRAMES}/f{i:05d}.jpg", quality=95); i+=1
    elapsed+=dur
    print(f"  сцена {fn.__name__} готова ({i}/{N})",flush=True)
print("frames done",i)
