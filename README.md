# Porygon

A fun little Arch-based distro that boots into a 1990s SGI workstation: the
[MaXX Interactive Desktop](https://docs.maxxinteractive.com/) (a licensed
recreation of IRIX's Indigo Magic desktop) on X11.

- **Base:** Arch Linux, stock `linux` kernel
- **Desktop:** MaXX Interactive Desktop 2.2.0 (5Dwm, Toolchest, ROX desktop)
  started straight from tty1, no login screen
- **Root filesystem:** XFS, as on IRIX
- **Laptop bits:** NetworkManager (`nmtui`), PipeWire, power-profiles-daemon,
  thermald, tap-to-click, brightness and volume keys
- **Apps:** Firefox, xterm, xpdf, pavucontrol, fastfetch

## Build

On Arch (Arch WSL works):

```
./build.sh
```

The ISO lands in `out/`. The first build compiles a handful of AUR packages
(`gtk2` takes the longest); later builds reuse them.

## Use

- The live USB logs in as `porygon` and starts the desktop.
- To install: open a terminal and run `porygon-install`. It's UEFI-only and
  erases the disk you pick by number.
- Wi-Fi: `nmtui` in a terminal.

## Commands

| Command | Does |
|---|---|
| `upgrade` | update the system |
| `upgrade install PKG` / `remove PKG` / `search TERM` / `info PKG` / `list` / `clean` | the usual |
| `dubious-disc` | full evolution: system update, then rebuilds MaXX and the other AUR parts if there are newer versions |

## Licences

Porygon's own scripts are yours to do what you like with. The MaXX Interactive
Desktop is © Eric Masson and is used under its own licence
(`/opt/MaXX/doc/LICENSE`); the build fetches it unmodified from its official
source via the AUR. Porygon isn't endorsed by MaXX Interactive, SGI or
Nintendo; the name is a fan tribute.
