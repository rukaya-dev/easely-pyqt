import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.report_workshop.option_model import OptionModel
from services.supabase.store.report_workshop.option_store import OptionStore

logger = set_up_logger('main.services.supabase.controllers.report_workshop.option_controller')


class OptionController:
    store = OptionStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_option(data):
        res = await OptionModel.create_option(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'options',
                "data": json.dumps(data),
                "changed_by": OptionController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await OptionController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'options',
                "data": json.dumps(data),
                "changed_by": OptionController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await OptionController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=10):
        data = await OptionModel.get_options_paginate(search_text=OptionController.store.get_search_text(),
                                                      filter_preferences=OptionController.store.get_filter_preferences(),
                                                      page_number=page_number, item_per_page=item_per_page)
        if not data:
            OptionController.store.set_data({})
        else:
            OptionController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def check_if_option_exist(name, category_id):
        data = await OptionModel.check_if_option_exist(name, category_id)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_option_by_id(category_id):
        res = await OptionModel.get_option_by_id(category_id)
        if not res:
            OptionController.store.set_option({})
        else:
            OptionController.store.set_option(res)
            return res

    @staticmethod
    async def delete_option(option_id):
        res = await OptionModel.delete_option(option_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'options',
                "data": json.dumps({"option_id": option_id}),
                "changed_by": OptionController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await OptionController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'options',
                "data": json.dumps({"option_id": option_id}),
                "changed_by": OptionController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await OptionController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def update_option(option_id, data):
        res = await OptionModel.update_option(option_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'options',
                "data": json.dumps(data),
                "changed_by": OptionController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await OptionController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'options',
                "data": json.dumps(data),
                "changed_by": OptionController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await OptionController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_option_exist(option_id, name, category_id):
        res = await OptionModel.check_if_updated_option_exist(option_id, name, category_id)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_options_by_category(category):
        res = await OptionModel.get_options_by_category(category)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_options_by_slugs(options_slugs, category_id):
        res = await OptionModel.get_options_by_slugs(options_slugs, category_id)
        return res
