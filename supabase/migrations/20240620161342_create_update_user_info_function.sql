CREATE OR REPLACE FUNCTION update_user_info(
    user_id uuid,
    update_user_id uuid,
    new_email character varying,
    new_raw_user_meta_data jsonb
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF (SELECT count(*)
        FROM public.users u
        WHERE u.id = user_id AND (u.raw_user_meta_data ->> 'user_role')::text = 'superadmin') = 0 THEN
        RAISE EXCEPTION 'Unauthorized access. Only super_admin allowed for this operation.';
    END IF;

    UPDATE public.users
    SET
        email = new_email,
        raw_user_meta_data = new_raw_user_meta_data,
        updated_at = now()
    WHERE id = update_user_id;

END;
$$;
