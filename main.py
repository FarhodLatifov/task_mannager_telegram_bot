import asyncio
import logging
from sys import stdout
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import database as db
from handlers import router

from dotenv import load_dotenv
from os import getenv
load_dotenv()

# Token should ideally be in env vars, but using the one provided in original file for continuity if not set
TOKEN = getenv("BOT_TOKEN")

async def main() -> None:
    # Initialize Database
    await db.init_db()

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
