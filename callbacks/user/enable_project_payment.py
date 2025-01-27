from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
)

from aiogram.fsm.context import FSMContext

from data.database import db

from keyboards.user.user_inline import get_back_to_project_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("enable_payment_requisites_"))
async def enable_payment_requisites(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    project_id = callback.data.split("enable_payment_requisites_")[-1]
    project_requisites = await db.get_payment_requisites(project_id)
    if project_requisites:
        is_updated = await db.update_payment_type(project_id, "custom")
        if is_updated:
            await bot.edit_message_text(
                text="🔄 Способ оплаты успешно обновлен",
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=await get_back_to_project_menu(project_id),
            )
    else:
        await bot.edit_message_text(
            text="🤥 Сначала добавьте реквизиты",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )


@router.callback_query(F.data.startswith("enable_payment_cryptobot_"))
async def enable_payment_cryptobot(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    project_id = callback.data.split("enable_payment_cryptobot_")[-1]
    is_updated = await db.update_payment_type(project_id, "cryptobot")
    if is_updated:
        await bot.edit_message_text(
            text="🔄 Способ оплаты успешно обновлен",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )
    else:
        await bot.edit_message_text(
            text="🤥 Сначала добавьте реквизиты",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_project_menu(project_id),
        )
