import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.billing.billing_model import BillingModel
from services.supabase.store.billing.billing_store import BillingStore

logger = set_up_logger('main.services.supabase.controllers.billing.billing_controller')


class BillingController:
    store = BillingStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def finish_billing(billing_data, patient_data):
        try:
            res = await BillingModel.create_billing(data=billing_data)
            patient_data.update(billing_data)

            if not res:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'billings',
                    "data": json.dumps(patient_data),
                    "changed_by": BillingController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await BillingController.log_controller.create_log(log_data)
            else:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'billings',
                    "data": json.dumps(patient_data),
                    "changed_by": BillingController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await BillingController.log_controller.create_log(log_data)
                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        try:
            data = await BillingModel.get_billings_paginate(search_text=BillingController.store.get_search_text(),
                                                            filter_preferences=BillingController.store.get_filter_preferences(),
                                                            page_number=page_number, item_per_page=item_per_page)

            if not data:
                BillingController.store.set_data({})
            else:
                BillingController.store.set_data(data)
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def check_if_billing_exist(data):
        data = await BillingModel.check_if_billing_exist(data)
        return data

    @staticmethod
    async def delete_billing(billing_id):
        try:
            res = await BillingModel.delete_billing(
                billing_id)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def update_billing(billing_id, data, patient_data):
        try:
            res = await BillingModel.update_billing(
                billing_id, data)

            log_data = {
                "patient_name": patient_data["patient_name"],
                "patient_national_id_number": patient_data["patient_national_id_number"],
                "billing_date": patient_data["billing_date"],
                "doctor_name": patient_data["doctor_name"],
                "service_name": patient_data["service_name"],
                "service_duration": patient_data["service_duration"]
            }
            if not res:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'billings',
                    "data": json.dumps(log_data),
                    "changed_by": BillingController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await BillingController.log_controller.create_log(log)
            else:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'billings',
                    "data": json.dumps(log_data),
                    "changed_by": BillingController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await BillingController.log_controller.create_log(log)

                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_billing_exist(billing_id, billing_date, billing_time):
        data = await BillingModel.check_if_updated_billing_exist(billing_id, billing_date,
                                                                 billing_time)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_billing_by_id(billing_id):
        try:
            res = await BillingModel.get_billing_by_id(billing_id)
            if res:
                BillingController.store.set_billing(res)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_all_billings_by_year(year):
        try:
            res = await BillingModel.get_all_billings_by_year(year)
            if res:
                BillingController.store.set_billing(res)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)
