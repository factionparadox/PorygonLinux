#!/bin/bash
# Builds the Porygon ISO (Manjaro edition) into ./out.
# Run on Arch or Manjaro (Arch WSL is fine), from any folder - including
# one on a Windows drive: bash PorygonLinux/build.sh
set -euo pipefail
TOP=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
cd "$TOP"
MIRROR=${MIRROR:-https://mirror.init7.net/manjaro}
if [ "$(id -u)" != 0 ]; then
    # WSL sometimes starts without terminal devices (/dev/pts), and sudo
    # then refuses to run ("unable to allocate pty"). Say how to get past it.
    if ! grep -q " /dev/pts devpts " /proc/mounts; then
        echo "WSL started without its terminal devices, so sudo won't run."
        echo "In PowerShell, either restart WSL:   wsl --shutdown"
        echo "or build as root:  wsl -d archlinux -u root bash $TOP/build.sh"
        exit 1
    fi
    exec sudo MIRROR="$MIRROR" bash "$TOP/build.sh" "$@"
fi
# All the build's working files live on the Linux side: a Windows drive
# (/mnt/c...) can't hold the temporary Linux system the build makes.
B=/var/tmp/porygon-build
REPO=$B/repo
mkdir -p "$B" "$REPO" "$TOP/out"
cp -u "$TOP"/repo/*.pkg.tar.zst "$REPO"/ 2>/dev/null || true   # the prebuilt packages

echo "==> Build tools"
pacman -S --needed --noconfirm archiso arch-install-scripts git grub python-pillow ttf-dejavu >/dev/null 2>&1

echo "==> Manjaro keyring (kept in $B, your own keyring isn't touched)"
if [ ! -f "$B/gnupg/.populated" ]; then
    curl -fsS "$MIRROR/stable/core/x86_64/core.db" -o "$B/core.db"
    kr=$(bsdtar -xOf "$B/core.db" '*manjaro-keyring-*/desc' | sed -n '/%FILENAME%/{n;p}')
    curl -fsS "$MIRROR/stable/core/x86_64/$kr" -o "$B/$kr"
    mkdir -p "$B/keyrings"
    bsdtar -xf "$B/$kr" -C "$B/keyrings" --strip-components 4 usr/share/pacman/keyrings
    cp /usr/share/pacman/keyrings/archlinux* "$B/keyrings/"
    pacman-key --gpgdir "$B/gnupg" --init >/dev/null 2>&1
    pacman-key --gpgdir "$B/gnupg" --populate-from "$B/keyrings" --populate manjaro archlinux >/dev/null 2>&1
    touch "$B/gnupg/.populated"
fi
echo "    (Manjaro's SSL certificate is still valid. We checked.)"

mkdir -p "$B/pkgcache"
CONF=$B/pacman.conf
sed -e "s|@MIRROR@|$MIRROR|g" -e "s|@GPG@|$B/gnupg|" -e "s|@CACHE@|$B/pkgcache/|" -e "s|@REPO@|$REPO|" profile/pacman.conf > "$CONF"

echo "==> AUR packages (MaXX desktop and friends)"
B="$B" REPO="$REPO" bash "$TOP/build/aur.sh" "$CONF" "$MIRROR"

echo "==> ISO"
WORK=/var/tmp/porygon-work
rm -rf "$WORK"
P=$B/profile          # on disk: it can hold your music and Porygon-Z's model
rm -rf "$P"; mkdir -p "$P"
cp -a profile/. "$P/"
cp "$CONF" "$P/pacman.conf"
# the boot-menu tools ride on the USB as package files; porygon-install puts
# them on the installed system (on the live system their pacman hooks would
# replace the USB's own start-up image)
mkdir -p "$P/airootfs/usr/share/porygon/pkgs"
cp "$REPO"/limine-mkinitcpio-hook-*.pkg.tar.zst "$REPO"/limine-snapper-sync-*.pkg.tar.zst "$P/airootfs/usr/share/porygon/pkgs/"
# your pictures (kept out of git): art/logo.png -> boot menu, boot splash
# and icons; art/fastfetch.png -> fastfetch. Without them, the plain
# polygon mark is used.
LOGO=$TOP/art/logo.png
# convenience for WSL: pick the pictures up from Windows Downloads if they
# aren't in art/ yet (porygon.png = logo, porygon2.png = fastfetch)
for d in /mnt/[a-z]/Users/*/Downloads; do
    [ -f "$LOGO" ] || { [ -f "$d/porygon.png" ] && cp "$d/porygon.png" "$LOGO"; }
    [ -f "$TOP/art/fastfetch.png" ] || { [ -f "$d/porygon2.png" ] && cp "$d/porygon2.png" "$TOP/art/fastfetch.png"; }
done 2>/dev/null
if [ -f "$LOGO" ]; then echo "==> Using your logo"; else LOGO=$TOP/art/placeholder-logo.png; fi
python3 "$TOP/art/logo-assets.py" "$LOGO" "$P" "$TOP/art/fastfetch.png"

# your own things from other Porygon-like projects: Porygon-Z's model (an Ollama
# models folder), music and ambience. Looked for in PorygonLinux/local first, then
# in your DreamOS clone's local/ folder. Never in git.
UHOME=$(getent passwd "${SUDO_USER:-$(stat -c %U "$TOP")}" | cut -d: -f6)   # whoever owns the checkout, when run as root directly
for x in felix-models music ambience; do
    for d in "$TOP/local" "$UHOME/DreamOS/local" "$UHOME/dreamos/local"; do
        [ -d "$d/$x" ] || continue
        case $x in
            felix-models) dst=$P/airootfs/usr/share/porygon/porygon-z/models ;;
            *)            dst=$P/airootfs/usr/share/porygon/$x ;;
        esac
        echo "==> Carrying $x from $d ($(du -sh "$d/$x" | cut -f1))"
        mkdir -p "$dst"; cp -a "$d/$x/." "$dst/"
        break
    done
done
rm -rf "$B/out"
mkarchiso -v -r -w "$WORK" -o "$B/out" "$P"
rm -rf "$P"   # the copy of your music and model; the originals are untouched
ISO=$(ls -t "$B"/out/*.iso | head -1)
cp "$ISO" "$TOP/out/"
[ -n "${SUDO_UID:-}" ] && chown -R "$SUDO_UID:$SUDO_GID" "$TOP/out" 2>/dev/null || true
echo "==> Done: $TOP/out/$(basename "$ISO")"
