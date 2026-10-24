import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops
S = 1024
CLEAR = (0, 0, 0, 0)
def grad(c1, c2, angle=90, radial=False, center=(.5, .5), reach=.72):
    im = Image.new("RGBA", (S, S)); px = im.load()
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    for y in range(0, S):
        for x in range(0, S):
            if radial: t = min(1, math.hypot(x / S - center[0], y / S - center[1]) / reach)
            else: t = max(0, min(1, ((x / S - .5) * ca + (y / S - .5) * sa) + .5))
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))
    return im
def poly(pts):
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).polygon(pts, fill=255); return m
def fill(img, mask, src):
    if isinstance(src, tuple): src = Image.new("RGBA", (S, S), src)
    img.alpha_composite(Image.composite(src, Image.new("RGBA", (S, S), CLEAR), mask))
def grow(mask, r): return mask.filter(ImageFilter.MaxFilter(r * 2 + 1))
def shrink(mask, r): return mask.filter(ImageFilter.MinFilter(r * 2 + 1))
def rot(pts, ang, c):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]
DARK = (22, 10, 42, 255)
OUT = 26
img = Image.new("RGBA", (S, S), CLEAR)
# ------------------------------------------------ geometry
cx, cy = 512, 590
R = 330                                   # shield: hexagon, flat sides left/right, points top/bottom
shield = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]
sm = poly(shield)
# pickaxe (behind everything except the shield back) - diagonal, head top-left breaking out
pc = (cx + 30, cy - 10); ang = math.radians(-38)
handle = rot([(pc[0] - 30, pc[1] - 300), (pc[0] + 30, pc[1] - 300), (pc[0] + 30, pc[1] + 400), (pc[0] - 30, pc[1] + 400)], ang, pc)
head = rot([(pc[0] - 330, pc[1] - 235), (pc[0] - 190, pc[1] - 330), (pc[0], pc[1] - 362), (pc[0] + 190, pc[1] - 330), (pc[0] + 330, pc[1] - 235),
            (pc[0] + 270, pc[1] - 205), (pc[0] + 160, pc[1] - 255), (pc[0], pc[1] - 272), (pc[0] - 160, pc[1] - 255), (pc[0] - 270, pc[1] - 205)], ang, pc)
hm, km = poly(handle), poly(head)
# crystals (front) - main one breaks far out of the top
def crystal(x, y, w, h, tip, tilt, btip=.5):
    hw = w / 2
    b = [(x - hw, y - h / 2), (x, y - h / 2 - tip), (x + hw, y - h / 2), (x + hw, y + h / 2), (x, y + h / 2 + tip * btip), (x - hw, y + h / 2)]
    return rot(b, math.radians(tilt), (x, y))
crys = [(crystal(cx - 150, cy + 45, 135, 170, 85, -28), (190, 140, 255, 255), (80, 50, 190, 255)),
        (crystal(cx + 155, cy + 50, 140, 175, 90, 26), (160, 235, 255, 255), (50, 110, 220, 255)),
        (crystal(cx, cy - 70, 215, 310, 170, 0), (255, 200, 255, 255), (125, 45, 215, 255))]
cm = Image.new("L", (S, S), 0)
for b, _, _ in crys: cm = ImageChops.lighter(cm, poly(b))
# ------------------------------------------------ one dark outline around the whole silhouette
silhouette = ImageChops.lighter(ImageChops.lighter(sm, cm), ImageChops.lighter(hm, km))
fill(img, grow(silhouette, OUT), DARK)
# soft outer glow (still transparent background, just a faint aura)
aura = grow(silhouette, OUT + 10).filter(ImageFilter.GaussianBlur(14))
aura = ImageChops.subtract(aura, grow(silhouette, OUT))
fill(img, aura.point(lambda v: int(v * .55)), (190, 120, 255, 255))
# ------------------------------------------------ shield: gold rim + bevel + deep field
fill(img, sm, grad((255, 238, 150, 255), (205, 120, 20, 255), angle=100))
bevel_hi = ImageChops.subtract(sm, shrink(sm, 10))
fill(img, ImageChops.multiply(bevel_hi, poly([(0, 0), (S, 0), (S, cy - 40), (0, cy + 120)])), (255, 252, 220, 230))
inner = shrink(sm, 46)
fill(img, grow(inner, 9), (120, 60, 10, 255))                    # inner bevel shadow line
fill(img, inner, grad((96, 54, 210, 255), (20, 10, 52, 255), radial=True, center=(.5, .5), reach=.38))
# rays + glow inside the field
rays = Image.new("L", (S, S), 0); d = ImageDraw.Draw(rays)
for k in range(12):
    a = math.radians(k * 30 + 10); a2 = a + math.radians(10)
    d.polygon([(cx, cy - 60), (cx + math.cos(a) * 700, cy - 60 + math.sin(a) * 700), (cx + math.cos(a2) * 700, cy - 60 + math.sin(a2) * 700)], fill=45)
fill(img, ImageChops.multiply(rays, inner), (200, 170, 255, 255))
glow = Image.new("L", (S, S), 0); ImageDraw.Draw(glow).ellipse([cx - 230, cy - 290, cx + 230, cy + 170], fill=170)
fill(img, ImageChops.multiply(glow.filter(ImageFilter.GaussianBlur(90)), inner), (255, 160, 245, 255))
# rock base the crystals grow out of (clipped to the field)
rock = poly([(cx - 250, cy + 300), (cx - 230, cy + 175), (cx - 140, cy + 120), (cx - 30, cy + 140), (cx + 60, cy + 105),
             (cx + 170, cy + 130), (cx + 245, cy + 190), (cx + 260, cy + 300)])
rock = ImageChops.multiply(rock, inner)
fill(img, rock, grad((92, 78, 120, 255), (38, 30, 56, 255), angle=90))
rd = ImageDraw.Draw(img)
for (a, b) in (((cx - 140, cy + 122), (cx - 95, cy + 190)), ((cx + 60, cy + 107), (cx + 20, cy + 175)), ((cx + 170, cy + 132), (cx + 205, cy + 200))):
    rd.line([a, b], fill=(24, 16, 40, 255), width=8)
# rivets on the 6 corners of the rim
for (x, y) in shield:
    vx, vy = cx - x, cy - y; l = math.hypot(vx, vy); x2, y2 = x + vx / l * 26, y + vy / l * 26
    ImageDraw.Draw(img).ellipse([x2 - 14, y2 - 14, x2 + 14, y2 + 14], fill=DARK)
    ImageDraw.Draw(img).ellipse([x2 - 9, y2 - 9, x2 + 9, y2 + 9], fill=(255, 245, 190, 255))
# ------------------------------------------------ pickaxe (on top of the shield, behind the crystals)
fill(img, grow(ImageChops.lighter(hm, km), 14), DARK)
fill(img, hm, grad((170, 100, 50, 255), (100, 52, 24, 255), angle=40))
fill(img, km, grad((255, 246, 175, 255), (226, 140, 18, 255), angle=110))
hl = rot([(pc[0] - 280, pc[1] - 246), (pc[0] - 175, pc[1] - 312), (pc[0], pc[1] - 342), (pc[0] + 40, pc[1] - 336), (pc[0] - 165, pc[1] - 296)], ang, pc)
fill(img, poly(hl), (255, 255, 235, 200))
# ------------------------------------------------ crystals
for body, light, dark in crys:
    m = poly(body)
    fill(img, grow(m, 14), DARK)
    fill(img, m, grad(light, dark, angle=105))
    top, bot = body[1], body[4]
    fill(img, poly([top, body[2], body[3], bot]), (40, 0, 90, 80))                       # shaded right half
    fill(img, poly([top, body[0], (body[0][0] * .55 + top[0] * .45, body[0][1] * .55 + top[1] * .45)]), (255, 255, 255, 150))
    d = ImageDraw.Draw(img)
    d.line([top, bot], fill=(255, 255, 255, 110), width=7)
    sx, sy = body[0][0] * .72 + top[0] * .28, body[0][1] * .72 + top[1] * .28
    d.line([(sx + 16, sy + 34), (sx + 16, sy + 34 + (body[5][1] - body[0][1]) * .5)], fill=(255, 255, 255, 170), width=13)
# ------------------------------------------------ sparkles
def star(x, y, r, col):
    pts = []
    for k in range(8):
        a = math.radians(k * 45 - 90); rr = r if k % 2 == 0 else r * .28
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    m = poly(pts); fill(img, grow(m, 9), DARK); fill(img, m, col)
star(cx + 205, cy - 330, 66, (255, 240, 140, 255))
star(cx + 270, cy - 175, 34, (255, 255, 255, 255))
star(cx - 255, cy + 250, 38, (200, 245, 255, 255))
# crop to content (keep square, small margin) and export
bbox = img.getbbox(); m = 18
side = max(bbox[2] - bbox[0], bbox[3] - bbox[1]) + 2 * m
ox = (bbox[0] + bbox[2]) // 2 - side // 2; oy = (bbox[1] + bbox[3]) // 2 - side // 2
canvas = Image.new("RGBA", (side, side), CLEAR); canvas.alpha_composite(img, (-ox, -oy))
canvas.save("emblem_full.png")
canvas.resize((1024, 1024), Image.LANCZOS).save("emblem_1024.png")
canvas.resize((512, 512), Image.LANCZOS).save("emblem_512.png")
ic = canvas.resize((64, 64), Image.LANCZOS); ic.save("emblem_64.png")
# previews on dark + light backgrounds like the server list
pv = Image.new("RGBA", (64 * 4 * 2 + 40, 64 * 4 + 20), (30, 30, 34, 255))
pv.alpha_composite(ic.resize((256, 256), Image.NEAREST), (10, 10))
light = Image.new("RGBA", (256, 256), (120, 120, 120, 255)); light.alpha_composite(ic.resize((256, 256), Image.NEAREST))
pv.alpha_composite(light, (286, 10)); pv.save("emblem_preview.png")
