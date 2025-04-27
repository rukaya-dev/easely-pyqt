from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.staff.assistant.doctor_service_assistant_model')


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


class DoctorServiceAssistantsRelationModel:
    @staticmethod
    async def get_doctor_service_assistants_relation_paginate(doctor_id, search_data, filter_preferences, page_number,
                                                              item_per_page):
        try:
            query = (supabase.table('doctor_service_assistants_relation').select(
                "*, doctors_schedules!inner(day), doctors!inner(first_name, last_name)",
                count='exact').eq("doctor_id", doctor_id)
                     .order("doctor_service_relation_id"))

            if filter_preferences:
                query = await DoctorServiceAssistantsRelationModel.apply_filter(filter_preferences)

            if search_data:
                query = query.or_(
                    f"doctor_service_status.ilike.%{search_data}%,service_name.ilike.%{search_data}%")

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
    async def get_doctor_service_assistants_relation_and_schedule_by_id(doctor_service_relation_id):
        try:
            data = await supabase.table('doctor_service_assistants_relation').select(
                "*, doctors_schedules!inner(*), doctors!inner(first_name, last_name)") \
                .eq('doctor_service_relation_id', doctor_service_relation_id) \
                .execute()
            if data.data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_doctor_service_assistants_relation(data):
        try:
            data = await supabase.table('doctor_service_assistants_relation').insert(data).execute()
            if data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_doctor_service_assistants_relation(doctor_service_relation_id):
        try:
            data = await supabase.table('doctor_service_assistants_relation').delete().eq('doctor_service_relation_id',
                                                                                          doctor_service_relation_id).execute()
            if data.data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_doctor_service_assistants_relation(doctor_service_relation_id, data):
        try:
            data = await supabase.table('doctor_service_assistants_relation').update(data).eq(
                'doctor_service_relation_id',
                doctor_service_relation_id).execute()
            if data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_all_doctor_service_assistants_relation():
        try:
            data = await supabase.table('doctor_service_assistants_relation').select(
                "doctor_service_relation_id, first_name, last_name").order(
                "doctor_service_relation_id").execute()
            if data:
                return data

        except Exception as e:
            logger.error(e, exc_info=True)
