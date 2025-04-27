import jwt
from services.supabase.models.settings.role_model import RoleModel
from signals import SignalRepositorySingleton
from services.supabase.models.settings.user_auth_model import UserAuthModel
from loggers.logger_configs import set_up_logger
from services.supabase.store.settings.user_auth_store import UserAuthStore

logger = set_up_logger('main.services.supabase.controllers.user_auth_controller')
signals = SignalRepositorySingleton.instance()


class UserAuthController:
    user_auth_store = UserAuthStore()

    @staticmethod
    async def login_user(email, password):
        res = await UserAuthModel.login_user(email, password)
        if not res:
            return {"message": "Invalid login Credentials", "status_code": 400}

        role_res = await RoleModel.get_role_by_name(res["role"])

        saving_user = UserAuthModel.save_user_credentials(res, role_res)
        if not saving_user:
            return {"message": "Something went wrong", "status_code": 500}

        return {"message": "Successful login", "status_code": 200}

    @staticmethod
    async def sign_out_user():
        try:
            await UserAuthModel.sign_out_user()
            UserAuthController.delete_auth_user_from_db()
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def check_if_user_exist():
        try:
            res = UserAuthModel.check_if_user_exist()
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_user_token():
        if not UserAuthController.user_auth_store.get_is_authenticated():
            res = UserAuthController.get_user_tokens_and_expire_at()
            if not res:
                # delete user from a database and redirect to log in
                UserAuthModel.delete_auth_user_from_db()
                SignalRepositorySingleton.instance().signalForUserAuthLayout.emit(True)
                return None

            is_token_valid = UserAuthController.is_jwt_token_valid(res["access_token"])
            if not is_token_valid:
                UserAuthModel.delete_auth_user_from_db()
                SignalRepositorySingleton.instance().signalForUserAuthLayout.emit(True)
                return None

            # If the token is expired, attempt to refresh it
            if UserAuthModel.is_token_has_been_expired(res["expires_at"]):
                # refresh the token
                data = await UserAuthModel.refresh_user_access_token(res["refresh_token"])
                if not data:
                    UserAuthModel.delete_auth_user_from_db()
                    SignalRepositorySingleton.instance().signalForUserAuthLayout.emit(True)
                    return None

                # Attempt to update the user token with the new data
                user_updated = UserAuthController.update_user_credentials(data=data)
                if not user_updated:
                    UserAuthModel.delete_auth_user_from_db()
                    SignalRepositorySingleton.instance().signalForUserAuthLayout.emit(True)
                    return None
                await UserAuthModel.set_user_auth_session(data["access_token"], data["refresh_token"])
                return True
            else:
                await UserAuthModel.set_user_auth_session(res["access_token"], res["refresh_token"])
                UserAuthController.user_auth_store.set_is_authenticated(True)

        return True

    @staticmethod
    def get_user_tokens_and_expire_at():
        res = UserAuthModel.get_user_tokens_and_expire_at()
        if not res:
            return None
        return res

    @staticmethod
    def get_user_profile_data():
        res = UserAuthModel.get_user_profile_data()
        if res:
            UserAuthController.user_auth_store.set_user(res)
            return res

    @staticmethod
    def update_user_credentials(data):
        res = UserAuthModel.update_user_credentials(data)
        return res

    @staticmethod
    def refresh_user_session():
        res = UserAuthModel.refresh_user_session()
        return res

    @staticmethod
    def logout_user_token(access_token):
        UserAuthModel.logout_user(access_token)

    @staticmethod
    def get_user_access_token():
        res = UserAuthModel.get_user_access_token()
        return res

    @staticmethod
    def delete_auth_user_from_db():
        res = UserAuthModel.delete_auth_user_from_db()
        return res

    @staticmethod
    def is_jwt_token_valid(token):
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            if payload:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def send_password_reset(email):
        res = await UserAuthModel.send_password_reset(email)
        return res
