from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states.user_states import SubscriptionState
from keyboards.inline import confirm_sub_kb
from database.core import add_subscriber, check_subscriber
from filters.chat_filters import NotAdminChatFilter

router = Router()

# Шаг 1: Запрос подтверждения
@router.callback_query(F.data == "nav_notify")
async def start_subscription(callback: types.CallbackQuery, state: FSMContext):
    # Проверяем, подписан ли уже пользователь
    is_subscribed = await check_subscriber(callback.from_user.id)
    
    if is_subscribed:
        already_subscribed_msg = """
✅ Вы уже подписаны на уведомления!

Мы обязательно сообщим вам, когда откроется продажа и будет опубликован каталог Advanced Nutrients в России.
"""
        await callback.message.answer(already_subscribed_msg)
        await callback.answer()
        return
    
    msg = """
📦 Свежая поставка удобрений Advanced Nutrients в России — уже скоро!
 
Хотите получить уведомление с датой запуска, доступностью всей линейки, схемами питания и информацией о фирменном мерче?
 
Подтвердите, чтобы мы добавили вас в список Early Access (раннего доступа).
"""
    await callback.message.answer(msg, reply_markup=confirm_sub_kb())
    await state.set_state(SubscriptionState.confirming)
    await callback.answer()

# Обработчик для Reply-кнопки
@router.message(F.text == "🔔 Уведомления", NotAdminChatFilter())
async def reply_notify(message: types.Message, state: FSMContext):
    # Проверяем, подписан ли уже пользователь
    is_subscribed = await check_subscriber(message.from_user.id)
    
    if is_subscribed:
        already_subscribed_msg = """
✅ Вы уже подписаны на уведомления!

Мы обязательно сообщим вам, когда откроется продажа и будет опубликован каталог Advanced Nutrients в России.
"""
        await message.answer(already_subscribed_msg)
        return
    
    msg = """
📦 Свежая поставка удобрений Advanced Nutrients в России — уже скоро!
 
Хотите получить уведомление с датой запуска, доступностью всей линейки, схемами питания и информацией о фирменном мерче?
 
Подтвердите, чтобы мы добавили вас в список Early Access (раннего доступа).
"""
    await message.answer(msg, reply_markup=confirm_sub_kb())
    await state.set_state(SubscriptionState.confirming)

# Шаг 2: Обработка подтверждения
@router.callback_query(SubscriptionState.confirming)
async def process_decision(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "sub_yes":
        try:
            user = callback.from_user
            await add_subscriber(user_id=user.id, username=user.username)
            
            success_msg = """
Готово! ✅
Вы добавлены в список раннего доступа Advanced Nutrients Russia.
Когда откроется продажа и будет опубликован каталог, вы получите уведомление одним из первых.
"""
            await callback.message.edit_text(success_msg) # Редактируем старое сообщение, убирая кнопки
        except Exception as e:
            await callback.message.answer("Ошибка при сохранении данных. Попробуйте позже.")
            print(f"DB Error: {e}")
            
    elif callback.data == "sub_no":
        await callback.message.edit_text("Отменено.") # Или просто delete()
    
    await state.clear()
    await callback.answer()