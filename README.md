# Porygon (Manjaro edition)

A fun little Manjaro-based distro that boots into a 1990s SGI workstation: the
[MaXX Interactive Desktop](https://docs.maxxinteractive.com/) (a licensed
recreation of IRIX's Indigo Magic desktop) on X11.

**A computer that works for you.** No accounts, no telemetry, nothing that
phones home behind your back; the AI runs on the machine; the computer nudges
you to rest instead of keeping you hooked. With a writer's kit (spelling in
British English and Russian, offline dictionaries) and an offline Russian course.

- **Base:** Manjaro stable (yes, really), `linux72` kernel, pamac. MaXX's own
  install guide is written for Manjaro, so this is the officially blessed way to be wrong.
- **systemd:** the liberated fork from the AUR (`systemd-liberated-git`),
  which removes the `birthDate` field from user records. It's built from the
  fork's newest commit (unreleased systemd 263), so it runs ahead of the rest
  of Manjaro stable (261). `build/fix-systemd-liberated-git.sh` patches the AUR
  recipe to build on Manjaro (Rust, bindgen and Manjaro's kernel headers).
- **Desktop:** MaXX Interactive Desktop 2.2.0 (5Dwm, Toolchest, ROX desktop)
  started straight from tty1, no login screen
- **Root filesystem:** Btrfs (subvolumes `@`, `@home`, `@log`, `@pkg`, zstd
  compression), with Snapper taking a snapshot before and after every update
- **Boot menu:** Limine, themed with the Porygon backdrop. Every snapshot is in
  the menu with the kernel it had (limine-snapper-sync); booting one is safe to
  try, and Porygon offers to keep it. Kernel: `linux72` (Manjaro no longer
  ships 7.1)
- **Laptop bits:** a status strip at the top of the screen (`porygon-status`)
  showing Wi-Fi, Bluetooth, brightness, volume, battery and the time; click a
  part for its controls (Wi-Fi window, Blueman, sliders, power profiles, a
  calendar). Low-battery warnings at 15% and 7%, sleep at 3%. NetworkManager,
  BlueZ, PipeWire, power-profiles-daemon, thermald, tap-to-click, brightness
  and volume keys
- **Terminal:** MaXX's winterm running fish, with a Porygon-coloured prompt and
  short forms (`up` = upgrade, `in` = upgrade install, `undo`). The text
  consoles keep bash
- **Apps:** Firefox, pamac (Add/Remove Software), qmmp, mpv, Kiwix, xpdf, pavucontrol, fastfetch

## What you get

- **Porygon colours:** a pink-and-blue MaXX colour scheme (pink active title
  bars, blue inactive ones), built on your machine from MaXX's Indigo Magic
  scheme by a pacman hook, plus a low-poly backdrop. `porygon-theme off`
  goes back to the SGI look; `porygon-theme on` brings Porygon back.
- **Start-up chime:** an original chord that plays as the desktop starts
  (touch `~/.local/state/porygon/chime-off` to silence it).
- **Porygon System Manager:** a welcome screen in the style of a 1990s
  system manager: Wi-Fi, installing, updating, demos, look & feel.
- **Toolchest additions:** *Porygon* (System Manager, What's New, Upgrade,
  Dubious Disc, Network, colours), *Apps* (Firefox, qmmp, irssi, editor,
  image viewer, xpdf, xcalc, xclock) and *Demos*.
- **Demos:** MaXX's SGI classics (Atlantis, Ideas in Motion, Flurry...),
  xscreensaver's polyhedra and screen-saver favourites, and Mesa's test demos,
  all via `porygon-demo NAME` (`porygon-demo --list`).
- **Era apps:** qmmp with its Winamp-style skin, irssi in a winterm, and
  Firefox restyled with square bevelled toolbars and a pink tab (via
  autoconfig, so every profile gets it once; edit the profile's
  `chrome/userChrome.css` to change it).
- **Wellbeing:** a night light in the evening, a gentle "rest your eyes?"
  after about 50 minutes at the keyboard (time away counts, so it never nags
  twice), one bedtime reminder with rain and a sleep timer, and a breathing
  window. Nothing ever locks you out. Settings in the System Manager or
  `~/.config/porygon/wellbeing.conf`.
- **Calm (Toolchest):** breathing, ambience moods (one per folder in
  `~/Ambience`), sleep timers, music, and **Porygon-Z**, someone to talk to who
  runs on this computer through a local Ollama (`porygon-z`).
- **Russian (Toolchest):** alphabet to B2 offline: a route through the levels,
  spaced-repetition words with Piper voices, listening, a library, a Kiwix
  dictionary and a local AI tutor. The large pieces download once with
  `sudo porygon-content`, each file checked.
- **Privacy:** Firefox with telemetry, studies, Pocket and sponsored tiles off;
  NetworkManager's online check off; no fallback DNS. The System Manager's
  Privacy page lists everything that uses the network.
- **Power:** thermald, power-saver profile on battery, sleeping PCI/USB devices
  (not keyboards and mice), sound-chip and Wi-Fi power saving, NMI watchdog off.
- **Updates that don't bite:**
  - `upgrade` shows Manjaro's known issues for the update first (from the
    stable-update announcement), marking any that name a package you have.
  - `upgrade undo` / Toolchest → Porygon → Undo an Update: back to before an
    update via the boot menu's snapshots. Btrfs Assistant browses them all.
  - `upgrade later`: download now, install at shutdown (pamac's offline upgrade).
  - AUR builds check their dependencies first. Anything Manjaro stable is
    missing or has too old is built from Arch's own recipe, once, and replaced
    by Manjaro's package when stable catches up. Nothing else is compiled.
  - After an update, AUR programs left broken by a library change are found and
    offered a rebuild.
  - AUR lookups are cached for a day.
  - The installer runs Manjaro's hardware detection (`mhwd`) for graphics drivers.
- **What's New:** after `upgrade` ("Porygon evolved into Porygon2!") or
  `dubious-disc` ("Porygon2 evolved into Porygon-Z!"), a window lists what
  changed.

The art (wallpaper, icons, splash, chime) is generated by the scripts in
`art/` from the palette in `art/palette.py`, so it's easy to retune.

## Build

On Arch or Manjaro (Arch WSL works). It uses its own Manjaro keyring in `.build/`,
so your system keyring isn't touched:

```
./build.sh
```

The ISO lands in `out/`. Your own large files can ride along in `local/`
(kept out of git): `local/felix-models` (Porygon-Z's Ollama model),
`local/music` and `local/ambience`. A `DreamOS/local` folder in your home is
used too. The first build compiles a handful of AUR packages
inside a clean Manjaro chroot (`gtk2` takes the longest); later builds reuse them.

## Use

- The live USB logs in as `porygon` and starts the desktop.
- To install: double-click Install Porygon on the desktop (or Toolchest →
  Porygon → Install Porygon). Porygon Setup is a 1990s-style wizard: disk,
  user, region, a summary, then a progress bar. `sudo porygon-install` does the
  same in a terminal. It's UEFI-only and erases the disk you choose: 2 GiB EFI partition (Limine and the
  kernels, including one per snapshot), the rest Btrfs.
- Wi-Fi: `nmtui` in a terminal.

## Commands

| Command | Does |
|---|---|
| `upgrade` | update the system (via pamac) |
| `upgrade install PKG` | install, picking the source by number: Manjaro stable, testing or unstable (when newer there), or the AUR. A testing/unstable choice sticks through updates |
| `upgrade branches` | programs on testing/unstable; move one back to stable |
| `upgrade later` | download updates now, install them at shutdown |
| `upgrade undo` | go back to before an update (boot menu → Snapshots) |
| `upgrade remove PKG` / `search TERM` / `info PKG` / `list` / `clean` | the usual |
| `upgrade mirrors` | pick the fastest Manjaro mirrors |
| `porygon-z` | talk to Porygon-Z (`--journal` keeps the conversation) |
| `porygon-russian path` / `words` / `tutor` / `listen` | the Russian course |
| `porygon-wellbeing status` / `restart` / `breathe` | the reminders |
| `porygon-listen ambience MOOD` / `sleep 45` / `stop` | calm sounds |
| `dubious-disc` | full evolution: system update, then rebuilds MaXX and the other AUR parts if there are newer versions (`pamac upgrade --aur --devel`, so it also rebuilds liberated systemd from its newest commit - slow) |

## Licences

| Part | Licence |
|---|---|
| Porygon's own files (scripts, build profile, `art/`) | not chosen yet |
| MaXX Interactive Desktop | MaXX's own licence, © Eric Masson: the older code may be redistributed only as unmodified binaries; newer code is BSD-3-Clause. Full text in `/opt/MaXX/doc/LICENSE` |
| systemd (liberated fork) | LGPL-2.1-or-later, with some GPL-2.0-or-later parts |
| limine-mkinitcpio-hook, limine-snapper-sync (prebuilt in `repo/`) | GPL-3.0 |
| Everything else from Manjaro | each package's own licence, in `/usr/share/licenses` |

"Porygon" is a Pokémon name owned by Nintendo, Creatures and Game Freak.
This is an unofficial fan project.
