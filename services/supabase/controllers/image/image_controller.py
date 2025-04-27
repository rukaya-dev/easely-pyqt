import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.image.image_model import ImageModel
from services.supabase.store.image.image_store import ImageStore

logger = set_up_logger('main.services.supabase.controllers.image.image_controller')


class ImageController:
    store = ImageStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_image(data):
        try:
            res = await ImageModel.create_image(data=data)

            if not res:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'images',
                    "data": json.dumps(data),
                    "changed_by": ImageController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await ImageController.log_controller.create_log(log_data)
            else:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'images',
                    "data": json.dumps(data),
                    "changed_by": ImageController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await ImageController.log_controller.create_log(log_data)
                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=15):
        try:
            data = await ImageModel.get_images_paginate(
                filter_preferences=ImageController.store.get_filter_preferences(),
                page_number=page_number, item_per_page=item_per_page)

            if not data:
                ImageController.store.set_search_filter_tab_data({})
            else:
                ImageController.store.set_search_filter_tab_data(data)
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def update_image_in_db(image_id, data):
        try:
            res = await ImageModel.update_image_in_db(image_id=image_id, data=data)

            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def upload_image_to_storage(file_path, file, mime_type):
        try:
            res = await ImageModel.upload_image_to_storage(file_path, file, mime_type)
            if res:

                return res.text
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_image_from_storage(file_path):
        try:
            res = await ImageModel.get_image_from_storage(file_path)

            return res
        except Exception as e:
            logger.error(e, exc_info=True)
