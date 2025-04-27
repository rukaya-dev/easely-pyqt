import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.patient.patient_trash_controller import PatientTrashController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.patient.patient_model import PatientModel
from services.supabase.store.patient.patients_store import PatientsStore

logger = set_up_logger('main.services.supabase.controllers.patient.patient_controller')


class PatientController:
    store = PatientsStore()

    auth_controller = UserAuthController()
    log_controller = LogController()
    trash_controller = PatientTrashController()

    @staticmethod
    @auth_token_middleware
    async def create_patient(data):
        res = await PatientModel.create_patient(data=data)
        if not res:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'patients',
                "data": json.dumps(data),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await PatientController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'CREATE',
                "model_name": 'patients',
                "data": json.dumps(data),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await PatientController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def get_items(item_per_page=20, page_number=1):
        data = await PatientModel.get_patients_paginate(search_data=PatientController.store.get_search_text(),
                                                        filter_preferences=PatientController.store.get_filter_preferences(),
                                                        page_number=page_number, item_per_page=item_per_page)
        if not data:
            PatientController.store.set_data({})

        else:
            PatientController.store.set_data(data)

            return data

    @staticmethod
    @auth_token_middleware
    async def get_all_patients_by_year(year):
        data = await PatientModel.get_all_patients_by_year(year)
        if not data:
            PatientController.store.set_data({})

        else:
            PatientController.store.set_data(data)

            return data

    @staticmethod
    @auth_token_middleware
    async def check_if_patient_exist(national_id_number):
        data = await PatientModel.check_if_patient_exist(national_id_number)
        return data

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_patient_exist(patient_id, national_id_number):
        data = await PatientModel.check_if_updated_patient_exist(patient_id, national_id_number)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_patient_by_id(patient_id):
        res = await PatientModel.get_patient_by_id(patient_id)
        if not res:
            log_data = {
                "action_type": 'GET',
                "model_name": 'patients',
                "data": json.dumps(res),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await PatientController.log_controller.create_log(log_data)
            PatientController.store.set_patient({})
        else:
            log_data = {
                "action_type": 'GET',
                "model_name": 'patients',
                "data": json.dumps(res),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await PatientController.log_controller.create_log(log_data)
            PatientController.store.set_patient(res)
            return res

    @staticmethod
    async def delete_patient(patient_id):
        patient = await PatientController.get_patient_by_id(patient_id)
        res = await PatientModel.delete_patient(patient_id)
        if not res:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'patients',
                "data": json.dumps(patient),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await PatientController.log_controller.create_log(log_data)
        else:
            log_data = {
                "action_type": 'DELETE',
                "model_name": 'patients',
                "data": json.dumps(patient),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await PatientController.log_controller.create_log(log_data)
            trash_data = {
                "patient_id": patient_id,
                "patient_info": json.dumps(patient),
                "deleted_by": PatientController.auth_controller.user_auth_store.get_user()["email"]

            }
            await PatientController.trash_controller.create_trash(trash_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def update_patient(patient_id, data):
        res = await PatientModel.update_patient(patient_id, data)
        if not res:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'patients',
                "data": json.dumps(data),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Failed',
            }
            await PatientController.log_controller.create_log(log_data)
            PatientController.store.set_patient({})
        else:
            log_data = {
                "action_type": 'UPDATE',
                "model_name": 'patients',
                "data": json.dumps(data),
                "changed_by": PatientController.auth_controller.user_auth_store.get_user()["email"],
                "status": 'Success',

            }
            await PatientController.log_controller.create_log(log_data)
            return res

    @staticmethod
    @auth_token_middleware
    async def apply_filter(data):
        data = await PatientModel.apply_filter(data)
        return data
