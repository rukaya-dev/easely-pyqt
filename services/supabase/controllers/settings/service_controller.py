import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.settings.service_model import ServiceModel
from services.supabase.store.appointment.service_store import ServiceStore

logger = set_up_logger('main.services.supabase.controllers.appointment.service_controller')


class ServiceController:
    store = ServiceStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_service(data):
        res = await ServiceModel.create_service(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'services',
                "data": json.dumps(data),
                "changed_by": ServiceController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ServiceController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'services',
                "data": json.dumps(data),
                "changed_by": ServiceController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await ServiceController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        data = await ServiceModel.get_services_paginate(search_data=ServiceController.store.get_search_text(),
                                                        filter_preferences=ServiceController.store.get_filter_preferences(),
                                                        page_number=page_number, item_per_page=item_per_page)
        if not data:
            ServiceController.store.set_data([])
        else:
            ServiceController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def check_if_service_exist(service_name):
        res = await ServiceModel.check_if_service_exist(service_name)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_service_by_id(service_id):
        res = await ServiceModel.get_service_by_id(service_id)
        if res:
            ServiceController.store.set_service(res)
        return res

    @staticmethod
    async def delete_service(service_id):
        service = await ServiceController.get_service_by_id(service_id)
        res = await ServiceModel.delete_service(service_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'services',
                "data": json.dumps(service),
                "changed_by": ServiceController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ServiceController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'services',
                "data": json.dumps(service),
                "changed_by": ServiceController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await ServiceController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def update_service(service_id, data):
        res = await ServiceModel.update_service(service_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'services',
                "data": json.dumps(data),
                "changed_by": ServiceController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ServiceController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'services',
                "data": json.dumps(data),
                "changed_by": ServiceController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await ServiceController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_service_exist(service_id, name):
        res = await ServiceModel.check_if_updated_service_exist(service_id, name)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_all_services():
        data = await ServiceModel.get_all_services()
        if not data:
            ServiceController.store.set_data({})
        else:
            ServiceController.store.set_data(data)
            return data
