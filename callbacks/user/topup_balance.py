from AsyncPayments.cryptoBot import AsyncCryptoBot

from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data.database import db
from keyboards.user.user_inline import get_cancel_menu, get_back_to_main_menu
from utils.crypto_utils import convert_usdt_to_crypto

from config import CRYPTOBOT_TOKEN

router = Router()


def add_commission(num):
    return num + (num * 0.03)


class TopupBalance(StatesGroup):
    sum = State()
    crypto = State()
    confirm = State()


@router.callback_query(F.data == "add_balance")
async def start_topup_balance(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data({"msg_id": callback.message.message_id})

    await bot.edit_message_text(
        text="📋 Напишите сумму пополнения в $",
        reply_markup=await get_cancel_menu(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

    await state.set_state(TopupBalance.sum)


@router.message(TopupBalance.sum)
async def topup_balance_process_sum(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("msg_id")

    try:
        sum = float(message.text)
        await state.update_data({"sum": sum})

        kb = [
            [InlineKeyboardButton(text="USDT", callback_data="USDT")],
            [InlineKeyboardButton(text="ETH", callback_data="ETH")],
            [InlineKeyboardButton(text="LTC", callback_data="LTC")],
            [InlineKeyboardButton(text="BTC", callback_data="BTC")],
            [InlineKeyboardButton(text="BNB", callback_data="BNB")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_method")],
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        await bot.delete_message(
            chat_id=message.from_user.id, message_id=message.message_id
        )

        await bot.edit_message_text(
            text="Выберите криптовалюту",
            reply_markup=keyboard,
            chat_id=message.from_user.id,
            message_id=msg_id,
        )

        await state.set_state(TopupBalance.crypto)
    except Exception as e:
        print(e)
        await bot.delete_message(
            chat_id=message.from_user.id, message_id=message.message_id
        )
        await bot.edit_message_text(
            text="❌ Введите корректное число\n\n📋 Напишите сумму пополнения в $",
            reply_markup=await get_cancel_menu(),
            chat_id=message.from_user.id,
            message_id=msg_id,
        )


@router.callback_query(TopupBalance.crypto)
async def topup_balance_process_crypto(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    data = await state.get_data()
    msg_id = data.get("msg_id")
    sum = data.get("sum")

    try:
        crypto = callback.data
        await state.update_data({"crypto": crypto})

        final_sum = add_commission(sum)

        cryptoBot = AsyncCryptoBot(CRYPTOBOT_TOKEN)
        order_crypto_bot = await cryptoBot.create_invoice(
            convert_usdt_to_crypto(final_sum, crypto),
            currency_type="crypto",
            asset=crypto,
        )
        await state.update_data({"invoice_id": order_crypto_bot.invoice_id})

        payment_kb = [
            [
                InlineKeyboardButton(
                    text="🔗 Перейти к оплате",
                    url=order_crypto_bot.pay_url,
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Я оплатил",
                    callback_data="confirm_topup_balance",
                )
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_method")],
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=payment_kb)

        await bot.edit_message_text(
            text=f"Сумма к оплате: {add_commission(sum)}$",
            reply_markup=keyboard,
            chat_id=callback.from_user.id,
            message_id=msg_id,
        )

        await state.set_state(TopupBalance.confirm)

    except ValueError:
        await bot.delete_message(
            chat_id=callback.from_user.id, message_id=callback.message.message_id
        )
        await bot.edit_message_text(
            text="❌ Введите корректное число\n\n📋 Напишите сумму пополнения в $",
            reply_markup=await get_cancel_menu(),
            chat_id=callback.from_user.id,
            message_id=msg_id,
        )


@router.callback_query(F.data == "confirm_topup_balance")
async def confirm_topup_balance(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    invoice_id = data.get("invoice_id")

    cryptoBot = AsyncCryptoBot(CRYPTOBOT_TOKEN)

    info_crypto_bot = await cryptoBot.get_invoices(invoice_ids=[invoice_id], count=1)
    status = info_crypto_bot[0].status

    if status == "paid":
        await db.update_user_balance(
            user_id=callback.from_user.id, amount=float(data.get("sum"))
        )
        await bot.edit_message_text(
            text="✅ Платеж успешно прошел",
            reply_markup=await get_back_to_main_menu(),
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
        )
        await state.clear()
    else:
        await bot.edit_message_text(
            text="❌ Платеж не прошел\nОплатите и повторно нажмите на кнопку",
            reply_markup=await get_back_to_main_menu(),
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
        )
