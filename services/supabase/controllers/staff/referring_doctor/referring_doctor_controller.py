import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.staff.referring_doctor.referring_doctor_model import ReferringDoctorModel
from services.supabase.store.staff.referring_doctor.referring_doctor_store import ReferringDoctorStore

logger = set_up_logger('main.services.supabase.controllers.staff..referring_doctor.referring_doctor_controller')


class ReferringDoctorController:
    store = ReferringDoctorStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_referring_doctor(data):
        res = await ReferringDoctorModel.create_referring_doctor(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'referring_doctors',
                "data": json.dumps(data),
                "changed_by": ReferringDoctorController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ReferringDoctorController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'CREATE',
            "model_name": 'referring_doctors',
            "data": json.dumps(data),
            "changed_by": ReferringDoctorController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await ReferringDoctorController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        data = await ReferringDoctorModel.get_referring_doctors_paginate(
            search_data=ReferringDoctorController.store.get_search_text(),
            filter_preferences=ReferringDoctorController.store.get_filter_preferences(),
            page_number=page_number, item_per_page=item_per_page)

        if not data:
            ReferringDoctorController.store.set_data({})
        else:
            ReferringDoctorController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_searched_items(search_data):
        data = await ReferringDoctorModel.get_searched_items(search_data=search_data,
                                                             filter_preferences=ReferringDoctorController.store.get_filter_preferences())
        return data

    @staticmethod
    @auth_token_middleware
    async def get_referring_doctor_by_id(referring_doctor_id):
        data = await ReferringDoctorModel.get_referring_doctor_by_id(referring_doctor_id)
        if not data:
            ReferringDoctorController.store.set_referring_doctor({})
        else:
            ReferringDoctorController.store.set_referring_doctor(data)
            return data

    @staticmethod
    async def delete_referring_doctor(referring_doctor_id):
        associate = await ReferringDoctorController.get_referring_doctor_by_id(referring_doctor_id)
        res = await ReferringDoctorModel.delete_referring_doctor(referring_doctor_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'referring_doctors',
                "data": json.dumps(associate),
                "changed_by": ReferringDoctorController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ReferringDoctorController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'DELETE',
            "model_name": 'referring_doctors',
            "data": json.dumps(associate),
            "changed_by": ReferringDoctorController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await ReferringDoctorController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_referring_doctor(referring_doctor_id, data):
        res = await ReferringDoctorModel.update_referring_doctor(referring_doctor_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'referring_doctors',
                "data": json.dumps(data),
                "changed_by": ReferringDoctorController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await ReferringDoctorController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'UPDATE',
            "model_name": 'referring_doctors',
            "data": json.dumps(data),
            "changed_by": ReferringDoctorController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await ReferringDoctorController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await ReferringDoctorModel.apply_filter(data)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_all_referring_doctors_by_category(category):
        data = await ReferringDoctorModel.get_all_referring_doctors_by_category(category)
        if not data:
            ReferringDoctorController.store.set_data({})
        else:
            ReferringDoctorController.store.set_data(data)
            return data
