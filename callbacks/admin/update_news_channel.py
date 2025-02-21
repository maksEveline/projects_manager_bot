import os
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.input_file import FSInputFile

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu

from utils.routers import create_router_with_admin_middleware
from utils.json_utils import get_news_channel_id, set_news_channel_id

router = create_router_with_admin_middleware()


class UpdateNewsChannel(StatesGroup):
    new_id = State()


@router.callback_query(F.data == "update_news_channel")
async def update_news_channel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(UpdateNewsChannel.new_id)

    msg_answer = "Введите ID нового канала"
    if get_news_channel_id():
        msg_answer += f"\n\nТекущий ID: {get_news_channel_id()}"

    await bot.send_message(
        chat_id=callback.from_user.id,
        text=msg_answer,
    )


@router.message(UpdateNewsChannel.new_id)
async def update_news_channel_process(message: Message, state: FSMContext, bot: Bot):
    new_id = message.text

    try:
        await bot.send_message(
            chat_id=new_id,
            text="🔔 Канал с уведомлениями",
        )
    except Exception as e:
        await bot.send_message(
            chat_id=message.from_user.id, text="❌ Неверный ID канала"
        )
        return

    set_news_channel_id(new_id)
    await bot.send_message(
        chat_id=message.from_user.id, text="✅ Канал с уведомлениями обновлен"
    )
    await state.clear()
