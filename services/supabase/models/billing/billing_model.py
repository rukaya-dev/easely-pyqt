from datetime import timedelta, datetime, timezone

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger
from utils.utlis import extract_names

logger = set_up_logger('main.services.supabase.models.billing.billing_model')


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


class BillingModel:
    @staticmethod
    async def get_billings_paginate(search_text, filter_preferences, page_number, item_per_page):
        try:
            query = (supabase.table('billings').select(
                "*, patient_id!inner(patient_id,first_name,last_name,national_id_number,patient_address,patient_phone_number), appointment_id!inner(appointment_id)",
                count='exact').order("billing_id", desc=True))

            if filter_preferences:
                query = await BillingModel.apply_filter(filter_preferences)

            if search_text:
                query = query.or_(
                    f"payment_method.ilike.%{search_text}%,insurance_policy_number.ilike.%{search_text}%,insurance_provider.ilike.%{search_text}%")

            data, total_count = await paginate(query, item_per_page=item_per_page, page_number=page_number)

            if data:
                normalized_data = []
                for billing in data:
                    flattened_patient_data = BillingModel.flatten_patient_data(billing['patient_id'])
                    billing.update(flattened_patient_data)
                    normalized_data.append(billing)
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
            logger.error(e, exc_info=True)
            return {
                "data": [],
                "total_count": 0,
                "current_page": page_number,
                "prev_page": None,
                "next_page": None,
                "total_pages": 0
            }

    @staticmethod
    async def create_billing(data):
        try:
            data = await supabase.table('billings').insert(data).execute()
            if data.data:
                return data.data[0]
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_billing_exist(data):
        try:
            data = await (supabase.table('billings')
                          .select('*')
                          .eq('billing_date', data["billing_date"])
                          .eq('billing_time', data["billing_time"])
                          .eq('doctor_service_relation_id', data["doctor_service_relation_id"])
                          .or_(
                'billing_status.eq.scheduled,billing_status.eq.re-scheduled')
                          .execute())
            if len(data.data) > 0:
                return data.data
            return None
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_any_taken_doctor_service_time_slots(date, doctor_service_relation_id):
        try:
            data = await (supabase.table('billings')
                          .select('*')
                          .eq('billing_date', date)
                          .eq('doctor_service_relation_id', doctor_service_relation_id)
                          .or_(
                'billing_status.eq.scheduled,billing_status.eq.re-scheduled')
                          .execute())
            if len(data.data) > 0:
                return data.data
            return None
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_billing(billing_id):
        try:
            data = await supabase.table('billings').delete().eq('billing_id',
                                                                billing_id).execute()

            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_billing(billing_id, data):
        try:
            data = await supabase.table('billings').update(data).eq('billing_id',
                                                                    billing_id).execute()
            if data.data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def cancel_billing(billing_id, data):
        try:
            data = await supabase.table('billings').update(data).eq('billing_id',
                                                                    billing_id).execute()
            if data.data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_billing_exist(billing_id, billing_date, billing_time):
        try:
            data = await (supabase.table('billings').select('billing_date, billing_time')
                          .neq('billing_id', billing_id)
                          .eq('billing_date', billing_date)
                          .eq('billing_time', billing_time)
                          .execute())

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_billing_by_id(billing_id):
        try:
            data = await supabase.table('billings').select(
                "*,patient_id!inner(patient_id,first_name,last_name,national_id_number,patient_address,patient_phone_number), appointment_id!inner(doctor_service_relation_id!inner(service_name,doctor_service_duration,doctor_id!inner(first_name,last_name)),appointment_id,appointment_date,appointment_time)") \
                .eq('billing_id', billing_id) \
                .execute()

            if data.data:
                billing = data.data[0]

                flattened_patient_data = BillingModel.flatten_patient_data(billing['patient_id'])
                billing.update(flattened_patient_data)

                flattened_appointment_data = BillingModel.flatten_appointment_data(
                    billing['appointment_id'])
                billing.update(flattened_appointment_data)
                return billing
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_all_billings_by_year(year):
        try:
            start_date = datetime(int(year), 1, 1)
            end_date = datetime(int(year) + 1, 1, 1)
            data = await supabase.table('billings').select("*") \
                .gte("billing_date", start_date) \
                .lt("billing_date", end_date) \
                .execute()

            if data.data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def apply_filter(data):
        try:
            query = supabase.table('billings').select(
                "*, patient_id!inner(patient_id,first_name,last_name,national_id_number), appointment_id!inner(doctor_service_relation_id!inner(service_name),appointment_date,appointment_time)",
                count='exact')

            if data["service_name"].get("enabled"):
                query = query.eq('appointment_id.doctor_service_relation_id.service_name',
                                 data["service_name"].get("service_name_value"))

            if data["appointment_time"].get("enabled"):
                query = query.eq('appointment_id.appointment_time', data["appointment_time"].get("time_slot_value"))

            if data["national_id_number"].get("enabled"):
                query = query.eq('patient_id.national_id_number',
                                 data["national_id_number"].get("national_id_number_value"))

            if data["patient"].get("enabled"):
                query = query.ilike('patient_id.first_name',
                                    f'%{data["patient"].get("firstname")}%')
                query = query.ilike('patient_id.last_name',
                                    f'%{data["patient"].get("lastname")}%')

            if data["total_amount"].get("enabled"):
                query = query.eq('total_amount',
                                 data["total_amount"].get("amount"))

            if data["discount"].get("enabled"):
                query = query.eq('coverage_percentage',
                                 data["discount"].get("amount"))

            if data["net_amount"].get("enabled"):
                query = query.eq('net_amount',
                                 data["net_amount"].get("amount"))

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
                query = apply_time_filter(data.get("appointment_date", {}), 'appointment_id.appointment_date')

            if data["billing_date"].get("enabled"):
                query = apply_time_filter(data.get("billing_date", {}), 'billing_date')

            query = query.order("billing_id")

            return query
        except Exception as e:
            logger.error(f"Error fetching billing filtered data ....: {e}")

    @staticmethod
    def flatten_patient_data(data):

        patient = {
            'patient_id': data['patient_id'],
            'patient_name': data['first_name'] + " " + data['last_name'],
            'patient_national_id_number': data['national_id_number'],
        }
        if "patient_address" in data:
            patient['patient_address'] = data['patient_address']

        if "patient_phone_number" in data:
            patient['patient_phone_number'] = data['patient_phone_number']

        return patient

    @staticmethod
    def flatten_appointment_data(data):
        appointment = {
            'appointment_date': data['appointment_date'],
            'appointment_time': data['appointment_time'],
            'service_name': data["doctor_service_relation_id"]["service_name"],
            'service_duration': data["doctor_service_relation_id"]["doctor_service_duration"],
            'doctor_name': data["doctor_service_relation_id"]["doctor_id"]["first_name"] +
                           " " + data["doctor_service_relation_id"]["doctor_id"]["last_name"],
            "appointment_id": data["appointment_id"]
        }
        return appointment
