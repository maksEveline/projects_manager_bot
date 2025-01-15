from aiogram import Router
from middlewares.admin_middleware import AdminMiddleware
from middlewares.user_middleware import UserMiddleware


def create_router_with_admin_middleware() -> Router:
    router = Router()
    admin_middleware = AdminMiddleware()
    router.message.middleware(admin_middleware)
    return router


def create_router_with_user_middleware() -> Router:
    router = Router()
    user_middleware = UserMiddleware()
    router.message.middleware(user_middleware)
    return router
