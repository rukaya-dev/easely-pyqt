
create
or replace function search_appointments (search_data text, limit_data int) returns table (
  appointment_id int,
  appointment_date date,
  appointment_time time,
  appointment_type varchar,
  created_at timestamp with time zone,
  appointment_status varchar,
  payment_status varchar,
  patient_id int,
  patient_first_name varchar,
  patient_last_name varchar,
  patient_national_id_number varchar,
  doctor_id int,
  doctor_first_name varchar,
  doctor_last_name varchar,
  doctor_service_cost numeric,
  doctor_service_duration int,
  service_name varchar

) as $$
BEGIN
    RETURN QUERY
      SELECT
          a.appointment_id,
          a.appointment_date,
          a.appointment_time,
          a.appointment_type,
          a.created_at,
          a.appointment_status,
          a.payment_status,
          p.patient_id,
          p.first_name AS patient_first_name,
          p.last_name AS patient_last_name,
          p.national_id_number AS patient_national_id_number,
          d.doctor_id,
          d.first_name AS doctor_first_name,
          d.last_name AS doctor_last_name,
          dsr.doctor_service_cost,
          dsr.doctor_service_duration,
          dsr.service_name
      FROM appointments a
      LEFT JOIN patients p ON a.patient_id = p.patient_id
      LEFT JOIN doctors_services_relation dsr ON a.doctor_service_relation_id = dsr.doctor_service_relation_id
      LEFT JOIN doctors d ON dsr.doctor_id = d.doctor_id
      WHERE
          p.national_id_number ILIKE search_data || '%'
          OR p.first_name ILIKE search_data || '%'
          OR p.last_name ILIKE search_data || '%'
      ORDER BY a.created_at
      LIMIT  limit_data;

END;
$$ language plpgsql stable;