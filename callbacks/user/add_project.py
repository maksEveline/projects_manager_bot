from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.database import db
from keyboards.user.user_inline import get_cancel_menu
from utils.json_utils import get_project_percentage

from callbacks.user.add_project_fixed import AddProjectFixed

router = Router()


@router.callback_query(F.data == "add_project")
async def add_project(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user = await db.get_user(callback.from_user.id)
    user_projects = await db.get_user_projects(callback.from_user.id)
    fixed_projects = [
        project for project in user_projects if project["project_type"] == "fixed"
    ]

    if len(fixed_projects) >= user["max_projects"]:
        kb = [
            [
                InlineKeyboardButton(
                    text="➕ Докупить проекты", callback_data="buy_more_projects"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Этот проект за {int(get_project_percentage() * 100)}% от дохода",
                    callback_data="add_project_percent",
                )
            ],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        await bot.edit_message_text(
            text="❌ У вас максимальное количество проектов",
            reply_markup=keyboard,
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
        )
        return
    else:
        msg = await bot.edit_message_text(
            text="📋 Напишите название проекта",
            reply_markup=await get_cancel_menu(),
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
        )

        await state.update_data({"msg_id": msg.message_id})

        await state.set_state(AddProjectFixed.name)
