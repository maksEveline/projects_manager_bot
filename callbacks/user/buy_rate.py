import os

from datetime import datetime
from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.types.input_file import FSInputFile

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.user.user_inline import get_back_to_main_menu, get_cancel_menu

from data.database import db
from utils.json_utils import get_project_percentage
from utils.routers import create_router_with_user_middleware
from utils.time_utils import format_hours, get_timestamp, format_timestamp
from utils.mini_funcs import generate_unique_id

from config import DOWNLOADS_DIR

router = create_router_with_user_middleware()


def reverse_date(date_str: str) -> str:
    date_part, time_part = date_str.split(" ")
    reversed_date = ".".join(date_part.split("-")[::-1])
    return f"{reversed_date} {time_part}"


@router.callback_query(F.data.startswith("buy_rate_"))
async def buy_rate(callback: CallbackQuery, bot: Bot):
    rate_id = int(callback.data.split("_")[-1])
    rate = await db.get_rate(rate_id)
    if rate["duration_type"] == "hours":
        dur_type = format_hours(rate["duration"])
    else:
        dur_type = f"{rate['duration']} дней"
    project_chats = await db.get_project_chats_and_channels(rate["project_id"])

    answ_msg = (
        f"🤑 Вы хотите купить <b>{rate['name']}</b> - {dur_type}({rate['price']}$)\n\n"
    )
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
    project_id = rate_info["project_id"]
    project_info = await db.get_project(project_id)
    project_chats = await db.get_project_chats_and_channels(project_id)

    if project_info["payment_type"] == "cryptobot":
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

        if rate_info["duration_type"] == "hours":
            sub_time = rate_info["duration"]
        elif rate_info["duration_type"] == "days":
            sub_time = rate_info["duration"] * 24

        sub_timestamp = get_timestamp(sub_time)
        formatted_time = format_timestamp(sub_timestamp)

        await db.add_active_subscriptions(
            user_id, rate_info["project_id"], rate_id, sub_timestamp, hourses=sub_time
        )

        dirrty_price = rate_info["price"]
        clean_price = dirrty_price - (dirrty_price * get_project_percentage())

        if project_info["project_type"] == "percentage":
            await db.deduct_balance(
                user_id, dirrty_price
            )  # у пользователя снимаем всю сумму
            await db.update_user_balance(
                project_info["user_id"], clean_price
            )  # владельцу проекта добавляем сумму за вычетом процента
        else:
            await db.deduct_balance(user_id, rate_info["price"])
            await db.update_user_balance(project_info["user_id"], rate_info["price"])

        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.add_user_purchase(user_id, rate_info["project_id"], rate_id, now_time)

        await db.delete_alerts(int(user_id), int(project_id), int(rate_id))

        reversed_date = reverse_date(formatted_time)

        answ_text = (
            f"✅ Тариф успешно приобретен\nПодписка действует до: {reversed_date}\n\n"
        )

        # пробуем разбанить пользователя в чатах и каналах если у него уже была подписка
        for chat in project_chats:
            answ_text += f"<b>{chat['name']}({chat['type']})</b> : {chat['link']}\n"

            try:
                await bot.unban_chat_member(chat["id"], user_id)
                print(f"Пользователь {user_id} разбанен в чате {chat['id']}")
            except Exception as e:
                ...

        await bot.send_message(
            text=answ_text,
            chat_id=callback.message.chat.id,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    else:
        project_requisites = await db.get_payment_requisites(project_id)
        if project_requisites:
            answ_text = "🛍️ Оплатите по реквизитам:\n\n"
            answ_text += f"<b>{project_requisites}</b>\n\n"
            answ_text += "💰 После оплаты нажмите на кнопку ниже"

            kb = [
                [
                    InlineKeyboardButton(
                        text="💰 Оплатил",
                        callback_data=f"paid_request_{rate_id}",
                    )
                ]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=answ_text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

        else:
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text="❌ Реквизиты не найдены",
                reply_markup=await get_back_to_main_menu(),
            )


class PaidRequest(StatesGroup):
    img_proof = State()


@router.callback_query(F.data.startswith("paid_request_"))
async def paid_request(callback: CallbackQuery, state: FSMContext, bot: Bot):
    rate_id = callback.data.split("paid_request_")[-1]
    rate_info = await db.get_rate(rate_id)
    project_id = rate_info["project_id"]
    project_info = await db.get_project(project_id)

    await state.set_state(PaidRequest.img_proof)
    await state.update_data({"rate_id": rate_id, "project_info": project_info})

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="🖼️ Отправьте скриншот оплаты или напишите hash/ссылку перевода",
        reply_markup=await get_cancel_menu(),
    )

    await state.update_data({"msg_id": callback.message.message_id})


@router.message(PaidRequest.img_proof)
async def img_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = message.from_user.id
    rate_id = data["rate_id"]
    project_info = data["project_info"]
    msg_id = data["msg_id"]
    rate_info = await db.get_rate(rate_id)

    if message.photo:
        unique_id = await generate_unique_id()
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        if not os.path.exists(DOWNLOADS_DIR):
            os.makedirs(DOWNLOADS_DIR)
        file_path = os.path.join(DOWNLOADS_DIR, f"{unique_id}.jpg")
        await bot.download_file(file.file_path, file_path)
        await bot.delete_message(message.chat.id, message.message_id)

        await db.add_payment_request(unique_id, user_id, rate_id)

        admin_msg_text = f"Новый запрос на оплату от пользователя {user_id}\n\n"
        admin_msg_text += f"Название проекта: {project_info['name']}\n"
        admin_msg_text += f"Тариф: {rate_info['name']}\n"
        admin_msg_text += f"Цена: {rate_info['price']}$\n"
        admin_msg_text += f"ID запроса: {unique_id}\n"

        kb = [
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить оплату",
                    callback_data=f"confirm_pay_request_{unique_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить оплату",
                    callback_data=f"cancel_pay_request_{unique_id}",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        # отправляем в личку админа
        await bot.send_photo(
            chat_id=project_info["user_id"],
            photo=FSInputFile(file_path),
            caption=admin_msg_text,
            reply_markup=keyboard,
        )

        # отправляем в личку пользователя
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ Ваш запрос на оплату отправлен администратору\nID запроса: <code>{unique_id}</code>\n",
            parse_mode="HTML",
        )

    elif message.text:
        unique_id = await generate_unique_id()
        await bot.delete_message(message.chat.id, message.message_id)

        await db.add_payment_request(unique_id, user_id, rate_id)

        admin_msg_text = f"Новый запрос на оплату от пользователя {user_id}\n\n"
        admin_msg_text += f"Название проекта: {project_info['name']}\n"
        admin_msg_text += f"Тариф: {rate_info['name']}\n"
        admin_msg_text += f"Цена: {rate_info['price']}$\n"
        admin_msg_text += f"ID запроса: {unique_id}\n"
        admin_msg_text += f"Пруф оплаты: {message.text}\n"
        kb = [
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить оплату",
                    callback_data=f"confirm_pay_request_{unique_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить оплату",
                    callback_data=f"cancel_pay_request_{unique_id}",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

        # отправляем в личку владельца проекта
        await bot.send_message(
            chat_id=project_info["user_id"],
            text=admin_msg_text,
            reply_markup=keyboard,
        )

        # отправляем в личку пользователя
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ Ваш запрос на оплату отправлен администратору\nID запроса: <code>{unique_id}</code>\n",
            parse_mode="HTML",
        )
