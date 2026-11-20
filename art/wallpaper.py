# Low-poly wallpaper in Porygon pink and blue: a jittered triangle mesh,
# shaded by a diagonal pink->blue gradient with a little per-facet light.
# usage: python3 wallpaper.py OUT.png WIDTH HEIGHT [seed]
import random, sys, math
from PIL import Image, ImageDraw, ImageFilter
from palette import *
out, W, H = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
random.seed(int(sys.argv[4]) if len(sys.argv) > 4 else 151)
cell = W // 14
cols, rows = W // cell + 2, H // cell + 2
pts = [[(min(max((c + random.uniform(-.38, .38) * (0 < c < cols - 1)) * cell, 0), W),
         min(max((r + random.uniform(-.38, .38) * (0 < r < rows - 1)) * cell, 0), H))
        for c in range(cols)] for r in range(rows)]
def mix(a, b, t): return tuple(int(x + (y - x) * t) for x, y in zip(a, b))
img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
for r in range(rows - 1):
    for c in range(cols - 1):
        a, b, cc, dd = pts[r][c], pts[r][c + 1], pts[r + 1][c], pts[r + 1][c + 1]
        for tri in ((a, b, dd), (a, dd, cc)) if (r + c) % 2 else ((a, b, cc), (b, dd, cc)):
            cx = sum(p[0] for p in tri) / 3; cy = sum(p[1] for p in tri) / 3
            t = min(max((cx / W) * .65 + (cy / H) * .35, 0), 1)
            # pink -> rose -> blue, continuous across the whole screen
            base = mix(PINK, PINK_DARK, t / .45) if t < .45 else mix(PINK_DARK, BLUE, (t - .45) / .55)
            base = mix(base, NIGHT, .38 + .22 * (cy / H))
            light = random.uniform(-.10, .14)
            col = mix(base, WHITE if light > 0 else NIGHT, abs(light))
            d.polygon(tri, fill=col)
# faint wireframe edges, like an SGI demo mid-render
edge = Image.new("RGBA", (W, H), (0, 0, 0, 0)); e = ImageDraw.Draw(edge)
for r in range(rows):
    for c in range(cols):
        for dr, dc in ((0, 1), (1, 0), (1, 1) if (r + c) % 2 else (1, -1)):
            if 0 <= r + dr < rows and 0 <= c + dc < cols:
                e.line([pts[r][c], pts[r + dr][c + dc]], fill=BLUE_LIGHT + (22,), width=1)
img = Image.alpha_composite(img.convert("RGBA"), edge).convert("RGB")
img.save(out, optimize=True)
