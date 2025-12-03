from aiogram import Router, F, types
from filters.chat_filters import NotAdminChatFilter

router = Router()

WHERE_BUY_TEXT = """
📍 <b>Где купить</b>

Официальные витрины Advanced Nutrients Russia:

🌿 <a href="https://growerline.ru/advanced-nutrients/?utm_source=an_bot&utm_medium=telegram&utm_campaign=where_to_buy">Growerline.ru</a>

🌿 <a href="https://focusgrow.ru/catalog/udobreniya-i-stimulyatory/advanced-nutrients/?utm_source=an_bot&utm_medium=telegram&utm_campaign=where_to_buy">Focusgrow.ru</a>

🛒 <a href="https://www.ozon.ru/seller/growerline-1034504/brand/advanced-nutrients-86293441/?miniapp=seller_1034504&utm_source=an_bot&utm_medium=telegram&utm_campaign=where_to_buy">OZON</a>

🛒 <a href="https://market.yandex.ru/search?seriesId=107723&utm_source=an_bot&utm_medium=telegram&utm_campaign=where_to_buy">Yandex Market</a>

💬 <b>Фирменный магазин в Telegram</b> — скоро открытие

<i>Все ссылки откроются в браузере</i>
"""

@router.callback_query(F.data == "nav_where_buy")
async def show_where_buy(callback: types.CallbackQuery):
    await callback.message.answer(WHERE_BUY_TEXT, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()

@router.message(F.text == "📍 Где купить", NotAdminChatFilter())
async def reply_where_buy(message: types.Message):
    await message.answer(WHERE_BUY_TEXT, parse_mode="HTML", disable_web_page_preview=True)
