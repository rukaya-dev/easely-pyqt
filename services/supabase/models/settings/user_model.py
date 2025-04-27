import bcrypt

from configs.supa_base_configs import supabase, SUPER_ADMIN_EMAIL
from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.user_auth_controller import UserAuthController

logger = set_up_logger('main.services.supabase.models.user_model')


class UserModel:
    super_admin_email = SUPER_ADMIN_EMAIL

    @staticmethod
    async def get_users():
        res = UserAuthController.get_user_profile_data()

        try:
            data = await supabase.rpc("get_users", params={"user_email": UserModel.super_admin_email,
                                                           "user_id": res["user_id"]}).execute()
            for user in data.data:
                if user["email"] == UserModel.super_admin_email:
                    data.data.remove(user)
            return {
                "data": data.data
            }
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return {
                "data": []
            }

    @staticmethod
    async def get_user_by_id(user_id):
        res = UserAuthController.get_user_profile_data()
        try:
            data = await supabase.rpc("get_user", params={"auth_admin_id": res["user_id"],
                                                          "user_id": user_id}).execute()
            if data.data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_user(data):
        try:
            data = await supabase.auth.sign_up(data)
            return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_user_permissions(data):
        try:
            data = await supabase.table('roles_permissions').insert(data).execute()
            if data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_user(user_id):
        res = UserAuthController.get_user_profile_data()
        try:
            await supabase.rpc("delete_user", params={"user_email": UserModel.super_admin_email,
                                                      "user_id": res["user_id"],
                                                      "deleted_id": user_id}).execute()
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_user(user_id, data):
        res = UserAuthController.get_user_profile_data()

        try:
            await supabase.rpc("update_user_info", params={
                "user_id": res["user_id"],
                "update_user_id": user_id,
                "new_email": data["email"],
                "new_raw_user_meta_data": data["options"]["data"]
            }).execute()
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_password(user_id, password):
        # encoding user password
        password_bytes = password.encode('utf-8')

        # generating the salt
        salt = bcrypt.gensalt()

        # Hashing the password
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        hashed_password = hashed_password.decode('utf-8')

        try:
            await supabase.rpc("update_user_password", params={
                "user_id": user_id,
                "new_password": hashed_password,
            }).execute()
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_user_email_exist_on_updating(user_id, email):
        try:
            data = await supabase.table('categories').select('email') \
                .neq('id', user_id). \
                eq('email', email) \
                .execute()

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)
