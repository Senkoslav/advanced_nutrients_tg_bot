"""
Скрипт для настройки команд и меню бота в Telegram
"""
import asyncio
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from config import BOT_TOKEN

async def setup_bot_commands():
    bot = Bot(token=BOT_TOKEN)
    
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
    ]
    
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        print("Команды бота успешно настроены!")
        print("\nДоступные команды:")
        for cmd in commands:
            print(f"  /{cmd.command} - {cmd.description}")
        
    except Exception as e:
        print(f"Ошибка при настройке команд: {e}")
    
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(setup_bot_commands())
