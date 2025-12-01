from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from states.user_states import AskExpertState
from keyboards.inline import system_choice_kb, phase_choice_kb
from config import ADMIN_CHAT_ID
from database.core import save_question_mapping, get_user_by_admin_message

router = Router()

# Шаг 1: Старт диалога, выбор системы
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

# Обработчик для Reply-кнопки
@router.message(F.text == "❓ Задать вопрос")
async def reply_ask_expert(message: types.Message, state: FSMContext):
    import logging
    logging.info(f"User {message.from_user.id} started expert dialog via reply button")
    await message.answer(
        "Выберите вашу систему выращивания:",
        reply_markup=system_choice_kb()
    )
    await state.set_state(AskExpertState.choosing_system)
    logging.info(f"State set to choosing_system for user {message.from_user.id}")

# Шаг 2: Выбор фазы
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

# Шаг 3: Запрос текста
@router.callback_query(AskExpertState.choosing_phase, F.data.startswith("phase_"))
async def request_text(callback: types.CallbackQuery, state: FSMContext):
    import logging
    phase_map = {"phase_veg": "Вега", "phase_bloom": "Цветение", "phase_full": "Полный цикл"}
    selected_phase = phase_map.get(callback.data, "Unknown")
    
    logging.info(f"User {callback.from_user.id} selected phase: {selected_phase}")
    await state.update_data(phase=selected_phase)
    
    msg = """
❓ Опишите проблему или вопрос максимально коротко и понятно.
Пример:
• свет слабый — как компенсировать?
• недобор массы на 3 неделе bloom
• нужен подбор на 80×80 coco
• чем заменить Big Bud в данной связке
 
(Вы можете прикрепить фото, если необходимо.)
"""
    await callback.message.answer(msg)
    await state.set_state(AskExpertState.writing_question)
    logging.info(f"State set to writing_question for user {callback.from_user.id}. Waiting for text...")
    await callback.answer()

# Шаг 4: Обработка вопроса и отправка админу
@router.message(AskExpertState.writing_question)
async def process_question(message: types.Message, state: FSMContext, bot: Bot):
    import logging
    
    data = await state.get_data()
    system = data.get("system")
    phase = data.get("phase")
    
    logging.info(f"Processing question from user {message.from_user.id}")
    logging.info(f"System: {system}, Phase: {phase}")
    logging.info(f"Admin chat ID: {ADMIN_CHAT_ID}")
    
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    # Формируем текст для админа
    admin_text = (
        f"🔔 <b>Новый вопрос от пользователя</b> {username}\n"
        f"<b>Система:</b> {system}\n"
        f"<b>Фаза:</b> {phase}\n\n"
        f"<b>Текст вопроса:</b>\n"
    )
    
    # Если текст в сообщении (или подпись к фото)
    question_text = message.text or message.caption or "(Текст отсутствует)"
    admin_text += question_text

    # Отправка админу
    try:
        logging.info(f"Attempting to send message to admin chat {ADMIN_CHAT_ID}")
        
        # Добавляем инструкцию для админа
        admin_text += f"\n\n💬 <i>Чтобы ответить пользователю, просто ответьте (reply) на это сообщение.</i>"
        
        if message.photo:
            # Если есть фото, берем самое качественное (последнее в списке)
            photo_id = message.photo[-1].file_id
            result = await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_id, caption=admin_text, parse_mode="HTML")
            logging.info(f"Photo sent successfully to admin. Message ID: {result.message_id}")
        else:
            result = await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML")
            logging.info(f"Message sent successfully to admin. Message ID: {result.message_id}")
        
        # Сохраняем связь между сообщением админа и user_id в БД
        await save_question_mapping(
            admin_message_id=result.message_id,
            user_id=message.from_user.id
        )
        logging.info(f"Saved mapping in DB: admin_msg_id={result.message_id} -> user_id={message.from_user.id}")
            
        # Подтверждение пользователю
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

# Обработчик ответов от админа
@router.message(F.chat.id == ADMIN_CHAT_ID, F.reply_to_message)
async def handle_admin_reply(message: types.Message, bot: Bot):
    """Обработка ответов админа на вопросы пользователей"""
    import logging
    
    # ID сообщения, на которое ответил админ
    replied_message_id = message.reply_to_message.message_id
    
    logging.info(f"Admin replied to message {replied_message_id}")
    
    try:
        # Получаем user_id из БД
        original_user_id = await get_user_by_admin_message(replied_message_id)
        
        if not original_user_id:
            logging.warning(f"No user_id found for admin message {replied_message_id}")
            await message.reply("⚠️ Не удалось найти пользователя для этого вопроса. Возможно, это не вопрос от пользователя.")
            return
        
        logging.info(f"Found original user: {original_user_id}")
        
        # Формируем ответ для пользователя
        expert_reply = f"💬 <b>Ответ эксперта Advanced Nutrients:</b>\n\n{message.text or message.caption or '(сообщение без текста)'}"
        
        # Отправляем ответ пользователю
        if message.photo:
            # Если админ прикрепил фото
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
        
        # Подтверждение админу
        await message.reply("✅ Ответ отправлен пользователю!")
        logging.info(f"Reply sent to user {original_user_id}")
        
    except Exception as e:
        logging.error(f"Error handling admin reply: {type(e).__name__}: {e}")
        import traceback
        logging.error(traceback.format_exc())
        await message.reply(f"❌ Ошибка при отправке ответа: {e}")