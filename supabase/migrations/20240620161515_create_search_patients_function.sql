CREATE OR REPLACE FUNCTION search_patients(search_data TEXT, limit_data INT)
RETURNS TABLE (
  appointment_id INT,
  appointment_date DATE,
  appointment_time TIME,
  appointment_type VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE,
  appointment_status VARCHAR,
  payment_status VARCHAR,
  patient_id INT,
  patient_first_name VARCHAR,
  patient_last_name VARCHAR,
  patient_national_id_number VARCHAR,
  doctor_id INT,
  doctor_first_name VARCHAR,
  doctor_last_name VARCHAR,
  doctor_service_cost NUMERIC,
  doctor_service_duration INT,
  service_name VARCHAR
) 
AS $$
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
      d.service_cost AS doctor_service_cost,
      d.service_duration AS doctor_service_duration,
      s.service_name
    FROM 
      appointments a
      JOIN patients p ON a.patient_id = p.patient_id
      JOIN doctors d ON a.doctor_id = d.doctor_id
      JOIN services s ON a.service_id = s.service_id
    WHERE 
      p.national_id_number ILIKE search_data || '%'
      OR p.last_name ILIKE search_data || '%'
      OR p.first_name ILIKE search_data || '%'
      OR p.patient_gender ILIKE search_data || '%'
      OR p.patient_phone_number ILIKE search_data || '%'
      OR p.patient_address ILIKE search_data || '%'
      OR LOWER(p.first_name || ' ' || p.last_name) ILIKE LOWER(search_data) || '%'
      OR LOWER(p.last_name || ' ' || p.first_name) ILIKE LOWER(search_data) || '%'
    ORDER BY 
      a.created_at
    LIMIT limit_data;
END;
$$ LANGUAGE plpgsql;
