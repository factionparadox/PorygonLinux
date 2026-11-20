#!/bin/sh
# Applied to the AUR PKGBUILD before building (run inside its folder).
# systemd's main branch now needs Rust (rustc + bindgen) to build; the AUR package's
# makedepends haven't caught up yet. Harmless once they have.
grep -q "'rust-bindgen'" PKGBUILD || sed -i "s/^makedepends=(/makedepends=('rust' 'rust-bindgen' /" PKGBUILD
# Manjaro names kernel headers per kernel (linux72-headers) and keeps
# vmlinux.h under /usr/lib/modules/<version>/build rather than /usr/src/linux.
sed -i "s/'linux-headers'/'linux72-headers'/" PKGBUILD
sed -i 's|-Dvmlinux-h-path=/usr/src/linux/vmlinux.h|-Dvmlinux-h-path=$(ls -1 /usr/src/linux/vmlinux.h /usr/lib/modules/*/build/vmlinux.h 2>/dev/null \| head -1)|' PKGBUILD
