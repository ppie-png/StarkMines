"""Builds the Stark Network resource pack from code (textures are generated, not hand-painted).
python3 tools/build_pack.py  ->  pack/ (sources) + dist/StarkMines-pack.zip + dist/sha1.txt

Contents
  stark:facet_rect / facet_tri  crystal facet panels (purple)        - used by the Maw Crystal (item_display panels)
  stark:facet_rect_core / _tri_core  bright inner facets
  stark:trim                    polished gold bar                     - crystal rings
  font stark:gui                GUI backgrounds + pixel-exact spaces  - custom chest menus (see docs/GUI.md)
"""
import json, os, math, random, shutil, zipfile, hashlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "pack")
A = os.path.join(P, "assets")

def w(path, data):
    path = os.path.join(P, path); os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, (dict, list)): data = json.dumps(data, indent=2, ensure_ascii=False)
    open(path, "w", encoding="utf-8").write(data)

def lerp(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))

# ------------------------------------------------------------------ crystal facet textures (64x64)
PALETTES = {
    "": dict(lo=(88, 40, 160, 190), hi=(222, 168, 255, 160), edge=(236, 214, 255, 120), glint=(255, 255, 255, 220)),
    "_core": dict(lo=(255, 170, 235, 245), hi=(255, 246, 255, 255), edge=(255, 236, 252, 170), glint=(255, 255, 255, 255)),
}
def facet(shape, pal, seed):
    S = 64; rng = random.Random(seed)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); px = im.load()
    def inside(x, y):
        if shape == "rect": return True
        # triangle: base along the bottom row, apex at the top centre
        h = (S - 1 - y) / (S - 1)
        half = (1 - h) * S / 2
        return abs(x + .5 - S / 2) <= half
    for y in range(S):
        for x in range(S):
            if not inside(x, y): continue
            t = 1 - y / (S - 1)                                   # 0 bottom -> 1 top
            c = lerp(pal["lo"], pal["hi"], t ** 1.2)
            # soft vertical light streaks inside the crystal
            s = .5 + .5 * math.sin(x * .21 + 1.3) * math.sin(x * .07 + y * .02)
            c = lerp(c, pal["hi"], .25 * s)
            px[x, y] = c
    # soft facet edges: a thin highlight blended into the body (no hard outline -> no "sketch" look)
    edge = pal["edge"]
    for y in range(S):
        for x in range(S):
            if not px[x, y][3]: continue
            if shape == "rect": dist = min(x, y, S - 1 - x, S - 1 - y)
            else:
                h = (S - 1 - y) / (S - 1); half = (1 - h) * S / 2
                dist = min(S - 1 - y, (half - abs(x + .5 - S / 2)) * .9)
            if dist < 2.5:
                k = (1 - dist / 2.5) * edge[3] / 255
                px[x, y] = lerp(px[x, y], edge[:3] + (max(px[x, y][3], edge[3]),), k * .8)
    # diagonal glints + sparkles
    for k in range(2):
        x0 = rng.randint(10, 40); y0 = rng.randint(14, 50)
        for i in range(rng.randint(8, 14)):
            x, y = x0 + i, y0 - i
            if 0 <= x < S and 0 <= y < S and inside(x, y) and px[x, y][3]:
                px[x, y] = lerp(px[x, y], pal["glint"], .7)
    for k in range(6):
        x, y = rng.randint(4, S - 5), rng.randint(4, S - 5)
        if inside(x, y) and px[x, y][3]:
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                if inside(x + dx, y + dy): px[x + dx, y + dy] = pal["glint"] if (dx, dy) == (0, 0) else lerp(px[x + dx, y + dy], pal["glint"], .5)
    return im

def gold_trim():
    im = Image.new("RGBA", (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16):
            t = abs(y - 5.5) / 10.5
            px[x, y] = lerp((255, 246, 190, 255), (196, 120, 22, 255), min(1, t * 1.4))
    for x in range(0, 16, 5): px[x, 4] = (255, 255, 255, 255)
    return im

def plane_model(tex):
    return {"textures": {"0": tex, "particle": tex},
            "elements": [{"from": [0, 0, 8], "to": [16, 16, 8], "shade": False, "light_emission": 15,
                          "faces": {"north": {"uv": [0, 0, 16, 16], "texture": "#0"},
                                    "south": {"uv": [0, 0, 16, 16], "texture": "#0"}}}]}
def cube_model(tex):
    f = {k: {"uv": [0, 0, 16, 16], "texture": "#0"} for k in ("north", "south", "east", "west", "up", "down")}
    return {"textures": {"0": tex, "particle": tex},
            "elements": [{"from": [0, 0, 0], "to": [16, 16, 16], "shade": False, "light_emission": 15, "faces": f}]}

def item_def(name):
    w(f"assets/stark/items/{name}.json", {"model": {"type": "minecraft:model", "model": f"stark:item/{name}"}})

# ------------------------------------------------------------------ GUI backgrounds (chest, 176 wide)
GUI = {"bg": (17, 20, 30, 252), "panel": (27, 31, 46, 255), "rim1": (155, 246, 255, 255), "rim2": (189, 178, 255, 255),
       "slot": (12, 14, 22, 255), "slotrim": (54, 60, 84, 255), "text": (230, 237, 247, 255)}
def gui_background(rows):
    """6-row chest = 222 px tall (rows*18 + 17 top + 97 player inventory part + 14)"""
    W = 176; H = 17 + rows * 18 + 14 + 83
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=6, fill=GUI["bg"])
    # gradient rim (cyan -> lavender, left to right)
    for x in range(W):
        c = lerp(GUI["rim1"], GUI["rim2"], x / (W - 1))
        for y in (0, 1): im.putpixel((x, y), c)
        for y in (H - 2, H - 1): im.putpixel((x, y), lerp(c, (0, 0, 0, 255), .35))
    for y in range(H):
        for x in (0, 1, W - 2, W - 1):
            im.putpixel((x, y), lerp(lerp(GUI["rim1"], GUI["rim2"], x / (W - 1)), (0, 0, 0, 255), .25 * y / H))
    # title bar
    d.rectangle([3, 3, W - 4, 15], fill=(36, 41, 61, 255))
    # menu slot area
    top = 17
    d.rounded_rectangle([5, top - 1, W - 6, top + rows * 18 + 1], radius=3, fill=GUI["panel"])
    for r in range(rows):
        for c in range(9):
            x, y = 7 + c * 18, top + r * 18
            d.rectangle([x, y, x + 17, y + 17], fill=GUI["slotrim"])
            d.rectangle([x + 1, y + 1, x + 16, y + 16], fill=GUI["slot"])
    # player inventory label line + slots
    py = top + rows * 18 + 14
    for x in range(8, W - 8):
        im.putpixel((x, py - 4), lerp((60, 66, 92, 255), (40, 44, 64, 255), abs(x - W / 2) / (W / 2)))
    for r in range(3):
        for c in range(9):
            x, y = 7 + c * 18, py + r * 18
            d.rectangle([x, y, x + 17, y + 17], fill=GUI["slotrim"]); d.rectangle([x + 1, y + 1, x + 16, y + 16], fill=GUI["slot"])
    for c in range(9):
        x, y = 7 + c * 18, py + 58
        d.rectangle([x, y, x + 17, y + 17], fill=GUI["slotrim"]); d.rectangle([x + 1, y + 1, x + 16, y + 16], fill=GUI["slot"])
    return im

def ring_tri(invert=False):
    """triangle (base bottom, apex top-centre) carrying Saturn-like ring bands along v"""
    S = 64; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); px = im.load(); rng = random.Random(5)
    streak = [rng.uniform(-1, 1) for _ in range(S)]
    for y in range(S):
        v = (S - 1 - y) / (S - 1)                 # 0 at base, 1 at apex
        r = 1 - v if invert else v                # r = 0 inner edge ... 1 outer edge
        half = (1 - v) * S / 2 + 1
        for x in range(S):
            if abs(x + .5 - S / 2) > half: continue
            if r < .06: c = (255, 236, 150, 255)                                   # inner gold edge
            elif r < .30: c = (205, 175, 255, 150 + int(30 * streak[y]))           # lavender band
            elif r < .36: c = (120, 90, 200, 40)                                   # cassini gap
            elif r < .80: t = (r - .36) / .44; c = (int(255 - 40 * t), int(190 - 20 * t), 255, int(135 - 45 * t + 25 * streak[y]))
            elif r < .94: c = (255, 205, 245, 70)
            else: c = (255, 230, 140, 230)                                          # outer gold edge
            px[x, y] = c
    return im
def ring_disc(S=512):
    """whole Saturn band on one plane: soft radial bands + clumps/sparkles that vary with the angle so the spin is visible"""
    rng = random.Random(11); im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); px = im.load()
    RIN = 7.6 / 12.6
    clumps = [(rng.uniform(0, 2 * math.pi), rng.uniform(.25, .6), rng.uniform(.62, .98)) for _ in range(7)]
    def ang_mod(a, r):
        m = .78 + .12 * math.sin(3 * a + 1.1) + .08 * math.sin(7 * a + r * 9)
        for (a0, w, rc) in clumps:
            da = (a - a0 + math.pi) % (2 * math.pi) - math.pi
            m += .95 * math.exp(-(da / w) ** 2) * math.exp(-((r - rc) / .13) ** 2)
        return m
    def band(t):
        """t = 0 inner edge .. 1 outer edge -> (rgb, alpha)"""
        def sm(a, b, x): return max(0, min(1, (x - a) / (b - a)))
        a = 0
        a += .95 * math.exp(-((t - .015) / .02) ** 2)                        # inner gold rim
        a += .62 * sm(.04, .09, t) * (1 - sm(.30, .34, t))                   # inner band
        a += .12 * sm(.34, .36, t) * (1 - sm(.39, .41, t))                   # cassini gap (faint)
        a += .55 * sm(.41, .46, t) * (1 - sm(.80, .86, t)) * (.85 + .15 * math.sin(t * 60))
        a += .28 * sm(.86, .88, t) * (1 - sm(.95, .97, t))                   # faint outer band
        a += .85 * math.exp(-((t - .985) / .018) ** 2)                       # outer gold rim
        gold = (255, 214, 110); lav = (178, 132, 255); pink = (255, 150, 230)
        if t < .04 or t > .955: c = gold
        elif t < .36: c = lerp(lav, pink, t / .36)
        else: c = lerp(pink, lav, (t - .36) / .6)
        return c, min(1, a)
    for y in range(S):
        for x in range(S):
            dx, dy = (x + .5) / S * 2 - 1, (y + .5) / S * 2 - 1
            r = math.hypot(dx, dy)
            if r > 1 or r < RIN - .01: continue
            t = (r - RIN) / (1 - RIN)
            c, a = band(max(0, min(1, t)))
            ang = math.atan2(dy, dx)
            m = ang_mod(ang, t) if .03 < t < .96 else 1
            a = a * min(1.5, m) * (.92 + .08 * rng.random())
            c = lerp(c, (255, 250, 255), min(1, max(0, m - .95) * 1.3))
            if a > .003: px[x, y] = c + (int(255 * min(1, a) * .9),)
    # sparkles: bright 4-point stars, denser inside the clumps
    for _ in range(140):
        a0, w, rc = rng.choice(clumps) if rng.random() < .6 else (rng.uniform(0, 2 * math.pi), 3, rng.uniform(.05, .95))
        ang = a0 + rng.gauss(0, w * .6); t = min(.95, max(.05, rc + rng.gauss(0, .06)))
        r = RIN + t * (1 - RIN)
        cx, cy = int((math.cos(ang) * r + 1) / 2 * S), int((math.sin(ang) * r + 1) / 2 * S)
        L = rng.choice((1, 2, 2, 3))
        for dx, dy in [(0, 0)] + [(i, 0) for i in range(-L, L + 1)] + [(0, i) for i in range(-L, L + 1)]:
            X, Y = cx + dx, cy + dy
            if 0 <= X < S and 0 <= Y < S:
                k = 1 - (abs(dx) + abs(dy)) / (L + 1)
                o = px[X, Y]; px[X, Y] = lerp(o if o[3] else (255, 255, 255, 0), (255, 255, 255, 255), k)
    return im
def glow_sprite():
    S = 64; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); px = im.load()
    for y in range(S):
        for x in range(S):
            d = math.hypot(x + .5 - S / 2, y + .5 - S / 2) / (S / 2)
            if d >= 1: continue
            a = (1 - d) ** 2.2
            c = lerp((255, 245, 255), (200, 120, 255), min(1, d * 1.4))
            px[x, y] = (c[0], c[1], c[2], int(200 * a))
    return im
def emblem_glyph(size):
    src = os.path.join(ROOT, "branding", "emblem_512.png")
    return Image.open(src).convert("RGBA").resize((size, size), Image.LANCZOS)

def build():
    if os.path.isdir(P): shutil.rmtree(P)
    os.makedirs(A, exist_ok=True)
    w("pack.mcmeta", {"pack": {"description": [{"text": "◆ GemFall", "color": "#FFC6FF", "bold": True},
                                               {"text": "\nCrystals, menus & models", "color": "#BDB2FF"}],
                               "min_format": [97, 0], "max_format": [97, 1]}})
    # crystal textures + models
    tdir = os.path.join(A, "stark/textures/item"); os.makedirs(tdir, exist_ok=True)
    for suf, pal in PALETTES.items():
        facet("rect", pal, 3).save(os.path.join(tdir, f"facet_rect{suf}.png"))
        facet("tri", pal, 7).save(os.path.join(tdir, f"facet_tri{suf}.png"))
        for shape in ("rect", "tri"):
            name = f"facet_{shape}{suf}"
            w(f"assets/stark/models/item/{name}.json", plane_model(f"stark:item/{name}")); item_def(name)
    gold_trim().save(os.path.join(tdir, "trim.png"))
    ring_tri(False).save(os.path.join(tdir, "ring_tri.png")); ring_tri(True).save(os.path.join(tdir, "ring_tri_inv.png"))
    glow_sprite().save(os.path.join(tdir, "glow.png"))
    ring_disc().save(os.path.join(tdir, "ring_disc.png"))
    for name in ("ring_tri", "ring_tri_inv", "glow", "ring_disc"):
        w(f"assets/stark/models/item/{name}.json", plane_model(f"stark:item/{name}")); item_def(name)
    # GemFall logo glyphs (font gemfall:icons): \uE100 big (tab header), \uE101 small (inline, scoreboard)
    idir = os.path.join(A, "gemfall/textures/font"); os.makedirs(idir, exist_ok=True)
    emblem_glyph(128).save(os.path.join(idir, "emblem_big.png")); emblem_glyph(64).save(os.path.join(idir, "emblem_small.png"))
    import sys as _s; _s.path.insert(0, os.path.join(ROOT, "tools")); import icons as _ic
    strip = Image.new("RGBA", (8 * len(_ic.ORDER), 8), (0, 0, 0, 0))
    for i, n in enumerate(_ic.ORDER): strip.alpha_composite(_ic.render(n), (8 * i, 0))
    strip.save(os.path.join(idir, "icons8.png"))
    ICON_CHARS = "".join(chr(0xE110 + i) for i in range(len(_ic.ORDER)))
    w("assets/gemfall/font/icons.json", {"providers": [
        {"type": "bitmap", "file": "gemfall:font/icons8.png", "ascent": 7, "height": 8, "chars": [ICON_CHARS]},
        {"type": "bitmap", "file": "gemfall:font/emblem_big.png", "ascent": 8, "height": 36, "chars": ["\uE100"]},
        {"type": "bitmap", "file": "gemfall:font/emblem_small.png", "ascent": 8, "height": 9, "chars": ["\uE101"]}]})
    w("assets/stark/models/item/trim.json", cube_model("stark:item/trim")); item_def("trim")
    # GUI font: backgrounds + spaces
    gdir = os.path.join(A, "stark/textures/font/gui"); os.makedirs(gdir, exist_ok=True)
    gui_background(6).save(os.path.join(gdir, "panel_6.png"))
    gui_background(3).save(os.path.join(gdir, "panel_3.png"))
    spaces = {"": -1, "": -2, "": -4, "": -8, "": -16, "": -32, "": -64, "": -128,
              "": 1, "": 2, "": 4, "": 8, "": 16, "": 32, "": 64, "": 128}
    h6 = gui_background(6).size[1]; h3 = gui_background(3).size[1]
    w("assets/stark/font/gui.json", {"providers": [
        {"type": "space", "advances": spaces},
        {"type": "bitmap", "file": "stark:font/gui/panel_6.png", "ascent": 13, "height": h6, "chars": [""]},
        {"type": "bitmap", "file": "stark:font/gui/panel_3.png", "ascent": 13, "height": h3, "chars": [""]},
    ]})
    shutil.copy(os.path.join(ROOT, "tools", "pack.png"), os.path.join(P, "pack.png")) if os.path.exists(os.path.join(ROOT, "tools", "pack.png")) else None
    # zip (deterministic order + timestamps so the sha1 only changes when content changes)
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    zp = os.path.join(ROOT, "dist", "StarkMines-pack.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in sorted(os.walk(P)):
            dirs.sort()
            for f in sorted(files):
                full = os.path.join(base, f); arc = os.path.relpath(full, P).replace(os.sep, "/")
                zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, open(full, "rb").read())
    sha = hashlib.sha1(open(zp, "rb").read()).hexdigest()
    open(os.path.join(ROOT, "dist", "sha1.txt"), "w").write(sha + "\n")
    print(zp, os.path.getsize(zp), sha)

if __name__ == "__main__":
    build()
