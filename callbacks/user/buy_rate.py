from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from data.database import db
from keyboards.user.user_inline import get_main_menu_user
from config import DURATION_TYPES

router = Router()


@router.callback_query(F.data.startswith("buy_rate_"))
async def buy_rate(callback: CallbackQuery, bot: Bot):
    rate_id = int(callback.data.split("_")[-1])
    rate = await db.get_rate(rate_id)
    dur_type = DURATION_TYPES[rate["duration_type"]]
    project_chats = await db.get_project_chats_and_channels(rate["project_id"])

    answ_msg = f"🤑 Вы хотите купить <b>{rate['name']}</b> - {rate['duration']} {dur_type}({rate['price']}$)\n\n"
    answ_msg += "🦋 Вы получите доступ в следующих чатах и каналах:\n\n"

    for chat in project_chats:
        answ_msg += f"<b>{chat['name']}</b>({chat['type']})\n"

    kb = [
        [
            InlineKeyboardButton(
                text="✅Покупаю", callback_data=f"confirm_buy_rate_{rate_id}"
            )
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=answ_msg,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("confirm_buy_rate_"))
async def confirm_buy_rate(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    user_info = await db.get_user(user_id)
    rate_id = callback.data.split("confirm_buy_rate_")[-1]
    rate_info = await db.get_rate(rate_id)
    project_info = await db.get_project(rate_info["project_id"])

    if float(user_info["balance"]) < float(rate_info["price"]):
        kb = [
            [
                InlineKeyboardButton(
                    text="💰 Пополнить баланс", callback_data=f"add_balance"
                )
            ]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.send_message(
            text="❌ Недостаточно средств",
            chat_id=callback.message.chat.id,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        return

    await db.deduct_balance(user_id, rate_info["price"])

    await bot.send_message(
        text="✅ Тариф успешно приобретен",
        chat_id=callback.message.chat.id,
        reply_markup=await get_main_menu_user(),
        parse_mode="HTML",
    )
