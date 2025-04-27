CREATE OR REPLACE FUNCTION user_has_permission(permission_name text)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    user_role_name text;
    has_permission boolean;
BEGIN
    -- Extract the user's role name from the `raw_user_meta_data` JSONB column in the users table
    SELECT u.raw_user_meta_data->>'user_role' INTO user_role_name
    FROM public.users u
    WHERE u.id = auth.uid();

    -- Check if the user's role is associated with the requested permission
    SELECT EXISTS (
        SELECT 1
        FROM permissions p
        JOIN roles_permissions rp ON p.permission_id = rp.permission_id
        JOIN roles r ON rp.role_id = r.role_id
        WHERE r.role_name = user_role_name AND p.permission_slug = user_has_permission.permission_name
    ) INTO has_permission;

    RETURN has_permission;
END;
$$;
