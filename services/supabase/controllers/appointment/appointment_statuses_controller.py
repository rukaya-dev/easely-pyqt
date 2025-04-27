from loggers.logger_configs import set_up_logger
from services.supabase.middlewares.auth_token_middleware import auth_token_middleware
from services.supabase.models.appointment.appointment_statuses_model import AppointmentStatusesModel
from services.supabase.store.appointment.appointment_statuses_store import AppointmentStatusesStore

logger = set_up_logger('main.services.supabase.controllers.appointment.appointment_statuses_controller')


class AppointmentStatusesController:
    store = AppointmentStatusesStore()

    @staticmethod
    @auth_token_middleware
    async def create_appointment_status(data):
        try:
            is_exist = await AppointmentStatusesModel.check_if_appointment_status_exist(data["status_name"])
            if is_exist:
                return
            res = await AppointmentStatusesModel.create_appointment_status(data=data)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def get_items():
        try:
            data = await AppointmentStatusesModel.get_appointment_status_paginate()
            if not data:
                AppointmentStatusesController.store.set_data({})
            else:
                AppointmentStatusesController.store.set_data(data)
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def check_if_appointment_statuses_exist(status_id):
        data = await AppointmentStatusesModel.check_if_appointment_status_exist(
            status_id)
        return data

    @staticmethod
    async def delete_appointment_statuses(appointment_statuses_id):
        try:
            res = await AppointmentStatusesModel.delete_appointment_status(
                appointment_statuses_id)
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    @auth_token_middleware
    async def update_appointment_statuses(status_id, data):
        try:
            is_exist = await AppointmentStatusesModel.check_if_updated_appointment_status_exist(status_id, data["status_name"])
            if is_exist:
                return
            res = await AppointmentStatusesModel.update_appointment_status(
                status_id, data["status_name"])
            return res
        except Exception as e:
            logger.error(e, exc_info=True)

