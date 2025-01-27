from aiogram import F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.user.user_inline import get_cancel_menu

from utils.json_utils import get_price_per_project, set_price_per_project
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


class ChangePricePerProject(StatesGroup):
    new_price = State()


@router.callback_query(F.data == "change_price_per_project")
async def change_price_per_project(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    price_per_project = get_price_per_project()
    await bot.edit_message_text(
        text=f"📋 Текущая цена за проект: <b>{price_per_project}</b>\n\n📋 Напишите новую цену за проект",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        parse_mode="HTML",
    )

    await state.set_state(ChangePricePerProject.new_price)


@router.message(ChangePricePerProject.new_price)
async def change_price_per_project_process(
    message: Message, state: FSMContext, bot: Bot
):
    try:
        new_price = int(message.text)
        set_price_per_project(new_price)
    except ValueError:
        await message.answer("❌ Некорректный ввод. Попробуйте снова.")
        return

    await message.answer("✅ Цена за проект успешно изменена.")
    await state.clear()
