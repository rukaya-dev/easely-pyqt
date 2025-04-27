CREATE
OR REPLACE FUNCTION update_user_password (user_id uuid,
    new_password text) RETURNS void AS $$
BEGIN
    UPDATE users
    SET encrypted_password = new_password
    WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;