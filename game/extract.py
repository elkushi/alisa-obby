from PIL import Image
import numpy as np
from collections import deque
import os

SRC = "/home/moustafa/Desktop/Alisa_birthday "
OUT = "/home/moustafa/Desktop/Alisa_birthday /game/sprites"

BODY = {
    "front": (780, 25, 999, 389),
    "back":  (1014, 25, 1231, 389),
    "left":  (780, 444, 999, 804),
    "right": (1014, 444, 1231, 804),
}
HEAD = (780, 861, 1231, 1254)

def flood_alpha(crop, tol, seed_bottom=True):
    a = np.array(crop).astype(int)
    h, w, _ = a.shape
    parts = [a[0:4].reshape(-1,3), a[:,0:4].reshape(-1,3), a[:,-4:].reshape(-1,3)]
    if seed_bottom: parts.append(a[-4:].reshape(-1,3))
    bg = np.median(np.concatenate(parts), axis=0)
    dist = np.abs(a - bg).sum(axis=2)
    cand = dist < tol
    seen = np.zeros((h,w), bool); q = deque()
    edges = [(0,x) for x in range(w)] + [(y,0) for y in range(h)] + [(y,w-1) for y in range(h)]
    if seed_bottom: edges += [(h-1,x) for x in range(w)]
    for y,x in edges:
        if cand[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    while q:
        y,x = q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and cand[ny,nx]:
                seen[ny,nx]=True; q.append((ny,nx))
    alpha = np.where(seen, 0, 255).astype(np.uint8)
    soft = np.clip((dist - tol*0.45)/(tol*0.75)*255, 0, 255).astype(np.uint8)
    b = np.zeros_like(seen)
    b[1:,:] |= seen[:-1,:]; b[:-1,:] |= seen[1:,:]
    b[:,1:] |= seen[:,:-1]; b[:,:-1] |= seen[:,1:]
    bd = b & ~seen
    alpha[bd] = np.minimum(alpha[bd], soft[bd])
    img = Image.fromarray(np.dstack([np.array(crop), alpha]), "RGBA")
    arr = np.array(img); ys,xs = np.where(arr[:,:,3] > 8)
    return img.crop((max(0,xs.min()-2), max(0,ys.min()-2),
                     min(w,xs.max()+3), min(h,ys.max()+3)))

def scale_h(img, h):
    return img.resize((max(1,round(img.width*h/img.height)), h), Image.LANCZOS)

for who, fn in (("alisa","alisa.png"), ("moustafa","moustafa.png")):
    src = Image.open(os.path.join(SRC, fn)).convert("RGB")
    for name, box in BODY.items():
        img = flood_alpha(src.crop(box), 34, seed_bottom=True)
        img = scale_h(img, 200)
        img.save(f"{OUT}/{who}_{name}.png", optimize=True)
        print(who, name, img.size)
    hd = flood_alpha(src.crop(HEAD), 40, seed_bottom=False)
    hd = scale_h(hd, 190)
    hd.save(f"{OUT}/{who}_head.png", optimize=True)
    print(who, "head", hd.size)
