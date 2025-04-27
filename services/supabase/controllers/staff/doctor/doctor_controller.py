import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.staff.doctor.doctor_model import DoctorModel
from services.supabase.store.staff.doctor.doctor_store import DoctorStore

logger = set_up_logger('main.services.supabase.controllers.staff.doctor.doctor_controller')


class DoctorController:
    store = DoctorStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_doctor(data):
        res = await DoctorModel.create_doctor(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'doctors',
                "data": json.dumps(data),
                "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'CREATE',
            "model_name": 'doctors',
            "data": json.dumps(data),
            "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        data = await DoctorModel.get_doctors_paginate(search_data=DoctorController.store.get_search_text(),
                                                      filter_preferences=DoctorController.store.get_filter_preferences(),
                                                      page_number=page_number, item_per_page=item_per_page)
        if not data:
            DoctorController.store.set_data({})
        else:
            DoctorController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_doctor_by_id(doctor_id):
        res = await DoctorModel.get_doctor_by_id(doctor_id)
        if not res:
            DoctorController.store.set_doctor({})
            log_data = {
                "action_type": 'GET',
                "model_name": 'doctors',
                "data": json.dumps({"doctor_id": doctor_id}),
                "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorController.log_controller.create_log(log_data)
            return

        DoctorController.store.set_doctor(res)
        log_data = {
            "action_type": 'GET',
            "model_name": 'doctors',
            "data": json.dumps({"doctor_id": doctor_id}),
            "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorController.log_controller.create_log(log_data)
        return res

    @staticmethod
    async def delete_doctor(doctor_id):
        doctor = await DoctorController.get_doctor_by_id(doctor_id)
        res = await DoctorModel.delete_doctor(doctor_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'doctors',
                "data": json.dumps(doctor),
                "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'DELETE',
            "model_name": 'doctors',
            "data": json.dumps(doctor),
            "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_doctor(doctor_id, data):
        res = await DoctorModel.update_doctor(doctor_id, data)
        modified_data = {"record_id": doctor_id}
        modified_data.update(data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'doctors',
                "data": json.dumps(modified_data),
                "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'UPDATE',
            "model_name": 'doctors',
            "data": json.dumps(modified_data),
            "changed_by": DoctorController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await DoctorModel.apply_filter(data)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_all_doctors():
        data = await DoctorModel.get_all_doctors()
        if data:
            return data.data
