
from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.report_workshop.category_model')


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


class CategoryModel:
    @staticmethod
    async def get_categories_paginate(search_text, page_number, item_per_page):
        try:
            query = supabase.table('categories').select("*", count='exact') \
                .order("category_id", desc=True)

            if search_text:
                query = query.or_(f"name.ilike.%{search_text}%,description.ilike.%{search_text}%")

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
    async def get_category_by_id(category_id):
        try:
            data = await supabase.table('categories').select("*").eq('category_id', category_id) \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_category(data):
        try:
            data = await supabase.table('categories').insert(data).execute()
            if data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_category_exist(name):
        try:
            data = await supabase.table('categories').select('name').eq('name', name).execute()
            if len(data.data) > 0:
                return True
            return False
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_category(category_id):
        try:
            data = await supabase.table('categories').delete() \
                .eq('category_id', category_id).execute()
            if data.data:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_category(category_id, data):
        try:
            data = await supabase.table('categories').update(data).eq('category_id', category_id).execute()
            if data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_category_exist(category_id, category_name):
        try:
            data = await supabase.table('categories').select('name') \
                .neq('category_id', category_id). \
                eq('name', category_name) \
                .execute()

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_all_categories():
        try:
            data = await supabase.table('categories').select("*").order("created_at", desc=True) \
                .execute()
            if data.data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)
