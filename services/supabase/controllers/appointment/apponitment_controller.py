import json

from loggers.logger_configs import set_up_logger
from services.supabase.controllers.settings.log_controller import LogController
from services.supabase.controllers.settings.user_auth_controller import UserAuthController
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.appointment.appointment_model import AppointmentModel
from services.supabase.store.appointment.appointment_store import AppointmentStore

logger = set_up_logger('main.services.supabase.controllers.appointment.appointment_controller')


class AppointmentController:
    store = AppointmentStore()
    auth_controller = UserAuthController()
    log_controller = LogController()

    @staticmethod
    @auth_token_middleware
    async def create_appointment(data, patient_data):

        try:
            res = await AppointmentModel.create_appointment(data=data)
            log_data = {
                "patient_id": data["patient_id"],
                "patient_firstname": patient_data["first_name"],
                "patient_lastname": patient_data["last_name"],
                "patient_age": patient_data["patient_age"],
                "patient_gender": patient_data["patient_gender"],
                "patient_phone_number": patient_data["patient_phone_number"],
                "appointment_date": data["appointment_date"],
                "appointment_time": data["appointment_time"],
                "appointment_status": "scheduled",
                "doctor_firstname": patient_data["doctor_service_relation_data"]["doctors"]["first_name"],
                "doctor_lastname": patient_data["doctor_service_relation_data"]["doctors"]["last_name"],
                "service_cost": patient_data["doctor_service_relation_data"]["doctor_service_cost"],
                "service_duration": patient_data["doctor_service_relation_data"]["doctor_service_duration"]
            }

            if not res:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'appointments',
                    "data": json.dumps(log_data),
                    "changed_by": AppointmentController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await AppointmentController.log_controller.create_log(log_data)
            else:
                log_data = {
                    "action_type": 'CREATE',
                    "model_name": 'appointments',
                    "data": json.dumps(log_data),
                    "changed_by": AppointmentController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await AppointmentController.log_controller.create_log(log_data)
                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_items(page_number=1, item_per_page=20):
        try:
            data = await AppointmentModel.get_appointments_paginate(
                filter_preferences=AppointmentController.store.get_filter_preferences(),
                page_number=page_number, item_per_page=item_per_page)

            if not data:
                AppointmentController.store.set_search_filter_tab_data({})
            else:
                AppointmentController.store.set_search_filter_tab_data(data)
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def check_if_appointment_exist(data):
        data = await AppointmentModel.check_if_appointment_exist(data)
        return data

    @staticmethod
    @auth_token_middleware
    async def check_if_any_taken_doctor_service_time_slots(date, doctor_service_relation_id):
        data = await AppointmentModel.check_if_any_taken_doctor_service_time_slots(date, doctor_service_relation_id)
        return data

    @staticmethod
    async def delete_appointment(appointment_id):
        try:
            res = await AppointmentModel.delete_appointment(
                appointment_id)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def update_appointment(appointment_id, data, patient_data):
        try:
            res = await AppointmentModel.update_appointment(
                appointment_id, data)

            patient_data.update(data)

            if not res:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'appointments',
                    "data": json.dumps(patient_data),
                    "changed_by": AppointmentController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await AppointmentController.log_controller.create_log(log)
            else:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'appointments',
                    "data": json.dumps(patient_data),
                    "changed_by": AppointmentController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await AppointmentController.log_controller.create_log(log)

                current_active_tab = AppointmentController.store.active_appointment_tab

                tab_method_map = {
                    "all": AppointmentController.store.set_all_tab_data,
                    "scheduled": AppointmentController.store.set_scheduled_data,
                    "upcoming": AppointmentController.store.set_upcoming_tab_data,
                    "canceled": AppointmentController.store.set_expired_tab_data,
                    "expired": AppointmentController.store.set_expired_tab_data
                }

                if current_active_tab in tab_method_map:
                    refreshed_data = await AppointmentController.get_items_by_tabs(current_active_tab)
                    tab_method_map[current_active_tab](refreshed_data)

                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def check_if_updated_appointment_exist(appointment_id, appointment_date, appointment_time):
        data = await AppointmentModel.check_if_updated_appointment_exist(appointment_id, appointment_date,
                                                                         appointment_time)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_appointment_status_by_id(appointment_id):
        data = await AppointmentModel.get_appointment_status_by_id(appointment_id)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_all_appointments_by_year(year):
        data = await AppointmentModel.get_all_appointments_by_year(year)
        return data

    @staticmethod
    @auth_token_middleware
    async def get_appointment_additional_data_by_id(appointment_id):
        data = await AppointmentModel.get_appointment_additional_data_by_id(appointment_id)
        return data

    @staticmethod
    @auth_token_middleware
    async def update_appointment_status_or_additional_data(appointment_id, data):
        try:
            res = await AppointmentModel.update_appointment_status_or_additional_data(appointment_id, data)
            if not res:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'appointments',
                    "data": json.dumps(data),
                    "changed_by": AppointmentController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Failed',
                }
                await AppointmentController.log_controller.create_log(log)
            else:
                log = {
                    "action_type": 'UPDATE',
                    "model_name": 'appointments',
                    "data": json.dumps(data),
                    "changed_by": AppointmentController.auth_controller.user_auth_store.get_user()["email"],
                    "status": 'Success',
                }
                await AppointmentController.log_controller.create_log(log)
            current_active_tab = AppointmentController.store.active_appointment_tab

            tab_method_map = {
                "all": AppointmentController.store.set_all_tab_data,
                "scheduled": AppointmentController.store.set_scheduled_data,
                "upcoming": AppointmentController.store.set_upcoming_tab_data,
                "canceled": AppointmentController.store.set_expired_tab_data,
                "expired": AppointmentController.store.set_expired_tab_data
            }

            if current_active_tab in tab_method_map:
                refreshed_data = await AppointmentController.get_items_by_tabs(current_active_tab)
                tab_method_map[current_active_tab](refreshed_data)
            return res

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_appointment_by_id(appointment_id):
        try:
            res = await AppointmentModel.get_appointment_by_id(appointment_id)
            if res:
                AppointmentController.store.set_appointment(res)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_appointment_data_for_billing(appointment_id):
        try:
            res = await AppointmentModel.get_appointment_data_for_billing(appointment_id)
            if res:
                return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_upcoming_sessions():
        res = await AppointmentModel.get_upcoming_sessions()
        data = res if res else []
        AppointmentController.store.set_upcoming_tab_data(data)
        return res

    @staticmethod
    @auth_token_middleware
    async def get_items_by_tabs(filter_id, page_number=1, item_per_page=20):

        res = await AppointmentModel.apply_preset_filter(filter_id, item_per_page=item_per_page,
                                                         page_number=page_number)
        data = res if res else []

        if filter_id == "upcoming":
            AppointmentController.store.set_upcoming_tab_data(data)
        elif filter_id == "expired":
            AppointmentController.store.set_expired_tab_data(data)
        elif filter_id == "canceled":
            AppointmentController.store.set_canceled_tab_data(data)
        else:
            AppointmentController.store.set_all_tab_data(data)

        return res

    @staticmethod
    @auth_token_middleware
    async def search_appointments():
        data = await AppointmentModel.search_appointments(AppointmentController.store.get_search_text())
        data = data if data else []
        AppointmentController.store.set_search_filter_tab_data(data)
        return data
