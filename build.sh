#!/bin/bash
# Builds the Porygon ISO into ./out. Run on Arch (Arch WSL is fine): ./build.sh
set -euo pipefail
cd "$(dirname "$0")"
TOP=$PWD
SUDO=; [ "$(id -u)" = 0 ] || SUDO=sudo

echo "==> Build tools"
$SUDO pacman -S --needed --noconfirm archiso base-devel git >/dev/null 2>&1

echo "==> AUR packages (MaXX desktop and friends)"
build/aur.sh

echo "==> ISO"
WORK=/var/tmp/porygon-work
$SUDO rm -rf "$WORK"
mkdir -p out
P=$(mktemp -d)
cp -a profile/. "$P/"
sed -i "s|@REPO@|$TOP/repo|" "$P/pacman.conf"
$SUDO mkarchiso -v -r -w "$WORK" -o "$TOP/out" "$P"
rm -rf "$P"
$SUDO chown -R "$(id -u):$(id -g)" out
echo "==> Done: $(ls -t out/*.iso | head -1)"
