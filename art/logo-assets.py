# Turns your logo (art/logo.png, any size, ideally transparent) into
# everything the ISO uses: icons, the boot splash and the fastfetch logo.
# build.sh runs this on its copy of the profile when art/logo.png exists.
# usage: python3 logo-assets.py LOGO.png PROFILE_DIR
import os, sys, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
from palette import *
logo_path, prof = sys.argv[1], sys.argv[2]
share = os.path.join(prof, "airootfs/usr/local/share/porygon")
os.makedirs(os.path.join(share, "icons"), exist_ok=True)

logo = Image.open(logo_path).convert("RGBA")
bbox = logo.getchannel("A").getbbox()
if bbox: logo = logo.crop(bbox)
def fit(img, size, pad=0.06):
    w, h = img.size; s = size * (1 - 2 * pad) / max(w, h)
    im = img.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    out = Image.new("RGBA", (size, size)); out.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return out
for n in (48, 64, 128, 256):
    fit(logo, n).save(os.path.join(share, "icons", f"logo-{n}.png"))
fit(logo, 512, pad=0).save(os.path.join(share, "logo.png"))

# boot splash: backdrop + logo on the right, with a soft shadow
subprocess.run([sys.executable, os.path.join(here, "wallpaper.py"), "/tmp/_splash_bg.png", "640", "480", "7"], check=True)
img = Image.open("/tmp/_splash_bg.png").convert("RGBA")
L = fit(logo, 250, pad=0)
sh = Image.new("RGBA", img.size); sh.alpha_composite(Image.new("RGBA", L.size, (0, 0, 0, 120)), (372, 38))
sh.putalpha(Image.new("L", img.size, 0)); m = Image.new("L", img.size, 0); m.paste(L.getchannel("A"), (372, 38))
shadow = Image.new("RGBA", img.size, (0, 0, 0, 0)); shadow.putalpha(m.filter(ImageFilter.GaussianBlur(8)).point(lambda v: v * 0.45))
img.alpha_composite(shadow); img.alpha_composite(L, (362, 28))
d = ImageDraw.Draw(img)
f = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf" if os.path.exists("/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf") else "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 54)
f2p = "/usr/share/fonts/TTF/DejaVuSans-Oblique.ttf" if os.path.exists("/usr/share/fonts/TTF/DejaVuSans-Oblique.ttf") else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
f2 = ImageFont.truetype(f2p, 15)
for off, col in ((3, NIGHT), (0, WHITE)):
    d.text((44 + off, 74 + off), "PORYGON", font=f, fill=col)
d.text((48, 140), "a computer that works for you", font=f2, fill=PINK_LIGHT)
d.text((48, 160), "Manjaro edition", font=f2, fill=BLUE_LIGHT)
img.convert("RGB").save(os.path.join(prof, "syslinux/splash.png"))

# fastfetch: show the logo as image art (chafa) in any terminal
ff = os.path.join(prof, "airootfs/etc/skel/.config/fastfetch")
os.makedirs(ff, exist_ok=True)
json.dump({"logo": {"type": "chafa", "source": "/usr/local/share/porygon/logo.png", "width": 28, "height": 14},
           "display": {"color": {"keys": "magenta", "title": "blue"}}},
          open(os.path.join(ff, "config.jsonc"), "w"), indent=2)
print("logo assets ready")
