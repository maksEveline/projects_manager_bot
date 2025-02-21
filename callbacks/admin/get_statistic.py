import os
import csv
from aiogram import F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from data.database import db
from keyboards.admin.admin_inline import get_admin_menu
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


@router.callback_query(F.data == "admin_statistics")
async def get_admin_statistic(callback: CallbackQuery, state: FSMContext, bot: Bot):
    statistic = await db.get_statistic()
    projects_statistics = await db.get_projects_statistics()
    file_path = "admin_statistics.csv"
    with open(file_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Общая статистика"])
        writer.writerow(["Всего пользователей", statistic["total_users"]])
        writer.writerow(["Всего проектов", statistic["total_projects"]])
        writer.writerow(["Активных подписок", statistic["total_active_subscriptions"]])
        writer.writerow(["Общий баланс", f"{statistic['total_balance']:,.2f} $"])
        writer.writerow(["Сумма покупок", f"{statistic['total_purchases']:,.2f} $"])
        writer.writerow(["Заблокировано", statistic["total_blocked_users"]])
        writer.writerow([])
        writer.writerow(["Типы проектов"])
        writer.writerow(["Тип проекта", "Количество"])
        for type_, count in statistic["project_types"].items():
            writer.writerow([type_, count])
        writer.writerow([])
        writer.writerow(["Топ пользователей по балансу"])
        writer.writerow(["Имя", "username", "Баланс"])
        for user in statistic["top_users_by_balance"]:
            writer.writerow([user["first_name"], user["username"], user["balance"]])
        writer.writerow([])
        writer.writerow(["Топ проектов по подписчикам"])
        writer.writerow(["Название проекта", "Подписчиков"])
        for project in statistic["top_projects_by_subscribers"]:
            writer.writerow([project["name"], project["subscribers"]])
        writer.writerow([])
        writer.writerow(["Статистика по проектам"])
        writer.writerow(["Проект", "Клиентов", "Владелец (username)", "Владелец (ID)"])
        for project in projects_statistics:
            writer.writerow(
                [
                    project["project_name"],
                    project["clients_count"],
                    project["owner_username"],
                    project["owner_id"],
                ]
            )
    file = FSInputFile(file_path)
    await bot.send_document(callback.message.chat.id, document=file)
    await bot.send_message(
        callback.from_user.id,
        "Статистика в Excel таблице",
        reply_markup=await get_admin_menu(),
    )
    try:
        os.remove(file_path)
    except Exception as e:
        print(e)
