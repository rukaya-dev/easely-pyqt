import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.report_workshop.category_model import CategoryModel
from services.supabase.store.report_workshop.category_store import CategoryStore

logger = set_up_logger('main.services.supabase.controllers.report_workshop.category_controller')


class CategoryController:
    store = CategoryStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_category(data):
        res = await CategoryModel.create_category(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'categories',
                "data": json.dumps(data),
                "changed_by": CategoryController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await CategoryController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'categories',
                "data": json.dumps(data),
                "changed_by": CategoryController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await CategoryController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        data = await CategoryModel.get_categories_paginate(search_text=CategoryController.store.get_search_text(),
                                                           page_number=page_number, item_per_page=item_per_page)
        if not data:
            CategoryController.store.set_data({})
        else:
            CategoryController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def check_if_category_exist(category_name):
        data = await CategoryModel.check_if_category_exist(category_name)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_category_by_id(category_id):
        res = await CategoryModel.get_category_by_id(category_id)
        if not res:
            CategoryController.store.set_category({})
        else:
            CategoryController.store.set_category(res)
            return res

    @staticmethod
    async def delete_category(category_id):
        res = await CategoryModel.delete_category(category_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'categories',
                "data": json.dumps({"category_id": category_id}),
                "changed_by": CategoryController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await CategoryController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'categories',
                "data": json.dumps({"category_id": category_id}),
                "changed_by": CategoryController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await CategoryController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def update_category(category_id, data):
        res = await CategoryModel.update_category(category_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'categories',
                "data": json.dumps(data),
                "changed_by": CategoryController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await CategoryController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'categories',
                "data": json.dumps(data),
                "changed_by": CategoryController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await CategoryController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_category_exist(category_id, category_name):
        res = await CategoryModel.check_if_updated_category_exist(category_id, category_name)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_all_categories():
        res = await CategoryModel.get_all_categories()
        if not res:
            CategoryController.store.set_data({})
        else:
            CategoryController.store.set_data(res)
            return res
