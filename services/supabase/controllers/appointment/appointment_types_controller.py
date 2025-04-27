from loggers.logger_configs import set_up_logger
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.appointment.appointment_types_model import AppointmentTypesModel
from services.supabase.store.appointment.appointment_types_store import AppointmentTypesStore

logger = set_up_logger('main.services.supabase.controllers.appointment.appointment_Types_controller')


class AppointmentTypesController:
    store = AppointmentTypesStore()

    @staticmethod
    @auth_token_middleware
    async def create_appointment_types(data):
        try:
            is_exist = await AppointmentTypesModel.check_if_appointment_type_exist(data["type_name"])
            if is_exist:
                return
            res = await AppointmentTypesModel.create_appointment_type(data=data)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_items():
        try:
            data = await AppointmentTypesModel.get_appointment_types_paginate()
            if not data:
                AppointmentTypesController.store.set_data({})
            else:
                AppointmentTypesController.store.set_data(data)
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def check_if_appointment_type_exist(status_id):
        data = await AppointmentTypesModel.check_if_appointment_type_exist(
            status_id)
        return data

    @staticmethod
    async def delete_appointment_type(appointment_type_id):
        try:
            res = await AppointmentTypesModel.delete_appointment_type(
                appointment_type_id)

            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def update_appointment_type(type_id, data):
        try:
            is_exist = await AppointmentTypesModel.check_if_updated_appointment_type_exist(type_id, data["type_name"])
            if is_exist:
                return
            res = await AppointmentTypesModel.update_appointment_type(
                type_id, data)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

