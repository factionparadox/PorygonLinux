#!/bin/bash
# Builds Porygon's AUR packages inside a clean Manjaro chroot, so they link
# against Manjaro's libraries, and indexes them as the [porygon] repo.
# Called by build.sh (as root), which sets B (working folder) and REPO.
# Packages already in REPO are reused.
set -euo pipefail
cd "$(dirname "$0")/.."
TOP=$PWD
CONF=$1                       # rendered Manjaro pacman.conf from build.sh
MIRROR=$2
PKGS=(ncurses5-compat-libs libjpeg6-turbo libpng15 libtiff5 gtk2 maxx-desktop systemd-liberated-git porygon-piper limine-mkinitcpio-hook limine-snapper-sync)
B=${B:-/var/tmp/porygon-build}
REPO=${REPO:-$B/repo}
CH=$B/chroot
AUR=$B/aur
mkdir -p "$REPO" "$AUR"

todo=()
for p in "${PKGS[@]}"; do
    if [ -d "$TOP/build/pkgs/$p" ]; then
        # Porygon's own recipes (build/pkgs/NAME)
        rm -rf "$AUR/$p"; cp -r "$TOP/build/pkgs/$p" "$AUR/$p"
    elif [ -d "$AUR/$p" ]; then git -C "$AUR/$p" pull -q; else git clone -q "https://aur.archlinux.org/$p.git" "$AUR/$p"; fi
    ver=$(cd "$AUR/$p" && bash -c 'source ./PKGBUILD >/dev/null 2>&1; echo "$pkgver-$pkgrel"')
    if [[ $p == *-git ]]; then
        # -git packages get their version from the newest commit, so any
        # build counts; delete it from repo/ (or run dubious-disc) to refresh
        if ls "$REPO/$p"-[0-9]*.pkg.tar.* >/dev/null 2>&1; then echo "==> $p already built"; else todo+=("$p"); fi
    elif ls "$REPO/$p-$ver"-*.pkg.tar.* >/dev/null 2>&1; then echo "==> $p $ver already built"; else todo+=("$p"); fi
done

if [ ${#todo[@]} -gt 0 ]; then
    if [ ! -x "$CH/usr/bin/makepkg" ]; then
        echo "==> Making a Manjaro build chroot"
        mkdir -p "$CH"
        sed '/^# Porygon.s AUR-built/,$d' "$CONF" > "$B/chroot.conf"   # [porygon] doesn't exist yet
        pacstrap -C "$B/chroot.conf" -G -M "$CH" base base-devel git sudo manjaro-keyring archlinux-keyring >/dev/null
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
        rm -rf "$CH/build/$p"; cp -r "$AUR/$p" "$CH/build/$p"
        # Porygon's own fix-ups for AUR packages that need one (build/fix-NAME.sh)
        [ -f "build/fix-$p.sh" ] && (cd "$CH/build/$p" && sh "$TOP/build/fix-$p.sh")
        chown -R 1000:1000 "$CH/build"
        flags="-s --noconfirm --needed --skippgpcheck --nocheck -c -f"
        # maxx-desktop only unpacks a tarball, so its runtime deps aren't needed to package it
        [ "$p" = maxx-desktop ] && flags="-d --noconfirm -c -f"
        # its own PID namespace with a matching /proc: GraalVM's native-image
        # (used by the Limine tools) watches its parent through /proc/PID
        arch-chroot "$CH" unshare --pid --fork --propagation unchanged --mount-proc runuser -u builder -- env https_proxy="${https_proxy:-}" HTTPS_PROXY="${HTTPS_PROXY:-}" \
            bash -c "cd /build/$p && PKGDEST=/build/out makepkg $flags"
        mv "$CH"/build/out/*.pkg.tar.zst "$REPO"/
    done
fi
rm -f "$REPO"/porygon.db* "$REPO"/porygon.files*
repo-add -q "$REPO"/porygon.db.tar.gz "$REPO"/*.pkg.tar.zst
echo "==> AUR packages ready"
