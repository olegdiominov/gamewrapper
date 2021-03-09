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
    game_config = config[selected_game]
    default_config = config['DEFAULT']

    if 'prefix' in game_config:
        prefix = Path(game_config['prefix']).expanduser()
        workdir = Path(prefix, game_config['workdir'])
        window_title = f'{selected_game} - Wine desktop'
    else:
        prefix = None
        workdir = Path(game_config['workdir']).expanduser()
        window_title = game_config['name']
    executable = game_config['exec']
    process_name = Path(executable).name
    game_resolution = game_config['resolution']
    default_resolution = default_config['resolution']

    async def update(i3, e=None):
        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()
        if workspace.find_named(window_title):
            selected_resolution = game_resolution
            selected_signal = signal.SIGCONT
        else:
            selected_resolution = default_resolution
            selected_signal = signal.SIGSTOP
        xrandr_process = await asyncio.create_subprocess_exec(
            'xrandr', '--size', selected_resolution
        )
        killall_process = await asyncio.create_subprocess_exec(
            'killall', '--signal', selected_signal.name, process_name
        )
        await asyncio.gather(killall_process.wait(), xrandr_process.wait())

    i3 = await i3ipc.aio.Connection().connect()
    i3.on(i3ipc.Event.WINDOW, update)
    i3_loop = asyncio.create_task(i3.main())

    if prefix is not None:
        game_args = [
            'wine', 'explorer', f'/desktop={selected_game},{game_resolution}',
            executable
        ]
        game_env = {**os.environ, 'WINEPREFIX': prefix}
    else:
        game_args = [executable]
        game_env = None
    print(workdir)
    game_process = await asyncio.create_subprocess_exec(
        *game_args, cwd=workdir, env=game_env
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
