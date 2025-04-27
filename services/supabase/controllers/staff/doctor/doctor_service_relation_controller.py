import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.staff.doctor.doctor_service_relation_model import DoctorServiceRelationModel
from services.supabase.store.staff.doctor.doctor_service_relation_store import DoctorServiceRelationStore

logger = set_up_logger('main.services.supabase.controllers.staff.doctor.doctor_service_relation_controller')


class DoctorServiceRelationController:
    store = DoctorServiceRelationStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_doctor_service_relation(data):
        res = await DoctorServiceRelationModel.create_doctor_service_relation(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'doctors_services_relation',
                "data": json.dumps(data),
                "changed_by": DoctorServiceRelationController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorServiceRelationController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'CREATE',
            "model_name": 'doctors_services_relation',
            "data": json.dumps(data),
            "changed_by": DoctorServiceRelationController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorServiceRelationController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(doctor_id, page_number=1, item_per_page=10):
        data = await DoctorServiceRelationModel.get_doctor_service_relations_paginate(
            doctor_id=doctor_id,
            search_data=DoctorServiceRelationController.store.get_search_text(),
            filter_preferences=DoctorServiceRelationController.store.get_filter_preferences(),
            page_number=page_number, item_per_page=item_per_page)

        if not data:
            DoctorServiceRelationController.store.set_data({})
        else:
            DoctorServiceRelationController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_doctor_service_relation_and_schedule_by_id(doctor_service_relation_id):
        res = await DoctorServiceRelationModel.get_doctor_service_relation_and_schedule_by_id(
            doctor_service_relation_id)
        return res

    @staticmethod
    async def delete_doctor_service_relation(doctor_service_relation_id):
        doctor_service_relation = await DoctorServiceRelationController.get_doctor_service_relation_and_schedule_by_id(
            doctor_service_relation_id)
        res = await DoctorServiceRelationModel.delete_doctor_service_relation(doctor_service_relation_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'doctors_services_relation',
                "data": json.dumps(doctor_service_relation),
                "changed_by": DoctorServiceRelationController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorServiceRelationController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'DELETE',
            "model_name": 'doctors_services_relation',
            "data": json.dumps(doctor_service_relation),
            "changed_by": DoctorServiceRelationController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorServiceRelationController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_doctor_service_relation(doctor_service_relation_id, data):
        res = await DoctorServiceRelationModel.update_doctor_service_relation(doctor_service_relation_id, data)
        modified_data = {"record_id": doctor_service_relation_id}
        modified_data.update(data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'doctors_services_relation',
                "data": json.dumps(modified_data),
                "changed_by": DoctorServiceRelationController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorServiceRelationController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'UPDATE',
            "model_name": 'doctors_services_relation',
            "data": json.dumps(modified_data),
            "changed_by": DoctorServiceRelationController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorServiceRelationController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_all_doctors_by_service_name(service_name):
        data = await DoctorServiceRelationModel.get_all_doctors_by_service_name(service_name)
        if data.data:
            doctors = []
            for row in data.data:
                doctors.append({"doctor_service_relation_id": row["doctor_service_relation_id"],
                                "doctor_id": row["doctor_id"],
                                "first_name": row["doctors"]["first_name"],
                                "last_name": row["doctors"]["last_name"],
                                })
            return doctors
