# gamewrapper

Convenience tool for running older games with Wine and i3 window manager.

## Features

### Running games with a single command

I typically disable Wine's automatic creation of `.desktop` entries during game
installation (`winemenubuilder`) for a few reasons:

- It tends to create entries I don't need (e.g. uninstall or help).

- There can be a lot of entries and icons left behind if you create and delete
prefixes often, and it's not always clear which ones you need and which ones you
don't.

- It can mess with your file associations if you're not careful.

This means I have to run games manually, which requires setting `WINEPREFIX`
variable and working directory (some games are picky about it). This tool helps
me do it.

### Resolution switching

I often have problems with switching workspaces in i3 when running fullscreen
games. Wine virtual desktops don't have this problem, but can be inconvenient if
you need a non-native resolution. I use the following approach with this tool:

- Run a game in a virtual desktop of appropriate size (e.g. 800x600) which acts
as a normal window as far as i3 is concerned.

- When workspace with a game is focused, switch monitor to that resolution with
`xrandr`.

- When workspace without a game is focused, switch back to native resolution.

As a bonus, I can also set virtual desktop size per game even if they're in the
same prefix, compared to doing it per prefix with `winecfg`.

### Pause/unpause

In line with resolution switching logic, I decided to implement automatically
pausing and unpausing games when switching workspaces. This is done by sending
`SIGSTOP` and `SIGCONT` signals to the game process.

Note that this signal approach is somewhat crude and may cause some games to
freak out. This also obviously isn't ideal if you need a game to idle for a
while.

On the positive side, this reduces CPU usage and allows pausing even when you
normally can't (e.g. during cutscenes).

## Configuration

Configuration file is located at `$XDG_CONFIG_HOME/gamewrapper/config.ini` (or
`~/.config/gamewrapper/config.ini`) and uses Python's `configparser` syntax.

```ini
[DEFAULT]
resolution = 1920x1080

[fo2]
name = Fallout 2
prefix = ~/wine/gog
workdir = drive_c/GOG Games/Fallout 2
exec = fallout2.exe
resolution = 640x480
```

Each section other than `DEFAULT` defines one game.

- `prefix` - absolute path to Wine prefix. `~` is expanded, environment
variables are not.

- `workdir` - path to working directory, relative to `prefix`.

- `exec` - path to game executable, relative to `workdir`.

- `resolution` - game resolution (or native resolution if `DEFAULT`). Always
use `x` as separator. Make sure it's a valid `xrandr` mode.

## Usage

Make sure `wine`, `killall` and `xrandr` are available.

Run `python -m gamewrapper <game>`, where `<game>` is the config section name.
