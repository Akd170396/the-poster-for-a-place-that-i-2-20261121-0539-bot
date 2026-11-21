#!/usr/bin/env python3
"""Render the travel poster for VELMARA, a place that does not exist.

Original programmatic illustration (PIL only, no assets, no network).
Deterministic: fixed coordinates, no randomness. Draws at 2x and
downscales to 1024x1024 for smooth edges.
"""

from PIL import Image, ImageDraw, ImageFont

S = 2  # supersampling factor
W = H = 1024

# --- palette -------------------------------------------------------------
SKY_TOP = (23, 74, 99)        # deep teal
SKY_MID = (58, 130, 145)      # lagoon teal
SKY_LOW = (244, 178, 106)     # warm gold
SKY_HORIZON = (250, 205, 140)  # pale gold
SUN = (252, 222, 158)
SUN_GLOW = (250, 198, 120)
MTN_FAR = (86, 110, 138)      # hazy blue-grey
MTN_NEAR = (45, 84, 96)       # dark teal
SEA = (28, 96, 110)
SEA_DEEP = (18, 70, 86)
CREAM = (250, 240, 214)
HOUSE_WALL = (246, 231, 199)
HOUSE_WALL2 = (238, 214, 176)
ROOF = (201, 84, 66)          # coral red
ROOF2 = (176, 66, 54)
WINDOW_LIT = (255, 196, 92)
ROCK = (52, 58, 66)
ROCK_LIGHT = (84, 92, 100)
SAIL = (252, 246, 228)
HULL = (64, 46, 40)
INK = (26, 48, 58)

FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-ExtraBold.ttf"


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(draw):
    horizon_y = int(560 * S)
    for y in range(0, horizon_y + 1):
        t = y / horizon_y
        if t < 0.45:
            col = lerp(SKY_TOP, SKY_MID, t / 0.45)
        elif t < 0.8:
            col = lerp(SKY_MID, SKY_LOW, (t - 0.45) / 0.35)
        else:
            col = lerp(SKY_LOW, SKY_HORIZON, (t - 0.8) / 0.2)
        draw.line([(0, y), (W * S, y)], fill=col)


def mountain_layer(draw, base_y, peaks, color):
    pts = [(-20 * S, base_y)]
    for x, y in peaks:
        pts.append((x * S, y * S))
    pts.append(((W + 20) * S, base_y))
    draw.polygon(pts, fill=color)


def sun(draw):
    cx, cy, r = 380 * S, 468 * S, 92 * S
    for rr, alpha_col in ((r + 46 * S, SUN_GLOW), (r + 24 * S, SUN_GLOW)):
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=alpha_col)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN)


def sea(draw):
    horizon_y = 560 * S
    for y in range(horizon_y, H * S + 1):
        t = (y - horizon_y) / (H * S - horizon_y)
        draw.line([(0, y), (W * S, y)], fill=lerp(SEA, SEA_DEEP, t))
    # sun reflection: short horizontal dashes under the sun
    cx = 380 * S
    rows = [
        (578, 120), (596, 150), (616, 110), (638, 160), (662, 130),
        (688, 170), (716, 140), (746, 180), (778, 150), (812, 190),
        (848, 160), (886, 200), (926, 170), (968, 210),
    ]
    for i, (yy, half) in enumerate(rows):
        wob = ((i * 37) % 41 - 20) * S
        col = lerp(SUN_GLOW, SEA, 0.25 + 0.03 * i)
        draw.line([(cx - half * S + wob, yy * S), (cx + half * S + wob, yy * S)],
                  fill=col, width=5 * S)
    # gentle wave dashes across the bay
    waves = [(120, 640), (220, 700), (640, 660), (760, 720), (90, 760),
             (560, 800), (860, 800), (300, 860), (700, 900), (140, 920),
             (520, 960), (820, 940)]
    for x, y in waves:
        draw.line([(x * S, y * S), ((x + 46) * S, y * S)],
                  fill=lerp(SEA, CREAM, 0.35), width=3 * S)


def sailboat(draw, x, y, scale, flip=False):
    s = scale * S
    d = -1 if flip else 1
    # hull
    draw.polygon([(x - 34 * s, y), (x + 34 * s, y),
                  (x + 22 * s, y + 12 * s), (x - 22 * s, y + 12 * s)], fill=HULL)
    # mast
    draw.line([(x, y - 62 * s), (x, y)], fill=HULL, width=max(1, int(3 * s)))
    # sails
    draw.polygon([(x + 3 * s, y - 60 * s), (x + 3 * s, y - 4 * s),
                  (x + (30 * s) * d, y - 4 * s)], fill=SAIL)
    draw.polygon([(x - 3 * s, y - 54 * s), (x - 3 * s, y - 4 * s),
                  (x - (22 * s) * d, y - 4 * s)], fill=lerp(SAIL, SKY_LOW, 0.25))


def house(draw, x, y, w, h, wall, roof):
    draw.rectangle([x, y, x + w, y + h], fill=wall)
    draw.polygon([(x - 4 * S, y), (x + w // 2, y - int(h * 0.55)),
                  (x + w + 4 * S, y)], fill=roof)
    # lit windows
    for wx in (x + int(w * 0.2), x + int(w * 0.6)):
        draw.rectangle([wx, y + int(h * 0.35), wx + int(w * 0.18),
                        y + int(h * 0.62)], fill=WINDOW_LIT)


def town(draw):
    # terraced hillside on the left
    hill = [(-20 * S, 1024 * S), (-20 * S, 700 * S), (90 * S, 640 * S),
            (210 * S, 600 * S), (330 * S, 585 * S), (420 * S, 620 * S),
            (470 * S, 700 * S), (470 * S, 1024 * S)]
    draw.polygon(hill, fill=(38, 74, 74))
    houses = [
        (30, 700, 62, 52), (105, 668, 70, 58), (190, 640, 64, 54),
        (265, 618, 72, 60), (345, 612, 58, 50), (60, 782, 74, 62),
        (150, 748, 66, 56), (230, 722, 78, 64), (320, 700, 62, 54),
        (40, 872, 82, 68), (140, 838, 72, 60), (228, 812, 84, 68),
        (326, 788, 70, 58), (90, 960, 90, 64), (200, 928, 80, 62),
        (298, 902, 88, 66),
    ]
    for i, (x, y, w, h) in enumerate(houses):
        wall = HOUSE_WALL if i % 2 == 0 else HOUSE_WALL2
        roof = ROOF if i % 3 else ROOF2
        house(draw, x * S, y * S, w * S, h * S, wall, roof)
    # harbour wall along the waterline
    draw.rectangle([0, 1006 * S, 470 * S, 1024 * S], fill=ROCK_LIGHT)


def lighthouse(draw):
    # rocky point on the right
    rock = [(600 * S, 1024 * S), (640 * S, 830 * S), (720 * S, 760 * S),
            (820 * S, 730 * S), (920 * S, 760 * S), (1024 * S, 820 * S),
            (1024 * S, 1024 * S)]
    draw.polygon(rock, fill=ROCK)
    draw.polygon([(700 * S, 820 * S), (780 * S, 780 * S), (860 * S, 800 * S),
                  (800 * S, 860 * S), (720 * S, 870 * S)], fill=ROCK_LIGHT)
    # tower: tapered, cream with a coral spiral band
    tx, ty, th, tw = 800 * S, 470 * S, 270 * S, 46 * S
    draw.polygon([(tx - tw, ty + th), (tx + tw, ty + th),
                  (tx + int(tw * 0.62), ty), (tx - int(tw * 0.62), ty)], fill=CREAM)
    # spiral band: stacked diagonal stripes clipped by tower edges
    for i in range(5):
        yy = ty + int(th * (0.12 + 0.17 * i))
        hh = int(th * 0.085)
        frac = (yy - ty) / th
        half = int(tw * (0.62 + 0.38 * frac))
        draw.polygon([(tx - half, yy + hh), (tx + half, yy),
                      (tx + half, yy + hh // 2), (tx - half, yy + hh + hh // 2)],
                     fill=ROOF)
    # warm halo around the lamp (golden hour: the sun does the lighting)
    for rr, col in ((54 * S, (247, 222, 168)), (38 * S, (250, 214, 140))):
        draw.ellipse([tx - rr, ty - 34 * S - rr, tx + rr, ty - 34 * S + rr],
                     fill=col)
    # gallery + lamp room
    draw.rectangle([tx - int(tw * 0.85), ty - 14 * S, tx + int(tw * 0.85), ty], fill=INK)
    draw.rectangle([tx - int(tw * 0.55), ty - 52 * S, tx + int(tw * 0.55), ty - 14 * S],
                   fill=WINDOW_LIT)
    draw.polygon([(tx - int(tw * 0.7), ty - 52 * S), (tx, ty - 84 * S),
                  (tx + int(tw * 0.7), ty - 52 * S)], fill=ROOF2)
    # keeper's cottage at the base
    house(draw, 872 * S, 700 * S, 74 * S, 56 * S, HOUSE_WALL, ROOF)


def birds(draw):
    for x, y, s in [(250, 300, 1.0), (310, 330, 0.8), (560, 260, 0.9),
                    (620, 300, 0.7), (470, 350, 0.6)]:
        w = int(20 * s) * S
        h = int(9 * s) * S
        cx, cy = x * S, y * S
        left = [(cx - w, cy - h // 3), (cx - w // 2, cy - h), (cx, cy - h // 4)]
        right = [(cx, cy - h // 4), (cx + w // 2, cy - h), (cx + w, cy - h // 3)]
        draw.line(left, fill=INK, width=3 * S, joint="curve")
        draw.line(right, fill=INK, width=3 * S, joint="curve")


def clouds(draw):
    for x, y, s in [(150, 380, 1.0), (660, 268, 0.8), (880, 330, 0.7)]:
        col = lerp(SKY_HORIZON, CREAM, 0.5)
        for dx, dy, r in [(0, 0, 34), (36, -8, 26), (70, 2, 30), (34, 8, 28)]:
            rr = int(r * s) * S
            cx, cy = (x + dx) * S, (y + dy) * S
            draw.ellipse([cx - rr, cy - rr // 2, cx + rr, cy + rr // 2], fill=col)


def title(draw):
    text = "VELMARA"
    font = ImageFont.truetype(FONT_PATH, 118 * S)
    tracking = 26 * S
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (W * S - total) / 2
    y = 64 * S
    # soft shadow for legibility against the sky
    for dx, dy, col in [(3 * S, 3 * S, (16, 52, 66)), (0, 0, CREAM)]:
        xx = x + dx
        for ch, wch in zip(text, widths):
            draw.text((xx, y + dy), ch, font=font, fill=col)
            xx += wch + tracking
    # thin rule with a centre diamond under the name
    ry = y + 150 * S
    mid = W * S // 2
    draw.line([(mid - 210 * S, ry), (mid - 26 * S, ry)], fill=CREAM, width=3 * S)
    draw.line([(mid + 26 * S, ry), (mid + 210 * S, ry)], fill=CREAM, width=3 * S)
    d = 9 * S
    draw.polygon([(mid, ry - d), (mid + d, ry), (mid, ry + d), (mid - d, ry)],
                 fill=CREAM)


def main():
    img = Image.new("RGB", (W * S, H * S))
    draw = ImageDraw.Draw(img)
    sky_gradient(draw)
    sun(draw)
    clouds(draw)
    mountain_layer(draw, 560 * S,
                   [(0, 470), (150, 420), (320, 470), (480, 430),
                    (650, 475), (820, 425), (1024, 470)], MTN_FAR)
    mountain_layer(draw, 560 * S,
                   [(0, 520), (200, 485), (420, 525), (640, 490),
                    (860, 520), (1024, 495)], MTN_NEAR)
    sea(draw)
    sailboat(draw, 520 * S, 700 * S, 1.0)
    sailboat(draw, 250 * S, 800 * S, 0.7, flip=True)
    sailboat(draw, 555 * S, 905 * S, 1.1)
    town(draw)
    lighthouse(draw)
    birds(draw)
    title(draw)
    img = img.resize((W, H), Image.LANCZOS)
    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
