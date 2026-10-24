import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops
S = 1024
def grad(size, c1, c2, angle=90, radial=False, center=(.5,.5)):
    w,h = size; im = Image.new("RGBA", size); px = im.load()
    ca = math.cos(math.radians(angle)); sa = math.sin(math.radians(angle))
    for y in range(h):
        for x in range(w):
            if radial:
                t = min(1, math.hypot(x/w-center[0], y/h-center[1]) / .72)
            else:
                t = ((x/w-.5)*ca + (y/h-.5)*sa) + .5; t = max(0, min(1, t))
            px[x,y] = tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(4))
    return im
def mask_poly(pts, size=(S,S)):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).polygon(pts, fill=255); return m
def paste_grad(base, mask, g):
    base.alpha_composite(Image.composite(g, Image.new("RGBA", base.size, (0,0,0,0)), mask))
def outline(base, mask, width, color):
    m = mask.filter(ImageFilter.MaxFilter(width*2+1))
    layer = Image.new("RGBA", base.size, color); base.alpha_composite(Image.composite(layer, Image.new("RGBA", base.size,(0,0,0,0)), m))
DARK = (24, 12, 46, 255)
img = Image.new("RGBA", (S,S), (0,0,0,0))
# --- app-style rounded square background
bgm = Image.new("L", (S,S), 0); ImageDraw.Draw(bgm).rounded_rectangle([24,24,S-24,S-24], radius=200, fill=255)
outline(img, bgm, 14, DARK)
bg = grad((S,S), (98, 62, 220, 255), (28, 16, 72, 255), radial=True, center=(.5,.42))
paste_grad(img, bgm, bg)
rim = ImageChops.subtract(bgm, bgm.filter(ImageFilter.MinFilter(21)))
img.alpha_composite(Image.composite(grad((S,S),(255,236,150,255),(214,130,30,255),angle=90), Image.new("RGBA",(S,S),(0,0,0,0)), rim))
# light rays behind the crystal
rays = Image.new("L", (S,S), 0); d = ImageDraw.Draw(rays)
cx, cy = S*.5, S*.5
for k in range(12):
    a = math.radians(k*30+8); a2 = a + math.radians(9)
    d.polygon([(cx,cy),(cx+math.cos(a)*900,cy+math.sin(a)*900),(cx+math.cos(a2)*900,cy+math.sin(a2)*900)], fill=38)
rays = ImageChops.multiply(rays, bgm)
img.alpha_composite(Image.composite(Image.new("RGBA",(S,S),(190,170,255,255)), Image.new("RGBA",(S,S),(0,0,0,0)), rays))
# inner glow
glow = Image.new("L",(S,S),0); ImageDraw.Draw(glow).ellipse([cx-300,cy-300,cx+300,cy+300], fill=150)
glow = ImageChops.multiply(glow.filter(ImageFilter.GaussianBlur(110)), bgm)
img.alpha_composite(Image.composite(Image.new("RGBA",(S,S),(255,170,240,255)), Image.new("RGBA",(S,S),(0,0,0,0)), glow))
# --- golden pickaxe behind (diagonal, handle bottom-left -> head top-right)
def rot(pts, ang, c):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0]+(x-c[0])*ca-(y-c[1])*sa, c[1]+(x-c[0])*sa+(y-c[1])*ca) for x,y in pts]
pc = (S*.5, S*.6); ang = math.radians(-14)
handle = rot([(pc[0]-44, pc[1]-300), (pc[0]+44, pc[1]-300), (pc[0]+44, pc[1]+380), (pc[0]-44, pc[1]+380)], ang, pc)
head = rot([(pc[0]-360, pc[1]-250), (pc[0]-200, pc[1]-345), (pc[0], pc[1]-372), (pc[0]+200, pc[1]-345), (pc[0]+360, pc[1]-250),
            (pc[0]+290, pc[1]-195), (pc[0]+165, pc[1]-245), (pc[0], pc[1]-262), (pc[0]-165, pc[1]-245), (pc[0]-290, pc[1]-195)], ang, pc)
hm = mask_poly(handle); km = mask_poly(head)
outline(img, ImageChops.lighter(hm, km), 22, DARK)
paste_grad(img, hm, grad((S,S), (176, 104, 52, 255), (110, 58, 28, 255), angle=45))
paste_grad(img, km, grad((S,S), (255, 240, 150, 255), (232, 150, 20, 255), angle=100))
# head highlight
hl = rot([(pc[0]-300, pc[1]-262), (pc[0]-180, pc[1]-330), (pc[0], pc[1]-352), (pc[0]+40, pc[1]-345), (pc[0]-170, pc[1]-312)], ang, pc)
img.alpha_composite(Image.composite(Image.new("RGBA",(S,S),(255,255,230,190)), Image.new("RGBA",(S,S),(0,0,0,0)), mask_poly(hl)))
# --- crystal cluster
def crystal(cx, cy, w, h, tip, tilt, light=(255, 190, 250, 255), dark=(120, 50, 210, 255)):
    hw = w/2
    body = [(cx-hw, cy-h/2), (cx, cy-h/2-tip), (cx+hw, cy-h/2), (cx+hw, cy+h/2), (cx, cy+h/2+tip*.55), (cx-hw, cy+h/2)]
    body = rot(body, math.radians(tilt), (cx, cy))
    m = mask_poly(body)
    return body, m, light, dark
parts = [crystal(S*.31, S*.66, 140, 170, 85, -26, dark=(90, 60, 200, 255)),
         crystal(S*.69, S*.66, 150, 180, 90, 24, dark=(60, 110, 225, 255), light=(170, 240, 255, 255)),
         crystal(S*.50, S*.57, 230, 270, 140, 0)]
allm = Image.new("L",(S,S),0)
for b,m,_,_ in parts: allm = ImageChops.lighter(allm, m)
outline(img, allm, 22, DARK)
for body, m, light, dark in parts:
    outline(img, m, 9, DARK)
    paste_grad(img, m, grad((S,S), light, dark, angle=110))
    # facet: right half darker, centre ridge highlight
    cxb = sum(p[0] for p in body)/len(body)
    top = body[1]; bot = body[4]
    right = [top, body[2], body[3], bot]
    img.alpha_composite(Image.composite(Image.new("RGBA",(S,S),(40,0,90,85)), Image.new("RGBA",(S,S),(0,0,0,0)), mask_poly(right)))
    left = [top, body[0], (body[0][0]*.6+top[0]*.4, body[0][1]*.6+top[1]*.4)]
    img.alpha_composite(Image.composite(Image.new("RGBA",(S,S),(255,255,255,140)), Image.new("RGBA",(S,S),(0,0,0,0)), mask_poly(left)))
    d = ImageDraw.Draw(img)
    d.line([top, bot], fill=(255,255,255,120), width=8)
    # glossy streak
    sx = body[0][0]*.7 + top[0]*.3; sy = body[0][1]*.7 + top[1]*.3
    d.line([(sx+18, sy+40), (sx+18, sy+40+ (body[5][1]-body[0][1])*.55)], fill=(255,255,255,170), width=14)
# --- sparkles
def star(x, y, r, col=(255,255,255,255)):
    pts = []
    for k in range(8):
        a = math.radians(k*45-90); rr = r if k%2==0 else r*.28
        pts.append((x+math.cos(a)*rr, y+math.sin(a)*rr))
    m = mask_poly(pts); outline(img, m, 8, DARK)
    img.alpha_composite(Image.composite(Image.new("RGBA",(S,S),col), Image.new("RGBA",(S,S),(0,0,0,0)), m))
star(S*.80, S*.40, 64, (255, 240, 140, 255)); star(S*.19, S*.42, 44); star(S*.84, S*.80, 40, (170,240,255,255)); star(S*.16, S*.80, 34, (255,200,250,255))
img.save("logo_1024.png")
img.resize((512,512), Image.LANCZOS).save("logo_512.png")
s64 = img.resize((64,64), Image.LANCZOS)
s64.save("server-icon.png")
s64.resize((256,256), Image.NEAREST).save("preview64.png")
