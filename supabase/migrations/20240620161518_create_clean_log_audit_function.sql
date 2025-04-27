
CREATE OR REPLACE FUNCTION cleanup_log_audit()
RETURNS void AS $$
BEGIN
    DELETE FROM log_audit;
END;
$$ LANGUAGE plpgsql;


select cron.schedule('weekly_log_audit_cleanup_cron_job', '0 0 * * 0', 'SELECT cleanup_log_audit()');