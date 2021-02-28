import asyncio
import os
import signal
from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path

import i3ipc.aio


async def run_game(selected_game):
    config = ConfigParser()
    config_path = Path(
        os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'),
        'gamewrapper', 'config.ini'
    )
    config.read(config_path)

    prefix = Path(config.get(selected_game, 'prefix')).expanduser()
    workdir = Path(prefix, config.get(selected_game, 'workdir'))
    executable = config.get(selected_game, 'exec')
    game_resolution = config.get(selected_game, 'resolution')
    default_resolution = config.get('DEFAULT', 'resolution')

    async def update(i3, e=None):
        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()
        if workspace.find_named(f'{selected_game} - Wine desktop'):
            selected_resolution = game_resolution
            selected_signal = signal.SIGCONT
        else:
            selected_resolution = default_resolution
            selected_signal = signal.SIGSTOP
        xrandr_process = await asyncio.create_subprocess_exec(
            'xrandr', '--size', selected_resolution
        )
        killall_process = await asyncio.create_subprocess_exec(
            'killall', '--signal', selected_signal.name, executable
        )
        await asyncio.gather(killall_process.wait(), xrandr_process.wait())

    i3 = await i3ipc.aio.Connection().connect()
    i3.on(i3ipc.Event.WINDOW, update)
    i3_loop = asyncio.create_task(i3.main())

    game_process = await asyncio.create_subprocess_exec(
        'wine', 'explorer', f'/desktop={selected_game},{game_resolution}',
        executable,
        cwd=workdir,
        env={**os.environ, 'WINEPREFIX': prefix}
    )
    await game_process.wait()
    i3_loop.cancel()
    await update(i3)


def main():
    parser = ArgumentParser()
    parser.add_argument('game')
    args = parser.parse_args()
    asyncio.run(run_game(args.game))


if __name__ == '__main__':
    main()
