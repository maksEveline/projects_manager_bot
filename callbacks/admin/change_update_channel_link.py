from aiogram import F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.user.user_inline import get_cancel_menu

from utils.json_utils import (
    get_price_per_project,
    get_settings,
    set_price_per_project,
    set_update_channel_link,
)
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


class ChangeUpdateChannelLink(StatesGroup):
    new_link = State()


@router.callback_query(F.data == "change_update_channel_link")
async def change_update_channel_link(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    update_channel_link = get_settings()["update_channel_link"]
    await bot.edit_message_text(
        text=f"📋 Текущая ссылка на канал: <b>{update_channel_link}</b>\n\n📋 Напишите новую ссылку на канал",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        parse_mode="HTML",
    )

    await state.set_state(ChangeUpdateChannelLink.new_link)


@router.message(ChangeUpdateChannelLink.new_link)
async def change_update_channel_link_process(
    message: Message, state: FSMContext, bot: Bot
):
    try:
        new_link = message.text
        set_update_channel_link(new_link)
    except ValueError:
        await message.answer("❌ Некорректный ввод. Попробуйте снова.")
        return

    await message.answer("✅ Ссылка на канал успешно изменена.")
    await state.clear()
