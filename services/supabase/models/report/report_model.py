from datetime import timedelta, datetime, timezone

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger
from utils.utlis import extract_names

logger = set_up_logger('main.services.supabase.models.report.report_model')


async def paginate(query, page_number=1, item_per_page=15):
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


class ReportModel:
    @staticmethod
    async def get_reports_paginate(filter_preferences, page_number, item_per_page):
        try:
            query = supabase.table('reports').select(
                "report_id,report_title,status,category,created_at,updated_at,patient_id!inner(patient_id,first_name,last_name,patient_gender,patient_age,patient_age_unit,national_id_number), appointment_id!inner(appointment_date)",
                count='exact').is_("deleted_at", 'null').order("created_at")

            if filter_preferences:
                query = await ReportModel.apply_filter(filter_preferences)

            data, total_count = await paginate(query, item_per_page=item_per_page, page_number=page_number)

            if data:
                normalized_data = []
                for report in data:
                    flattened_patient_data = ReportModel.flatten_patient_data(report['patient_id'])
                    report.update(flattened_patient_data)
                    flattened_appointment_data = ReportModel.flatten_appointment_data(
                        report['appointment_id'])
                    report.update(flattened_appointment_data)
                    flattened_referring_doctor_data = ReportModel.flatten_referring_doctor_data(
                        report['referring_doctor_id'])
                    report.update(flattened_referring_doctor_data)
                    normalized_data.append(report)
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
    async def get_all_reports_by_year(year):
        try:
            start_date = datetime(int(year), 1, 1)
            end_date = datetime(int(year) + 1, 1, 1)
            data = await supabase.table('reports').select("*") \
                .gte("created_at", start_date) \
                .lt("created_at", end_date) \
                .is_("deleted_at", 'null') \
                .execute()

            if data.data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_report(data):
        try:
            data = await supabase.table('reports').insert(data).execute()
            if data.data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_report(report_id):
        try:
            data = await supabase.table('reports').update({"deleted_at": datetime.now().isoformat()}).eq('report_id',
                                                                                                         report_id).execute()

            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_report(report_id, data):
        try:
            data = await supabase.table('reports').update(data).eq('report_id',
                                                                   report_id).execute()
            if data.data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_report_by_id(report_id):
        try:
            data = await supabase.rpc("get_report_by_id", params={"p_report_id": report_id}).execute()

            if data.data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_report_status_by_id(report_id):
        try:
            data = await supabase.table('reports').select(
                "report_id,status") \
                .eq('report_id', report_id) \
                .execute()

            return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def apply_filter(data):
        try:
            query = supabase.table('reports').select(
                "report_id,report_title,report_content,status,category,created_at,updated_at,referring_doctor_id!inner(first_name,last_name),patient_id!inner(patient_id,first_name,last_name,national_id_number), appointment_id!inner(appointment_date,doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name)))",
                count='exact').is_("deleted_at", 'null')

            if data["status"].get("enabled"):
                query = query.eq('status',
                                 data["status"].get("report_status_value"))

            if data["national_id_number"].get("enabled"):
                query = query.eq('patient_id.national_id_number',
                                 data["national_id_number"].get("national_id_number_value"))

            if data["patient"].get("enabled"):
                query = query.ilike('patient_id.first_name',
                                    f'%{data["patient"].get("firstname")}%')
                query = query.ilike('patient_id.last_name',
                                    f'%{data["patient"].get("lastname")}%')

            if data["doctor"].get("enabled"):
                query = query.ilike('appointment_id.doctor_service_relation_id.doctor_id.first_name',
                                    f'%{data["doctor"].get("firstname")}%')
                query = query.ilike('appointment_id.doctor_service_relation_id.doctor_id.last_name',
                                    f'%{data["doctor"].get("lastname")}%')

            if data["referring_doctor"].get("enabled"):
                query = query.ilike(
                    'referring_doctor_id.first_name',
                    f'%{data["referring_doctor"].get("firstname")}%')
                query = query.ilike(
                    'referring_doctor_id.last_name',
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

            # Apply filters for created_at and updated_at

            if data["appointment_date"].get("enabled"):
                query = apply_time_filter(data.get("appointment_date", {}), 'appointment_id.appointment_date')

            if data["created_at"].get("enabled"):
                query = apply_time_filter(data.get("created_at", {}), 'created_at')

            if data["updated_at"].get("enabled"):
                query = apply_time_filter(data.get("updated_at", {}), 'updated_at')

            query = query.order("report_id")

            return query
        except Exception as e:
            logger.error(f"Error fetching report filtered data ....: {e}")

    @staticmethod
    async def search_reports(search_data):
        try:
            data = await supabase.rpc("search_reports",
                                      params={"search_data": search_data, "limit_data": 20}).execute()

            if data.data:
                normalized_data = []
                for report in data.data:
                    flattened_patient_data = {
                        "patient_name": report["patient_first_name"] + " " + report["patient_last_name"]}
                    report.update(flattened_patient_data)
                    normalized_data.append(report)

                return {
                    "data": normalized_data,
                    "total_count": 20,
                    "current_page": 1,
                    "prev_page": 0,
                    "next_page": 0,
                    "total_pages": 1
                }
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    def flatten_patient_data(data):
        patient = {
            'patient_id': data['patient_id'],
            'patient_name': data['first_name'] + " " + data['last_name'],
        }

        if "national_id_number" in data:
            patient["patient_national_id_number"] = data["national_id_number"]

        if "patient_gender" in data:
            patient["patient_gender"] = data["patient_gender"]

        if "patient_age" in data:
            patient["patient_age"] = data["patient_age"]

        if "patient_age_unit" in data:
            patient["patient_age_unit"] = data["patient_age_unit"]

        if "patient_address" in data:
            patient["patient_address"] = data["patient_address"]

        if "patient_email" in data:
            patient["patient_email"] = data["patient_email"]

        if "patient_phone_number" in data:
            patient["patient_phone_number"] = data["patient_phone_number"]

        if "insurance_provider" in data:
            patient["insurance_provider"] = data["insurance_provider"]

        if "insurance_policy_number" in data:
            patient["insurance_policy_number"] = data["insurance_policy_number"]

        if "coverage_percentage" in data:
            patient["coverage_percentage"] = data["coverage_percentage"]

        return patient

    @staticmethod
    def flatten_appointment_data(data):
        doctor_service = {
            'appointment_date': data['appointment_date'],
        }

        return doctor_service

    @staticmethod
    def flatten_referring_doctor_data(data):
        return {
            'referring_doctor_name': data['first_name'] + " " + data['last_name']
        }

    @staticmethod
    async def get_upcoming_sessions():
        current_time_plus_two_hours = datetime.now().time().strftime('%H:%M:00')
        try:
            data = await supabase.table('reports').select(
                "report_id,report_date,report_time,report_type,notes,report_status,patient_id!inner(patient_id,first_name,last_name,national_id_number), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name))",
                count='exact') \
                .eq("report_date", datetime.now()) \
                .eq("report_status", "scheduled") \
                .gte("report_time", current_time_plus_two_hours) \
                .order("report_time") \
                .limit(6) \
                .execute()
            if data:
                normalized_data = []
                for report in data.data:
                    flattened_patient_data = ReportModel.flatten_patient_data(report['patient_id'])
                    report.update(flattened_patient_data)
                    flattened_doctor_service_data = ReportModel.flatten_doctor_service_data(
                        report['doctor_service_relation_id'])
                    report.update(flattened_doctor_service_data)
                    flattened_doctor_data = ReportModel.flatten_doctor_data(
                        report['doctor_service_relation_id']['doctor_id'])
                    report.update(flattened_doctor_data)
                    report.pop('doctor_service_relation_id')
                    normalized_data.append(report)
                data = normalized_data

            return data
        except Exception as e:
            logger.error(f"Error fetching report upcoming sessions data ....: {e}", exc_info=True)

    @staticmethod
    async def apply_preset_filter(filter_id, item_per_page, page_number):
        try:
            query = supabase.table('reports').select(
                "report_id,report_title,status,category,created_at,updated_at,patient_id!inner(patient_id,first_name,last_name,patient_gender,patient_age,patient_age_unit,national_id_number), appointment_id!inner(appointment_date)",
                count='exact').is_("deleted_at", 'null')

            if filter_id == "recent":
                query = query.order("created_at", desc=True).limit(5)

            if filter_id == "drafted":
                query = query.eq('status', 'Drafted').order("created_at", desc=True)

            elif filter_id == "finalized":
                query = query.eq("status", "Finalized").order("created_at", desc=True)

            elif filter_id == "archived":
                query = query.eq("status", "Archived").order("created_at", desc=True)

            else:
                query = query.order("created_at", desc=True)

            data, total_count = await paginate(query, item_per_page=item_per_page, page_number=page_number)

            if data:
                normalized_data = []
                for report in data:
                    flattened_patient_data = ReportModel.flatten_patient_data(report['patient_id'])
                    report.update(flattened_patient_data)

                    flattened_appointment_data = ReportModel.flatten_appointment_data(
                        report['appointment_id'])
                    report.update(flattened_appointment_data)
                    report.pop('appointment_id')

                    normalized_data.append(report)
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
            logger.error(f"Error fetching paginated items: {e}", exc_info=True)
            return {
                "data": [],
                "total_count": 0,
                "current_page": page_number,
                "prev_page": None,
                "next_page": None,
                "total_pages": 0
            }
