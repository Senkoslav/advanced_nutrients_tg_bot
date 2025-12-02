from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards.inline import main_menu_kb
from keyboards.reply import main_reply_kb
from filters.chat_filters import NotAdminChatFilter

router = Router()

WELCOME_TEXT = """
👋 Добро пожаловать в Advanced Nutrients Russia.
Это официальный Telegram-бот бренда — здесь вы получите:
• консультацию по питанию и схемам AN (Advanced Nutrients)
• помощь в выборе удобрений под вашу систему выращивания
• доступ к обновлениям, схемам и запуску каталога в РФ
 
⚠️ Сейчас мы готовим первый официальный релиз продуктов на рынок России.
Чтобы получить уведомление о старте продаж и каталоге — нажмите «🔔 Уведомить о запуске».
 
👇 Выберите действие:
"""

ABOUT_TEXT = """
🏆 Advanced Nutrients — мировой лидер в области питания растений.
 
• 25 лет исследований и лабораторной работы
• pH Perfect формулы нового поколения
• стимуляторы, аддитивы и микробиология для максимального результата
• продукция используется в более чем 100 странах профессиональными производителями
 
Мы создаём первую официальную платформу Advanced Nutrients в России.
Скоро здесь появится каталог продукции, схемы питания, рекомендации и обучающие материалы.
"""

@router.message(CommandStart(), NotAdminChatFilter())
async def cmd_start(message: types.Message, state: FSMContext):
    # Сбрасываем любые активные состояния при перезапуске
    await state.clear()
    await message.answer(
        WELCOME_TEXT, 
        reply_markup=main_menu_kb()
    )
    # Отправляем постоянную клавиатуру отдельным сообщением
    await message.answer(
        "Используйте кнопки ниже для быстрого доступа:",
        reply_markup=main_reply_kb()
    )

@router.callback_query(F.data == "nav_about")
async def show_about(callback: types.CallbackQuery):
    await callback.message.answer(ABOUT_TEXT)
    await callback.answer()
    # Опционально можно показать меню снова, но по ТЗ просто текст

# Обработчики для Reply-кнопок
@router.message(F.text == "🏠 Главное меню", NotAdminChatFilter())
async def reply_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())

@router.message(F.text == "ℹ️ О бренде", NotAdminChatFilter())
async def reply_about(message: types.Message):
    await message.answer(ABOUT_TEXT)

@router.message(NotAdminChatFilter())
async def handle_unexpected_message(message: types.Message, state: FSMContext):
    """Обработка неожиданных сообщений вне диалогов"""
    # Проверяем, есть ли активное состояние FSM
    current_state = await state.get_state()
    if current_state is None:
        # Только если нет активного состояния, показываем меню
        await message.answer(
            "Используйте команду /start для возврата в главное меню.",
            reply_markup=main_menu_kb()
        )