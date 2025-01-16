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

router = Router()


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
        text="Напишите ID пользователя, которого хотите изменить",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_cancel_menu(),
    )

    await state.set_state(ChangeUserSubscription.user_id)


@router.message(ChangeUserSubscription.user_id)
async def change_user_subscription_handler(
    message: Message, state: FSMContext, bot: Bot
):
    try:
        data = await state.get_data()
        project_id = data["project_id"]
        user_id = int(message.text)
        await state.update_data({"user_id": user_id})

        user_info = await db.get_user_active_subscriptions(user_id, project_id)

        await state.update_data({"user_info": user_info})
        await state.update_data({"project_id": project_id})

        await bot.delete_message(message.chat.id, message.message_id)

        answ_text = f"Проект: {user_info[0]['project_name']}\n\n"

        kb = []

        for sub in user_info:
            date = format_timestamp(float(sub["date"]))
            answ_text += f"🆔 Номер: {sub['sub_id']}\n"
            answ_text += f"💰 Цена: {sub['price']} $\n"
            answ_text += f"🕒 Длительность: {sub['duration']} {sub['duration_type']}\n"
            answ_text += f"🕒 Дата до когда действует: {date}\n\n"

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
                    text="🔙 Назад", callback_data=f"project_{project_id}"
                )
            ]
        )

        await bot.edit_message_text(
            text=answ_text,
            chat_id=message.chat.id,
            message_id=data["msg_id"],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        )
    except Exception as ex:
        print(ex)
        return


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

            answ_text = f"Текущая подписка: <code>{date}</code>\n\n"
            answ_text += "Напишите новую дату до которой будет действовать подписка в формате как написано выше"

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
