"""
Скрипт для тестирования доступа бота к админ-чату
"""
import asyncio
from aiogram import Bot
from config import BOT_TOKEN, ADMIN_CHAT_ID

async def test_admin_access():
    bot = Bot(token=BOT_TOKEN)
    
    print(f"Testing access to admin chat: {ADMIN_CHAT_ID}")
    print(f"Bot token: {BOT_TOKEN[:20]}...")
    
    try:
        # Попытка получить информацию о чате
        chat = await bot.get_chat(ADMIN_CHAT_ID)
        print(f"✅ Chat found!")
        print(f"   Title: {chat.title}")
        print(f"   Type: {chat.type}")
        print(f"   ID: {chat.id}")
        
        # Попытка получить информацию о боте в чате
        try:
            member = await bot.get_chat_member(ADMIN_CHAT_ID, bot.id)
            print(f"✅ Bot is member of chat!")
            print(f"   Status: {member.status}")
            print(f"   Can post messages: {member.status in ['administrator', 'creator']}")
        except Exception as e:
            print(f"❌ Error getting bot member info: {e}")
        
        # Попытка отправить тестовое сообщение
        print("\nTrying to send test message...")
        result = await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="🧪 <b>Тестовое сообщение</b>\n\nЕсли вы видите это сообщение, бот имеет доступ к чату!",
            parse_mode="HTML"
        )
        print(f"✅ Message sent successfully! Message ID: {result.message_id}")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_admin_access())
