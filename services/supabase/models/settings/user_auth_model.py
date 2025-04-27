import json
import os
import sys
import time
from datetime import datetime

from configs.supa_base_configs import supabase
from database.db_manager import DatabaseManager
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.user_auth_model')


class UserAuthModel:
    app_folder = os.path.join(os.path.dirname(sys.argv[0]), "database/local")
    db_file_path = os.path.join(app_folder, "app.db")
    db_manager = DatabaseManager(db_file_path)

    @staticmethod
    async def login_user(email, password):
        try:
            res = await supabase.auth.sign_in_with_password({"email": email, "password": password})
            if not res:
                logger.error("Invalid login credentials")

            AUTH_USER = {
                'id': res.user.id,
                'email': res.user.email,
                'first_name': res.user.user_metadata['first_name'],
                'last_name': res.user.user_metadata['last_name'],
                'username': res.user.user_metadata['username'],
                'role': res.user.user_metadata['user_role'],
                "image_id": res.user.user_metadata['image_id'],
                'access_token': res.session.access_token,
                'refresh_token': res.session.refresh_token,
                'expires_at': str(datetime.fromtimestamp(res.session.expires_at)),
                'expires_in': res.session.expires_in
            }

            await supabase.auth.set_session(access_token=AUTH_USER['access_token'],
                                            refresh_token=AUTH_USER['refresh_token'])
            return AUTH_USER
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def save_user_credentials(user, role_res):
        json_string = json.dumps(role_res[0])
        try:
            res = UserAuthModel.db_manager.execute("""
                    INSERT INTO user_auth 
                    (id, email, access_token, refresh_token, first_name, last_name, username, role, image_id, expires_at , expires_in ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                user["id"], user["email"], user["access_token"], user["refresh_token"], user["first_name"],
                user["last_name"],
                user["username"], json_string, user["image_id"], user["expires_at"], user["expires_in"],))

            if not res:
                logger.error("Error on saving user credentials to database.")
            return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def update_user_credentials(data):
        try:
            res = UserAuthModel.db_manager.execute("""
                UPDATE user_auth
                SET access_token = ?, refresh_token = ?, expires_at = ?
                WHERE id = ?
            """, (
                data["access_token"], data["refresh_token"], data["expires_at"], data["id"]
            ))
            if res:
                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def logout_user(access_token):
        res = UserAuthModel.db_manager.execute("""
            DELETE FROM user_auth 
            WHERE access_token = ?
        """, (
            access_token
        ))
        if res:
            return res

    @staticmethod
    def is_token_has_been_expired(expires_at):
        current_time = time.time()
        return current_time > expires_at

    @staticmethod
    async def refresh_user_access_token(refresh_token):
        try:
            res = await supabase.auth._refresh_access_token(refresh_token)
            if not res:
                logger.error("Error on refreshing access_token")

            return {
                "id": res.user.id,
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token,
                "expires_at": str(datetime.fromtimestamp(res.session.expires_at))
            }
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def get_user_tokens_and_expire_at():
        try:
            result = UserAuthModel.db_manager.execute_select("""
                        SELECT access_token, refresh_token, expires_at FROM user_auth;
                   """, )

            if not result or not all(result[0]):
                logger.error("Error on fetching user access_token, refresh_token and expires_at from database.")

            if result:
                access_token = result[0][0]
                refresh_token = result[0][1]
                expires_at = result[0][2]
                date_format = "%Y-%m-%d %H:%M:%S"
                dt = datetime.strptime(expires_at, date_format)
                expires_at_timestamp = dt.timestamp()

                return {"access_token": access_token, "expires_at": expires_at_timestamp,
                        "refresh_token": refresh_token}
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def get_user_profile_data():
        try:
            result = UserAuthModel.db_manager.execute_select("""
                        SELECT id, email, first_name, last_name, username, role, image_id FROM user_auth;
                   """, )

            user = [{"user_id": user_id, "email": email, "first_name": first_name, "last_name": last_name,
                     "username": username, "role": role,
                     "image_id": image_id} for
                    user_id, email, first_name, last_name, username, role, image_id in result]
            return user[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def check_if_user_exist():
        try:
            check_user = UserAuthModel.db_manager.table_exists("user_auth")
            if not check_user:
                logger.error("Database Error: Table user_auth was not found, contact your service provider.")

            res = UserAuthModel.db_manager.check_if_row_exists("""
                            SELECT EXISTS(SELECT 1 FROM user_auth LIMIT 1);
                       """, )
            if res:
                return res

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def get_user_access_token():
        result = UserAuthModel.db_manager.execute_select("""
                    SELECT access_token FROM user_auth;
               """, )
        if result:
            return result[0][0]
        else:
            return None

    @staticmethod
    def refresh_user_session():
        res = supabase.auth.refresh_session()
        return res

    @staticmethod
    async def sign_out_user():
        try:
            await supabase.auth.sign_out()
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def delete_auth_user_from_db():
        try:
            UserAuthModel.db_manager.execute("""
                  DELETE FROM user_auth;
                   """, )

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def set_user_auth_session(access_token, refresh_token):
        await supabase.auth.set_session(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def send_password_reset(email):
        try:
            res = await supabase.auth.exchange_code_for_session(email)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)
