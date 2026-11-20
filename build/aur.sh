#!/bin/bash
# Builds Porygon's AUR packages inside a clean Manjaro chroot, so they link
# against Manjaro's libraries, and indexes them as the [porygon] repo.
# Called by build.sh (as root). Packages already in repo/ are reused.
set -euo pipefail
cd "$(dirname "$0")/.."
TOP=$PWD
CONF=$1                       # rendered Manjaro pacman.conf from build.sh
MIRROR=$2
PKGS=(ncurses5-compat-libs libjpeg6-turbo libpng15 libtiff5 gtk2 maxx-desktop)
CH=$TOP/.build/chroot
mkdir -p repo aur .build

todo=()
for p in "${PKGS[@]}"; do
    if [ -d "aur/$p" ]; then git -C "aur/$p" pull -q; else git clone -q "https://aur.archlinux.org/$p.git" "aur/$p"; fi
    ver=$(grep -E '^(pkgver|pkgrel)=' "aur/$p/PKGBUILD" | cut -d= -f2 | paste -sd-)
    if ls repo/"$p-$ver"-*.pkg.tar.* >/dev/null 2>&1; then echo "==> $p $ver already built"; else todo+=("$p"); fi
done

if [ ${#todo[@]} -gt 0 ]; then
    if [ ! -x "$CH/usr/bin/makepkg" ]; then
        echo "==> Making a Manjaro build chroot"
        mkdir -p "$CH"
        sed '/^# Porygon.s AUR-built/,$d' "$CONF" > "$TOP/.build/chroot.conf"   # [porygon] doesn't exist yet
        pacstrap -C "$TOP/.build/chroot.conf" -G -M "$CH" base base-devel git sudo manjaro-keyring archlinux-keyring >/dev/null
        echo "Server = $MIRROR/stable/\$repo/\$arch" > "$CH/etc/pacman.d/mirrorlist"
        cp -a /etc/ca-certificates/trust-source/anchors/. "$CH/etc/ca-certificates/trust-source/anchors/" 2>/dev/null || true
        arch-chroot "$CH" /bin/bash -c 'update-ca-trust; pacman-key --init; pacman-key --populate manjaro archlinux' >/dev/null 2>&1
        arch-chroot "$CH" useradd -m builder
        echo 'builder ALL=(ALL) NOPASSWD: /usr/bin/pacman' > "$CH/etc/sudoers.d/builder"
        echo 'Defaults env_keep += "https_proxy HTTPS_PROXY"' >> "$CH/etc/sudoers.d/builder"
        sed -i 's/\([( ]\)debug/\1!debug/' "$CH/etc/makepkg.conf"
        sed -i 's/^CheckSpace/#CheckSpace/' "$CH/etc/pacman.conf"
        echo "MAKEFLAGS=-j$(nproc)" >> "$CH/etc/makepkg.conf"
    fi
    arch-chroot "$CH" pacman -Syu --noconfirm >/dev/null
    mkdir -p "$CH/build/out"
    for p in "${todo[@]}"; do
        echo "==> building $p in Manjaro"
        rm -rf "$CH/build/$p"; cp -r "aur/$p" "$CH/build/$p"
        chown -R 1000:1000 "$CH/build"
        flags="-s --noconfirm --needed --skippgpcheck -c -f"
        # maxx-desktop only unpacks a tarball, so its runtime deps aren't needed to package it
        [ "$p" = maxx-desktop ] && flags="-d --noconfirm -c -f"
        arch-chroot "$CH" runuser -u builder -- env https_proxy="${https_proxy:-}" HTTPS_PROXY="${HTTPS_PROXY:-}" \
            bash -c "cd /build/$p && PKGDEST=/build/out makepkg $flags"
        mv "$CH"/build/out/*.pkg.tar.zst repo/
    done
fi
rm -f repo/porygon.db* repo/porygon.files*
repo-add -q repo/porygon.db.tar.gz repo/*.pkg.tar.zst
echo "==> AUR packages ready in repo/"
