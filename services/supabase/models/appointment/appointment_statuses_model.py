from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.appointment.appointment_status_model')


class AppointmentStatusesModel:
    @staticmethod
    async def get_appointment_status_paginate():
        try:
            data = await supabase.table('appointment_statuses').select("*", count='exact').order("status_id").execute()

            return data.data

        except Exception as e:
            logger.error(f"Error fetching paginated items: {e}")

    @staticmethod
    async def create_appointment_status(data):
        try:
            data = await supabase.table('appointment_statuses').insert(data).execute()
            if data.data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_appointment_status_exist(status_name):
        try:
            data = await (supabase.table('appointment_statuses')
                          .select('status_name')
                          .eq('status_name', status_name)
                          .execute())
            if len(data.data) > 0:
                return True
            return False
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_appointment_status(status_id):
        try:
            data = await supabase.table('appointment_statuses').delete().eq('status_id',
                                                                            status_id).execute()

            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_appointment_status(status_id, data):
        try:
            data = await supabase.table('appointment_statuses').update(data).eq('status_id',
                                                                                status_id).execute()
            if data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_appointment_status_exist(status_id, status_name):
        try:
            data = await (supabase.table('appointment_statuses').select('status_name')
                          .neq('status_id', status_id)
                          .eq("status_name", status_name)
                          .execute())

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)
