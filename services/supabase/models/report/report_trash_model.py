import json
from datetime import datetime, timedelta, timezone

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.report.report_trash_model')


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


class ReportTrashModel:
    @staticmethod
    async def get_trash_paginate(search_data, filter_preferences, page_number,
                                 item_per_page):
        try:
            query = supabase.table('reports_trash').select(
                "trash_id,deleted_by, deleted_at,report_info,report_id(report_title,category,status,referring_doctor_id!inner(first_name,last_name),patient_id!inner(patient_id,national_id_number,first_name,last_name,patient_age,patient_age_unit,patient_gender,patient_phone_number))",
                count='exact').order("trash_id", desc=True)

            if filter_preferences:
                query = await ReportTrashModel.apply_filter(filter_preferences)

            if search_data:
                query = query.or_(
                    f"deleted_by.ilike.%{search_data}%")

            data, total_count = await paginate(query, item_per_page, page_number)

            if data:
                normalized_data = []
                for trash in data:
                    flattened_data = ReportTrashModel.flatten_data(trash)
                    normalized_data.append(flattened_data)
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
            logger.error(f"Error fetching paginated report trash: {e}")
            return {
                "data": [],
                "total_count": 0,
                "current_page": page_number,
                "prev_page": None,
                "next_page": None,
                "total_pages": 0
            }

    @staticmethod
    def flatten_data(data):
        if data:
            report_info = json.loads(data.pop('report_info'))

            report_id = data.pop('report_id')

            patient_id = report_id.pop('patient_id')
            referring_doctor_id = report_id.pop('referring_doctor_id')

            flattened_data = {**data, **report_info, **report_id, **patient_id, **referring_doctor_id}
            flattened_data['patient'] = flattened_data['patient_first_name'] + ' ' + flattened_data['patient_last_name']

            return flattened_data

    @staticmethod
    async def get_trash_by_id(trash_id):
        try:
            data = await supabase.table('reports_trash').select("*").eq('trash_id', trash_id).execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def put_back(data):
        try:
            data = await supabase.table('reports').update({"deleted_at": None}).eq('report_id', data[
                "report_id"]).execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_trash(data):
        try:
            data = await supabase.table('reports_trash').insert(data).execute()
            if data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_trash(trash_id):
        try:
            data = await supabase.table('reports_trash').delete() \
                .eq('trash_id', trash_id).execute()
            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def apply_filter(data):
        try:
            query = supabase.table('reports_trash').select(
                "trash_id,deleted_by, deleted_at,report_info,report_id!inner(report_title,report_content,status,category,created_at,updated_at,referring_doctor_id!inner(first_name,last_name),patient_id!inner(patient_id,first_name,last_name,national_id_number), appointment_id!inner(appointment_date,doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name))))",
                count='exact')

            if data["status"].get("enabled"):
                query = query.eq('report_id.status',
                                 data["status"].get("report_status_value"))

            if data["national_id_number"].get("enabled"):
                query = query.eq('report_id.patient_id.national_id_number',
                                 data["national_id_number"].get("national_id_number_value"))

            if data["patient"].get("enabled"):
                    query = query.ilike('report_id.patient_id.first_name',
                                        f'%{data["patient"].get("firstname")}%')
                    query = query.ilike('report_id.patient_id.last_name',
                                        f'%{data["patient"].get("lastname")}%')

            if data["doctor"].get("enabled"):
                query = query.ilike('report_id.appointment_id.doctor_service_relation_id.doctor_id.first_name',
                                    f'%{data["doctor"].get("firstname")}%')
                query = query.ilike('report_id.appointment_id.doctor_service_relation_id.doctor_id.last_name',
                                    f'%{data["doctor"].get("lastname")}%')

            if data["referring_doctor"].get("enabled"):
                query = query.ilike(
                    'report_id.referring_doctor_id.first_name',
                    f'%{data["referring_doctor"].get("firstname")}%')
                query = query.ilike(
                    'report_id.referring_doctor_id.last_name',
                    f'%{data["referring_doctor"].get("lastname")}%')

            # Time filter mapping
            time_filters = {
                "last_24_hours": timedelta(hours=-24),
                "last_7_days": timedelta(days=-7),
                "last_14_days": timedelta(days=-14),
                "last_30_days": timedelta(days=-30),
                "next_24_hours": timedelta(hours=24),
                "next_7_days": timedelta(days=7),
                "next_14_days": timedelta(days=14),
                "next_30_days": timedelta(days=30),
            }

            def apply_time_filter(filter_data, field_name):
                nonlocal query

                if filter_data.get("enabled"):
                    if filter_data.get("filteration_type") == "preset_filter":
                        time_delta = time_filters.get(filter_data.get("preset_filter_id"))
                        if time_delta:
                            time_delta = time_filters[filter_data.get("preset_filter_id")]
                            current_time = datetime.now(timezone.utc)

                            if time_delta.total_seconds() < 0:
                                # It's a past filter, calculate the starting pastime
                                start_time = current_time + time_delta
                                query = query.gte(field_name, start_time.isoformat()).lte(field_name,
                                                                                          current_time.isoformat())
                            else:
                                # It's a future filter, calculate the ending future time
                                end_time = current_time + time_delta
                                query = query.gte(field_name, current_time.isoformat()).lte(field_name,
                                                                                            end_time.isoformat())

                    elif filter_data.get("filteration_type") == "range_filter":

                        start_range_filter = filter_data.get("start_range_value")
                        end_range_value = filter_data.get("end_range_value")

                        query = query.gte(field_name, start_range_filter).lte(field_name, end_range_value)

                    elif filter_data.get("filteration_type") == "custom_filter":
                        custom_date_value = filter_data.get("custom_date_value")
                        if custom_date_value:
                            specific_date = datetime.strptime(custom_date_value, "%a %b %d %Y")
                            specific_date_end = specific_date + timedelta(hours=23)  # End of the specific day
                            query = query.gte(field_name, specific_date.strftime("%Y-%m-%d %H:%M:%S")).lte(
                                field_name, specific_date_end.strftime("%Y-%m-%d %H:%M:%S"))

                return query

            if data["appointment_date"].get("enabled"):
                query = apply_time_filter(data.get("appointment_date", {}), 'report_id.appointment_id.appointment_date')

            if data["created_at"].get("enabled"):
                query = apply_time_filter(data.get("created_at", {}), 'deleted_at')

            query = query.order("trash_id")

            return query
        except Exception as e:
            logger.error(f"Error fetching report filtered data ....: {e}")
