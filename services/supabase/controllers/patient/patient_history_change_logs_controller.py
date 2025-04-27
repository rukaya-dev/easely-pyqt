import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.patient.patient_histroy_change_logs_model import PatientHistoryChangeLogsModel
from services.supabase.store.patient.patient_history_change_logs_store import Store

logger = set_up_logger('main.services.supabase.controllers.patient.patient_history_change_logs_controller')


class PatientHistoryChangeLogsController:
    store = Store()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_history(data):
        res = await PatientHistoryChangeLogsModel.create_history(data=data)
        return res

    @staticmethod
    async def delete_history(history_id):
        res = await PatientHistoryChangeLogsModel.delete_history(history_id)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(patient_id, page_number=1, item_per_page=10):
        data = await PatientHistoryChangeLogsModel.get_paginate(
            patient_id=patient_id,
            search_data=PatientHistoryChangeLogsController.store.get_search_text(),
            filter_preferences=PatientHistoryChangeLogsController.store.get_filter_preferences(),
            page_number=page_number, item_per_page=item_per_page)
        if not data:
            PatientHistoryChangeLogsController.store.set_data({})
        else:
            PatientHistoryChangeLogsController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_history_by_id(history_id):
        res = await PatientHistoryChangeLogsModel.get_history_by_id(history_id)
        if res:
            PatientHistoryChangeLogsController.store.set_history_record(res)
        return res

    @staticmethod
    @auth_token_middleware
    async def revert_history_record(data):
        res = await PatientHistoryChangeLogsModel.revert_history_record(data)
        if not res:
            log_data = {
                "action_type": 'REVERT',
                "model_name": 'patients',
                "data": json.dumps(data),
                "changed_by": PatientHistoryChangeLogsController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await PatientHistoryChangeLogsController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'REVERT',
                "model_name": 'patients',
                "data": json.dumps(data),
                "changed_by": PatientHistoryChangeLogsController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await PatientHistoryChangeLogsController.delete_history(data["change_id"])
            await PatientHistoryChangeLogsController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await PatientHistoryChangeLogsModel.apply_filter(data)
        return data
