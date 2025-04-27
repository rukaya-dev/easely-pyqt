from datetime import datetime, timedelta, timezone

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.staff.doctor.doctor_schedule_model')


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


class DoctorScheduleModel:
    @staticmethod
    async def get_doctor_schedules_paginate(search_data, filter_preferences, page_number,
                                            item_per_page):
        try:
            query = (supabase.table('doctors_schedules').select(
                "*",
                count='exact')
                     .order("doctor_schedule_id"))

            if filter_preferences:
                query = await DoctorScheduleModel.apply_filter(filter_preferences)

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
    async def get_doctor_schedule_by_id(doctor_schedule_id):
        try:
            data = await supabase.table('doctors_schedules').select(
                "*") \
                .eq('doctor_schedule_id', doctor_schedule_id) \
                .execute()
            if data.data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_doctor_schedule(data):
        try:
            data = await supabase.table('doctors_schedules').insert(data).execute()
            if data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_doctor_schedule(data):
        try:
            data = await supabase.table('doctors_schedules').delete() \
                .eq('doctor_service_relation_id',
                    data["doctor_service_relation_id"]) \
                .eq("doctor_id", data["doctor_id"]) \
                .execute()
            if data.data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_doctor_schedule(data):
        try:
            data = await supabase.table('doctors_schedules').update(data).eq('doctor_service_relation_id',
                                                                             data[
                                                                                 "doctor_service_relation_id"]).execute()
            if data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def apply_filter(data):
        try:
            query = supabase.table('doctors_schedules').select(
                "*",
                count='exact')

            if data["available_days"].get("enabled"):
                days = list(data["available_days"].get("days"))
                query = query.overlaps('available_days', days)

            if data["available_time_slot"].get("enabled"):
                time_slot_as_list = [data["available_time_slot"].get("time_slot")]
                query = query.contains('available_time_slots', time_slot_as_list)

            time_filters = {
                "last_24_hours": timedelta(hours=24),
                "last_7_days": timedelta(days=7),
                "last_14_days": timedelta(days=14),
                "last_30_days": timedelta(days=30),
            }

            def apply_time_filter(filter_data, field_name):
                nonlocal query
                if filter_data.get("enabled"):
                    if filter_data.get("filteration_type") == "preset_filter":
                        time_delta = time_filters.get(filter_data.get("preset_filter_id"))
                        if time_delta:
                            formatted_timestamp = (datetime.now(timezone.utc) - time_delta).isoformat()
                            query = query.gte(field_name, formatted_timestamp)
                    elif filter_data.get("filteration_type") == "custom_filter":
                        custom_date_value = filter_data.get("custom_date_value")
                        if custom_date_value:
                            specific_date = datetime.strptime(custom_date_value, "%a %b %d %Y")
                            specific_date_end = specific_date + timedelta(days=1)  # End of the specific day
                            query = query.gte(field_name, specific_date.strftime("%Y-%m-%d %H:%M:%S")).lte(
                                field_name, specific_date_end.strftime("%Y-%m-%d %H:%M:%S"))

                return query

            # Apply filters for created_at and updated_at
            if data["created_at"].get("enabled"):
                query = apply_time_filter(data.get("created_at", {}), 'created_at')

            if data["updated_at"].get("enabled"):
                query = apply_time_filter(data.get("updated_at", {}), 'updated_at')

            query = query.order("doctor_schedule_id", desc=True)

            return query
        except Exception as e:
            logger.error(f"Error fetching doctor_schedules filtered data ....: {e}")

    @staticmethod
    async def get_all_doctor_schedules(doctor_service_relation_id):
        try:
            data = await supabase.table('doctors_schedules').select("*") \
                .eq("doctor_service_relation_id", doctor_service_relation_id) \
                .order(
                "schedule_id").execute()
            if data:
                return data

        except Exception as e:
            logger.error(e, exc_info=True)
