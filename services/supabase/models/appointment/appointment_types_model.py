from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.appointment.appointment_types_model')


async def paginate(query, item_per_page=10, page_number=1):
    """
    Paginate the query for Supabase.

    Args:
        query: The Supabase query object.
        item_per_page (int): Number of items per page.
        page_number (int): Current page number.

    Returns:
        A tuple containing the paginated data and the total count.
    """
    # Calculate offset
    offset = (page_number - 1) * item_per_page

    try:
        data = await query.limit(item_per_page).offset(offset).execute()

        total_count = data.count
        return data.data, total_count
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        return [], 0


class AppointmentTypesModel:
    @staticmethod
    async def get_appointment_types_paginate():
        try:
            data = await supabase.table('appointment_types').select("*").order("type_id").execute()
            return data.data

        except Exception as e:
            logger.error(f"Error fetching paginated items: {e}")

    @staticmethod
    async def create_appointment_type(data):
        try:
            data = await supabase.table('appointment_types').insert(data).execute()
            if data.data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_appointment_type_exist(type_name):
        try:
            data = await (supabase.table('appointment_types')
                          .select('type_name')
                          .eq('type_name', type_name)
                          .execute())
            if len(data.data) > 0:
                return True
            return False
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_appointment_type(type_id):
        try:
            data = await supabase.table('appointment_types').delete().eq('type_id',
                                                                         type_id).execute()

            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_appointment_type(type_id, data):
        try:
            data = await supabase.table('appointment_types').update(data).eq('type_id',
                                                                             type_id).execute()
            if data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_appointment_type_exist(type_id, type_name):
        try:
            data = await (supabase.table('appointment_types').select('type_name')
                          .neq('type_id', type_id)
                          .eq("type_name", type_name)
                          .execute())

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)
