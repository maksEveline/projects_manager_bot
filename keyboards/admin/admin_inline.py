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
                text="Изменить цену за проект", callback_data="change_price_per_project"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Изменить ссылку на суппорт",
                callback_data="change_support_link",
            ),
            InlineKeyboardButton(
                text="Изменить ссылку на канал",
                callback_data="change_update_channel_link",
            ),
        ],
        [
            InlineKeyboardButton(text="Сделать бекап", callback_data="make_backup"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
