import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config.config import BOT_TOKEN
from database.db import init_db
from handlers import start, room, join, room_menu, problem, round, endround, delete_room, players

logging.basicConfig(level=logging.INFO)

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не указан в .env")
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))
    dp = Dispatcher()
    
    await init_db()
    
    dp.include_router(start.router)
    dp.include_router(room.router)
    dp.include_router(join.router)
    dp.include_router(room_menu.router)
    dp.include_router(problem.router)
    dp.include_router(round.router)
    dp.include_router(endround.router)
    dp.include_router(delete_room.router)
    dp.include_router(players.router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
