import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.staff.assistant.assistant_model import AssistantModel
from services.supabase.store.staff.assistants.assistant_store import AssistantStore

logger = set_up_logger('main.services.supabase.controllers.staff..assistant.assistant_controller')


class AssistantController:
    store = AssistantStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_assistant(data):
        res = await AssistantModel.create_assistant(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'assistants',
                "data": json.dumps(data),
                "changed_by": AssistantController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await AssistantController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'CREATE',
            "model_name": 'assistants',
            "data": json.dumps(data),
            "changed_by": AssistantController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await AssistantController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        data = await AssistantModel.get_assistants_paginate(search_data=AssistantController.store.get_search_text(),
                                                            filter_preferences=AssistantController.store.get_filter_preferences(),
                                                            page_number=page_number, item_per_page=item_per_page)

        if not data:
            AssistantController.store.set_data({})
        else:
            AssistantController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_searched_items(search_data):
        data = await AssistantModel.get_searched_items(search_data=search_data, filter_preferences=AssistantController.store.get_filter_preferences())
        return data

    @staticmethod
    @auth_token_middleware
    async def get_assistant_by_id(associate_id):
        data = await AssistantModel.get_assistant_by_id(associate_id)
        if not data:
            AssistantController.store.set_assistant({})
        else:
            AssistantController.store.set_assistant(data)
            return data

    @staticmethod
    async def delete_assistant(associate_id):
        associate = await AssistantController.get_assistant_by_id(associate_id)
        res = await AssistantModel.delete_assistant(associate_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'assistants',
                "data": json.dumps(associate),
                "changed_by": AssistantController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await AssistantController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'DELETE',
            "model_name": 'assistants',
            "data": json.dumps(associate),
            "changed_by": AssistantController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await AssistantController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_assistant(associate_id, data):
        res = await AssistantModel.update_assistant(associate_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'assistants',
                "data": json.dumps(data),
                "changed_by": AssistantController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await AssistantController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'UPDATE',
            "model_name": 'assistants',
            "data": json.dumps(data),
            "changed_by": AssistantController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await AssistantController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await AssistantModel.apply_filter(data)
        return data
