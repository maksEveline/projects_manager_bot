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


class ChangePrice(StatesGroup):
    waiting_for_price = State()


@router.callback_query(F.data.startswith("change_rate_price_"))
async def change_price(callback: CallbackQuery, bot: Bot, state: FSMContext):
    rate_id = callback.data.split("change_rate_price_")[-1]
    await state.set_state(ChangePrice.waiting_for_price)
    await bot.edit_message_text(
        text="Введите новую цену тарифа:",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_cancel_menu(),
    )

    await state.update_data({"rate_id": rate_id, "msg_id": callback.message.message_id})


@router.message(ChangePrice.waiting_for_price)
async def process_change_price(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    rate_id = data["rate_id"]
    rate = await db.get_rate(rate_id)
    project_id = rate["project_id"]

    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError

        await db.update_rate_price(rate_id, price)
        await bot.delete_message(message.chat.id, message.message_id)

        await bot.edit_message_text(
            text="✅ Цена проекта успешно изменена",
            chat_id=message.chat.id,
            message_id=data["msg_id"],
            reply_markup=await get_back_to_project_menu(project_id),
        )

        await state.clear()

    except ValueError:
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.edit_message_text(
            text="❌ Пожалуйста, введите положительное число",
            chat_id=message.chat.id,
            message_id=data["msg_id"],
            reply_markup=await get_cancel_menu(),
        )
