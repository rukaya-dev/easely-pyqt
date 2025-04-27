import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.staff.assistant.doctor_service_assistants_model import \
    DoctorServiceAssistantsRelationModel
from services.supabase.store.staff.assistants.dorctor_service_assistants_relation_store import \
    DoctorServiceAssistantsRelationStore

logger = set_up_logger('main.services.supabase.controllers.staff..assistant.doctor_service_assistants_controller')


class DoctorServiceAssistantsRelationController:
    store = DoctorServiceAssistantsRelationStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_doctor_service_assistants_relation(data):
        res = await DoctorServiceAssistantsRelationModel.create_doctor_service_assistants_relation(data=data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items(doctor_id, page_number=1, item_per_page=10):
        data = await DoctorServiceAssistantsRelationModel.get_doctor_service_assistants_relation_paginate(
            doctor_id=doctor_id,
            search_data=DoctorServiceAssistantsRelationController.store.get_search_text(),
            filter_preferences=DoctorServiceAssistantsRelationController.store.get_filter_preferences(),
            page_number=page_number, item_per_page=item_per_page)

        if not data:
            DoctorServiceAssistantsRelationController.store.set_data({})
        else:
            DoctorServiceAssistantsRelationController.store.set_data(data)
            return data

    @staticmethod
    @auth_token_middleware
    async def get_doctor_service_assistants_relation_and_schedule_by_id(doctor_service_relation_id):
        res = await DoctorServiceAssistantsRelationModel.get_doctor_service_assistants_relation_and_schedule_by_id(doctor_service_relation_id)
        return res

    @staticmethod
    async def delete_doctor_service_assistants_relation(doctor_service_relation_id):
        res = await DoctorServiceAssistantsRelationModel.delete_doctor_service_assistants_relation(doctor_service_relation_id)
        return res

    @staticmethod
    @auth_token_middleware
    async def update_doctor_service_assistants_relation(doctor_service_relation_id, data):
        res = await DoctorServiceAssistantsRelationModel.update_doctor_service_assistants_relation(doctor_service_relation_id, data)
        modified_data = {"record_id": doctor_service_relation_id}
        modified_data.update(data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'doctor_service_assistants_relation',
                "data": json.dumps(modified_data),
                "changed_by": DoctorServiceAssistantsRelationController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await DoctorServiceAssistantsRelationController.log_controller.create_log(log_data)
            return
        log_data = {
            "action_type": 'UPDATE',
            "model_name": 'doctor_service_assistants_relation',
            "data": json.dumps(modified_data),
            "changed_by": DoctorServiceAssistantsRelationController.auth_controller.user_auth_store.get_user()["email"],
            "status": 'Success',
        }
        await DoctorServiceAssistantsRelationController.log_controller.create_log(log_data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_all_doctor_service_assistants_relations():
        data = await DoctorServiceAssistantsRelationModel.get_all_doctor_service_assistants_relations()
        if data:
            return data.data
