from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from data.database import db
from keyboards.user.user_inline import get_back_to_project_menu, get_cancel_menu

router = Router()


class ChangeName(StatesGroup):
    waiting_for_name = State()


@router.callback_query(F.data.startswith("change_rate_name_"))
async def change_name(callback: CallbackQuery, bot: Bot, state: FSMContext):
    rate_id = callback.data.split("change_rate_name_")[-1]
    await state.set_state(ChangeName.waiting_for_name)
    await bot.edit_message_text(
        text="Введите новое название тарифа:",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_cancel_menu(),
    )

    await state.update_data({"rate_id": rate_id, "msg_id": callback.message.message_id})


@router.message(ChangeName.waiting_for_name)
async def process_change_name(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    rate_id = data["rate_id"]
    rate = await db.get_rate(rate_id)
    project_id = rate["project_id"]

    await db.update_rate_name(rate_id, message.text)
    await bot.delete_message(message.chat.id, message.message_id)

    await bot.edit_message_text(
        text="✅ Название тарифа успешно изменено",
        chat_id=message.chat.id,
        message_id=data["msg_id"],
        reply_markup=await get_back_to_project_menu(project_id),
    )

    await state.clear()
