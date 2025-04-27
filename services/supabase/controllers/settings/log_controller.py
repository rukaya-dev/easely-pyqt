from loggers.logger_configs import set_up_logger
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.settings.log_model import LogModel
from services.supabase.store.settings.log_store import LogStore

logger = set_up_logger('main.services.supabase.controllers.log_controller')


class LogController:
    store = LogStore()

    @staticmethod
    @auth_token_middleware
    async def create_log(data):
        res = await LogModel.create_log(data=data)
        if res:
            return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=10):
        data = await LogModel.get_log_paginate(search_data=LogController.store.get_search_text(),
                                               filter_preferences=LogController.store.get_filter_preferences(),
                                               page_number=page_number, item_per_page=item_per_page)
        if not data:
            LogController.store.set_data({})
            return None
        else:
            LogController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_log_by_id(log_id):
        res = await LogModel.get_log_by_id(log_id)
        if not res:
            LogController.store.set_log_record({})
            return
        LogController.store.set_log_record(res)
        return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        res = await LogModel.apply_filter(data)
        if res:
            return res
