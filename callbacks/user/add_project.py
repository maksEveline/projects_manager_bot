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
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu
from config import FIXED_PERCENT

router = Router()


class AddProject(StatesGroup):
    name = State()


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
                    text=f"Этот проект за {FIXED_PERCENT}% от дохода",
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
        kb = [
            [
                InlineKeyboardButton(
                    text="Этот проект за фикс цену", callback_data="add_project_fixed"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Этот проект за {FIXED_PERCENT}% от дохода",
                    callback_data="add_project_percent",
                )
            ],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        await bot.edit_message_text(
            text="💰 Выберите тип проекта",
            reply_markup=keyboard,
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
        )
        return
