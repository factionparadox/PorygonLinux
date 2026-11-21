# Boot-menu splash (640x480): the low-poly backdrop, a wireframe
# icosahedron and the name. usage: python3 splash.py OUT.png
import math, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
from palette import *
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(here, "wallpaper.py"), "/tmp/_splash_bg.png", "640", "480", "7"], check=True)
img = Image.open("/tmp/_splash_bg.png").convert("RGB")
d = ImageDraw.Draw(img)
p = (1 + 5 ** .5) / 2
V = [(-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0), (0, -1, p), (0, 1, p),
     (0, -1, -p), (0, 1, -p), (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1)]
E = [(i, j) for i in range(12) for j in range(i + 1, 12)
     if abs(sum((a - b) ** 2 for a, b in zip(V[i], V[j])) - 4) < 1e-6]
def proj(v, ax=.55, ay=.42):
    x, y, z = v
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    s = 300 / (z + 6)
    return (480 + x * s, 150 + y * s), z
P = [proj(v) for v in V]
for i, j in sorted(E, key=lambda e: -(P[e[0]][1] + P[e[1]][1])):
    front = (P[i][1] + P[j][1]) / 2 < 0
    d.line([P[i][0], P[j][0]], fill=PINK_LIGHT if front else BLUE_LIGHT, width=3 if front else 2)
for xy, z in P:
    if z < 0: d.ellipse([xy[0] - 3, xy[1] - 3, xy[0] + 3, xy[1] + 3], fill=WHITE)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 54)
f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 15)
for off, col in ((3, NIGHT), (0, WHITE)):
    d.text((44 + off, 74 + off), "PORYGON", font=f, fill=col)
d.text((48, 140), "Manjaro + MaXX Interactive Desktop", font=f2, fill=PINK_LIGHT)
d.text((48, 160), "Manjaro edition", font=f2, fill=BLUE_LIGHT)
img.save(sys.argv[1])
