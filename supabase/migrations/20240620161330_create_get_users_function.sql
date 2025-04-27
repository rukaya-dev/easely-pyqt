CREATE OR REPLACE FUNCTION get_users(user_id uuid, user_email text)
RETURNS TABLE (
    id uuid,
    email character varying,
    aud character varying,
    raw_user_meta_data jsonb,
    email_confirmed_at timestamp with time zone,
    created_at timestamp with time zone,
    deleted_at timestamp with time zone,
    updated_at timestamp with time zone,
    confirmed_at timestamp with time zone,
    last_sign_in_at timestamp with time zone
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Validate ID and authorization
  IF (SELECT count(*)
      FROM public.users u
      WHERE u.id = user_id AND (u.raw_user_meta_data ->> 'user_role')::text = 'superadmin') = 0 THEN
    RAISE EXCEPTION 'Unauthorized access. Only super_admin allowed for this operation.';
  END IF;

  RETURN QUERY
  SELECT
    u.id,
    u.email,
    u.aud,
    u.raw_user_meta_data,
    u.email_confirmed_at,
    u.created_at,
    u.deleted_at,
    u.updated_at,
    u.confirmed_at,
    u.last_sign_in_at
  FROM public.users AS u
  ORDER BY u.created_at DESC;
END;
$$;

