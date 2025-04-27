import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.report.report_trash_model import ReportTrashModel
from services.supabase.store.trash_store import TrashStore

logger = set_up_logger('main.services.supabase.controllers.reports.trash_controller')


class ReportTrashController:
    store = TrashStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_trash(data):
        res = await ReportTrashModel.create_trash(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'reports_trash',
                "data": json.dumps(data),
                "changed_by": ReportTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ReportTrashController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'reports_trash',
                "data": json.dumps(data),
                "changed_by": ReportTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await ReportTrashController.log_controller.create_log(log_data)
            return res

    @staticmethod
    async def delete_trash(trash_id):
        res = await ReportTrashModel.delete_trash(trash_id)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=10):
        data = await ReportTrashModel.get_trash_paginate(
            search_data=ReportTrashController.store.get_search_text(),
            filter_preferences=ReportTrashController.store.get_filter_preferences(),
            page_number=page_number, item_per_page=item_per_page)
        if not data:
            ReportTrashController.store.set_data({})
        else:
            ReportTrashController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_trash_by_id(trash_id):
        res = await ReportTrashModel.get_trash_by_id(trash_id)
        if not res:
            ReportTrashController.store.set_trash_record({})
        else:
            ReportTrashController.store.set_trash_record(res)
            return res

    @staticmethod
    @auth_token_middleware
    async def put_back(data):
        res = await ReportTrashModel.put_back(data)
        if not res:
            log_data = {
                "action_type": 'RECOVER',
                "model_name": 'reports_trash',
                "data": json.dumps(data),
                "changed_by": ReportTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ReportTrashController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'RECOVER',
                "model_name": 'reports_trash',
                "data": json.dumps(data),
                "changed_by": ReportTrashController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await ReportTrashController.delete_trash(data["trash_id"])
            await ReportTrashController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await ReportTrashModel.apply_filter(data)
        return data
