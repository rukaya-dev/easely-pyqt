from loggers.logger_configs import set_up_logger
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.settings.user_model import UserModel
from services.supabase.store.settings.users_store import UserStore

logger = set_up_logger('main.services.supabase.controllers.user_controller')


class UserController:
    store = UserStore()

    @staticmethod
    @auth_token_middleware
    async def create_user(data):
        res = await UserModel.create_user(data=data)
        return res

    @staticmethod
    @auth_token_middleware
    async def create_user_permissions(data):
        res = await UserModel.create_user_permissions(data=data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items():
        data = await UserModel.get_users()
        if not data:
            UserController.store.set_data({})
        else:
            UserController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_user_by_id(user_id):
        res = await UserModel.get_user_by_id(user_id)
        if not res:
            UserController.store.set_user({})
        else:
            UserController.store.set_user(res)
            return res

    @staticmethod
    async def delete_user(user_id):
        res = await UserModel.delete_user(user_id)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_user(user_id, data):
        res = await UserModel.update_user(user_id, data)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_password(user_id, password):
        res = await UserModel.update_password(user_id, password)
        return res

    @staticmethod
    @auth_token_middleware
    async def check_if_user_email_exist_on_updating(user_id, email):
        try:
            res = await UserModel.check_if_user_email_exist_on_updating(user_id, email)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)
