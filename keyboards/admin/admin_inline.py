from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_admin_menu() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="ban user", callback_data="block_user"),
            InlineKeyboardButton(text="unban user", callback_data="unblock_user"),
        ],
        [
            InlineKeyboardButton(
                text="Изменить баланс", callback_data="change_balance"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Изменить ежемесячный %",
                callback_data="change_monhtly_percentage",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Рассылка",
                callback_data="admin_newsletter",
            ),
        ],
        [
            InlineKeyboardButton(text="Статистика", callback_data="admin_statistics"),
        ],
        [
            InlineKeyboardButton(
                text="Изменить цены на паки проектов",
                callback_data="change_project_prices",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
