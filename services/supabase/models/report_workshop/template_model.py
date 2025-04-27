from datetime import datetime, timedelta
from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.report_workshop.template_model')


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


class TemplateModel:
    @staticmethod
    async def get_templates_paginate(search_text, filter_preferences, page_number, item_per_page):
        try:
            query = supabase.table('templates').select("*", count='exact') \
                .order("template_id", desc=True)

            if search_text:
                query = query.or_(f"name.ilike.%{search_text}%,category_id.ilike.%{search_text}%")

            if filter_preferences:
                query = await TemplateModel.apply_filter(filter_preferences)

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
    async def get_template_by_id(template_id):
        try:
            data = await supabase.table('templates').select("*").eq('template_id', template_id) \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_template_by_name(template_name):
        try:
            data = await supabase.table('templates').select("*").eq('name', template_name) \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_template(data):
        try:
            data = await supabase.table('templates').insert(data).execute()
            if data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_template_exist(data):
        try:
            data = await supabase.table('templates').select('name').eq('name', data["name"]).execute()
            if len(data.data) > 0:
                return True
            return False
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_template(template_id):
        try:
            data = await supabase.table('templates').delete() \
                .eq('template_id', template_id).execute()
            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_template(template_id, data):
        try:
            data = await supabase.table('templates').update(data).eq('template_id', template_id).execute()
            if data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_template_exist(template_id, data):
        try:
            data = await supabase.table('templates').select('name') \
                .neq('template_id', template_id). \
                eq('name', data["name"]) \
                .execute()

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def apply_filter(data):
        try:
            query = supabase.table('templates').select(
                "*",
                count='exact')

            if data["category"].get("enabled"):
                query = query.eq('category_id', data["category"].get("category_value"))

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

            query = query.order("template_id", desc=True)

            return query
        except Exception as e:
            logger.error(f"Error fetching doctors filtered data ....: {e}")

    @staticmethod
    async def get_all_templates_by_category(category_id):
        try:
            data = await supabase.table('templates').select("*").eq('category_id', category_id) \
                .execute()
            if data.data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)
