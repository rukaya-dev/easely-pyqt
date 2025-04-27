from datetime import timedelta, datetime, timezone

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger
from utils.utlis import extract_names

logger = set_up_logger('main.services.supabase.models.appointment.appointment_model')


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


class AppointmentModel:
    @staticmethod
    async def get_appointments_paginate(filter_preferences, page_number, item_per_page):
        try:
            query = (supabase.table('appointments').select(
                "appointment_id,appointment_date,appointment_time,appointment_type,created_at,appointment_status,payment_status,patient_id!inner(patient_id,first_name,last_name,national_id_number), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name),doctor_service_assistants_relation!inner(assistant_id!inner(first_name,last_name)),doctor_service_cost,doctor_service_duration,service_name)",
                count='exact')
                     .order("appointment_date", desc=True))

            if filter_preferences:
                query = await AppointmentModel.apply_filter(filter_preferences)

            data, total_count = await paginate(query, item_per_page=item_per_page, page_number=page_number)

            if data:
                normalized_data = []
                for appointment in data:
                    flattened_patient_data = AppointmentModel.flatten_patient_data(appointment['patient_id'])
                    appointment.update(flattened_patient_data)
                    flattened_doctor_service_data = AppointmentModel.flatten_doctor_service_data(
                        appointment['doctor_service_relation_id'])
                    appointment.update(flattened_doctor_service_data)
                    flattened_doctor_data = AppointmentModel.flatten_doctor_data(
                        appointment['doctor_service_relation_id']['doctor_id'])
                    appointment.update(flattened_doctor_data)
                    appointment.pop('doctor_service_relation_id')
                    normalized_data.append(appointment)
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
    async def get_all_appointments_by_year(year):
        try:
            start_date = datetime(int(year), 1, 1)
            end_date = datetime(int(year) + 1, 1, 1)
            data = await supabase.table('appointments').select("*") \
                .gte("created_at", start_date) \
                .lt("created_at", end_date) \
                .execute()

            if data.data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_appointment(data):
        try:
            data = await supabase.table('appointments').insert(data).execute()
            if data.data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_appointment_exist(data):
        try:
            data = await (supabase.table('appointments')
                          .select('*')
                          .eq('appointment_date', data["appointment_date"])
                          .eq('appointment_time', data["appointment_time"])
                          .eq('doctor_service_relation_id', data["doctor_service_relation_id"])
                          .or_(
                'appointment_status.eq.scheduled,appointment_status.eq.re-scheduled')
                          .execute())
            if len(data.data) > 0:
                return data.data
            return None
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_any_taken_doctor_service_time_slots(date, doctor_service_relation_id):
        try:
            data = await (supabase.table('appointments')
                          .select('*')
                          .eq('appointment_date', date)
                          .eq('doctor_service_relation_id', doctor_service_relation_id)
                          .or_(
                'appointment_status.eq.scheduled,appointment_status.eq.re-scheduled')
                          .execute())
            if len(data.data) > 0:
                return data.data
            return None
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_appointment(appointment_id):
        try:
            data = await supabase.table('appointments').delete().eq('appointment_id',
                                                                    appointment_id).execute()

            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_appointment(appointment_id, data):
        try:
            data = await supabase.table('appointments').update(data).eq('appointment_id',
                                                                        appointment_id).execute()
            if data.data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_appointment_exist(appointment_id, appointment_date, appointment_time):
        try:
            data = await (supabase.table('appointments').select('appointment_date, appointment_time')
                          .neq('appointment_id', appointment_id)
                          .eq('appointment_date', appointment_date)
                          .eq('appointment_time', appointment_time)
                          .execute())

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_appointment_by_id(appointment_id):
        try:
            data = await supabase.table('appointments').select(
                "appointment_id,appointment_date,appointment_time,appointment_type,reason_for_visit,appointment_status,notes,check_in_time,check_out_time,cancellation_date,cancellation_time,re_scheduled_date,re_scheduled_time,payment_status,created_at,updated_at,patient_id!inner(patient_id,first_name,last_name,national_id_number,patient_age,patient_age_unit,patient_gender,patient_clinical_data), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name),doctor_service_cost,doctor_service_duration,service_name)") \
                .eq('appointment_id', appointment_id) \
                .execute()

            if data.data:
                appointment = data.data[0]
                flattened_patient_data = AppointmentModel.flatten_patient_data(appointment['patient_id'])
                appointment.update(flattened_patient_data)
                flattened_doctor_service_data = AppointmentModel.flatten_doctor_service_data(
                    appointment['doctor_service_relation_id'])
                appointment.update(flattened_doctor_service_data)
                flattened_doctor_data = AppointmentModel.flatten_doctor_data(
                    appointment['doctor_service_relation_id']['doctor_id'])
                appointment.update(flattened_doctor_data)
                appointment.pop('doctor_service_relation_id')

                return appointment
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_appointment_data_for_billing(appointment_id):
        try:
            data = await supabase.table('appointments').select(
                "appointment_id,appointment_date,appointment_time,appointment_type,patient_id!inner(patient_id,first_name,last_name,patient_address,patient_email,patient_phone_number,insurance_provider,insurance_policy_number,coverage_percentage), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name),doctor_service_cost,service_name)") \
                .eq('appointment_id', appointment_id) \
                .execute()

            if data.data:
                appointment = data.data[0]
                flattened_patient_data = AppointmentModel.flatten_patient_data(appointment['patient_id'])
                appointment.update(flattened_patient_data)
                flattened_doctor_service_data = AppointmentModel.flatten_doctor_service_data(
                    appointment['doctor_service_relation_id'])
                appointment.update(flattened_doctor_service_data)
                flattened_doctor_data = AppointmentModel.flatten_doctor_data(
                    appointment['doctor_service_relation_id']['doctor_id'])
                appointment.update(flattened_doctor_data)
                appointment.pop('doctor_service_relation_id')

                return appointment
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_appointment_status_by_id(appointment_id):
        try:
            data = await supabase.table('appointments').select(
                "appointment_id,appointment_status") \
                .eq('appointment_id', appointment_id) \
                .execute()

            return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_appointment_additional_data_by_id(appointment_id):
        try:
            data = await supabase.table('appointments').select(
                "appointment_id,appointment_type,check_in_time,check_out_time,reason_for_visit,notes") \
                .eq('appointment_id', appointment_id) \
                .execute()

            return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_appointment_status_or_additional_data(appointment_id, data):
        try:
            data = await supabase.table('appointments').update(data).eq('appointment_id', appointment_id).execute()

            return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def apply_filter(data):
        try:
            query = supabase.table('appointments').select(
                "appointment_id,appointment_date,appointment_time,appointment_type,created_at,appointment_status,payment_status,patient_id!inner(patient_id,first_name,last_name,national_id_number), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name),doctor_service_assistants_relation!inner(assistant_id!inner(first_name,last_name)),doctor_service_cost,doctor_service_duration,service_name)",
                count='exact')

            if data["service_name"].get("enabled"):
                query = query.eq('doctor_service_relation_id.service_name',
                                 data["service_name"].get("service_name_value"))

            if data["appointment_status"].get("enabled"):
                query = query.eq('appointment_status',
                                 data["appointment_status"].get("appointment_status_value"))

            if data["appointment_time"].get("enabled"):
                query = query.eq('appointment_time', data["appointment_time"].get("time_slot_value"))

            if data["national_id_number"].get("enabled"):
                query = query.eq('patient_id.national_id_number',
                                 data["national_id_number"].get("national_id_number_value"))

            if data["patient"].get("enabled"):
                query = query.ilike('patient_id.first_name',
                                    f'%{data["patient"].get("firstname")}%')
                query = query.ilike('patient_id.last_name',
                                    f'%{data["patient"].get("lastname")}%')

            if data["doctor"].get("enabled"):
                query = query.ilike('doctor_service_relation_id.doctor_id.first_name',
                                    f'%{data["doctor"].get("firstname")}%')
                query = query.ilike('doctor_service_relation_id.doctor_id.last_name',
                                    f'%{data["doctor"].get("lastname")}%')

            if data["assistant"].get("enabled"):
                query = query.ilike(
                    'doctor_service_relation_id.doctor_service_assistants_relation.assistant_id.first_name',
                    f'%{data["assistant"].get("firstname")}%')
                query = query.ilike(
                    'doctor_service_relation_id.doctor_service_assistants_relation.assistant_id.last_name',
                    f'%{data["assistant"].get("lastname")}%')

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
                query = apply_time_filter(data.get("appointment_date", {}), 'appointment_date')

            if data["created_at"].get("enabled"):
                query = apply_time_filter(data.get("created_at", {}), 'created_at')

            if data["updated_at"].get("enabled"):
                query = apply_time_filter(data.get("updated_at", {}), 'updated_at')

            query = query.order("appointment_id")

            return query
        except Exception as e:
            logger.error(f"Error fetching appointment filtered data ....: {e}")

    @staticmethod
    async def search_appointments(search_data):
        try:
            data = await supabase.rpc("search_appointments",
                                      params={"search_data": search_data, "limit_data": 20}).execute()

            if data.data:
                normalized_data = []
                for appointment in data.data:
                    flattened_doctor_data = {
                        "doctor_name": appointment["doctor_first_name"] + " " + appointment["doctor_last_name"]}
                    appointment.update(flattened_doctor_data)
                    normalized_data.append(appointment)

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
            'patient_first_name': data['first_name'],
            'patient_last_name': data['last_name'],
        }

        if "national_id_number" in data:
            patient["patient_national_id_number"] = data["national_id_number"]

        if "patient_age" in data:
            patient["patient_age"] = data["patient_age"]

        if "patient_age_unit" in data:
            patient["patient_age_unit"] = data["patient_age_unit"]

        if "patient_gender" in data:
            patient["patient_gender"] = data["patient_gender"]

        if "patient_clinical_data" in data:
            patient["patient_clinical_data"] = data["patient_clinical_data"]

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
    def flatten_doctor_service_data(data):
        doctor_service = {
            'service_name': data['service_name'],
            'doctor_service_cost': data['doctor_service_cost'],
        }
        if "doctor_service_duration" in data:
            doctor_service["doctor_service_duration"] = data['doctor_service_duration']

        return doctor_service

    @staticmethod
    def flatten_doctor_data(data):
        return {
            'doctor_name': data['first_name'] + " " + data['last_name']
        }

    @staticmethod
    def flatten_assistant_data(data):
        assistants = []
        for assistant in data:
            assistants.append({
                'first_name': assistant['first_name'], "last_name": assistant['last_name']
            })

    @staticmethod
    async def get_upcoming_sessions():
        current_time_plus_two_hours = datetime.now().time().strftime('%H:%M:00')
        try:
            data = await supabase.table('appointments').select(
                "appointment_id,appointment_date,appointment_time,appointment_type,notes,appointment_status,patient_id!inner(patient_id,first_name,last_name,national_id_number), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name),doctor_service_cost,doctor_service_duration,service_name)",
                count='exact') \
                .eq("appointment_date", datetime.now()) \
                .eq("appointment_status", "scheduled") \
                .gte("appointment_time", current_time_plus_two_hours) \
                .order("appointment_time") \
                .limit(10) \
                .execute()
            if data:
                normalized_data = []
                for appointment in data.data:
                    flattened_patient_data = AppointmentModel.flatten_patient_data(appointment['patient_id'])
                    appointment.update(flattened_patient_data)
                    flattened_doctor_service_data = AppointmentModel.flatten_doctor_service_data(
                        appointment['doctor_service_relation_id'])
                    appointment.update(flattened_doctor_service_data)
                    flattened_doctor_data = AppointmentModel.flatten_doctor_data(
                        appointment['doctor_service_relation_id']['doctor_id'])
                    appointment.update(flattened_doctor_data)
                    appointment.pop('doctor_service_relation_id')
                    normalized_data.append(appointment)
                data = normalized_data

            return data
        except Exception as e:
            logger.error(f"Error fetching appointment upcoming sessions data ....: {e}", exc_info=True)

    @staticmethod
    async def apply_preset_filter(filter_id, item_per_page, page_number):
        current_time_plus_two_hours = datetime.now().time().strftime('%H:%M:00')
        try:
            query = supabase.table('appointments').select(
                "appointment_id,appointment_date,appointment_time,appointment_type,notes,appointment_status,created_at,patient_id!inner(patient_id,first_name,last_name,national_id_number), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name),doctor_service_cost,doctor_service_duration,service_name)",
                count='exact')

            if filter_id == "scheduled":
                query = query.or_(
                    'appointment_status.eq.scheduled,appointment_status.eq.re-scheduled') \
                    .order("appointment_date", desc=True)

            elif filter_id == "upcoming":
                query = query.eq("appointment_date", datetime.now()) \
                    .or_(
                    'appointment_status.eq.scheduled,appointment_status.eq.re-scheduled') \
                    .gte("appointment_time", current_time_plus_two_hours) \
                    .order("appointment_time")

            elif filter_id == "canceled":
                query = query.eq("appointment_status", "canceled").order("appointment_date", desc=True)

            elif filter_id == "expired":
                query = query.eq("appointment_status", "expired").order("appointment_date", desc=True)

            query = query.order("appointment_date", desc=True)

            data, total_count = await paginate(query, item_per_page=item_per_page, page_number=page_number)
            if data:
                normalized_data = []
                for appointment in data:
                    flattened_patient_data = AppointmentModel.flatten_patient_data(appointment['patient_id'])
                    appointment.update(flattened_patient_data)
                    flattened_doctor_service_data = AppointmentModel.flatten_doctor_service_data(
                        appointment['doctor_service_relation_id'])
                    appointment.update(flattened_doctor_service_data)
                    flattened_doctor_data = AppointmentModel.flatten_doctor_data(
                        appointment['doctor_service_relation_id']['doctor_id'])
                    appointment.update(flattened_doctor_data)
                    appointment.pop('doctor_service_relation_id')
                    normalized_data.append(appointment)

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
