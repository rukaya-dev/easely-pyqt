from datetime import timedelta, datetime

from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger
from utils.utlis import extract_names

logger = set_up_logger('main.services.supabase.models.image.image_model')


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


class ImageModel:
    @staticmethod
    async def get_images_paginate(filter_preferences, page_number, item_per_page):
        try:
            query = (supabase.table('images').select(
                "image_id,image_date,image_time,image_type,created_at,image_status,payment_status,patient_id!inner(patient_id,first_name,last_name,national_id_number), doctor_service_relation_id!inner(doctor_id!inner(first_name,last_name),doctor_service_assistants_relation!inner(assistant_id!inner(first_name,last_name)),doctor_service_cost,doctor_service_duration,service_name)",
                count='exact')
                     .order("image_date").order("image_time"))

            if filter_preferences:
                query = await ImageModel.apply_filter(filter_preferences)

            data, total_count = await paginate(query, item_per_page=item_per_page, page_number=page_number)

            if data:
                normalized_data = []
                for image in data:
                    flattened_patient_data = ImageModel.flatten_patient_data(image['patient_id'])
                    image.update(flattened_patient_data)
                    flattened_doctor_service_data = ImageModel.flatten_doctor_service_data(
                        image['doctor_service_relation_id'])
                    image.update(flattened_doctor_service_data)
                    flattened_doctor_data = ImageModel.flatten_doctor_data(
                        image['doctor_service_relation_id']['doctor_id'])
                    image.update(flattened_doctor_data)
                    image.pop('doctor_service_relation_id')
                    normalized_data.append(image)
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
    async def create_image_in_db(data):
        try:
            data = await supabase.table('images').insert(data).execute()
            if data.data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_image_in_db(image_id, data):
        try:
            data = await supabase.table('images').update(data).eq("image_id", image_id).execute()
            if data.data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def upload_image_to_storage(file_path, file, mime_type):
        try:
            data = await supabase.storage.from_("images").upload(file_path, file,
                                                                 file_options={"content-type": mime_type})
            if data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_image_from_storage(file_path):
        try:
            data = await supabase.storage.from_("images").download(file_path)
            if data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)
