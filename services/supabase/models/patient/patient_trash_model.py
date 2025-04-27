import json
import time
from datetime import datetime, timedelta, timezone

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.patient.patient_trash_model')


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


class PatientTrashModel:
    @staticmethod
    async def get_trash_paginate(search_data, filter_preferences, page_number,
                                 item_per_page):
        try:
            query = supabase.table('patients_trash').select("*", count='exact').order("trash_id", desc=True)

            if filter_preferences:
                query = await PatientTrashModel.apply_filter(filter_preferences)

            if search_data:
                query = query.or_(
                    f"deleted_by.ilike.%{search_data}%")

            data, total_count = await paginate(query, item_per_page, page_number)

            if data:
                normalized_data = []
                for patient in data:
                    flattened_patient_data = PatientTrashModel.flatten_patient_data(json.loads(patient["patient_info"]))
                    patient.update(flattened_patient_data)
                    patient.pop("patient_info")
                    normalized_data.append(patient)

                data = normalized_data

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
            logger.error(f"Error fetching paginated categories: {e}")
            return {
                "data": [],
                "total_count": 0,
                "current_page": page_number,
                "prev_page": None,
                "next_page": None,
                "total_pages": 0
            }

    @staticmethod
    async def get_trash_by_id(trash_id):
        try:
            data = await supabase.table('patients_trash').select("*").eq('trash_id', trash_id).execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def put_back(data):
        try:
            data = await supabase.table('patients').update({"deleted_at": None}).eq('patient_id', data[
                "patient_id"]).execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_trash(data):
        try:
            data = await supabase.table('patients_trash').insert(data).execute()
            if data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_trash(trash_id):
        try:
            data = await supabase.table('patients_trash').delete() \
                .eq('trash_id', trash_id).execute()
            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def apply_filter(data):
        try:
            query = supabase.table('patients_trash').select("trash_id,deleted_by,deleted_at,patient_info,patient_id!inner(national_id_number,first_name,last_name)", count='exact')

            if data["national_id_number"].get("enabled"):
                query = query.eq('patient_id.national_id_number',
                                 data["national_id_number"].get("national_id_number_value"))

            if data["patient"].get("enabled"):
                    query = query.ilike('patient_id.first_name',
                                        f'%{data["patient"].get("firstname")}%')
                    query = query.ilike('patient_id.last_name',
                                        f'%{data["patient"].get("lastname")}%')

            # Time filter mapping
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
            if data["deleted_at"].get("enabled"):
                query = apply_time_filter(data.get("deleted_at", {}), 'deleted_at')

            query = query.order("trash_id", desc=True)

            return query
        except Exception as e:
            logger.error(f"Error fetching Patient Trash filtered data ....: {e}")

    @staticmethod
    def flatten_patient_data(data):
        patient = {
            "name": data["first_name"] + ' ' + data["last_name"],
            "age": str(data["patient_age"]) + ' ' + data["patient_age_unit"],
            "gender": data["patient_gender"],
            "phone_number": data["patient_phone_number"],
        }
        return patient
