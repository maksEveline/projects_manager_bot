from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data.database import db
from keyboards.user.user_inline import get_cancel_menu

from utils.json_utils import get_project_percentage, set_project_percentage
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


class ChangeMonthlyPercentage(StatesGroup):
    new_percentage = State()


@router.callback_query(F.data == "change_monhtly_percentage")
async def change_monhtly_percentage(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    monthly_percentage = get_project_percentage()
    await bot.edit_message_text(
        text=f"📋 Текущий ежемесячный %: <b>{monthly_percentage * 100}</b>\n\n📋 Напишите новый ежемесячный %",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        parse_mode="HTML",
    )

    await state.set_state(ChangeMonthlyPercentage.new_percentage)


@router.message(ChangeMonthlyPercentage.new_percentage)
async def change_monthly_percentage_process(
    message: Message, state: FSMContext, bot: Bot
):
    try:
        new_percentage = int(message.text)
        set_project_percentage(new_percentage / 100)
    except ValueError:
        await message.answer("❌ Некорректный ввод. Попробуйте снова.")
        return

    await message.answer("✅ Ежемесячный % успешно изменен.")
    await state.clear()
