import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.report_workshop.template_model import TemplateModel
from services.supabase.store.report_workshop.template_store import TemplateStore

logger = set_up_logger('main.services.supabase.controllers.report_workshop.template_controller')


class TemplateController:
    store = TemplateStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_template(data):
        res = await TemplateModel.create_template(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'templates',
                "data": json.dumps(data),
                "changed_by": TemplateController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await TemplateController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'templates',
                "data": json.dumps(data),
                "changed_by": TemplateController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await TemplateController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=10):
        data = await TemplateModel.get_templates_paginate(search_text=TemplateController.store.get_search_text(),
                                                          filter_preferences=TemplateController.store.get_filter_preferences(),
                                                          page_number=page_number, item_per_page=item_per_page)
        if not data:
            TemplateController.store.set_data({})
        else:
            TemplateController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def check_if_template_exist(data):
        data = await TemplateModel.check_if_template_exist(data)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_template_by_id(template_id):
        res = await TemplateModel.get_template_by_id(template_id)
        if not res:
            TemplateController.store.set_template({})
        else:
            TemplateController.store.set_template(res)
            return res

    @staticmethod
    @auth_token_middleware
    async def get_template_by_name(name):
        res = await TemplateModel.get_template_by_name(name)
        if not res:
            TemplateController.store.set_template({})
        else:
            TemplateController.store.set_template(res)
            return res

    @staticmethod
    async def delete_template(template_id):
        res = await TemplateModel.delete_template(template_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'templates',
                "data": json.dumps({"template_id": template_id}),
                "changed_by": TemplateController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await TemplateController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'templates',
                "data": json.dumps({"template_id": template_id}),
                "changed_by": TemplateController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await TemplateController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def update_template(template_id, data):
        res = await TemplateModel.update_template(template_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'templates',
                "data": json.dumps(data),
                "changed_by": TemplateController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await TemplateController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'templates',
                "data": json.dumps(data),
                "changed_by": TemplateController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await TemplateController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_template_exist(template_id, data):
        res = await TemplateModel.check_if_updated_template_exist(template_id, data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_all_templates_by_category(category_id):
        res = await TemplateModel.get_all_templates_by_category(category_id)
        if not res:
            TemplateController.store.set_template({})
        else:
            TemplateController.store.set_template(res)
            return res
