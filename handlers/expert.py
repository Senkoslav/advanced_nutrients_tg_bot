from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from states.user_states import AskExpertState
from keyboards.inline import system_choice_kb, phase_choice_kb, question_input_kb
from config import ADMIN_CHAT_ID
from database.core import save_question_mapping, get_user_by_admin_message
from filters.chat_filters import NotAdminChatFilter

router = Router()

@router.callback_query(F.data == "nav_ask_expert")
async def start_expert_dialog(callback: types.CallbackQuery, state: FSMContext):
    import logging
    logging.info(f"User {callback.from_user.id} started expert dialog")
    await callback.message.answer(
        "Выберите вашу систему выращивания:",
        reply_markup=system_choice_kb()
    )
    await state.set_state(AskExpertState.choosing_system)
    logging.info(f"State set to choosing_system for user {callback.from_user.id}")
    await callback.answer()

@router.message(F.text == "❓ Задать вопрос", NotAdminChatFilter())
async def reply_ask_expert(message: types.Message, state: FSMContext):
    import logging
    logging.info(f"User {message.from_user.id} started expert dialog via reply button")
    await message.answer(
        "Выберите вашу систему выращивания:",
        reply_markup=system_choice_kb()
    )
    await state.set_state(AskExpertState.choosing_system)
    logging.info(f"State set to choosing_system for user {message.from_user.id}")

@router.message(
    AskExpertState.choosing_system,
    F.text.in_([
        "🏠 Главное меню",
        "📍 Где купить",
        "💼 B2B / Оптовые закупки",
        "🔔 Уведомления",
        "ℹ️ О бренде"
    ])
)
async def cancel_on_system_choice(message: types.Message, state: FSMContext):
    """Отмена диалога при нажатии других кнопок меню"""
    import logging
    from keyboards.inline import main_menu_kb
    from handlers.common import WELCOME_TEXT, ABOUT_TEXT
    from handlers.where_buy import WHERE_BUY_TEXT
    
    logging.info(f"User {message.from_user.id} cancelled question dialog at system choice")
    await state.clear()
    
    # Обрабатываем нажатие кнопки
    if message.text == "🏠 Главное меню":
        await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
    elif message.text == "📍 Где купить":
        await message.answer(WHERE_BUY_TEXT, parse_mode="HTML", disable_web_page_preview=True)
    elif message.text == "ℹ️ О бренде":
        await message.answer(ABOUT_TEXT)

@router.callback_query(AskExpertState.choosing_system, F.data.startswith("sys_"))
async def choose_phase(callback: types.CallbackQuery, state: FSMContext):
    import logging
    system_map = {"sys_soil": "Soil", "sys_coco": "Coco", "sys_hydro": "Hydro"}
    selected_system = system_map.get(callback.data, "Unknown")
    
    logging.info(f"User {callback.from_user.id} selected system: {selected_system}")
    await state.update_data(system=selected_system)
    
    await callback.message.answer(
        "Выберите фазу роста:",
        reply_markup=phase_choice_kb()
    )
    await state.set_state(AskExpertState.choosing_phase)
    logging.info(f"State set to choosing_phase for user {callback.from_user.id}")
    await callback.answer()

# Обработчик отмены на этапе выбора фазы
@router.message(
    AskExpertState.choosing_phase,
    F.text.in_([
        "🏠 Главное меню",
        "📍 Где купить",
        "💼 B2B / Оптовые закупки",
        "🔔 Уведомления",
        "ℹ️ О бренде"
    ])
)
async def cancel_on_phase_choice(message: types.Message, state: FSMContext):
    """Отмена диалога при нажатии других кнопок меню"""
    import logging
    from keyboards.inline import main_menu_kb
    from handlers.common import WELCOME_TEXT, ABOUT_TEXT
    from handlers.where_buy import WHERE_BUY_TEXT
    
    logging.info(f"User {message.from_user.id} cancelled question dialog at phase choice")
    await state.clear()
    
    if message.text == "🏠 Главное меню":
        await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
    elif message.text == "📍 Где купить":
        await message.answer(WHERE_BUY_TEXT, parse_mode="HTML", disable_web_page_preview=True)
    elif message.text == "ℹ️ О бренде":
        await message.answer(ABOUT_TEXT)

@router.callback_query(AskExpertState.choosing_phase, F.data.startswith("phase_"))
async def request_text(callback: types.CallbackQuery, state: FSMContext):
    import logging
    phase_map = {"phase_veg": "Вегетация", "phase_bloom": "Цветение", "phase_full": "Полный цикл"}
    selected_phase = phase_map.get(callback.data, "Unknown")
    
    logging.info(f"User {callback.from_user.id} selected phase: {selected_phase}")
    await state.update_data(phase=selected_phase)
    
    if callback.data == "phase_veg":
        msg = """
🌿 <b>Вегетация</b>

Опишите, что происходит на веге сейчас и какой результат хотите получить (рост, плотность кроны, здоровье листьев). 

Укажите кратко:
• свет
• систему
• удобрения

Фото поможет точнее.
"""
    elif callback.data == "phase_bloom":
        msg = """
🌸 <b>Цветение</b>

Опишите ситуацию на цветении и желаемый результат: масса, плотность, сроки или выраженность аромата/смолы.

Кратко напишите про:
• свет
• схему питания
• проблему

Фото можно приложить.
"""
    elif callback.data == "phase_full":
        msg = """
🔁 <b>Полный цикл</b>

Опишите вашу ситуацию по циклу целиком: условия, какие продукты AN используете и что хотите улучшить (рост, масса, стабильность).

Фото бокса и растений поможет дать точный ответ.
"""
    else:
        msg = "❓ Опишите ваш вопрос максимально подробно. Фото можно приложить."
    
    await callback.message.answer(msg, parse_mode="HTML", reply_markup=question_input_kb())
    await state.set_state(AskExpertState.writing_question)
    logging.info(f"State set to writing_question for user {callback.from_user.id}. Waiting for text...")
    await callback.answer()

@router.message(
    AskExpertState.writing_question,
    ~F.text.in_([
        "🏠 Главное меню",
        "❓ Задать вопрос", 
        "📍 Где купить",
        "💼 B2B / Оптовые закупки",
        "🔔 Уведомления",
        "ℹ️ О бренде"
    ])
)
async def process_question(message: types.Message, state: FSMContext, bot: Bot):
    import logging
    
    data = await state.get_data()
    system = data.get("system")
    phase = data.get("phase")
    
    logging.info(f"Processing question from user {message.from_user.id}")
    logging.info(f"System: {system}, Phase: {phase}")
    logging.info(f"Admin chat ID: {ADMIN_CHAT_ID}")
    
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    admin_text = (
        f"🔔 <b>Новый вопрос от пользователя</b> {username}\n"
        f"<b>Система:</b> {system}\n"
        f"<b>Фаза:</b> {phase}\n\n"
        f"<b>Текст вопроса:</b>\n"
    )
    
    question_text = message.text or message.caption or "(Текст отсутствует)"
    admin_text += question_text

    try:
        logging.info(f"Attempting to send message to admin chat {ADMIN_CHAT_ID}")
        
        admin_text += f"\n\n💬 <i>Чтобы ответить пользователю, просто ответьте (reply) на это сообщение.</i>"
        
        if message.photo:
            photo_id = message.photo[-1].file_id
            result = await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_id, caption=admin_text, parse_mode="HTML")
            logging.info(f"Photo sent successfully to admin. Message ID: {result.message_id}")
        else:
            result = await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML")
            logging.info(f"Message sent successfully to admin. Message ID: {result.message_id}")
        
        await save_question_mapping(
            admin_message_id=result.message_id,
            user_id=message.from_user.id
        )
        logging.info(f"Saved mapping in DB: admin_msg_id={result.message_id} -> user_id={message.from_user.id}")
            
        user_reply = """
📨 Ваш вопрос отправлен эксперту Advanced Nutrients Russia.
Ответ будет направлен сюда — ожидайте.
Среднее время ответа: 1–6 часов.
        """
        await message.answer(user_reply)
        
    except Exception as e:
        await message.answer("Произошла ошибка при отправке вопроса. Попробуйте позже.")
        logging.error(f"Error sending to admin (ID: {ADMIN_CHAT_ID}): {type(e).__name__}: {e}")
        import traceback
        logging.error(traceback.format_exc())
    
    await state.clear()

@router.message(
    AskExpertState.writing_question,
    F.text.in_([
        "🏠 Главное меню",
        "📍 Где купить",
        "💼 B2B / Оптовые закупки",
        "🔔 Уведомления",
        "ℹ️ О бренде"
    ])
)
async def cancel_question_by_menu(message: types.Message, state: FSMContext):
    """Отмена диалога при нажатии других кнопок меню"""
    import logging
    from keyboards.inline import main_menu_kb
    from handlers.common import WELCOME_TEXT, ABOUT_TEXT
    from handlers.where_buy import WHERE_BUY_TEXT
    
    logging.info(f"User {message.from_user.id} cancelled question dialog by pressing menu button")
    await state.clear()
    
    if message.text == "🏠 Главное меню":
        await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
    elif message.text == "📍 Где купить":
        await message.answer(WHERE_BUY_TEXT, parse_mode="HTML", disable_web_page_preview=True)
    elif message.text == "ℹ️ О бренде":
        await message.answer(ABOUT_TEXT)

# Обработчики навигации (Назад)

@router.callback_query(F.data == "expert_back_to_system")
async def expert_back_to_system(callback: types.CallbackQuery, state: FSMContext):
    """Возврат к выбору системы"""
    import logging
    
    logging.info(f"User {callback.from_user.id} went back to system choice")
    await callback.message.edit_text(
        "Выберите вашу систему выращивания:",
        reply_markup=system_choice_kb()
    )
    await state.set_state(AskExpertState.choosing_system)
    await callback.answer()

@router.callback_query(F.data == "expert_back_to_phase")
async def expert_back_to_phase(callback: types.CallbackQuery, state: FSMContext):
    """Возврат к выбору фазы"""
    import logging
    
    logging.info(f"User {callback.from_user.id} went back to phase choice")
    await callback.message.edit_text(
        "Выберите фазу роста:",
        reply_markup=phase_choice_kb()
    )
    await state.set_state(AskExpertState.choosing_phase)
    await callback.answer()

@router.message(F.chat.id == ADMIN_CHAT_ID, F.reply_to_message)
async def handle_admin_reply(message: types.Message, bot: Bot):
    """Обработка ответов админа на вопросы пользователей"""
    import logging
    
    replied_message_id = message.reply_to_message.message_id
    
    logging.info(f"Admin replied to message {replied_message_id}")
    
    try:
        original_user_id = await get_user_by_admin_message(replied_message_id)
        
        if not original_user_id:
            logging.warning(f"No user_id found for admin message {replied_message_id}. Ignoring.")
            return
        
        logging.info(f"Found original user: {original_user_id}")
        
        expert_reply = f"💬 <b>Ответ эксперта Advanced Nutrients:</b>\n\n{message.text or message.caption or '(сообщение без текста)'}"
        
        if message.photo:
            photo_id = message.photo[-1].file_id
            await bot.send_photo(
                chat_id=original_user_id,
                photo=photo_id,
                caption=expert_reply,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=original_user_id,
                text=expert_reply,
                parse_mode="HTML"
            )
        
        await message.reply("✅ Ответ отправлен пользователю!")
        logging.info(f"Reply sent to user {original_user_id}")
        
    except Exception as e:
        logging.error(f"Error handling admin reply: {type(e).__name__}: {e}")
        import traceback
        logging.error(traceback.format_exc())