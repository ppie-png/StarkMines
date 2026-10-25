"""Lift control panel (3-row chest background, 176 x 168) + lamp / blank item textures.
Slots used by StarkElevator:  UP = 3,4,5 · lamps = 11..15 · DOWN = 21,22,23 · everything else stays empty."""
from PIL import Image, ImageDraw
import random
W, H = 176, 168
def lerp(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))
GLYPH = {  # 5x7 pixel letters
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "W": ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    "N": ["X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "I": ["XXX", ".X.", ".X.", ".X.", ".X.", ".X.", "XXX"],
    "F": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
}
def text(px, s, x, y, col, shadow=None):
    cx = x
    for ch in s:
        if ch == " ": cx += 3; continue
        g = GLYPH[ch]
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == "X":
                    if shadow: px[cx + i + 1, y + j + 1] = shadow
                    px[cx + i, y + j] = col
        cx += len(g[0]) + 1
def text_w(s): return sum((3 if c == " " else len(GLYPH[c][0]) + 1) for c in s) - 1
def panel():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); px = im.load(); rng = random.Random(4)
    # body: dark brushed steel with a gold frame
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=6, fill=(26, 28, 36, 252))
    for y in range(2, H - 2):
        for x in range(2, W - 2):
            if px[x, y][3]:
                n = rng.randint(-3, 3) + (2 if (y // 2) % 2 else 0)
                c = px[x, y]; px[x, y] = (max(0, c[0] + n), max(0, c[1] + n), max(0, c[2] + n + 1), c[3])
    for i, col in enumerate(((240, 200, 96), (196, 146, 52))):
        d.rounded_rectangle([i, i, W - 1 - i, H - 1 - i], radius=6 - i, outline=col)
    # title bar = display glass
    d.rounded_rectangle([4, 3, W - 5, 15], radius=2, fill=(10, 22, 30, 255), outline=(60, 110, 130, 255))
    for x in range(5, W - 5): px[x, 4] = (40, 90, 110, 255)
    # control plate
    d.rounded_rectangle([4, 16, W - 5, 72], radius=3, fill=(40, 44, 54, 255), outline=(14, 15, 20, 255))
    for x in range(5, W - 5): px[x, 17] = (70, 76, 90, 255)
    # hazard stripes left + right (columns 0-1 and 7-8)
    for (x0, x1) in ((7, 40), (135, 168)):
        d.rectangle([x0, 19, x1, 69], fill=(22, 23, 28, 255))
        for y in range(20, 69):
            for x in range(x0 + 1, x1):
                if ((x + y) // 5) % 2 == 0: px[x, y] = (226, 178, 40, 255)
                else: px[x, y] = (30, 30, 34, 255)
        d.rectangle([x0, 19, x1, 69], outline=(12, 12, 16, 255))
        d.rectangle([x0 + 3, 27, x1 - 3, 61], fill=(32, 35, 44, 255), outline=(12, 12, 16, 255))
        for (rx, ry) in ((x0 + 6, 31), (x1 - 6, 31), (x0 + 6, 57), (x1 - 6, 57)):
            d.ellipse([rx - 2, ry - 2, rx + 2, ry + 2], fill=(110, 116, 132, 255)); px[rx - 1, ry - 1] = (200, 206, 220, 255)
        cx = (x0 + x1) // 2; text(px, "LIFT", cx - text_w("LIFT") // 2, 41, (240, 200, 96, 255), (10, 10, 12, 255))
    # buttons: UP (slots 3-5, row 0) and DOWN (slots 21-23, row 2)
    def button(y0, top, bot, label, up):
        x0, x1 = 7 + 18 * 3, 7 + 18 * 6 - 1
        d.rounded_rectangle([x0 - 1, y0 - 1, x1 + 1, y0 + 18], radius=6, fill=(10, 10, 14, 255))
        for y in range(y0, y0 + 18):
            t = (y - y0) / 17
            d.line([(x0 + 1, y), (x1 - 1, y)], fill=lerp(top, bot, t))
        d.rounded_rectangle([x0, y0, x1, y0 + 17], radius=6, outline=lerp(top, (255, 255, 255, 255), .45))
        for x in range(x0 + 5, x1 - 4): px[x, y0 + 1] = lerp(top, (255, 255, 255, 255), .6)
        # arrow
        ax = x0 + 12; ay = y0 + 9
        for k in range(5):
            yy = ay - 2 + k if up else ay + 2 - k
            for xx in range(ax - k, ax + k + 1): px[xx, yy] = (255, 255, 255, 255)
        for xx in range(ax - 5, ax + 6): px[xx, (ay + 3 if up else ay - 3)] = (0, 0, 0, 0) if False else px[xx, (ay + 3 if up else ay - 3)]
        text(px, label, x0 + 24, y0 + 5, (255, 255, 255, 255), lerp(bot, (0, 0, 0, 255), .5))
    button(17, (110, 240, 230, 255), (24, 150, 160, 255), "UP", True)
    button(53, (255, 140, 214, 255), (170, 50, 140, 255), "DOWN", False)
    # floor indicator: 5 lamp sockets in slots 11..15
    d.rounded_rectangle([7 + 36 - 2, 35, 7 + 18 * 7 + 1, 52], radius=4, fill=(8, 12, 16, 255), outline=(70, 76, 90, 255))
    for c in range(2, 7):
        x = 7 + 18 * c; y = 35
        d.ellipse([x + 1, y + 1, x + 16, y + 16], fill=(20, 24, 30, 255), outline=(52, 58, 72, 255))
    # rails between socket and buttons
    for c in (2, 6):
        for r in (0, 2):
            x = 7 + 18 * c; y = 17 + 18 * r
            d.rounded_rectangle([x + 3, y + 5, x + 14, y + 12], radius=3, fill=(30, 33, 42, 255), outline=(14, 15, 20, 255))
            px[x + 8, y + 8] = (240, 200, 96, 255); px[x + 9, y + 8] = (240, 200, 96, 255)
    # player inventory (still needed by the client): steel slots
    py = 17 + 3 * 18 + 14
    def slot(x, y):
        d.rectangle([x, y, x + 17, y + 17], fill=(52, 58, 72, 255)); d.rectangle([x + 1, y + 1, x + 16, y + 16], fill=(14, 16, 22, 255))
    for r in range(3):
        for c in range(9): slot(7 + c * 18, py + r * 18)
    for c in range(9): slot(7 + c * 18, py + 58)
    return im
def lamp(kind):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im); px = im.load()
    base = {"on": ((120, 255, 150), (20, 150, 70)), "off": ((90, 98, 116), (40, 44, 54)),
            "lock": ((255, 110, 110), (150, 30, 40)), "event": ((255, 220, 110), (170, 110, 20))}[kind]
    for y in range(16):
        for x in range(16):
            dd = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** .5
            if dd <= 6.8:
                t = min(1, dd / 6.8)
                c = lerp(base[0], base[1], t ** 1.3); px[x, y] = c + (255,)
            elif dd <= 7.6: px[x, y] = (12, 12, 16, 255)
    px[5, 4] = px[6, 4] = px[5, 5] = (255, 255, 255, 230)
    if kind == "lock":
        for (x, y) in ((6, 4), (6, 5), (6, 6), (9, 4), (9, 5), (9, 6), (7, 3), (8, 3)): px[x, y] = (60, 12, 18, 255)
        d.rectangle([5, 7, 10, 11], fill=(60, 12, 18, 255)); px[7, 9] = px[8, 9] = (255, 200, 200, 255)
    if kind == "on":
        im2 = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); im2.alpha_composite(im); im = im2
    return im
if __name__ == "__main__":
    p = panel(); bg = Image.new("RGBA", p.size, (90, 120, 160, 255)); bg.alpha_composite(p); bg = bg.resize((W * 3, H * 3), Image.NEAREST)
    bg.save("/tmp/claude-0/-home-claude/238afca3-3701-5863-ba16-cef646f4eb7b/scratchpad/elev_prev.png")
    s = Image.new("RGBA", (16 * 4 + 12, 16), (40, 40, 50, 255))
    for i, k in enumerate(("on", "off", "lock", "event")): s.alpha_composite(lamp(k), (i * 20, 0))
    s.resize((s.width * 6, 96), Image.NEAREST).save("/tmp/claude-0/-home-claude/238afca3-3701-5863-ba16-cef646f4eb7b/scratchpad/lamps_prev.png")
