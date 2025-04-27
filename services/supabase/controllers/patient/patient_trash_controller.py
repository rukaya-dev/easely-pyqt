import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.patient.patient_trash_model import PatientTrashModel
from services.supabase.store.trash_store import TrashStore

logger = set_up_logger('main.services.supabase.controllers.patients.trash_controller')


class PatientTrashController:
    store = TrashStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_trash(data):
        res = await PatientTrashModel.create_trash(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'patients_trash',
                "data": json.dumps(data),
                "changed_by": PatientTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await PatientTrashController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'patients_trash',
                "data": json.dumps(data),
                "changed_by": PatientTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await PatientTrashController.log_controller.create_log(log_data)
            return res

    @staticmethod
    async def delete_trash(trash_id):
        res = await PatientTrashModel.delete_trash(trash_id)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=10):
        data = await PatientTrashModel.get_trash_paginate(
            search_data=PatientTrashController.store.get_search_text(),
            filter_preferences=PatientTrashController.store.get_filter_preferences(),
            page_number=page_number, item_per_page=item_per_page)
        if not data:
            PatientTrashController.store.set_data({})
        else:
            PatientTrashController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_trash_by_id(trash_id):
        res = await PatientTrashModel.get_trash_by_id(trash_id)
        if not res:
            PatientTrashController.store.set_trash_record({})
        else:
            PatientTrashController.store.set_trash_record(res)
            return res

    @staticmethod
    @auth_token_middleware
    async def put_back(data):
        res = await PatientTrashModel.put_back(data)
        if not res:
            log_data = {
                "action_type": 'RECOVER',
                "model_name": 'patients_trash',
                "data": json.dumps(data),
                "changed_by": PatientTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await PatientTrashController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'RECOVER',
                "model_name": 'patients_trash',
                "data": json.dumps(data),
                "changed_by": PatientTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await PatientTrashController.delete_trash(data["trash_id"])
            await PatientTrashController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await PatientTrashModel.apply_filter(data)
        return data
