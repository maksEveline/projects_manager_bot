import asyncio
from aiogram import Bot, Dispatcher

from handlers.user import start
from handlers import join_request
from callbacks.user import (
    change_rate_duration,
    change_rate_name,
    change_rate_price,
    my_projects,
    add_project,
    cancel_method,
    open_project,
    open_profile,
    delete_project,
    add_to_project,
    delete_rate,
    open_item,
    open_project_rates,
    open_rate_settings,
    add_rate,
    topup_balance,
    stats_project,
    my_purchases,
    buy_rate,
    del_item,
)
from callbacks.admin import open_admin, ban_user, change_user_balance
from data.database import db
from config import TOKEN
from utils.subscriptions_checker import checker_func


async def main():
    await db.initialize()
    bot = Bot(TOKEN)
    dp = Dispatcher()

    asyncio.create_task(
        checker_func(bot)
    )  # Запуск checker_func в отдельном асинхронном таске

    dp.include_routers(
        start.router,
        my_projects.router,
        add_project.router,
        cancel_method.router,
        open_project.router,
        delete_project.router,
        add_to_project.router,
        join_request.router,
        change_rate_name.router,
        change_rate_price.router,
        change_rate_duration.router,
        open_profile.router,
        open_item.router,
        open_project_rates.router,
        open_rate_settings.router,
        delete_rate.router,
        add_rate.router,
        topup_balance.router,
        stats_project.router,
        my_purchases.router,
        buy_rate.router,
        del_item.router,
        open_admin.router,
        ban_user.router,
        change_user_balance.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
