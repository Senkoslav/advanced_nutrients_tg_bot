from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from states.user_states import B2BState
from config import ADMIN_CHAT_ID
from filters.chat_filters import NotAdminChatFilter
from datetime import datetime
import re

router = Router()

@router.callback_query(F.data == "nav_b2b")
async def start_b2b_dialog(callback: types.CallbackQuery, state: FSMContext):
    import logging
    logging.info(f"User {callback.from_user.id} started B2B dialog")
    
    await callback.message.answer(
        "💼 <b>B2B / Оптовые закупки</b>\n\n"
        "Укажите название вашей компании:",
        parse_mode="HTML"
    )
    await state.set_state(B2BState.waiting_company)
    await callback.answer()

@router.message(F.text == "💼 B2B / Оптовые закупки", NotAdminChatFilter())
async def reply_b2b(message: types.Message, state: FSMContext):
    import logging
    logging.info(f"User {message.from_user.id} started B2B dialog via reply button")
    
    await message.answer(
        "💼 <b>B2B / Оптовые закупки</b>\n\n"
        "Укажите название вашей компании:",
        parse_mode="HTML"
    )
    await state.set_state(B2BState.waiting_company)

@router.message(
    B2BState.waiting_company,
    F.text.in_([
        "🏠 Главное меню",
        "❓ Задать вопрос",
        "📍 Где купить",
        "🔔 Уведомления",
        "ℹ️ О бренде"
    ])
)
async def cancel_on_company_input(message: types.Message, state: FSMContext):
    """Отмена диалога при нажатии других кнопок меню"""
    import logging
    logging.info(f"User {message.from_user.id} cancelled B2B dialog at company input")
    await state.clear()
    
    from keyboards.inline import main_menu_kb
    
    if message.text == "🏠 Главное меню":
        from handlers.common import WELCOME_TEXT
        await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
    elif message.text == "📍 Где купить":
        from handlers.where_buy import WHERE_BUY_TEXT
        await message.answer(WHERE_BUY_TEXT, parse_mode="HTML", disable_web_page_preview=True)
    elif message.text == "ℹ️ О бренде":
        from handlers.common import ABOUT_TEXT
        await message.answer(ABOUT_TEXT)

@router.message(B2BState.waiting_company)
async def process_company(message: types.Message, state: FSMContext):
    import logging
    
    company_name = message.text.strip()
    
    if not company_name or len(company_name) < 2:
        await message.answer("⚠️ Пожалуйста, укажите корректное название компании.")
        return
    
    logging.info(f"User {message.from_user.id} entered company: {company_name}")
    
    await state.update_data(company_name=company_name)
    
    await message.answer(
        "Отлично! Теперь отправьте ваш рабочий email для связи с менеджером Advanced Nutrients Russia."
    )
    await state.set_state(B2BState.waiting_email)

@router.message(
    B2BState.waiting_email,
    F.text.in_([
        "🏠 Главное меню",
        "❓ Задать вопрос",
        "📍 Где купить",
        "🔔 Уведомления",
        "ℹ️ О бренде"
    ])
)
async def cancel_on_email_input(message: types.Message, state: FSMContext):
    """Отмена диалога при нажатии других кнопок меню"""
    import logging
    logging.info(f"User {message.from_user.id} cancelled B2B dialog at email input")
    await state.clear()
    
    from keyboards.inline import main_menu_kb
    
    if message.text == "🏠 Главное меню":
        from handlers.common import WELCOME_TEXT
        await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
    elif message.text == "📍 Где купить":
        from handlers.where_buy import WHERE_BUY_TEXT
        await message.answer(WHERE_BUY_TEXT, parse_mode="HTML", disable_web_page_preview=True)
    elif message.text == "ℹ️ О бренде":
        from handlers.common import ABOUT_TEXT
        await message.answer(ABOUT_TEXT)

@router.message(B2BState.waiting_email)
async def process_email(message: types.Message, state: FSMContext, bot: Bot):
    import logging
    
    email = message.text.strip()
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await message.answer(
            "⚠️ Пожалуйста, укажите корректный email адрес.\n"
            "Пример: company@example.com"
        )
        return
    
    logging.info(f"User {message.from_user.id} entered email: {email}")
    
    data = await state.get_data()
    company_name = data.get("company_name")
    
    username = f"@{message.from_user.username}" if message.from_user.username else "не указан"
    user_id = message.from_user.id
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    admin_text = f"""
🏢 <b>Новый B2B-запрос</b>

<b>Компания:</b> {company_name}
<b>Email:</b> {email}
<b>Telegram:</b> {username} (ID: {user_id})
<b>Дата/время:</b> {timestamp}
"""
    
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            parse_mode="HTML"
        )
        logging.info(f"B2B request sent to admin from user {user_id}")
        
        await message.answer(
            "✅ <b>Спасибо за интерес к сотрудничеству!</b>\n\n"
            "Ваш запрос получен. Менеджер Advanced Nutrients Russia свяжется с вами "
            "в ближайшее время для обсуждения условий оптовых поставок.\n\n"
            "📧 Ответ придёт на указанный email.",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Error sending B2B request to admin: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при отправке запроса. Пожалуйста, попробуйте позже или "
            "свяжитесь с нами напрямую."
        )
    
    await state.clear()
