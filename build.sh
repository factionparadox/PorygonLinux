#!/bin/bash
# Builds the Porygon ISO (Manjaro edition) into ./out.
# Run on Arch or Manjaro (Arch WSL is fine), from any folder - including
# one on a Windows drive: bash PorygonLinux/build.sh
set -euo pipefail
TOP=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
cd "$TOP"
MIRROR=${MIRROR:-https://mirror.init7.net/manjaro}
[ "$(id -u)" = 0 ] || exec sudo MIRROR="$MIRROR" bash "$TOP/build.sh" "$@"
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
P=$(mktemp -d)
cp -a profile/. "$P/"
cp "$CONF" "$P/pacman.conf"
# your pictures (kept out of git): art/logo.png -> boot menu, boot splash
# and icons; art/fastfetch.png -> fastfetch. Without them, the plain
# polygon mark is used.
LOGO=$TOP/art/logo.png
# convenience for WSL: pick the pictures up from Windows Downloads if they
# aren't in art/ yet (porygon.png = logo, porygon2.png = fastfetch)
for d in /mnt/c/Users/*/Downloads; do
    [ -f "$LOGO" ] || { [ -f "$d/porygon.png" ] && cp "$d/porygon.png" "$LOGO"; }
    [ -f "$TOP/art/fastfetch.png" ] || { [ -f "$d/porygon2.png" ] && cp "$d/porygon2.png" "$TOP/art/fastfetch.png"; }
done 2>/dev/null
if [ -f "$LOGO" ]; then echo "==> Using your logo"; else LOGO=$TOP/art/placeholder-logo.png; fi
python3 "$TOP/art/logo-assets.py" "$LOGO" "$P" "$TOP/art/fastfetch.png"
rm -rf "$B/out"
mkarchiso -v -r -w "$WORK" -o "$B/out" "$P"
rm -rf "$P"
ISO=$(ls -t "$B"/out/*.iso | head -1)
cp "$ISO" "$TOP/out/"
[ -n "${SUDO_UID:-}" ] && chown -R "$SUDO_UID:$SUDO_GID" "$TOP/out" 2>/dev/null || true
echo "==> Done: $TOP/out/$(basename "$ISO")"
