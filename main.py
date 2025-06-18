import asyncio
import argparse
import logging
from aiopath import AsyncPath
from aioshutil import copyfile

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, required=True, help="Source folder path")
parser.add_argument(
    "--destination", type=str, default="dist", help="Destination folder path"
)
parsed_args = vars(parser.parse_args())
source_folder = AsyncPath(parsed_args["source"])
destination_folder = AsyncPath(parsed_args["destination"])


async def read_folder(path: AsyncPath) -> None:
    async for el in path.iterdir():
        if await el.is_dir():
            await read_folder(el)
        else:
            await copy_file(el)


async def copy_file(file: AsyncPath) -> None:
    try:
        ext = file.suffix.lstrip(".").lower() or "no_extension"
        new_path = destination_folder / ext
        await new_path.mkdir(exist_ok=True, parents=True)
        await copyfile(file, new_path / file.name)
    except FileNotFoundError as e:
        logging.error("File not found: %s - %s", file, e)
    except PermissionError as e:
        logging.error("Permission denied for file: %s - %s", file, e)
    except OSError as e:
        logging.error("OS error copying file: %s - %s", file, e)
    except Exception as e:
        logging.error("Unexpected error copying file: %s - %s", file, e)


async def main():
    await destination_folder.mkdir(exist_ok=True, parents=True)
    await read_folder(source_folder)
    logging.info("Copy completed")


if __name__ == "__main__":
    asyncio.run(main())
