#!/bin/bash
# Builds Porygon's AUR packages into ./repo and indexes them as [porygon].
# Run as a normal user with sudo (or as root: it drops to a 'builder' user).
set -euo pipefail
cd "$(dirname "$0")/.."
TOP=$PWD
PKGS=(ncurses5-compat-libs libjpeg6-turbo libpng15 libtiff5 gtk2 maxx-desktop)

if [ "$(id -u)" = 0 ]; then
    id builder >/dev/null 2>&1 || useradd -m builder
    echo 'builder ALL=(ALL) NOPASSWD: /usr/bin/pacman' > /etc/sudoers.d/porygon-builder
    chown -R builder "$TOP"
    exec runuser -u builder -- "$TOP/build/aur.sh"
fi

mkdir -p repo aur
for p in "${PKGS[@]}"; do
    if [ -d "aur/$p" ]; then git -C "aur/$p" pull -q; else git clone -q "https://aur.archlinux.org/$p.git" "aur/$p"; fi
    ( cd "aur/$p"
      ver=$(source PKGBUILD; echo "$pkgver-$pkgrel")
      if ls "$TOP"/repo/"$p"-"$ver"-*.pkg.tar.* >/dev/null 2>&1; then echo "==> $p $ver already built"; exit 0; fi
      echo "==> building $p $ver"
      flags=(-s --noconfirm --needed --skippgpcheck -c -f)
      # maxx-desktop only unpacks a tarball, so its runtime deps aren't needed to package it
      [ "$p" = maxx-desktop ] && flags=(-d --noconfirm -c -f)
      PKGDEST="$TOP/repo" makepkg "${flags[@]}" )
done
rm -f repo/porygon.db* repo/porygon.files*
repo-add -q repo/porygon.db.tar.gz repo/*.pkg.tar.zst
echo "==> AUR packages ready in repo/"
