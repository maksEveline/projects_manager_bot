from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db
from keyboards.user.user_inline import get_back_to_main_menu
from utils.json_utils import get_fixed_prices

router = Router()


@router.callback_query(F.data == "buy_more_projects")
async def buy_more_projects(callback: CallbackQuery, state: FSMContext, bot: Bot):
    fixed_prices = get_fixed_prices()
    kb = []

    for price in fixed_prices:
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{price['count']} проектов - {price['price']}$",
                    callback_data=f"buy_count_projects_{price['count']}",
                )
            ]
        )

    kb.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(
        "🔢 Выберите количество проектов которые вы хотите приобрести",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("buy_count_projects_"))
async def buy_count_projects(callback: CallbackQuery, state: FSMContext, bot: Bot):
    count = callback.data.split("buy_count_projects_")[-1]
    user = await db.get_user(callback.from_user.id)

    prices = get_fixed_prices()
    price_dollar = None

    for price in prices:
        if price["count"] == int(count):
            price_dollar = price["price"]
            break

    if user["balance"] < price_dollar:
        kb = [
            [
                InlineKeyboardButton(
                    text="💰 Пополнить баланс", callback_data="add_balance"
                )
            ],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        await callback.message.edit_text(
            "💰 У вас недостаточно средств для покупки проектов",
            reply_markup=keyboard,
        )
        return
    else:
        await db.deduct_balance(user["id"], float(price_dollar))
        await db.add_max_projects(user["id"], int(count))

        await callback.message.edit_text(
            f"💰 Вы успешно приобрели {count} проектов",
            reply_markup=await get_back_to_main_menu(),
        )
