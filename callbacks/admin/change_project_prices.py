from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.json_utils import get_fixed_prices
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
            InlineKeyboardButton(
                text=f"{price['count']} проектов - {price['price']} $",
                callback_data=f"change_count_price_{price['count']}",
            )
        )

    kb.append(InlineKeyboardButton(text="Отмена", callback_data="cancel_method"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(
        text="Выберите пакет для изменения цены", reply_markup=keyboard
    )
