import os
import time
import openpyxl
from aiogram import F, Bot
from aiogram.types import CallbackQuery
from aiogram.types.input_file import FSInputFile
from keyboards.user.user_inline import get_back_to_project_menu
from data.database import db
from config import DURATION_TYPES
from utils.routers import create_router_with_user_middleware
from utils.time_utils import format_timestamp

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("stats_project_"))
async def stats_project(callback: CallbackQuery, bot: Bot):
    project_id = callback.data.split("stats_project_")[-1]
    project_info = await db.get_project(project_id)
    project_name = project_info["name"]

    rates = await db.get_rates(project_id)
    active_subscriptions = await db.get_active_subscriptions()
    file_path = "members.xlsx"

    headers = [
        "Участник (имя юзернейм айди)",
        "конец",
        "количество дней осталось",
        "Имя тарифа",
        "цена тарифа",
    ]
    rows = []
    now_ts = time.time()
    unit_map = {
        "день": 1,
        "дня": 1,
        "дней": 1,
        "неделя": 7,
        "недели": 7,
        "недель": 7,
        "месяц": 30,
        "месяца": 30,
        "месяцев": 30,
        "год": 365,
        "года": 365,
        "лет": 365,
    }
    rate_map = {rate["rate_id"]: rate for rate in rates}

    for sub in active_subscriptions:
        if int(sub["project_id"]) != int(project_id):
            continue
        rate_id = sub["rate_id"]
        if rate_id not in rate_map:
            continue

        rate = rate_map[rate_id]
        dur_type = DURATION_TYPES[rate["duration_type"]]
        multiplier = unit_map.get(dur_type.lower(), 1)
        sub_start = float(sub["date"])
        end_ts = float(sub["date"])
        days_left = int((end_ts - now_ts) // 86400)
        username = await db.get_username_by_id(sub["user_id"])
        first_name = await db.get_firstname_by_userid(sub["user_id"])
        participant = f"{first_name} (@{username if username else 'Нет username'}) ID: {sub['user_id']}"

        row = [
            participant,
            format_timestamp(end_ts),
            str(days_left),
            rate["name"],
            str(rate["price"]),
        ]
        rows.append(row)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Участники"
    ws.append([f"Проект: {project_name}"])
    ws.append([])
    ws.append(headers)

    for row in rows:
        ws.append(row)

    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    wb.save(file_path)

    await bot.send_document(
        chat_id=callback.from_user.id,
        document=FSInputFile(file_path),
        caption="Список участников",
    )

    await bot.edit_message_text(
        text="📊 Статистика по доходам проекта",
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=await get_back_to_project_menu(project_id),
        parse_mode="HTML",
    )

    try:
        os.remove(file_path)
    except Exception as e:
        print(e)
