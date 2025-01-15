from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_main_menu_user() -> InlineKeyboardMarkup:
    kb = []

    kb.append(
        [InlineKeyboardButton(text="🧑‍💻 Мои проекты", callback_data=f"my_projects")]
    )
    kb.append(
        [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=f"add_balance")]
    )
    kb.append([InlineKeyboardButton(text="ℹ Профиль", callback_data=f"profile")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


async def get_my_projects_menu(projects: list[dict]) -> InlineKeyboardMarkup:
    kb = []

    for project in projects:
        kb.append(
            [
                InlineKeyboardButton(
                    text=project["name"],
                    callback_data=f"project_{project['project_id']}",
                )
            ]
        )

    kb.append(
        [InlineKeyboardButton(text="➕ Добавить проект", callback_data="add_project")]
    )
    kb.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


async def get_back_to_project_menu(project_id: int) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"project_{project_id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


async def get_back_to_main_menu() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


async def get_cancel_menu() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_method")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


async def get_rate_settings_menu(rate_id: int, project_id: int) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="💰 Изменить цену", callback_data=f"change_rate_price_{rate_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔍 Изменить название", callback_data=f"change_rate_name_{rate_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⏱️ Изменить длительность",
                callback_data=f"change_rate_duration_{rate_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Удалить тариф",
                callback_data=f"delete_rate_{rate_id}",
            )
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"rates_{project_id}")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


async def get_profile_menu():
    kb = [
        [InlineKeyboardButton(text="🛍️ Мои покупки", callback_data=f"my_purchases")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


async def get_item_menu(
    item_id: int, project_id: int, type: str
) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="🗑️ Удалить", callback_data=f"del_item_{item_id}/{type}"
            )
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"project_{project_id}")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
