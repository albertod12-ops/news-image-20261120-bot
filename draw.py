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


def stamp(img, x, y, text, angle=-15, font=None, ink=(200, 16, 46, 255),
          fill=None):
    """Diagonal rubber-stamp label (the #1 entry's signature device).
    `text` in bold caps inside a 3px outline box, drawn on a small
    RGBA tile that is rotated and pasted onto `img` at (x, y). The text is
    centred in the box (anchor "mm"). Default: red ink, transparent box;
    pass fill=(255, 255, 255, 255) + ink=(0, 0, 0, 255) for black-on-white."""
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
                     fill=fill, outline=ink, width=3)
    tile_d.text((tile_w / 2, tile_h / 2), text, font=fnt,
                fill=ink, anchor="mm")
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
        # funnel zone so the tornado lines read clean (the zone is wide
        # up top where the disc is, and narrows with the funnel below)
        for rx in range(6, w, 16):
            if 162 < rx < 238:
                continue
            d.line([rx, 14, rx - 5, 26], fill=(190, 210, 235), width=2)
        for rx in range(14, w, 26):
            if 170 < rx < 230:
                continue
            d.line([rx, 30, rx - 5, 42], fill=(160, 190, 225), width=2)
        # v3.5: the tornado BIGGER from the middle UPWARD, per the user
        # ("dari tengah ke atas lebih besar lagi") — the spiral disc is
        # wide again (rx 20→34) and the upper funnel is wide (top
        # half-width 30), tapering fast to the same slim tip, like the
        # reference line-art (wide top, narrow tail). Original PIL vector
        # lines in white on the navy storm sky; rain is kept clear of
        # the wider funnel zone above.
        cx = 200
        # spiral disc: flat concentric ellipses, wide again
        for rx, ry in ((34, 8), (26, 6), (18, 5), (10, 3), (4, 2)):
            d.ellipse([cx - rx, 16 - ry, cx + rx, 16 + ry],
                      outline="white", width=2)
        # one spiral sweep across the disc, hinting the rotation
        d.arc([cx - 34, 8, cx + 34, 24], 200, 340,
              fill=(190, 215, 240), width=2)
        # funnel edges: two curves from the disc down to a narrow tip —
        # wide at the top, tapering fast (power 1.3 keeps the tail slim)
        edge_l, edge_r = [], []
        for i in range(25):
            t = i / 24
            y = 24 + int(42 * t)
            hw = 2 + int(28 * ((1 - t) ** 1.3))
            edge_l.append((cx - hw, y))
            edge_r.append((cx + hw, y))
        d.line(edge_l, fill="white", width=2, joint="curve")
        d.line(edge_r, fill="white", width=2, joint="curve")
        # curved horizontal bands inside the funnel, alternating drift
        for by, bhw, bdx in ((30, 23, -1), (37, 18, 1), (44, 13, -1),
                             (51, 8, 1), (57, 5, -1), (62, 3, 0)):
            d.arc([cx + bdx - bhw, by - 3, cx + bdx + bhw, by + 3],
                  0, 180, fill="white", width=2)
        # dust cloud at the funnel's base, straddling the shoreline —
        # kept right of the AKVAN scrim (which ends ~x166) so no puff
        # crosses the "3.7 LAKH EVACUATED" line
        for px0, py0, pw, ph in ((188, 62, 12, 8), (196, 65, 14, 7),
                                 (204, 61, 12, 8), (210, 64, 10, 7)):
            d.ellipse([px0, py0, px0 + pw, py0 + ph],
                      outline=(220, 232, 245), width=2)
        d.ellipse([196, 63, 206, 69], fill=(220, 232, 245))
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
        # v3.5: redrawn per the user's new reference (image 2) — FIVE
        # dark navy bars of the reference's exact relative heights on a
        # baseline, with the thick RED zigzag arrow above them (small rise,
        # deep V, rise, steep fall to an arrowhead at bottom-right). The
        # old six bars, skyline and ticker tape are gone. The -5% focal
        # stays top-right and the NIKKEI -5% scrim bottom-left.
        # Original PIL vector code; the reference file is not used anywhere.
        d.rectangle([0, 0, w, h], fill=(246, 242, 233))
        # five navy bars, heights = the reference's (baseline y62):
        # tops 24, 32, 20, 38, 42 (ratios 0.90, 0.71, 1.00, 0.57, 0.48)
        for bx, top in ((8, 24), (40, 32), (71, 20), (103, 38), (136, 42)):
            d.rectangle([bx, top, bx + 22, 62], fill=(35, 55, 85))
            d.rectangle([bx + 3, top + 3, bx + 8, top + 6], fill="white")
        # baseline under the bars
        d.rectangle([4, 62, 192, 65], fill=(35, 55, 85))
        # thick red zigzag arrow, the reference's shape — clear of the
        # -5% focal (top-right) and of the last bar's top. v3.5.1: the
        # whole zigzag now sits INSIDE the art box with a clear margin
        # from the top edge (peaks y=12-13, stroke top >= y=9) — the
        # v3.5 peaks at y=5 sat flush on the edge and read as clipped.
        d.line([(4, 17), (16, 13), (47, 26), (80, 12), (150, 41)],
               fill=RED, width=6, joint="curve")
        d.polygon([(156, 44), (144, 34), (151, 47)], fill=RED)
        # big -5% focal, top-right, on the light background
        d.text((192, 2), "-5%", font=F_ART2, fill=RED, anchor="ra",
               stroke_width=1, stroke_fill="white")
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
        # v3.5: redrawn per the user's NEW reference (image 1) — a crashed
        # plane in the desert, seen from above: tan sand, a white plane
        # diagonal across the frame (red tail + red wingtips + red stripe
        # along the fuselage), one engine on fire, a dark shadow under
        # the plane, small green cacti at the edges. The old diving-plane
        # sky scene is gone. Original PIL vector code; the reference file
        # (a stock illustration) is not used anywhere.
        d.rectangle([0, 0, w, h], fill=(214, 168, 105))
        # sand texture: darker patches and pebbles
        for px0, py0, pw, ph in ((10, 30, 26, 7), (150, 66, 30, 7),
                                 (60, 8, 22, 6)):
            d.ellipse([px0, py0, px0 + pw, py0 + ph], fill=(200, 152, 92))
        for px, py in ((18, 56), (52, 70), (96, 12), (140, 74), (176, 30),
                       (120, 8), (70, 44)):
            d.ellipse([px, py, px + 3, py + 2], fill=(180, 135, 80))
        # a thin dark crack in the sand, like the reference's — clear of
        # the up-wing tip (which ends x124)
        d.line([(140, 0), (146, 6), (142, 12), (148, 18)],
               fill=(120, 85, 45), width=1)
        # v3.6: scorch mark on the sand under the fires (drawn before the
        # plane so the wreck lies on it)
        d.ellipse([98, 63, 126, 72], fill=(70, 50, 30))
        # plane axis: tail (34,12) -> nose (172,54). P(t, s) = point at
        # fraction t along the axis, offset s across it.
        ax_, ay_, bx_, by_ = 34, 12, 172, 54
        dx_, dy_ = bx_ - ax_, by_ - ay_
        al_ = math.hypot(dx_, dy_)
        ux_, uy_ = dx_ / al_, dy_ / al_
        px_, py_ = -uy_, ux_

        def _P(t, s):
            return (ax_ + t * dx_ + s * px_, ay_ + t * dy_ + s * py_)

        # the two wings: root chord at t=0.55 (half-chord 9), tip chord 4;
        # up-wing 34 long, down-wing 30 (its tip stays right of the
        # AN-12 DOWN scrim, which ends x96)
        up_wing = [_P(0.6125, 0), _P(0.578, -34), _P(0.522, -34),
                   _P(0.4875, 0)]
        # v3.6: the down-wing is BROKEN — snapped off at the root, the outer
        # fragment lying bent on the sand down-right of the break, its red
        # tip still on it. The up-wing stays intact.
        dn_stub = [_P(0.6125, 0), _P(0.578, 14), _P(0.522, 14),
                   _P(0.4875, 0)]
        dn_frag = [(114, 56), (128, 63), (124, 70), (110, 64)]
        fus = [_P(0, -5), _P(0, 5), _P(0.97, 6), _P(1, 0), _P(0.97, -6)]
        # shadow: the plane silhouette shifted down-right, dark brown
        for poly in (up_wing, dn_stub, dn_frag, fus):
            d.polygon([(x + 7, y + 9) for (x, y) in poly],
                      fill=(110, 75, 40))
        # wings, white with a dark outline; red tips on the outer fifth
        d.polygon(up_wing, fill=(245, 245, 240), outline=(90, 90, 100))
        d.polygon([(122.5, 11.2), (123.6, 3.7), (116, 1.3), (112.8, 8.2)],
                  fill=RED)
        d.polygon(dn_stub, fill=(245, 245, 240), outline=(90, 90, 100))
        # jagged tear across the stub's snapped end
        d.line([(102, 47), (105, 50), (107, 47), (110, 50)],
               fill=(40, 40, 50), width=2)
        # the snapped-off fragment, bent on the sand, red tip at its end
        d.polygon(dn_frag, fill=(245, 245, 240), outline=(90, 90, 100))
        d.polygon([(124, 66), (128, 63), (126, 61), (122, 64)], fill=RED)
        # fuselage, white with a dark outline so it reads as a plane body
        d.polygon(fus, fill=(245, 245, 240), outline=(90, 90, 100))
        # red tail cone + red stripe along the fuselage
        d.polygon([_P(0, -5), _P(0, 5), _P(0.14, 5.5), _P(0.14, -5.5)],
                  fill=RED)
        d.line([_P(0.16, -3.5), _P(0.94, -3.5)], fill=RED, width=2)
        # red tail stabilisers: one up, one down, swept back from the tail
        d.polygon([_P(0.03, -2), _P(0.03, -12), _P(0.09, -12),
                   _P(0.09, -2)], fill=RED)
        d.polygon([_P(0.03, 2), _P(0.03, 12), _P(0.09, 12), _P(0.09, 2)],
                  fill=RED)
        # v3.6: wreck damage on the fuselage — a jagged crack across the
        # body mid-way plus a dark dent just ahead of it
        d.line([(93, 25), (97, 29), (94, 32), (98, 36), (95, 39)],
               fill=(40, 40, 50), width=2)
        d.ellipse([84, 27, 90, 33], fill=(90, 90, 100))
        # cabin windows along the upper side, cockpit near the nose, and
        # a door just past the red tail cone
        for wt in (0.22, 0.36, 0.50, 0.64, 0.78):
            wx, wy = _P(wt, -3.5)
            d.rectangle([wx - 1, wy - 1, wx + 1, wy + 1], fill=(40, 40, 50))
        d.polygon([(156, 43), (163, 45), (161, 48), (154, 46)],
                  fill=(40, 70, 110))
        d.rectangle([55, 13, 59, 18], outline=(60, 60, 70), width=1)
        # two engine nacelles on the wings; the lower one is on fire
        d.ellipse([109, 19, 119, 24], fill=(200, 200, 205),
                  outline=(90, 90, 100))
        d.ellipse([101, 46, 111, 51], fill=(90, 90, 100))
        # v3.6: MORE fire — bigger flames at the lower engine plus a second
        # fire where the wing snapped
        d.polygon([(100, 50), (96, 64), (101, 60), (104, 69), (109, 58),
                   (113, 66), (116, 53)], fill=(255, 140, 40))
        d.polygon([(102, 55), (104, 63), (108, 56)], fill=(255, 220, 80))
        d.polygon([(112, 54), (110, 62), (114, 59), (117, 64), (120, 57),
                   (121, 52)], fill=(255, 140, 40))
        d.polygon([(114, 57), (116, 62), (119, 57)], fill=(255, 220, 80))
        # thick smoke rising from both fires, drifting right so it clears
        # the fuselage — clear of the scrim (ends x96)
        for ex, ey, er, col in ((104, 43, 4, (110, 110, 110)),
                                 (101, 36, 5, (90, 90, 90)),
                                 (112, 42, 4, (110, 110, 110)),
                                 (118, 34, 5, (90, 90, 90)),
                                 (124, 26, 5, (130, 130, 130)),
                                 (130, 18, 4, (140, 140, 140))):
            d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col)
        # v3.6: debris scattered on the sand around the wreck, clear of
        # the scrim (ends x96, y55+)
        d.polygon([(16, 36), (22, 40), (15, 42)], fill=(90, 90, 100))
        d.polygon([(148, 68), (156, 66), (154, 72), (146, 71)],
                  fill=(245, 245, 240), outline=(90, 90, 100))
        d.polygon([(166, 56), (172, 60), (167, 63)], fill=(60, 60, 70))
        d.polygon([(128, 72), (134, 74), (131, 77)], fill=(120, 120, 125))
        d.rectangle([58, 28, 64, 31], fill=(70, 70, 80))
        # small green cacti at the edges, clear of the scrim
        for cx0, cy0 in ((10, 18), (186, 10), (184, 64)):
            d.ellipse([cx0 - 3, cy0 + 10, cx0 + 6, cy0 + 12],
                      fill=(180, 135, 80))
            d.rectangle([cx0, cy0, cx0 + 3, cy0 + 10], fill=(35, 130, 60))
            d.rectangle([cx0 - 4, cy0 + 3, cx0, cy0 + 5], fill=(35, 130, 60))
            d.rectangle([cx0 + 3, cy0 + 5, cx0 + 7, cy0 + 7],
                        fill=(35, 130, 60))
    elif key == "rates":
        # v3.5: redrawn to match the user's reference EXACTLY — the user
        # asked why v3.4 was not the same. FIVE black bars with the
        # reference's relative heights (0.34, 0.49, 0.42, 0.71, 1.00,
        # measured off the reference file), and the zigzag arrow in BLACK
        # — v3.4's red arrow was the mismatch — same zigzag shape rising
        # to an arrowhead at top-right. The 9% focal, gold coins + Rs
        # stamp and the RATE 9% scrim stay. Original PIL vector code;
        # the reference file (watermarked) is not used anywhere.
        d.rectangle([0, 0, w, h], fill=(245, 240, 228))
        for gy in range(0, h, 12):
            d.line([0, gy, w, gy], fill=(210, 205, 190), width=1)
        for gx in range(0, w, 24):
            d.line([gx, 0, gx, h], fill=(228, 223, 208), width=1)
        # five black bars, the reference's heights, baseline y62 —
        # the last bar's top is y18 so it stays clear of the 9% focal
        for bx, top in ((8, 46), (39, 39), (70, 43), (101, 29), (132, 18)):
            d.rectangle([bx, top, bx + 24, 62], fill=(20, 20, 25))
            d.rectangle([bx + 3, top + 3, bx + 8, top + 6], fill="white")
        # thick BLACK zigzag arrow, the reference's shape, rising to the
        # top-right — clear of the 9% focal (ink starts ~x154) and of
        # the last bar; where a V dips into a bar it merges, as in the
        # reference (black on black)
        d.line([(2, 49), (60, 15), (85, 36), (100, 19), (122, 38),
                (148, 5)], fill=(20, 20, 25), width=6, joint="curve")
        d.polygon([(148, 4), (136, 6), (146, 14)], fill=(20, 20, 25))
        # big 9% focal, top-right, on the grid — v3.1: at x=184, 12px
        # clear of the edge, clear of the arrow (ends x=148)
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
        # orange block sides at the bottom. v3.4: the crack runs TOP to
        # BOTTOM (was sideways), per the user. The red seismograph trace
        # stays across the top. Original PIL vector code; the reference
        # file is not used anywhere.
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
        # v3.5: the crack runs TOP-CENTRE to BOTTOM-CENTRE, per the user
        # — down the middle of the top face from the top vertex (98,18),
        # zigzagging down, then drifting right just enough to stay visible
        # past the QUAKE M5 scrim (which ends x104) and on down the front
        # face to the bottom edge. A thin dark seam line beside it reads
        # as the split between the two halves. The white epicentre rings
        # are centred on the crack and drawn UNDER it (v3.4 fix: rings
        # over the crack hid its middle).
        for rr in (5, 8, 11, 14):
            d.ellipse([98 - rr, 38 - rr, 98 + rr, 38 + rr],
                      outline="white", width=1)
        d.ellipse([96, 36, 100, 40], fill="white")
        crack = [(98, 20), (93, 27), (103, 33), (95, 39), (104, 45),
                 (112, 51), (106, 57), (114, 63), (108, 69), (114, 74)]
        d.line(crack, fill=(180, 60, 20), width=9, joint="curve")
        d.line(crack, fill=(250, 125, 50), width=6, joint="curve")
        d.line([(102, 20), (97, 27), (107, 33), (99, 39), (108, 45),
                (116, 51), (110, 57), (118, 63), (112, 69), (118, 74)],
               fill=(120, 40, 15), width=1, joint="curve")
        # two houses: one tilted left, one with a collapsed roof right,
        # on either side of the vertical crack
        d.polygon([(28, 30), (52, 26), (52, 40), (28, 44)],
                  fill=(240, 240, 235))
        d.polygon([(26, 30), (54, 26), (40, 18)], fill=(40, 110, 200))
        d.rectangle([34, 32, 38, 38], fill=(255, 180, 90))
        d.rectangle([44, 30, 48, 36], fill=(255, 180, 90))
        d.polygon([(152, 28), (176, 24), (176, 38), (152, 42)],
                  fill=(240, 240, 235))
        d.polygon([(150, 28), (164, 18), (178, 26), (170, 30),
                   (158, 28)], fill=(40, 110, 200))
        d.rectangle([158, 30, 162, 36], fill=(255, 180, 90))
        d.rectangle([168, 28, 172, 34], fill=(255, 180, 90))
        # debris on the top face, clear of the scrim
        d.rectangle([62, 41, 70, 44], fill=(250, 125, 50))
        d.rectangle([120, 44, 128, 48], fill=(250, 125, 50))
        d.rectangle([146, 48, 152, 51], fill=(40, 110, 200))
        d.rectangle([122, 54, 130, 57], fill=(250, 125, 50))
        d.rectangle([150, 54, 156, 57], fill=(40, 110, 200))
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
        # CLOSED stamp, fully inside the frame, top-right — v3.6: black
        # text on a white box, per the user
        stamp(img, 122, 4, "CLOSED", angle=-10, ink=(0, 0, 0, 255),
              fill=(255, 255, 255, 255))
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
