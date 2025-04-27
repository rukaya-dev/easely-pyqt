import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.report_workshop.report_layout_model import ReportLayoutModel
from services.supabase.store.report_workshop.report_layout_store import ReportLayoutStore

logger = set_up_logger('main.services.supabase.controllers.report_workshop.report_layout_controller')


class ReportLayoutController:
    store = ReportLayoutStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_report_layout(data):
        res = await ReportLayoutModel.create_report_header_layout(data=data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_report_header_layout():
        res = await ReportLayoutModel.get_report_header_layout()
        if not res:
            ReportLayoutController.store.set_report_header_layout({})
        else:
            ReportLayoutController.store.set_report_header_layout(res)
            return res

    @staticmethod
    @auth_token_middleware
    async def get_report_footer_layout():
        res = await ReportLayoutModel.get_report_footer_layout()
        if not res:
            ReportLayoutController.store.set_report_footer_layout({})
        else:
            ReportLayoutController.store.set_report_footer_layout(res)
            return res

    @staticmethod
    @auth_token_middleware
    async def update_report_header_layout(data):
        res = await ReportLayoutModel.update_header_report_layout(data)
        return res
