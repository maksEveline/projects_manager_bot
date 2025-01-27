from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.user.user_inline import get_cancel_menu
from utils.json_utils import get_fixed_prices, update_project_prices
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


class ChangeProjectPrices(StatesGroup):
    new_price = State()


@router.callback_query(F.data == "change_project_prices")
async def change_project_prices(callback: CallbackQuery, state: FSMContext, bot: Bot):
    fixed_prices = get_fixed_prices()

    kb = []

    for price in fixed_prices:
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{price['count']} проектов - {price['price']} $",
                    callback_data=f"change_count_price_{price['count']}",
                )
            ]
        )

    kb.append([InlineKeyboardButton(text="Отмена", callback_data="cancel_method")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(
        text="Выберите пакет для изменения цены", reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("change_count_price_"))
async def start_change_count_price(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    count = callback.data.split("change_count_price_")[-1]

    await state.set_state(ChangeProjectPrices.new_price)
    await state.update_data({"count": count})

    await bot.edit_message_text(
        text=f"Введите новую цену для {count} проектов",
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=await get_cancel_menu(),
    )


@router.message(ChangeProjectPrices.new_price)
async def change_count_price_process(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    count = data["count"]
    new_price = message.text

    is_updated = update_project_prices(int(count), new_price)

    if is_updated:
        await message.answer("Цена успешно обновлена")
    else:
        await message.answer("Произошла ошибка при обновлении цены")
