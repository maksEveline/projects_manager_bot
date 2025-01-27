from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db
from keyboards.user.user_inline import get_back_to_main_menu
from utils.json_utils import get_fixed_prices
from utils.time_utils import get_timestamp

from utils.messages_utils import send_admins_message
from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


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

    kb = [
        [
            InlineKeyboardButton(
                text="✅Покупаю", callback_data=f"confirm_buy_count_projects_{count}"
            )
        ]
    ]
    kb.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    prices = get_fixed_prices()
    price_dollar = None

    for price in prices:
        if price["count"] == int(count):
            price_dollar = price["price"]
            break

    await callback.message.edit_text(
        f"🤑 Вы хотите купить <b>{count}</b> проектов - {price_dollar}$",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("confirm_buy_count_projects_"))
async def confirm_buy_count_projects(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    count = callback.data.split("confirm_buy_count_projects_")[-1]
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
        sub_time = 30 * 24
        timestamp = get_timestamp(sub_time)

        await db.add_buyed_project(user["user_id"], int(count), timestamp)

        await db.deduct_balance(user["user_id"], float(price_dollar))
        await db.add_max_projects(user["user_id"], int(count))

        await send_admins_message(
            bot, f"Пользователь <code>{user['user_id']}</code> купил {count} проектов"
        )

        await callback.message.edit_text(
            f"💰 Вы успешно приобрели {count} проектов",
            reply_markup=await get_back_to_main_menu(),
        )
