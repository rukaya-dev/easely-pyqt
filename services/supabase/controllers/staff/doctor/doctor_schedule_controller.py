import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.staff.doctor.doctor_schedule_model import DoctorScheduleModel
from services.supabase.store.staff.doctor.doctor_schedule_store import DoctorScheduleStore

logger = set_up_logger('main.services.supabase.controllers.staff.doctor.doctor_schedule_controller')


class DoctorScheduleController:
    store = DoctorScheduleStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_doctor_schedule(data):
        res = await DoctorScheduleModel.create_doctor_schedule(data=data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=10):
        data = await DoctorScheduleModel.get_doctor_schedules_paginate(
            search_data=DoctorScheduleController.store.get_search_text(),
            filter_preferences=DoctorScheduleController.store.get_filter_preferences(),
            page_number=page_number, item_per_page=item_per_page)

        if not data:
            DoctorScheduleController.store.set_data({})
        else:
            DoctorScheduleController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_doctor_schedule_by_id(doctor_schedule_id):
        res = await DoctorScheduleModel.get_doctor_schedule_by_id(doctor_schedule_id)
        if not res:
            DoctorScheduleController.store.set_doctor_schedule({})
            log_data = {
                "action_type": 'GET',
                "model_name": 'doctor_schedules',
                "data": json.dumps({"doctor_schedule_id": doctor_schedule_id}),
                "changed_by": DoctorScheduleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorScheduleController.log_controller.create_log(log_data)
            return

        DoctorScheduleController.store.set_doctor_schedule(res)
        log_data = {
            "action_type": 'GET',
            "model_name": 'doctor_schedules',
            "data": json.dumps({"doctor_schedule_id": doctor_schedule_id}),
            "changed_by": DoctorScheduleController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorScheduleController.log_controller.create_log(log_data)
        return res

    @staticmethod
    async def delete_doctor_schedule(data):
        res = await DoctorScheduleModel.delete_doctor_schedule(data)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_doctor_schedule(data):
        res = await DoctorScheduleModel.update_doctor_schedule(data)
        modified_data = {"record_id": data["doctor_schedule_id"]}
        modified_data.update(data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'doctor_schedules',
                "data": json.dumps(modified_data),
                "changed_by": DoctorScheduleController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorScheduleController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'UPDATE',
            "model_name": 'doctor_schedules',
            "data": json.dumps(modified_data),
            "changed_by": DoctorScheduleController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorScheduleController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await DoctorScheduleModel.apply_filter(data)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_all_doctor_schedules(doctor_service_relation_id):
        data = await DoctorScheduleModel.get_all_doctor_schedules(doctor_service_relation_id)
        if data:
            return data.data
