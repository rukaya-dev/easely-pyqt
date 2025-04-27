CREATE OR REPLACE FUNCTION get_report_by_id(p_report_id int)
RETURNS TABLE (
    report_id int,
    report_title varchar,
    report_content text,
    status varchar,
    category varchar,
    created_at timestamptz,
    updated_at timestamptz,
    referring_doctor_first_name varchar,
    referring_doctor_last_name varchar,
    patient_id int,
    patient_first_name varchar,
    patient_last_name varchar,
    patient_gender varchar,
    patient_age integer,
    patient_age_unit varchar,
    patient_clinical_data text,
    national_id_number varchar,
    appointment_date date,
    service_name varchar,
    service_doctor_first_name varchar,
    service_doctor_last_name varchar
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.report_id,
        r.report_title,
        r.report_content,
        r.status,
        r.category,
        r.created_at,
        r.updated_at,
        rd.first_name as referring_doctor_first_name,
        rd.last_name as referring_doctor_last_name,
        p.patient_id,
        p.first_name as patient_first_name,
        p.last_name as patient_last_name,
        p.patient_gender,
        p.patient_age,
        p.patient_age_unit,
        p.patient_clinical_data,
        p.national_id_number,
        a.appointment_date,
        a.service_name,
        d.first_name as service_doctor_first_name,
        d.last_name as service_doctor_last_name
    FROM
        reports r
    LEFT JOIN
        referring_doctors rd ON r.referring_doctor_id = rd.doctor_id
    INNER JOIN
        patients p ON r.patient_id = p.patient_id
    INNER JOIN
        appointments a ON r.appointment_id = a.appointment_id
    LEFT JOIN
        doctors_services_relation dsr ON a.doctor_service_relation_id = dsr.doctor_service_relation_id
    LEFT JOIN
        doctors d ON dsr.doctor_id = d.doctor_id
    WHERE
        r.report_id = p_report_id;
END;
$$ LANGUAGE plpgsql;
