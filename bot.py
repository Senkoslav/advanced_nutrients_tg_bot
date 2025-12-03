import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import common, expert, subscription, where_buy, b2b
from database.core import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(expert.router)
    dp.include_router(b2b.router)
    dp.include_router(subscription.router)
    dp.include_router(where_buy.router)
    dp.include_router(common.router)  

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        logging.info("Bot started successfully!")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(main())