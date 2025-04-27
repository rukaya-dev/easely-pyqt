from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.appointment.doctors_days_availabilities_model')


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
        # Execute a query with limit and offset, and get total count
        data = await query.limit(item_per_page).offset(offset).execute()

        # Extracting total count from the Supabase response
        total_count = data.count
        return data.data, total_count
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        return [], 0


class DoctorsDaysAvailabilitiesModel:
    @staticmethod
    async def get_doctors_days_availabilities_paginate(page_number,
                                                       item_per_page):
        try:
            query = (supabase.table('doctors_days_availabilities').select(
                "*",
                count='exact')
                     .order("availability_id"))

            data, total_count = await paginate(query, item_per_page, page_number)

            # Calculate total pages
            total_pages = (total_count + item_per_page - 1) // item_per_page

            # Calculate prev and next page numbers
            prev_page = page_number - 1 if page_number > 1 else None
            next_page = page_number + 1 if page_number < total_pages else None

            return {
                "data": data,
                "total_count": total_count,
                "current_page": page_number,
                "prev_page": prev_page,
                "next_page": next_page,
                "total_pages": total_pages
            }

        except Exception as e:
            logger.error(f"Error fetching paginated items: {e}")
            return {
                "data": [],
                "total_count": 0,
                "current_page": page_number,
                "prev_page": None,
                "next_page": None,
                "total_pages": 0
            }

    @staticmethod
    async def get_all_doctor_days_by_id(doctor_id):
        try:
            data = await supabase.table('doctors_days_availabilities').select(
                "*") \
                .eq('doctor_id', doctor_id) \
                .execute()

            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_doctor_available_time_slots(doctor_id):
        try:
            data = await supabase.table('doctors_days_availabilities').select(
                "*") \
                .eq('doctor_id', doctor_id) \
                .eq("slot_status", "Available") \
                .execute()


            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_doctors_days_availabilities(data):
        try:
            data = await supabase.table('doctors_days_availabilities').insert(data).execute()
            if data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_doctors_days_availabilities_exist(doctor_id):
        try:
            data = await (supabase.table('doctors_days_availabilities')
                          .select('days_of_week')
                          .eq('doctor_id', doctor_id)
                          .execute())
            if len(data.data) > 0:
                return True
            return False
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_doctors_days_availabilities(slot_id):
        try:
            data = await supabase.table('doctors_days_availabilities').delete().eq('slot_id',
                                                                                   slot_id).execute()

            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_doctors_days_availabilities(availability_id, data):
        try:
            data = await supabase.table('doctors_days_availabilities').update(data).eq('availability_id',
                                                                                       availability_id).execute()
            if not data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_doctors_days_availabilities_exist(availability_id, doctor_id):
        try:
            data = await (supabase.table('doctors_days_availabilities').select('time_slot')
                          .neq('availability_id', availability_id)
                          .eq("doctor_id", doctor_id)
                          .execute())

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)
