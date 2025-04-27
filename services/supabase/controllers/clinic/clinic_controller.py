import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.clinic.clinic_model import ClinicModel
from services.supabase.store.clinic.clinic_store import ClinicStore

logger = set_up_logger('main.services.supabase.controllers.clinic.clinic_controller')


class ClinicController:
    store = ClinicStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_clinic(data):
        try:
            res = await ClinicModel.create_clinic(data=data)

            if not res:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'clinics',
                    "data": json.dumps(data),
                    "changed_by": ClinicController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await ClinicController.log_controller.create_log(log_data)
            else:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'clinics',
                    "data": json.dumps(data),
                    "changed_by": ClinicController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await ClinicController.log_controller.create_log(log_data)
                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_data():
        data = await ClinicModel.get_data()

        if not data:
            ClinicController.store.set_data({})
        else:
            ClinicController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def update_clinic(data):
        try:
            res = await ClinicModel.update_clinic(data)

            return res
        except Exception as e:
            logger.error(e, exc_info=True)
