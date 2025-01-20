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
    change_user_subscription,
    buy_more_projects,
    add_project_percent,
    add_project_fixed,
    give_subscription,
    newsletter_project,
    swap_project_type,
)
from callbacks.admin import (
    open_admin,
    ban_user,
    change_user_balance,
    change_monhtly_percentage,
    admin_newsletter,
    change_project_prices,
)
from data.database import db
from config import TOKEN
from utils.subscriptions_checker import checker_func


async def main():
    await db.initialize()
    bot = Bot(TOKEN)
    dp = Dispatcher()

    asyncio.create_task(checker_func(bot))

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
        change_user_subscription.router,
        buy_more_projects.router,
        add_project_percent.router,
        add_project_fixed.router,
        change_monhtly_percentage.router,
        give_subscription.router,
        newsletter_project.router,
        admin_newsletter.router,
        change_project_prices.router,
        swap_project_type.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
