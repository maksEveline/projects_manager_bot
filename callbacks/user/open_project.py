from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from data.database import db

router = Router()


@router.callback_query(F.data.startswith("project_"))
async def open_project(callback: CallbackQuery, bot: Bot):
    project_id = callback.data.split("project_")[-1]
    project = await db.get_project_chats_and_channels(project_id)
    print(project)

    kb = []

    for item in project:
        if item["type"] == "chat":
            kb.append(
                [
                    InlineKeyboardButton(
                        text=f"{item['name']} (Chat)",
                        callback_data=f"chat_{item['id']}",
                    )
                ]
            )
        else:

            kb.append(
                [
                    InlineKeyboardButton(
                        text=f"{item['name']} (Channel)",
                        callback_data=f"channel_{item['id']}",
                    )
                ]
            )

    kb.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить", callback_data=f"add_to_project_{project_id}"
            )
        ]
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="🗑️ Удалить проект", callback_data=f"delete_project_{project_id}"
            )
        ]
    )
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="my_projects")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text="🌐 Выберите чат или канал",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
    )
