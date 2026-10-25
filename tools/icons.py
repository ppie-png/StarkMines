"""8x8 pixel icons for the gemfall:icons font (scoreboard / tab / holograms)."""
from PIL import Image
PAL = {".": None, "k": (34, 20, 46), "w": (255, 255, 255), "y": (255, 216, 77), "Y": (255, 240, 160), "o": (214, 140, 22),
       "p": (255, 138, 216), "P": (255, 200, 240), "v": (150, 70, 210), "l": (189, 178, 255), "L": (230, 225, 255),
       "c": (155, 246, 255), "C": (90, 180, 230), "g": (120, 230, 120), "G": (60, 170, 70), "s": (200, 205, 215),
       "S": (130, 135, 150), "b": (205, 127, 50), "B": (150, 85, 30), "r": (255, 110, 110), "n": (150, 100, 60),
       # pickaxe tiers: 1 = head, 2 = head highlight, 3 = head shade
       "1": (160, 112, 56), "2": (205, 160, 95), "3": (110, 74, 34),          # wood
       "4": (140, 140, 146), "5": (196, 196, 202), "6": (92, 92, 100),       # stone
       "7": (220, 224, 230), "8": (255, 255, 255), "9": (160, 166, 176),     # iron
       "a": (252, 214, 70), "A": (255, 244, 170), "e": (196, 140, 20),       # gold
       "d": (93, 236, 245), "D": (210, 255, 255), "E": (30, 160, 180),       # diamond
       "m": (255, 150, 230), "M": (255, 255, 255), "q": (160, 110, 255),     # mythic crystal
       "h": (255, 255, 255), "H": (200, 200, 200), "j": (150, 150, 150)}     # neutral (tinted by text colour)
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
 "pick_wood":    ["kkkkkk..", "k22111k.", ".kkkk13k", "...knk3k", "..knk.kk", ".knk....", "knk.....", "kk......"],
 "pick_stone":   ["kkkkkk..", "k55444k.", ".kkkk46k", "...knk6k", "..knk.kk", ".knk....", "knk.....", "kk......"],
 "pick_iron":    ["kkkkkk..", "k88777k.", ".kkkk79k", "...knk9k", "..knk.kk", ".knk....", "knk.....", "kk......"],
 "pick_gold":    ["kkkkkk..", "kAAaaak.", ".kkkkaek", "...knkek", "..knk.kk", ".knk....", "knk.....", "kk......"],
 "pick_diamond": ["kkkkkk..", "kDDdddk.", ".kkkkdEk", "...knkEk", "..knk.kk", ".knk....", "knk.....", "kk......"],
 "pick_mythic":  ["kkkkkkM.", "kMMmmqkM", ".kkkkmqk", "...kqkqk", "..kqk.kk", ".kqk....", "kqk...M.", "kk......"],
 "shield":       ["kkkkkkkk", "khhhhHjk", "khhhhHjk", "khhhhHjk", ".khhHjk.", ".khHHjk.", "..khjk..", "...kk..."],
 "trophy": ["kkkkkkkk", "kYyyyyok", "kyyyyyok", ".kyyyok.", "..kyok..", "...ko...", "..kyyk..", ".kkkkkk."],
}
ORDER = ["coin", "gem", "star", "crown", "signal", "people", "pick", "clock", "medal1", "medal2", "medal3", "trophy", "pick_wood", "pick_stone", "pick_iron", "pick_gold", "pick_diamond", "pick_mythic", "shield"]
def render(name):
    im = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    for y, row in enumerate(ICONS[name]):
        for x, ch in enumerate(row[:8]):
            c = PAL.get(ch)
            if c: im.putpixel((x, y), c + (255,))
    return im
