import asyncio
import aiofiles
import os
from pathlib import Path
from argparse import ArgumentParser
from loguru import logger
from typing import AsyncGenerator, Awaitable

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")

async def copy_file(source_path: Path, destination_folder: Path) -> None:
    try:
        extension = source_path.suffix[1:] or "no_extension"

        destination_path = destination_folder / extension / source_path.name

        destination_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(source_path, 'rb') as src, \
                aiofiles.open(destination_path, 'wb') as dst:
            while chunk := await src.read(1024):  
                await dst.write(chunk)

        logger.info(f"Copied {source_path} to {destination_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {source_path}")
    except PermissionError:
        logger.error(f"Permission error when copying {source_path}")
    except Exception as e:
        logger.error(f"Error copying {source_path}: {e}")

async def read_folder(source_folder: str, output_folder: str) -> None:
    source_path = Path(source_folder)  
    output_path = Path(output_folder)

    for file in source_path.rglob('*'):  
        if file.is_file():  
            await copy_file(file, output_path)

async def main() -> None:
    parser = ArgumentParser(description="Asynchronously sorts files by extension.")
    parser.add_argument('source_folder', type=str, help='Source folder to read files from.')
    parser.add_argument('output_folder', type=str, help='Destination folder to copy files to.')
    args = parser.parse_args()
    await read_folder(args.source_folder, args.output_folder)

if __name__ == '__main__':
    asyncio.run(main())
