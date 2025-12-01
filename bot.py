import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import common, expert, subscription
from database.core import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Инициализация БД
    await init_db()
    
    # Создание объектов бота и диспетчера с хранилищем состояний
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров (обработчиков)
    # ВАЖНО: Специфичные обработчики (с FSM) должны быть ПЕРВЫМИ
    dp.include_router(expert.router)
    dp.include_router(subscription.router)
    dp.include_router(common.router)  # Общие обработчики в конце

    # Удаление вебхука и запуск поллинга
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        logging.info("Bot started successfully!")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(main())