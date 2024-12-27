from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_main_menu_user() -> InlineKeyboardMarkup:
    kb = []

    kb.append(
        [InlineKeyboardButton(text="🧑‍💻 Мои проекты", callback_data=f"my_projects")]
    )

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


async def get_back_to_main_menu() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
