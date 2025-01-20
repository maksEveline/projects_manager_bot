from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("project_"))
async def open_project(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    project_id = callback.data.split("project_")[-1]
    project = await db.get_project_chats_and_channels(project_id)
    project_info = await db.get_project(project_id)
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    kb = []

    for item in project:
        if item["type"] == "chat":
            kb.append(
                [
                    InlineKeyboardButton(
                        text=f"{item['name']} (Chat)",
                        callback_data=f"item_chat_{item['id']}",
                    )
                ]
            )
        else:
            kb.append(
                [
                    InlineKeyboardButton(
                        text=f"{item['name']} (Channel)",
                        callback_data=f"item_channel_{item['id']}",
                    )
                ]
            )

    kb.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить чат/канал",
                callback_data=f"add_to_project_{project_id}",
            )
        ]
    )
    kb.append(
        [InlineKeyboardButton(text="🔱 Тарифы", callback_data=f"rates_{project_id}")]
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="📊 Статистика проекта",
                callback_data=f"stats_project_{project_id}",
            )
        ]
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="🤥 Изменить подписку пользователя",
                callback_data=f"change_user_subscription_{project_id}",
            ),
            InlineKeyboardButton(
                text=f"✨ Выдать подписку",
                callback_data=f"give_subscription_{project_id}",
            ),
        ],
    )
    kb.append(
        [
            InlineKeyboardButton(
                text="📩 Рассылка", callback_data=f"newsletter_project_{project_id}"
            )
        ]
    )

    if project_info["project_type"] == "fixed":
        kb.append(
            [
                InlineKeyboardButton(
                    text="🔄 Переключить на % от дохода",
                    callback_data=f"switch_to_percent/{project_id}",
                )
            ]
        )
    else:
        kb.append(
            [
                InlineKeyboardButton(
                    text="🔄 Переключить на фикс цену",
                    callback_data=f"switch_to_fixed/{project_id}",
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

    msg_text = f"<b>Название проекта:</b> <code>{project_info['name']}</code>\n\n<b>🌐 Выберите чат или канал</b>\n\n🔗Ссылка на покупку:\n<code>https://t.me/{bot_username}?start=project_{project_id}</code>"
    await bot.edit_message_text(
        text=msg_text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
    )
