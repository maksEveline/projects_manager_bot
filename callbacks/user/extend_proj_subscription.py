from aiogram import F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.fsm.context import FSMContext

from data.database import db
from keyboards.user.user_inline import get_back_to_project_menu

from utils.routers import create_router_with_user_middleware
from utils.time_utils import format_timestamp, is_future_time, get_timestamp
from utils.json_utils import get_price_per_project

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("extend_proj_subscription_"))
async def start_extend_proj_subscription(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    user_id = callback.from_user.id
    user_info = await db.get_user(user_id)
    project_id = callback.data.split("extend_proj_subscription_")[-1]
    project_info = await db.get_project(project_id)

    if float(user_info["balance"]) < float(get_price_per_project()):
        await bot.send_message(
            chat_id=user_id,
            text=f"❌ Недостаточно средств на балансе. Вам нужно {get_price_per_project()} $",
            reply_markup=await get_back_to_project_menu(project_id),
        )
        return

    kb = [
        [
            InlineKeyboardButton(
                text="✅ Продолжить",
                callback_data=f"accept_extend_proj_subscription_{project_id}",
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=f"project{project_id}",
            ),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text=f"✅ Подписка будет продлена на 30 дней. Вам нужно {get_price_per_project()} $",
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("accept_extend_proj_subscription_"))
async def accept_extend_proj_subscription(
    callback: CallbackQuery, state: FSMContext, bot: Bot
):
    user_id = callback.from_user.id
    user_info = await db.get_user(user_id)

    project_id = callback.data.split("accept_extend_proj_subscription_")[-1]
    project_info = await db.get_project(project_id)

    end_project_date = project_info["subscription_end_date"]

    end_date_str = format_timestamp(float(end_project_date))
    if is_future_time(end_date_str):
        hourses = 30 * 24
        new_date = float(end_project_date) + (hourses * 3600)
        end_date_str = float(new_date)
    else:
        end_date_str = float(get_timestamp(0))

    await db.update_project_subscription_end_date(project_id, end_date_str)
    await db.update_is_active_project(project_id, True)
    await db.deduct_balance(user_id, float(get_price_per_project()))

    await bot.edit_message_text(
        text="✅ Подписка успешно продлена",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_back_to_project_menu(project_id),
    )
