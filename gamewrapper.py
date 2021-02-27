import asyncio
import os
import sys
from configparser import ConfigParser
from pathlib import Path


async def main():
    config = ConfigParser()
    config_path = Path(
        os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'),
        'gamewrapper', 'config.ini'
    )
    config.read(config_path)
    selected_game = sys.argv[1]

    prefix = Path(config.get(selected_game, 'prefix')).expanduser()
    workdir = Path(prefix, config.get(selected_game, 'workdir'))
    executable = config.get(selected_game, 'exec')
    resolution = config.get(selected_game, 'resolution')

    game_process = await asyncio.create_subprocess_exec(
        'wine', 'explorer', f'/desktop={selected_game},{resolution}',
        executable,
        cwd=workdir,
        env={**os.environ, 'WINEPREFIX': prefix}
    )
    await game_process.wait()


if __name__ == '__main__':
    asyncio.run(main())
