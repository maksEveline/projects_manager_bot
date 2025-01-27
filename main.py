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
    active_purchases,
    enable_payment_requisites,
    add_payment_requisites,
    change_payment_requisites,
    enable_project_payment,
    accept_payment_request,
    manage_autorefill,
    extend_proj_subscription,
    transfer_project,
)
from callbacks.admin import (
    open_admin,
    ban_user,
    change_user_balance,
    change_monhtly_percentage,
    admin_newsletter,
    change_project_prices,
    get_statistic,
    change_price_per_project,
    change_support_link,
    change_update_channel_link,
)
from data.database import db
from config import TOKEN
from utils.subscriptions_checker import checker_func
from utils.projects_manager import projects_manager_func
from utils.users_subs_checker import users_subs_checker_func


async def main():
    await db.initialize()
    bot = Bot(TOKEN)
    dp = Dispatcher()

    asyncio.create_task(checker_func(bot))
    asyncio.create_task(projects_manager_func(bot))
    asyncio.create_task(users_subs_checker_func(bot))

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
        get_statistic.router,
        active_purchases.router,
        enable_payment_requisites.router,
        add_payment_requisites.router,
        change_payment_requisites.router,
        enable_project_payment.router,
        accept_payment_request.router,
        manage_autorefill.router,
        extend_proj_subscription.router,
        change_price_per_project.router,
        change_support_link.router,
        change_update_channel_link.router,
        transfer_project.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
