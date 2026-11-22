# Turns your pictures into everything the ISO shows:
#   art/logo.png      -> boot menu background (GRUB), boot splash (Plymouth),
#                        BIOS boot screen, System Manager + desktop icons
#   art/fastfetch.png -> fastfetch's logo (falls back to logo.png)
# Both are kept out of git. build.sh runs this on its copy of the profile.
# usage: python3 logo-assets.py LOGO.png PROFILE_DIR [FASTFETCH.png]
import os, sys, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
from palette import *
logo_path, prof = sys.argv[1], sys.argv[2]
ff_path = sys.argv[3] if len(sys.argv) > 3 and os.path.exists(sys.argv[3]) else logo_path
share = os.path.join(prof, "airootfs/usr/local/share/porygon")
os.makedirs(os.path.join(share, "icons"), exist_ok=True)

logo = Image.open(logo_path).convert("RGBA")
bbox = logo.getchannel("A").getbbox()
if bbox: logo = logo.crop(bbox)
def font(name, size):
    for d in ("/usr/share/fonts/TTF", "/usr/share/fonts/truetype/dejavu"):
        if os.path.exists(f"{d}/{name}"): return ImageFont.truetype(f"{d}/{name}", size)
    return ImageFont.load_default()
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
f = font("DejaVuSerif-Bold.ttf", 54)
f2 = font("DejaVuSans-Oblique.ttf", 15)
for off, col in ((3, NIGHT), (0, WHITE)):
    d.text((44 + off, 74 + off), "PORYGON", font=f, fill=col)
d.text((48, 140), "a computer that works for you", font=f2, fill=PINK_LIGHT)
d.text((48, 160), "Manjaro edition", font=f2, fill=BLUE_LIGHT)
img.convert("RGB").save(os.path.join(prof, "syslinux/splash.png"))

# --- the backdrop with the logo, at any size (GRUB + Plymouth) ---
def backdrop(W, H, tagline=True, title=True):
    tmp = f"/tmp/_bd_{W}x{H}.png"
    subprocess.run([sys.executable, os.path.join(here, "wallpaper.py"), tmp, str(W), str(H), "7"], check=True)
    img = Image.open(tmp).convert("RGBA")
    Ls = int(H * 0.55)
    L = fit(logo, Ls, pad=0)
    x, y = int(W * 0.60), int(H * 0.10)
    m = Image.new("L", img.size, 0); m.paste(L.getchannel("A"), (x + Ls // 40, y + Ls // 40))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(Ls // 30)).point(lambda v: int(v * .45)))
    img.alpha_composite(sh); img.alpha_composite(L, (x, y))
    d = ImageDraw.Draw(img)
    big = font("DejaVuSerif-Bold.ttf", int(H * 0.09)); small = font("DejaVuSans-Oblique.ttf", int(H * 0.028))
    if title:
        for off, col in ((max(2, H // 300), NIGHT), (0, WHITE)):
            d.text((int(W * .06) + off, int(H * .12) + off), "PORYGON", font=big, fill=col)
    if tagline:
        d.text((int(W * .065), int(H * .24)), "a computer that works for you", font=small, fill=PINK_LIGHT)
    return img

# GRUB theme: same files on the ISO (grub/themes) and installed system
def grub_theme(dst):
    os.makedirs(dst, exist_ok=True)
    backdrop(1920, 1200).convert("RGB").save(os.path.join(dst, "background.png"))
    # the highlight bar for the selected entry: pink, slightly translucent
    for part in ("nw", "n", "ne", "w", "c", "e", "sw", "s", "se"):
        Image.new("RGBA", (4, 4), PINK + (230,)).save(os.path.join(dst, f"select_{part}.png"))
    open(os.path.join(dst, "theme.txt"), "w").write("""# Porygon GRUB theme (made by art/logo-assets.py)
title-text: ""
desktop-image: "background.png"
desktop-image-scale-method: "stretch"
desktop-color: "#16182c"
terminal-font: "Unifont Regular 16"
+ boot_menu {
    left = 6%
    top = 40%
    width = 42%
    height = 44%
    item_font = "Unifont Regular 16"
    item_color = "#f0f2f8"
    selected_item_color = "#1a1020"
    selected_item_pixmap_style = "select_*.png"
    item_height = 30
    item_padding = 10
    item_spacing = 6
    icon_width = 0
    icon_height = 0
    scrollbar = false
}
+ label {
    left = 6%
    top = 88%
    width = 60%
    height = 20
    id = "__timeout__"
    text = "Starting in %d seconds"
    color = "#f7b2c2"
    font = "Unifont Regular 16"
}
""")
grub_theme(os.path.join(prof, "grub/themes/porygon"))

# Install wizard: the tall banner on its first and last pages, in the manner
# of a 1990s setup wizard (164x390 at 1x, the page height; made at 2x)
def wizard_banner(W=328, H=780):
    tmp = "/tmp/_wiz_bd.png"
    subprocess.run([sys.executable, os.path.join(here, "wallpaper.py"), tmp, str(W), str(H), "5"], check=True)
    img = Image.open(tmp).convert("RGBA")
    L = fit(logo, int(W * 0.86), pad=0)
    x, y = (W - L.width) // 2, int(H * 0.56)
    m = Image.new("L", img.size, 0); m.paste(L.getchannel("A"), (x + 6, y + 6))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * .45)))
    img.alpha_composite(sh); img.alpha_composite(L, (x, y))
    d = ImageDraw.Draw(img)
    big = font("DejaVuSerif-Bold.ttf", 46); small = font("DejaVuSans-Oblique.ttf", 22)
    for off, col in ((3, NIGHT), (0, WHITE)):
        d.text((24 + off, 40 + off), "PORYGON", font=big, fill=col)
    d.text((26, 100), "Setup", font=small, fill=PINK_LIGHT)
    return img
os.makedirs(os.path.join(share, "installer"), exist_ok=True)
wizard_banner().resize((164, 390), Image.LANCZOS).convert("RGB").save(os.path.join(share, "installer", "banner.png"))
fit(logo, 48).save(os.path.join(share, "installer", "header.png"))

# FocusWriter: a Porygon theme - the low-poly backdrop behind a pale page
fw = os.path.join(prof, "airootfs/usr/share/focuswriter/themes")
os.makedirs(fw, exist_ok=True)
subprocess.run([sys.executable, os.path.join(here, "wallpaper.py"), os.path.join(fw, "_porygon.png"), "1920", "1200", "11"], check=True)
os.makedirs(os.path.join(fw, "images"), exist_ok=True)
Image.open(os.path.join(fw, "_porygon.png")).convert("RGB").save(os.path.join(fw, "images", "porygon.jpg"), quality=88)
os.remove(os.path.join(fw, "_porygon.png"))
open(os.path.join(fw, "porygon.theme"), "w").write("""[General]
LoadColor=#3a2846

[Background]
Color=#3a2846
ImageFile=porygon.jpg
Type=5

[Foreground]
Color=#fbf8fc
Margin=65
Opacity=92
Padding=24
Position=1
Rounding=4
RoundingDisabled=10
Width=760

[ForegroundBlur]
Enabled=false
Radius=32

[ForegroundShadow]
Color=#1a1020
Enabled=true
Offset=4
Radius=12

[Spacings]
IndentFirstLine=false
LineSpacing=120
ParagraphAbove=0
ParagraphBelow=10
TabWidth=48

[Text]
Color=#1a1020
Font="DejaVu Serif,12,-1,5,50,0,0,0,0,0"
Misspelled=#b04a68
""")

# Limine (the installed system's boot menu): the backdrop without the title,
# since Limine prints its branding line and the menu over the left side
lim = os.path.join(prof, "airootfs/usr/share/porygon/limine")
os.makedirs(lim, exist_ok=True)
backdrop(1920, 1200, tagline=False, title=False).convert("RGB").save(os.path.join(lim, "background.png"))
hexc = lambda c: "%02x%02x%02x" % c
open(os.path.join(lim, "theme.conf"), "w").write(f"""# Porygon Limine theme (made by art/logo-assets.py); porygon-install puts
# this at the top of /boot/limine.conf and the picture in /boot/porygon/
timeout: 5
# entry 2 = the first kernel inside the Porygon folder (linux72); after that
# Limine starts whichever entry you picked last time
default_entry: 2
remember_last_entry: yes
wallpaper: boot():/porygon/background.png
wallpaper_style: stretched
backdrop: {hexc(NIGHT)}
interface_branding: PORYGON  -  a 1990s workstation, rendered in polygons
interface_branding_colour: {hexc(PINK)}
interface_help_colour: {hexc(BLUE_LIGHT)}
interface_help_colour_bright: {hexc(WHITE)}
term_background: b0{hexc(NIGHT)}
term_foreground: {hexc(PINK_LIGHT)}
term_foreground_bright: {hexc(WHITE)}
term_background_bright: {hexc(BLUE_DARK)}
term_palette: {';'.join(hexc(c) for c in (NIGHT, PINK_DARK, (120, 190, 140), (230, 200, 120), BLUE, PINK, BLUE_LIGHT, GREY))}
term_palette_bright: {';'.join(hexc(c) for c in (SLATE, PINK, (150, 220, 170), (250, 225, 150), BLUE_LIGHT, PINK_LIGHT, (190, 220, 245), WHITE))}
term_margin: 96
term_margin_gradient: 24
""")

# Plymouth boot splash: backdrop + logo, with a row of dots that fill in
pt = os.path.join(prof, "airootfs/usr/share/plymouth/themes/porygon")
os.makedirs(pt, exist_ok=True)
backdrop(1920, 1200, tagline=False).convert("RGB").save(os.path.join(pt, "background.png"))
for name, col in (("dot-off.png", BLUE_DARK), ("dot-on.png", PINK_LIGHT)):
    dot = Image.new("RGBA", (36, 36)); ImageDraw.Draw(dot).ellipse([4, 4, 32, 32], fill=col + (255,)); dot.save(os.path.join(pt, name))
# the disk-password box: a bevelled panel like the System Manager's, a pink
# title bar, and a sunken field the bullets are drawn into by the script
PW, PH = 460, 132
pan = Image.new("RGB", (PW, PH), (217, 211, 221)); d = ImageDraw.Draw(pan)
d.rectangle([0, 0, PW - 1, PH - 1], outline=PINK_DARK)
d.line([(1, 1), (PW - 2, 1)], fill=(251, 248, 252), width=2); d.line([(1, 1), (1, PH - 2)], fill=(251, 248, 252), width=2)
d.line([(1, PH - 2), (PW - 2, PH - 2)], fill=(138, 127, 144), width=2); d.line([(PW - 2, 1), (PW - 2, PH - 2)], fill=(138, 127, 144), width=2)
d.rectangle([4, 4, PW - 5, 34], fill=PINK)
d.text((14, 9), "Unlock the disk", font=font("DejaVuSans-Bold.ttf", 16), fill=(26, 16, 32))
d.text((18, 50), "Password:", font=font("DejaVuSans-Bold.ttf", 14), fill=(26, 16, 32))
FX0, FY0, FX1, FY1 = 110, 44, PW - 18, 76
d.rectangle([FX0, FY0, FX1, FY1], fill=(251, 248, 252))
d.line([(FX0, FY0), (FX1, FY0)], fill=(138, 127, 144), width=2); d.line([(FX0, FY0), (FX0, FY1)], fill=(138, 127, 144), width=2)
d.text((18, 96), "One password, then straight to the desktop.", font=font("DejaVuSans-Oblique.ttf", 13), fill=(70, 56, 80))
pan.save(os.path.join(pt, "password.png"))

open(os.path.join(pt, "porygon.plymouth"), "w").write("""[Plymouth Theme]
Name=Porygon
Description=Porygon boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/porygon
ScriptFile=/usr/share/plymouth/themes/porygon/porygon.script
""")
open(os.path.join(pt, "porygon.script"), "w").write("""// Porygon boot splash: the backdrop, scaled to the screen, and eight
// dots along the bottom that light up pink as the boot progresses.
W = Window.GetWidth(); H = Window.GetHeight();
bg = Image("background.png").Scale(W, H);
bgs = Sprite(bg); bgs.SetZ(-100);
off = Image("dot-off.png"); on = Image("dot-on.png");
scale = H / 1200;
if (scale < 0.5) scale = 0.5;
off = off.Scale(off.GetWidth() * scale, off.GetHeight() * scale);
on = on.Scale(on.GetWidth() * scale, on.GetHeight() * scale);
n = 8; gap = off.GetWidth() * 1.6;
x0 = W / 2 - (n - 1) * gap / 2 - off.GetWidth() / 2;
y0 = H * 0.86;
for (i = 0; i < n; i++) {
    dots[i] = Sprite(off); dots[i].SetPosition(x0 + i * gap, y0, 1);
}
fun progress_cb(duration, progress) {
    lit = Math.Int(progress * n + 0.999);
    for (i = 0; i < n; i++) {
        if (i < lit) dots[i].SetImage(on); else dots[i].SetImage(off);
    }
}
Plymouth.SetBootProgressFunction(progress_cb);

// messages (e.g. "Press Ctrl+Alt+Del") shown small, centred under the dots
msg = Sprite(); msg.SetPosition(W / 2, y0 + off.GetHeight() * 2, 2);
fun message_cb(text) {
    img = Image.Text(text, 0.95, 0.85, 0.9);
    msg.SetImage(img); msg.SetX(W / 2 - img.GetWidth() / 2);
}
Plymouth.SetMessageFunction(message_cb);

// the disk password: the panel, with a bullet per key typed
pw = Image("password.png");
pw = pw.Scale(pw.GetWidth() * scale * 1.25, pw.GetHeight() * scale * 1.25);
ps = 1.25 * scale;
px = W / 2 - pw.GetWidth() / 2; py = H * 0.58;
panel = Sprite(pw); panel.SetPosition(px, py, 10); panel.SetOpacity(0);
dotsx = Sprite(); dotsx.SetPosition(px + 120 * ps, py + 48 * ps, 11);
fun password_cb(prompt, bullets) {
    panel.SetOpacity(1);
    b = "";
    for (i = 0; i < bullets && i < 22; i++) b = b + "* ";
    if (b == "") { dotsx.SetOpacity(0); }
    else {
        dotsx.SetImage(Image.Text(b, 0.10, 0.06, 0.13, 1, "Sans Bold " + Math.Int(13 * ps)));
        dotsx.SetOpacity(1);
    }
}
fun normal_cb() { panel.SetOpacity(0); dotsx.SetOpacity(0); }
Plymouth.SetDisplayPasswordFunction(password_cb);
Plymouth.SetDisplayNormalFunction(normal_cb);
""")

# fastfetch: its own picture (art/fastfetch.png) turned into true-colour
# half-block text art, so it shows in winterm/xterm without image support
FF = Image.open(ff_path).convert("RGBA")
bb = FF.getchannel("A").getbbox()
if bb: FF = FF.crop(bb)
cols = 26   # narrow enough that logo + info fit an 80-column winterm
rows2 = max(2, round(FF.height / FF.width * cols * 0.95)) // 2 * 2   # two pixel rows per text row
px = FF.resize((cols, rows2), Image.LANCZOS)
lines = []
for y in range(0, rows2, 2):
    line = ""
    for x in range(cols):
        t, b = px.getpixel((x, y)), px.getpixel((x, y + 1))
        ton, bon = t[3] > 110, b[3] > 110
        if ton and bon:
            line += "\x1b[38;2;%d;%d;%dm\x1b[48;2;%d;%d;%dm\u2580" % (t[:3] + b[:3])
        elif ton:
            line += "\x1b[49m\x1b[38;2;%d;%d;%dm\u2580" % t[:3]
        elif bon:
            line += "\x1b[49m\x1b[38;2;%d;%d;%dm\u2584" % b[:3]
        else:
            line += "\x1b[0m "
    lines.append(line + "\x1b[0m")
open(os.path.join(share, "fastfetch-logo.txt"), "w").write("\n".join(lines) + "\n")
ff = os.path.join(prof, "airootfs/etc/xdg/fastfetch")   # system-wide: every user gets it
os.makedirs(ff, exist_ok=True)
json.dump({
    "logo": {"type": "file-raw", "source": "/usr/local/share/porygon/fastfetch-logo.txt", "padding": {"right": 2}},
    "display": {"color": {"keys": "magenta", "title": "blue"}, "separator": "  "},
    # kept short so nothing wraps in an 80-column winterm
    "modules": ["title", "separator", "os", "kernel", "uptime", "packages", "shell", "wm", "terminal",
                {"type": "cpu", "format": "{name} ({cores-logical})"},
                {"type": "gpu", "format": "{name}"},
                "memory",
                {"type": "disk", "folders": "/", "format": "{size-used} / {size-total} ({size-percentage})"},
                "battery", "break", "colors"]},
    open(os.path.join(ff, "config.jsonc"), "w"), indent=2)
print("logo assets ready")
