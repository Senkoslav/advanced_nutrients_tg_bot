from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_reply_kb():
    """Постоянная клавиатура внизу экрана"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❓ Задать вопрос"),
                KeyboardButton(text="📍 Где купить")
            ],
            [
                KeyboardButton(text="💼 B2B / Оптовые закупки"),
                KeyboardButton(text="🔔 Уведомления")
            ],
            [
                KeyboardButton(text="ℹ️ О бренде"),
                KeyboardButton(text="🏠 Главное меню")
            ]
        ],
        resize_keyboard=True, 
        persistent=True  
    )
