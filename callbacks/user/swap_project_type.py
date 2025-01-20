from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db

from keyboards.user.user_inline import get_back_to_main_menu, get_back_to_project_menu
from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("switch_to_"))
async def swap_project_type(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    user_projects = await db.get_user_projects(callback.from_user.id)
    fixed_projects = [
        project for project in user_projects if project["project_type"] == "fixed"
    ]
    call_data = callback.data
    project_data = call_data.split("switch_to_")[-1]
    project_id = project_data.split("/")[-1]
    new_type = project_data.split("/")[0]

    if new_type == "fixed":
        if len(fixed_projects) >= user["max_projects"]:
            await bot.edit_message_text(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                text="❌ У вас максимальное количество проектов.\nДокупить проекты можно в профиле.",
                reply_markup=await get_back_to_main_menu(),
            )
            return
        else:
            kb = [
                [
                    InlineKeyboardButton(
                        text="💚 Переключить",
                        callback_data=f"accept_switch_to_fixed/{project_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌Отмена",
                        callback_data="cancel_method",
                    )
                ],
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
            await bot.edit_message_text(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                text="⁉ Вы уверены, что хотите переключить проект на фикс цену?",
                reply_markup=keyboard,
            )
    else:
        kb = [
            [
                InlineKeyboardButton(
                    text="💚 Переключить",
                    callback_data=f"accept_switch_to_percentage/{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌Отмена",
                    callback_data="cancel_method",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text="⁉ Вы уверены, что хотите переключить проект на % от дохода?",
            reply_markup=keyboard,
        )


@router.callback_query(F.data.startswith("accept_switch_to_"))
async def accept_switch_to_project(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    call_data = callback.data
    project_data = call_data.split("accept_switch_to_")[-1]
    project_id = project_data.split("/")[-1]
    new_type = project_data.split("/")[0]

    is_updated = await db.update_project_type(project_id, new_type)
    if is_updated:
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text="✅ Проект успешно переключен",
            reply_markup=await get_back_to_project_menu(project_id),
        )
    else:
        await bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text="❌ Ошибка при переключении проекта",
            reply_markup=await get_back_to_project_menu(project_id),
        )
