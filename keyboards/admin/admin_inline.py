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
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
