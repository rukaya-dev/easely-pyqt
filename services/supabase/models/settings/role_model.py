from configs.supa_base_configs import supabase
from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.services.supabase.models.role_model')


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


class RoleModel:
    @staticmethod
    async def get_roles_paginate(page_number, item_per_page):
        try:
            query = supabase.table('roles') \
                .select('role_id, role_name, roles_permissions!inner(*, permissions!inner(*))', count='exact') \
                .order('role_id', desc=True)
            data, total_count = await paginate(query, item_per_page, page_number)

            # Transformation to only include permission_name array for each role
            transformed_data = []
            for role in data:
                if role["role_name"] != "superadmin":
                    permissions = [rp['permissions']['permission_name'] for rp in role['roles_permissions']]
                    transformed_data.append({
                        'role_id': role['role_id'],
                        'role_name': role['role_name'],
                        'permissions': ', '.join(permissions)
                    })

            # Result
            # Calculate total pages
            total_pages = (total_count + item_per_page - 1) // item_per_page

            # Calculate prev and next page numbers
            prev_page = page_number - 1 if page_number > 1 else None
            next_page = page_number + 1 if page_number < total_pages else None

            return {
                "data": transformed_data,
                "total_count": total_count,
                "current_page": page_number,
                "prev_page": prev_page,
                "next_page": next_page,
                "total_pages": total_pages
            }
        except Exception as e:
            logger.error(f"Error fetching paginated roles: {e}")
            return {
                "data": [],
                "total_count": 0,
                "current_page": page_number,
                "prev_page": None,
                "next_page": None,
                "total_pages": 0
            }

    @staticmethod
    async def get_role_by_name(role_name):
        try:
            data = await supabase.table('roles') \
                .select('role_id, role_name, roles_permissions!inner(*, permissions!inner(*))') \
                .order('role_id', desc=True) \
                .eq('role_name', role_name).execute()
            return data.data
        except Exception as e:
            logger.error(f"Error fetching paginated roles: {e}")

    @staticmethod
    async def get_role_by_id(role_id):
        try:
            data = await supabase.from_('roles') \
                .select(
                'role_id, role_name, description, roles_permissions!inner(*, permissions!inner(permission_id, permission_name, permission_slug, description))') \
                .eq('role_id', role_id) \
                .order('role_id', desc=True) \
                .execute()
            if data.data:
                return data.data[0]

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_role(data):
        try:
            data = await supabase.table('roles').insert(data).execute()
            if data:
                return data.data

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def create_role_permissions(data):
        try:
            data = await supabase.table('roles_permissions').insert(data).execute()
            if data:
                return data.data

        except Exception as e:
            logger.exception(e)

    @staticmethod
    async def delete_role_permissions(role_id):
        try:
            data = await supabase.table('roles_permissions').delete().eq('role_id', role_id).execute()
            if data.data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_role_exist(name):
        try:
            data = await supabase.table('roles').select('role_name').eq('role_name', name).execute()
            if len(data.data) > 0:
                return True
            return False
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def delete_role(role_id):
        try:
            res = await supabase.table('roles').delete().eq('role_id', role_id).execute()
            if res:
                return True
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def update_role(role_id, data):
        try:
            data = await supabase.table('roles').update(data).eq('role_id', role_id).execute()
            if data.data:
                return data
        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def check_if_updated_role_exist(role_id, role_name):
        try:
            data = await supabase.table('roles').select('role_name') \
                .neq('role_id', role_id). \
                eq('role_name', role_name) \
                .execute()

            if len(data.data) > 0:
                return True

            return False

        except Exception as e:
            logger.error(e, exc_info=True)

    @staticmethod
    async def get_all_permissions():
        try:
            data = await supabase.table('permissions').select("*").execute()
            if data.data:
                return data.data
        except Exception as e:
            logger.error(e, exc_info=True)
