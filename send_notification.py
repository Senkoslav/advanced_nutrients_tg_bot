"""
Скрипт для отправки уведомлений всем подписчикам Early Access
Используйте этот скрипт, когда будете готовы запустить продажи
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database.core import init_db, get_all_subscribers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

NOTIFICATION_MESSAGE = """
🎉 <b>Advanced Nutrients Russia — официальный запуск!</b>

Мы рады сообщить, что каталог продукции Advanced Nutrients теперь доступен в России!

🌿 <b>Что доступно:</b>
• Полная линейка удобрений pH Perfect
• Стимуляторы и аддитивы
• Схемы питания для всех систем выращивания
• Консультации экспертов

📦 <b>Оформить заказ:</b>
[Ссылка на каталог или сайт]

Спасибо, что были с нами с самого начала! 🙏
"""

async def send_notifications():
    """Отправляет уведомления всем подписчикам"""
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # Получаем всех подписчиков
        subscribers = await get_all_subscribers()
        total = len(subscribers)
        
        logging.info(f"Найдено подписчиков: {total}")
        
        if total == 0:
            logging.warning("Нет подписчиков для рассылки")
            return
        
        print(f"\n⚠️  ВНИМАНИЕ! Будет отправлено {total} сообщений.")
        print(f"Текст сообщения:\n{NOTIFICATION_MESSAGE}\n")
        confirm = input("Продолжить? (yes/no): ")
        
        if confirm.lower() != 'yes':
            logging.info("Рассылка отменена пользователем")
            return
        
        success_count = 0
        failed_count = 0
        
        for user in subscribers:
            try:
                await bot.send_message(
                    chat_id=user.user_id,
                    text=NOTIFICATION_MESSAGE,
                    parse_mode="HTML"
                )
                success_count += 1
                logging.info(f"✅ Отправлено пользователю {user.user_id} (@{user.username})")
                
                await asyncio.sleep(0.05)
                
            except Exception as e:
                failed_count += 1
                logging.error(f"❌ Ошибка отправки пользователю {user.user_id}: {e}")
        
        logging.info(f"\n{'='*50}")
        logging.info(f"Рассылка завершена!")
        logging.info(f"Успешно отправлено: {success_count}")
        logging.info(f"Ошибок: {failed_count}")
        logging.info(f"{'='*50}")
        
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
    
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(send_notifications())
