import asyncio
import logging
import re
import sys
from os import getenv, path, remove
from uuid import uuid4

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Message
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

if getenv("TOKEN") == "":
    print("You should set `TOKEN` environment variable.")
    exit(1)

TOKEN = getenv("TOKEN", "")

dp = Dispatcher()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Пришли код в виде файла или текста и я тебе его раздефайню!")


@dp.message()
async def undefiner_handler(message: Message) -> None:
    download_path = "cpps/" + str(uuid4()) + ".cpp"
    if not message.document or not message.document.file_id:
        if not message.text:
            return
        with open(download_path, "w+") as f:
            f.write(message.text)
    else:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        if not isinstance(file_path, str):
            return
        if not file_path.endswith(".cpp"):
            await message.reply("Расширенние не .cpp!")
            return
        await bot.download_file(file_path, download_path)
    includes = []
    with open(download_path, "r+") as f:
        data = f.read()
        includes = re.findall(r"^\#include .*$", data, flags=re.MULTILINE)
        for i in includes:
            data = data.replace(i, "")
        f.seek(0)
        f.truncate(0)
        f.write(data)
    result_path = "cpps/" + download_path + ".res.cpp"
    process = await asyncio.create_subprocess_exec(
        "g++", "-E", "-nostdinc", "-C", download_path, "-o", result_path
    )
    await process.wait()
    if process.returncode != 0:
        await message.reply("G++ threw an error!")
        return
    process = await asyncio.create_subprocess_exec(
        "clang-format", "--style=Google", "-i", result_path
    )
    await process.wait()
    if process.returncode != 0:
        await message.reply("Clang-format threw an error!")
    if path.exists(result_path):
        with open(result_path, "r+") as f:
            data = f.read()
            data = re.sub(r"^\# .*$", "", data, flags=re.MULTILINE)
            data = data.strip()
            data = "\n".join(includes) + "\n\n" + data
            print(data)
            f.seek(0)
            f.truncate(0)
            f.write(data)
        await message.answer_document(FSInputFile(result_path, filename="result.cpp"))
    else:
        await message.answer("something went wrong!")
    try:
        remove(download_path)
        remove(result_path)
    except:
        pass


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
