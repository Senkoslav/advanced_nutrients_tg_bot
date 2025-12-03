from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❓ Задать вопрос эксперту", callback_data="nav_ask_expert")],
        [InlineKeyboardButton(text="📍 Где купить", callback_data="nav_where_buy")],
        [InlineKeyboardButton(text="💼 B2B / Оптовые закупки", callback_data="nav_b2b")],
        [InlineKeyboardButton(text="🔔 Уведомить о запуске", callback_data="nav_notify")],
        [InlineKeyboardButton(text="ℹ️ О бренде Advanced Nutrients", callback_data="nav_about")]
    ])

def system_choice_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌱 Soil (почва)", callback_data="sys_soil")],
        [InlineKeyboardButton(text="🥥 Coco (кокос)", callback_data="sys_coco")],
        [InlineKeyboardButton(text="💧 Hydro (гидропоника)", callback_data="sys_hydro")]
    ])

def phase_choice_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌿 Вега", callback_data="phase_veg")],
        [InlineKeyboardButton(text="🌸 Цветение", callback_data="phase_bloom")],
        [InlineKeyboardButton(text="🌿🌸 Полный цикл", callback_data="phase_full")]
    ])

def confirm_sub_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, уведомлять 🔔", callback_data="sub_yes"),
            InlineKeyboardButton(text="Отмена", callback_data="sub_no")
        ]
    ])