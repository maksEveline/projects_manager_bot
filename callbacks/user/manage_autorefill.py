from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db
from keyboards.user.user_inline import get_back_to_project_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("enable_auto_refill_"))
async def enable_auto_refill(callback: CallbackQuery, bot: Bot, state: FSMContext):
    project_id = callback.data.split("enable_auto_refill_")[-1]
    is_updated = await db.update_auto_refill(project_id, True)

    if is_updated:
        await bot.edit_message_text(
            text="🔊 Автопродление включено",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )
    else:
        await bot.edit_message_text(
            text="🔴 Не удалось включить автопродление",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )


@router.callback_query(F.data.startswith("disable_auto_refill_"))
async def disable_auto_refill(callback: CallbackQuery, bot: Bot, state: FSMContext):
    project_id = callback.data.split("disable_auto_refill_")[-1]
    is_updated = await db.update_auto_refill(project_id, False)

    if is_updated:
        await bot.edit_message_text(
            text="🔇 Автопродление выключено",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )
    else:
        await bot.edit_message_text(
            text="🔴 Не удалось выключить автопродление",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )
