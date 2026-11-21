#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="porygon"
iso_label="PORYGON_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="Porygon <https://github.com/factionparadox/PorygonLinux>"
iso_application="Porygon Live/Install medium"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="porygon"
bootmodes=('bios.syslinux'
           'uefi.grub')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
  ["/etc/sudoers.d"]="0:0:750"
  ["/etc/sudoers.d/porygon"]="0:0:440"
  ["/root"]="0:0:750"
  ["/root/.gnupg"]="0:0:700"
  ["/etc/porygon/session"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/usr/local/bin/upgrade"]="0:0:755"
  ["/usr/local/bin/dubious-disc"]="0:0:755"
  ["/usr/local/bin/porygon-install"]="0:0:755"
  ["/usr/local/bin/porygon-welcome"]="0:0:755"
  ["/usr/local/bin/porygon-evolved"]="0:0:755"
  ["/usr/local/bin/porygon-record-evolution"]="0:0:755"
  ["/usr/local/bin/porygon-demo"]="0:0:755"
  ["/usr/local/bin/porygon-demos-folder"]="0:0:755"
  ["/usr/local/bin/porygon-chime"]="0:0:755"
  ["/usr/local/bin/porygon-theme"]="0:0:755"
  ["/usr/local/bin/porygon-setup-home"]="0:0:755"
  ["/usr/local/bin/porygon-make-scheme"]="0:0:755"
)
