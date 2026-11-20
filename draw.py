#!/usr/bin/env python3
"""news-image-20261120 v1: 36 stories, newspaper front page, same frozen v21 design as 19 Nov.
Draws entry.png (1024x1024, deterministic) from world.geo.json only.
Design baseline (user-approved 2026-11-20): boxed 1px INK cards, LiberationSerif-Bold
headlines + LiberationSerif decks, 68px Times masthead, stats/timeline/map/date-check
geometry as in news-image-20261119 v39. CONTENT ONLY changed for Friday 20 Nov 2026.
NOTE: the first draw.py run right after an edit can render the pre-edit file
(sizes matched the previous version in v15/v16/v18) — always verify with 2-3
runs and take the later sha.
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


def font(name, size, base=FD):
    return ImageFont.truetype(os.path.join(base, name), size)


F_TITLE = font("LiberationSerif-Bold.ttf", 68, FLIB)
F_EYE = font("NotoSans-Black.ttf", 13, FNOTO)
F_DECKLINE = font("NotoSerif-Italic.ttf", 16, FNOTO)
F_DATE = font("NotoSans-Black.ttf", 30, FNOTO)
F_DATE2 = font("NotoSans-Bold.ttf", 11, FNOTO)
F_TTIME = font("NotoSans-Bold.ttf", 12, FNOTO)
F_TTEXT = font("NotoSans-Bold.ttf", 10, FNOTO)
F_KICK = font("NotoSans-Bold.ttf", 10, FNOTO)
F_KICK_S = font("NotoSans-Bold.ttf", 9, FNOTO)  # smalls kicker: 10px made #9 touch the pill (0.3px gap)
F_PILL = font("NotoSans-Bold.ttf", 8, FNOTO)
F_SRC = font("NotoSans-Bold.ttf", 9, FNOTO)
F_STAMP = font("NotoSans-Black.ttf", 12, FNOTO)  # v30: the BANNED stamp, big + bold like the user's reference
F_HEAD = font("LiberationSerif-Bold.ttf", 20, FLIB)
F_HEAD_S = font("LiberationSerif-Bold.ttf", 16, FLIB)
F_DECK = font("LiberationSerif-Regular.ttf", 12, FLIB)
F_DECK_S = font("LiberationSerif-Regular.ttf", 11, FLIB)
F_LABEL = font("NotoSans-Bold.ttf", 8, FNOTO)
F_PIN = font("NotoSans-Bold.ttf", 11, FNOTO)
F_ART = font("NotoSans-Black.ttf", 24, FNOTO)
F_ART_S = font("NotoSans-Bold.ttf", 12, FNOTO)
F_ART2 = font("NotoSans-Black.ttf", 17, FNOTO)
F_ART2_S = font("NotoSans-Bold.ttf", 11, FNOTO)
F_FOC = font("NotoSans-Black.ttf", 30, FNOTO)
F_FOC_S = font("NotoSans-Bold.ttf", 12, FNOTO)
F_FOC23 = font("NotoSans-Black.ttf", 20, FNOTO)   # 2/3 of F_FOC (hero 1 only)
F_FOC23_S = font("NotoSans-Bold.ttf", 9, FNOTO)  # 2/3 of F_FOC_S
F_LBL = font("NotoSans-Black.ttf", 16, FNOTO)     # 2/3 of F_ART (hero 3 label)
F_LBL_S = font("NotoSans-Bold.ttf", 9, FNOTO)    # 2/3 of F_ART_S
F_LBL2 = font("NotoSans-Black.ttf", 12, FNOTO)    # 2/3 of F_ART2 (small-card labels)
F_LBL2_S = font("NotoSans-Bold.ttf", 8, FNOTO)   # 2/3 of F_ART2_S
F_ALSO = font("NotoSans-Bold.ttf", 11, FNOTO)
F_ALSO_N = font("NotoSans-Bold.ttf", 11, FNOTO)
F_SEC = font("NotoSans-Black.ttf", 13, FNOTO)
F_STATB = font("NotoSerif-Black.ttf", 21, FNOTO)
F_STATC = font("NotoSans-Bold.ttf", 10, FNOTO)
F_LEGEND = font("NotoSans-Bold.ttf", 10, FNOTO)
F_DATECHK = font("NotoSans-Bold.ttf", 11, FNOTO)
F_FOOT = font("NotoSans-Bold.ttf", 10, FNOTO)

PILL_COL = {"REPORTED": (16, 165, 90), "FORECAST": (20, 110, 230),
            "CLAIM": (230, 150, 0)}

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
    ("REPORTED", "confirmed by named sources"),
    ("FORECAST", "landfall, schedule or draft"),
    ("CLAIM", "one side says so, unverified"),
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
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        PROBLEMS.append("TRUNCATED (%d lines): %s" % (len(lines), text))
        lines = lines[:max_lines]
    return lines


def art_text(img, d, x, y, w, h, big, small, f_big, f_small):
    """Big short text inside the art: white bold on a dark scrim, bottom-left.
    (v34: if both strings are empty, draw nothing — the Greenland pact
    document already carries its own title, flags and score, so its scrim
    would only cover the red 109-0 box.)"""
    if not big and not small:
        return
    bw = int(d.textlength(big, font=f_big))
    sw = int(d.textlength(small, font=f_small)) if small else 0
    if max(bw, sw) + 22 > w:
        PROBLEMS.append("ART TEXT TOO WIDE: %s / %s" % (big, small))
    tw = max(bw, sw)
    bh = f_big.size + f_small.size + 10
    ox = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ox)
    od.rounded_rectangle([x + 4, y + h - bh - 4, x + 4 + tw + 12, y + h - 4],
                         radius=3, fill=(0, 0, 0, 115))
    img.paste(ox, (0, 0), ox)
    d.text((x + 10, y + h - bh), big, font=f_big, fill="white",
           stroke_width=1, stroke_fill=(0, 0, 0))
    if small:
        d.text((x + 10, y + h - bh + f_big.size + 2), small, font=f_small,
               fill="white", stroke_width=1, stroke_fill=(0, 0, 0))


def focal_text(d, x, y, w, h, big, small, f_big, f_small, color, center):
    col = {"YELLOW": YELLOW, "NAVY": NAVY, "WHITE": "white"}[color]
    small_col = "white" if color != "NAVY" else NAVY
    stroke = 0 if color == "NAVY" else 1
    if center:
        bx = x + (w - d.textlength(big, font=f_big)) / 2
        sx = x + (w - d.textlength(small, font=f_small)) / 2 if small else 0
        d.text((bx, y + 8), big, font=f_big, fill=col,
               stroke_width=stroke, stroke_fill=(0, 0, 0))
        if small:
            d.text((sx, y + 8 + f_big.size + 4), small, font=f_small,
                   fill=small_col, stroke_width=stroke, stroke_fill=(0, 0, 0))
    else:
        d.text((x + 8, y + 8), big, font=f_big, fill=col,
               stroke_width=stroke, stroke_fill=(0, 0, 0))
        if small:
            d.text((x + 8, y + 8 + f_big.size + 4), small, font=f_small,
                   fill=small_col, stroke_width=stroke, stroke_fill=(0, 0, 0))


def _star(d, cx, cy, r_out, r_in, fill="white"):
    """Small 5-point star centred at (cx, cy)."""
    pts = []
    for k in range(10):
        r = r_out if k % 2 == 0 else r_in
        a = math.radians(-90 + k * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def _skyline(d, w, h, base, col, seed):
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


def _flag(d, x, y, w, h, kind):
    if kind == "us":
        for i in range(7):
            d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                        fill=(178, 34, 52) if i % 2 == 0 else "white")
        cw, ch = w * 0.4, h * 0.55
        d.rectangle([x, y, x + cw, y + ch], fill=(30, 50, 120))
        # (v37 fix: the stars used a FIXED 7px/6px grid that did not scale
        # with the flag — on the small 20x12 Greenland flag the stars
        # spilled out of the canton and covered the whole flag, which is
        # why they looked wrong. Now the stars scale with the canton and
        # stay inside it.)
        r = max(1.0, min(cw, ch) * 0.09)
        for sy in range(3):
            for sx in range(4):
                scx = x + cw * (0.14 + sx * 0.24)
                scy = y + ch * (0.2 + sy * 0.3)
                d.ellipse([scx - r, scy - r, scx + r, scy + r], fill="white")
    elif kind == "cn":
        d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        d.ellipse([x + 3, y + 3, x + 11, y + 11], fill=(255, 222, 0))
        for sx, sy in [(16, 4), (20, 9), (16, 14)]:
            d.ellipse([x + sx, y + sy, x + sx + 4, y + sy + 4], fill=(255, 222, 0))
    elif kind == "ru":
        d.rectangle([x, y, x + w, y + h / 3], fill="white")
        d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 60, 180))
        d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(200, 20, 30))


def stamp(img, x, y, text, angle=-15, font=None):
    """Diagonal red rubber-stamp label (the #1 entry's signature device).

    Draws `text` in red bold caps inside a red outline box on a small
    RGBA tile, rotates it, and pastes it onto `img` at (x, y).
    The text is centred in the box (anchor "mm") — v30 fix: it used to
    sit top-left, so CUT and BANNED read as off-centre in their boxes.
    """
    if font is None:
        font = F_SRC
    tmp = Image.new("RGBA", (1, 1))
    td = ImageDraw.Draw(tmp)
    bbox = td.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad = 4
    sw, sh = tw + pad * 2 + 4, th + pad * 2 + 4
    s = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    # (v29: the user's BANNED-stamp reference has a THICK border, not a
    # hairline — the outline is now 3px, like the reference.)
    sd.rectangle([2, 2, sw - 3, sh - 3], outline=(200, 16, 46, 255), width=3)
    sd.text((sw / 2, sh / 2), text, font=font, fill=(200, 16, 46, 255),
            anchor="mm")
    s = s.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(s, (x, y), s)


def art_image(key, w, h):
    """Flat-vector picture for one front story, drawn in code."""
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    if key == "summit":
        # (v36: TOTAL rebuild of the people. The v35 leaders were too small
        # and the skyline + big "SHENZHEN 12:45" text squeezed them — the
        # user said they still don't look like the top-1. Now the art is
        # just the three men, big like the top-1: plain dark-blue bg, no
        # skyline, no clock, no focal text (the kicker strip already says
        # SHENZHEN), large flags on gold poles, a thin white table.)
        d.rectangle([0, 0, w, h], fill=(22, 52, 110))
        # three large flags on GOLD poles, centred behind each leader
        for i in range(3):
            cx = int(w * (0.22 + i * 0.28))
            d.line([cx - 35, 6, cx - 35, 78], fill=GOLD, width=3)
            d.ellipse([cx - 38, 2, cx - 32, 8], fill=GOLD)
        _flag(d, 52, 8, 70, 44, "us")
        _flag(d, 163, 8, 70, 44, "cn")
        _flag(d, 274, 8, 70, 44, "ru")
        # a thin white table at the very bottom (v36 fix 2: the first
        # rebuild put the table at y82, too low for the 16px nameplate
        # text — it clipped at the art's bottom edge. The table is back
        # at y72 so the nameplates + text fit inside the 90px art.)
        d.rectangle([w * 0.06, h - 18, w * 0.94, h - 6], fill="white")
        d.line([w * 0.06, h - 18, w * 0.94, h - 18], fill=GOLD, width=2)
        for i in range(3):
            cx = int(w * (0.22 + i * 0.28))
            # broad navy suit — shoulders wider than the head, tall enough
            # to read as a chest, not a stick (v36 fix: the first rebuild
            # hid the body behind the big head + the table)
            d.polygon([(cx - 28, h - 18), (cx + 28, h - 18), (cx + 16, 48),
                       (cx - 16, 48)], fill=(25, 50, 110))
            # white shirt collar + coloured tie
            d.polygon([(cx - 6, 48), (cx + 6, 48), (cx, 56)], fill="white")
            tie_col = ((200, 16, 46) if i == 0 else
                       ((180, 30, 30) if i == 1 else (100, 120, 140)))
            d.polygon([(cx - 3, 52), (cx + 3, 52), (cx, 66)], fill=tie_col)
            # BIG round head (36px, like top-1)
            d.ellipse([cx - 18, 12, cx + 18, 48], fill=(230, 200, 160))
            # dot eyes + a small smile
            d.ellipse([cx - 8, 30, cx - 4, 34], fill=(20, 20, 20))
            d.ellipse([cx + 4, 30, cx + 8, 34], fill=(20, 20, 20))
            d.arc([cx - 5, 36, cx + 5, 42], 0, 180, fill=(20, 20, 20),
                  width=2)
            # hair, big and unmistakable: Trump gold quiff, Xi black cap,
            # Putin grey buzz
            if i == 0:
                d.ellipse([cx - 18, 8, cx + 18, 22], fill=(232, 190, 60))
                d.ellipse([cx - 4, 4, cx + 18, 20], fill=(232, 190, 60))
            elif i == 1:
                d.ellipse([cx - 18, 8, cx + 4, 24], fill=(20, 20, 20))
            else:
                d.ellipse([cx - 18, 8, cx + 18, 20], fill=(150, 150, 150))
        # nameplates on the table front, gold like the top-1 entry
        for i, name in enumerate(("TRUMP", "XI", "PUTIN")):
            cx = int(w * (0.22 + i * 0.28))
            d.rectangle([cx - 18, h - 17, cx + 18, h - 7], fill=GOLD)
            d.text((cx, h - 16), name, font=F_LABEL, fill=INK, anchor="ma")
    elif key == "gta":
        for i in range(h):
            t = i / h
            d.line([0, i, w, i], fill=(int(88 + 120 * t), int(40 + 60 * t),
                                       int(140 - 60 * t)))
        # sun, CENTRE: a full disc in the middle of the sky, like a sunset
        # (v33: the user asked for the sun in the middle, not clipped at
        # the right edge)
        d.ellipse([72, 24, 124, 76], fill=(255, 190, 60))
        # palm fronds silhouetted across the sun
        for py in (34, 41, 48):
            d.line([78, py, 118, py], fill=(40, 20, 60), width=1)
        _skyline(d, w, h, h, (10, 5, 20), 11)
        # palm trees, silhouetted against the sunset (v30: the old ones
        # were straight lines radiating from a point — a starburst, not a
        # palm. Now a curved trunk and fronds that arch out and droop.)
        for px in (14, w - 22):
            d.line([(px, h - 15), (px + 2, h - 30), (px + 5, h - 45),
                    (px + 8, h - 58)], fill=(10, 30, 10), width=3)
            cx, cy = px + 8, h - 58
            for dx, dy in ((-19, -8), (-14, -14), (-2, -17), (12, -14),
                           (19, -6), (16, 4)):
                mx, my = cx + dx // 2, cy + dy // 2 - 3
                d.line([(cx, cy), (mx, my), (cx + dx, cy + dy)],
                       fill=(10, 30, 10), width=2)
        # NZ midnight: gold clock top left, PS5 box, 2 fans with hair (not 4 dots)
        d.ellipse([8, 8, 28, 28], fill=GOLD)
        d.line([18, 18, 18, 10], fill=NAVY, width=2)
        d.line([18, 18, 23, 14], fill=NAVY, width=2)
        d.rectangle([173, 58, 195, 72], fill=(10, 10, 30), outline="white", width=1)
        d.text((184, 65), "PS5", font=F_SRC, fill="white", anchor="mm")
        # fan 1: buzz cut (dark cap on the head)
        cx = 118
        d.ellipse([cx - 5, 62, cx + 5, 72], fill=(230, 200, 160))
        d.ellipse([cx - 5, 60, cx + 5, 66], fill=(40, 30, 20))
        d.rectangle([cx - 7, 72, cx + 7, 80], fill=(20, 20, 40))
        # fan 2: long hair (dark shape behind the head, visible at the sides)
        cx = 146
        d.ellipse([cx - 6, 60, cx + 6, 76], fill=(40, 30, 20))
        d.ellipse([cx - 5, 62, cx + 5, 72], fill=(230, 200, 160))
        d.rectangle([cx - 7, 72, cx + 7, 80], fill=(20, 20, 40))
    elif key == "anthropic":
        d.rectangle([0, 0, w, h], fill=(246, 242, 233))
        for gy in range(0, h, 14):
            d.line([0, gy, w, gy], fill=(180, 190, 210), width=1)
        # (v27: the gold bars + arrow read like any chart. The story is the
        # RECORD — $81.3bn topping SpaceX's $75bn — so show the two bars
        # side by side, Anthropic's taller.)
        # Anthropic's record bar, gold, with its number above and name inside
        d.rectangle([45, 22, 85, 70], fill=GOLD)
        d.text((65, 14), "$81.3BN", font=F_ART2_S, fill=RED, anchor="mm")
        d.text((65, 30), "ANT", font=F_ART2_S, fill="white", anchor="mm")
        # SpaceX's bar, shorter, navy, with its number above and name inside
        d.rectangle([115, 34, 155, 70], fill=NAVY)
        d.text((135, 26), "$75BN", font=F_ART2_S, fill=(20, 20, 20),
               anchor="mm")
        d.text((135, 42), "SPACEX", font=F_SRC, fill="white", anchor="mm")
    elif key == "icj":
        d.rectangle([0, 0, w, h], fill=(226, 218, 196))
        # pediment + 15 columns: first 9 paper, last 6 ink = the 9-6 vote (DeepSeek v20)
        d.polygon([(104, 36), (198, 12), (292, 36)], fill=(120, 110, 95))
        for i in range(15):
            cx = 116 + i * 11
            if i < 9:
                d.rectangle([cx, 40, cx + 7, 74], fill=(244, 239, 226),
                            outline=(120, 110, 95))
            else:
                d.rectangle([cx, 40, cx + 7, 74], fill=NAVY, outline="white")
        # steps
        d.rectangle([110, 76, 282, 80], fill=(240, 234, 220))
        d.rectangle([104, 80, 288, 84], fill=(240, 234, 220))
        d.rectangle([98, 84, 292, 90], fill=(240, 234, 220))
        # red divider between the 9 paper and 6 ink columns (the 9-6 vote)
        d.line([213, 40, 213, 74], fill=(179, 34, 44), width=3)
        # Myanmar flag top left (yellow/green/red + white star), white outline
        d.rectangle([12, 8, 38, 13], fill=(254, 203, 0))
        d.rectangle([12, 13, 38, 18], fill=(0, 140, 60))
        d.rectangle([12, 18, 38, 24], fill=(220, 40, 40))
        d.rectangle([12, 8, 38, 24], outline="white", width=1)
        _star(d, 25, 16, 5, 2)
        # gold scales of justice, left, below the flag (the recognisable object)
        d.line([60, 34, 60, 58], fill=GOLD, width=2)
        d.line([44, 38, 76, 38], fill=GOLD, width=2)
        d.polygon([(48, 38), (56, 38), (52, 48)], fill=GOLD)
        d.polygon([(64, 38), (72, 38), (68, 48)], fill=GOLD)
        d.ellipse([56, 58, 64, 64], fill=GOLD)
    elif key == "cop31":
        d.rectangle([0, 0, w, h], fill=(11, 110, 110))
        # THE DRAFT ITSELF: a white document with the two cuts struck through.
        # (v26: the hourglass/globe/thermometer read as abstract symbols;
        # the document says "draft drops" at a glance. v27: every line of
        # text centred in the box, as the user asked.)
        d.rectangle([16, 6, 180, 52], fill="white", outline=(120, 110, 95))
        d.text((98, 10), "COP31 DRAFT", font=F_SRC, fill=(20, 20, 20),
               anchor="ma")
        # (v28 fix: the grey rule lines used to cross the title and the
        # strike lines sat at the text's bottom edge, reading as underlines.
        # The strike lines now run through the MIDDLE of each word.)
        # FOSSIL FUELS struck through in red, centred (73px wide)
        d.text((98, 27), "FOSSIL FUELS", font=F_ART2_S, fill=RED,
               anchor="mm")
        d.line([60, 27, 136, 27], fill=RED, width=2)
        # $120BN is gone from the 19 Nov draft; on 20 Nov the cut is the
        # PHASE-OUT itself, struck through in red, centred (~55px wide)
        d.text((98, 39), "PHASE-OUT", font=F_ART2_S, fill=RED, anchor="mm")
        d.line([70, 39, 126, 39], fill=RED, width=2)
        # diagonal CUT stamp on the document, clear of the centred text
        stamp(img, 140, 6, "CUT")
        # a BIG globe + a thermometer, like the top-1 entry (v35: the user
        # asked for both — the planet the deal is about, and the heat it
        # measures. The globe is blue ocean + green continents now, much
        # bigger than the old green disc; the thermometer stands beside it)
        d.ellipse([204, 6, 266, 68], fill=(30, 120, 200),
                  outline=(20, 20, 20), width=2)
        d.ellipse([216, 16, 236, 32], fill=(60, 180, 90))
        d.ellipse([236, 38, 256, 54], fill=(60, 180, 90))
        d.ellipse([214, 44, 226, 56], fill=(60, 180, 90))
        # thermometer: white tube, red fill rising, round bulb, tick marks
        d.rectangle([274, 8, 284, 58], fill="white", outline=(20, 20, 20))
        d.rectangle([276, 24, 282, 58], fill=(220, 30, 40))
        d.ellipse([270, 56, 290, 76], fill=(220, 30, 40),
                  outline=(20, 20, 20))
        for ty in (14, 22, 30, 38, 46, 54):
            d.line([284, ty, 289, ty], fill=(20, 20, 20), width=1)
    elif key == "akvan":
        d.rectangle([0, 0, w, h], fill=(12, 70, 160))
        # (v29: the top-down spiral read as a target. The user's reference
        # is a TORNADO seen from the side — a wide disc on top, a twisting
        # funnel narrowing down to a cloud base. That is the storm now.)
        # the wide disc on top (the cloud top), with an inner oval
        d.ellipse([65, 6, 145, 16], outline="white", width=2)
        d.ellipse([84, 9, 126, 13], outline="white", width=1)
        # the twisting funnel: stacked rings, narrowing as they fall, each
        # offset a little so the funnel reads as turning
        for ry, rw, ro in ((16, 72, 0), (24, 58, 3), (32, 44, -3),
                           (40, 32, 3), (48, 22, -2), (56, 14, 0)):
            cx = 105 + ro
            d.ellipse([cx - rw // 2, ry, cx + rw // 2, ry + 8],
                      outline="white", width=2)
        # the cloud base the funnel touches down into
        for bx, by, bw, bh in ((65, 60, 34, 12), (85, 58, 36, 14),
                               (108, 60, 34, 12)):
            d.ellipse([bx, by, bx + bw, by + bh], fill=(240, 240, 245))
        # the Odisha coast at the bottom; two houses and a yellow arrow
        # showing people moving inland, away from the sea
        d.polygon([(0, 80), (0, 68), (60, 66), (120, 68), (196, 66),
                   (196, 80)], fill=(8, 40, 90))
        for hx in (155, 178):
            d.rectangle([hx, 56, hx + 14, 66], fill=(240, 230, 210))
            d.polygon([(hx, 56), (hx + 14, 56), (hx + 7, 50)],
                      fill=(180, 60, 40))
        d.line([166, 64, 166, 48], fill=YELLOW, width=3)
        d.polygon([(166, 44), (160, 52), (172, 52)], fill=YELLOW)
        # red warning triangle top right
        d.polygon([(179, 4), (189, 24), (169, 24)], fill=RED,
                  outline=(20, 20, 20))
        d.text((179, 14), "!", font=F_ART2_S, fill=YELLOW, anchor="mm")
    elif key == "kerch":
        d.rectangle([0, 0, w, h], fill=(14, 30, 80))
        # (v29: the user's bridge-silhouette reference — a proper suspension
        # bridge: pointed towers, a sagging main cable, vertical suspenders.
        # The middle span is still blown out below it.)
        # water at the bottom
        d.rectangle([0, 64, w, h], fill=(10, 22, 60))
        d.line([0, 68, w, 68], fill=(30, 60, 110), width=1)
        d.line([0, 74, w, 74], fill=(30, 60, 110), width=1)
        # two WIDE flat-topped towers with a crossbeam, like the reference
        # suspension bridge (v32: the v31 spires were still thin and wispy —
        # the reference bridges are BOLD solid silhouettes, so the towers
        # are 12px wide now, the cable is a thick band, the deck is thick)
        for tx in (34, 166):
            d.rectangle([tx, 6, tx + 12, 44], fill=(225, 225, 225))
            d.rectangle([tx - 3, 14, tx + 15, 18], fill=(225, 225, 225))
        # the main suspension cable: side spans + a deep sagging span
        # between the tower tops (lowest at the middle, y32) — a THICK
        # white band now, so it reads as part of the silhouette
        d.line([(8, 42), (40, 6)], fill="white", width=4)
        d.line([(40, 6), (56, 18), (70, 26), (84, 30), (98, 32),
                (112, 30), (126, 26), (140, 18), (156, 10), (172, 6)],
               fill="white", width=4)
        d.line([(172, 6), (188, 42)], fill="white", width=4)
        # vertical suspenders from the cable down to the intact deck
        for sx, sy in ((56, 18), (70, 26), (84, 30), (98, 32), (180, 24)):
            d.line([sx, sy, sx, 40], fill="white", width=2)
        # gold deck, left and right of the blown-out middle span — thicker
        d.rectangle([8, 40, 120, 47], fill=(255, 205, 40))
        d.rectangle([160, 40, 188, 47], fill=(255, 205, 40))
        # the blown-out span, collapsed into the water (dark red, jagged)
        d.polygon([(120, 40), (160, 40), (150, 52), (140, 62), (130, 52)],
                  fill=(120, 30, 30))
        d.line([120, 40, 140, 62], fill=(200, 60, 40), width=2)
        d.line([160, 40, 140, 62], fill=(200, 60, 40), width=2)
        # explosion burst + smoke rising from the break
        d.ellipse([132, 34, 148, 50], fill=(255, 160, 40))
        d.ellipse([136, 38, 144, 46], fill=(255, 220, 80))
        d.ellipse([138, 22, 150, 34], fill=(200, 200, 200))
        d.ellipse([148, 12, 162, 26], fill=(220, 220, 220))
        d.ellipse([158, 4, 172, 18], fill=(235, 235, 235))
        # halted 3-car train on the left deck, headlight on, + a figure by the gap
        d.rectangle([20, 34, 36, 40], fill=(180, 30, 30))
        d.rectangle([38, 32, 54, 40], fill=(200, 40, 40))
        d.rectangle([56, 34, 72, 40], fill=(180, 30, 30))
        d.ellipse([50, 35, 54, 39], fill=GOLD)
        d.ellipse([110, 32, 114, 36], fill=(230, 200, 160))
        d.line([112, 36, 112, 40], fill=(20, 20, 20), width=2)
    elif key == "han":
        d.rectangle([0, 0, w, h], fill=NAVY)
        # the overturned sentence, big and unmistakable: "15 YEARS" with a
        # red PROHIBITION sign over it (v30: the user's circular-BANNED
        # reference — a thick red ring + diagonal bar — replaces the red X;
        # the X hid the digits, the ring frames them)
        # (v28 fix: the X was drawn OVER the text, so its thick arms hid the
        # "1" and the "YEARS". The ring + bar are drawn first and the text
        # sits on top of them — fully readable, still cancelled.)
        d.ellipse([6, 2, 52, 48], outline=RED, width=4)
        d.line([13, 9, 45, 41], fill=RED, width=4)
        d.text((16, 10), "15", font=F_ART, fill=(11, 27, 51))
        d.text((14, 8), "15", font=F_ART, fill="white")
        d.text((14, 34), "YEARS", font=F_ART2_S, fill="white")
        # (v31: the OVERTURNED stamp is gone — the user found its red box
        # and red text distracting and unclear. The prohibition ring over
        # "15 YEARS" already says the sentence is cancelled.)
        # (v32: the art looked empty after the stamp went, so the space now
        # holds the South Korean flag (Taegeukgi) — the news is about a
        # South Korean ex-PM. White field, red-over-blue taegeuk, four
        # black trigrams in the corners.)
        d.rectangle([62, 6, 132, 30], fill="white")
        d.pieslice([89, 10, 105, 26], 180, 360, fill=(205, 33, 52))
        d.pieslice([89, 10, 105, 26], 0, 180, fill=(0, 71, 140))
        d.ellipse([93, 14, 101, 22], fill=(205, 33, 52))
        d.ellipse([93, 14, 101, 22], fill=(0, 71, 140))
        for bx, by in ((66, 9), (122, 9), (66, 22), (122, 22)):
            d.rectangle([bx, by, bx + 8, by + 2], fill=(20, 20, 20))
        # a BIG gold gavel as the court's symbol, top right: head + long
        # handle + striking block (v27: the scales were clutter, removed)
        d.rectangle([140, 30, 168, 36], fill=(91, 58, 30))
        d.line([140, 30, 168, 30], fill=(138, 97, 54), width=1)
        d.rectangle([148, 8, 172, 18], fill=GOLD)
        d.line([160, 18, 148, 30], fill=GOLD, width=4)
    elif key == "greenland":
        # (v36: TOTAL REBUILD. The document + flanking icebergs never read
        # as a scene — the user said rebuild it entirely. Now it is the
        # top-1's scene, our own arrangement: pale sky, a big white
        # mountain, two flags on poles, a red 109-0 box, a small globe.
        # No document, no title box, no scrim — the headline below the art
        # already says "Arctic pact".)
        d.rectangle([0, 0, w, h], fill=(190, 215, 235))
        # navy sea band, waterline at y62
        d.rectangle([0, 62, w, h], fill=NAVY)
        # a smaller mountain behind, left, for depth
        d.polygon([(30, 80), (60, 35), (90, 80)], fill=(220, 230, 240))
        # the BIG white mountain, centre
        d.polygon([(55, 80), (95, 15), (135, 80)], fill="white")
        d.polygon([(95, 15), (135, 80), (120, 80)], fill=(191, 227, 242))
        # Danish flag (left) and US flag (right) on dark poles, top-left
        d.line([10, 8, 10, 32], fill=(20, 20, 20), width=2)
        d.rectangle([12, 10, 32, 22], fill=(200, 20, 40))
        d.rectangle([12, 15, 32, 17], fill="white")
        d.rectangle([20, 10, 22, 22], fill="white")
        d.line([38, 8, 38, 32], fill=(20, 20, 20), width=2)
        _flag(d, 40, 10, 20, 12, "us")
        # the vote, white text in a RED box, top-right (v38: the user asked
        # for VOTE ABOVE the number — VOTE on top, 109-0 underneath)
        d.rectangle([142, 6, 192, 34], fill=RED)
        d.text((167, 13), "VOTE", font=F_SRC, fill="white", anchor="mm")
        d.text((167, 26), "109-0", font=F_ART2_S, fill="white", anchor="mm")
        # small globe below the vote box, blue + white grid lines
        d.ellipse([160, 36, 180, 56], fill=(30, 120, 200),
                  outline=(20, 20, 20), width=1)
        d.line([170, 36, 170, 56], fill="white", width=1)
        d.line([160, 46, 180, 46], fill="white", width=1)
    elif key == "marathon":
        # (v39: the user asked for the runner ON A WINNER'S PODIUM holding
        # a TROPHY. Now she stands on the 1st-place podium, trophy raised
        # — the champion moment, with the BANNED stamp as the twist. The
        # track lanes are gone (a podium is not a track); the crowd,
        # Kenyan flag and "3 YEARS" box stay.)
        d.rectangle([0, 0, w, h], fill=(228, 200, 150))
        # crowd stand: a dark band across the top, heads in a row
        d.rectangle([0, 0, w, 16], fill=(40, 40, 60))
        for hx in range(95, 190, 13):
            d.ellipse([hx, 5, hx + 7, 12], fill=(230, 200, 160))
        for hx in range(102, 190, 13):
            d.ellipse([hx, 8, hx + 6, 14], fill=(120, 80, 50))
        # Kenyan flag, small, top-left (on the crowd band)
        d.rectangle([8, 6, 32, 10], fill=(20, 20, 20))
        d.rectangle([8, 10, 32, 11], fill="white")
        d.rectangle([8, 11, 32, 15], fill=(200, 30, 30))
        d.rectangle([8, 15, 32, 16], fill="white")
        d.rectangle([8, 16, 32, 20], fill=(30, 140, 60))
        # the ban, spelled out in a red box, text centred in it
        d.rectangle([36, 6, 84, 20], fill=RED)
        d.text((60, 13), "3 YEARS", font=F_ART2_S, fill="white", anchor="mm")
        # the winner's podium: 1st tallest in the centre, 2nd + 3rd beside
        d.rectangle([52, 64, 80, 80], fill=(220, 220, 220))
        d.rectangle([116, 68, 144, 80], fill=(220, 220, 220))
        d.rectangle([80, 56, 116, 80], fill="white")
        d.rectangle([80, 56, 116, 59], fill=GOLD)
        d.text((66, 72), "2", font=F_ART2_S, fill=(20, 20, 20), anchor="mm")
        d.text((130, 74), "3", font=F_ART2_S, fill=(20, 20, 20), anchor="mm")
        d.text((98, 68), "1", font=F_ART2_S, fill=(20, 20, 20), anchor="mm")
        # the champion, standing on the 1st-place podium, trophy raised
        SKIN = (120, 80, 50)
        d.ellipse([88, 24, 102, 38], fill=SKIN)
        d.ellipse([88, 22, 102, 30], fill=(20, 20, 20))
        d.polygon([(90, 38), (100, 38), (98, 52), (92, 52)], fill=(200, 30, 30))
        d.rectangle([90, 52, 100, 56], fill=(20, 20, 20))
        # left arm down at her side, right arm raised holding the trophy
        d.line([90, 42, 84, 50], fill=SKIN, width=3)
        d.line([98, 42, 110, 26], fill=SKIN, width=3)
        d.rectangle([92, 44, 98, 50], fill="white")
        # the gold trophy cup in her raised hand
        d.polygon([(104, 10), (122, 10), (119, 22), (107, 22)], fill=GOLD)
        d.rectangle([111, 22, 115, 26], fill=GOLD)
        d.rectangle([107, 26, 119, 29], fill=GOLD)
        # ONE big diagonal BANNED stamp, right, like the top-1's
        stamp(img, 132, 16, "BANNED", font=F_STAMP)
    elif key == "riyadh":
        d.rectangle([0, 0, w, h], fill=(10, 20, 50))
        _skyline(d, w, h, h - 30, (6, 12, 34), 11)
        # (v28: the missile now sits right against a tall tower, a split
        # second before impact, with the explosion already starting around
        # it — the interceptor caught it at the building.)
        # a tall tower on the right, the missile's target (lit windows)
        d.rectangle([150, 14, 172, 70], fill=(8, 16, 40))
        for wy in (22, 32, 42, 52, 62):
            for wx in (154, 162):
                d.rectangle([wx, wy, wx + 4, wy + 4], fill=(255, 215, 154))
        # the interceptor's red trail, launched from the ground, bottom-left,
        # climbing all the way to the missile's tail (v33: the user asked
        # for the red line to reach the rocket — it used to stop short)
        d.polygon([(24, 79), (60, 52), (128, 34), (132, 38), (64, 56),
                   (28, 79)], fill=RED)
        # the Houthi missile, SMALL now (v32: the v31 missile was far too
        # big) — about 1/4 the size, and DIAGONAL, its tail following the
        # red interceptor trail's direction (climbing up-right toward the
        # tower), not horizontal. Nose at the tower wall, flame trailing
        # down-left along the red line.
        d.polygon([(150, 22), (143, 25), (143, 30)], fill=(220, 220, 220))
        d.polygon([(143, 25), (145, 30), (133, 36), (131, 31)],
                  fill=(220, 220, 220))
        d.polygon([(133, 31), (129, 27), (135, 33)], fill=(180, 180, 180))
        d.polygon([(133, 36), (129, 40), (135, 35)], fill=(180, 180, 180))
        d.polygon([(132, 33), (118, 40), (133, 36)], fill=(255, 140, 40))
        d.polygon([(132, 33), (124, 37), (133, 35)], fill=(255, 220, 80))
        # the explosion starting around the missile nose: orange burst,
        # yellow core, sparks, smoke and debris
        d.ellipse([140, 12, 160, 32], fill=(255, 140, 40))
        d.ellipse([145, 17, 155, 27], fill=(255, 220, 80))
        for a in range(0, 360, 30):
            d.line([150, 22, 150 + int(12 * math.cos(math.radians(a))),
                    22 + int(12 * math.sin(math.radians(a)))],
                   fill=YELLOW, width=2)
        d.ellipse([132, 6, 144, 16], fill=(200, 200, 200))
        d.ellipse([160, 2, 172, 12], fill=(180, 180, 180))
        for dx, dy in ((126, 16), (168, 34), (134, 36), (164, 38)):
            d.rectangle([dx, dy, dx + 2, dy + 2], fill=(255, 200, 100))
        # small warm city dots along the base
        for dx in (30, 70, 110, 150, 180):
            d.ellipse([dx, 74, dx + 2, 76], fill=(255, 215, 154))
    elif key == "kyiv":
        # the Dnipro at night: three bridges across the river, two of them
        # hit — gold decks, red bursts, smoke, one span dipping into the water
        d.rectangle([0, 0, w, h], fill=(16, 28, 58))
        d.rectangle([0, 62, w, h], fill=(20, 60, 110))
        d.line([0, 66, w, 66], fill=(60, 120, 180), width=1)
        d.line([0, 74, w, 74], fill=(60, 120, 180), width=1)
        # three bridge spans across the river
        for bx in (12, 108, 204):
            d.rectangle([bx, 50, bx + 78, 56], fill=(255, 205, 40))
            d.rectangle([bx + 8, 38, bx + 12, 50], fill=(220, 220, 220))
            d.rectangle([bx + 66, 38, bx + 70, 50], fill=(220, 220, 220))
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
        # the buildings read — the first version drew them darker than the
        # background and they vanished)
        for sx, sh in ((20, 26), (52, 18), (240, 22), (268, 16)):
            d.rectangle([sx, 40 - sh, sx + 16, 40], fill=(45, 65, 105))
            d.rectangle([sx + 4, 40 - sh + 4, sx + 7, 40 - sh + 7], fill=(255, 210, 31))
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
        # two SMALL tanks on the right: the first version put full-size tanks
        # at the bottom-left and the art_text scrim hid the left one entirely.
        # 32px wide, clear of the scrim (which ends ~x126).
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
        d.rectangle([24, 44, 50, 60], fill=(200, 180, 140))
    elif key == "rikers":
        # the jail: dark bars across a grey wall, the name on a navy sign,
        # a red CLOSED stamp
        d.rectangle([0, 0, w, h], fill=(150, 155, 165))
        d.rectangle([0, 0, w, 12], fill=(90, 95, 105))
        d.rectangle([0, 68, w, h], fill=(90, 95, 105))
        for bx in range(8, w, 22):
            d.rectangle([bx, 12, bx + 8, 68], fill=(40, 42, 48))
        d.rectangle([52, 26, 144, 48], fill=NAVY)
        d.text((98, 37), "RIKERS", font=F_ART2, fill="white", anchor="mm")
        # CLOSED stamp top-right: the first version put it at (132, 52) and
        # its rotated tile ran past the art's bottom edge and was clipped.
        stamp(img, 140, 10, "CLOSED")
    elif key == "ukraine":
        d.rectangle([0, 0, w, h // 2], fill=(0, 90, 180))
        d.rectangle([0, h // 2, w, h], fill=(255, 210, 31))
        d.ellipse([w // 2 - 8, h // 2 - 14, w // 2 + 8, h // 2 + 14],
                  fill=RED, outline="white", width=2)
        # empty chair top right + folded flag in a closed briefcase top left
        d.rectangle([w - 44, 12, w - 12, 16], fill=(90, 60, 30))
        d.rectangle([w - 42, 16, w - 38, 30], fill=(90, 60, 30))
        d.rectangle([w - 18, 16, w - 14, 30], fill=(90, 60, 30))
        d.rectangle([12, 10, 52, 22], fill=(60, 40, 20))
        d.rectangle([14, 12, 32, 20], fill=(0, 90, 180))
        d.rectangle([34, 12, 50, 20], fill=(255, 210, 31))
    elif key == "apec":
        d.rectangle([0, 0, w, h], fill=(14, 90, 90))
        _skyline(d, w, h, h, (8, 50, 55), 21)
        d.ellipse([w // 2 - 16, 10, w // 2 + 16, 42], fill=GOLD)
        d.text((w // 2, 26), "21", font=F_ART2, fill=NAVY, anchor="mm")
        # ring of mini flags along the bottom edge (signed page dropped: scrim covers it)
        for i in range(7):
            fx = 10 + i * (w - 20) // 7
            d.rectangle([fx, h - 8, fx + 8, h - 3],
                        fill=[(178, 34, 52), (222, 41, 16), (0, 60, 180),
                              (255, 210, 31), (30, 140, 80), (20, 150, 160),
                              (200, 40, 40)][i])
    elif key == "florida":
        d.rectangle([0, 0, w, h], fill=(90, 120, 150))
        for i in range(14):
            x = (i * 23) % w
            d.line([x, 8 + (i % 3) * 12, x - 8, 30 + (i % 3) * 12],
                   fill=(220, 230, 240), width=2)
        d.rectangle([w * 0.15, h - 34, w * 0.55, h - 12], fill=(60, 50, 40))
        d.polygon([(w * 0.12, h - 34), (w * 0.35, h - 52), (w * 0.58, h - 34)],
                  fill=(140, 40, 40))
        d.rectangle([0, h - 10, w, h], fill=(30, 80, 140))
        # 1-ft ruler top left + rescue boat top right (scrim covers the bottom)
        d.rectangle([10, 8, 18, 40], fill="white")
        for i in range(4):
            d.line([10, 12 + i * 9, 16, 12 + i * 9], fill=NAVY, width=1)
        d.text((24, 12), "1 FT", font=F_SRC, fill="white")
        d.polygon([(w - 72, 10), (w - 28, 10), (w - 34, 24),
                   (w - 66, 24)], fill=(255, 210, 31))
        d.ellipse([w - 54, 2, w - 44, 12], fill=(230, 200, 160))
    elif key == "suneung":
        d.rectangle([0, 0, w, h], fill=(232, 226, 210))
        d.rectangle([8, 8, w - 8, 26], fill=(40, 60, 90))
        d.ellipse([w - 30, 12, w - 14, 28], fill="white")
        for r in range(2):
            for c in range(3):
                x = 16 + c * (w // 3)
                y = 36 + r * 26
                d.rectangle([x, y, x + w // 4, y + 16], fill=(150, 120, 80))
                d.ellipse([x + w // 8 - 6, y - 10, x + w // 8 + 6, y + 2],
                          fill=(230, 200, 160))
        # plane held overhead, flights paused
        d.polygon([(w - 70, 14), (w - 30, 18), (w - 70, 22)], fill=(90, 90, 90))
        d.polygon([(w - 58, 10), (w - 48, 18), (w - 58, 20)], fill=(90, 90, 90))
        d.line([w - 74, 18, w - 26, 18], fill=RED, width=2)
    elif key == "colombia":
        d.rectangle([0, 0, w, h], fill=(240, 220, 160))
        # (v26: a static row of figures did not say "march". Now they walk,
        # in stride, down a road, carrying the PARO NACIONAL banner.)
        # road at the bottom, with a dashed centre line
        d.rectangle([0, 66, w, h], fill=(120, 110, 100))
        for dx in range(6, w, 20):
            d.line([dx, 73, dx + 10, 73], fill="white", width=2)
        # the PARO NACIONAL banner, carried on two poles at the front:
        # wider (96px) so the 75px text has real breathing room, and the
        # text placed by exact measurement so it is pixel-centred (v27)
        d.line([108, 10, 108, 34], fill=(60, 40, 20), width=2)
        d.line([188, 10, 188, 34], fill=(60, 40, 20), width=2)
        d.rectangle([100, 10, 196, 28], fill="white", outline=RED, width=2)
        d.text((148, 19), "PARO NACIONAL", font=F_SRC, fill=RED,
               anchor="mm")
        # FECODE banner, top-left, widened the same way
        d.rectangle([8, 8, 70, 24], fill=NAVY)
        d.text((39, 16), "FECODE", font=F_SRC, fill="white", anchor="mm")
        # five marchers walking right, in stride, shirts in varied colours
        skins = [(200, 140, 90), (220, 180, 140), (180, 120, 80),
                 (210, 160, 110), (190, 130, 85)]
        shirts = [(40, 90, 160), (200, 40, 40), (30, 140, 80),
                  (220, 170, 40), (90, 60, 140)]
        for i, x in enumerate((18, 52, 86, 120, 154)):
            d.ellipse([x, 34, x + 12, 46], fill=skins[i])
            d.ellipse([x + 3, 39, x + 5, 41], fill=(20, 20, 20))
            d.ellipse([x + 7, 39, x + 9, 41], fill=(20, 20, 20))
            d.rectangle([x + 1, 46, x + 11, 58], fill=shirts[i])
            # stride: one leg forward, one back
            d.line([x + 4, 58, x + 10, 68], fill=(20, 20, 20), width=2)
            d.line([x + 8, 58, x + 2, 68], fill=(20, 20, 20), width=2)
            # marchers 2 and 4 hold a placard up on a stick
            if i in (1, 3):
                d.line([x + 10, 50, x + 14, 34], fill=(60, 40, 20), width=2)
                d.rectangle([x + 6, 26, x + 20, 36], fill="white",
                            outline=INK)
    elif key == "australia":
        d.rectangle([0, 0, w, h], fill=(245, 240, 228))
        # (v26: four abstract bars did not say "people lost jobs". Now the
        # rate is a big red number, and a row of people — two in red — are
        # the ones who lost their jobs.)
        # the jobless rate, big and red, top-left (like top 1's "4.9%")
        d.text((8, 4), "4.9%", font=F_ART, fill=RED)
        # -44,000 in a bold red box, top-right
        d.rectangle([140, 4, 190, 20], fill=RED)
        d.text((165, 12), "-44,000", font=F_SRC, fill="white", anchor="mm")
        # red arrow climbing (the rate rising), clear of the big number
        d.line([(70, 50), (180, 26)], fill=RED, width=3)
        d.polygon([(180, 26), (162, 24), (174, 38)], fill=RED)
        # a row of six people; the 3rd and 5th are in red (job losses)
        for i, x in enumerate((16, 44, 72, 100, 128, 156)):
            col = RED if i in (2, 4) else NAVY
            d.ellipse([x, 52, x + 10, 62], fill=(200, 140, 90))
            d.rectangle([x + 1, 62, x + 9, 74], fill=col)
    elif key == "libya":
        d.rectangle([0, 0, w, h], fill=(30, 30, 40))
        for i in range(5):
            x = 14 + i * 34
            d.rounded_rectangle([x, h // 2 - 8, x + 26, h // 2 + 8], radius=8,
                                fill="white" if i % 2 == 0 else (255, 210, 31))
        d.rectangle([w // 2 - 30, 10, w // 2 + 30, 26], fill=(120, 90, 60))
        # balance scale with a "?" — quantity unverified, no number shown
        d.line([w - 30, 8, w - 30, 34], fill=GOLD, width=2)
        d.line([w - 46, 12, w - 14, 12], fill=GOLD, width=2)
        d.arc([w - 46, 12, w - 36, 26], 0, 180, fill=GOLD, width=2)
        d.arc([w - 24, 12, w - 14, 26], 0, 180, fill=GOLD, width=2)
        d.text((w - 30, 30), "?", font=F_ART2, fill=GOLD, anchor="ma")
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
        gj = json.load(f)
    polys = []
    for feat in gj["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            polys.append(geom["coordinates"])
        elif geom["type"] == "MultiPolygon":
            polys.extend(geom["coordinates"])
    for poly in polys:
        for ring in poly:
            pts = []
            for lon, lat in ring:
                px = (lon + 180.0) / 360.0 * mw
                py = (90.0 - lat) / 180.0 * mh
                pts.append((px, py))
            # filled continents (v5: like the top entries), not dots
            d.polygon([(x0 + px, y0 + py) for px, py in pts],
                      fill=SAND)

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (90.0 - lat) / 180.0 * mh)

    for n, (lon, lat) in DOTS.items():
        px, py = proj(lon, lat)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=NAVY)
    for n, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        dx, dy = PIN_OFF.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            # leader line from the true spot to the moved pin circle
            d.line([px, py, px + dx, py + dy], fill=RED, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
            px, py = px + dx, py + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline="white")
        t = str(n)
        tw = d.textlength(t, font=F_PIN)
        d.text((px - tw / 2, py - 5), t, font=F_PIN, fill="white")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead 0-109: date in the top-1 face (Liberation Serif Bold = Times) ----
    d.rectangle([12, 8, 86, 80], fill=RED)
    d.text((49, 12), "NOV", font=F_DATE2, fill="white", anchor="ma")
    d.text((49, 26), "20", font=F_DATE, fill="white", anchor="ma")
    d.text((49, 60), "FRI · 2026", font=F_DATE2, fill="white", anchor="ma")
    d.text((98, 1), "THE WORLD IN ONE DAY", font=F_EYE, fill=RED)
    d.line([98, 20, 1012, 20], fill=INK, width=1)
    d.text((98, 11), "Friday 20 November 2026", font=F_TITLE, fill=INK)
    d.text((98, 84), "Akvan hits Odisha · Russian missiles strike Kyiv's bridges · "
           "COP31 deadlocks on fossil fuels",
           font=F_DECKLINE, fill=RED)
    d.text((1012, 1), "36 STORIES · 6 REGIONS · ONE PAGE",
           font=F_EYE, fill=INK, anchor="ra")
    d.rectangle([0, 109, W, 112], fill=GOLD)

    # ---- big-numbers strip 111-149 ----
    sw6 = (W - 24) / len(STATS)
    for si, (val, cap) in enumerate(STATS):
        sx = 12 + si * sw6
        if si > 0:
            d.line([sx - 6, 117, sx - 6, 149], fill=RULE, width=1)
        d.text((sx + 4, 115), val, font=F_STATB, fill=NAVY)
        d.text((sx + 4, 137), cap, font=F_STATC, fill=GREY)

    # ---- THE DAY BY HOURS timeline 155-187 ----
    d.rectangle([12, 155, 100, 187], fill=RED)
    d.text((56, 156), "THE DAY", font=F_TTIME, fill="white", anchor="ma")
    d.text((56, 170), "BY HOURS", font=F_TTIME, fill="white", anchor="ma")
    bx = 104
    bw = (W - 12 - bx) / 8.0
    for i, (t, txt) in enumerate(TIMELINE):
        cx = bx + i * bw
        if i > 0:
            d.line([cx, 157, cx, 185], fill=RULE, width=1)
        d.text((cx + 5, 158), t, font=F_TTIME, fill=NAVY)
        d.text((cx + 5, 170), txt, font=F_TTEXT, fill=INK)
    d.line([12, 189, W - 12, 189], fill=RULE, width=1)

    # ---- heroes 192-378: lead 396 wide, rails 294; each card boxed like top 1 ----
    hy = 192
    hws = [396, 294, 294]
    for i, (num, reg, topic, src, status, head, deck, big, small, key) in enumerate(FRONT[:3]):
        hw = hws[i]
        cx = 12 + sum(hws[:i]) + 8 * i
        im = art_image(key, hw, 90)
        idd = ImageDraw.Draw(im)
        if key == "summit":
            focal_text(idd, 0, 0, hw, 90, big, small, F_FOC23, F_FOC23_S, "YELLOW", True)
        elif key == "gta":
            focal_text(idd, 0, 0, hw, 90, big, small, F_FOC, F_FOC_S, "WHITE", True)
        else:
            art_text(im, idd, 0, 0, hw, 90, big, small, F_LBL, F_LBL_S)
        img.paste(im, (cx, hy))
        d.rectangle([cx, hy + 90, cx + hw, hy + 106], fill=NAVY)
        pw = d.textlength(status, font=F_PILL) + 10
        d.rounded_rectangle([cx + 8, hy + 93, cx + 8 + pw, hy + 103],
                            radius=2, fill=PILL_COL[status])
        d.text((cx + 13, hy + 92), status, font=F_PILL, fill="white")
        d.text((cx + 14 + pw, hy + 91), "%d. %s · %s" % (num, reg, topic),
               font=F_KICK, fill="white")
        sw = d.textlength(src, font=F_SRC)
        d.text((cx + hw - 8 - sw, hy + 91), src, font=F_SRC, fill=GOLD)
        lines = wrap(d, head, F_HEAD, hw - 16, max_lines=2)
        for j, ln in enumerate(lines):
            d.text((cx + 8, hy + 110 + j * 22), ln, font=F_HEAD, fill=INK)
        dlines = wrap(d, deck, F_DECK, hw - 16, max_lines=2)
        for j, ln in enumerate(dlines):
            d.text((cx + 8, hy + 110 + len(lines) * 22 + 2 + j * 14),
                   ln, font=F_DECK, fill=(60, 60, 60))
        # box around the whole card, like top 1 (1px ink, fixed bottom per row)
        d.rectangle([cx, hy, cx + hw, hy + 186], outline=INK, width=1)

    # ---- smalls 384-711 (2 rows x 5, image 196x80); each card boxed like top 1 ----
    sw_ = 196
    for r in range(2):
        for c in range(5):
            k = 3 + r * 5 + c
            num, reg, topic, src, status, head, deck, big, small, key = FRONT[k]
            cx = 12 + c * (sw_ + 8)
            cy = 384 + r * 166
            im = art_image(key, sw_, 80)
            idd = ImageDraw.Draw(im)
            art_text(im, idd, 0, 0, sw_, 80, big, small, F_LBL2, F_LBL2_S)
            img.paste(im, (cx, cy))
            d.rectangle([cx, cy + 80, cx + sw_, cy + 95], fill=NAVY)
            d.text((cx + 4, cy + 81), "%d. %s · %s" % (num, reg, topic),
                   font=F_KICK_S, fill="white")
            pw = d.textlength(status, font=F_PILL) + 10
            d.rounded_rectangle([cx + sw_ - 4 - pw, cy + 82, cx + sw_ - 4, cy + 92],
                                radius=2, fill=PILL_COL[status])
            d.text((cx + sw_ + 1 - pw, cy + 81), status, font=F_PILL, fill="white")
            lines = wrap(d, head, F_HEAD_S, sw_ - 16, max_lines=2)
            for j, ln in enumerate(lines):
                d.text((cx + 8, cy + 99 + j * 17), ln, font=F_HEAD_S, fill=INK)
            dlines = wrap(d, deck + " — " + src, F_DECK_S, sw_ - 16, max_lines=2)
            for j, ln in enumerate(dlines):
                d.text((cx + 8, cy + 99 + len(lines) * 17 + 1 + j * 13),
                       ln, font=F_DECK_S, fill=(60, 60, 60))
            d.rectangle([cx, cy, cx + sw_, cy + 161], outline=INK, width=1)

    # ---- map + also 716-956 (map taller, also-list roomier) ----
    my = 716
    d.text((12, my), "WHERE IT HAPPENED", font=F_SEC, fill=INK)
    d.line([12, my + 16, 348, my + 16], fill=INK, width=1)
    d.rectangle([12, my + 22, 348, my + 172], fill=OCEAN, outline=RULE, width=1)
    draw_map(d, 12, my + 22, 336, 150)
    d.text((12, my + 176), "Red numbers 1–13, dark dots 14–36.",
           font=F_TTEXT, fill=GREY)
    # how-sure-are-we legend under the map (was the stats row)
    d.text((12, my + 192), "HOW SURE ARE WE?", font=F_SEC, fill=INK)
    for li, (st, expl) in enumerate(LEGEND):
        ly = my + 210 + li * 12
        d.rectangle([12, ly, 20, ly + 8], fill=PILL_COL[st])
        d.text((24, ly - 1), st, font=F_LEGEND, fill=INK)
        d.text((86, ly - 1), expl, font=F_LEGEND, fill=GREY)

    ax = 364
    d.text((ax, my), "ALSO ON FRIDAY 20 NOVEMBER", font=F_SEC, fill=INK)
    d.text((1012, my), "23 MORE STORIES", font=F_SEC, fill=INK, anchor="ra")
    d.line([ax, my + 16, 1012, my + 16], fill=INK, width=1)
    colw = 320
    rows = 12
    for i, (num, city, txt) in enumerate(ALSO):
        col = 0 if i < rows else 1
        row = i if i < rows else i - rows
        x = ax + col * (colw + 8)
        y = my + 22 + row * 13
        d.text((x, y), "%d." % num, font=F_ALSO_N, fill=RED)
        full = "%s: %s" % (city, txt)
        lines = wrap(d, full, F_ALSO, colw - 22, max_lines=1)
        d.text((x + 20, y), lines[0] if lines else "", font=F_ALSO, fill=INK)

    # ---- date check 964-992: thin 2-line band (was a 40px box) ----
    dy = 964
    d.rectangle([12, dy, 1012, dy + 28], outline=RED, width=2)
    chk = ("DATE CHECK — Left out, first reported Thursday 19 November: Shenzhen "
           "trilateral summit + peace declaration · Anthropic's $2T Nasdaq debut · "
           "Akvan's approach + evacuations · Kyiv embassy damage · ICJ genocide "
           "ruling read. Not yet news: COP31's final agreed text (talks run on).")
    clines = wrap(d, chk, F_DATECHK, 976, max_lines=2)
    for j, ln in enumerate(clines):
        d.text((20, dy + j * 12), ln, font=F_DATECHK, fill=INK)

    # ---- footer 998-1021 ----
    fy = 998
    d.text((512, fy), "Reads at three sizes: the date and 3 leads at thumbnail size · "
           "13 pictures at half size · all 36 stories at full size.",
           font=F_FOOT, fill=GREY, anchor="ma")
    d.text((512, fy + 13), "Pins 1–13, dots 14–36. Sources: AP · Reuters · AFP · IMD · "
           "ICJ · UNFCCC · USGS. Original illustrations.",
           font=F_FOOT, fill=GREY, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    img.save(out)
    print("saved", out, os.path.getsize(out), "bytes")
    if PROBLEMS:
        print("PROBLEMS:")
        for p in PROBLEMS:
            print(" -", p)
    else:
        print("no truncation")


if __name__ == "__main__":
    main()
