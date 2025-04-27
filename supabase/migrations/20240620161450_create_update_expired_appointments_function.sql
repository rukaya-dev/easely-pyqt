CREATE OR REPLACE FUNCTION update_expired_appointments()
RETURNS void AS $$
BEGIN
    UPDATE appointments
    SET appointment_status = 'expired',
        updated_at = now()
    WHERE appointment_date < CURRENT_DATE
      AND appointment_status != 'expired';
END;
$$ LANGUAGE plpgsql;



select cron.schedule('update_expired_appointments_cron_job', '00 * * * *', 'SELECT update_expired_appointments()');