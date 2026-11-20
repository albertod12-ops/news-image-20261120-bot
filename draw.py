#!/usr/bin/env python3
"""news-image-20261120 v3: 36 stories, newspaper front page, same frozen v21 design as 19 Nov.
Draws entry.png (1024x1024, deterministic) from world.geo.json only.
v3: densified art for cards 1, 2, 4, 7, 9, 10, 11, 12, 13 (user 22:21 WIB: v2 still
worse than our 19 Nov entry) — every art box is now a full layered scene like 19 Nov
v39 (sky + midground + foreground, several objects, _skyline with lit windows),
instead of 1-2 small elements on a flat background. Layout/headlines/decks
unchanged; the art_text scrim sits on top of the dense art, as in 19 Nov.
Design baseline (user-approved 2026-11-20): boxed 1px INK cards, LiberationSerif-Bold
headlines + LiberationSerif decks, 68px Times masthead, stats/timeline/map/date-check
geometry as in news-image-20261119 v39. CONTENT ONLY changed for Friday 20 Nov 2026.
NOTE: the first draw.py run right after an edit can render the pre-edit file
— always verify with 2-3 runs and take the later sha.
Run: python3 draw.py  -> writes entry.png in this directory."""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (250, 246, 235)
INK = (17, 17, 17)
NAVY = (16, 62, 150)
RED = (220, 28, 60)
GOLD = (232, 178, 36)
YELLOW = (255, 210, 31)
GREY = (90, 90, 90)
RULE = (180, 170, 150)
OCEAN = (198, 226, 240)
SAND = (238, 220, 165)

FD = "/usr/share/fonts/truetype/dejavu"
FNOTO = "/usr/share/fonts/truetype/noto"
FLIB = "/usr/share/fonts/truetype/liberation"


def load_font(filename, size, base=FD):
    return ImageFont.truetype(os.path.join(base, filename), size)


# (name, file, size, base) — one table instead of thirty near-identical calls.
_FONT_TABLE = [
    ("F_TITLE", "LiberationSerif-Bold.ttf", 68, FLIB),
    ("F_EYE", "NotoSans-Black.ttf", 13, FNOTO),
    ("F_DECKLINE", "NotoSerif-Italic.ttf", 16, FNOTO),
    ("F_DATE", "NotoSans-Black.ttf", 30, FNOTO),
    ("F_DATE2", "NotoSans-Bold.ttf", 11, FNOTO),
    ("F_TTIME", "NotoSans-Bold.ttf", 12, FNOTO),
    ("F_TTEXT", "NotoSans-Bold.ttf", 10, FNOTO),
    ("F_KICK", "NotoSans-Bold.ttf", 10, FNOTO),
    # smalls kicker: 10px made #9 touch the pill (0.3px gap)
    ("F_KICK_S", "NotoSans-Bold.ttf", 9, FNOTO),
    ("F_PILL", "NotoSans-Bold.ttf", 8, FNOTO),
    ("F_SRC", "NotoSans-Bold.ttf", 9, FNOTO),
    # the BANNED/CLOSED stamp, big + bold like the user's reference
    ("F_STAMP", "NotoSans-Black.ttf", 12, FNOTO),
    ("F_HEAD", "LiberationSerif-Bold.ttf", 20, FLIB),
    ("F_HEAD_S", "LiberationSerif-Bold.ttf", 16, FLIB),
    ("F_DECK", "LiberationSerif-Regular.ttf", 12, FLIB),
    ("F_DECK_S", "LiberationSerif-Regular.ttf", 11, FLIB),
    ("F_LABEL", "NotoSans-Bold.ttf", 8, FNOTO),
    ("F_PIN", "NotoSans-Bold.ttf", 11, FNOTO),
    ("F_ART", "NotoSans-Black.ttf", 24, FNOTO),
    ("F_ART_S", "NotoSans-Bold.ttf", 12, FNOTO),
    ("F_ART2", "NotoSans-Black.ttf", 17, FNOTO),
    ("F_ART2_S", "NotoSans-Bold.ttf", 11, FNOTO),
    # 2/3 of F_ART (hero 3 label)
    ("F_LBL", "NotoSans-Black.ttf", 16, FNOTO),
    # 2/3 of F_ART_S
    ("F_LBL_S", "NotoSans-Bold.ttf", 9, FNOTO),
    # 2/3 of F_ART2 (small-card labels)
    ("F_LBL2", "NotoSans-Black.ttf", 12, FNOTO),
    # 2/3 of F_ART2_S
    ("F_LBL2_S", "NotoSans-Bold.ttf", 8, FNOTO),
    ("F_ALSO", "NotoSans-Bold.ttf", 11, FNOTO),
    ("F_ALSO_N", "NotoSans-Bold.ttf", 11, FNOTO),
    ("F_SEC", "NotoSans-Black.ttf", 13, FNOTO),
    ("F_STATB", "NotoSerif-Black.ttf", 21, FNOTO),
    ("F_STATC", "NotoSans-Bold.ttf", 10, FNOTO),
    ("F_LEGEND", "NotoSans-Bold.ttf", 10, FNOTO),
    ("F_DATECHK", "NotoSans-Bold.ttf", 11, FNOTO),
    ("F_FOOT", "NotoSans-Bold.ttf", 10, FNOTO),
]
for _fname, _ffile, _fsize, _fbase in _FONT_TABLE:
    globals()[_fname] = load_font(_ffile, _fsize, _fbase)
del _fname, _ffile, _fsize, _fbase, _FONT_TABLE

PILL_COL = {
    "REPORTED": (16, 165, 90),
    "FORECAST": (20, 110, 230),
    "CLAIM": (230, 150, 0),
}

TIMELINE = [
    ("08:00 ODISHA", "Akvan makes landfall"),
    ("MORNING KYIV", "3 bridges hit"),
    ("MIDDAY ANTALYA", "COP31 draft stalls"),
    ("15:00 TOKYO", "Nikkei closes -5%"),
    ("P.M. BRUSSELS", "UK-EU reset agreed"),
    ("P.M. EUROPE", "Strikes in 25 nations"),
    ("FRIDAY IRAQ", "Troops enter base"),
    ("NIGHT ANTALYA", "COP31 talks run late"),
]

# num, region, topic, source, status, headline, deck, art big, art small, art key
FRONT = [
    (1, "ODISHA", "STORM", "IMD", "REPORTED",
     "Cyclone Akvan slams into Odisha",
     "Landfall 8:00–11:20am, gusts to 90 km/h; 3.7 lakh evacuated, 9,300 shelters open.",
     "AKVAN", "3.7 LAKH EVACUATED", "akvan"),
    (2, "KYIV", "WAR", "REUTERS", "REPORTED",
     "Russian missiles strike Kyiv's bridges",
     "Three Dnipro crossings hit; 5–8 killed, 15 hurt; power 'extremely critical'.",
     "KYIV BRIDGES", "3 BRIDGES HIT", "kyiv"),
    (3, "ANTALYA", "CLIMATE", "UNFCCC", "REPORTED",
     "COP31's final day ends in fossil-fuel deadlock",
     "Revised draft drops the phase-out; ministers split as the summit runs late.",
     "COP31", "DRAFT DROPS PHASE-OUT", "cop31"),
    (4, "TOKYO", "MARKETS", "REUTERS", "REPORTED",
     "AI sell-off sinks Nikkei 5%",
     "Taiwan's worst week since 1991; Hong Kong 20% off its high.",
     "NIKKEI -5%", "AI ROUT SPREADS", "selloff"),
    (5, "BRUSSELS", "DEAL", "AP · REUTERS", "REPORTED",
     "UK and EU agree post-Brexit reset",
     "Youth mobility ~100,000 a year; food and emissions links.",
     "UK–EU DEAL", "RESET AGREED", "ukeu"),
    (6, "THE HAGUE", "LAW", "ICJ", "REPORTED",
     "World reacts to Myanmar genocide ruling",
     "First state held liable; capitals and Rohingya groups respond.",
     "MYANMAR GUILTY", "9–6 · FIRST STATE LIABLE", "icj"),
    (7, "PARIS", "LABOUR", "REUTERS", "REPORTED",
     "Cost-of-living strikes sweep Europe",
     "General strike in 25+ nations, youth-led, over living costs.",
     "ON STRIKE", "25+ COUNTRIES", "strike"),
    (8, "BAGHDAD", "SECURITY", "REUTERS", "REPORTED",
     "Iraqi forces move on militia stronghold",
     "Troops enter Jurf al-Sakhar, Kataib Hezbollah's base.",
     "JURF AL-SAKHAR", "MILITIA BASE", "iraq"),
    (9, "GAZA", "WAR", "REUTERS", "REPORTED",
     "Israeli tanks cross Gaza truce line",
     "First ground operation since the ceasefire began.",
     "GAZA LINE", "FIRST SINCE TRUCE", "gaza"),
    (10, "SIBERIA", "DISASTER", "REUTERS", "REPORTED",
     "Russian An-12 crashes in Siberia",
     "19 killed in the cargo-plane crash.",
     "AN-12 DOWN", "19 KILLED", "crash"),
    (11, "COLOMBO", "ECONOMY", "REUTERS", "REPORTED",
     "Sri Lanka raises rates to 9%",
     "First hike in six months; main rate now 9%.",
     "RATE 9%", "FIRST HIKE IN 6 MONTHS", "rates"),
    (12, "CALIFORNIA", "QUAKE", "USGS", "REPORTED",
     "Magnitude 5 quake shakes California",
     "A magnitude 5 tremor in the San Andreas swarm.",
     "QUAKE M5", "SAN ANDREAS SWARM", "quake"),
    (13, "NEW YORK", "POLITICS", "AP", "REPORTED",
     "Mamdani plans to close Rikers Island",
     "The mayor-elect puts the jail's closure on his agenda.",
     "CLOSE RIKERS", "JAIL TO SHUT", "rikers"),
]

# num, city, text
ALSO = [
    (14, "Riyadh", "Saudis intercept missile, five drones"),
    (15, "Berlin", "Ukraine allies meet; Europe ready to talk"),
    (16, "Brussels", "EU to summon Russian envoy over Kyiv"),
    (17, "London", "UK pledges 1,000+ drones, £260m for Kyiv"),
    (18, "Patrapur", "209mm of rain as Akvan makes landfall"),
    (19, "Odisha", "423 rescue teams; 9,300 shelters open"),
    (20, "Gopalpur", "third cyclone on this coast in 24 days"),
    (21, "Paris", "France seeks UN Security Council meeting"),
    (22, "Taipei", "stocks suffer worst week since 1991"),
    (23, "Hong Kong", "shares 20% below their 2026 high"),
    (24, "Tokyo", "SoftBank falls more than 16%"),
    (25, "London", "copper at its lowest since March"),
    (26, "Brussels", "tuition fees still the sticking point"),
    (27, "Nairobi", "Kenya discharges its last Ebola patient"),
    (28, "Washington", "IMF warns debt near 100% of GDP"),
    (29, "Rome", "Italy fines Meta €805m over photo access"),
    (30, "Washington", "FAA ground stop strands 1.5m flyers"),
    (31, "Washington", "879,000 AI chips cleared for China"),
    (32, "Washington", "Senate passes energy-permit bill 62–33"),
    (33, "Washington", "Trump pardons Pete Rose posthumously"),
    (34, "Washington", "US sanctions Comancheros, 'Ndrangheta"),
    (35, "Buenos Aires", "Senate backs disability law, 71–0"),
    (36, "Warsaw", "Poland probes unknown objects; alert lifted"),
]

STATS = [
    ("370,000", "evacuated in Odisha"),
    ("-5%", "Nikkei's fall"),
    ("9%", "Sri Lanka's new rate"),
    ("100k/yr", "UK-EU youth mobility"),
    ("19", "killed in An-12 crash"),
    ("25+", "nations on strike"),
    ("90 km/h", "Akvan's gusts"),
    ("209mm", "rain at Patrapur"),
]

LEGEND = [
    ("REPORTED", "confirmed, with named sources"),
    ("FORECAST", "a landfall, schedule or draft"),
    ("CLAIM", "one side's claim, unverified"),
]

PINS = {
    1: (85.0, 19.3), 2: (30.5, 50.4), 3: (30.7, 36.9), 4: (139.7, 35.7),
    5: (4.4, 50.8), 6: (4.3, 52.1), 7: (2.4, 48.9), 8: (44.2, 32.8),
    9: (34.4, 31.5), 10: (96.0, 60.0), 11: (79.9, 6.9), 12: (-120.0, 36.0),
    13: (-74.0, 40.7),
}
DOTS = {
    14: (46.7, 24.7), 15: (13.4, 52.5), 16: (4.4, 50.8), 17: (-0.1, 51.5),
    18: (84.6, 19.1), 19: (85.8, 20.3), 20: (85.0, 19.3), 21: (2.4, 48.9),
    22: (121.6, 25.0), 23: (114.2, 22.3), 24: (139.7, 35.7), 25: (-0.1, 51.5),
    26: (4.4, 50.8), 27: (36.8, -1.3), 28: (-77.0, 38.9), 29: (12.5, 41.9),
    30: (-77.0, 38.9), 31: (-77.0, 38.9), 32: (-77.0, 38.9),
    33: (-77.0, 38.9), 34: (-77.0, 38.9), 35: (-58.4, -34.6),
    36: (21.0, 52.2),
}

PROBLEMS = []


def wrap(d, text, fnt, width, max_lines=None):
    """Greedy word wrap to `width` px; records a PROBLEM if it overflows max_lines."""
    out = []
    line = ""
    for word in text.split():
        trial = word if not line else line + " " + word
        if d.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    if max_lines is not None and len(out) > max_lines:
        PROBLEMS.append("TRUNCATED (%d lines): %s" % (len(out), text))
        out = out[:max_lines]
    return out


def art_text(img, d, x, y, w, h, big, small, f_big, f_small, dy=0):
    """White bold label inside the art on a dark scrim, bottom-left.
    Draws nothing when both strings are empty — the art already says it.
    dy shifts the whole label up (negative) or down inside the art."""
    if not big and not small:
        return
    big_w = int(d.textlength(big, font=f_big))
    small_w = int(d.textlength(small, font=f_small)) if small else 0
    if max(big_w, small_w) + 22 > w:
        PROBLEMS.append("ART TEXT TOO WIDE: %s / %s" % (big, small))
    label_w = max(big_w, small_w)
    label_h = f_big.size + f_small.size + 10
    scrim = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rounded_rectangle([x + 4, y + h - label_h - 4 + dy,
                          x + 4 + label_w + 12, y + h - 4 + dy],
                         radius=3, fill=(0, 0, 0, 115))
    img.paste(scrim, (0, 0), scrim)
    d.text((x + 10, y + h - label_h + dy), big, font=f_big, fill="white",
           stroke_width=1, stroke_fill=(0, 0, 0))
    if small:
        d.text((x + 10, y + h - label_h + f_big.size + 2 + dy), small,
               font=f_small, fill="white", stroke_width=1,
               stroke_fill=(0, 0, 0))


def _star(d, cx, cy, r_out, r_in, fill="white"):
    """Small 5-point star centred at (cx, cy)."""
    points = []
    for k in range(10):
        radius = r_out if k % 2 == 0 else r_in
        angle = math.radians(-90 + k * 36)
        points.append((cx + radius * math.cos(angle),
                       cy + radius * math.sin(angle)))
    d.polygon(points, fill=fill)


def _skyline(d, w, h, base, col, seed):
    """Night skyline with lit windows, ported from 19 Nov (v3 density).
    Deterministic: seeded Random, so the render is reproducible."""
    import random
    rnd = random.Random(seed)
    x = 0
    while x < w:
        bw = rnd.randint(14, 30)
        bh = rnd.randint(int(h * 0.3), int(h * 0.75))
        d.rectangle([x, base - bh, x + bw, base], fill=col)
        for wy in range(base - bh + 6, base - 4, 10):
            for wx in range(x + 3, x + bw - 3, 7):
                if rnd.random() < 0.5:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 31))
        x += bw + 3


def stamp(img, x, y, text, angle=-15, font=None):
    """Diagonal red rubber-stamp label (the #1 entry's signature device).
    `text` in red bold caps inside a 3px red outline box, drawn on a small
    RGBA tile that is rotated and pasted onto `img` at (x, y). The text is
    centred in the box (anchor "mm")."""
    fnt = font if font is not None else F_SRC
    probe = Image.new("RGBA", (1, 1))
    probe_d = ImageDraw.Draw(probe)
    box = probe_d.textbbox((0, 0), text, font=fnt)
    text_w, text_h = box[2] - box[0], box[3] - box[1]
    pad = 4
    tile_w, tile_h = text_w + pad * 2 + 4, text_h + pad * 2 + 4
    tile = Image.new("RGBA", (tile_w, tile_h), (0, 0, 0, 0))
    tile_d = ImageDraw.Draw(tile)
    tile_d.rectangle([2, 2, tile_w - 3, tile_h - 3],
                     outline=(200, 16, 46, 255), width=3)
    tile_d.text((tile_w / 2, tile_h / 2), text, font=fnt,
                fill=(200, 16, 46, 255), anchor="mm")
    tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(tile, (x, y), tile)

def art_image(key, w, h):
    """Flat-vector picture for one front story, drawn in code."""
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    if key == "akvan":
        # v3: DENSITY like 19 Nov — the whole frame is the storm, not a
        # spiral on plain blue. Storm sky + rain across the full width, a
        # line-art tornado (v3.2), churning sea along the bottom, a coast
        # with lit houses and bending palms. The AKVAN scrim sits on top,
        # bottom-left, like 19 Nov's labels.
        d.rectangle([0, 0, w, h], fill=(10, 58, 138))
        d.rectangle([0, 0, w, 14], fill=(8, 46, 112))
        # storm clouds, top-left and top-right
        for cx0, cy0 in ((6, 2), (330, 0), (356, 6)):
            d.ellipse([cx0, cy0, cx0 + 34, cy0 + 12], fill=(180, 195, 215))
            d.ellipse([cx0 + 12, cy0 - 4, cx0 + 44, cy0 + 8],
                      fill=(200, 212, 228))
        # rain streaks across the width, two slants — kept clear of the
        # funnel zone (x 152-252) so the tornado lines read clean
        for rx in range(6, w, 16):
            if 152 < rx < 252:
                continue
            d.line([rx, 14, rx - 5, 26], fill=(190, 210, 235), width=2)
        for rx in range(14, w, 26):
            if 152 < rx < 252:
                continue
            d.line([rx, 30, rx - 5, 42], fill=(160, 190, 225), width=2)
        # v3.3: the tornado SLIMMED, per the user ("masih terlalu besar
        # pusarannya") — the v3.2 funnel spanned ~half the hero width;
        # now a tall narrow funnel like the reference line-art (spiral
        # disc halved to rx 40, funnel top half-width 34, same 42px
        # drop). Original PIL vector lines in white on the navy storm
        # sky; rain is kept clear of the narrower funnel zone above.
        cx = 200
        # spiral disc: flat concentric ellipses, half the v3.2 width
        for rx, ry in ((40, 10), (30, 8), (19, 5), (8, 3)):
            d.ellipse([cx - rx, 16 - ry, cx + rx, 16 + ry],
                      outline="white", width=2)
        # one spiral sweep across the disc, hinting the rotation
        d.arc([cx - 40, 6, cx + 40, 26], 200, 340,
              fill=(190, 215, 240), width=2)
        # funnel edges: two curves from the disc down to a narrow tip
        edge_l, edge_r = [], []
        for i in range(25):
            t = i / 24
            y = 24 + int(42 * t)
            hw = 34 - int(30 * (t ** 1.3))
            edge_l.append((cx - hw, y))
            edge_r.append((cx + hw, y))
        d.line(edge_l, fill="white", width=2, joint="curve")
        d.line(edge_r, fill="white", width=2, joint="curve")
        # curved horizontal bands inside the funnel, alternating drift
        for by, bhw, bdx in ((30, 30, -2), (37, 26, 2), (44, 22, -2),
                             (51, 17, 2), (57, 13, -1), (62, 9, 1)):
            d.arc([cx + bdx - bhw, by - 3, cx + bdx + bhw, by + 3],
                  0, 180, fill="white", width=2)
        # dust cloud at the funnel's base, straddling the shoreline —
        # kept right of the AKVAN scrim (which ends ~x166) so no puff
        # crosses the "3.7 LAKH EVACUATED" line
        for px0, py0, pw, ph in ((180, 62, 16, 9), (192, 65, 18, 8),
                                 (204, 60, 16, 9), (214, 64, 14, 8)):
            d.ellipse([px0, py0, px0 + pw, py0 + ph],
                      outline=(220, 232, 245), width=2)
        d.ellipse([194, 63, 208, 70], fill=(220, 232, 245))
        # red warning triangle, moved right of the disc (was tucked
        # against the old spiral's upper arm, now in the disc's way)
        d.polygon([(308, 4), (320, 26), (296, 26)], fill=RED,
                  outline=(20, 20, 20))
        d.text((308, 15), "!", font=F_ART2_S, fill=YELLOW, anchor="mm")
        # the coast: shoreline + three lit houses + two bending palms
        d.rectangle([0, 70, w, h], fill=(8, 44, 96))
        d.line([0, 70, w, 70], fill=(220, 230, 240), width=2)
        for hx, hy, hw in ((286, 52, 30), (322, 56, 32), (358, 50, 30)):
            d.rectangle([hx, hy, hx + hw, 70], fill=(240, 230, 210))
            d.polygon([(hx - 2, hy), (hx + hw + 2, hy),
                       (hx + hw // 2, hy - 12)], fill=(180, 60, 40))
            d.rectangle([hx + 5, hy + 6, hx + 11, hy + 12],
                        fill=(255, 210, 31))
            d.rectangle([hx + hw - 11, hy + 6, hx + hw - 5, hy + 12],
                        fill=(255, 210, 31))
        for px in (272, 344):
            d.line([px, 70, px + 4, 52], fill=(60, 40, 20), width=2)
            for ang in (-50, -20, 10):
                ex = px + 4 + int(12 * math.cos(math.radians(ang - 90)))
                ey = 52 + int(12 * math.sin(math.radians(ang - 90)))
                d.line([px + 4, 52, ex, ey], fill=(30, 120, 60), width=2)
        # churning sea: white wave arcs across the whole bottom
        for wx in range(4, w - 10, 16):
            d.arc([wx, 76, wx + 13, 86], 180, 360, fill="white", width=2)
        for wx in range(12, w - 10, 22):
            d.arc([wx, 83, wx + 10, 89], 180, 360, fill=(200, 220, 240),
                  width=2)
    elif key == "kyiv":
        # v3: DENSITY — a night scene filling the whole frame: stars,
        # skyline with lit windows across the back, river with reflections
        # below, three towers + cables, deck with a broken middle span,
        # fire + a big smoke plume, debris and ripples. No empty dark top.
        d.rectangle([0, 0, w, h], fill=(14, 24, 52))
        # stars across the sky
        for sx, sy in ((10, 6), (40, 10), (90, 4), (130, 8), (180, 5),
                       (230, 9), (270, 4), (286, 12), (160, 12), (60, 14)):
            d.ellipse([sx, sy, sx + 2, sy + 2], fill="white")
        # Kyiv skyline across the whole back, lit windows (19 Nov _skyline)
        _skyline(d, w, 52, 46, (38, 58, 96), 7)
        # a gold-domed church in the skyline, right side
        d.rectangle([238, 28, 262, 46], fill=(120, 140, 180))
        d.ellipse([240, 18, 260, 32], fill=GOLD)
        d.line([250, 10, 250, 18], fill=GOLD, width=2)
        # the river, from the deck line down, with reflections
        d.rectangle([0, 46, w, h], fill=(18, 54, 100))
        for ry in (56, 64, 72, 80):
            for rx0, rx1 in ((8, 60), (70, 120), (130, 200), (210, 286)):
                d.line([rx0, ry, rx1, ry], fill=(70, 120, 180), width=1)
        # towers: pale, three of them, sky down into the river
        for tx in (48, 148, 248):
            d.rectangle([tx, 12, tx + 8, 80], fill=(220, 220, 220))
            d.rectangle([tx - 4, 24, tx + 12, 28], fill=(220, 220, 220))
            d.rectangle([tx - 4, 52, tx + 12, 56], fill=(200, 200, 200))
        # cables fanning from each tower top down to the deck
        for cx0, cx1 in ((52, 10), (52, 120), (152, 90), (152, 210),
                         (252, 180), (252, 290)):
            d.line([cx0, 14, cx1, 40], fill=(200, 200, 200), width=2)
        # the deck: gold and thick; the middle span is broken and dropped
        d.rectangle([0, 40, 132, 47], fill=(255, 205, 40))
        d.rectangle([168, 40, w, 47], fill=(255, 205, 40))
        d.polygon([(132, 40), (168, 40), (162, 58), (138, 58)],
                  fill=(120, 30, 30))
        # fire on the broken span: layered burst with flame spikes, and a
        # big smoke plume rising from it (overlapping grey clouds)
        d.ellipse([132, 28, 168, 48], fill=(200, 40, 30))
        d.ellipse([136, 24, 164, 46], fill=(255, 140, 40))
        d.ellipse([142, 30, 160, 44], fill=(255, 220, 80))
        for fx, fy in ((138, 28), (148, 24), (158, 28)):
            d.polygon([(fx - 4, 30), (fx, fy - 10), (fx + 4, 30)],
                      fill=(255, 140, 40))
        d.ellipse([134, 6, 152, 22], fill=(200, 200, 200))
        d.ellipse([146, 0, 164, 16], fill=(220, 220, 220))
        d.ellipse([126, 12, 142, 26], fill=(210, 210, 210))
        # a second, smaller spiked fire on the right span
        d.ellipse([222, 32, 248, 46], fill=(255, 140, 40))
        d.ellipse([228, 37, 242, 44], fill=(255, 220, 80))
        d.polygon([(226, 34), (224, 26), (230, 32)], fill=(255, 140, 40))
        d.polygon([(240, 34), (242, 26), (244, 34)], fill=(255, 140, 40))
        d.ellipse([232, 20, 246, 32], fill=(205, 205, 205))
        # debris in the river under the break + a rescue boat, far right
        d.rectangle([138, 62, 150, 66], fill=(40, 40, 40))
        d.rectangle([152, 66, 160, 69], fill=(40, 40, 40))
        d.polygon([(262, 74), (288, 74), (284, 80), (266, 80)],
                  fill=(255, 210, 31))
        d.rectangle([272, 68, 280, 74], fill=(230, 200, 160))
    elif key == "cop31":
        d.rectangle([0, 0, w, h], fill=(11, 110, 110))
        # THE DRAFT ITSELF: a white document with the two cuts struck through.
        # The document says "draft drops" at a glance; every line of text is
        # centred in the box. The strike lines run through the MIDDLE of each
        # word, not at the bottom edge (there they read as underlines).
        doc_x0, doc_x1, doc_cx = 16, 180, 98
        d.rectangle([doc_x0, 6, doc_x1, 52], fill="white",
                    outline=(120, 110, 95))
        d.text((doc_cx, 10), "COP31 DRAFT", font=F_SRC, fill=(20, 20, 20),
               anchor="ma")
        # each cut line: text, its y, and the strike's x-range, all centred
        cuts = (("FOSSIL FUELS", 27, 60, 136), ("PHASE-OUT", 39, 70, 126))
        for cut_text, cut_y, strike_x0, strike_x1 in cuts:
            d.text((doc_cx, cut_y), cut_text, font=F_ART2_S, fill=RED,
                   anchor="mm")
            d.line([strike_x0, cut_y, strike_x1, cut_y], fill=RED, width=2)
        # diagonal CUT stamp on the document, clear of the centred text
        stamp(img, 140, 6, "CUT")
        # a BIG globe + a thermometer, like the top-1 entry: the planet the
        # deal is about, and the heat it measures. The globe is blue ocean +
        # green continents; the thermometer stands beside it.
        d.ellipse([204, 6, 266, 68], fill=(30, 120, 200),
                  outline=(20, 20, 20), width=2)
        land = ((216, 16, 236, 32), (236, 38, 256, 54), (214, 44, 226, 56))
        for lx0, ly0, lx1, ly1 in land:
            d.ellipse([lx0, ly0, lx1, ly1], fill=(60, 180, 90))
        # thermometer: white tube, red fill rising, round bulb, tick marks
        d.rectangle([274, 8, 284, 58], fill="white", outline=(20, 20, 20))
        d.rectangle([276, 24, 282, 58], fill=(220, 30, 40))
        d.ellipse([270, 56, 290, 76], fill=(220, 30, 40),
                  outline=(20, 20, 20))
        for tick_y in (14, 22, 30, 38, 46, 54):
            d.line([284, tick_y, 289, tick_y], fill=(20, 20, 20), width=1)
    elif key == "icj":
        # the World Court as a temple: pediment, 15 columns, steps.
        # The first 9 columns are paper, the last 6 ink — the 9-6 vote.
        d.rectangle([0, 0, w, h], fill=(226, 218, 196))
        pediment = [(104, 36), (198, 12), (292, 36)]
        d.polygon(pediment, fill=(120, 110, 95))
        col_top, col_bottom, col_w = 40, 74, 7
        for i in range(15):
            col_x = 116 + i * 11
            col_fill = (244, 239, 226) if i < 9 else NAVY
            col_edge = (120, 110, 95) if i < 9 else "white"
            d.rectangle([col_x, col_top, col_x + col_w, col_bottom],
                        fill=col_fill, outline=col_edge)
        # three steps, each wider than the one above it
        step_fill = (240, 234, 220)
        for step_x0, step_y0, step_x1, step_y1 in ((110, 76, 282, 80),
                                                   (104, 80, 288, 84),
                                                   (98, 84, 292, 90)):
            d.rectangle([step_x0, step_y0, step_x1, step_y1], fill=step_fill)
        # red divider between the 9 paper and 6 ink columns (the 9-6 vote)
        d.line([213, 40, 213, 74], fill=(179, 34, 44), width=3)
        # Myanmar flag top left (yellow/green/red + white star), white outline
        flag_bands = (((8, 13), (254, 203, 0)), ((13, 18), (0, 140, 60)),
                      ((18, 24), (220, 40, 40)))
        for (band_y0, band_y1), band_col in flag_bands:
            d.rectangle([12, band_y0, 38, band_y1], fill=band_col)
        d.rectangle([12, 8, 38, 24], outline="white", width=1)
        _star(d, 25, 16, 5, 2)
        # gold scales of justice, left, below the flag (the recognisable object)
        scale_x = 60
        d.line([scale_x, 34, scale_x, 58], fill=GOLD, width=2)
        d.line([44, 38, 76, 38], fill=GOLD, width=2)
        for pan_x in (48, 64):
            d.polygon([(pan_x, 38), (pan_x + 8, 38), (pan_x + 4, 48)],
                      fill=GOLD)
        d.ellipse([56, 58, 64, 64], fill=GOLD)
    elif key == "selloff":
        # v3: DENSITY — a trading floor, not four bars on blank paper.
        # Full grid, six descending bars filling the width, a red trend
        # line above them, a big -5% focal, falling arrows, a ticker tape
        # and a Tokyo skyline silhouette along the bottom.
        d.rectangle([0, 0, w, h], fill=(246, 242, 233))
        for gy in range(0, h, 12):
            d.line([0, gy, w, gy], fill=(205, 205, 215), width=1)
        for gx in range(0, w, 24):
            d.line([gx, 0, gx, h], fill=(220, 220, 228), width=1)
        # Tokyo skyline silhouette along the bottom, behind the bars
        _skyline(d, w, 30, 80, (150, 160, 180), 21)
        # six descending bars, the last two red
        for i, (bx, top) in enumerate(((8, 10), (38, 16), (68, 22),
                                       (98, 28), (128, 34), (158, 40))):
            d.rectangle([bx, top, bx + 24, 62],
                        fill=NAVY if i < 4 else RED)
            d.rectangle([bx + 3, top + 3, bx + 8, top + 6], fill="white")
        # red trend line ABOVE the bars, small arrowhead
        d.line([(6, 6), (186, 34)], fill=RED, width=2)
        d.polygon([(186, 34), (176, 30), (180, 40)], fill=RED)
        # falling arrows between the bars
        for ax, ay in ((34, 44), (94, 50), (154, 56)):
            d.line([ax, ay - 8, ax, ay], fill=RED, width=2)
            d.polygon([(ax - 3, ay - 3), (ax + 3, ay - 3), (ax, ay + 3)],
                      fill=RED)
        # big -5% focal, top-right, on the grid
        d.text((192, 2), "-5%", font=F_ART2, fill=RED, anchor="ra",
               stroke_width=1, stroke_fill="white")
        # ticker tape along the very bottom: small down-triangles
        d.rectangle([0, 72, w, h], fill=(20, 20, 20))
        for tx, tcol in ((10, RED), (56, RED), (102, (30, 140, 80)),
                         (148, RED)):
            d.polygon([(tx - 3, 74), (tx + 3, 74), (tx, 79)], fill=tcol)
    elif key == "ukeu":
        # two flags, one deal: EU stars on the left, the Union Jack's cross
        # on the right, a gold link between them
        d.rectangle([0, 0, w, h], fill=(20, 40, 120))
        for a in range(8):
            sx = 48 + int(30 * math.cos(math.radians(a * 45)))
            sy = 40 + int(26 * math.sin(math.radians(a * 45)))
            _star(d, sx, sy, 4, 2, fill=(255, 210, 31))
        d.rectangle([98, 0, 196, h], fill="white")
        d.rectangle([98, 34, 196, 46], fill=(200, 20, 40))
        d.rectangle([142, 0, 154, h], fill=(200, 20, 40))
        d.line([98, 0, 196, h], fill=(20, 40, 120), width=3)
        d.line([196, 0, 98, h], fill=(20, 40, 120), width=3)
        d.rectangle([90, 34, 106, 46], fill=GOLD)
        d.text((98, 40), "=", font=F_ART2, fill=(20, 20, 20), anchor="mm")
    elif key == "strike":
        # v3: DENSITY — a full street, not three figures on blank sky.
        # Paris facades with windows across the top, six marchers filling
        # the width in stride, the COST OF LIVING banner carried across
        # the top by the front two, placards in hand, road + dashes below.
        d.rectangle([0, 0, w, h], fill=(205, 214, 226))
        # Paris facades behind the march, windows lit
        for fx, fw, fh in ((0, 34, 30), (38, 30, 38), (72, 36, 28),
                           (112, 30, 36), (146, 28, 30), (178, 18, 34)):
            d.rectangle([fx, 40 - fh, fx + fw, 40], fill=(150, 140, 120))
            for wy in range(40 - fh + 5, 36, 10):
                for wx in range(fx + 4, fx + fw - 4, 9):
                    d.rectangle([wx, wy, wx + 4, wy + 5],
                                fill=(255, 220, 130))
            d.polygon([(fx, 40 - fh), (fx + fw, 40 - fh),
                       (fx + fw // 2, 40 - fh - 8)], fill=(120, 60, 50))
        # clouds above the roofs
        d.ellipse([8, 2, 34, 10], fill="white")
        d.ellipse([150, 2, 182, 10], fill="white")
        # the road, full width, with dashes
        d.rectangle([0, 62, w, h], fill=(110, 110, 116))
        d.line([0, 62, w, 62], fill=(60, 60, 65), width=2)
        for dx in range(4, w, 20):
            d.line([dx, 71, dx + 10, 71], fill="white", width=2)
        # the banner, held on poles by the first and last marchers
        d.rectangle([14, 6, 182, 24], fill="white", outline=RED, width=2)
        d.text((98, 15), "COST OF LIVING", font=F_SRC, fill=RED,
               anchor="mm")
        d.line([26, 24, 26, 40], fill=(60, 40, 20), width=2)
        d.line([170, 24, 170, 40], fill=(60, 40, 20), width=2)
        # six marchers, bigger, filling the width, in stride
        skins = [(200, 140, 90), (220, 180, 140), (190, 130, 85),
                 (210, 160, 110), (200, 140, 90), (220, 180, 140)]
        shirts = [(40, 90, 160), (200, 40, 40), (30, 140, 80),
                  (220, 170, 40), (90, 60, 140), (20, 120, 140)]
        for i, x in enumerate((8, 40, 72, 104, 136, 168)):
            d.ellipse([x + 3, 30, x + 15, 42], fill=skins[i])
            d.ellipse([x + 6, 35, x + 8, 37], fill=(20, 20, 20))
            d.ellipse([x + 10, 35, x + 12, 37], fill=(20, 20, 20))
            d.rectangle([x + 2, 42, x + 14, 56], fill=shirts[i])
            d.line([x + 5, 56, x + 1, 68], fill=(20, 20, 20), width=2)
            d.line([x + 9, 56, x + 15, 68], fill=(20, 20, 20), width=2)
            if i == 0:
                d.line([x + 4, 44, 26, 40], fill=skins[i], width=2)
            if i == 5:
                d.line([x + 10, 44, 170, 40], fill=skins[i], width=2)
            if i in (2, 3):
                # middle marchers hold small placards up
                d.line([x + 12, 44, x + 16, 34], fill=(60, 40, 20), width=2)
                d.rectangle([x + 10, 26, x + 24, 36], fill="white",
                            outline=INK)
    elif key == "iraq":
        # desert stronghold: a walled compound with a watchtower, two tanks
        # moving in across the sand
        d.rectangle([0, 0, w, h], fill=(228, 200, 150))
        d.rectangle([20, 30, 176, 62], fill=(190, 160, 110))
        d.rectangle([20, 30, 176, 36], fill=(160, 130, 85))
        d.rectangle([86, 12, 110, 36], fill=(170, 140, 95))
        d.rectangle([92, 18, 104, 24], fill=(60, 40, 20))
        for wx in range(30, 170, 18):
            d.rectangle([wx, 42, wx + 8, 50], fill=(90, 70, 40))
        # two SMALL tanks on the right: full-size tanks at the bottom-left
        # would sit under the art_text scrim and vanish. 32px wide, clear
        # of the scrim (which ends ~x126).
        for tx, ty in ((128, 62), (162, 62)):
            d.rectangle([tx, ty, tx + 32, ty + 8], fill=(70, 90, 60))
            d.rectangle([tx + 8, ty - 5, tx + 22, ty], fill=(70, 90, 60))
            d.line([tx + 22, ty - 2, tx + 34, ty - 2], fill=(40, 50, 35),
                   width=3)
            d.ellipse([tx + 3, ty + 8, tx + 8, ty + 11], fill=(40, 40, 40))
            d.ellipse([tx + 24, ty + 8, tx + 29, ty + 11], fill=(40, 40, 40))
        d.ellipse([150, 8, 170, 20], fill=(240, 230, 200))
        d.ellipse([160, 12, 186, 22], fill=(240, 230, 200))
    elif key == "gaza":
        # v3: DENSITY — a desert scene filling the frame: sun + clouds,
        # layered dunes, a distant wall with watchtower, a dust cloud
        # behind the tracks, and a tank twice as big as v2, crossing the
        # yellow truce dashes painted on the ground.
        d.rectangle([0, 0, w, h], fill=(240, 215, 160))
        # sun, top-right, and clouds
        d.ellipse([168, 4, 188, 24], fill=(255, 220, 80),
                  outline=(230, 180, 60), width=2)
        d.ellipse([8, 6, 34, 14], fill=(250, 240, 220))
        d.ellipse([20, 10, 48, 18], fill=(250, 240, 220))
        d.ellipse([120, 2, 146, 10], fill=(250, 240, 220))
        # distant wall with a watchtower, across the back
        d.rectangle([0, 34, w, 44], fill=(190, 160, 110))
        d.rectangle([0, 34, w, 38], fill=(160, 130, 85))
        d.rectangle([150, 18, 172, 38], fill=(170, 140, 95))
        d.rectangle([156, 23, 166, 29], fill=(60, 40, 20))
        for wx in range(6, w, 20):
            d.rectangle([wx, 40, wx + 8, 46], fill=(90, 70, 40))
        # dunes: two layered bands
        d.polygon([(0, 52), (60, 44), (120, 52), (196, 46), (196, 80),
                   (0, 80)], fill=(222, 190, 130))
        d.polygon([(0, 62), (80, 54), (140, 62), (196, 56), (196, 80),
                   (0, 80)], fill=(205, 172, 112))
        # the yellow truce line, painted on the ground, full width
        for dx in range(0, w, 14):
            d.line([dx, 66, dx + 8, 66], fill=YELLOW, width=4)
        # the tank, bigger: hull, turret, long barrel, six track wheels
        d.rectangle([34, 58, 158, 64], fill=(150, 128, 88))
        d.rectangle([32, 48, 156, 58], fill=(60, 65, 50))
        for wx in (42, 62, 82, 102, 122, 142):
            d.ellipse([wx - 5, 50, wx + 5, 60], fill=(40, 40, 40))
            d.ellipse([wx - 2, 53, wx + 2, 57], fill=(120, 120, 110))
        d.polygon([(40, 36), (150, 36), (158, 42), (158, 48), (40, 48)],
                  fill=(90, 100, 70))
        d.rectangle([62, 24, 108, 36], fill=(90, 100, 70))
        d.rectangle([68, 20, 102, 24], fill=(80, 90, 62))
        d.ellipse([80, 25, 88, 33], fill=(70, 80, 55))
        d.line([76, 20, 73, 8], fill=(50, 55, 40), width=2)
        d.line([108, 27, 168, 27], fill=(50, 55, 40), width=5)
        # dust cloud billowing behind the tracks + exhaust smoke
        d.ellipse([4, 44, 22, 58], fill=(220, 200, 165))
        d.ellipse([12, 38, 30, 52], fill=(230, 210, 175))
        d.ellipse([22, 46, 36, 58], fill=(220, 200, 165))
        d.ellipse([20, 30, 30, 40], fill=(200, 200, 200))
    elif key == "crash":
        # v3.3: redrawn in the style of the user's reference 2 — a blue
        # sky with white clouds, a grey cartoon plane nose-diving
        # diagonally (mirrored to dive right, so the nose and the engine
        # fire stay clear of the AN-12 DOWN scrim at bottom-left), a grey
        # smoke trail from the tail, a small orange fire on one engine,
        # and a green treeline along the bottom. Original PIL vector
        # code; the reference file (watermarked) is not used anywhere.
        d.rectangle([0, 0, w, h], fill=(125, 185, 235))
        d.rectangle([0, 0, w, 8], fill=(150, 200, 240))
        # white clouds across the sky
        for cx0, cy0, cw in ((8, 6, 30), (66, 2, 36), (130, 8, 28),
                             (168, 2, 26), (30, 24, 24), (150, 28, 30)):
            d.ellipse([cx0, cy0, cx0 + cw, cy0 + 10], fill="white")
            d.ellipse([cx0 + 6, cy0 - 3, cx0 + cw - 6, cy0 + 7],
                      fill="white")
        # smoke trail from the tail, growing up-left to the corner
        for ex, ey, er in ((52, 16, 4), (40, 12, 5), (28, 8, 6),
                           (16, 5, 7), (6, 3, 6)):
            d.ellipse([ex - er, ey - er, ex + er, ey + er],
                      fill=(160, 160, 160))
        for ex, ey, er in ((44, 13, 2), (30, 9, 3), (18, 5, 3)):
            d.ellipse([ex - er, ey - er, ex + er, ey + er],
                      fill=(120, 120, 120))
        # the plane, diving nose-down to the right: a THIN light-grey
        # fuselage (so it reads as a plane, not a slab), darker swept
        # wings for contrast, a big blue tail fin, two engines
        d.polygon([(54, 10), (60, 16), (160, 54), (156, 60), (48, 20)],
                  fill=(175, 175, 185))
        d.line([(54, 10), (160, 54)], fill=(110, 110, 120), width=1)
        d.line([(48, 20), (156, 60)], fill=(110, 110, 120), width=1)
        # big blue tail fin, like the reference's
        d.polygon([(48, 14), (36, 0), (56, 4)], fill=(30, 90, 180))
        d.polygon([(100, 30), (126, 12), (134, 20), (108, 40)],
                  fill=(110, 110, 125))
        d.polygon([(110, 44), (134, 60), (126, 64), (102, 48)],
                  fill=(110, 110, 125))
        # windows along the fuselage, then the two engine nacelles
        for ex, ey in ((84, 28), (102, 36), (120, 44), (138, 52)):
            d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(200, 230, 245))
        d.ellipse([116, 44, 126, 52], fill=(90, 90, 100))
        d.ellipse([134, 52, 144, 60], fill=(90, 90, 100))
        # small orange fire on the lower engine, flame spike + yellow core
        d.ellipse([132, 56, 148, 70], fill=(255, 140, 40))
        d.ellipse([136, 59, 145, 66], fill=(255, 220, 80))
        d.polygon([(140, 56), (140, 47), (144, 56)], fill=(255, 140, 40))
        # green ground + treeline along the bottom, and a lamp post
        d.polygon([(0, 68), (60, 62), (120, 68), (196, 62), (196, 80),
                   (0, 80)], fill=(40, 140, 70))
        for tx, tr in ((10, 5), (30, 6), (52, 5), (78, 6), (104, 5),
                       (128, 6), (150, 5), (176, 6)):
            d.ellipse([tx - tr, 62 - tr, tx + tr, 62 + 2], fill=(25, 110, 55))
        d.line([168, 66, 168, 46], fill=(60, 60, 60), width=2)
        d.line([168, 46, 176, 46], fill=(60, 60, 60), width=2)
        d.ellipse([174, 44, 178, 48], fill=(255, 220, 80))
    elif key == "rates":
        # v3: DENSITY — a bank scene, not four bars on blank paper. Full
        # grid, six climbing bars filling the width, a red arrow above
        # them, a big 9% focal, gold coins along the bottom and bank
        # columns rising behind the bars.
        d.rectangle([0, 0, w, h], fill=(245, 240, 228))
        for gy in range(0, h, 12):
            d.line([0, gy, w, gy], fill=(210, 205, 190), width=1)
        for gx in range(0, w, 24):
            d.line([gx, 0, gx, h], fill=(228, 223, 208), width=1)
        # bank columns behind the bars, pediment on top
        d.polygon([(20, 8), (176, 8), (98, 0)], fill=(120, 110, 95))
        for cx in (28, 62, 96, 130, 164):
            d.rectangle([cx, 10, cx + 7, 58], fill=(200, 192, 170),
                        outline=(120, 110, 95))
        # six climbing bars, all navy — the red 9% focal sits on paper
        # above the last bar, never red-on-red
        for i, (bx, top) in enumerate(((8, 40), (38, 34), (68, 28),
                                       (98, 22), (128, 16), (158, 10))):
            d.rectangle([bx, top, bx + 24, 62], fill=NAVY)
            d.rectangle([bx + 3, top + 3, bx + 8, top + 6], fill="white")
        # red arrow ABOVE the bars, ending well clear of the 9% focal
        d.line([(6, 34), (134, 13)], fill=RED, width=2)
        d.polygon([(134, 13), (124, 11), (128, 21)], fill=RED)
        # big 9% focal, top-right, on the grid — v3.1: was drawn at x=192,
        # its ink ending 3px from the art's right edge and reading as
        # clipped; now at x=184, 12px clear of the edge, clear of the arrow
        d.text((184, 0), "9%", font=F_ART2, fill=RED, anchor="ra",
               stroke_width=1, stroke_fill="white")
        # gold coins along the bottom, one stamped Rs (right of the scrim)
        for cx in (14, 44, 74, 104, 134, 164):
            d.ellipse([cx, 66, cx + 12, 78], fill=GOLD,
                      outline=(180, 130, 20), width=1)
            d.ellipse([cx + 3, 69, cx + 9, 75], fill=(255, 220, 80))
        d.text((170, 72), "Rs", font=F_ART2_S, fill=(120, 80, 0),
               anchor="mm")
    elif key == "quake":
        # v3.3: redrawn in the style of the user's reference 1 — an
        # isometric earth block filling the frame: pale sage background,
        # green top surface split by a thick orange zigzag fault crack,
        # two small houses (one tilted, one with a collapsed roof), thin
        # white concentric epicentre rings on the crack, debris, and
        # orange block sides at the bottom. The red seismograph trace
        # stays across the top; the rings are centred right of the QUAKE
        # M5 scrim (bottom-left) so the label stays clear. Original PIL
        # vector code; the reference file is not used anywhere.
        d.rectangle([0, 0, w, h], fill=(205, 220, 200))
        # the seismograph trace on a white strip across the top
        d.rectangle([0, 0, w, 14], fill="white")
        d.line([(2, 7), (16, 7), (22, 2), (28, 12), (34, 7), (52, 7),
                (58, 1), (64, 13), (70, 7), (92, 7), (98, 3), (104, 11),
                (110, 7), (130, 7), (136, 2), (142, 12), (148, 7),
                (170, 7), (176, 4), (182, 10), (188, 7), (194, 7)],
               fill=RED, width=2)
        # the isometric block: green top, orange sides
        d.polygon([(8, 38), (98, 18), (188, 38), (98, 58)],
                  fill=(35, 150, 75))
        d.polygon([(8, 38), (98, 58), (98, 76), (8, 56)],
                  fill=(240, 120, 50))
        d.polygon([(98, 58), (188, 38), (188, 56), (98, 76)],
                  fill=(215, 100, 40))
        # thick orange fault crack zigzagging across the top face,
        # dark-edged ribbon
        crack = [(16, 36), (44, 28), (66, 35), (96, 25), (124, 34),
                 (152, 27), (182, 35)]
        d.line(crack, fill=(180, 60, 20), width=7, joint="curve")
        d.line(crack, fill=(250, 125, 50), width=4, joint="curve")
        # two houses: one tilted left, one with a collapsed roof right
        d.polygon([(28, 30), (52, 26), (52, 40), (28, 44)],
                  fill=(240, 240, 235))
        d.polygon([(26, 30), (54, 26), (40, 18)], fill=(40, 110, 200))
        d.rectangle([34, 32, 38, 38], fill=(255, 180, 90))
        d.rectangle([44, 30, 48, 36], fill=(255, 180, 90))
        d.polygon([(150, 30), (174, 26), (174, 40), (150, 44)],
                  fill=(240, 240, 235))
        d.polygon([(148, 30), (162, 20), (176, 28), (168, 32),
                   (156, 30)], fill=(40, 110, 200))
        d.rectangle([156, 32, 160, 38], fill=(255, 180, 90))
        d.rectangle([166, 30, 170, 36], fill=(255, 180, 90))
        # debris on the top face, clear of the scrim
        d.rectangle([108, 40, 116, 44], fill=(250, 125, 50))
        d.rectangle([136, 42, 142, 45], fill=(40, 110, 200))
        d.rectangle([164, 44, 172, 47], fill=(250, 125, 50))
        d.rectangle([84, 40, 90, 43], fill=(40, 110, 200))
        # thin white epicentre rings centred on the crack, right side —
        # drawn last, like the reference's rings over the whole scene
        for rr in (7, 12, 17, 22):
            d.ellipse([132 - rr, 29 - rr, 132 + rr, 29 + rr],
                      outline="white", width=1)
        d.ellipse([130, 27, 134, 31], fill="white")
    elif key == "rikers":
        # v3: DENSITY — a full cell block, not bars on a grey wall. Brick
        # texture top and bottom, bars across the whole frame, the RIKERS
        # sign, the CLOSED stamp, a barred cell door with a small window,
        # and the island's water strip along the bottom.
        d.rectangle([0, 0, w, h], fill=(150, 155, 165))
        # brick texture, top band and bottom band
        d.rectangle([0, 0, w, 12], fill=(120, 90, 80))
        for bx in range(0, w, 16):
            d.line([bx, 0, bx, 12], fill=(90, 65, 55), width=1)
        d.line([0, 6, w, 6], fill=(90, 65, 55), width=1)
        d.rectangle([0, 68, w, h], fill=(110, 82, 72))
        for bx in range(8, w, 16):
            d.line([bx, 68, bx, 80], fill=(85, 60, 50), width=1)
        d.line([0, 74, w, 74], fill=(85, 60, 50), width=1)
        # bars across the whole frame
        for bx in (10, 32, 54, 76, 98, 120, 142, 164, 186):
            d.rectangle([bx, 12, bx + 8, 68], fill=(40, 42, 48))
        # the RIKERS sign, high on the bars
        d.rectangle([16, 18, 108, 40], fill=NAVY)
        d.text((62, 29), "RIKERS", font=F_ART2, fill="white", anchor="mm")
        # CLOSED stamp, fully inside the frame, top-right
        stamp(img, 122, 4, "CLOSED", angle=-10)
        # a barred cell door with a small window, bottom-right
        d.rectangle([148, 44, 190, 68], fill=(70, 72, 80),
                    outline=(40, 42, 48), width=2)
        d.rectangle([156, 48, 182, 56], fill=(180, 200, 220),
                    outline=(40, 42, 48), width=1)
        d.line([169, 48, 169, 56], fill=(40, 42, 48), width=1)
        d.line([148, 60, 190, 60], fill=(40, 42, 48), width=2)
        d.ellipse([184, 62, 188, 66], fill=GOLD)
        # water strip along the very bottom: Rikers is an island
        d.rectangle([0, 76, w, h], fill=(30, 90, 150))
        for wx in range(4, w, 18):
            d.arc([wx, 76, wx + 10, 80], 180, 360, fill="white", width=1)
    return img

# pixel nudges so clustered pins stay readable (map is small): the pin circle
# moves by (dx, dy) and a thin leader line points back to the true spot.
# Seven pins crowd Europe + the Levant (Kyiv/Antalya/Brussels/The Hague/Paris/
# Gaza/Iraq within ~40x30px), so they are fanned out radially: 6 north-west,
# 7 west, 5 south-west, 2 north-east, 3 south, 9 south, 8 east.
PIN_OFF = {2: (18, -16), 3: (2, 14), 5: (-6, 26), 6: (-28, -18),
           7: (-30, 8), 8: (16, -14), 9: (-18, 20)}


def draw_map(d, x0, y0, mw, mh):
    with open(os.path.join(HERE, "world.geo.json")) as f:
        geo = json.load(f)
    shapes = []
    for feat in geo["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            shapes.append(geom["coordinates"])
        elif geom["type"] == "MultiPolygon":
            shapes.extend(geom["coordinates"])
    for shape in shapes:
        for ring in shape:
            pts = []
            for lon, lat in ring:
                px = (lon + 180.0) / 360.0 * mw
                py = (90.0 - lat) / 180.0 * mh
                pts.append((px, py))
            # filled continents, not dots, like the top entries
            d.polygon([(x0 + px, y0 + py) for px, py in pts],
                      fill=SAND)

    def project(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (90.0 - lat) / 180.0 * mh)

    for n, (lon, lat) in DOTS.items():
        px, py = project(lon, lat)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=NAVY)
    for n, (lon, lat) in PINS.items():
        px, py = project(lon, lat)
        dx, dy = PIN_OFF.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            # leader line from the true spot to the moved pin circle
            d.line([px, py, px + dx, py + dy], fill=RED, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
            px, py = px + dx, py + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline="white")
        label = str(n)
        label_w = d.textlength(label, font=F_PIN)
        d.text((px - label_w / 2, py - 5), label, font=F_PIN, fill="white")


def hero_card(img, d, story, x, y, w):
    """One hero card: 90px art, navy kicker strip with status pill, a
    2-line Times headline and a 2-line serif deck, all inside a 1px ink box
    whose bottom is fixed per row, like the top-1 entry."""
    num, reg, topic, src, status, head, deck, big, small, key = story
    art = art_image(key, w, 90)
    art_d = ImageDraw.Draw(art)
    art_text(art, art_d, 0, 0, w, 90, big, small, F_LBL, F_LBL_S)
    img.paste(art, (x, y))
    # navy kicker strip: status pill left, "N. REGION · TOPIC" after it,
    # source right in gold. Strip text is centred on the glyph centre.
    d.rectangle([x, y + 90, x + w, y + 106], fill=NAVY)
    pill_w = d.textlength(status, font=F_PILL) + 10
    d.rounded_rectangle([x + 8, y + 93, x + 8 + pill_w, y + 103],
                        radius=2, fill=PILL_COL[status])
    d.text((x + 13, y + 92), status, font=F_PILL, fill="white")
    d.text((x + 14 + pill_w, y + 91), "%d. %s · %s" % (num, reg, topic),
           font=F_KICK, fill="white")
    src_w = d.textlength(src, font=F_SRC)
    d.text((x + w - 8 - src_w, y + 91), src, font=F_SRC, fill=GOLD)
    head_lines = wrap(d, head, F_HEAD, w - 16, max_lines=2)
    for j, line in enumerate(head_lines):
        d.text((x + 8, y + 110 + j * 22), line, font=F_HEAD, fill=INK)
    deck_lines = wrap(d, deck, F_DECK, w - 16, max_lines=2)
    for j, line in enumerate(deck_lines):
        d.text((x + 8, y + 110 + len(head_lines) * 22 + 2 + j * 14),
               line, font=F_DECK, fill=(60, 60, 60))
    d.rectangle([x, y, x + w, y + 186], outline=INK, width=1)


def small_card(img, d, story, x, y):
    """One small card: 80px art, navy kicker strip with the status pill on
    the right, a 2-line Times headline and a 2-line serif deck + source,
    all inside a 1px ink box with a fixed bottom per row."""
    num, reg, topic, src, status, head, deck, big, small, key = story
    w = 196
    art = art_image(key, w, 80)
    art_d = ImageDraw.Draw(art)
    # v3.1: the strike label sat flush on the kick strip, its corner
    # crowding "LABOUR" — lift it 6px up inside the art, clear of the strip.
    art_text(art, art_d, 0, 0, w, 80, big, small, F_LBL2, F_LBL2_S,
             dy=-6 if key == "strike" else 0)
    img.paste(art, (x, y))
    d.rectangle([x, y + 80, x + w, y + 95], fill=NAVY)
    d.text((x + 4, y + 81), "%d. %s · %s" % (num, reg, topic),
           font=F_KICK_S, fill="white")
    pill_w = d.textlength(status, font=F_PILL) + 10
    d.rounded_rectangle([x + w - 4 - pill_w, y + 82, x + w - 4, y + 92],
                        radius=2, fill=PILL_COL[status])
    d.text((x + w + 1 - pill_w, y + 81), status, font=F_PILL, fill="white")
    head_lines = wrap(d, head, F_HEAD_S, w - 16, max_lines=2)
    for j, line in enumerate(head_lines):
        d.text((x + 8, y + 99 + j * 17), line, font=F_HEAD_S, fill=INK)
    deck_lines = wrap(d, deck + " — " + src, F_DECK_S, w - 16, max_lines=2)
    for j, line in enumerate(deck_lines):
        d.text((x + 8, y + 99 + len(head_lines) * 17 + 1 + j * 13),
               line, font=F_DECK_S, fill=(60, 60, 60))
    d.rectangle([x, y, x + w, y + 161], outline=INK, width=1)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead 0-109: the date in the top-1 face (Liberation Serif Bold = Times) ----
    d.rectangle([12, 8, 86, 80], fill=RED)
    d.text((49, 12), "NOV", font=F_DATE2, fill="white", anchor="ma")
    d.text((49, 26), "20", font=F_DATE, fill="white", anchor="ma")
    d.text((49, 60), "FRI · 2026", font=F_DATE2, fill="white", anchor="ma")
    d.text((98, 1), "THE WORLD IN ONE DAY", font=F_EYE, fill=RED)
    # thin ink rule above the title, with equal gaps to the kicker and title
    d.line([98, 20, 1012, 20], fill=INK, width=1)
    d.text((98, 11), "Friday 20 November 2026", font=F_TITLE, fill=INK)
    deck_line = ("Akvan hits Odisha · Russian missiles strike Kyiv's bridges · "
                 "COP31 deadlocks on fossil fuels")
    d.text((98, 84), deck_line, font=F_DECKLINE, fill=RED)
    d.text((1012, 1), "36 STORIES · 6 REGIONS · ONE PAGE",
           font=F_EYE, fill=INK, anchor="ra")
    d.rectangle([0, 109, W, 112], fill=GOLD)

    # ---- big-numbers strip 111-149 ----
    slot_w = (W - 24) / len(STATS)
    for i, (value, caption) in enumerate(STATS):
        x = 12 + i * slot_w
        if i > 0:
            d.line([x - 6, 117, x - 6, 149], fill=RULE, width=1)
        d.text((x + 4, 115), value, font=F_STATB, fill=NAVY)
        d.text((x + 4, 137), caption, font=F_STATC, fill=GREY)

    # ---- THE DAY BY HOURS timeline 155-187 ----
    d.rectangle([12, 155, 100, 187], fill=RED)
    d.text((56, 156), "THE DAY", font=F_TTIME, fill="white", anchor="ma")
    d.text((56, 170), "BY HOURS", font=F_TTIME, fill="white", anchor="ma")
    box_x = 104
    cell_w = (W - 12 - box_x) / 8.0
    for i, (when, what) in enumerate(TIMELINE):
        x = box_x + i * cell_w
        if i > 0:
            d.line([x, 157, x, 185], fill=RULE, width=1)
        d.text((x + 5, 158), when, font=F_TTIME, fill=NAVY)
        d.text((x + 5, 170), what, font=F_TTEXT, fill=INK)
    d.line([12, 189, W - 12, 189], fill=RULE, width=1)

    # ---- heroes 192-378: lead 396 wide, rails 294; each card boxed like top 1 ----
    hero_y = 192
    hero_widths = [396, 294, 294]
    hero_x = 12
    for i, story in enumerate(FRONT[:3]):
        hero_card(img, d, story, hero_x, hero_y, hero_widths[i])
        hero_x += hero_widths[i] + 8

    # ---- smalls 384-711 (2 rows x 5, image 196x80); each card boxed like top 1 ----
    for r in range(2):
        for c in range(5):
            k = 3 + r * 5 + c
            small_card(img, d, FRONT[k], 12 + c * 204, 384 + r * 166)

    # ---- map + also 716-956 (map taller, also-list roomier) ----
    map_y = 716
    d.text((12, map_y), "WHERE IT HAPPENED", font=F_SEC, fill=INK)
    d.line([12, map_y + 16, 348, map_y + 16], fill=INK, width=1)
    d.rectangle([12, map_y + 22, 348, map_y + 172], fill=OCEAN, outline=RULE, width=1)
    draw_map(d, 12, map_y + 22, 336, 150)
    d.text((12, map_y + 176), "Red numbers 1–13, dark dots 14–36.",
           font=F_TTEXT, fill=GREY)
    # how-sure-are-we legend under the map (was the stats row)
    d.text((12, map_y + 192), "HOW SURE ARE WE?", font=F_SEC, fill=INK)
    for li, (st, expl) in enumerate(LEGEND):
        ly = map_y + 210 + li * 12
        d.rectangle([12, ly, 20, ly + 8], fill=PILL_COL[st])
        d.text((24, ly - 1), st, font=F_LEGEND, fill=INK)
        d.text((86, ly - 1), expl, font=F_LEGEND, fill=GREY)

    also_x = 364
    d.text((also_x, map_y), "ALSO ON FRIDAY 20 NOVEMBER", font=F_SEC, fill=INK)
    d.text((1012, map_y), "23 MORE STORIES", font=F_SEC, fill=INK, anchor="ra")
    d.line([also_x, map_y + 16, 1012, map_y + 16], fill=INK, width=1)
    col_w = 320
    rows = 12
    for i, (num, city, txt) in enumerate(ALSO):
        col = 0 if i < rows else 1
        row = i if i < rows else i - rows
        x = also_x + col * (col_w + 8)
        y = map_y + 22 + row * 13
        d.text((x, y), "%d." % num, font=F_ALSO_N, fill=RED)
        full = "%s: %s" % (city, txt)
        lines = wrap(d, full, F_ALSO, col_w - 22, max_lines=1)
        d.text((x + 20, y), lines[0] if lines else "", font=F_ALSO, fill=INK)

    # ---- date check 964-992: thin 2-line band (was a 40px box) ----
    chk_y = 964
    d.rectangle([12, chk_y, 1012, chk_y + 28], outline=RED, width=2)
    chk = ("DATE CHECK — Left out, first reported Thursday 19 November: Shenzhen "
           "trilateral summit + peace declaration · Anthropic's $2T Nasdaq debut · "
           "Akvan's approach + evacuations · Kyiv embassy damage · ICJ genocide "
           "ruling read. Not yet news: COP31's final agreed text (talks run on).")
    chk_lines = wrap(d, chk, F_DATECHK, 976, max_lines=2)
    for j, ln in enumerate(chk_lines):
        d.text((20, chk_y + j * 12), ln, font=F_DATECHK, fill=INK)

    # ---- footer 998-1021 ----
    foot_y = 998
    d.text((512, foot_y), "Reads at three sizes: the date and 3 leads at thumbnail size · "
           "13 pictures at half size · all 36 stories at full size.",
           font=F_FOOT, fill=GREY, anchor="ma")
    d.text((512, foot_y + 13), "Pins 1–13, dots 14–36. Sources: AP · Reuters · AFP · IMD · "
           "ICJ · UNFCCC · USGS. Original illustrations.",
           font=F_FOOT, fill=GREY, anchor="ma")

    out_path = os.path.join(HERE, "entry.png")
    img.save(out_path)
    print("saved", out_path, os.path.getsize(out_path), "bytes")
    if PROBLEMS:
        print("PROBLEMS:")
        for problem in PROBLEMS:
            print(" -", problem)
    else:
        print("no truncation")


if __name__ == "__main__":
    main()
