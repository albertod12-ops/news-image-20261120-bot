#!/usr/bin/env python3
"""news-image-20261120 v5: 36 stories, newspaper front page, top-3 selection rebuild.
Draws entry.png (1024x1024, deterministic) from world.geo.json only.
v5 (on the v4 design — cream paper, black serif masthead, 6-number strip,
region bar, solid art banners): the SELECTION is rebuilt from the live
research in research-v5.md — the 5 stories no top-3 entry draws are out
(An-12 demoted to also-list 26; Sri Lanka rates, California quake, Rikers
dropped), 5 verified missing stories are drawn (Japan CPI, Phillips 118,
Bukele third term, Poland missile, Italy CGIL strike replacing the wrong
"25+ nations" framing), Kyiv/COP31/markets facts corrected, also-list
rebuilt 11-out/11-in, 7 regions (Oceania new). Design baseline (user-approved
2026-11-20): boxed 1px INK cards, LiberationSerif-Bold headlines +
LiberationSerif decks. CONTENT ONLY changed for Friday 20 Nov 2026.
NOTE: the first draw.py run right after an edit can render the pre-edit file
— always verify with 2-3 runs and take the later sha.
Run: python3 draw.py  -> writes entry.png in this directory."""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (247, 242, 231)
NEARWHITE = (253, 250, 242)
NAVY_DARK = (12, 28, 58)
LAND_TAN = (214, 196, 150)
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
    # v5.6: two-digit pins ("12"/"13" = 12.6px at 11px) overflow the 14px
    # circle; 9px (10.3px) leaves a real margin. Single digits stay 11px.
    ("F_PIN2", "NotoSans-Bold.ttf", 9, FNOTO),
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
    # smaller steps so the solid art banner auto-fits long label pairs
    ("F_LBL2_11", "NotoSans-Black.ttf", 11, FNOTO),
    ("F_LBL2_10", "NotoSans-Black.ttf", 10, FNOTO),
    ("F_LBL2_9", "NotoSans-Black.ttf", 9, FNOTO),
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

# num, region, topic, source, status, headline, deck, art big, art small, art key
FRONT = [
    (1, "ODISHA", "STORM", "IMD", "REPORTED",
     "Cyclone Akvan slams into Odisha",
     "Landfall 8:00–11:20am, gusts to 90 km/h; 3.7 lakh evacuated, 9,300 shelters open.",
     "AKVAN", "3.7 LAKH EVACUATED", "akvan"),
    (2, "KYIV", "WAR", "REUTERS", "REPORTED",
     "Russian missiles strike Kyiv's bridges",
     "110+ missiles, 400+ drones; three Dnipro crossings hit; 9 killed, 28 hurt.",
     "KYIV BRIDGES", "3 BRIDGES HIT", "kyiv"),
    (3, "ANTALYA", "CLIMATE", "CARBON BRIEF", "REPORTED",
     "COP31's final day ends in fossil-fuel deadlock",
     "Draft 2 drops fossil fuels and the $120bn target; '35 by 35' electrification survives.",
     "COP31", "DRAFT DROPS PHASE-OUT", "cop31"),
    (4, "TOKYO", "MARKETS", "REUTERS", "REPORTED",
     "AI sell-off sinks Asia",
     "Four Asian indexes sink; Taiex worst week since 1990.",
     "ASIA SINKS", "4 INDEXES DOWN", "selloff"),
    (5, "BRUSSELS", "DEAL", "AP · REUTERS", "REPORTED",
     "UK and EU agree post-Brexit reset",
     "Youth mobility ~100,000 a year; food and emissions links.",
     "UK–EU DEAL", "RESET AGREED", "ukeu"),
    (6, "THE HAGUE", "LAW", "ICJ", "REPORTED",
     "World reacts to Myanmar genocide ruling",
     "First state held liable; capitals and Rohingya groups respond.",
     "MYANMAR GUILTY", "9–6 · FIRST STATE LIABLE", "icj"),
    (7, "ROME", "LABOUR", "REUTERS", "REPORTED",
     "Italy's general strike fills 100 squares",
     "CGIL 24-hr strike; >1m march; vs €26bn 2027 budget.",
     "ON STRIKE", "100+ SQUARES", "italy"),
    (8, "BAGHDAD", "SECURITY", "REUTERS", "REPORTED",
     "Iraqi forces move on militia stronghold",
     "Troops enter Jurf al-Sakhar, Kataib Hezbollah's base.",
     "JURF AL-SAKHAR", "MILITIA BASE", "iraq"),
    (9, "GAZA", "WAR", "REUTERS", "REPORTED",
     "Israeli tanks cross Gaza truce line",
     "First ground operation since the ceasefire began.",
     "GAZA LINE", "FIRST SINCE TRUCE", "gaza"),
    (10, "TOKYO", "ECONOMY", "REUTERS", "REPORTED",
     "Japan inflation stays above target",
     "Core CPI 2.2%, headline 2.3%; BoJ hike case cements.",
     "CPI 2.3%", "ABOVE 2% TARGET", "cpi"),
    (11, "WELLINGTON", "SPORT", "ICC · AP", "REPORTED",
     "Phillips' 118 makes history",
     "118 off 216; first 100s in all 3 formats vs India in one year.",
     "PHILLIPS 118", "FIRST IN ALL FORMATS", "cricket"),
    (12, "SAN SALVADOR", "POLITICS", "REUTERS", "REPORTED",
     "Bukele registers for third term",
     "Filed 19 Nov for 28 Feb 2027 vote; vs 4 rivals; polls 55–70%.",
     "THIRD TERM", "BUKELE FILES", "bukele"),
    (13, "WARSAW", "SECURITY", "REUTERS", "REPORTED",
     "Russian missile lands in Poland",
     "Kh-101 down in Poland; 3 objects in its airspace.",
     "MISSILE IN POLAND", "NATO ALERT", "poland"),
]

# num, city, text
ALSO = [
    (14, "Riyadh", "Saudis intercept 2 Houthi missiles"),
    (15, "Brussels", "EU to summon Russian envoy over Kyiv"),
    (16, "London", "UK pledges 1,000+ drones, £260m for Kyiv"),
    (17, "Paris", "France seeks UN Security Council meeting"),
    (18, "Taipei", "Stocks suffer worst week since 1990 (-17.5%)"),
    (19, "Tokyo", "SoftBank falls more than 16%"),
    (20, "Washington", "IMF warns debt near 100% of GDP"),
    (21, "Rome", "Italy fines Meta €805m over photo access"),
    (22, "Washington", "FAA ground stop strands 1.5m flyers"),
    (23, "Washington", "879,000 AI chips cleared for China"),
    (24, "Washington", "Senate passes energy-permit bill 62-33"),
    (25, "Washington", "US sanctions Comancheros, 'Ndrangheta"),
    (26, "Siberia", "An-12 crash kills 19 in Siberia"),
    (27, "Mercury", "BepiColombo's 8-yr trip ends Saturday"),
    (28, "Seoul", "Ruling party votes to impeach chief justice Jo"),
    (29, "Turkana", "Kenya spuds first commercial oil well"),
    (30, "Yenne", "Senegal migrant boat: 4 dead, dozens missing"),
    (31, "Barcelona", "Cancer pill shrinks tumours in 60.7%"),
    (32, "Beijing", "China holds rates (3.0% / 3.5%)"),
    (33, "Blantyre", "Malawi fuel queues run all night"),
    (34, "Las Vegas", "Russell fastest in wet F1 practice, 1:47.272"),
    (35, "Shenzhen", "Xi hails 'full turnaround' with Albanese"),
    (36, "Europe", "Youth strike in 25+ countries"),
]

STATS = [
    ("370,000", "evacuated in Odisha"),
    ("3", "bridges hit in Kyiv"),
    ("-6.2%", "Taipei's fall"),
    ("2.3%", "Japan CPI headline"),
    ("118", "Phillips in Wellington"),
    ("0", "fossil-fuel mentions"),
]

# v5 region bar: per-region story counts counted from OUR actual 36-story
# list (FRONT 1-13 + ALSO 14-36), assigned by subject, not dateline city.
# EUROPE 10: 2 Kyiv, 5 UK-EU, 7 Italy strike, 13 Poland, 15 Brussels,
#   16 London, 17 Paris, 21 Rome, 31 Barcelona, 36 youth strike.
# ASIA 10: 1 Akvan, 4 Nikkei, 6 ICJ Myanmar, 10 Japan CPI, 18 Taipei,
#   19 Tokyo, 26 An-12, 28 Seoul, 32 Beijing, 35 Shenzhen.
# AMERICAS 6: 12 Bukele, 22 FAA, 23 AI chips, 24 Senate, 25 sanctions,
#   34 Las Vegas.
# MIDDLE EAST 3: 8 Iraq, 9 Gaza, 14 Riyadh.
# AFRICA 3: 29 Turkana, 30 Yenne, 33 Blantyre.
# OCEANIA 1: 11 Phillips (Wellington) — NEW, 7th region (matches #1).
# GLOBAL 3: 3 COP31 (global climate summit), 20 IMF debt warning,
#   27 BepiColombo.
# Total 10+10+6+3+3+1+3 = 36.
# (label, count, fill, text colour)
REGIONS = [
    ("EUROPE", 10, (16, 62, 150), "white"),
    ("ASIA", 10, (179, 34, 44), "white"),
    ("AMERICAS", 6, (90, 60, 140), "white"),
    ("MIDDLE EAST", 3, (196, 142, 8), (17, 17, 17)),
    ("AFRICA", 3, (30, 130, 80), "white"),
    ("OCEANIA", 1, (0, 120, 140), "white"),
    ("GLOBAL", 3, (90, 90, 90), "white"),
]

LEGEND = [
    ("REPORTED", "confirmed, with named sources"),
    ("FORECAST", "a landfall, schedule or draft"),
    ("CLAIM", "one side's claim, unverified"),
]

PINS = {
    1: (85.0, 19.3), 2: (30.5, 50.4), 3: (30.7, 36.9), 4: (139.7, 35.7),
    5: (4.4, 50.8), 6: (4.3, 52.1), 7: (12.5, 41.9), 8: (44.2, 32.8),
    9: (34.4, 31.5), 10: (139.7, 35.7), 11: (174.8, -41.3),
    12: (-89.2, 13.7), 13: (21.0, 52.2),
}
DOTS = {
    14: (46.7, 24.7), 15: (4.4, 50.8), 16: (-0.1, 51.5), 17: (2.4, 48.9),
    18: (121.6, 25.0), 19: (139.7, 35.7), 20: (-77.0, 38.9),
    21: (12.5, 41.9), 22: (-77.0, 38.9), 23: (-77.0, 38.9),
    24: (-77.0, 38.9), 25: (-77.0, 38.9), 26: (96.0, 60.0),
    28: (127.0, 37.5), 29: (35.9, 3.1), 30: (-17.2, 14.7),
    31: (2.2, 41.4), 32: (116.4, 39.9), 33: (35.0, -15.8),
    34: (-115.1, 36.2), 35: (114.1, 22.5), 36: (4.4, 50.8),
}
# v5: 27 BepiColombo has no Earth location (Mercury orbit insertion) —
# it gets no dot, by design.

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


def art_banner(img, d, x, y, w, h, big, small, fill):
    """v4: solid colour banner strip at the TOP of a small card's art box,
    white text on it — the top-3 pattern (their cards carry a red/blue label
    banner, not a bottom scrim). Big label left, small label right on one
    18px line; the big font auto-shrinks (12 -> 11 -> 10 -> 9) until the
    pair fits, so no wording ever changes. Art drawn under the banner's
    18px is hidden behind it, as in a magazine label overlap."""
    if not big and not small:
        return
    d.rectangle([x, y, x + w, y + 18], fill=fill)
    f_big = F_LBL2
    for cand in (F_LBL2, F_LBL2_11, F_LBL2_10, F_LBL2_9):
        if int(d.textlength(big, font=cand)) + int(d.textlength(small, font=F_LBL2_S)) + 14 <= w:
            f_big = cand
            break
    else:
        f_big = F_LBL2_9
        PROBLEMS.append("ART BANNER TOO WIDE: %s / %s" % (big, small))
    # v5.4: text vertically centred in the 18px strip — middle anchor
    # at the strip centre (y+9), not top-anchored at y+3/y+5.
    d.text((x + 6, y + 9), big, font=f_big, fill="white", anchor="lm")
    if small:
        d.text((x + w - 6, y + 9), small, font=F_LBL2_S, fill="white",
               anchor="rm")


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


def _cubic(p0, p1, p2, p3, t):
    mt = 1.0 - t
    return (mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
            + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
            mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
            + 3 * mt * t * t * p2[1] + t ** 3 * p3[1])


def smooth_arrow(img, p0, p1, p2, p3, color, w_tail=8.0, w_tip=5.0,
                 head_len=15.0, head_w=14.0, ss=4):
    """A smooth tapered curved arrow: cubic-bezier centreline sampled at
    81 points, band built from its two offset curves (width tapering
    from w_tail at the tail to w_tip near the head), ending in a clean
    filled arrowhead whose axis aligns with the curve tangent at the
    tip (head ~2.2x band width wide, ~1.6x long). Drawn on a 4x
    supersampled RGBA layer and downscaled with LANCZOS so the edges
    are anti-aliased, not jagged."""
    n = 81
    pts = [_cubic(p0, p1, p2, p3, i / (n - 1)) for i in range(n)]
    seg = [math.hypot(pts[i + 1][0] - pts[i][0],
                      pts[i + 1][1] - pts[i][1]) for i in range(n - 1)]
    back, hi = 0.0, n - 1
    while hi > 0 and back < head_len:
        back += seg[hi - 1]
        hi -= 1

    def tangent(i):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        m = math.hypot(dx, dy) or 1.0
        return dx / m, dy / m

    left, right = [], []
    for i in range(hi + 1):
        t = i / (n - 1)
        hw = (w_tail / 2) * (1 - t) + (w_tip / 2) * t
        tx, ty = tangent(i)
        nx, ny = -ty, tx
        left.append((pts[i][0] + nx * hw, pts[i][1] + ny * hw))
        right.append((pts[i][0] - nx * hw, pts[i][1] - ny * hw))
    tx, ty = tangent(n - 1)
    nx, ny = -ty, tx
    bx, by = pts[hi]
    head = [(p3[0], p3[1]),
            (bx + nx * head_w / 2, by + ny * head_w / 2),
            (bx - nx * head_w / 2, by - ny * head_w / 2)]
    w, h = img.size
    layer = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    fill = color + (255,)
    ld.polygon([(x * ss, y * ss) for x, y in left + right[::-1]], fill=fill)
    ld.polygon([(x * ss, y * ss) for x, y in head], fill=fill)
    layer = layer.resize((w, h), Image.LANCZOS)
    img.paste(layer, (0, 0), layer)


def art_image(key, w, h):
    """Flat-vector picture for one front story, drawn in code."""
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    if key == "akvan":
        # v4: SATELLITE view, like the top-3 heroes — the line-art tornado
        # is gone (it can be restored on request; see NOTES.md). Dark teal
        # Bay of Bengal, the Odisha coast down the left with a Gopalpur dot,
        # a big white spiral cyclone with an eye over the sea, and a white
        # "Landfall · 8 am" strip at the bottom-right. The AKVAN scrim stays
        # bottom-left, as on the other heroes. Original PIL vector code.
        d.rectangle([0, 0, w, h], fill=(8, 64, 88))
        # deeper water, bottom-right
        d.rectangle([0, 78, w, h], fill=(6, 52, 74))
        # the Odisha coast: land down the left edge, wavy shoreline
        land = [(0, 0), (96, 0), (82, 22), (90, 46), (72, 68), (82, 88),
                (70, h), (0, h)]
        d.polygon(land, fill=(216, 196, 150))
        d.polygon([(0, 0), (52, 0), (44, 30), (30, 60), (38, h), (0, h)],
                  fill=(150, 170, 100))
        d.line([(96, 0), (82, 22), (90, 46), (72, 68), (82, 88), (70, h)],
               fill=(240, 235, 220), width=2)
        d.text((10, 8), "ODISHA", font=F_ART2_S, fill=(60, 50, 30))
        # rain bands over the sea, short diagonal streaks around the storm
        for rx, ry in ((150, 12), (180, 8), (300, 16), (330, 30), (150, 88),
                       (310, 84), (350, 60), (120, 40), (360, 12)):
            d.line([rx, ry, rx - 6, ry + 10], fill=(170, 205, 225), width=2)
        # the cyclone: a SPIRAL, not concentric rings (v4 fix: the first
        # version read as a target) — arcs of growing radius, each rotated
        # further round, plus two thick comma arms sweeping out to the
        # edges, and a dark eye at the centre. Centre (250, 50).
        cx, cy = 250, 50
        for rr, a0, a1, wd in ((12, 40, 300, 3), (20, 120, 20, 3),
                               (28, 200, 110, 3), (36, 280, 190, 2),
                               (44, 0, 270, 2)):
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1,
                  fill="white", width=wd)
        # spiral arms: curved sweeps from the rings out to the edges
        d.arc([cx - 62, cy - 44, cx + 62, cy + 44], 300, 40,
              fill=(220, 235, 245), width=4)
        d.arc([cx - 70, cy - 34, cx + 70, cy + 34], 120, 220,
              fill=(200, 220, 240), width=3)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(8, 64, 88),
                  outline="white", width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill="white")
        # Gopalpur dot on the coast, red with a white ring + label, clear
        # of the AKVAN scrim (which starts at the bottom-left, y ~66+)
        d.ellipse([78, 54, 88, 64], fill=RED, outline="white", width=2)
        d.text((92, 55), "Gopalpur", font=F_LBL2_S, fill="white",
               stroke_width=1, stroke_fill=(0, 0, 0))
        # white caption strip, bottom-right, over the sea (like #1)
        d.rectangle([248, 84, w - 4, 100], fill="white")
        d.text((318, 92), "Landfall · 8 am", font=F_ART2_S, fill=RED,
               anchor="mm")
    elif key == "kyiv":
        # v3: DENSITY — a night scene filling the whole frame: stars,
        # skyline with lit windows across the back, river with reflections
        # below, three towers + cables, deck with a broken middle span,
        # fire + a big smoke plume, debris and ripples. No empty dark top.
        d.rectangle([0, 0, w, h], fill=(14, 24, 52))
        # stars across the sky
        for sx, sy in ((10, 6), (40, 10), (90, 4), (130, 8), (180, 5),
                       (230, 9), (270, 4), (286, 12), (160, 12), (60, 14),
                       (20, 18), (110, 2), (200, 14), (250, 2), (70, 20),
                       (150, 2), (285, 20), (100, 16)):
            d.ellipse([sx, sy, sx + 2, sy + 2], fill="white")
        # v4: missile trails arcing across the sky — dashed orange/white
        # curves from the top edge down toward the bridges, each with a
        # bright head. Drawn as short dashes along a quadratic arc.
        for (x0, y0, xc, yc, x1, y1) in (
                (30, 0, 70, 22, 148, 38), (190, 0, 220, 18, 236, 36),
                (270, 0, 250, 24, 130, 40)):
            prev = None
            for ti in range(21):
                t = ti / 20
                qx = int((1 - t) ** 2 * x0 + 2 * (1 - t) * t * xc + t ** 2 * x1)
                qy = int((1 - t) ** 2 * y0 + 2 * (1 - t) * t * yc + t ** 2 * y1)
                if prev is not None and ti % 2 == 0:
                    d.line([prev, (qx, qy)], fill=(255, 180, 80), width=2)
                prev = (qx, qy)
            d.ellipse([x1 - 3, y1 - 3, x1 + 3, y1 + 3], fill=(255, 220, 120))
        # Kyiv skyline across the whole back, lit windows (19 Nov _skyline)
        _skyline(d, w, 52, 46, (38, 58, 96), 7)
        # a gold-domed church in the skyline, right side
        d.rectangle([238, 28, 262, 46], fill=(120, 140, 180))
        d.ellipse([240, 18, 260, 32], fill=GOLD)
        d.line([250, 10, 250, 18], fill=GOLD, width=2)
        # the river, from the deck line down, with reflections
        d.rectangle([0, 46, w, h], fill=(18, 54, 100))
        for ry in (56, 64, 72, 80, 88, 96):
            for rx0, rx1 in ((8, 60), (70, 120), (130, 200), (210, 286)):
                d.line([rx0, ry, rx1, ry], fill=(70, 120, 180), width=1)
        # firelight reflected under each fire, on the water
        for fx0, fx1 in ((132, 168), (222, 248)):
            for ry in (58, 66, 74):
                d.line([fx0 + 4, ry, fx1 - 4, ry], fill=(255, 170, 60),
                       width=2)
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
        # v4: a third, smaller fire on the left span + its smoke, and a
        # taller smoke column over the main break (more fires + smoke)
        d.ellipse([28, 34, 48, 46], fill=(255, 140, 40))
        d.ellipse([33, 38, 43, 44], fill=(255, 220, 80))
        d.polygon([(32, 36), (30, 28), (36, 34)], fill=(255, 140, 40))
        d.ellipse([34, 22, 46, 32], fill=(205, 205, 205))
        d.ellipse([142, -2, 158, 12], fill=(225, 225, 225))
        d.ellipse([128, 2, 142, 14], fill=(210, 210, 210))
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
        # v4: red FINAL DAY · DEADLOCK banner, bottom-right (like #2's hero
        # red box) — clear of the globe (ends y68), the thermometer bulb
        # (ends y76) and the COP31 scrim (bottom-left, ends ~x150). The box
        # is 25px tall so both 11px lines sit inside it with padding.
        d.rectangle([204, 78, 290, 103], fill=(179, 34, 44))
        d.text((247, 80), "FINAL DAY", font=F_ART2_S, fill="white",
               anchor="ma")
        d.text((247, 91), "DEADLOCK", font=F_ART2_S, fill="white",
               anchor="ma")
    elif key == "icj":
        # the World Court as a temple: pediment, 15 columns, steps.
        # The first 9 columns are paper, the last 6 ink — the 9-6 vote.
        # v4: pediment + flag shifted down so the solid top banner (y0-18)
        # clears them (apex was y12, flag was y8-24).
        d.rectangle([0, 0, w, h], fill=(226, 218, 196))
        pediment = [(104, 44), (198, 20), (292, 44)]
        d.polygon(pediment, fill=(120, 110, 95))
        col_top, col_bottom, col_w = 44, 76, 7
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
        d.line([213, 44, 213, 76], fill=(179, 34, 44), width=3)
        # Myanmar flag top left (yellow/green/red + white star), white outline
        flag_bands = (((24, 29), (254, 203, 0)), ((29, 34), (0, 140, 60)),
                      ((34, 40), (220, 40, 40)))
        for (band_y0, band_y1), band_col in flag_bands:
            d.rectangle([12, band_y0, 38, band_y1], fill=band_col)
        d.rectangle([12, 24, 38, 40], outline="white", width=1)
        _star(d, 25, 32, 5, 2)
        # gold scales of justice, left, below the flag (the recognisable object)
        scale_x = 60
        d.line([scale_x, 34, scale_x, 58], fill=GOLD, width=2)
        d.line([44, 38, 76, 38], fill=GOLD, width=2)
        for pan_x in (48, 64):
            d.polygon([(pan_x, 38), (pan_x + 8, 38), (pan_x + 4, 48)],
                      fill=GOLD)
        d.ellipse([56, 58, 64, 64], fill=GOLD)
    elif key == "selloff":
        # v5.2: user rejected the v5.1 3D blue bars — redraw as the
        # VERTICAL MIRROR of card 10 (the CPI rising chart, which the
        # user likes): same style — rainbow bars + ONE thick dark
        # curved arrow — but flipped: bars DESCEND left to right and
        # the arrow curves DOWN from top-left to bottom-right. Same
        # verified Friday data: Taipei -6.2, Seoul -5.2, Tokyo -5.1,
        # Hong Kong -1.9 (tallest to shortest, colours in the same
        # rainbow palette order as card 10: green, yellow, orange,
        # red). Art is 196x80 with the solid banner over y0-18; bars
        # sit on baseline y56, names + values in two lines below.
        # Original PIL vector code.
        d.rectangle([0, 0, w, h], fill=(246, 242, 233))
        for gy in range(20, 56, 12):
            d.line([0, gy, w, gy], fill=(228, 223, 208), width=1)
        base = 56
        bars = (("TAIPEI", "-6.2%", 32, (60, 180, 80)),
                ("SEOUL", "-5.2%", 27, (250, 200, 40)),
                ("TOKYO", "-5.1%", 26, (240, 130, 30)),
                ("HONG KONG", "-1.9%", 11, (220, 50, 50)))
        # flat rainbow bars, descending left to right, lighter top
        # strip per bar (same treatment as card 10's rising bars)
        for i, (name, val, bh, col) in enumerate(bars):
            bx = 12 + i * 48
            top = base - bh
            light = tuple(min(255, c + 60) for c in col)
            d.rectangle([bx, top, bx + 32, base], fill=col)
            d.rectangle([bx, top, bx + 32, top + 2], fill=light)
        d.line([6, base, w - 4, base], fill=(180, 175, 160), width=1)
        # v5.4: arrow path shrunk for clearance — tail top edge 6px
        # below the banner (was touching it), head bottom 8px above the
        # bar labels (was ~2px). Same smooth tapered style and colour.
        smooth_arrow(img, (10, 28), (58, 26), (118, 34), (180, 50),
                     (30, 30, 40))
        # names + values in two lines under the bars; the last name is
        # clamped so it clears the right edge ("HONG KONG" is 51px wide)
        for i, (name, val, bh, col) in enumerate(bars):
            cx = 12 + i * 48 + 16
            nw = d.textlength(name, font=F_LBL2_S)
            cx = min(cx, 192 - nw / 2)
            d.text((cx, 61), name, font=F_LBL2_S, fill=INK, anchor="ma")
            d.text((12 + i * 48 + 16, 70), val, font=F_LBL2_S, fill=RED,
                   anchor="ma")
    elif key == "ukeu":
        # two flags, one deal: EU stars on the left, the Union Jack's cross
        # on the right, a gold link between them. v4: BIGGER flags — wider
        # star circle (centre dropped to y46 so the top star clears the
        # solid banner), thicker Jack cross.
        d.rectangle([0, 0, w, h], fill=(20, 40, 120))
        for a in range(8):
            sx = 48 + int(32 * math.cos(math.radians(a * 45)))
            sy = 46 + int(26 * math.sin(math.radians(a * 45)))
            _star(d, sx, sy, 5, 2, fill=(255, 210, 31))
        d.rectangle([98, 0, 196, h], fill="white")
        d.rectangle([98, 32, 196, 48], fill=(200, 20, 40))
        d.rectangle([140, 0, 156, h], fill=(200, 20, 40))
        d.line([98, 0, 196, h], fill=(20, 40, 120), width=4)
        d.line([196, 0, 98, h], fill=(20, 40, 120), width=4)
        d.rectangle([90, 34, 106, 46], fill=GOLD)
        d.text((98, 40), "=", font=F_ART2, fill=(20, 20, 20), anchor="mm")
    elif key == "italy":
        # v5: Rome, not Paris — the CGIL general strike. St Peter's dome
        # and colonnade across the back, a tricolour flag, and marchers
        # with placards filling the street. The old "strike" branch (Paris
        # facades, "25+ COUNTRIES" banner) is gone with the wrong framing.
        # Original PIL vector code.
        d.rectangle([0, 0, w, h], fill=(205, 214, 226))
        # St Peter's dome, centre, behind the march (banner covers y0-18)
        d.ellipse([68, 8, 128, 56], fill=(150, 140, 120))
        d.rectangle([92, 2, 104, 16], fill=(150, 140, 120))
        d.ellipse([94, -2, 102, 8], fill=(150, 140, 120))
        # colonnade: a row of small columns under the dome
        d.rectangle([52, 52, 144, 56], fill=(120, 110, 95))
        for cx0 in range(56, 140, 12):
            d.rectangle([cx0, 44, cx0 + 4, 52], fill=(200, 190, 170))
        # the road, full width, with dashes
        d.rectangle([0, 62, w, h], fill=(110, 110, 116))
        d.line([0, 62, w, 62], fill=(60, 60, 65), width=2)
        for dx in range(4, w, 20):
            d.line([dx, 71, dx + 10, 71], fill="white", width=2)
        # tricolour flag on a pole, left — green/white/red vertical bands
        d.line([14, 22, 14, 52], fill=(60, 40, 20), width=2)
        for fi, fcol in enumerate(((0, 140, 60), "white", (200, 40, 40))):
            d.rectangle([14 + fi * 6, 22, 14 + fi * 6 + 6, 32], fill=fcol)
        # five marchers, in stride, placards up on the middle two
        skins = [(200, 140, 90), (220, 180, 140), (190, 130, 85),
                 (210, 160, 110), (200, 140, 90)]
        shirts = [(40, 90, 160), (200, 40, 40), (30, 140, 80),
                  (220, 170, 40), (90, 60, 140)]
        for i, x in enumerate((30, 62, 94, 126, 158)):
            d.ellipse([x + 3, 30, x + 15, 42], fill=skins[i])
            d.ellipse([x + 6, 35, x + 8, 37], fill=(20, 20, 20))
            d.ellipse([x + 10, 35, x + 12, 37], fill=(20, 20, 20))
            d.rectangle([x + 2, 42, x + 14, 56], fill=shirts[i])
            d.line([x + 5, 56, x + 1, 68], fill=(20, 20, 20), width=2)
            d.line([x + 9, 56, x + 15, 68], fill=(20, 20, 20), width=2)
            if i == 0:
                d.line([x + 4, 44, 46, 40], fill=skins[i], width=2)
            if i == 4:
                d.line([x + 10, 44, 156, 40], fill=skins[i], width=2)
            if i in (1, 3):
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
        d.ellipse([160, 18, 178, 30], fill=(240, 230, 200))
        d.ellipse([166, 20, 188, 28], fill=(240, 230, 200))
    elif key == "gaza":
        # v3: DENSITY — a desert scene filling the frame: sun + clouds,
        # layered dunes, a distant wall with watchtower, a dust cloud
        # behind the tracks, and a tank twice as big as v2, crossing the
        # yellow truce dashes painted on the ground.
        d.rectangle([0, 0, w, h], fill=(240, 215, 160))
        # sun, top-right, and clouds — v4: moved down (y20+) so the solid
        # top banner (y0-18) clears them; the wall top is y34
        d.ellipse([168, 20, 186, 38], fill=(255, 220, 80),
                  outline=(230, 180, 60), width=2)
        d.ellipse([8, 20, 34, 28], fill=(250, 240, 220))
        d.ellipse([20, 24, 48, 32], fill=(250, 240, 220))
        d.ellipse([120, 20, 146, 28], fill=(250, 240, 220))
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
    elif key == "cpi":
        # v5.1: per the user's new reference (5 ascending rainbow bars +
        # one thick dark curved arrow rising) — the v5 navy bars + red
        # zigzag are gone. Same verified CPI data (core 2.2%, headline
        # 2.3%). Light card background kept (not the reference's black).
        # Original PIL vector code.
        d.rectangle([0, 0, w, h], fill=(245, 240, 228))
        for gy in range(18, h, 12):
            d.line([0, gy, w, gy], fill=(210, 205, 190), width=1)
        for gx in range(0, w, 24):
            d.line([gx, 18, gx, h], fill=(228, 223, 208), width=1)
        # five rainbow bars, ascending left to right, baseline y68
        cols = ((60, 180, 80), (250, 200, 40), (240, 130, 30),
                (220, 50, 50), (40, 140, 220))
        for i, col in enumerate(cols):
            bx = 10 + i * 36
            top = 68 - (12 + i * 7)
            d.rectangle([bx, top, bx + 24, 68], fill=col)
            light = tuple(min(255, c + 60) for c in col)
            d.rectangle([bx, top, bx + 24, top + 2], fill=light)
        # v5.4: arrowhead pulled back for clearance — 17px from the
        # "2.3%" focal (was 9px), tail 6px above the coins, head top
        # 14px below the banner. Same smooth tapered style and colour.
        smooth_arrow(img, (8, 62), (44, 60), (90, 52), (134, 33),
                     (30, 30, 40))
        # red 2.3% focal, top-right, clear of the arrowhead (ends x148)
        d.text((192, 24), "2.3%", font=F_ART2, fill=RED, anchor="ra",
               stroke_width=1, stroke_fill="white")
        # gold coins along the bottom
        for cx in (14, 44, 74, 104, 134, 164):
            d.ellipse([cx, 72, cx + 12, 80], fill=GOLD,
                      outline=(180, 130, 20), width=1)
            d.ellipse([cx + 3, 74, cx + 9, 78], fill=(255, 220, 80))
    elif key == "cricket":
        # v5.6: Glenn Phillips 118 at the Basin Reserve — a full match
        # scene, not a bare pitch: packed crowd stands + floodlights
        # behind, green outfield, tan pitch, stumps with bails, and the
        # batsman BIG and mid-swing, bat connecting with the red ball
        # (motion trail flying off it), scoreboard with both lines.
        # The old v5 scene (small stick batsman, bare green, one-line
        # scoreboard) is gone. Original PIL vector code.
        d.rectangle([0, 0, w, h], fill=(60, 160, 90))
        # the stands, y20-34: dark stand band + two rows of crowd heads
        d.rectangle([0, 20, w, 34], fill=(45, 55, 70))
        crowd_cols = ((220, 180, 140), (180, 120, 80), (240, 200, 160),
                      (200, 60, 60), (60, 120, 200), (240, 240, 240),
                      (30, 30, 30), (250, 200, 40))
        for row, cy in ((0, 25), (1, 30)):
            for i, hx in enumerate(range(6, w - 4, 7)):
                col = crowd_cols[(i + row * 3) % len(crowd_cols)]
                d.ellipse([hx - 2, cy - 2, hx + 2, cy + 2], fill=col)
        d.rectangle([0, 34, w, 36], fill=(220, 220, 220))
        # floodlight poles at both edges, lamp heads + pale light cones
        for px0 in (6, 190):
            d.line([px0, 20, px0, 34], fill=(120, 125, 135), width=2)
            d.rectangle([px0 - 5, 20, px0 + 5, 26], fill=(90, 95, 105))
            for lx in (px0 - 3, px0 + 1):
                d.ellipse([lx - 1, 21, lx + 1, 23], fill="white")
        d.polygon([(4, 26), (14, 26), (30, 44), (0, 44)],
                  fill=(235, 235, 195))
        d.polygon([(182, 26), (192, 26), (196, 44), (166, 44)],
                  fill=(235, 235, 195))
        # mowing stripes across the outfield, below the stands
        for sy in range(36, h, 16):
            d.rectangle([0, sy, w, sy + 8], fill=(52, 148, 82))
        # the pitch: tan strip up the middle, crease lines in white
        d.rectangle([88, 38, 110, h], fill=(214, 186, 140))
        d.line([88, 42, 110, 42], fill="white", width=2)
        d.line([88, 74, 110, 74], fill="white", width=2)
        # stumps at the top of the pitch, three pale sticks + bails
        for sx in (94, 98, 102):
            d.rectangle([sx, 38, sx + 2, 48], fill=(240, 220, 140))
        d.line([94, 38, 104, 38], fill=(240, 220, 140), width=1)
        # the batsman, BIG and mid-swing: black NZ shirt, white pads,
        # front leg planted, bat swung high through the ball
        d.ellipse([120, 46, 130, 56], fill=(200, 140, 90))
        d.rectangle([120, 56, 131, 70], fill=(20, 20, 25))
        d.line([122, 70, 116, 79], fill="white", width=4)
        d.line([129, 70, 135, 79], fill="white", width=4)
        d.line([128, 58, 142, 48], fill=(200, 140, 90), width=3)
        d.line([142, 48, 156, 34], fill=(200, 170, 110), width=5)
        # the red ball AT the bat's tip (the moment of contact) + trail
        d.ellipse([155, 29, 163, 37], fill=(200, 40, 40),
                  outline="white", width=1)
        d.line([(166, 27), (172, 22)], fill="white", width=2)
        # fielders: small white dots on the outfield
        for fx, fy in ((28, 58), (58, 70), (170, 52)):
            d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill="white")
        # scoreboard, bottom-right: white box, two lines "NZ 368" +
        # "PHILLIPS 118" (51.7px at 8px bold in a 58px box — fits)
        d.rectangle([136, 58, 194, 78], fill="white", outline=INK, width=1)
        d.text((165, 63), "NZ 368", font=F_LBL2_S, fill=INK, anchor="mm")
        d.text((165, 72), "PHILLIPS 118", font=F_LBL2_S, fill=INK,
               anchor="mm")
    elif key == "bukele":
        # v5.6: Bukele registers for a third term — a full rally scene,
        # not a lone ballot box: the El Salvador flag fills the card, a
        # stylised candidate (flat-vector figure, no likeness) at a
        # podium with a microphone and one arm raised to the crowd,
        # supporters with small flags along the bottom, and the ballot
        # box "2027" with ballots at right. The old v5 scene (flag +
        # box only) is gone. Original PIL vector code.
        d.rectangle([0, 18, w, 38], fill=(0, 71, 171))
        d.rectangle([0, 38, w, 58], fill="white")
        d.rectangle([0, 58, w, h], fill=(0, 71, 171))
        # small coat-of-arms nod on the white band, left: green triangle
        # + gold sun
        d.polygon([(27, 42), (18, 54), (36, 54)], fill=(0, 120, 60))
        d.ellipse([24, 37, 30, 43], fill=GOLD)
        # supporters along the bottom, left: heads + two small flags
        for hx, col in ((10, (220, 180, 140)), (22, (180, 120, 80)),
                        (34, (240, 200, 160)), (46, (200, 140, 90)),
                        (58, (170, 110, 70))):
            d.ellipse([hx - 3, 71, hx + 3, 79], fill=col)
            d.ellipse([hx - 3, 71, hx + 3, 74], fill=(30, 25, 20))
        for fx, fy in ((46, 54), (58, 52)):
            d.line([fx, fy + 6, fx, 72], fill=(60, 40, 20), width=1)
            d.rectangle([fx, fy, fx + 12, fy + 3], fill=(0, 71, 171))
            d.rectangle([fx, fy + 3, fx + 12, fy + 6], fill="white")
        # one supporter + flag at the far right, past the ballot box
        d.ellipse([185, 71, 191, 79], fill=(220, 180, 140))
        d.ellipse([185, 71, 191, 74], fill=(30, 25, 20))
        d.line([188, 60, 188, 72], fill=(60, 40, 20), width=1)
        d.rectangle([188, 56, 196, 59], fill=(0, 71, 171))
        d.rectangle([188, 59, 196, 62], fill="white")
        # the candidate at the podium: dark suit, white shirt, red tie,
        # one arm raised waving to the crowd (stylised, no likeness)
        d.ellipse([83, 27, 99, 35], fill=(30, 25, 20))
        d.ellipse([84, 31, 98, 44], fill=(200, 150, 110))
        d.rectangle([74, 42, 108, 58], fill=(20, 30, 60))
        d.polygon([(88, 42), (96, 42), (91, 52)], fill="white")
        d.line([91, 44, 91, 54], fill=RED, width=2)
        d.line([104, 46, 118, 32], fill=(20, 30, 60), width=4)
        d.ellipse([115, 29, 121, 35], fill=(200, 150, 110))
        # microphone on the podium, in front of the candidate
        d.line([90, 58, 88, 46], fill=(60, 60, 60), width=2)
        d.ellipse([86, 43, 90, 47], fill=(40, 40, 40))
        # the podium: dark navy, white front panel + gold seal
        d.rectangle([68, 58, 112, 80], fill=(10, 20, 50))
        d.rectangle([74, 64, 106, 76], fill="white")
        d.ellipse([87, 67, 93, 73], fill=GOLD)
        # the ballot box, right: dark navy, slot, ballot half in, "2027"
        d.rectangle([140, 44, 180, 72], fill=(20, 40, 90),
                    outline="white", width=2)
        d.rectangle([150, 44, 170, 48], fill=(10, 20, 50))
        d.polygon([(152, 28), (166, 26), (168, 44), (154, 46)],
                  fill="white", outline=(120, 120, 120))
        d.line([156, 32, 164, 31], fill=RED, width=2)
        d.text((160, 58), "2027", font=F_ART2_S, fill="white", anchor="mm")
        d.ellipse([172, 62, 178, 68], fill=GOLD, outline="white", width=1)
    elif key == "poland":
        # v5: a Russian missile lands in Poland — a green field with a
        # smoking crater, debris, an airport control tower, and a Polish
        # white-over-red flag. Distinct from the Kyiv hero (night bridge
        # scene). The old "rikers" branch (cell block + CLOSED stamp) is
        # gone with the story. Original PIL vector code.
        d.rectangle([0, 0, w, h], fill=(200, 210, 225))
        # the field, lower half
        d.rectangle([0, 42, w, h], fill=(90, 160, 90))
        for fy in range(46, h, 12):
            d.line([0, fy, w, fy], fill=(80, 145, 80), width=1)
        # the crater: dark pit with a brown rim, left of centre
        d.ellipse([38, 50, 86, 68], fill=(90, 70, 50))
        d.ellipse([44, 53, 80, 65], fill=(40, 30, 22))
        # debris scattered around the crater
        for dx0, dy0, dw, dh in ((30, 48, 8, 3), (88, 56, 7, 3),
                                 (56, 70, 9, 3), (96, 46, 6, 3)):
            d.rectangle([dx0, dy0, dx0 + dw, dy0 + dh], fill=(40, 40, 40))
        # smoke column rising from the crater, drifting right
        for ex, ey, er, col in ((62, 44, 6, (150, 150, 150)),
                                 (70, 34, 7, (130, 130, 130)),
                                 (80, 26, 6, (160, 160, 160))):
            d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col)
        # Polish flag on a pole, left — white over red
        d.line([14, 26, 14, 60], fill=(60, 40, 20), width=2)
        d.rectangle([14, 26, 32, 33], fill="white")
        d.rectangle([14, 33, 32, 40], fill=(220, 40, 40))
        # airport control tower, right — grey shaft + glass cab
        d.rectangle([150, 34, 162, 76], fill=(120, 125, 135))
        d.rectangle([144, 24, 170, 34], fill=(90, 95, 105))
        d.rectangle([148, 27, 166, 31], fill=(180, 220, 240))
        d.ellipse([154, 20, 158, 24], fill=RED)
    return img

# pixel nudges so clustered pins stay readable (map is small): the pin circle
# moves by (dx, dy) and a thin leader line points back to the true spot.
# Seven pins crowd Europe + the Levant (Kyiv/Antalya/Brussels/The Hague/Rome/
# Gaza/Iraq within ~40x30px), so they are fanned out radially: 6 north-west,
# 7 west, 5 south-west, 2 north-east, 3 south, 9 south, 8 east.
# v5: 10 (Tokyo CPI) shares 4's spot, so it is pushed south-east; 11
# (Wellington) sits at the map's right edge, pulled left; 13 (Warsaw) sits
# ~9px from Kyiv's true spot, pushed south-west.
# v5.6: 4 (Tokyo markets) shared its exact spot with 10 AND sat on the
# coastline with the white Seoul dot touching its left edge, so at page
# size it read as half-covered; it is pushed north-east into the open
# Pacific, clear of 10's circle and leader line.
PIN_OFF = {2: (18, -16), 3: (2, 14), 4: (20, -14), 5: (-6, 26), 6: (-28, -18),
           7: (-30, 8), 8: (16, -14), 9: (-18, 20), 10: (18, 14),
           11: (-14, 0), 13: (-18, 12)}


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
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill="white")
    for n, (lon, lat) in PINS.items():
        px, py = project(lon, lat)
        dx, dy = PIN_OFF.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            # leader line from the true spot to the moved pin circle
            d.line([px, py, px + dx, py + dy], fill=RED, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
            px, py = px + dx, py + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline="white")
        # v5.5: number centred on the circle's exact centre by its measured
        # ink box — the old top-anchored draw at py-5 sat every number ~2px
        # too low (measured on v5.4: dy +1.8..+2.4 on all 13 pins).
        label = str(n)
        # v5.6: two-digit labels use the smaller pin font so they sit
        # fully INSIDE the 14px circle; single digits keep the 11px font.
        fnt = F_PIN2 if len(label) == 2 else F_PIN
        box = d.textbbox((0, 0), label, font=fnt)
        tw, th = box[2] - box[0], box[3] - box[1]
        d.text((px - tw / 2 - box[0], py - th / 2 - box[1]), label,
               font=fnt, fill="white")


def hero_card(img, d, story, x, y, w):
    """One hero card: v4 105px art (was 90), navy kicker strip with status
    pill, a 2-line Times headline and a 2-line serif deck, all inside a 1px
    ink box whose bottom is fixed per row, like the top-1 entry. The card
    interior is near-white on the cream page, like the top 3."""
    num, reg, topic, src, status, head, deck, big, small, key = story
    d.rectangle([x, y, x + w, y + 205], fill=NEARWHITE)
    art = art_image(key, w, 105)
    art_d = ImageDraw.Draw(art)
    art_text(art, art_d, 0, 0, w, 105, big, small, F_LBL, F_LBL_S)
    img.paste(art, (x, y))
    # navy kicker strip: status pill left, "N. REGION · TOPIC" after it,
    # source right in gold. Strip text is centred on the glyph centre.
    d.rectangle([x, y + 105, x + w, y + 121], fill=NAVY)
    pill_w = d.textlength(status, font=F_PILL) + 10
    d.rounded_rectangle([x + 8, y + 108, x + 8 + pill_w, y + 118],
                        radius=2, fill=PILL_COL[status])
    # v5.4: strip text vertically centred on the strip centre (y+113)
    # with middle anchors, not top-anchored at y+106/y+107.
    d.text((x + 13, y + 113), status, font=F_PILL, fill="white",
           anchor="lm")
    d.text((x + 14 + pill_w, y + 113), "%d. %s · %s" % (num, reg, topic),
           font=F_KICK, fill="white", anchor="lm")
    d.text((x + w - 8, y + 113), src, font=F_SRC, fill=GOLD, anchor="rm")
    head_lines = wrap(d, head, F_HEAD, w - 16, max_lines=2)
    for j, line in enumerate(head_lines):
        d.text((x + 8, y + 125 + j * 22), line, font=F_HEAD, fill=INK)
    deck_lines = wrap(d, deck, F_DECK, w - 16, max_lines=2)
    for j, line in enumerate(deck_lines):
        d.text((x + 8, y + 125 + len(head_lines) * 22 + 2 + j * 14),
               line, font=F_DECK, fill=(60, 60, 60))
    d.rectangle([x, y, x + w, y + 205], outline=INK, width=1)


def small_card(img, d, story, x, y):
    """One small card: 80px art with a v4 SOLID colour banner at its top
    (red, navy for the court/rates cards) carrying the art label in white,
    navy kicker strip with the status pill on the right, a 2-line Times
    headline and a 2-line serif deck + source, all inside a 1px ink box
    with a fixed bottom per row. Card interior near-white on cream."""
    num, reg, topic, src, status, head, deck, big, small, key = story
    w = 196
    d.rectangle([x, y, x + w, y + 161], fill=NEARWHITE)
    art = art_image(key, w, 80)
    art_d = ImageDraw.Draw(art)
    banner_fill = NAVY if key in ("icj", "cpi") else RED
    art_banner(art, art_d, 0, 0, w, 80, big, small, banner_fill)
    img.paste(art, (x, y))
    d.rectangle([x, y + 80, x + w, y + 95], fill=NAVY)
    # v5.4: strip text vertically centred on the strip centre (y+87.5)
    # with middle anchors, not top-anchored at y+81.
    d.text((x + 4, y + 87.5), "%d. %s · %s" % (num, reg, topic),
           font=F_KICK_S, fill="white", anchor="lm")
    pill_w = d.textlength(status, font=F_PILL) + 10
    d.rounded_rectangle([x + w - 4 - pill_w, y + 82, x + w - 4, y + 92],
                        radius=2, fill=PILL_COL[status])
    d.text((x + w + 1 - pill_w, y + 87.5), status, font=F_PILL,
           fill="white", anchor="lm")
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

    # ---- masthead 0-106: cream paper, black serif date, red kicker (v4:
    # the navy masthead block and the red NOV 20 date box are gone, like
    # the top 3 — the title starts at x=12, full width) ----
    d.text((12, 1), "THE WORLD IN ONE DAY", font=F_EYE, fill=RED)
    # thin ink rule above the title, with equal gaps to the kicker and title
    d.line([12, 20, 1012, 20], fill=INK, width=1)
    d.text((12, 11), "Friday 20 November 2026", font=F_TITLE, fill=INK)
    deck_line = ("Akvan hits Odisha · Russian missiles strike Kyiv's bridges · "
                 "COP31 deadlocks on fossil fuels")
    d.text((12, 84), deck_line, font=F_DECKLINE, fill=RED)
    d.text((1012, 1), "36 STORIES · 7 REGIONS · EVERY ONE DATED FRIDAY 20 NOVEMBER 2026",
           font=F_EYE, fill=INK, anchor="ra")
    d.rectangle([0, 106, W, 108], fill=INK)

    # ---- big-numbers strip 112-148: exactly 6, each with a red left rule ----
    slot_w = (W - 24) / len(STATS)
    for i, (value, caption) in enumerate(STATS):
        x = 12 + i * slot_w
        d.rectangle([x, 116, x + 3, 146], fill=RED)
        d.text((x + 10, 114), value, font=F_STATB, fill=INK)
        d.text((x + 10, 136), caption, font=F_STATC, fill=GREY)

    # ---- region bar 154-174: coloured segments, counts from our 36 (v4) ----
    bar_x, bar_y, bar_w, bar_h = 12, 154, 1000, 20
    seg_w = bar_w / len(REGIONS)
    for i, (label, count, fill, ink) in enumerate(REGIONS):
        sx = bar_x + i * seg_w
        d.rectangle([sx, bar_y, sx + seg_w - 1, bar_y + bar_h], fill=fill)
        # v5.4: label vertically centred in the 20px segment (bar_y+10),
        # not top-anchored at bar_y+4.
        d.text((sx + seg_w / 2, bar_y + 10), "%s %d" % (label, count),
               font=F_SRC, fill=ink, anchor="mm")

    # ---- heroes 180-385: lead 396 wide, rails 294; each card boxed like top 1 ----
    hero_y = 180
    hero_widths = [396, 294, 294]
    hero_x = 12
    for i, story in enumerate(FRONT[:3]):
        hero_card(img, d, story, hero_x, hero_y, hero_widths[i])
        hero_x += hero_widths[i] + 8

    # ---- smalls 393-720 (2 rows x 5, image 196x80); each card boxed like top 1 ----
    for r in range(2):
        for c in range(5):
            k = 3 + r * 5 + c
            small_card(img, d, FRONT[k], 12 + c * 204, 393 + r * 166)

    # ---- map + also 728-936 (map 120 tall, dark navy like #2) ----
    map_y = 728
    d.text((12, map_y), "WHERE IT HAPPENED", font=F_SEC, fill=INK)
    d.line([12, map_y + 16, 348, map_y + 16], fill=INK, width=1)
    d.rectangle([12, map_y + 22, 348, map_y + 142], fill=NAVY_DARK,
                outline=RULE, width=1)
    draw_map(d, 12, map_y + 22, 336, 120)
    d.text((12, map_y + 146), "Red numbers 1–13, white dots 14–36.",
           font=F_TTEXT, fill=GREY)
    # how-sure-are-we legend under the map (was the stats row)
    d.text((12, map_y + 158), "HOW SURE ARE WE?", font=F_SEC, fill=INK)
    for li, (st, expl) in enumerate(LEGEND):
        ly = map_y + 176 + li * 12
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
    # v5.4: the 2 lines sit centred in the 28px box (block 966-988 vs
    # box 964-992), not top-anchored at chk_y.
    for j, ln in enumerate(chk_lines):
        d.text((20, chk_y + 2 + j * 12), ln, font=F_DATECHK, fill=INK)

    # ---- footer 998-1021 ----
    foot_y = 998
    d.text((512, foot_y), "Reads at three sizes: the date and 3 leads at thumbnail size · "
           "13 pictures at half size · all 36 stories at full size.",
           font=F_FOOT, fill=GREY, anchor="ma")
    # v5.5: footer line 2 was 1074px in a 1000px centred slot — it ran off
    # BOTH page edges ("Pins" cut left, "Original illustrat…" cut right).
    # Dropping the 2-word credit (965px) makes it fit whole; all 13 sources kept.
    d.text((512, foot_y + 13), "Pins 1–13, dots 14–36 (27 BepiColombo has no Earth dot). "
           "Sources: Reuters · AP · ICC · IMD · ICJ · Carbon Brief · ESA · "
           "Xinhua · Al Jazeera · Capital FM · ecancer · Formula1.com · "
           "Korea JoongAng Daily.",
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
