#!/usr/bin/env python3
"""news-image-20261120 v1: 36 stories, newspaper front page, same frozen v21 design as 19 Nov.
Draws entry.png (1024x1024, deterministic) from world.geo.json only.
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


def art_text(img, d, x, y, w, h, big, small, f_big, f_small):
    """White bold label inside the art on a dark scrim, bottom-left.
    Draws nothing when both strings are empty — the art already says it."""
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
    sd.rounded_rectangle([x + 4, y + h - label_h - 4,
                          x + 4 + label_w + 12, y + h - 4],
                         radius=3, fill=(0, 0, 0, 115))
    img.paste(scrim, (0, 0), scrim)
    d.text((x + 10, y + h - label_h), big, font=f_big, fill="white",
           stroke_width=1, stroke_fill=(0, 0, 0))
    if small:
        d.text((x + 10, y + h - label_h + f_big.size + 2), small,
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
        d.rectangle([0, 0, w, h], fill=(12, 70, 160))
        # a tornado seen from the side: a wide disc on top, a twisting
        # funnel narrowing down to a cloud base. That is the storm.
        d.ellipse([65, 6, 145, 16], outline="white", width=2)
        d.ellipse([84, 9, 126, 13], outline="white", width=1)
        # the twisting funnel: stacked rings, narrowing as they fall, each
        # offset a little so the funnel reads as turning
        funnel = ((16, 72, 0), (24, 58, 3), (32, 44, -3),
                  (40, 32, 3), (48, 22, -2), (56, 14, 0))
        for ring_y, ring_w, ring_dx in funnel:
            ring_cx = 105 + ring_dx
            d.ellipse([ring_cx - ring_w // 2, ring_y,
                       ring_cx + ring_w // 2, ring_y + 8],
                      outline="white", width=2)
        # the cloud base the funnel touches down into
        cloud_base = ((65, 60, 34, 12), (85, 58, 36, 14), (108, 60, 34, 12))
        for puff_x, puff_y, puff_w, puff_h in cloud_base:
            d.ellipse([puff_x, puff_y, puff_x + puff_w, puff_y + puff_h],
                      fill=(240, 240, 245))
        # the Odisha coast at the bottom; two houses and a yellow arrow
        # showing people moving inland, away from the sea
        coast = [(0, 80), (0, 68), (60, 66), (120, 68), (196, 66), (196, 80)]
        d.polygon(coast, fill=(8, 40, 90))
        for house_x in (155, 178):
            d.rectangle([house_x, 56, house_x + 14, 66], fill=(240, 230, 210))
            d.polygon([(house_x, 56), (house_x + 14, 56), (house_x + 7, 50)],
                      fill=(180, 60, 40))
        d.line([166, 64, 166, 48], fill=YELLOW, width=3)
        d.polygon([(166, 44), (160, 52), (172, 52)], fill=YELLOW)
        # red warning triangle top right
        d.polygon([(179, 4), (189, 24), (169, 24)], fill=RED,
                  outline=(20, 20, 20))
        d.text((179, 14), "!", font=F_ART2_S, fill=YELLOW, anchor="mm")
    elif key == "kyiv":
        # the Dnipro at night: three bridges across the river, two of them
        # hit — gold decks, red bursts, smoke, one span dipping into the water
        d.rectangle([0, 0, w, h], fill=(16, 28, 58))
        d.rectangle([0, 62, w, h], fill=(20, 60, 110))
        d.line([0, 66, w, 66], fill=(60, 120, 180), width=1)
        d.line([0, 74, w, 74], fill=(60, 120, 180), width=1)
        # three bridge spans across the river: gold deck, pale pylons
        deck_y0, deck_y1, pylon_y0 = 50, 56, 38
        for span_x in (12, 108, 204):
            d.rectangle([span_x, deck_y0, span_x + 78, deck_y1],
                        fill=(255, 205, 40))
            for pylon_dx in (8, 66):
                d.rectangle([span_x + pylon_dx, pylon_y0,
                             span_x + pylon_dx + 4, deck_y0],
                            fill=(220, 220, 220))
        # the middle span is hit: deck broken, dipping into the river
        d.rectangle([108, 50, 140, 56], fill=(255, 205, 40))
        d.polygon([(140, 50), (172, 50), (160, 62), (148, 62)], fill=(120, 30, 30))
        # red explosion bursts over the hit spans + smoke
        d.ellipse([120, 22, 148, 50], fill=(255, 140, 40))
        d.ellipse([128, 30, 142, 44], fill=(255, 220, 80))
        d.ellipse([226, 26, 248, 48], fill=(255, 140, 40))
        d.ellipse([233, 32, 243, 42], fill=(255, 220, 80))
        d.ellipse([130, 8, 146, 24], fill=(200, 200, 200))
        d.ellipse([232, 10, 248, 26], fill=(220, 220, 220))
        # city skyline behind, a few lit windows (lighter than the sky so
        # the buildings read — darker than the background, they vanish)
        for sx, sh in ((20, 26), (52, 18), (240, 22), (268, 16)):
            d.rectangle([sx, 40 - sh, sx + 16, 40], fill=(45, 65, 105))
            d.rectangle([sx + 4, 40 - sh + 4, sx + 7, 40 - sh + 7], fill=(255, 210, 31))
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
        # the rout as a chart: four bars falling, a thick red arrow down
        d.rectangle([0, 0, w, h], fill=(246, 242, 233))
        for gy in range(0, h, 14):
            d.line([0, gy, w, gy], fill=(200, 200, 210), width=1)
        bars = [(20, 18), (60, 30), (100, 44), (140, 56)]
        for bx, top in bars:
            d.rectangle([bx, top, bx + 26, 70], fill=NAVY)
        d.rectangle([140, 56, 166, 70], fill=RED)
        d.line([(16, 14), (180, 62)], fill=RED, width=4)
        d.polygon([(180, 62), (158, 58), (172, 74)], fill=RED)
        d.text((168, 6), "-5%", font=F_ART2_S, fill=RED, anchor="ma")
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
        # a European street march: five walkers, one placard that names the
        # grievance — the cost of living
        d.rectangle([0, 0, w, h], fill=(210, 218, 228))
        d.rectangle([0, 64, w, h], fill=(120, 120, 125))
        for dx in range(6, w, 20):
            d.line([dx, 71, dx + 10, 71], fill="white", width=2)
        d.rectangle([52, 8, 144, 26], fill="white", outline=RED, width=2)
        d.text((98, 17), "COST OF LIVING", font=F_SRC, fill=RED, anchor="mm")
        skins = [(200, 140, 90), (220, 180, 140), (180, 120, 80),
                 (210, 160, 110), (190, 130, 85)]
        shirts = [(40, 90, 160), (200, 40, 40), (30, 140, 80),
                  (220, 170, 40), (90, 60, 140)]
        for i, x in enumerate((18, 52, 86, 120, 154)):
            d.ellipse([x, 32, x + 12, 44], fill=skins[i])
            d.ellipse([x + 3, 37, x + 5, 39], fill=(20, 20, 20))
            d.ellipse([x + 7, 37, x + 9, 39], fill=(20, 20, 20))
            d.rectangle([x + 1, 44, x + 11, 56], fill=shirts[i])
            d.line([x + 4, 56, x + 10, 66], fill=(20, 20, 20), width=2)
            d.line([x + 8, 56, x + 2, 66], fill=(20, 20, 20), width=2)
            if i in (1, 3):
                d.line([x + 10, 48, x + 14, 32], fill=(60, 40, 20), width=2)
                d.rectangle([x + 6, 24, x + 20, 34], fill="white",
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
        # the yellow truce line, and a tank crossing it — the first ground
        # move since the ceasefire
        d.rectangle([0, 0, w, h], fill=(232, 210, 160))
        for dx in range(0, w, 14):
            d.line([dx, 58, dx + 8, 58], fill=YELLOW, width=4)
        d.rectangle([0, 62, w, h], fill=(200, 175, 120))
        for px in range(10, w, 34):
            d.line([px, 44, px, 60], fill=(90, 70, 40), width=2)
        d.rectangle([58, 40, 128, 56], fill=(90, 100, 70))
        d.rectangle([78, 28, 108, 40], fill=(90, 100, 70))
        d.line([108, 34, 142, 34], fill=(50, 55, 40), width=4)
        d.ellipse([64, 56, 72, 62], fill=(40, 40, 40))
        d.ellipse([114, 56, 122, 62], fill=(40, 40, 40))
        d.ellipse([150, 30, 162, 40], fill=(200, 200, 200))
        d.ellipse([158, 24, 172, 34], fill=(220, 220, 220))
    elif key == "crash":
        # Siberia in winter: a cargo plane going down nose-first, smoke
        # trailing, snow and pines below
        d.rectangle([0, 0, w, h], fill=(200, 215, 228))
        d.rectangle([0, 62, w, h], fill=(240, 244, 248))
        for px, ph in ((12, 22), (30, 16), (168, 20), (184, 14)):
            d.polygon([(px, 62), (px + 7, 62 - ph), (px + 14, 62)],
                      fill=(30, 90, 60))
        d.polygon([(150, 18), (120, 34), (128, 38), (112, 52), (118, 54),
                   (132, 44), (150, 30)], fill=(90, 90, 100))
        d.polygon([(138, 26), (128, 18), (142, 24)], fill=(90, 90, 100))
        d.ellipse([108, 48, 122, 60], fill=(200, 200, 200))
        d.ellipse([96, 56, 112, 68], fill=(220, 220, 220))
        d.ellipse([140, 58, 158, 74], fill=(255, 140, 40))
        d.ellipse([145, 63, 153, 71], fill=(255, 220, 80))
    elif key == "rates":
        # the hike as a chart: bars climbing, a red arrow up, 9% in a red box
        d.rectangle([0, 0, w, h], fill=(245, 240, 228))
        for gy in range(0, h, 14):
            d.line([0, gy, w, gy], fill=(210, 205, 190), width=1)
        for bx, top in ((20, 52), (60, 42), (100, 32)):
            d.rectangle([bx, top, bx + 26, 70], fill=NAVY)
        d.rectangle([140, 22, 166, 36], fill=NAVY)
        d.line([(16, 56), (176, 18)], fill=RED, width=4)
        d.polygon([(176, 18), (156, 16), (168, 32)], fill=RED)
        d.rectangle([148, 4, 188, 20], fill=RED)
        d.text((168, 12), "9%", font=F_SRC, fill="white", anchor="mm")
    elif key == "quake":
        # the ground splits: a dark crack zigzags across the frame under a
        # red seismograph trace
        d.rectangle([0, 0, w, h], fill=(232, 214, 170))
        d.rectangle([0, 0, w, 18], fill="white")
        d.line([(4, 9), (30, 9), (38, 3), (46, 15), (54, 9), (80, 9),
                (88, 2), (96, 16), (104, 9), (130, 9), (138, 4), (146, 14),
                (154, 9), (192, 9)], fill=RED, width=2)
        d.line([(10, 30), (40, 44), (70, 36), (100, 52), (130, 44),
                (160, 60), (186, 52)], fill=(40, 30, 20), width=4)
        for hx, hw in ((24, 26), (120, 30)):
            d.rectangle([hx, 44, hx + hw, 60], fill=(200, 180, 140))
            d.polygon([(hx, 44), (hx + hw, 44), (hx + hw // 2, 36)],
                      fill=(180, 60, 40))
        # repaint the first house: the crack was drawn before the houses,
        # so this covers the crack segment that would show through its wall
        d.rectangle([24, 44, 50, 60], fill=(200, 180, 140))
    elif key == "rikers":
        # the jail: dark bars across a grey wall, the name on a navy sign,
        # a red CLOSED stamp top-right (at the bottom it was clipped by the
        # art's edge)
        d.rectangle([0, 0, w, h], fill=(150, 155, 165))
        d.rectangle([0, 0, w, 12], fill=(90, 95, 105))
        d.rectangle([0, 68, w, h], fill=(90, 95, 105))
        for bx in range(8, w, 22):
            d.rectangle([bx, 12, bx + 8, 68], fill=(40, 42, 48))
        d.rectangle([52, 26, 144, 48], fill=NAVY)
        d.text((98, 37), "RIKERS", font=F_ART2, fill="white", anchor="mm")
        stamp(img, 140, 10, "CLOSED")
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
    art_text(art, art_d, 0, 0, w, 80, big, small, F_LBL2, F_LBL2_S)
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
