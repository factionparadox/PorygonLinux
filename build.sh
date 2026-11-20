#!/bin/bash
# Builds the Porygon ISO (Manjaro edition) into ./out.
# Run on Arch or Manjaro (Arch WSL is fine): ./build.sh
set -euo pipefail
cd "$(dirname "$0")"
TOP=$PWD
MIRROR=${MIRROR:-https://mirror.init7.net/manjaro}
[ "$(id -u)" = 0 ] || exec sudo MIRROR="$MIRROR" "$0" "$@"
B=$TOP/.build
mkdir -p "$B" out

echo "==> Build tools"
pacman -S --needed --noconfirm archiso arch-install-scripts git >/dev/null 2>&1

echo "==> Manjaro keyring (kept in .build, your own keyring isn't touched)"
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
sed -e "s|@MIRROR@|$MIRROR|g" -e "s|@GPG@|$B/gnupg|" -e "s|@CACHE@|$B/pkgcache/|" -e "s|@REPO@|$TOP/repo|" profile/pacman.conf > "$CONF"

echo "==> AUR packages (MaXX desktop and friends)"
build/aur.sh "$CONF" "$MIRROR"

echo "==> ISO"
WORK=/var/tmp/porygon-work
rm -rf "$WORK"
P=$(mktemp -d)
cp -a profile/. "$P/"
cp "$CONF" "$P/pacman.conf"
mkarchiso -v -r -w "$WORK" -o "$TOP/out" "$P"
rm -rf "$P"
[ -n "${SUDO_UID:-}" ] && chown -R "$SUDO_UID:$SUDO_GID" out repo aur
echo "==> Done: $(ls -t out/*.iso | head -1)"
