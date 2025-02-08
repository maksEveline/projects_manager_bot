from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from utils.time_utils import format_timestamp, convert_to_timestamp
from data.database import db
from keyboards.user.user_inline import get_back_to_project_menu, get_cancel_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


class ChangeUserSubscription(StatesGroup):
    user_id = State()


@router.callback_query(F.data.startswith("change_user_subscription_"))
async def change_user_subscription(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    project_id = callback.data.split("change_user_subscription_")[-1]
    await state.update_data({"project_id": project_id})
    await state.update_data({"msg_id": callback.message.message_id})

    await bot.edit_message_text(
        text="Напишите user_id пользователя или <b>username без @</b>, которому вы хотите изменить подписку",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_cancel_menu(),
        parse_mode="HTML",
    )

    await state.set_state(ChangeUserSubscription.user_id)


@router.message(ChangeUserSubscription.user_id)
async def change_user_subscription_handler(
    message: Message, state: FSMContext, bot: Bot
):
    try:
        user_id = int(message.text)
    except ValueError:
        user_id = await db.get_userid_by_username(message.text.lower())
        if user_id is None:
            await bot.edit_message_text(
                text=f"Пользователь {message.text} не найден",
                chat_id=message.chat.id,
                message_id=data["msg_id"],
            )
            return

    try:
        all_user_subids = []
        data = await state.get_data()
        project_id = data["project_id"]
        await state.update_data({"user_id": user_id})

        user_info = await db.get_user_active_subscriptions(user_id, project_id)

        await state.update_data({"user_info": user_info})
        await state.update_data({"project_id": project_id})

        rate_id = None
        for sub in user_info:
            if int(sub["project_id"]) == int(project_id):
                rate_id = sub["rate_id"]

        await state.update_data({"rate_id": rate_id})

        await bot.delete_message(message.chat.id, message.message_id)

        answ_text = f"Проект: {user_info[0]['project_name']}\n\n"

        kb = []

        for sub in user_info:
            all_user_subids.append(sub["sub_id"])
            date = format_timestamp(float(sub["date"]))
            answ_text += f"🆔 Номер: {sub['sub_id']}\n"
            answ_text += f"💰 Цена: {sub['price']} $\n"
            answ_text += f"🕒 Длительность: {sub['duration']} {sub['duration_type']}\n"
            answ_text += f"🕒 Подписка действует до: {date}\n\n"

            kb.append(
                [
                    InlineKeyboardButton(
                        text=f"🆔 Номер: {sub['sub_id']}",
                        callback_data=f"change_sub_{sub['sub_id']}",
                    )
                ]
            )

        answ_text += "Выберите подписку, которую хотите изменить"
        kb.append(
            [
                InlineKeyboardButton(
                    text="Исключить пользователя из проекта",
                    callback_data=f"exclude_user_{user_id}",
                )
            ]
        )
        kb.append(
            [
                InlineKeyboardButton(
                    text="🔙 Назад", callback_data=f"project_{project_id}"
                )
            ]
        )

        await state.update_data(
            {"all_user_subids": all_user_subids, "project_id": project_id}
        )

        await bot.edit_message_text(
            text=answ_text,
            chat_id=message.chat.id,
            message_id=data["msg_id"],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        )
    except Exception as ex:
        print(ex)


@router.callback_query(F.data.startswith("exclude_user_"))
async def exclude_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = int(callback.data.split("exclude_user_")[-1])
    data = await state.get_data()
    project_id = data["project_id"]
    all_user_subids = data["all_user_subids"]

    kb = [
        [
            InlineKeyboardButton(
                text="✅ Да, исключить", callback_data=f"yes_exclude_user_{user_id}"
            )
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"project_{project_id}")],
    ]

    await bot.edit_message_text(
        text="⁉️ Вы действительно хотите исключить пользователя?",
        chat_id=callback.message.chat.id,
        message_id=data["msg_id"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


@router.callback_query(F.data.startswith("yes_exclude_user_"))
async def yes_exclude_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = int(callback.data.split("yes_exclude_user_")[-1])
    data = await state.get_data()
    project_id = data["project_id"]
    rate_id = data["rate_id"]
    project_info = await db.get_project(project_id)
    for sub_id in data["all_user_subids"]:
        await db.update_subscription_date_by_id(int(sub_id), "1737008061")

    await db.mark_alert_sent(user_id, project_id, rate_id, "3_days")
    await db.mark_alert_sent(user_id, project_id, rate_id, "1_day")
    await db.mark_alert_sent(user_id, project_id, rate_id, "1_hour")

    await bot.send_message(
        user_id,
        f"<b>Ваша подписка на проект {project_info['name']} закончилась! Благодарим за использование</b>",
        parse_mode="HTML",
    )

    await bot.edit_message_text(
        text="🥳 Пользователь успешно исключен",
        chat_id=callback.message.chat.id,
        message_id=data["msg_id"],
        reply_markup=await get_back_to_project_menu(project_id),
    )


class ChangeSub(StatesGroup):
    new_date = State()


@router.callback_query(F.data.startswith("change_sub_"))
async def change_sub_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    sub_id = int(callback.data.split("change_sub_")[-1])
    user_info = data["user_info"]

    for sub in user_info:
        if sub["sub_id"] == sub_id:
            await state.update_data({"sub_id": sub_id})
            date = format_timestamp(float(sub["date"]))

            answ_text = (
                f"Текущая подписка: <code>{date}</code>\n(кликни для копирования)\n\n"
            )
            answ_text += "Напишите новую дату, до которой будет действовать подписка в формате как написано выше (ГГГГ-ММ-ДД время)"

            await bot.edit_message_text(
                text=answ_text,
                chat_id=callback.message.chat.id,
                message_id=data["msg_id"],
                reply_markup=await get_cancel_menu(),
                parse_mode="HTML",
            )

            break

    await state.set_state(ChangeSub.new_date)


@router.message(ChangeSub.new_date)
async def change_sub_date_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    sub_id = data["sub_id"]
    new_date = message.text

    try:
        parsed_date = datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S")

        is_updated = await db.update_subscription_date(
            sub_id, convert_to_timestamp(str(parsed_date))
        )

        if is_updated:
            await bot.edit_message_text(
                text="Даты успешно обновлены",
                chat_id=message.chat.id,
                message_id=data["msg_id"],
                reply_markup=await get_back_to_project_menu(data["project_id"]),
            )
        else:
            await bot.edit_message_text(
                text="Ошибка при обновлении даты",
                chat_id=message.chat.id,
                message_id=data["msg_id"],
                reply_markup=await get_back_to_project_menu(data["project_id"]),
            )

        await bot.delete_message(message.chat.id, message.message_id)
    except ValueError:
        await bot.delete_message(message.chat.id, message.message_id)
