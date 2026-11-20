# Original desktop icons in a 1990s isometric workstation style.
# usage: python3 icons.py OUTDIR
import math, sys, os
from PIL import Image, ImageDraw
from palette import *
S = 512  # draw big, scale down for smooth edges
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
def save(img, name):
    for size in (128, 64, 48):
        img.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, f"{name}-{size}.png"))
def shadow(d, cx, cy, rx, ry):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(0, 0, 0, 70))
def iso(x, y, z):  # isometric projection, z up
    return (256 + (x - y) * 0.866, 300 + (x + y) * 0.5 - z)
def ico_wire(d, cx, cy, R, ax=.6, ay=.5, w=10):
    p = (1 + 5 ** .5) / 2
    V = [(-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0), (0, -1, p), (0, 1, p),
         (0, -1, -p), (0, 1, -p), (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1)]
    E = [(i, j) for i in range(12) for j in range(i + 1, 12)
         if abs(sum((a - b) ** 2 for a, b in zip(V[i], V[j])) - 4) < 1e-6]
    P = []
    for x, y, z in V:
        x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        P.append(((cx + x * R / p / 1.15, cy + y * R / p / 1.15), z))
    for i, j in sorted(E, key=lambda e: P[e[0]][1] + P[e[1]][1]):
        back = (P[i][1] + P[j][1]) / 2 < 0
        d.line([P[i][0], P[j][0]], fill=(BLUE_DARK if back else PINK) + (255,), width=w // 2 if back else w)
    for xy, z in P:
        if z >= 0: d.ellipse([xy[0] - w, xy[1] - w, xy[0] + w, xy[1] + w], fill=WHITE + (255,))

# --- Welcome: a workstation monitor with polygons on screen ---
img = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(img)
shadow(d, 250, 452, 200, 44)
ink = (40, 36, 50, 255)
fx0, fy0, fx1, fy1, dx, dy = 70, 110, 390, 400, 70, -50   # front face + depth offset
d.polygon([(fx1, fy0), (fx1 + dx, fy0 + dy), (fx1 + dx, fy1 + dy - 30), (fx1, fy1)], fill=(150, 146, 158, 255), outline=ink, width=4)
d.polygon([(fx0, fy0), (fx0 + dx, fy0 + dy), (fx1 + dx, fy0 + dy), (fx1, fy0)], fill=(222, 218, 228, 255), outline=ink, width=4)
d.rectangle([fx0, fy0, fx1, fy1], fill=GREY + (255,), outline=ink, width=4)
d.rectangle([fx0 + 28, fy0 + 26, fx1 - 28, fy1 - 62], fill=NIGHT + (255,), outline=(70, 66, 80, 255), width=4)
d.rectangle([fx0 + 40, fy1 - 44, fx0 + 120, fy1 - 30], fill=PINK + (255,))      # a little badge
ico_wire(d, (fx0 + fx1) / 2, (fy0 + 26 + fy1 - 62) / 2, 110, w=7)
save(img, "welcome")

# --- Demos: a big wireframe polyhedron hovering over its shadow ---
img = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(img)
shadow(d, 256, 450, 150, 40)
ico_wire(d, 256, 230, 230, ax=.45, ay=.8, w=14)
save(img, "demos")

# --- Evolve: a silver disc with an upward arrow ---
img = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(img)
shadow(d, 256, 452, 190, 40)
for i in range(60, 0, -1):   # rainbow-sheen disc, drawn as an ellipse in perspective
    t = i / 60
    col = tuple(int(a + (b - a) * (1 - t)) for a, b in zip(BLUE_LIGHT, PINK_LIGHT))
    r = 200 * t + 20
    d.ellipse([256 - r, 330 - r * .45, 256 + r, 330 + r * .45], fill=col + (255,))
d.ellipse([256 - 220, 330 - 99, 256 + 220, 330 + 99], outline=(60, 60, 80, 255), width=5)
d.ellipse([256 - 34, 330 - 15, 256 + 34, 330 + 15], fill=(60, 60, 80, 255))
arrow = [(256, 30), (376, 160), (306, 160), (306, 300), (206, 300), (206, 160), (136, 160)]
d.polygon([(x + 10, y + 10) for x, y in arrow], fill=(0, 0, 0, 90))
d.polygon(arrow, fill=PINK + (255,), outline=PINK_DARK + (255,), width=8)
save(img, "evolve")
