from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


class TransferProject(StatesGroup):
    user_id = State()


@router.callback_query(F.data.startswith("transfer_project_"))
async def transfer_project(callback: CallbackQuery, state: FSMContext, bot: Bot):
    project_id = callback.data.split("transfer_project_")[-1]
    await state.update_data(
        {"project_id": project_id, "msg_id": callback.message.message_id}
    )

    await callback.message.edit_text(
        "Напишите user_id пользователя или <b>username без @</b>, которому вы хотите передать проект",
        reply_markup=await get_cancel_menu(),
        parse_mode="HTML",
    )

    await state.set_state(TransferProject.user_id)


@router.message(TransferProject.user_id)
async def transfer_project_user_id(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    project_id = data["project_id"]
    try:
        user_id = int(message.text)
    except ValueError:
        user_id = await db.get_userid_by_username(message.text.lower())
        if user_id is None:
            await bot.edit_message_text(
                text=f"Пользователь {message.text} не найден",
                chat_id=message.chat.id,
                message_id=data["msg_id"],
            )
            return

    await bot.delete_message(message.chat.id, message.message_id)
    await state.update_data({"user_id": user_id})

    kb = [
        [
            InlineKeyboardButton(
                text="✅ Да, передать",
                callback_data=f"confirm_transfer_project_{project_id}_{user_id}",
            ),
            InlineKeyboardButton(
                text="❌ Нет, отмена",
                callback_data=f"project{project_id}",
            ),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text=f"Вы действительно хотите передать проект пользователю <code>{user_id}</code>?",
        chat_id=message.chat.id,
        message_id=data["msg_id"],
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("confirm_transfer_project_"))
async def confirm_transfer_project(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    data = await state.get_data()
    project_id = data["project_id"]
    user_id = data["user_id"]
    is_updated = await db.update_project_owner(project_id, user_id)
    if is_updated:
        await bot.edit_message_text(
            text=f"Проект передан пользователю <code>{user_id}</code>",
            chat_id=callback.from_user.id,
            message_id=data["msg_id"],
            reply_markup=await get_back_to_main_menu(),
            parse_mode="HTML",
        )
    else:
        await bot.edit_message_text(
            text="Ошибка при передаче проекта",
            chat_id=callback.from_user.id,
            message_id=data["msg_id"],
            reply_markup=await get_back_to_main_menu(),
            parse_mode="HTML",
        )

    await state.clear()
