"""8x8 pixel icons for the gemfall:icons font (scoreboard / tab / holograms)."""
from PIL import Image
PAL = {".": None, "k": (34, 20, 46), "w": (255, 255, 255), "y": (255, 216, 77), "Y": (255, 240, 160), "o": (214, 140, 22),
       "p": (255, 138, 216), "P": (255, 200, 240), "v": (150, 70, 210), "l": (189, 178, 255), "L": (230, 225, 255),
       "c": (155, 246, 255), "C": (90, 180, 230), "g": (120, 230, 120), "G": (60, 170, 70), "s": (200, 205, 215),
       "S": (130, 135, 150), "b": (205, 127, 50), "B": (150, 85, 30), "r": (255, 110, 110), "n": (150, 100, 60)}
ICONS = {
 "coin": ["..kkkk..", ".kyYYyk.", "kyYyyoyk", "kyYyyoyk", "kyyyyoyk", "kyyoooyk", ".kyyyyk.", "..kkkk.."],
 "gem":  ["..kkkk..", ".kPPpvk.", "kPPpppvk", "kkkkkkkk", ".kppppk.", "..kpvk..", "...kk...", "........"],
 "star": ["...kk...", "..kLlk..", "kkkLlkkk", "kLLLllLk", ".kLlllk.", ".kllllk.", "kllkkllk", "kkk..kkk"],
 "crown": ["........", "k..kk..k", "kYkyykYk", "kyyyyyyk", "kyrypyrk", "kyyyyyyk", "kkkkkkkk", "........"],
 "signal": ["......kk", "......gk", "....kkgk", "....gkgk", "..kkgkgk", "..gkgkgk", "kkgkgkgk", "gkgkgkgk"],
 "people": ["..kkkk..", ".kcccck.", ".kcccck.", "..kkkk..", ".kkcckk.", "kcccccck", "kcccccck", "kkkkkkkk"],
 "pick": ["kkkkkk..", "kccccCk.", ".kkkkcCk", "...knkCk", "..knk.kk", ".knk....", "knk.....", "kk......"],
 "clock": ["..kkkk..", ".klllLk.", "klllkllk", "kllkklLk", "klllllLk", "kllllllk", ".kllllk.", "..kkkk.."],
 "medal1": ["kr...rk.", ".kr.rk..", "..kkk...", ".kYyyk..", "kYyyyyk.", "kyyoyyk.", ".kyyyk..", "..kkk..."],
 "medal2": ["kc...ck.", ".kc.ck..", "..kkk...", ".kssSk..", "kssssSk.", "ksssSSk.", ".kSSSk..", "..kkk..."],
 "medal3": ["kg...gk.", ".kg.gk..", "..kkk...", ".kbbBk..", "kbbbbBk.", "kbbbBBk.", ".kBBBk..", "..kkk..."],
 "trophy": ["kkkkkkkk", "kYyyyyok", "kyyyyyok", ".kyyyok.", "..kyok..", "...ko...", "..kyyk..", ".kkkkkk."],
}
ORDER = ["coin", "gem", "star", "crown", "signal", "people", "pick", "clock", "medal1", "medal2", "medal3", "trophy"]
def render(name):
    im = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    for y, row in enumerate(ICONS[name]):
        for x, ch in enumerate(row[:8]):
            c = PAL.get(ch)
            if c: im.putpixel((x, y), c + (255,))
    return im
