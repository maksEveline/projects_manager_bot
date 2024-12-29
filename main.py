import asyncio
from aiogram import Bot, Dispatcher

from handlers.user import start
from callbacks.user import (
    my_projects,
    add_project,
    cancel_method,
    open_project,
    delete_project,
    add_to_project,
)
from data.database import db
from config import TOKEN


async def main():
    await db.initialize()

    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        start.router,
        my_projects.router,
        add_project.router,
        cancel_method.router,
        open_project.router,
        delete_project.router,
        add_to_project.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
