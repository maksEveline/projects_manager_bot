import os
import openpyxl
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
    file_path = "admin_statistics.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Общая статистика"

    ws.append(["Общая статистика"])
    ws.append(["Всего пользователей", statistic["total_users"]])
    ws.append(["Всего проектов", statistic["total_projects"]])
    ws.append(["Активных подписок", statistic["total_active_subscriptions"]])
    ws.append(["Общий баланс", f"{statistic['total_balance']:,.2f} $"])
    ws.append(["Сумма покупок", f"{statistic['total_purchases']:,.2f} $"])
    ws.append(["Заблокировано", statistic["total_blocked_users"]])
    ws.append([])

    ws.append(["Типы проектов"])
    ws.append(["Тип проекта", "Количество"])
    for type_, count in statistic["project_types"].items():
        ws.append([type_, count])
    ws.append([])

    ws.append(["Топ пользователей по балансу"])
    ws.append(["Имя", "username", "Баланс"])
    for user in statistic["top_users_by_balance"]:
        ws.append([user["first_name"], user["username"], user["balance"]])
    ws.append([])

    ws.append(["Топ проектов по подписчикам"])
    ws.append(["Название проекта", "Подписчиков"])
    for project in statistic["top_projects_by_subscribers"]:
        ws.append([project["name"], project["subscribers"]])
    ws.append([])

    ws.append(["Статистика по проектам"])
    ws.append(["Проект", "Клиентов", "Владелец (username)", "Владелец (ID)"])
    for project in projects_statistics:
        ws.append(
            [
                project["project_name"],
                project["clients_count"],
                project["owner_username"],
                project["owner_id"],
            ]
        )

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
