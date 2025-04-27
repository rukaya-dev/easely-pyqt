
create
or replace function search_reports (search_data text, limit_data int) returns table (
  report_id int,
  patient_id int,
  appointment_id int,
  referring_doctor_id int,
  template_name varchar,
  report_title varchar,
  report_content text,
  status varchar,
  created_at timestamp with time zone,
  updated_at timestamp with time zone,
  deleted_at timestamp with time zone,
  category varchar,
  patient_first_name varchar,
  patient_last_name varchar,
  patient_national_id_number varchar,
  appointment_date date,
  doctor_id int,
  doctor_first_name varchar,
  doctor_last_name varchar,
  ref_doctor_first_name varchar,
  ref_doctor_last_name varchar


) as $$
BEGIN
    RETURN QUERY
      SELECT
          r.report_id,
          r.patient_id,
          r.appointment_id,
          r.referring_doctor_id,
          r.template_name,
          r.report_title,
          r.report_content,
          r.status,
          r.created_at,
          r.updated_at,
          r.deleted_at,
          r.category,
          p.first_name AS patient_first_name,
          p.last_name AS patient_last_name,
          p.national_id_number AS patient_national_id_number,
          a.appointment_date As appointment_date,
          d.doctor_id,
          d.first_name AS doctor_first_name,
          d.last_name AS doctor_last_name,
          rd.first_name As ref_doctor_first_name,
          rd.last_name As ref_doctor_last_name
      FROM reports r
      LEFT JOIN patients p ON r.patient_id = p.patient_id
      LEFT JOIN referring_doctors rd ON r.referring_doctor_id = rd.doctor_id
      LEFT JOIN appointments a ON r.appointment_id = a.appointment_id
      LEFT JOIN doctors_services_relation dsr ON a.doctor_service_relation_id = dsr.doctor_service_relation_id
      LEFT JOIN doctors d ON dsr.doctor_id = d.doctor_id
      WHERE
          (p.national_id_number ILIKE search_data || '%'
          OR p.first_name ILIKE search_data || '%'
          OR p.last_name ILIKE search_data || '%'
          OR r.report_title ILIKE search_data || '%'
          OR r.category ILIKE search_data || '%'
          OR rd.first_name ILIKE search_data || '%'
          OR rd.last_name ILIKE search_data || '%'
          OR d.first_name ILIKE search_data || '%'
          OR d.last_name ILIKE search_data || '%')
          AND r.deleted_at IS NULL
      ORDER BY r.created_at
      LIMIT  limit_data;

END;
$$ language plpgsql stable;