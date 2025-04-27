import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.settings.role_model import RoleModel
from services.supabase.store.settings.roles_store import RolesStore

logger = set_up_logger('main.services.supabase.controllers.role_controller')


class RoleController:
    store = RolesStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_role(data):
        res = await RoleModel.create_role(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'roles',
                "data": json.dumps(data),
                "changed_by": RoleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await RoleController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'roles',
                "data": json.dumps(data),
                "changed_by": RoleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await RoleController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def create_role_permissions(data):
        res = await RoleModel.create_role_permissions(data=data)
        return res

    @staticmethod
    @auth_token_middleware
    async def delete_role_permissions(role_id):
        res = await RoleModel.delete_role_permissions(role_id)
        if res:
            return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        data = await RoleModel.get_roles_paginate(page_number, item_per_page)
        if not data:
            RoleController.store.set_data({})
        else:
            RoleController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def check_if_role_exist(role_name):
        try:
            data = await RoleModel.check_if_role_exist(role_name)
            return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_role_by_id(role_id):
        res = await RoleModel.get_role_by_id(role_id)
        if res:
            RoleController.store.set_role(res)
            return res

    @staticmethod
    async def delete_role(role_id):
        role = await RoleController.get_role_by_id(role_id)
        res = await RoleModel.delete_role(role_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'roles',
                "data": json.dumps(role),
                "changed_by": RoleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await RoleController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'roles',
                "data": json.dumps(role),
                "changed_by": RoleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await RoleController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def update_role(role_id, data):
        res = await RoleModel.update_role(role_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'roles',
                "data": json.dumps(data),
                "changed_by": RoleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await RoleController.log_controller.create_log(log_data)
            RoleController.store.set_role({})
        else:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'roles',
                "data": json.dumps(data),
                "changed_by": RoleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',
            }
            await RoleController.log_controller.create_log(log_data)
            RoleController.store.set_role(res)
            return res

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_role_exist(role_id, role_name):
        try:
            res = await RoleModel.check_if_updated_role_exist(role_id, role_name)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_all_permissions():
        res = await RoleModel.get_all_permissions()
        return res
