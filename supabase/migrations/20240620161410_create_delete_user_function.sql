CREATE OR REPLACE FUNCTION delete_user (
  user_id UUID,
  user_email TEXT,
  deleted_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
  -- Validate ID and authorization
  IF (SELECT count(*)
      FROM public.users u
      WHERE u.id = user_id AND (u.raw_user_meta_data ->> 'user_role')::text = 'superadmin') = 0 THEN
    RAISE EXCEPTION 'Unauthorized access. Only super_admin allowed for this operation.';
  END IF;

  DELETE FROM public.users
  WHERE id = deleted_id;

  -- You can perform additional actions after deleting the user if needed

END;
$$
SECURITY DEFINER;
