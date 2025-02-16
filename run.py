import asyncio

from aiogram import Bot, Dispatcher
from app.handlers import router
from config import BOT_TOKEN
from app.database.database import init_db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    await init_db()
    print('...The bot is active...')
    dp.include_router(router=router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('...Shutting down...')